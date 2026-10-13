#!/usr/bin/env python3
"""Research-only exhaustive V1/V5 UMUL8 direct-output proof.

This script patches two CPU-model resident images in memory using an
independent source include. It does NOT change shipped PRGs, API, or source
generation. Promotion requires source/V5 builds, VICE and package CI.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import hashlib
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from benchmark_multiply_refresh import load

PROFILES=("v1_balanced","v5_hybrid_lowzp")
PATCH_EXPECTED={0x3014,0x3015,*range(0x4714,0x471d)}
OLD_PUBLIC=bytes.fromhex("a5 14 8d 08 c0 18 60")
OLD_CORE=bytes.fromhex("85 14 b1 12 fd 00 82 60 00")

def screen(profile):
    old,api=load(profile)
    new,api2=load(profile)
    assert api==api2 and api["MATH_UMUL8"]==0x3000
    assert bytes(old.mem[0x3014:0x301b])==OLD_PUBLIC
    assert bytes(old.mem[0x4714:0x471d])==OLD_CORE
    assert bytes(new.mem[0x3014:0x301b])==OLD_PUBLIC
    src=(ROOT/"relocatable_source/v1_balanced/umul8_directout_trial.inc").read_text()
    config="MATH_UMUL8=$3000\nREG_KERNEL=$4000\nREG_TABLE=$6000\nMATH_Z=$C008\nZP_MAIN=$02\n"
    patch,_,_=Assembler().assemble(config+src)
    assert set(patch)==PATCH_EXPECTED,(profile,"unexpected candidate footprint",sorted(patch))
    for addr,value in patch.items():
        new.mem[addr]=value
    assert bytes(new.mem[0x3014:0x3016])==bytes.fromhex("18 60")
    assert bytes(new.mem[0x4714:0x471d])==bytes.fromhex("8d 08 c0 b1 12 fd 00 82 60")
    hist={}
    sums=[0,0]
    for x in range(256):
        for y in range(256):
            outputs=[]
            cycles=[]
            for cpu in (old,new):
                cpu.mem[0xc000]=x
                cpu.mem[0xc004]=y
                cpu.mem[0xc001]=0x55
                cpu.mem[0xc005]=0xaa
                cpu.mem[0xc00a]=0xb5
                cpu.mem[0xc00b]=0xc7
                cpu.c=(x^y)&1
                sp=cpu.sp
                cycles.append(cpu.call(0x3000,3000))
                z=cpu.mem[0xc008]|cpu.mem[0xc009]<<8
                assert z==x*y,(profile,x,y,z)
                assert cpu.c==0 and cpu.sp==sp
                assert (cpu.mem[0xc000],cpu.mem[0xc001],cpu.mem[0xc004],cpu.mem[0xc005])==(x,0x55,y,0xaa)
                assert (cpu.mem[0xc00a],cpu.mem[0xc00b])==(0xb5,0xc7)
                outputs.append(z)
            assert outputs[0]==outputs[1]
            saving=cycles[0]-cycles[1]
            hist[str(saving)]=hist.get(str(saving),0)+1
            sums[0]+=cycles[0]
            sums[1]+=cycles[1]
    assert hist=={"6":65536},hist
    return {"profile":profile,"cases":65536,"mean_before":sums[0]/65536,
            "mean_after":sums[1]/65536,"saving_histogram":hist,
            "product_carry_inputs_stack_output_sentinel":"PASS"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    rows=[screen(s) for s in PROFILES]
    result={"status":"PASS_RESEARCH_CPU_MODEL_ONLY",
            "scope":"source candidate overlaid in memory; shipped PRGs unchanged",
            "note":"N/Z/V are volatile; native VICE timing not measured",
            "profiles":rows,"issue39_complete":False}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
