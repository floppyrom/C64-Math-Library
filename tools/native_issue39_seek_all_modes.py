#!/usr/bin/env python3
"""Issue39: native x64sc all public SEEK8/16 steppers, actual V3/V4 REU.

This is actual 6502 code running inside VICE with hardware-observed output,
not a re-run of the Python CPU model. Compares carry, position, X and stack
on all 16 frames per test, including repeated post-arrival calls. No native
cycle counts are claimed.
"""
from __future__ import annotations
import hashlib,json,os,socket,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
sys.path.insert(0,str(ROOT/"routines/movement"))
from native_issue39_signed_multiply_family import api
from native_issue39_trig_angle import original_reu
from native_issue39_u24_txa_resident import command
from seek_model import expected_frames

P=("v1_balanced","v2_pareto_fast","v3_reu_512k",
   "v4_reu_16m","v5_hybrid_lowzp")
SCENARIOS=((8,"step",0x0180),(8,"step",0x8180),
           (8,"int",0x0200),(8,"one",0x0100),
           (16,"step",0x0180),(16,"step",0x8180),
           (16,"int",0x0200),(16,"one",0x0100))
FRAMES=16
FIELDS=6
OUT=0x0500
ENTRY=0x0900
IDX=0x03f0
SAVE_X=0xc033
SLOT=2

def sha(b):return hashlib.sha256(b).hexdigest()

def resident(profile):
    return (ROOT/profile/"resident"/f"math_{profile}_game_math.prg").read_bytes()

def build_code(A):
    prog=bytearray()
    def emit(*values):prog.extend(values)
    def absop(op,where):emit(op,where&255,(where>>8)&255)
    def setbyte(where,value):
        emit(0xa9,value&255)
        absop(0x8d,where)
    def jsr(symbol):absop(0x20,A[symbol])
    # Ensure normal C64 RAM/I/O map and deterministic decimal/interrupt flags.
    emit(0x78,0xd8,0xa9,0x35,0x85,0x01)
    jsr("MATH_INIT")
    for scenario_index,(width,mode,speed) in enumerate(SCENARIOS):
        start_x=1 if width==8 else 256
        target_x=start_x+8
        start_y=2;target_y=7
        prefix=f"MATH_SEEK{width}_"
        if width==8:
            setbyte(A["MATH_SEEK8_POS_X"]+SLOT,start_x)
            setbyte(A["MATH_SEEK8_POS_Y"]+SLOT,start_y)
            posxl=A["MATH_SEEK8_POS_X"]+SLOT
            posxh=None
            posy=A["MATH_SEEK8_POS_Y"]+SLOT
        else:
            setbyte(A["MATH_SEEK16_POS_XL"]+SLOT,start_x&255)
            setbyte(A["MATH_SEEK16_POS_XH"]+SLOT,start_x>>8)
            setbyte(A["MATH_SEEK16_POS_Y"]+SLOT,start_y)
            posxl=A["MATH_SEEK16_POS_XL"]+SLOT
            posxh=A["MATH_SEEK16_POS_XH"]+SLOT
            posy=A["MATH_SEEK16_POS_Y"]+SLOT
        setbyte(A["MATH_X"],target_x&255)
        setbyte(A["MATH_X"]+1,target_x>>8)
        setbyte(A["MATH_Y"],target_y)
        setbyte(A["MATH_N"],speed&255)
        setbyte(A["MATH_N"]+1,speed>>8)
        emit(0xa2,SLOT)
        jsr(prefix+"INIT")
        setbyte(IDX,0)
        loop=ENTRY+len(prog)
        emit(0xa2,SLOT)
        step={"step":"STEP","int":"STEP_INT","one":"STEP1"}[mode]
        jsr(prefix+step)
        absop(0x8e,SAVE_X)                # snapshot public X before TSX
        emit(0x08,0x68)                  # PHP / PLA
        absop(0xac,IDX)                  # LDY frame index
        row=OUT+scenario_index*FIELDS*FRAMES
        absop(0x99,row+3*FRAMES)         # status (returned carry)
        absop(0xad,posxl)
        absop(0x99,row)
        if posxh is None:emit(0xa9,0)
        else:absop(0xad,posxh)
        absop(0x99,row+FRAMES)
        absop(0xad,posy)
        absop(0x99,row+2*FRAMES)
        absop(0xad,SAVE_X)
        absop(0x99,row+4*FRAMES)
        emit(0xba,0x8a)                  # TSX / TXA (return stack)
        absop(0x99,row+5*FRAMES)
        absop(0xee,IDX)                  # INC frame index
        absop(0xad,IDX)
        emit(0xc9,FRAMES,0xf0,0x03)     # CMP #16 ; BEQ skip 3-byte JMP
        absop(0x4c,loop)
    stop=ENTRY+len(prog)
    absop(0x4c,stop)
    assert stop<0x1000,(hex(stop),len(prog))
    assert OUT+len(SCENARIOS)*FIELDS*FRAMES<=ENTRY
    return bytes(prog),stop

