#!/usr/bin/env python3
"""Actual VICE x64sc REU installed public Turbo16/32 and V4 QS16 test.

24 deterministic operands per mode/profile, real 512 KiB or 16 MiB REU image,
native BEGIN/CALL/END, carry/results/input/stack. CPU cycle timing is NOT
measured. REU source alternate-map correctness is separately model-audited.
"""
from pathlib import Path
import hashlib,json,os,socket,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from native_issue39_signed_multiply_family import api,pairs,FIELDS,STRIDE,COUNT,H,INPUT,OUTPUT,sha
from native_issue39_u24_txa_resident import command
P=("v3_reu_512k","v4_reu_16m")
OPS=(("MATH_REU_UMUL16",16),("MATH_REU_UMUL32",32))
IO=0xC000
def build(api,entry,bits):
    b=bytearray()
    def emit(*data):b.extend(data)
    def absop(op,addr):emit(op,addr&255,addr>>8)
    emit(0x78,0xD8,0xA9,0x34,0x85,0x01)   # SEI/CLD, RAM under ROM
    absop(0x20,api["MATH_INIT"])
    absop(0x20,api[entry+"_BEGIN"])
    emit(0xA2,0x00)
    loop=H+len(b)
    for j in range(8):
        absop(0xBD,INPUT+j*STRIDE)
        absop(0x8D,IO+j)
    emit(0xA9,0x91)
    for j in range(8):absop(0x8D,IO+8+j)
    emit(0xA9,0xA6);absop(0x8D,0xC024)
    emit(0x8A,0x48) # save case index on stack
    emit(0x38);absop(0x20,api[entry])
    emit(0x08,0x68);absop(0x8D,0xC030) # PHP PLA flags
    emit(0xBA);absop(0x8E,0xC032)      # stack pointer with loop index pushed
    emit(0x68,0xAA)
    for j,addr in enumerate(FIELDS):
        absop(0xAD,addr);absop(0x9D,OUTPUT+j*STRIDE)
    emit(0xE8,0xE0,COUNT,0xF0,0x03)
    absop(0x4C,loop)
    absop(0x20,api[entry+"_END"])
    stop=H+len(b)
    absop(0x4C,stop)
    assert len(b)<0x300,(entry,len(b))
    return bytes(b),stop
def run(profile,entry,bits,port,tmp,exe,prg,reu):
    ld=int.from_bytes(prg[:2],"little")
    assert ld==0x1000
    m=bytearray(65536);m[ld:ld+len(prg)-2]=prg[2:]
    code,stop=build(api(profile),entry,bits)
    m[H:H+len(code)]=code
    vectors=pairs(bits)
    n=bits//8
    for i,(x,y) in enumerate(vectors):
        for j in range(8):
            val=(x>>(8*j))&255 if j<n else (
                (y>>(8*(j-4)))&255 if 4<=j<4+n else 0x5c)
            m[INPUT+j*STRIDE+i]=val
    image=tmp/f"{profile}_{entry}.prg"
    dump=tmp/f"{profile}_{entry}.dump"
    log=tmp/f"{profile}_{entry}.log"
    image.write_bytes(bytes([INPUT&255,INPUT>>8])+m[INPUT:0xD000])
    size="512" if profile==P[0] else "16384"
    args=[str(exe),"-console","-silent","-sounddev","dummy","-warp",
          "-reu","-reusize",size,"-reuimage",str(reu),
          "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
          "-initbreak","reset"]
    with log.open("w") as output:
        proc=subprocess.Popen(args,cwd=tmp,stdout=output,stderr=output)
        try:
            sock=None
            for _ in range(240):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.25)
                    break
                except (ConnectionRefusedError,TimeoutError):time.sleep(.075)
            if sock is None:raise RuntimeError((profile,entry,"VICE remote unavailable",log.read_text()[-1500:]))
            sock.settimeout(1)
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
    if not dump.exists():raise AssertionError((profile,entry,"native missing dump",log.read_text()[-2200:]))
    data=dump.read_bytes()
    assert len(data)==STRIDE*len(FIELDS),(profile,entry,len(data))
    stacks=set()
    for i,(x,y) in enumerate(vectors):
        v=[data[j*STRIDE+i] for j in range(len(FIELDS))]
        result=sum(v[j]<<(8*j) for j in range(8))
        actual=result & ((1<<(2*bits))-1)
        expected=x*y
        assert actual==expected,(profile,entry,i,hex(actual),hex(expected))
        assert v[2*n:8]==[0x91]*(8-2*n),(profile,entry,"sentinel",i)
        xx=sum(v[8+j]<<(8*j) for j in range(n))
        yy=sum(v[12+j]<<(8*j) for j in range(n))
        assert xx==x and yy==y,(profile,entry,"operands",i)
        assert v[16]&1==0 and v[18]==0xA6,(profile,entry,"carry/marker",i)
        stacks.add(v[17])
    assert len(stacks)==1,(profile,entry,"stack drift",stacks)
    return {"calls":COUNT,"native_reu_profile":size+" KiB",
         "installed_reu_image_sha256":sha(reu.read_bytes()),
         "correct_products_inputs_carry_stack":True,
         "same_stack_pointer":next(iter(stacks)),
         "result_dump_sha256":sha(data),"native_cycle_timing_measured":False}
def main():
    st=json.loads((R/"RELEASE_STATUS.json").read_text())
    proof=json.loads((R/"validation/review/ISSUE39_REU_MULTIPLY_MATCHED_CORPUS_2026-10-14.json").read_text())
    assert proof["status"]=="PASS_PUBLIC_REU_MULTIPLY_MODES"
    report={"status":"PASS_NATIVE_VICE_REU_MODES","native_cycle_timing_measured":False,
      "total_public_calls":0,"profiles":{},"native_VICE_reu_flags":True}
    exe=os.getenv("VICE_WRAPPER","x64sc")
    with tempfile.TemporaryDirectory(prefix="issue39_native_reu_") as d:
        td=Path(d)
        for pi,profile in enumerate(P):
            prg=(R/profile/"resident"/f"math_{profile}_game_math.prg").read_bytes()
            reu=R/profile/"reu"/("c64_math_v3_512k_game_math.reu" if pi==0 else "c64_math_v4_16m_game_math.reu")
            assert sha(prg)==st["reference_prg_sha256"][profile]
            assert sha(reu.read_bytes())==st["reference_reu_sha256"][profile]
            report["profiles"][profile]={}
            modes=OPS+((("MATH_REU_QS16",16),) if pi==1 else ())
            for mi,(entry,bits) in enumerate(modes):
                result=run(profile,entry,bits,8750+pi*10+mi,td,exe,prg,reu)
                report["profiles"][profile][entry]=result
                report["total_public_calls"]+=result["calls"]
                print("NATIVE X64SC REU",profile,entry,result["calls"],"PASS",flush=True)
    assert report["total_public_calls"]==5*COUNT==120
    out=R/"validation/review/ISSUE39_REU_MULTIPLY_NATIVE_2026-10-14.json"
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("NATIVE REU MODE PROOF PASS",report["total_public_calls"])
if __name__=="__main__":main()
