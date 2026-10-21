#!/usr/bin/env python3
"""Identical-input whole-public-call CPU comparison: frozen V1 vs selected UMUL8.

First actual historical-resident-vs-selective replay for issue #375. This
compares the same 1000 operand pairs, Q16, Carry, preserved X/Y and stack
on the archived physical V1 resident and three current source-linked
candidates at two locations. It makes no native-VICE or all-56 parity claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from mini6502 import CPU, load_sparse
import selective_speed
import selective_linker

ROOT=Path(__file__).resolve().parents[1]
FROZEN=Path("v1_balanced/resident/math_v1_balanced_game_math.prg")
SYMBOLS=Path("v1_balanced/resident/math_api.inc")
SLOTS=((0x2000,0xc000,0xc020,0x50),
       (0x6000,0xc040,0xc060,0x58))
BASIS="v1-frozen-prg-vs-selective-umul8-identical-1000-public-calls-cpu-model-v1"

class ComparisonError(ValueError):
    pass

def frozen_source():
    code=(ROOT/FROZEN).read_bytes()
    if len(code)<16: raise ComparisonError("Missing frozen V1 PRG bytes")
    checksums={}
    for line in (ROOT/"SHA256SUMS.txt").read_text("utf-8").splitlines():
        if len(line)>=67 and line[64:66]=="  ":
            checksums[line[66:]]=line[:64]
    sha=hashlib.sha256(code).hexdigest()
    if sha!=checksums.get(FROZEN.as_posix()):
        raise ComparisonError("Frozen V1 resident SHA256 changed")
    origin=code[0]|(code[1]<<8)
    if origin+len(code)-2>0x10000:
        raise ComparisonError("Frozen resident exceeds 64K")
    mem=bytearray(65536)
    mem[origin:origin+len(code)-2]=code[2:]
    symbols={}
    for line in (ROOT/SYMBOLS).read_text("utf-8").splitlines():
        m=re.fullmatch(r"\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)\s*",line)
        if m:symbols[m.group(1)]=int(m.group(2),16)
    for name in ("MATH_UMUL8","MATH_INIT","MATH_X","MATH_Y","MATH_Z"):
        if name not in symbols:
            raise ComparisonError("Incomplete reference public ABI: "+name)
    return CPU(mem),symbols,sha

def evaluate(cpu,entry,io,corpus,*,initialization=False):
    if initialization:
        cpu.d=0
        cpu.call(initialization,2_000_000)
    outcomes=[]
    record=[]
    initial_sp=cpu.sp
    for x,y in corpus:
        cpu.mem[io]=x
        cpu.mem[io+4]=y
        cpu.mem[io+8]=0x55
        cpu.mem[io+9]=0x55
        cpu.d=0
        cpu.c=(x^y)&1
        elapsed=cpu.call(entry,4000)
        q=cpu.mem[io+8]|(cpu.mem[io+9]<<8)
        if q!=x*y or cpu.c!=0 or cpu.sp!=initial_sp:
            raise ComparisonError("Output/Carry/stack regression "+
                                  repr((entry,x,y,q,cpu.c,cpu.sp)))
        if (cpu.mem[io],cpu.mem[io+4])!=(x,y):
            raise ComparisonError("Public X/Y mutated for "+repr((x,y)))
        outcomes.append(elapsed)
        record.extend((x,y,q&255,q>>8,cpu.c))
    timings=sorted(outcomes)
    return {
        "cases":len(outcomes),
        "mean_cycles":sum(outcomes)/len(outcomes),
        "min_cycles":timings[0],
        "p95_cycles":timings[math.ceil(.95*len(timings))-1],
        "max_cycles":timings[-1],
        "public_result_carry_sha256":hashlib.sha256(bytes(record)).hexdigest(),
        "input_bytes_preserved":True,
        "stack_restored":True,
        "decimal_mode":0,
    }

def compare():
    modules=selective_linker.MODULES["MATH_UMUL8"]
    required={"link:v1-resident-fast","link:quarter-square","link:compact-zerozp"}
    if set(modules)!=required:
        raise ComparisonError("Selectable UMUL8 source inventory changed")
    corpus=selective_speed.corpus()
    if len(corpus)!=1000:
        raise ComparisonError("UMUL8 source-qualified corpus changed")
    corpus_sha=hashlib.sha256(bytes(v for pair in corpus for v in pair)).hexdigest()
    c,sym,old_sha=frozen_source()
    if (sym["MATH_UMUL8"],sym["MATH_INIT"],sym["MATH_X"],
        sym["MATH_Y"],sym["MATH_Z"])!=(0x3000,0x3280,0xc000,0xc004,0xc008):
        raise ComparisonError("Frozen V1 public ABI relocation/unexpected layout")
    original=evaluate(c,sym["MATH_UMUL8"],sym["MATH_X"],corpus,
                      initialization=sym["MATH_INIT"])
    layouts=[]
    for start,io,scratch,zp in SLOTS:
        alternatives={}
        for name,module in sorted(modules.items()):
            assembled,entry=selective_speed.assemble_variant(
                name,module["source"],start,io,scratch,ROOT,zp)
            cc=CPU(load_sparse(assembled))
            timings=evaluate(cc,entry,io,corpus)
            if timings["public_result_carry_sha256"]!=original["public_result_carry_sha256"]:
                raise ComparisonError("Cross-variant output digest mismatch "+name)
            timings["measured_entry"]="$%04X"%entry
            timings["resident_minus_selective_mean_cycles"]=(
                original["mean_cycles"]-timings["mean_cycles"])
            timings["cpu_model_equal_or_faster_than_v1"]=(
                timings["mean_cycles"]<=original["mean_cycles"])
            alternatives[name]=timings
        layouts.append({"code_origin":"$%04X"%start,
                        "public_io":"$%04X"%io,
                        "scratch":"$%04X"%scratch,
                        "zp_origin":"$%02X"%zp,
                        "variants":alternatives})
    return {
        "schema":"historical-v1-public-umul8-selective-replay-v1",
        "status":"CPU_MODEL_IDENTICAL_CORPUS_VERIFIED_NOT_NATIVE_VICE",
        "api":"MATH_UMUL8",
        "public_abi":["MATH_X[0]","MATH_Y[0]","MATH_Z[0:2]","Carry clear","stack preserved"],
        "historical_profile":"v1_balanced",
        "historical_prg_sha256":old_sha,
        "historical_public_entry":"$3000",
        "historical_init":"$3280",
        "cycle_basis":"CPU-model public entry through RTS, excluding caller JSR, input writes, one-time INIT and load",
        "corpus_sha256":corpus_sha,
        "cases":len(corpus),
        "historical_observation":original,
        "relocated_selective_observations":layouts,
        "hist_to_selective_same_input":True,
        "all_56_historical_speed_parity":False,
        "native_vice_verified":False,
        "note":"Quantifies one archived V1 resident vs three stock selective UMUL8 alternatives. Other V1–V5 leaders, REU transports and other 55 public operations not proven.",
    }

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args(argv)
    result=compare()
    out=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(out,encoding="utf-8")
    else:print(out,end="")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
