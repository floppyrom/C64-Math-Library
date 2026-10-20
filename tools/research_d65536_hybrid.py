#!/usr/bin/env python3
"""Opt-in research: source-assembled D=$00010000 full32 Q/R fast path.

This is NOT a selectable library routine. It retains the exact historical
V2 32/16 donor and full-width zero-page-tail fallback as separately
reassembled sources; only the dispatcher is extended. A signed wrapper is
relocated to the *new* end of the unsigned image. No V1-V5 or stock V2
code/ABI/resource reservation changes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from mini6502 import Assembler, CPU, load_sparse
import selective_hybrid_u3232 as unsigned
import selective_signed_hybrid_u3232 as signed
import selective_speed_s3232 as signed_reference
import selective_speed_u3232 as unsigned_reference

ROOT = Path(__file__).resolve().parents[1]
OLD_UNSIGNED_BYTES = unsigned.IMAGE_BYTES
IMAGE_BYTES = 0xa20
DISPATCH_OFFSET = unsigned.DISPATCH_OFFSET
WRAPPER_BYTES = signed.WRAPPER_BYTES
SIGNED_IMAGE_BYTES = IMAGE_BYTES + WRAPPER_BYTES
ZP_BYTES = unsigned.ZP_BYTES
PLACEMENTS = ((0x8000, 0xc000, 0x50), (0x4123, 0xc040, 0x70))
FRAME8_SMOD = (0x80000001, 0x00010000)
MASK32 = 0xffffffff
assert IMAGE_BYTES > OLD_UNSIGNED_BYTES and DISPATCH_OFFSET < OLD_UNSIGNED_BYTES


def render_dispatch(code, io, low_entry, wide_entry):
    """Assemble dispatch afresh: never binary-patch the original V2 producer."""
    return f"""!cpu 6510
INPUT_NUM = ${io+16:04X}
INPUT_DIV = ${io+20:04X}
OUTPUT_QUOT = ${io+24:04X}
OUTPUT_REM = ${io+28:04X}
FAST_LOW = ${low_entry:04X}
FULL_WIDE = ${wide_entry:04X}
* = ${code+DISPATCH_OFFSET:04X}
{unsigned.API_DIV}:
{unsigned.API_MOD}:
    lda INPUT_DIV+2
    ora INPUT_DIV+3
    beq NARROW_DIVISOR
    cmp #$01
    bne FULL_DIVISOR
    lda INPUT_DIV+3
    bne FULL_DIVISOR
    lda INPUT_DIV
    ora INPUT_DIV+1
    bne FULL_DIVISOR
D65536:
    lda INPUT_NUM+2
    sta OUTPUT_QUOT
    lda INPUT_NUM+3
    sta OUTPUT_QUOT+1
    lda #$00
    sta OUTPUT_QUOT+2
    sta OUTPUT_QUOT+3
    lda INPUT_NUM
    sta OUTPUT_REM
    lda INPUT_NUM+1
    sta OUTPUT_REM+1
    lda #$00
    sta OUTPUT_REM+2
    sta OUTPUT_REM+3
    clc
    rts
NARROW_DIVISOR:
    jsr FAST_LOW
    lda #$00
    sta OUTPUT_REM+2
    sta OUTPUT_REM+3
    rts
FULL_DIVISOR:
    jmp FULL_WIDE
