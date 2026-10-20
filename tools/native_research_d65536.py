#!/usr/bin/env python3
"""Research-only native x64sc correctness and *isolated-call* CIA timing.

Native public Q32/R32/C/input preservation is independently verified by
existing signed and unsigned 96-case VICE oracles, supplied identical
boundary-enriched operand corpora. A separate PAL/VIC/CIA microprobe times
only the exact frame-8 SMOD32 input, including staging and capture overhead.
This does not qualify a seven-operation linked PAL application.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

import research_d65536_hybrid as candidate
import selective_hybrid_u3232 as unsigned
import selective_signed_hybrid_u3232 as signed
import native_selective_sdiv32_32 as native_signed
import native_pal_vic_cia_probe as native_probe

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"routines/standalone_lab/portable"))
import native_vice as native_unsigned

CODE, IO, ZP = 0x4123, 0xc040, 0x70
TARGET_API = "MATH_SMOD32_32"
TARGET_N, TARGET_D = candidate.FRAME8_SMOD


def inputs(signed_mode):
    existing = candidate.corpus(signed_mode)
    directed = [
        (TARGET_N,TARGET_D), (0x80000000,TARGET_D),
        (0x7fffffff,TARGET_D), (0xffffffff,TARGET_D),
        (0x00010000,TARGET_D), (0x0000ffff,TARGET_D),
        (0x80000001,0xffff0000), (0x80000001,0),
        (0xffffffff,0xffffffff), (0xffffffff,1),
        (0x80000000,0x80000000), (0,0),
    ]
    selected = tuple(directed+list(existing[:96-len(directed)]))
    if len(selected)!=96 or selected[0]!=(TARGET_N,TARGET_D):
        raise AssertionError("Native fixed D65536 test inputs drifted")
    return selected


def packed(image, code):
    if min(image)!=code or max(image)!=code+len(image)-1:
        raise AssertionError("Research candidate emits a noncontiguous image")
    return code.to_bytes(2,'little')+bytes(image[at] for at in range(code,code+len(image)))


def source_images():
    u_new, u_entries, _=candidate.assemble_unsigned(CODE,IO,ZP)
    s_new, s_entries, _=candidate.assemble_signed(CODE,IO,ZP)
    u_old, u_old_entries, _, _=unsigned.assemble(CODE,IO,ZP)
    s_old, s_old_entries, _, _=signed.assemble(CODE,IO,ZP)
    return (
        ("unsigned","stock",packed(u_old,CODE),u_old_entries[unsigned.API_MOD]),
        ("unsigned","d65536",packed(u_new,CODE),u_entries[unsigned.API_MOD]),
        ("signed","stock",packed(s_old,CODE),s_old_entries[signed.PUBLIC_MOD]),
        ("signed","d65536",packed(s_new,CODE),s_entries[signed.PUBLIC_MOD]),
    )


def exact_target():
    return [(8,0,TARGET_API,TARGET_N,TARGET_D,0,0x5a,0x7b,0x3c,1,
             hashlib.sha256(f"{TARGET_API}|{TARGET_N:08x}|{TARGET_D:08x}".encode()).hexdigest())]


def verify(vice):
    if not vice or not Path(vice).is_file():
        raise RuntimeError("Need pinned native VICE_WRAPPER")
    native_unsigned.VICE=Path(vice)
    rows=[]
    with tempfile.TemporaryDirectory(prefix="d65536_native_") as temp:
        folder=Path(temp)
        for k,(mode,variant,binary,entry) in enumerate(source_images()):
            corpus=inputs(mode=="signed")
            tag=f"d65536_{mode}_{variant}"
            if mode=="signed":
                with patch.object(native_signed,"pairs",return_value=corpus):
                    digest=native_signed.verify(
                        vice,binary,entry,CODE,IO,tag,15300+k,folder)
            else:
                memory=bytearray(65536)
                memory[CODE:CODE+len(binary)-2]=binary[2:]
                mapping={"INPUT_NUM":IO+16,"INPUT_DIV":IO+20,
                         "OUTPUT_QUOT":IO+24,"OUTPUT_REM":IO+28}
                with patch.object(native_unsigned,"operands",return_value=corpus):
                    native=native_unsigned.check(
                        memory,entry,32,mapping,tag,15300+k,folder,False)
                digest=native["output_sha256"]
                if native["cases"]!=96:raise AssertionError("Incomplete unsigned oracles")
            micro={}
            if mode=="signed":
                # The same source-exact signed public entry is exercised under
                # visible VIC DMA and display-disabled control conditions.
                mapping={api:entry for api in native_probe.seven.OPS}
                with patch.object(native_probe,"busiest_calls",return_value=exact_target()):
                    for display in (False,True):
                        sample=native_probe.run_one(
                            vice,binary,mapping,folder,tag+f"_vic{int(display)}",
                            15400+2*k+int(display),frame=8,display=display)
                        micro["display_on" if display else "display_off"]=sample[
                            "measured_cia_phi2_slots"]
            rows.append({
                "source":mode,"variant":variant,"native_public_calls":96,
                "exact_frame8_divisor_in_corpus":True,
                "output_sha256":digest,
                "prg_sha256":hashlib.sha256(binary).hexdigest(),
                "main_ram_bytes":len(binary)-2,
                "zero_page_bytes":candidate.ZP_BYTES,
                "target_cia_microprobe_slots":micro,
            })
            print("NATIVE D65536",mode,variant,"ABI 96 PASS",micro,flush=True)
    for mode in ("unsigned","signed"):
        a=next(row for row in rows if row["source"]==mode and row["variant"]=="stock")
        b=next(row for row in rows if row["source"]==mode and row["variant"]=="d65536")
        if a["output_sha256"]!=b["output_sha256"]:
            raise AssertionError("Native boundary public output/carry differs")
    stock=next(row for row in rows if row["source"]=="signed" and row["variant"]=="stock")
    research=next(row for row in rows if row["source"]=="signed" and row["variant"]=="d65536")
    gain=stock["target_cia_microprobe_slots"]["display_on"]-research["target_cia_microprobe_slots"]["display_on"]
    if gain<=0:
        raise AssertionError("No native PAL improvement on the targeted boundary input")
    return {
        "schema":"research-d65536-native-public-abi-and-isolated-pal-vic-cia-v1",
        "target_dividend_hex":f"${TARGET_N:08X}",
        "target_divisor_hex":f"${TARGET_D:08X}",
        "native_exact_target_display_on_slots_saved":gain,
        "native_target_measurement_is_one_isolated_public_call":True,
        "full_seven_operation_frame_qualified":False,
        "real_50hz_application_frame_certified":False,
        "builder_variant_registered":False,
        "old_kernels_unmodified":True,
        "rows":rows,
    }


def main():
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    result=verify(os.environ.get("VICE_WRAPPER",""))
    payload=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")


if __name__=="__main__":
    main()
