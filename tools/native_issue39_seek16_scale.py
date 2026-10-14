#!/usr/bin/env python3
"""SEEK16_INIT paired baseline/candidate native VICE proof.

Public entry execution on actual five resident images and real V3/V4 REU
images. Native output/flag/state parity only; NO native cycle timing.
"""
from __future__ import annotations
import hashlib, json, os, random, socket, subprocess, sys, tempfile, time
from pathlib import Path

R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import CPU
from native_issue39_signed_multiply_family import api
from native_issue39_trig_angle import original_reu
from native_issue39_u24_txa_resident import command

P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
H=0x0e00
IN=0x0400
OUT=0x0600
STRIDE=64
COUNT=24
SLOT=3
def sha(b):return hashlib.sha256(b).hexdigest()
def original(p):return (R/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes()
def candidate(p):
    folder=(R/("build_hybrid/reference" if p==P[-1] else "build_source/reference")/p)
    man=json.loads((folder/"source_build_manifest.json").read_text())
    return (folder/man["output_prg"]).read_bytes()
def vectors():
    r=random.Random(0x39E16)
    seeds=[(0,0,0,0,0x8100),(0,0,319,199,0x8100),(319,199,0,0,0x8180),
           (0,0,319,0,0x8080),(319,0,0,199,0x8200),
           (255,100,256,100,0x8400),(256,100,255,100,0x8200),
           (1000,0,1100,199,0x8180),(50000,0,50200,255,0xFE80),
           (40000,100,40110,150,0x8100),(20,30,20,50,0x8100),
           (19,30,19,30,0x8100),(0,0,319,199,0x0100),
           (100,100,200,100,0x0200),(150,20,150,200,0x0400)]
    while len(seeds)<COUNT:
        x0=r.randrange(512)
        x1=r.randrange(512)
        seeds.append((x0,r.randrange(200),x1,r.randrange(200),
            r.choice((0x8100,0x8180,0x8200,0x8400,0xFE80,0x0100))))
    return seeds

def fields(A):
    s="MATH_SEEK16_"
    names=["POS_XL","POS_XH","POS_Y","TGT_XL","TGT_XH","TGT_Y",
           "RL","RM","RH","ERRL","ERRH","DMAJL","DMAJH","KF","KI",
           "REML","REMH","VXL","VXH","VY"]
    from seek_kernel import S16_FIELDS
    offsets=dict(S16_FIELDS)
    base=A[s+"POS_XL"]
    return [A["MATH_X"],A["MATH_X"]+1,A["MATH_Y"],A["MATH_N"],A["MATH_N"]+1,
            0xc030,0xc032,0xc033]+[base+offsets[n]+SLOT for n in names]

def harness(A):
    code=bytearray()
    def b(*data):code.extend(data)
    def absop(op,a):b(op,a&255,a>>8)
    b(0x78,0xd8,0xa9,0x35,0x85,0x01)  # SEI CLD, I/O visible and RAM
    absop(0x20,A["MATH_INIT"])
    b(0xa2,0x00)
    loop=H+len(code)
    S="MATH_SEEK16_"
    store=[A[S+"POS_XL"]+SLOT,A[S+"POS_XH"]+SLOT,A[S+"POS_Y"]+SLOT,
           A["MATH_X"],A["MATH_X"]+1,A["MATH_Y"],
           A["MATH_N"],A["MATH_N"]+1]
    b(0x8a,0x48)   # save corpus index before overwriting X with slot
    # Index was pushed, but still present in X for indexed case reads.
    for j,dst in enumerate(store):
        absop(0xbd,IN+j*STRIDE)
        absop(0x8d,dst)
    b(0xa2,SLOT,0x38)  # LDX slot, SEC: exercise incoming carry=1
    absop(0x20,A["MATH_SEEK16_INIT"])
    absop(0x8e,0xc033) # record returned X before TSX
    b(0x08,0x68)
    absop(0x8d,0xc030) # return status
    b(0xba)
    absop(0x8e,0xc032) # wrapper stack pointer
    b(0x68,0xaa)       # restore index
    for j,src in enumerate(fields(A)):
        absop(0xad,src)
        absop(0x9d,OUT+j*STRIDE)
    b(0xe8,0xe0,COUNT,0xf0,0x03)  # INX CPX COUNT BEQ skip
    absop(0x4c,loop)
    stop=H+len(code)
    absop(0x4c,stop)
    assert len(code)<0x200 and OUT+len(fields(A))*STRIDE<=H,(len(code),len(fields(A)))
    return bytes(code),stop

def prepare(prg,A):
    mem=bytearray(65536)
    ld=int.from_bytes(prg[:2],"little")
    mem[ld:ld+len(prg)-2]=prg[2:]
    code,stop=harness(A)
    mem[H:H+len(code)]=code
    for i,(x0,y0,x1,y1,speed) in enumerate(vectors()):
        for j,v in enumerate((x0&255,x0>>8,y0,x1&255,x1>>8,y1,speed&255,speed>>8)):
            mem[IN+j*STRIDE+i]=v
    return bytes([IN&255,IN>>8])+mem[IN:0xd000],stop

def native(p,prg,reu,port,tmp,exe):
    A=api(p)
    img,stop=prepare(prg,A)
    image=tmp/(p+"_"+str(port)+".prg")
    dump=tmp/(p+"_"+str(port)+".dump")
    log=tmp/(p+"_"+str(port)+".log")
    image.write_bytes(img)
    cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp"]
    if reu:
        cmd+=["-reu","-reusize",("512" if p==P[2] else "16384"),"-reuimage",str(reu)]
    cmd+=["-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}","-initbreak","reset"]
    with log.open("w") as out:
        proc=subprocess.Popen(cmd,cwd=tmp,stdout=out,stderr=out)
        try:
            sock=None
            for _ in range(250):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.2);break
                except (ConnectionRefusedError,TimeoutError):time.sleep(.06)
            if sock is None:raise RuntimeError(("VICE failed",p,log.read_text()[-1700:]))
            sock.settimeout(1.5)
            try:
                command(sock,'load "'+str(image)+'" 0',"Loading")
                command(sock,"break "+format(stop,"04x"),"BREAK:")
                command(sock,"g "+format(H,"04x"),"Stop on  exec")
                command(sock,'bsave "'+str(dump)+'" 0 '+format(OUT,"04x")+" "+
                        format(OUT+len(fields(A))*STRIDE-1,"04x"),"Saving")
                sock.sendall(b"quit\n")
            finally:sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
    assert dump.exists(),("VICE no output",p,log.read_text()[-1800:])
    data=dump.read_bytes()
    assert len(data)==len(fields(A))*STRIDE
    return data