def native(profile,port,tmp,exe):
    prg=resident(profile)
    a=api(profile)
    mem=bytearray(65536)
    load=int.from_bytes(prg[:2],"little")
    mem[load:load+len(prg)-2]=prg[2:]
    code,stop=build_code(a)
    mem[ENTRY:ENTRY+len(code)]=code
    image=tmp/(profile+"_seek_all.prg")
    image.write_bytes(bytes((0,4))+mem[0x0400:0xd000])
    dump=tmp/(profile+"_seek_all.dump")
    log=tmp/(profile+"_seek_all.log")
    reu=original_reu(profile)
    cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp"]
    if reu:
        assert reu.is_file()
        cmd+=["-reu","-reusize",("512" if profile==P[2] else "16384"),
              "-reuimage",str(reu)]
    cmd+=["-remotemonitor","-remotemonitoraddress",
          f"127.0.0.1:{port}","-initbreak","reset"]
    with log.open("w") as out:
        proc=subprocess.Popen(cmd,cwd=tmp,stdout=out,stderr=out)
        try:
            sock=None
            for _ in range(250):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.2)
                    break
                except (ConnectionRefusedError,TimeoutError):time.sleep(.06)
            if sock is None:raise RuntimeError((profile,"VICE failed",log.read_text()[-1400:]))
            sock.settimeout(1.5)
            try:
                command(sock,'load "'+str(image)+'" 0',"Loading")
                command(sock,"break "+format(stop,"04x"),"BREAK:")
                command(sock,"g "+format(ENTRY,"04x"),"Stop on  exec")
                command(sock,'bsave "'+str(dump)+'" 0 '+
                        format(OUT,"04x")+" "+
                        format(OUT+len(SCENARIOS)*FIELDS*FRAMES-1,"04x"),"Saving")
                sock.sendall(b"quit\n")
            finally:sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
    assert dump.is_file(),(profile,"native dump absent",log.read_text()[-1600:])
    result=dump.read_bytes()
    assert len(result)==len(SCENARIOS)*FIELDS*FRAMES
    return result,prg,reu

def verify(profile,blob):
    counts={}
    stacks=set()
    for index,(width,mode,speed) in enumerate(SCENARIOS):
        x0=1 if width==8 else 256
        x1=x0+8;y0=2;y1=7
        frames=expected_frames(x0,y0,x1,y1,speed,mode)
        assert frames and len(frames)<FRAMES,(profile,width,mode,"no arrived frames")
        for t in range(FRAMES):
            row=OUT*0+index*FIELDS*FRAMES
            v=[blob[row+j*FRAMES+t] for j in range(FIELDS)]
            arrived_expected=frames[t] if t<len(frames) else ((x1,y1),True)
            pos=(v[0] | v[1]<<8, v[2])
            assert pos==arrived_expected[0],(
                profile,index,t,"position",pos,arrived_expected[0])
            assert bool(v[3]&1)==bool(arrived_expected[1]),(
                profile,index,t,"carry",v[3],arrived_expected[1])
            assert v[4]==SLOT,(profile,index,t,"X preserve",v[4])
            stacks.add(v[5])
        counts[f"SEEK{width}_{mode}_{speed:04X}"]={
            "calls":FRAMES,"frames_to_arrive":len(frames)}
    assert len(stacks)==1,(profile,"stack imbalance",stacks)
    return {"step_calls":sum(x["calls"] for x in counts.values()),
            "public_modes":counts,"sp_after_return":next(iter(stacks)),
            "native_dump_sha256":sha(blob)}

def main():
    exe=os.getenv("VICE_WRAPPER","x64sc")
    report={"status":"PASS_NATIVE_SEEK8_16_ALL_STEP_MODES",
            "native_cycle_timing_measured":False,"profiles":{},
            "native_public_step_calls":0,"native_public_init_calls":0,
            "private_optisearch_source_published":False}
    status=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
    with tempfile.TemporaryDirectory(prefix="seek_family_native_") as tmpdir:
        tmp=Path(tmpdir)
        for i,p in enumerate(P):
            data,prg,reu=native(p,12600+i,tmp,exe)
            assert sha(prg)==status["reference_prg_sha256"][p],p
            if reu:
                assert sha(reu.read_bytes())==status["reference_reu_sha256"][p]
            row=verify(p,data)
            row["prg_sha256"]=sha(prg)
            report["profiles"][p]=row
            report["native_public_step_calls"]+=row["step_calls"]
            report["native_public_init_calls"]+=len(SCENARIOS)
            print("NATIVE ALL SEEK MODES",p,"PASS",row["step_calls"],flush=True)
    assert report["native_public_step_calls"]==len(P)*len(SCENARIOS)*FRAMES
    out=ROOT/"validation/review/ISSUE39_SEEK_ALL_MODES_NATIVE_VICE_2026-10-14.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("ISSUE39 NATIVE ALL SEEK MODES PASS",report["native_public_step_calls"],flush=True)

if __name__=="__main__":
    main()
