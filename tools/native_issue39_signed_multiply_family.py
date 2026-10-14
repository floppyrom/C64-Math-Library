#!/usr/bin/env python3
"""Native x64sc installed signed public entry audit, five profiles, no code changes.

Uses published binary residents; 24 deterministic signed pairs per width/profile.
READY is primed through ordinary SMUL32 to meet its documented state contract.
No attempt is made to measure native CPU cycles.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,os,random,re,socket,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from native_issue39_u24_txa_resident import command
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
OPS=(("MATH_SMUL8",8),("MATH_SMUL16",16),("MATH_SMUL24",24),
     ("MATH_SMUL32",32),("MATH_SMUL32_READY",32))
H=0x0b00;INPUT=0x0400;OUTPUT=0x0600;STRIDE=64;COUNT=24;IO=0xc000
FIELDS=[IO+8+i for i in range(8)]+[IO+i for i in range(4)]+[
        IO+4+i for i in range(4)]+[0xc030,0xc032,0xc024]
assert OUTPUT+len(FIELDS)*STRIDE < H
def sha(data):return hashlib.sha256(data).hexdigest()
def api(profile):
    data=(ROOT/profile/"resident"/"math_api.inc").read_text()
    return {m.group(1):int(m.group(2),16) for m in
            re.finditer(r"(?m)^\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)",data)}
def pairs(bits):
    m=(1<<bits)-1;s=1<<(bits-1)
    edge=[0,1,2,3,7,127,128,255,s-1,s,s+1,m-1,m]
    out=[(0,0),(m,m),(s,s),(s-1,s-1),(1,m),(m,1),
         (m,s-1),(s-1,m),(s,s-1),(s-1,s)]
    rng=random.Random(0x39534700+bits)
    while len(out)<COUNT:
        out.append((rng.choice(edge) if rng.randrange(3)==0 else rng.getrandbits(bits),
                    rng.choice(edge) if rng.randrange(3)==0 else rng.getrandbits(bits)))
    return out
def make_harness(api,entry,bits):
    out=bytearray()
    def b(*xs):out.extend(xs)
    def absop(op,address):b(op,address&255,address>>8)
    b(0x78,0xd8,0xa9,0x34,0x85,0x01) # SEI CLD and all RAM
    absop(0x20,api["MATH_INIT"])
    b(0xa2,0x00)
    loop=H+len(out)
    for j in range(8): # initialize ALL public X/Y bytes
        absop(0xbd,INPUT+j*STRIDE)
        absop(0x8d,IO+(j if j<4 else j))
    b(0xa9,0x91)
    for j in range(8):absop(0x8d,IO+8+j)
    b(0xa9,0xa6);absop(0x8d,0xc024)
    b(0x8a,0x48) # PHA original loop X
    if entry=="MATH_SMUL32_READY":
        b(0x38);absop(0x20,api["MATH_SMUL32"]) # prepare pointers
        b(0xa9,0x91)
        for j in range(8):absop(0x8d,IO+8+j)
    b(0x38)
    absop(0x20,api[entry])
    b(0x08,0x68);absop(0x8d,0xc030) # PHP PLA flags
    b(0xba);absop(0x8e,0xc032) # saved loop index still pushed
    b(0x68,0xaa)
    for j,addr in enumerate(FIELDS):
        absop(0xad,addr);absop(0x9d,OUTPUT+j*STRIDE)
    b(0xe8,0xe0,COUNT,0xf0,0x03)
    absop(0x4c,loop)
    stop=H+len(out);absop(0x4c,stop)
    assert len(out)<0x300,(entry,len(out))
    return bytes(out),stop
def native(profile,prg,entry,bits,port,tmp,exe):
    base=int.from_bytes(prg[:2],"little")
    assert base==0x1000 and len(prg)==49042,(profile,"unexpected PRG span")
    mem=bytearray(65536);mem[base:base+len(prg)-2]=prg[2:]
    code,stop=make_harness(api(profile),entry,bits);mem[H:H+len(code)]=code
    vectors=pairs(bits);n=bits//8
    for i,(x,y) in enumerate(vectors):
        for j in range(8):
            b=((x>>(8*j))&255) if j<n else ((y>>(8*(j-4)))&255) if 4<=j<4+n else 0x5c
            if j>=4 and j<4+n:b=(y>>(8*(j-4)))&255
            if j<n:b=(x>>(8*j))&255
            mem[INPUT+j*STRIDE+i]=b
    image=tmp/(profile+"_"+entry+".prg")
    dump=tmp/(profile+"_"+entry+".dump")
    log=tmp/(profile+"_"+entry+".log")
    image.write_bytes(bytes([INPUT&255,INPUT>>8])+mem[INPUT:0xd000])
    cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp",
      "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
      "-initbreak","reset"]
    with log.open("w") as dest:
        process=subprocess.Popen(cmd,cwd=tmp,stdout=dest,stderr=dest)
        try:
            sock=None
            for _ in range(200):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=0.2);break
                except (ConnectionRefusedError,TimeoutError):time.sleep(.07)
            if sock is None:raise RuntimeError((entry,"VICE unavailable",log.read_text()[-1200:]))
            sock.settimeout(.6)
            try:
                command(sock,'load "'+str(image)+'" 0',"Loading")
                command(sock,"break "+format(stop,"04x"),"BREAK:")
                command(sock,"g "+format(H,"04x"),"Stop on  exec")
                command(sock,'bsave "'+str(dump)+'" 0 '+format(OUTPUT,"04x")+" "+
                    format(OUTPUT+len(FIELDS)*STRIDE-1,"04x"),"Saving")
                sock.sendall(b"quit\n")
            finally:sock.close()
        finally:
            process.terminate()
            try:process.wait(timeout=3)
            except subprocess.TimeoutExpired:process.kill()
    if not dump.exists():raise RuntimeError((profile,entry,"no dump",log.read_text()[-1200:]))
    blob=dump.read_bytes()
    assert len(blob)==STRIDE*len(FIELDS),(entry,len(blob))
    stacks=set()
    for i,(x,y) in enumerate(vectors):
        values=[blob[j*STRIDE+i] for j in range(len(FIELDS))]
        out=sum(values[k]<<(8*k) for k in range(8))
        xx=sum(values[k+8]<<(8*k) for k in range(4))
        yy=sum(values[k+12]<<(8*k) for k in range(4))
        s=lambda v:v-(1<<bits) if v&(1<<(bits-1)) else v
        expected=(s(x)*s(y))&((1<<(bits*2))-1)
        assert out&((1<<(bits*2))-1)==expected,(profile,entry,i,hex(out),hex(expected))
        assert values[bits//4:8]==[0x91]*(8-bits//4),(profile,entry,"sentinel",i,values)
        assert xx&((1<<bits)-1)==x and yy&((1<<bits)-1)==y,(profile,entry,"input",i)
        assert values[16]&1==0 and values[18]==0xa6,(profile,entry,"carry/marker",i)
        stacks.add(values[17])
    assert len(stacks)==1,(profile,entry,"stack drift",stacks)
    return {"pairs":COUNT,"public_results_correct":True,
       "carry_clear":True,"inputs_preserved":True,"result_sentinels_preserved":True,
       "stable_stack_pointer":list(stacks)[0],"native_output_dump_sha256":sha(blob),
       "ready_prepared_by_ordinary_call":entry=="MATH_SMUL32_READY"}
def main():
    p={"status":"PASS_NATIVE_VICE_PUBLIC_SIGNED_FAMILY",
       "native_cycle_timing_measured":False,"public_abi_unchanged":True,
       "profiles":{},"captured_public_calls":0,"additional_ready_preparation_calls":0}
    state=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
    exe=os.getenv("VICE_WRAPPER","x64sc")
    with tempfile.TemporaryDirectory(prefix="issue39_signed_family_vice_") as t:
        tmp=Path(t)
        for pi,profile in enumerate(P):
            blob=(ROOT/profile/"resident"/f"math_{profile}_game_math.prg").read_bytes()
            assert sha(blob)==state["reference_prg_sha256"][profile]
            row={}
            for oi,(entry,bits) in enumerate(OPS):
                row[entry]=native(profile,blob,entry,bits,8600+pi*10+oi,tmp,exe)
                p["captured_public_calls"]+=COUNT
                if entry=="MATH_SMUL32_READY":p["additional_ready_preparation_calls"]+=COUNT
                print("NATIVE SIGNED",profile,entry,"PASS",COUNT,flush=True)
            p["profiles"][profile]=row
    assert p["captured_public_calls"]==len(P)*len(OPS)*COUNT==600
    dest=ROOT/"validation/review/ISSUE39_SIGNED_MULTIPLY_NATIVE_2026-10-14.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n")
    print("NATIVE SIGNED FAMILY VICE PASS",p["captured_public_calls"])
if __name__=="__main__":main()
