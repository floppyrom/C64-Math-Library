#!/usr/bin/env python3
"""Real x64sc old/new V2 UMUL8 public ABI comparison for source-installed PRG.

Runs 64 deterministic 8-bit operand pairs per resident image, 128 actual
native 6510 public calls. Counts/cycles are not inferred from emulator wall
time. Do NOT mark the production candidate released from this file alone.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,os,random,socket,subprocess,tempfile,time
from native_issue39_u24_txa_resident import command
ROOT=Path(__file__).resolve().parents[1]
PARENT="ed0d0330c8130cb0adb6c7e8d3d62b9ca8bb9ab7"
PROFILE="v2_pareto_fast"
OLD_SHA="8b52fe47c4d6aff5331a5d3a4aca73e34d84696a5aa83dba14c48f62a4ee9d92"
NEW_SHA="71648ececccba3186a1b186144dbace5e345a9a0967d397ec1db0655cef31c04"
ENTRY=0x3000
H=0x0B00;IN=0x0400;OUT=0x0600;STRIDE=64;COUNT=64;IO=0xC000
FIELDS=[0xC008,0xC009,0xC00A,0xC00B,0xC000,0xC001,0xC004,0xC005,0xC030,0xC032,0xC024]
assert OUT+STRIDE*len(FIELDS)<H
def sha(b):return hashlib.sha256(b).hexdigest()
def pairs():
    g=random.Random(0x39080039)
    edge=(0,1,2,3,7,15,16,31,63,127,128,254,255)
    out=[(a,b) for a in edge for b in edge]
    sample=[(0,0),(1,1),(255,255),(255,1),(1,255),(0,255),(255,0),(128,128)]
    sample.extend((a,b) for a,b in out if ((a+b)&0x19)==0)
    sample=list(dict.fromkeys(sample))
    while len(sample)<COUNT:
        p=(g.randrange(256),g.randrange(256))
        if p not in sample:sample.append(p)
    return sample[:COUNT]
def harness():
    b=bytearray()
    def e(*v):b.extend(v)
    def ab(op,addr):e(op,addr&255,addr>>8)
    e(0x78,0xD8,0xA9,0x34,0x85,0x01) # SEI CLD RAM-under-ROM
    ab(0x20,0x3280)  # existing source-resident MATH_INIT
    e(0xA2,0x00)
    top=H+len(b)
    ab(0xBD,IN+0*STRIDE);ab(0x8D,IO)
    ab(0xBD,IN+1*STRIDE);ab(0x8D,IO+4)
    e(0xA9,0x55);ab(0x8D,IO+1)
    e(0xA9,0xAA);ab(0x8D,IO+5)
    e(0xA9,0x93);ab(0x8D,IO+8);ab(0x8D,IO+9)
    e(0xA9,0xB5);ab(0x8D,IO+10);ab(0x8D,IO+11)
    e(0xA9,0xC7);ab(0x8D,0xC024)
    e(0x8A,0x48,0x38) # TXA/PHA save index; force carry set
    ab(0x20,ENTRY)
    e(0x08,0x68);ab(0x8D,0xC030)  # PHP PLA store carry
    e(0xBA);ab(0x8E,0xC032)
    e(0x68,0xAA)
    for j,addr in enumerate(FIELDS):
        ab(0xAD,addr);ab(0x9D,OUT+j*STRIDE)
    e(0xE8,0xE0,COUNT,0xF0,0x03);ab(0x4C,top)
    stop=H+len(b);ab(0x4C,stop)
    assert len(b)<0x300
    return bytes(b),stop
def native(prg,label,port,folder,exe):
    assert int.from_bytes(prg[:2],"little")==0x1000
    memory=bytearray(65536)
    memory[0x1000:0x1000+len(prg)-2]=prg[2:]
    code,stop=harness();memory[H:H+len(code)]=code
    sample=pairs()
    for i,(x,y) in enumerate(sample):
        memory[IN+i]=x;memory[IN+STRIDE+i]=y
    inp=folder/f"{label}.prg";out=folder/f"{label}.dump";log=folder/f"{label}.log"
    inp.write_bytes(bytes([IN&255,IN>>8])+memory[IN:0xD000])
    cmd=[str(exe),"-console","-silent","-sounddev","dummy","-warp",
         "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}","-initbreak","reset"]
    with log.open('w') as stdout:
        process=subprocess.Popen(cmd,cwd=folder,stdout=stdout,stderr=stdout)
        try:
            sock=None
            for _ in range(180):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=0.15)
                    break
                except (ConnectionRefusedError,TimeoutError):time.sleep(0.07)
            if sock is None:raise RuntimeError((label,'VICE remote connect failed',log.read_text()[-800:]))
            sock.settimeout(0.3)
            try:
                command(sock,'load "'+str(inp)+'" 0',"Loading")
                command(sock,"break "+format(stop,"04x"),"BREAK:")
                command(sock,"g "+format(H,"04x"),"Stop on  exec")
                command(sock,'bsave "'+str(out)+'" 0 '+format(OUT,"04x")+" "+format(OUT+len(FIELDS)*STRIDE-1,"04x"),"Saving")
                sock.sendall(b"quit\n")
            finally:sock.close()
        finally:
            process.terminate()
            try:process.wait(timeout=3)
            except subprocess.TimeoutExpired:process.kill()
    if not out.exists():raise RuntimeError((label,"dump missing",log.read_text()[-1500:]))
    raw=out.read_bytes()
    assert len(raw)==len(FIELDS)*STRIDE
    records=[]
    for i,(x,y) in enumerate(sample):
        row=[raw[j*STRIDE+i] for j in range(len(FIELDS))]
        value=row[0]+(row[1]<<8)
        assert (value,row[2],row[3],row[4],row[5],row[6],row[7],
                row[8]&1,row[10])==(x*y,0xB5,0xB5,x,0x55,y,0xAA,0,0xC7),(
                label,x,y,row)
        records.append(row)
    return {'dump_sha256':sha(raw),'cases':COUNT,'records':records}
def main():
    status=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
    assert status['issue39_v2_umul8_directout_2026_10_13']['status'] in (
      'PASS_STAGED_NATIVE_VICE_PENDING','PASS_NATIVE_VICE_SOURCE_INSTALLED_PR_CI_PENDING')
    rel=f'{PROFILE}/resident/math_{PROFILE}_game_math.prg'
    old=subprocess.check_output(['git','show',PARENT+':'+rel],cwd=ROOT)
    new=(ROOT/rel).read_bytes()
    assert sha(old)==OLD_SHA
    assert sha(new)==NEW_SHA==status['reference_prg_sha256'][PROFILE]
    exe=os.getenv('VICE_WRAPPER','x64sc')
    with tempfile.TemporaryDirectory(prefix='issue39_native_umul8_') as td:
        folder=Path(td)
        base=native(old,'v2_old_umul8',7712,folder,exe)
        trial=native(new,'v2_new_umul8',7713,folder,exe)
        if base['records']!=trial['records']:
            differences=[(i,pairs()[i],[(hex(FIELDS[j]),a[j],b[j]) for j in range(len(FIELDS)) if a[j]!=b[j]])
                for i,(a,b) in enumerate(zip(base['records'],trial['records'])) if a!=b]
            print('NATIVE DIFFERENT FIELDS',differences[:12],flush=True)
            raise AssertionError(('native public old/new mismatch',len(differences),differences[:3]))
    result={'status':'PASS_NATIVE_VICE_V2_UMUL8_PUBLIC_DIRECT_OUTPUT',
       'old_sha256':OLD_SHA,'new_sha256':NEW_SHA,'public_entry':hex(ENTRY),
       'old_native_calls':COUNT,'new_native_calls':COUNT,
       'native_calls':2*COUNT,'paired_operands':COUNT,
       'old_dump_sha256':base['dump_sha256'],
       'new_dump_sha256':trial['dump_sha256'],
       'all_public_results_identical':True,'native_cycles_measured':False,
       'source_profile':PROFILE,'parent_commit':PARENT}
    proof=ROOT/'validation/review/ISSUE39_V2_UMUL8_DIRECTOUT_NATIVE.json'
    proof.parent.mkdir(parents=True,exist_ok=True)
    proof.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('ISSUE39 V2 UMUL8 INSTALLED SOURCE NATIVE x64sc PASS',COUNT*2,flush=True)
if __name__=='__main__':main()
