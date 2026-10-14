#!/usr/bin/env python3
"""Issue39 real x64sc signed Q8.8->Q1.15 NORMALIZE public ABI audit.

Tests the shipped V1..V5 PRG and actual V3/V4 REU image against the independent
6502 CPU-model and certified reduction/table reference. Includes (0,0), signs,
axes, saturation and -32768. No native cycle timing claims. No production patch.
"""
from pathlib import Path
import hashlib,json,os,random,socket,subprocess,sys,tempfile,time
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import CPU,REV
REV[0xAF]=("lax","abs")
REV[0xBF]=("lax","absy")
from native_issue39_signed_multiply_family import api
from native_issue39_u24_txa_resident import command
from native_issue39_trig_angle import original_prg,original_reu
from normalize_model import normalized_reference
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
OP="MATH_VEC2_NORMALIZE_Q8_8"
POINTS=(
 (0,0),(1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,-1),(1,-1),(-1,1),
 (-32768,0),(0,-32768),(32767,0),(0,32767),(-32768,-32768),
 (32767,32767),(-32768,32767),(32767,-32768),
 (255,-255),(-255,255),(-256,256),(256,-256),
 (127,-128),(-128,127),(3,4),(4,3),(-3,4),(3,-4),
 (32767,1),(1,32767),(-32768,1),(1,-32768),(12345,-23456))
COUNT=len(POINTS)
assert COUNT<=64
STRIDE=64;INPUT=0x0400;OUTPUT=0x0600;H=0x0B00;IO=0xC000
FIELDS=tuple(IO+i for i in (0,1,2,3,4,5,6,7,8,9,10,11))+(IO+0x30,IO+0x32,IO+0x24)
assert OUTPUT+len(FIELDS)*STRIDE<=H
def sha(data):return hashlib.sha256(data).hexdigest()
def model_reference(profile,prg,reu):
    start=int.from_bytes(prg[:2],"little")
    mem=bytearray(65536);mem[start:start+len(prg)-2]=prg[2:]
    cpu=CPU(mem,reu=bytearray(reu.read_bytes()) if reu else None)
    api_map=api(profile)
    cpu.d=0;cpu.call(api_map["MATH_INIT"],2_000_000)
    backend="exact" if profile in P[2:4] else "log"
    design=json.loads((R/"validation/normalize"/("COMPONENT_TABLE_DESIGN.json" if backend=="exact" else "LOG_RATIO_TABLE_DESIGN.json")).read_text())
    ans=[]
    for x,y in POINTS:
        for off,val in ((0,x&255),(1,(x>>8)&255),(4,y&255),(5,(y>>8)&255),
                        (2,0xA5),(3,0x5A),(6,0x6C),(7,0xB9)):
            cpu.mem[IO+off]=val
        cpu.c=1;cpu.d=0
        cpu.call(api_map[OP],2_000_000)
        got=tuple(cpu.mem[IO+i] for i in range(8,12))
        ex=normalized_reference(x,y,design,backend)
        expected=tuple(z for value in ex for z in (value&255,(value>>8)&255))
        assert got==expected,(profile,x,y,got,expected)
        assert cpu.c==int(x==0 and y==0)
        assert tuple(cpu.mem[IO+i] for i in (0,1,2,3,4,5,6,7))==(
               x&255,(x>>8)&255,0xA5,0x5A,y&255,(y>>8)&255,0x6C,0xB9)
        assert cpu.sp==0xfd
        ans.append((got,cpu.c))
    return ans
def make_code(api_map):
    code=bytearray()
    def b(*args):code.extend(args)
    def op(oc,addr):b(oc,addr&255,addr>>8)
    b(0x78,0xd8,0xa9,0x35,0x85,0x01)  # SEI CLD LDA #$35 STA $01
    op(0x20,api_map["MATH_INIT"])
    b(0xA2,0)
    loop=H+len(code)
    for offset,addr in ((0,IO),(STRIDE,IO+1),(2*STRIDE,IO+4),(3*STRIDE,IO+5)):
        op(0xBD,INPUT+offset);op(0x8D,addr)
    for addr,value in ((IO+2,0xA5),(IO+3,0x5A),(IO+6,0x6C),(IO+7,0xB9),(IO+0x24,0xD5)):
        b(0xA9,value);op(0x8D,addr)
    b(0x8A,0x48,0x38)    # preserve loop X; set incoming carry
    op(0x20,api_map[OP])
    b(0x08,0x68);op(0x8D,IO+0x30)   # PHP,PLA,STA flag
    b(0xBA);op(0x8E,IO+0x32)        # TSX,STX SP after restore of flags
    b(0x68,0xAA)                   # PLA, TAX loop X
    for field_number,field in enumerate(FIELDS):
        op(0xAD,field);op(0x9D,OUTPUT+field_number*STRIDE)
    b(0xE8,0xE0,COUNT,0xF0,0x03)
    op(0x4C,loop)
    stop=H+len(code)
    op(0x4C,stop)
    assert H+len(code)<0x1000,(H,len(code))
    return bytes(code),stop
