#!/usr/bin/env python3
"""Identical-corpus original V1–V5 vs selective UDIV8 public Q/R/Carry timing.

CPU-model only, no native REU/hardware performance claim or all-56 parity.
"""
from __future__ import annotations
import argparse, hashlib, json, math, re
from pathlib import Path
from mini6502 import Assembler, CPU, load_sparse
from validate_unsigned_division import PROFILES, load as frozen_load
import selective_speed_udiv8 as selective
import selective_linker

ROOT=Path(__file__).resolve().parents[1]
MAPS=((0x2000,0xc000,0x50),(0x6000,0xc040,0x58))

class ParityError(ValueError):
    pass

def source_sha(path):
    data=(ROOT/path).read_bytes()
    sha=hashlib.sha256(data).hexdigest()
    found=None
    for line in (ROOT/"SHA256SUMS.txt").read_text("utf-8").splitlines():
        if line.endswith("  "+path):
            found=line[:64]
            break
    if found!=sha:raise ParityError("Frozen file SHA changed: "+path)
    return sha

def evaluate(cpu,entry,io,pairs):
    results=bytearray()
    counts=[]
    sp=cpu.sp
    for n,d in pairs:
        oldn=bytes((n,0xa1,0xb2,0xc3))
        oldd=bytes((d,0xd4,0xe5,0xf6))
        cpu.mem[io+16:io+20]=oldn
        cpu.mem[io+20:io+24]=oldd
        cpu.mem[io+24:io+28]=b"\x55"*4
        cpu.mem[io+28:io+32]=b"\x66"*4
        cpu.d=0
        cpu.c=(n^d)&1
        count=cpu.call(entry,30000)
        q,r,carry=cpu.mem[io+24],cpu.mem[io+28],cpu.c
        if (q,r,carry)!=(n//d if d else 0,n%d if d else 0,int(d==0)):
            raise ParityError("Q/R/C mismatch: "+repr((hex(entry),n,d,q,r,carry)))
        if cpu.sp!=sp or cpu.mem[io+16:io+20]!=oldn or cpu.mem[io+20:io+24]!=oldd:
            raise ParityError("Input or stack corruption")
        results.extend((n,d,q,r,carry))
        counts.append(count)
    rank=sorted(counts)
    return {"cases":len(pairs),"mean_cycles":sum(counts)/len(counts),
            "min_cycles":rank[0],"p95_cycles":rank[math.ceil(.95*len(rank))-1],
            "max_cycles":rank[-1],
            "public_result_sha256":hashlib.sha256(results).hexdigest(),
            "stack_and_inputs_preserved":True}

def assembly(name,module,origin,io,zp):
    code=(ROOT/module["source"]).read_text("utf-8")
    names={"KERNEL_CODE":origin,"INPUT_NUM":io+16,"INPUT_DIV":io+20,
           "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28,"TEMP_ZP":zp}
    for name0,value in names.items():
        regex=r"(?m)^"+re.escape(name0)+r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        literal=name0+" = "+chr(36)+format(value,"04X")
        code,n=re.subn(regex,literal,code)
        if n!=1:raise ParityError("Source location binding drift: "+name0)
    program,labels,_=Assembler().assemble(code)
    size=sum(n for _,n in module["segments"])
    if set(program)!=set(range(origin,origin+size)):
        raise ParityError("UDIV8 code layout changed")
    entry=labels[module["entry"]]
    if entry!=origin+8:raise ParityError("UDIV8 public source entry changed")
    return CPU(load_sparse(program)),entry,size

def compare():
    cases=selective.corpus()
    digest=hashlib.sha256(bytes(v for pair in cases for v in pair)).hexdigest()
    if len(cases)!=1000 or digest!=selective.EXPECTED_CORPUS_SHA256:
        raise ParityError("Frozen same-input UDIV8 corpus changed")
    historical={}
    for profile in PROFILES:
        path=profile+"/resident/math_"+profile+"_game_math.prg"
        sig=source_sha(path)
        if profile in ("v3_reu_512k","v4_reu_16m"):
            reu={"v3_reu_512k":"v3_reu_512k/reu/c64_math_v3_512k_game_math.reu",
                 "v4_reu_16m":"v4_reu_16m/reu/c64_math_v4_16m_game_math.reu"}[profile]
            source_sha(reu)
        cpu,api=frozen_load(profile)
        if [api[x] for x in ("MATH_N","MATH_D","MATH_Q","MATH_R")]!=[
            0xc010,0xc014,0xc018,0xc01c]:
            raise ParityError("Historical public memory ABI changed")
        row=evaluate(cpu,api["MATH_UDIV8"],0xc000,cases)
        row["frozen_prg_sha256"]=sig
        row["entry"]=format(api["MATH_UDIV8"],"#06x")
        historical[profile]=row
    common={x["public_result_sha256"] for x in historical.values()}
    if len(common)!=1:raise ParityError("Historical Q/R/C digests disagree")
    baseline=next(iter(common))
    options=selective_linker.MODULES["MATH_UDIV8"]
    if set(options)!=selective.EXPECTED_VARIANTS:
        raise ParityError("Selective UDIV8 variants changed")
    sampled=[]
    for origin,io,zp in MAPS:
        variants={}
        for variant,module in sorted(options.items()):
            if module["zp"]!=1 or module["scratch"]:
                raise ParityError("Selective candidate resource contract changed")
            cpu,entry,size=assembly(variant,module,origin,io,zp)
            row=evaluate(cpu,entry,io,cases)
            if row["public_result_sha256"]!=baseline:
                raise ParityError("Selective Q/R/C digest disagreement: "+variant)
            row["source_sha256"]=hashlib.sha256(
                (ROOT/module["source"]).read_bytes()).hexdigest()
            row["code_bytes"]=size
            row["entry"]=format(entry,"#06x")
            variants[variant]=row
        sampled.append({"origin":format(origin,"#06x"),"io":format(io,"#06x"),
                        "zp":format(zp,"#04x"),"variants":variants})
    return {"schema":"historical-five-profile-selective-udiv8-same-corpus-v1",
            "status":"MATCHED_PUBLIC_CPU_MODEL_ONLY_NOT_NATIVE_VICE",
            "api":"MATH_UDIV8","cases":len(cases),"corpus_sha256":digest,
            "cycle_basis":"public entry to RTS (one-time resident INIT excluded)",
            "historic_original_residents":historical,
            "selective_two_physical_placements":sampled,
            "all_seven_source_paths_identical_input":True,
            "all_56_speed_parity_certified":False,
            "reu_bus_cycles_measured":False,"native_vice_certified":False}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    args=p.parse_args(argv)
    text=json.dumps(compare(),sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(text,encoding="utf-8")
    else:print(text,end="")
    return 0

if __name__=="__main__":raise SystemExit(main())
