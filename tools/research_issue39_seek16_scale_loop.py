#!/usr/bin/env python3
"""Paired unchanged-shipped vs regenerated SEEK16 Euclidean scaler research.

All five published resident profiles, both reference/alternate candidate maps,
deterministic identical signed deltas/speeds, state-array, flags, inputs, X-slot
and CPU cycles. No release or native VICE timing is claimed.
"""
from pathlib import Path
import hashlib,json,random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU
from validate_source_build import seek_symbols,load as source_load
from benchmark_seek_profiles import corpus,api
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
SP=(0x80,0x100,0x180,0x200,0x300,0x400,0x8100,0x8180,0x8200,0x8300)
def sha(data):return hashlib.sha256(data).hexdigest()
def baseline(p):
    path=ROOT/p/"resident"/("math_"+p+"_game_math.prg")
    b=path.read_bytes()
    ld=int.from_bytes(b[:2],"little")
    mem=bytearray(65536);mem[ld:ld+len(b)-2]=b[2:]
    reu_path={"v3_reu_512k":"c64_math_v3_512k_game_math.reu",
              "v4_reu_16m":"c64_math_v4_16m_game_math.reu"}.get(p)
    reu=bytearray((ROOT/p/"reu"/reu_path).read_bytes()) if reu_path else None
    c=CPU(mem,reu=reu)
    c.d=0
    a=api(p);c.call(a["MATH_INIT"],2_000_000)
    return c,a,sha(b)
def candidate(p,kind):
    d=ROOT/("build_hybrid" if p=="v5_hybrid_lowzp" else "build_source")/kind/p
    c,a,io,m,_=source_load(p,d.parent)
    symbols=seek_symbols(d)
    return c,{**a,**symbols},m["output_sha256"]
def generate():
    ms=corpus(320)
    wide=[(0,0,32767,199),(32767,199,0,0),(9000,255,3,0),
          (65535,10,33000,220),(32000,0,60000,255),
          (0,0,0,0),(500,40,501,41),(500,40,501,40)]
    r=random.Random(0x519B)
    for _ in range(110):
        x0=r.randrange(65536)
        dx=r.randrange(-32767,32768)
        x1=x0+dx
        if x1<0 or x1>65535:continue
        wide.append((x0,r.randrange(256),x1,r.randrange(256)))
    return ms+wide
def init(c,a,m,sp,slot):
    x0,y0,x1,y1=m
    seek=a["MATH_SEEK16_POS_XL"]
    # Complete 248-byte state reset avoids cross-case contamination.
    c.mem[seek:seek+248]=bytes(248)
    for off,val in ((0,x0&255),(8,(x0>>8)&255),(16,y0)):
        c.mem[seek+off+slot]=val
    io=a["MATH_X"]
    c.mem[io]=x1&255;c.mem[io+1]=(x1>>8)&255
    c.mem[io+4]=y1
    c.mem[io+0x10]=sp&255;c.mem[io+0x11]=sp>>8
    inputs=(c.mem[io],c.mem[io+1],c.mem[io+4],c.mem[io+0x10],c.mem[io+0x11])
    c.x=slot;c.c=1;c.d=0
    cycles=c.call(a["MATH_SEEK16_INIT"],2_000_000)
    assert c.x==slot and c.sp==0xfd,(m,sp,"slot/stack")
    assert inputs==(c.mem[io],c.mem[io+1],c.mem[io+4],c.mem[io+0x10],c.mem[io+0x11]),(m,sp,"inputs")
    return cycles,c.c,bytes(c.mem[seek:seek+248]),c.x
def run():
    corpus16=generate()
    report={"status":"PASS_SEEK16_EUCLID_SCALE_LOOP_RESEARCH",
       "published_prgs_changed":False,
       "native_vice_cycle_timing":False,
       "candidate_models":"reference and alternate maps",
       "input_moves":len(corpus16),"speeds":list(SP),
       "profiles":{}}
    st=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
    for p in P:
        old,oldapi,oldsha=baseline(p)
        assert oldsha==st["reference_prg_sha256"][p],p
        report["profiles"][p]={}
        for kind in ("reference","alternate"):
            new,newapi,candidatesha=candidate(p,kind)
            assert oldapi["MATH_SEEK16_INIT"]==newapi["MATH_SEEK16_INIT"] if kind=="reference" else True
            count=0;euclid=0;changed=0;sum_gain=0;max_gain=0;min_gain=10000
            for i,m in enumerate(corpus16):
                for speed in SP:
                    slot=i&7
                    a=init(old,oldapi,m,speed,slot)
                    b=init(new,newapi,m,speed,slot)
                    assert a[1:]==b[1:],(p,kind,m,speed,"state or flag",a[1:],b[1:])
                    gain=a[0]-b[0]
                    assert 0<=gain<=25,(p,kind,m,speed,gain)
                    if speed&0x8000:
                        euclid+=1
                        if gain:changed+=1
                    else:assert gain==0,(p,kind,"major-axis path drift",gain)
                    count+=1;sum_gain+=gain
                    max_gain=max(max_gain,gain);min_gain=min(min_gain,gain)
            assert count==len(corpus16)*len(SP)
            assert changed>0 and euclid>0,(p,kind,changed,euclid)
            report["profiles"][p][kind]={
                "baseline_prg_sha256":oldsha,"candidate_prg_sha256":candidatesha,
                "init_calls_per_image":count,
                "state_and_carry_identical":True,"slot_and_inputs_preserved":True,
                "mean_cpu_model_cycles_saved":sum_gain/count,
                "max_cpu_model_cycles_saved":max_gain,
                "min_cpu_model_cycles_saved":min_gain,
                "euclid_calls":euclid,"euclid_cases_improved":changed}
            print(p,kind,"PASS",count,"mean_gain",sum_gain/count,"max",max_gain,flush=True)
    path=ROOT/"validation/review/ISSUE39_SEEK16_SCALE_LOOP_RESEARCH_2026-10-14.json"
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("SEEK16 SCALER CANDIDATE PASS (RESEARCH NOT RELEASE)",flush=True)
if __name__=="__main__":run()
