#!/usr/bin/env python3
"""Issue #39 research only: exhaustive paired DIST8 shared swap screen.

Patch an in-memory copy of each SHIPPED resident PRG. Never touch published
binaries, generated source, the stable entry-point map, or private OptiSearch.
Both distance routines use dist_abs_order. Preserve the 14-byte address span
and the original BCC destination, replacing the expensive PHA/PLA exchange
with TAX/LDA/STA/STX/RTS plus three unreachable NOPs.

This is NOT a production integration nor native-VICE timing evidence.
"""
from pathlib import Path
import argparse, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from validate_smul24_directout import parse_inc

PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k",
          "v4_reu_16m","v5_hybrid_lowzp")
OPS=("MATH_DIST8_FAST","MATH_DIST8_ACCURATE")
# Common resident scratch S10/S11, absolute C64 locations C04A/C04B.
OLD=bytes.fromhex("ad4ac048ad4bc08d4ac0688d4bc0")
NEW=bytes.fromhex("aaad4ac08d4bc08e4ac060eaeaea")
assert len(OLD)==len(NEW)==14
def loaded(profile):
    path=ROOT/profile/"resident"/("math_"+profile+"_game_math.prg")
    prg=path.read_bytes()
    address=int.from_bytes(prg[:2],"little")
    mem=bytearray(65536)
    mem[address:address+len(prg)-2]=prg[2:]
    reu_file={"v3_reu_512k":"c64_math_v3_512k_game_math.reu",
              "v4_reu_16m":"c64_math_v4_16m_game_math.reu"}.get(profile)
    reu=(ROOT/profile/"reu"/reu_file).read_bytes() if reu_file else None
    names=parse_inc(ROOT/profile/"resident"/"math_api.inc")
    return mem,reu,names,hashlib.sha256(prg).hexdigest()
def make_cpu(memory,reu,names):
    cpu=CPU(bytearray(memory),reu=bytearray(reu) if reu is not None else None)
    cpu.d=0
    cpu.call(names["MATH_INIT"],2_000_000)
    assert cpu.c==0
    return cpu
def run(profile):
    mem,reu,names,prg_hash=loaded(profile)
    count=mem.count(0) # irrelevant, verifies usable memory exists
    assert len(mem)==65536 and count>=0
    matches=[i for i in range(65536-len(OLD)+1) if mem[i:i+len(OLD)]==OLD]
    assert len(matches)==1,(profile,"expected exactly one complete shared swap",matches)
    at=matches[0]
    # Verify the 6502 carry-branch targets the first RTS after the 14-byte span.
    assert mem[at-2]==0x90 and (at+((mem[at-1]+128)%256-128)+0)==at+14, (profile,hex(at),mem[at-2:at].hex())
    assert mem[at+14]==0x60,(profile,"shared RTS missing",hex(at))
    patched=bytearray(mem)
    patched[at:at+14]=NEW
    old_cpu=make_cpu(mem,reu,names)
    new_cpu=make_cpu(patched,reu,names)
    I=names["MATH_X"]; J=names["MATH_Y"]; Z=names["MATH_Z"]
    profile_out={"status":"PASS","patch_address":f"${at:04X}",
                 "original_14_bytes":OLD.hex(),"replacement_14_bytes":NEW.hex(),
                 "baseline_prg_sha256":prg_hash,"routines":{}}
    for opname in OPS:
        entry=names[opname]
        total_old=total_new=swaps=cases=0
        digest_old=hashlib.sha256();digest_new=hashlib.sha256()
        min_delta=10**9;max_delta=-10**9
        for ax in range(256):
            x=ax if ax<128 else ax-256
            amag=abs(x)
            for ay in range(256):
                y=ay if ay<128 else ay-256
                swap=int(abs(y)>=amag)
                vals=[]
                for cpu,digest in ((old_cpu,digest_old),(new_cpu,digest_new)):
                    cpu.mem[I]=ax;cpu.mem[J]=ay
                    cpu.mem[Z]=0xA5;cpu.mem[Z+1]=0x5A
                    cpu.c=(ax^ay)&1;cpu.d=0
                    cycles=cpu.call(entry,2_000_000)
                    assert cpu.mem[I]==ax and cpu.mem[J]==ay
                    assert cpu.mem[Z+1]==0x5A
                    assert cpu.c==0 and cpu.sp==0xfd
                    scratch=bytes(cpu.mem[0xC04A:0xC04C])
                    digest.update(bytes([cpu.mem[Z],*scratch]))
                    vals.append((cycles,cpu.mem[Z],scratch))
                b,a=vals
                assert b[1:]==a[1:],(profile,opname,ax,ay,b,a)
                delta=b[0]-a[0]
                assert delta==9*swap,(profile,opname,ax,ay,delta,swap)
                total_old+=b[0];total_new+=a[0];swaps+=swap
                min_delta=min(min_delta,delta);max_delta=max(max_delta,delta)
                cases+=1
        assert cases==65536 and digest_old.hexdigest()==digest_new.hexdigest()
        profile_out["routines"][opname]={
          "cases":cases,"swap_path_cases":swaps,
          "mean_old_cpu_model_cycles":total_old/cases,
          "mean_candidate_cpu_model_cycles":total_new/cases,
          "mean_cpu_model_cycles_saved":(total_old-total_new)/cases,
          "min_saved":min_delta,"max_saved":max_delta,
          "output_and_scratch_sha256":digest_old.hexdigest(),
          "bytewise_equal":True,
          "public_input_carry_stack_preserved":True}
        print(profile,opname,cases,"PASS","mean saved",
              profile_out["routines"][opname]["mean_cpu_model_cycles_saved"],flush=True)
    return profile_out
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    data={"status":"PASS_EXHAUSTIVE_RESEARCH_NOT_PRODUCTION",
          "source":"shipped reference resident images",
          "branch_scope":"in-memory patched public ABI, not published code",
          "native_vice_cycles_measured":False,
          "production_binaries_changed":False,
          "private_optisearch_source_published":False,
          "required_next":"check reference+alternate relocation, native VICE, standalone, signed edge cases, mixed calls, integrate in binary/source safely, full release CI",
          "profiles":{}}
    for p in PROFILES:
        data["profiles"][p]=run(p)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print("ISSUE39 DIST8 REGISTER SWAP RESEARCH PASS",flush=True)
if __name__=="__main__":main()