def native(profile,port,tmp,exe,prg_override=None):
    prg=original_prg(profile) if prg_override is None else prg_override
    reu=original_reu(profile)
    ld=int.from_bytes(prg[:2],"little")
    mem=bytearray(65536);mem[ld:ld+len(prg)-2]=prg[2:]
    code,stop=make_code(api(profile))
    mem[H:H+len(code)]=code
    for i,(x,y) in enumerate(POINTS):
        for page,bval in enumerate((x&255,(x>>8)&255,y&255,(y>>8)&255)):
            mem[INPUT+page*STRIDE+i]=bval
    inp=tmp/(profile+".prg");dump=tmp/(profile+".dump");log=tmp/(profile+".log")
    inp.write_bytes(bytes((INPUT&255,INPUT>>8))+mem[INPUT:0xd000])
    cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp"]
    if reu:cmd+=["-reu","-reusize",("512" if profile=="v3_reu_512k" else "16384"),"-reuimage",str(reu)]
    cmd+=["-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}","-initbreak","reset"]
    with log.open("w") as out:
        proc=subprocess.Popen(cmd,cwd=tmp,stdout=out,stderr=out)
        try:
            sock=None
            for _ in range(230):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.2);break
                except (ConnectionRefusedError,TimeoutError):time.sleep(.07)
            if sock is None:raise RuntimeError((profile,"VICE unavailable",log.read_text()[-1200:]))
            sock.settimeout(0.9)
            try:
                command(sock,'load "'+str(inp)+'" 0',"Loading")
                command(sock,"break "+format(stop,"04x"),"BREAK:")
                command(sock,"g "+format(H,"04x"),"Stop on  exec")
                command(sock,'bsave "'+str(dump)+'" 0 '+format(OUTPUT,"04x")+" "+format(OUTPUT+len(FIELDS)*STRIDE-1,"04x"),"Saving")
                sock.sendall(b"quit\n")
            finally:sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
    assert dump.exists(),(profile,"VICE dump missing",log.read_text()[-1300:])
    d=dump.read_bytes()
    assert len(d)==len(FIELDS)*STRIDE
    refs=model_reference(profile,prg,reu)
    stamps=set()
    for i,(x,y) in enumerate(POINTS):
        values=[d[j*STRIDE+i] for j in range(len(FIELDS))]
        expected_inputs=(x&255,(x>>8)&255,0xA5,0x5A,y&255,(y>>8)&255,0x6C,0xB9)
        assert tuple(values[:8])==expected_inputs,(profile,i,"input/guards",values[:8])
        assert tuple(values[8:12])==refs[i][0],(profile,i,"native output",values[8:12],refs[i])
        assert (values[12]&1)==refs[i][1],(profile,i,"carry",values[12],refs[i])
        assert values[14]==0xD5,(profile,i,"sentinel")
        stamps.add(values[13])
    assert len(stamps)==1,(profile,"stack imbalance",stamps)
    return {"cases":COUNT,"reference_carry_output_and_inputs_match":True,
            "zero_flag_and_all_quadrants_checked":True,"hardware_stack_pointer_stable":True,
            "native_result_sha256":sha(d),"shipped_prg_sha256":sha(prg),
            "reu_sha256":sha(reu.read_bytes()) if reu else None}
def candidate(profile):
    root=R/("build_hybrid/reference" if profile=="v5_hybrid_lowzp" else "build_source/reference")/profile
    man=json.loads((root/"source_build_manifest.json").read_text())
    return (root/man["output_prg"]).read_bytes()
def main():
    exe=os.getenv("VICE_WRAPPER","x64sc")
    status=json.loads((R/"RELEASE_STATUS.json").read_text())
    summary={"status":"PASS_NATIVE_VICE_NORMALIZE_BRANCH_COLLAPSE",
        "native_cycle_timing_measured":False,
        "resident_binaries_modified":False,
        "baseline_and_candidate_calls":0,
        "public_abi_unchanged":True,
        "profiles":{}}
    with tempfile.TemporaryDirectory(prefix="issue39_normalize_branch_native_") as directory:
        root=Path(directory)
        before_dir=root/"old";after_dir=root/"new"
        before_dir.mkdir();after_dir.mkdir()
        for i,p in enumerate(P):
            old=original_prg(p);new=candidate(p)
            assert sha(old)==status["reference_prg_sha256"][p]
            if p in ("v1_balanced","v2_pareto_fast","v5_hybrid_lowzp"):
                assert sha(old)!=sha(new),(p,"branch candidate stale or not integrated")
            else:
                assert sha(old)==sha(new),(p,"REU backend accidentally changed")
            before=native(p,9700+i*2,before_dir,exe,old)
            after=native(p,9701+i*2,after_dir,exe,new)
            assert before["native_result_sha256"]==after["native_result_sha256"],(p,"normalization output drift")
            assert before["cases"]==after["cases"]==COUNT
            summary["baseline_and_candidate_calls"]+=2*COUNT
            summary["profiles"][p]={"baseline_sha256":sha(old),"candidate_sha256":sha(new),
                "native_output_sha256":after["native_result_sha256"],
                "cases_each":COUNT,"all_signed_vectors_and_flags_match":True}
            print("NATIVE NORMALIZE BRANCH",p,"PASS",COUNT*2,flush=True)
    assert summary["baseline_and_candidate_calls"]==len(P)*COUNT*2
    path=R/"validation/review/ISSUE39_NORMALIZE_BRANCH_COLLAPSE_NATIVE_2026-10-14.json"
    path.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\\n")
    print("ISSUE39 NORMALIZE BRANCH NATIVE DIFF PASS",summary["baseline_and_candidate_calls"],flush=True)
if __name__=="__main__":main()
