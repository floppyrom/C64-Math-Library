#!/usr/bin/env python3
"""Native VICE public trig/angle proof on installed V1..V5, 24 vectors/entry.

Compares real x64sc output bytes with the shipped CPU-model public ABI.
V3/V4 use their real REU images with I/O visible at $01=$35. Native cycles
are NOT measured. All ordinary phase values already checked exhaustively by
the independent source-build and ATAN2 proof.
"""
from pathlib import Path
import hashlib,json,os,socket,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import CPU
from native_issue39_signed_multiply_family import api
from native_issue39_u24_txa_resident import command
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
OPS=("MATH_SIN8","MATH_COS8","MATH_SINCOS8","MATH_ATAN2_8")
PHASES=(0,1,2,3,7,8,15,16,31,32,47,63,64,65,95,127,
        128,129,160,191,192,223,254,255)
COUNT=len(PHASES);STRIDE=64;INPUT=0x0400;OUTPUT=0x0600;H=0x0B00
IO=0xC000
FIELDS=(IO,IO+4,IO+8,IO+9,IO+0x30,IO+0x32,IO+0x24)
def sha(blob):return hashlib.sha256(blob).hexdigest()
def make_code(api_map,entry):
    out=bytearray()
    def b(*data):out.extend(data)
    def absop(op,addr):b(op,addr&255,addr>>8)
    b(0x78,0xd8,0xa9,0x35,0x85,0x01) # I/O visible for V3/V4 REU
    absop(0x20,api_map["MATH_INIT"])
    b(0xa2,0x00) # LDX #0
    loop=H+len(out)
    absop(0xbd,INPUT);absop(0x8d,IO)
    absop(0xbd,INPUT+STRIDE);absop(0x8d,IO+4)
    b(0xa9,0x91);absop(0x8d,IO+8)
    b(0xa9,0x5a);absop(0x8d,IO+9)
    b(0xa9,0xa6);absop(0x8d,IO+0x24)
    b(0x8a,0x48,0x38)  # TXA PHA SEC
    absop(0x20,api_map[entry])
    b(0x08,0x68);absop(0x8d,IO+0x30) # PHP, PLA flags
    b(0xba);absop(0x8e,IO+0x32) # TSX STX stack pointer
    b(0x68,0xaa) # PLA TAX loop-index
    for j,field in enumerate(FIELDS):
        absop(0xad,field);absop(0x9d,OUTPUT+j*STRIDE)
    b(0xe8,0xe0,COUNT,0xf0,0x03) # INX CPX COUNT BEQ +3
    absop(0x4c,loop)
    stop=H+len(out)
    absop(0x4c,stop)
    assert len(out)<0x300
    return bytes(out),stop
def original_prg(p):
    return (R/p/"resident"/("math_"+p+"_game_math.prg")).read_bytes()
def original_reu(p):
    if p=="v3_reu_512k":return R/p/"reu/c64_math_v3_512k_game_math.reu"
    if p=="v4_reu_16m":return R/p/"reu/c64_math_v4_16m_game_math.reu"
    return None
def cpu_reference(p,entry,prg,reu):
    mem=bytearray(65536)
    load=int.from_bytes(prg[:2],"little")
    mem[load:load+len(prg)-2]=prg[2:]
    model=CPU(mem,reu=bytearray(reu.read_bytes()) if reu else None)
    names=api(p)
    model.d=0;model.call(names["MATH_INIT"],2_000_000)
    result=[]
    for phase in PHASES:
        y=(phase*37+83)&255
        model.mem[IO]=phase;model.mem[IO+4]=y
        model.mem[IO+8]=0x91;model.mem[IO+9]=0x5a
        model.c=1;model.d=0
        model.call(names[entry],2_000_000)
        assert model.mem[IO]==phase and model.mem[IO+4]==y
        assert model.sp==0xfd and model.c==0
        result.append((model.mem[IO+8],model.mem[IO+9]))
    return result
