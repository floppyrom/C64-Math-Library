#!/usr/bin/env python3
"""Issue39 research: SEEK16 Euclidean-scale final-iteration fallthrough.

Compare SHIPPED old PRG to source-built new PRG across five profiles and both
relocation maps, with identical initial slot/target/speed inputs. All 248
object-state bytes, input bytes, carry, preserved X, stack and public-entry
cycles are audited. This script does not publish binaries.
"""
import hashlib,json,random,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
import validate_source_build as vsb
import benchmark_seek_profiles as oldbench
from seek_kernel import S16_BYTES
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
B=(R/"build_source",R/"build_hybrid")
SP=(0x0080,0x0100,0x0180,0x0200,0x0300,0x0400,0x8100,0x8180,0x8200,0x8300,0x8480)
def corpus():
    corners=(0,1,63,64,127,128,255,256,257,300,319)
    e=[(a,y0,b,y1) for a in corners for b in corners for y0,y1 in ((0,199),(199,0))]
    rng=random.Random(0x5EE6)
    e.extend((rng.randrange(320),rng.randrange(200),rng.randrange(320),rng.randrange(200)) for _ in range(120))
    # Signed-boundary horizontal deltas within the SEEK16 stated contract.
    e.extend(((0,0,319,0),(319,199,0,199),(300,50,40,51),
             (10,10,310,11),(310,20,5,19),(256,70,0,70)))
    return e
def test_one(cpu,api,seek,io,slot,m,speed):
    x0,y0,x1,y1=m
    b=seek["MATH_SEEK16_POS_XL"]
    cpu.mem[seek["MATH_SEEK16_POS_XL"]+slot]=x0&255
    cpu.mem[seek["MATH_SEEK16_POS_XH"]+slot]=(x0>>8)&255
    cpu.mem[seek["MATH_SEEK16_POS_Y"]+slot]=y0
    cpu.mem[io]=x1&255;cpu.mem[io+1]=(x1>>8)&255;cpu.mem[io+4]=y1
    cpu.mem[io+0x10]=speed&255;cpu.mem[io+0x11]=speed>>8
    inputs=bytes(cpu.mem[z] for z in (io,io+1,io+4,io+0x10,io+0x11))
    cpu.x=slot;cpu.d=0;cpu.c=1
    cycles=cpu.call(api["MATH_SEEK16_INIT"],2_000_000)
    assert cpu.x==slot and cpu.sp==0xfd,(m,speed,"x/stack")
    assert bytes(cpu.mem[z] for z in (io,io+1,io+4,io+0x10,io+0x11))==inputs,(m,speed,"input")
    return cycles,cpu.c,bytes(cpu.mem[b:b+S16_BYTES]),cpu.x
def main():
    st=json.loads((R/"RELEASE_STATUS.json").read_text())
    testcases=corpus()
    results={"status":"PASS_RESEARCH_NOT_PRODUCTION","native_vice_cycles_measured":False,
      "released_binaries_modified":False,"actual_6502_public_entry":True,
      "changed_routine":"MATH_SEEK16_INIT",
      "profiles":{}}
    for p in P:
      orig=(R/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes()
      assert hashlib.sha256(orig).hexdigest()==st["reference_prg_sha256"][p]
      results["profiles"][p]={}
      for kind in ("reference","alternate"):
        old,oldapi=oldbench.load(p)
        original_seek=vsb.seek_symbols(R/p/"resident")
        assert oldapi["MATH_SEEK16_INIT"]==original_seek["MATH_SEEK16_INIT"]
        built=R/("build_hybrid" if p==P[-1] else "build_source")/kind
        new,api,io,man,_=vsb.load(p,built)
        seek=vsb.seek_symbols(built/p)
        assert hashlib.sha256((built/p/man["output_prg"]).read_bytes()).hexdigest()==man["output_sha256"]
        if kind=="reference":
          assert man["output_sha256"]!=hashlib.sha256(orig).hexdigest(),(p,"stale source")
        delta_hist={}
        before_total=after_total=cases=4cycle=0
        outsha=hashlib.sha256()
        for m in testcases:
          for speed in SP:
            slot=cases&7
            bef=test_one(old,oldapi,original_seek,oldapi["MATH_X"],slot,m,speed)
            aft=test_one(new,api,seek,io,slot,m,speed)
            assert bef[1:]==aft[1:],(p,kind,m,speed,bef,aft)
            sav=bef[0]-aft[0]
            dx=abs(m[2]-m[0]);dy=abs(m[3]-m[1])
            # The scale loop is entered only on path-speed and
            # x-major >255 (y-major remains <=199).
            expect=4 if speed&0x8000 and dx>=256 and dx>=dy else 0
            assert sav==expect,(p,kind,m,speed,sav,expect)
            before_total+=bef[0];after_total+=aft[0];cases+=1
            delta_hist[str(sav)]=delta_hist.get(str(sav),0)+1
            if sav==4: fourcycle+=1
            outsha.update(aft[2])
        row={"cases":cases,"before_mean_cycles":before_total/cases,
           "candidate_mean_cycles":after_total/cases,
           "mean_cycles_saved":(before_total-after_total)/cases,
           "exact_savings_histogram":delta_hist,"four_cycle_cases":fourcycle,
           "all_248_state_bytes_flags_stack_and_X_equal":True,
           "output_sha256":outsha.hexdigest(),
           "candidate_sha256":man["output_sha256"]}
        assert cases==len(testcases)*len(SP)
        results["profiles"][p][kind]=row
        print("SEEK16 INIT",p,kind,"PASS",cases,"saving",row["mean_cycles_saved"],flush=True)
      assert results["profiles"][p]["reference"]["output_sha256"]==results["profiles"][p]["alternate"]["output_sha256"]
    assert all(results["profiles"][p]["reference"]["four_cycle_cases"]>0 for p in P)
    dest=R/"validation/review/ISSUE39_SEEK16_SCALE_EXIT_RESEARCH_2026-10-14.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(results,indent=2,sort_keys=True)+"\n")
    print("SEEK16 EUCLID SCALE EXIT RESEARCH PASS",flush=True)
if __name__=="__main__":main()
