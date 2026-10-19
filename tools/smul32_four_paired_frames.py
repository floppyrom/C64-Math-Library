#!/usr/bin/env python3
"""Four-way same-public-input SMUL32 paired 24-frame signed full64 cycle proof.

Full public caller ABI, exact original source-linked PRGs, 31-ZP FAST31 SMC
whitelist, mean/p95/maximum and busiest-frame regressions versus compact.
Not a physical PAL, VIC-II, IRQ, SID or REU hardware timing certificate.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from frame_cycle_budget import Call, score
from mini6502 import CPU
import math_builder
import selective_linker as linker
import selective_speed_smul32 as speed

ROOT=Path(__file__).resolve().parents[1]
API="MATH_SMUL32"
VARIANTS=tuple(sorted(speed.EXPECTED))
FRAMES=24
CALL_COUNT=150


def scenario():
    pairs=speed.corpus()
    calls=[]
    for frame in range(FRAMES):
        volume=24 if frame%8==0 else 8 if frame%4==0 else 3
        for ordinal in range(volume):
            x,y=pairs[(frame*37+ordinal*83)%len(pairs)]
            ra=(frame*17+ordinal*29)&255
            rx=(frame*31+ordinal*7)&255
            ry=(frame*13+ordinal*23)&255
            carry=(frame+ordinal)&1
            token=("%s|%08x|%08x|A=%02x|X=%02x|Y=%02x|C=%d|D=0" %
                   (API,x,y,ra,rx,ry,carry)).encode("ascii")
            calls.append((frame,ordinal,x,y,ra,rx,ry,carry,
                          hashlib.sha256(token).hexdigest()))
    if len(calls)!=CALL_COUNT:
        raise AssertionError("SMUL32 24-frame scenario count changed")
    return tuple(calls)


def evaluate(variant,code=0x8000,io=0xc000,zp=0x50):
    if variant not in speed.EXPECTED:
        raise ValueError("SMUL32 candidate is not source-qualified: "+str(variant))
    if io<0x200 or io+0x80>=0x10000 or zp+31>0xff:
        raise ValueError("Invalid SMUL32 I/O/ZP placement")
    plan=math_builder.create_plan(
        math_builder.operation_index(),["SMUL32"],objective="size",
        ram_budget=3200,zp_budget=31,pins={"SMUL32":variant})
    with tempfile.TemporaryDirectory(prefix="smul32_four_frame_") as td:
        out=Path(td)
        manifest=linker.build(plan,out,memory={
            "code_base":code,"math_io":io,"scratch_base":io+0x40,
            "zp_base":zp})
        ops=manifest["operations"]
        if len(ops)!=1 or ops[0]["api"]!=API or ops[0]["variant"]!=variant:
            raise AssertionError("SMUL32 pinned producer entry drift")
        actual_resources=manifest["resource_use"]
        needed_code,needed_zp,needed_scratch=speed.EXPECTED_RESOURCES[variant]
        if (actual_resources["image_span_bytes"]<needed_code or
            actual_resources["zero_page_bytes"]!=needed_zp or
            actual_resources["private_ram_scratch_bytes"]!=needed_scratch):
            raise AssertionError("SMUL32 source geometry/budget drift")
        binary=(out/"math_selective.prg").read_bytes()
        if binary[:2]!=code.to_bytes(2,"little"):
            raise AssertionError("SMUL32 load origin changed")
        size=len(binary)-2
        if code+size>=io or code+size>=0x10000:
            raise AssertionError("SMUL32 code overlaps math input")
        mem=bytearray(65536)
        mem[code:code+size]=binary[2:]
        original=bytes(mem[code:code+size])
        mod=linker.MODULES[API][variant]
        source,source_entry,mutable=speed.source_assemble(
            variant,mod,code,io,io+0x40,zp,ROOT)
        entry=int(ops[0]["entry"][1:],16)
        if (entry!=source_entry or
            any(mem[addr]!=byte for addr,byte in source.items())):
            raise AssertionError("SMUL32 emitted bytes/entry mismatch original source")
        cpu=CPU(mem)
        sp=cpu.sp
        rows=[]
        for frame,ordinal,x,y,ra,rx,ry,carry,identity in scenario():
            xb=x.to_bytes(4,"little")
            yb=y.to_bytes(4,"little")
            mem[io:io+4]=xb
            mem[io+4:io+8]=yb
            mem[io+8:io+16]=bytes([0xa5])*8
            cpu.a,cpu.x,cpu.y=ra,rx,ry
            cpu.c,cpu.d=carry,0
            cycles=cpu.call(entry,125000)
            got=int.from_bytes(mem[io+8:io+16],"little")
            want=(speed.signed(x)*speed.signed(y))&speed.MASK
            if (got!=want or bytes(mem[io:io+4])!=xb
                or bytes(mem[io+4:io+8])!=yb or cpu.c or cpu.sp!=sp):
                raise AssertionError(("SMUL32 signed64/C/SP/IO drift",variant,
                                      frame,ordinal,x,y,got,want))
            rows.append(Call(frame,ordinal,API,identity,cycles,variant))
        changed={code+i for i,(before,after) in enumerate(
            zip(original,mem[code:code+size])) if before!=after}
        if not changed.issubset(mutable):
            raise AssertionError(("SMUL32 unexpected executable mutation",
                                  variant,sorted(changed-mutable)))
        meta={"measurement_basis":"cpu-model-public-entry-through-rts",
              "placement":"$%04X/$%04X"%(code,io),
              "variants":{API:variant}}
        return {"variant":variant,
                "calls":rows,
                "score":score(rows,meta,frame_count=FRAMES),
                "resources":actual_resources,
                "source_sha256":hashlib.sha256(
                    (ROOT/mod["source"]).read_bytes()).hexdigest(),
                "prg_sha256":hashlib.sha256(binary).hexdigest()}


def compare(code,io,zp=0x50):
    cases={v:evaluate(v,code,io,zp) for v in VARIANTS}
    baseline=cases["link:compact-zerozp"]
    orig=baseline["calls"]
    keys=tuple(q.key for q in orig)
    if len(keys)!=CALL_COUNT or len(set(keys))!=CALL_COUNT:
        raise AssertionError("SMUL32 identical caller corpus changed")
    base=baseline["score"]
    result={"code":"$%04X"%code,"io":"$%04X"%io,
            "paired_calls":CALL_COUNT,"frames":FRAMES,
            "cpu_model_only":True,"native_pal_timing":False,
            "per_variant":{}}
    for variant,data in cases.items():
        calls=data["calls"]
        if tuple(q.key for q in calls)!=keys:
            raise AssertionError("SMUL32 candidate input corpus drift")
        totals=data["score"]
        diffs=[candidate.cycles-reference.cycles
               for reference,candidate in zip(orig,calls)]
        frame_diffs=[a-b for a,b in zip(
            totals["frame_math_cycles"],base["frame_math_cycles"])]
        res=data["resources"]
        result["per_variant"][variant]={
            "mean_public_cycles":sum(q.cycles for q in calls)/CALL_COUNT,
            "peak_frame_math_cycles":totals["peak_frame_math_cycles"],
            "p95_frame_math_cycles":totals["p95_frame_math_cycles"],
            "total_math_cycles":totals["total_math_cycles"],
            "total_savings_vs_compact":base["total_math_cycles"]-totals["total_math_cycles"],
            "peak_savings_vs_compact":base["peak_frame_math_cycles"]-totals["peak_frame_math_cycles"],
            "regressed_calls_vs_compact":sum(n>0 for n in diffs),
            "worst_call_regression_vs_compact":max((0,*diffs)),
            "regressed_frames_vs_compact":sum(n>0 for n in frame_diffs),
            "worst_frame_regression_vs_compact":max((0,*frame_diffs)),
            "zero_page_bytes":res["zero_page_bytes"],
            "code_span_bytes":res["image_span_bytes"],
            "main_ram_total_bytes":res["main_ram_total_bytes"],
            "source_sha256":data["source_sha256"],
            "linked_prg_sha256":data["prg_sha256"]}
    return result


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    result={"basis":"same-public signed full64 four-source 24-frame CPU model",
            "placements":[compare(0x8000,0xc000),
                          compare(0x7123,0xc040,0x70)]}
    content=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(content,encoding="utf-8")
    else:
        print(content,end="")
