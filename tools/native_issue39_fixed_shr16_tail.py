#!/usr/bin/env python3
"""Native x64sc A/B proof for the released fixed 32-bit SHR16 return-tail patch.

Checks identical old/new public data, carry, complete output bytes and stack
for signed and unsigned 32x32->48 fixed results across five resident profiles.
The native emulator is used for correctness, NOT timing.
"""
from pathlib import Path
import hashlib,json,os,socket,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from native_issue39_signed_multiply_family import (
    make_harness,api,pairs,FIELDS,STRIDE,COUNT,H,INPUT,OUTPUT,sha)
from native_issue39_u24_txa_resident import command
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
OPS=("MATH_UMUL32_SHR16","MATH_SMUL32_SHR16")
BASE="bfc43c2f6643a893304799683f73396e0eba3096"
def fixed_expected(x,y,is_signed):
    if is_signed:
        x=x-(1<<32) if x&0x80000000 else x
        y=y-(1<<32) if y&0x80000000 else y
    return ((x*y)>>16)&((1<<48)-1)
def run_native(profile,blob,entry,port,tmp,exe):
    load=int.from_bytes(blob[:2],"little")
    assert load==0x1000
    mem=bytearray(65536);mem[load:load+len(blob)-2]=blob[2:]
    code,stop=make_harness(api(profile),entry,32)
    mem[H:H+len(code)]=code
    vectors=pairs(32)
    for i,(x,y) in enumerate(vectors):
        for j in range(8):
            if j<4:v=(x>>(8*j))&255
            else:v=(y>>(8*(j-4)))&255
            mem[INPUT+j*STRIDE+i]=v
    image=tmp/(profile+"_"+entry+"_"+str(port)+".prg")
    dump=tmp/(profile+"_"+entry+"_"+str(port)+".dump")
    log=tmp/(profile+"_"+entry+"_"+str(port)+".log")
    image.write_bytes(bytes([INPUT&255,INPUT>>8])+mem[INPUT:0xd000])
    cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp",
         "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
         "-initbreak","reset"]
    with log.open("w") as out:
        proc=subprocess.Popen(cmd,cwd=tmp,stdout=out,stderr=out)
        try:
            sock=None
            for _ in range(200):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.2);break
                except (ConnectionRefusedError,TimeoutError):time.sleep(.07)
            if sock is None:raise RuntimeError(("VICE not listening",log.read_text()[-1200:]))
            sock.settimeout(.6)
            try:
                command(sock,'load "'+str(image)+'" 0',"Loading")
                command(sock,"break "+format(stop,"04x"),"BREAK:")
                command(sock,"g "+format(H,"04x"),"Stop on  exec")
                command(sock,'bsave "'+str(dump)+'" 0 '+
                        format(OUTPUT,"04x")+" "+format(OUTPUT+STRIDE*len(FIELDS)-1,"04x"),"Saving")
                sock.sendall(b"quit\n")
            finally:sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
    if not dump.exists():raise AssertionError((profile,entry,"no dump",log.read_text()[-1800:]))
    data=dump.read_bytes()
    assert len(data)==STRIDE*len(FIELDS),(profile,entry,len(data))
    stacks=set()
    for i,(x,y) in enumerate(vectors):
        v=[data[j*STRIDE+i] for j in range(len(FIELDS))]
        result=sum(v[j]<<(8*j) for j in range(6))
        exp=fixed_expected(x,y,entry.startswith("MATH_SMUL"))
        assert result==exp,(profile,entry,i,hex(result),hex(exp))
        xx=sum(v[8+j]<<(8*j) for j in range(4))
        yy=sum(v[12+j]<<(8*j) for j in range(4))
        assert (xx,yy)==(x,y),(profile,entry,"inputs",i)
        assert v[16]&1==0,(profile,entry,"carry not clear",i)
        assert v[18]==0xa6,(profile,entry,"marker",i)
        stacks.add(v[17])
    assert len(stacks)==1,(profile,entry,"unstable SP",stacks)
    return {"dump":data,"calls":len(vectors),"dump_sha256":sha(data),
            "signed_shift_correct":True,"carry_clear":True,"inputs_preserved":True,
            "stack_stable":True,"stack_pointer":next(iter(stacks)),
            "output_bytes_6_and_7_are_not_public_contract":True}
def main():
    report={"status":"PASS_NATIVE_VICE_INSTALLED_FIXED_SHR16",
      "native_cycle_timing_measured":False,"profile_count":len(P),
      "source_main_baseline_sha":BASE,"original_and_candidate_public_calls":0,
      "results":{}}
    state=json.loads((R/"RELEASE_STATUS.json").read_text())
    row=state["issue39_fixed_shr16_clc_2026_10_14"]
    assert row["status"] in ("PASS_STAGED_NATIVE_CI_PENDING","PASS_NATIVE_VICE_PR_MAIN_CI_PENDING")
    exe=os.getenv("VICE_WRAPPER","x64sc")
    with tempfile.TemporaryDirectory(prefix="fixed_shr16_native_") as tmpname:
        tmp=Path(tmpname)
        for pi,p in enumerate(P):
            old=subprocess.check_output(["git","show",BASE+":"+p+"/resident/math_"+p+"_game_math.prg"],cwd=R)
            new=(R/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes()
            assert sha(old)==row["old_sha256"][p] and sha(new)==row["new_sha256"][p]
            assert len(old)==len(new)
            offsets=[i for i,(a,b) in enumerate(zip(old,new)) if a!=b]
            assert len(offsets)==4,(p,offsets)
            entries={}
            for oi,entry in enumerate(OPS):
                oldr=run_native(p,old,entry,8900+pi*6+oi*2,tmp,exe)
                newr=run_native(p,new,entry,8901+pi*6+oi*2,tmp,exe)
                assert oldr["dump"]==newr["dump"],(p,entry,"native output/flags/stack changed")
                entries[entry]={"before_calls":oldr["calls"],"after_calls":newr["calls"],
                    "old_dump_sha256":oldr["dump_sha256"],
                    "candidate_dump_sha256":newr["dump_sha256"],
                    "bytewise_identical_native_records":True,
                    "carry_clear_inputs_and_stack_preserved":True}
                report["original_and_candidate_public_calls"]+=oldr["calls"]+newr["calls"]
                print("NATIVE FIXED SHR16",p,entry,"PASS",oldr["calls"]*2,flush=True)
            report["results"][p]={"changed_bytes":4,"entries":entries}
    assert report["original_and_candidate_public_calls"]==len(P)*len(OPS)*COUNT*2==480
    dest=R/"validation/review/ISSUE39_FIXED_SHR16_NATIVE_2026-10-14.json"
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("NATIVE VICE FIXED SHR16 OLD+NEW PASS",report["original_and_candidate_public_calls"])
if __name__=="__main__":main()