def check_model(p,prg,reu,data):
    A=api(p)
    mem=bytearray(65536)
    load=int.from_bytes(prg[:2],"little")
    mem[load:load+len(prg)-2]=prg[2:]
    c=CPU(mem,reu=bytearray(reu.read_bytes()) if reu else None)
    c.d=0
    c.call(A["MATH_INIT"],2_000_000)
    fld=fields(A)
    for i,(x0,y0,x1,y1,speed) in enumerate(vectors()):
        for addr,v in ((A["MATH_SEEK16_POS_XL"]+SLOT,x0&255),
                       (A["MATH_SEEK16_POS_XH"]+SLOT,x0>>8),
                       (A["MATH_SEEK16_POS_Y"]+SLOT,y0),
                       (A["MATH_X"],x1&255),(A["MATH_X"]+1,x1>>8),
                       (A["MATH_Y"],y1),(A["MATH_N"],speed&255),(A["MATH_N"]+1,speed>>8)):
            c.mem[addr]=v
        c.c=1;c.x=SLOT;c.d=0
        c.call(A["MATH_SEEK16_INIT"],200000)
        for j,addr in enumerate(fld):
            got=data[j*STRIDE+i]
            if addr==0xc030:
                # Hardware PHP sets B; the harness runs SEI and has a different
                # pre-call N/Z history. The paired native images compare *all*
                # actual status bits; the independent model asserts carry.
                assert (got & 1)==c.c,(p,i,'native carry',got,c.c)
                continue
            elif addr==0xc032:expected=0xfc # saved caller X index is on stack
            elif addr==0xc033:expected=SLOT
            else:expected=c.mem[addr]
            assert got==expected,(p,i,j,hex(addr),got,expected)
    return True

def main():
    exe=os.getenv("VICE_WRAPPER","x64sc")
    status=json.loads((R/"RELEASE_STATUS.json").read_text())
    report={"status":"PASS_NATIVE_VICE_PAIRED_SEEK16_INIT",
            "native_cycles_measured":False,"public_calls":0,"profiles":{}}
    with tempfile.TemporaryDirectory(prefix="seek16_native_") as folder:
        tmp=Path(folder)
        for pi,p in enumerate(P):
            old,new=original(p),candidate(p)
            reu=original_reu(p)
            assert sha(old)==status["reference_prg_sha256"][p]
            assert old!=new and len(old)==len(new)
            if reu:assert sha(reu.read_bytes())==status["reference_reu_sha256"][p]
            a=native(p,old,reu,11000+pi*4,tmp,exe)
            b=native(p,new,reu,11001+pi*4,tmp,exe)
            if a!=b:
                labels=fields(api(p)); dif=[]
                for j,addr in enumerate(labels):
                    for i in range(COUNT):
                        va=a[j*STRIDE+i];vb=b[j*STRIDE+i]
                        if va!=vb:
                            dif.append((i,hex(addr),va,vb))
                            if len(dif)>=16:break
                    if len(dif)>=16:break
                raise AssertionError((p,"native old/new differ",sha(a),sha(b),dif))
            check_model(p,old,reu,a)
            check_model(p,new,reu,b)
            report["profiles"][p]={"cases_per_image":COUNT,"output_sha256":sha(a),
                        "old_prg":sha(old),"candidate_prg":sha(new),
                        "bytewise_equal_with_model":True}
            report["public_calls"]+=2*COUNT
            print("SEEK16 native",p,COUNT,"paired calls PASS",flush=True)
    assert report["public_calls"]==240
    dest=R/"validation/review/ISSUE39_SEEK16_SCALE_NATIVE_2026-10-14.json"
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("SEEK16 240 NATIVE PUBLIC CALLS PASS")
if __name__=="__main__":main()
