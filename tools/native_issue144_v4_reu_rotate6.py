#!/usr/bin/env python3
"""Real VICE x64sc + actual 16-MiB REU V4 ISQRT32 rotate6 patch proof."""
from __future__ import annotations
import os,sys,tempfile,math,json,hashlib,subprocess,time,socket
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from native_issue39_u24_txa_resident import command
from validate_unsigned_division import api
from issue144_v4_reu_rotate6_peephole import PROFILE,ADDRS,ORIG,CAND
N=24;IN=0x0400;OUT=0x0700;H=0x0B00
VECTORS=[0,1,2,3,4,7,15,16,17,255,256,257,32767,65535,65536,65537,0x12345678,0x7FFFFFFF,0x80000000,0x80000001,0xBADDCAFE,0xFFFFFFFD,0xFFFFFFFE,0xFFFFFFFF]
assert len(VECTORS)==N

def test(optional,temp,port,vice):
    p=PROFILE
    prg=(ROOT/p/'resident'/f'math_{p}_game_math.prg').read_bytes()
    ld=int.from_bytes(prg[:2],'little')
    assert ld==0x1000
    mem=bytearray(65536);mem[ld:ld+len(prg)-2]=prg[2:]
    for at in ADDRS:
        assert bytes(mem[at:at+6])==ORIG
        if optional:mem[at:at+6]=CAND
    lines=['!cpu 6510','* = $0B00','    sei','    cld','    lda #$34','    sta $01','    jsr $3280','    ldx #$00','loop:']
    for k in range(4):lines += [f'    lda ${IN+k*64:04X},x',f'    sta ${0xC010+k:04X}']
    lines += ['    txa','    pha','    jsr $5E30','    php','    pla','    sta $C030','    pla','    tax','    lda $C030',f'    sta ${OUT+128:04X},x']
    for k in range(2):lines += [f'    lda ${0xC008+k:04X}',f'    sta ${OUT+k*64:04X},x']
    lines += ['    inx','    cpx #$18','    beq done','    jmp loop','done:','    jmp done']
    code,labels,_=Assembler().assemble('\n'.join(lines)+'\n');assert max(code)<0x0C00
    for k,b in code.items():mem[k]=b
    for i,n in enumerate(VECTORS):
        for k in range(4):mem[IN+i+k*64]=(n>>(k*8))&255
    stem='v4reu_rot6_'+('candidate' if optional else 'baseline')
    image=temp/(stem+'.prg');dump=temp/(stem+'.dump');log=temp/(stem+'.log')
    image.write_bytes(bytes((IN&255,IN>>8))+mem[IN:0xD000])
    cmd=[str(vice),'-console','-silent','-sounddev','dummy','-warp','-remotemonitor','-remotemonitoraddress',f'127.0.0.1:{port}','-initbreak','reset','-reu','-reusize','16384','-reuimage',str(ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu')]
    with log.open('w') as stream:
        proc=subprocess.Popen(cmd,cwd=temp,stdout=stream,stderr=stream)
        try:
            conn=None
            for _ in range(180):
                try:conn=socket.create_connection(('127.0.0.1',port),timeout=.2);break
                except (TimeoutError,ConnectionRefusedError):time.sleep(.06)
            if conn is None:raise RuntimeError(('VICE missing',log.read_text()[-1000:]))
            conn.settimeout(.8)
            try:
                command(conn,'load "'+str(image)+'" 0','Loading')
                command(conn,'break '+f"{labels['done']:04x}",'BREAK:')
                command(conn,'g '+f'{H:04x}','Stop on  exec')
                command(conn,'bsave "'+str(dump)+'" 0 '+f'{OUT:04x} '+f'{OUT+191:04x}','Saving')
                conn.sendall(b'quit\n')
            finally:conn.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
    if not dump.exists():raise RuntimeError((stem,log.read_text()[-1300:]))
    raw=dump.read_bytes();assert len(raw)==192
    for i,n in enumerate(VECTORS):
        got=raw[i]|raw[64+i]<<8
        assert got==math.isqrt(n),(stem,i,n,got)
        assert (raw[128+i]&1)==0,(stem,i,'carry')
    return raw

def main():
    vice=os.getenv('VICE_WRAPPER','/mnt/data/vice-runtime/vice-runtime/run-x64sc.sh')
    with tempfile.TemporaryDirectory(prefix='issue144_v4reu_rot6_native_') as folder:
        t=Path(folder)
        before=test(False,t,20100,vice)
        after=test(True,t,20101,vice)
    assert before==after,('native full output/status mismatch',[(i,x,y) for i,(x,y) in enumerate(zip(before,after)) if x!=y][:10])
    report={'status':'PASS_REAL_NATIVE_VICE_V4_REU_ISQRT32_ROTATE6','profile':PROFILE,'original_and_candidate_calls':N*2,'original_and_candidate_output_and_STATUS_BYTES_EQUAL':True,'real_16MiB_REU_image_loaded':True,'native_cycle_timing_not_measured':True,'original_output_dump_sha256':hashlib.sha256(before).hexdigest(),'candidate_output_dump_sha256':hashlib.sha256(after).hexdigest()}
    path=ROOT/'validation/review/ISSUE144_V4_REU_ISQRT32_ROTATE6_NATIVE_VICE.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2)+'\n')
    print('V4 REU REAL VICE 48 CALLS PASS')
if __name__=='__main__':main()