def native(p,entry,prg,reu,port,tmp,exe):
    ld=int.from_bytes(prg[:2],"little")
    mem=bytearray(65536);mem[ld:ld+len(prg)-2]=prg[2:]
    code,stop=make_code(api(p),entry)
    mem[H:H+len(code)]=code
    for i,phase in enumerate(PHASES):
        mem[INPUT+i]=phase
        mem[INPUT+STRIDE+i]=(phase*37+83)&255
    name=p+"_"+entry
    image=tmp/(name+".prg")
    dump=tmp/(name+".dump")
    log=tmp/(name+".log")
    image.write_bytes(bytes([INPUT&255,INPUT>>8])+mem[INPUT:0xd000])
    cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp"]
    if reu:
        cmd+=["-reu","-reusize",("512" if p=="v3_reu_512k" else "16384"),
              "-reuimage",str(reu)]
    cmd+=["-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
          "-initbreak","reset"]
    with log.open("w") as out:
        proc=subprocess.Popen(cmd,cwd=tmp,stdout=out,stderr=out)
        try:
            sock=None
            for _ in range(220):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.2)
                    break
                except (ConnectionRefusedError,TimeoutError):time.sleep(.07)
            if sock is None:raise RuntimeError((name,"VICE unavailable",log.read_text()[-1400:]))
            sock.settimeout(0.9)
            try:
                command(sock,'load "'+str(image)+'" 0',"Loading")
                command(sock,"break "+format(stop,"04x"),"BREAK:")
                command(sock,"g "+format(H,"04x"),"Stop on  exec")
                command(sock,'bsave "'+str(dump)+'" 0 '+format(OUTPUT,"04x")+" "+
                             format(OUTPUT+len(FIELDS)*STRIDE-1,"04x"),"Saving")
                sock.sendall(b"quit\n")
            finally:sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
    if not dump.exists():raise AssertionError((name,"missing native result",log.read_text()[-1200:]))
    result=dump.read_bytes()
    assert len(result)==len(FIELDS)*STRIDE,(name,len(result))
    model=cpu_reference(p,entry,prg,reu)
    stacks=set()
    for i,phase in enumerate(PHASES):
        x,y,z0,z1,flags,sp,marker=[result[j*STRIDE+i] for j in range(len(FIELDS))]
        assert x==phase and y==((phase*37+83)&255),(name,"inputs",i)
        assert (z0,z1)==model[i],(name,"reference",i,(z0,z1),model[i])
        assert not flags&1 and marker==0xa6,(name,"carry or marker",i)
        stacks.add(sp)
    assert len(stacks)==1,(name,"stack imbalance",stacks)
    return {"cases":COUNT,"correct_output_and_inputs":True,
      "carry_clear":True,"same_hardware_stack_pointer":next(iter(stacks)),
      "reu_image_sha256":sha(reu.read_bytes()) if reu else None,
      "native_output_sha256":sha(result),
      "matched_model_public_results":True}
def main():
    release=json.loads((R/"RELEASE_STATUS.json").read_text())
    report={"status":"PASS_NATIVE_VICE_TRIG_PUBLIC",
            "native_cycle_timing_measured":False,"profiles":{},
            "public_calls":0,"private_optisearch_source_published":False}
    exe=os.getenv("VICE_WRAPPER","x64sc")
    with tempfile.TemporaryDirectory(prefix="issue39_native_trig_") as t:
        tmp=Path(t)
        for pi,p in enumerate(P):
            resident=original_prg(p);reu=original_reu(p)
            assert sha(resident)==release["reference_prg_sha256"][p]
            if reu:assert sha(reu.read_bytes())==release["reference_reu_sha256"][p]
            report["profiles"][p]={}
            for oi,op in enumerate(OPS):
                item=native(p,op,resident,reu,8300+pi*8+oi,tmp,exe)
                report["profiles"][p][op]=item;report["public_calls"]+=COUNT
                print("NATIVE TRIG",p,op,"PASS",COUNT,flush=True)
    assert report["public_calls"]==480
    dest=R/"validation/review/ISSUE39_TRIG_ANGLE_NATIVE_2026-10-14.json"
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("NATIVE VICE TRIG FAMILY PUBLIC PROOF PASS",report["public_calls"],flush=True)
if __name__=="__main__":main()