"""


def assemble_unsigned(code, io, zp, root=ROOT):
    if not (0x0200 <= code and code+IMAGE_BYTES <= 0x10000
            and 2 <= zp <= 0xf4 and 0 <= io <= 0xffdf):
        raise ValueError("Research unsigned source placement outside 64K")
    low, low_labels, _ = unsigned.v2.assemble(
        code, io, zp, root, offsets=unsigned.V2_COMPACT_OFFSETS)
    if low_labels[unsigned.v2.PUB_ENTRY] != code+unsigned.V2_COMPACT_OFFSETS[2]:
        raise AssertionError("Historical V2 low-divisor source entry changed")
    wide, wide_labels, _ = Assembler().assemble(
        unsigned.render_wide(code, io, zp, root))
    wide_range=set(range(
        code+unsigned.FALLBACK_OFFSET,
        code+unsigned.FALLBACK_OFFSET+unsigned.FALLBACK_CORE+unsigned.FALLBACK_TAIL))
    if set(wide) != wide_range:
        raise AssertionError("Historical unrestricted wide source layout changed")
    dispatch, labels, _ = Assembler().assemble(render_dispatch(
        code, io, low_labels[unsigned.v2.PUB_ENTRY],
        wide_labels["FAST_UDIV32_PUBLIC"]))
    if (labels[unsigned.API_DIV] != code+DISPATCH_OFFSET
            or labels[unsigned.API_MOD] != code+DISPATCH_OFFSET
            or not set(dispatch)
            or min(dispatch) < code+DISPATCH_OFFSET
            or max(dispatch) >= code+IMAGE_BYTES):
        raise AssertionError("Research dispatch exceeded declared new image")
    regions=[set(low),set(wide),set(dispatch)]
    if any(regions[i].intersection(regions[j])
           for i in range(3) for j in range(i+1,3)):
        raise AssertionError("Reassembled source ranges overlap")
    image={at:0xea for at in range(code,code+IMAGE_BYTES)}
    image.update(low)
    image.update(wide)
    image.update(dispatch)
    return image, {unsigned.API_DIV: labels[unsigned.API_DIV],
                   unsigned.API_MOD: labels[unsigned.API_MOD],
                   "FAST_LOW": low_labels[unsigned.v2.PUB_ENTRY],
                   "WIDE": wide_labels["FAST_UDIV32_PUBLIC"]}, code+IMAGE_BYTES


def assemble_signed(code, io, zp, root=ROOT):
    if code+SIGNED_IMAGE_BYTES > 0x10000:
        raise ValueError("Research signed image outside 64K")
    u_image, u_labels, end = assemble_unsigned(code, io, zp, root)
    assert end == code+IMAGE_BYTES
    # signed.render() uses its argument only for the wrapper origin.
    # Displace it by the new unsigned core's extra source bytes.
    relocation = IMAGE_BYTES - signed.UNSIGNED_BYTES
    wrapper, labels, _ = Assembler().assemble(
        signed.render(code+relocation, io, u_labels[unsigned.API_DIV]))
    start=code+IMAGE_BYTES
    if (labels[signed.PUBLIC_DIV]!=start or labels[signed.PUBLIC_MOD]!=start
            or not set(wrapper) or min(wrapper)<start
            or max(wrapper)>=code+SIGNED_IMAGE_BYTES
            or set(u_image).intersection(wrapper)):
        raise AssertionError("Relocated signed wrapper source layout changed")
    image={at:0xea for at in range(code,code+SIGNED_IMAGE_BYTES)}
    image.update(u_image)
    image.update(wrapper)
    return image, {signed.PUBLIC_DIV:start,signed.PUBLIC_MOD:start,
                   "UNSIGNED":u_labels[unsigned.API_DIV]}, code+SIGNED_IMAGE_BYTES


def reference(signed_mode, n, d):
    if signed_mode:
        return signed_reference.reference(n,d)
    return (n//d if d else 0,n%d if d else 0,int(d==0))


def corpus(signed_mode):
    existing = signed_reference.corpus() if signed_mode else unsigned_reference.corpus()
    directed = (
        (0x80000001,0x10000), (0x80000001,0xffff), (0x80000001,0x10001),
        (0xffffffff,0x10000), (0,0x10000), (0x10000,0x10000),
        (0xffff,0x10000), (0x10001,0x10000), (0x7fffffff,0x10000),
        (0x80000000,0x10000), (0x80000001,0xffff0000),
        (0x80000000,0xffff0000), (0x80000001,0), (0xffffffff,0),
        (0x80000001,0xffffffff), (0xffffffff,0x7fffffff),
    )
    return tuple(existing)+directed


def qualify_one(image, entry, code, io, cases, signed_mode, *, name):
    memory=load_sparse(image)
    cpu=CPU(memory)
    sp=cpu.sp
    original=bytes(cpu.mem[code:code+len(image)])
    samples=[]
    for i,(n,d) in enumerate(cases):
        cpu.mem[io+16:io+20]=n.to_bytes(4,'little')
        cpu.mem[io+20:io+24]=d.to_bytes(4,'little')
        cpu.mem[io+24:io+32]=b'\x55'*8
        cpu.a=(n^d)&255
        cpu.x=(n>>8)&255
        cpu.y=(d>>8)&255
        cpu.d=0
        cpu.c=i&1
        cycles=cpu.call(entry,150000)
        result=(int.from_bytes(cpu.mem[io+24:io+28],"little"),
                int.from_bytes(cpu.mem[io+28:io+32],"little"),cpu.c)
        exp=reference(signed_mode,n,d)
        if (result!=exp or cpu.sp!=sp
            or int.from_bytes(cpu.mem[io+16:io+20],"little")!=n
            or int.from_bytes(cpu.mem[io+20:io+24],"little")!=d):
            raise AssertionError(("Complete public ABI mismatch",name,hex(code),
                                  i,hex(n),hex(d),result,exp))
        samples.append(cycles)
    if bytes(cpu.mem[code:code+len(image)]) != original:
        raise AssertionError("Research kernel wrote into executable source")
    return samples


def qualify():
    records=[]
    for code, io, zp in PLACEMENTS:
        for is_signed in (False,True):
            cases=corpus(is_signed)
            digest=hashlib.sha256(b''.join(
                n.to_bytes(4,'little')+d.to_bytes(4,'little') for n,d in cases
            )).hexdigest()
            if is_signed:
                new_image, labels, end=assemble_signed(code,io,zp)
                old_image, old_labels, _, old_end=signed.assemble(code,io,zp)
                entry_new=labels[signed.PUBLIC_MOD]
                entry_old=old_labels[signed.PUBLIC_MOD]
            else:
                new_image, labels, end=assemble_unsigned(code,io,zp)
                old_image, old_labels, _, old_end=unsigned.assemble(code,io,zp)
                entry_new=labels[unsigned.API_MOD]
                entry_old=old_labels[unsigned.API_MOD]
            new=qualify_one(new_image,entry_new,code,io,cases,is_signed,
                            name="d65536-optin")
            original=qualify_one(old_image,entry_old,code,io,cases,is_signed,
                                 name="stock-v2")
            hit=[i for i,(_,d) in enumerate(cases) if d==0x10000]
            miss=[i for i,(_,d) in enumerate(cases) if d!=0x10000]
            if not hit or not miss:
                raise AssertionError("Unmatched corpus has no target or fallback inputs")
            target=next(i for i,pair in enumerate(cases) if pair==FRAME8_SMOD)
            records.append({
                "placement": f"${code:04X}/${io:04X}/${zp:02X}",
                "signed": is_signed,
                "cases":len(cases), "input_corpus_sha256":digest,
                "public_entry_new":entry_new,
                "code_bytes_stock":old_end-code,
                "code_bytes_research":end-code,
                "extra_main_ram_bytes":end-old_end,
                "zero_page_bytes":ZP_BYTES,
                "average_stock_model_cycles":sum(original)/len(original),
                "average_research_model_cycles":sum(new)/len(new),
                "worst_stock_model_cycles":max(original),
                "worst_research_model_cycles":max(new),
                "target_d65536_cases":len(hit),
                "target_mean_stock_cycles":sum(original[i] for i in hit)/len(hit),
                "target_mean_research_cycles":sum(new[i] for i in hit)/len(hit),
                "fallback_mean_stock_cycles":sum(original[i] for i in miss)/len(miss),
                "fallback_mean_research_cycles":sum(new[i] for i in miss)/len(miss),
                "frame8_smod_input_stock_cycles":original[target],
                "frame8_smod_input_research_cycles":new[target],
                "same_complete_q32_r32_c_and_original_inputs":True,
                "native_pal_timing":False,
                "qualified_for_builder":False,
            })
    return {
        "schema":"d65536-unregistered-divmod-research-v1",
        "research_only":True, "native_pal_qualified":False,
        "operation_first_builder_variant_registered":False,
        "historical_producer_unmodified":True,
        "source_donors":unsigned.source_sha256(),
        "records":records,
    }


def main():
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    result=qualify()
    text=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(text,encoding="utf-8")
    else:
        print(text,end="")


if __name__=="__main__":
    main()
