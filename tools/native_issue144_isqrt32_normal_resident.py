#!/usr/bin/env python3
"""Issue144 normal-resident V2/V3 ISQRT32 direct highword: native x64sc/REU proof."""
from __future__ import annotations
import hashlib, json, math, os, socket, subprocess, sys, tempfile, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from native_issue39_u24_txa_resident import command
from issue144_isqrt32_normal_resident_screen import assembled, PROFILES
from validate_unsigned_division import REU

IN,OUT,H=0x0400,0x0700,0x0B00
N=24
E=(0,1,2,3,4,7,15,16,17,255,256,257,32767,65535,65536,65537,
   0x12345678,0x7fffffff,0x80000000,0x80000001,0xbaddcafe,
   0xfffffffd,0xfffffffe,0xffffffff)
assert len(E)==N

def native(profile,layout,cpu,api,io,port,tmp,vice):
    mem=bytearray(cpu.mem)
    asm=['!cpu 6510','* = $0B00','sei','cld','ldx #$FF','txs',
         'lda #$35','sta $01',f'jsr ${api["MATH_INIT"]:04X}','ldx #$00','loop:']
    for k in range(4):
        asm+=['lda $'+format(IN+k*64,'04X')+',x','sta ]
    asm+=['txa','pha',f'jsr ${api["MATH_ISQRT32"]:04X}','php','pla','sta $C030','pla','tax',
          'lda $C030','sta $0780,x']
    for k in range(2):
        asm+=['lda $'+format(io+0x08+k,'04X'),
              'sta $'+format(OUT+k*64,'04X')+',x']
    asm+=['inx','cpx #$18','beq done','jmp loop','done: jmp done']
    program,labels,_=Assembler().assemble('\n'.join(asm)+'\n')
    assert min(program)==H and max(program)<0x0C00
    for k,b in program.items():mem[k]=b
    for i,n in enumerate(E):
        for k in range(4):mem[IN+i+k*64]=(n>>(8*k))&255
    tag=profile+'_'+layout+'_'+str(port)
    image=tmp/(tag+'.prg');dump=tmp/(tag+'.dump');log=tmp/(tag+'.log')
    image.write_bytes(bytes((0,4))+mem[0x0400:0xD000])
    cmd=[vice,'-default','-console','-silent','-sounddev','dummy','-warp',
         '-remotemonitor','-remotemonitoraddress','127.0.0.1:'+str(port),
         '-initbreak','reset']
    reu=REU.get(profile)
    if reu is not None:
        assert reu.is_file()
        cmd+=['-reu','-reusize','512','-reuimage',str(reu)]
    with log.open('w') as output:
        proc=subprocess.Popen(cmd,cwd=tmp,stdout=output,stderr=output)
        try:
            conn=None
            for _ in range(180):
                try:
                    conn=socket.create_connection(('127.0.0.1',port),timeout=.25)
                    break
                except OSError:time.sleep(.06)
            if conn is None:raise RuntimeError(('VICE monitor timeout',profile,log.read_text()[-1600:]))
            conn.settimeout(1)
            try:
                command(conn,'load "'+str(image)+'" 0','Loading')
                command(conn,'break '+format(labels['done'],'04x'),'BREAK:')
                command(conn,'g 0b00','Stop on  exec')
                command(conn,'bsave "'+str(dump)+'" 0 0700 07bf','Saving')
                conn.sendall(b'quit\n')
            finally:conn.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=4)
            except subprocess.TimeoutExpired:proc.kill()
    if not dump.exists():raise RuntimeError((profile,layout,tag,log.read_text()[-1500:]))
    snapshot=dump.read_bytes()
    assert len(snapshot)==192
    for i,n in enumerate(E):
        root=snapshot[i]|(snapshot[64+i]<<8)
        assert root==math.isqrt(n),(profile,layout,i,hex(n),root)
        assert snapshot[128+i]&1==0,(profile,layout,i,'carry')
    return snapshot

def main():
    vice=os.getenv('VICE_WRAPPER')
    assert vice,'native qualification requires VICE_WRAPPER=x64sc'
    with tempfile.TemporaryDirectory(prefix='issue144_isqrt_resident_native_') as d:
        tmp=Path(d)
        report={'status':'PASS_NATIVE_VICE_ISQRT32_RESIDENT_V2V3','profiles':{},'total_native_public_calls':0,
                'physical_cycle_timing_measured':False,'caller_RAM_added':False,
                'normal_ZP_added':False,'reference_resident_PRGs_modified':False}
        for pi,p in enumerate(PROFILES):
            report['profiles'][p]={}
            for j,layout in enumerate(('reference','alternate')):
                std,opt,api,io,source_hash,slot=assembled(p,layout)
                start=24020+pi*4+j*2
                before=native(p,layout,std,api,io,start,tmp,vice)
                after=native(p,layout,opt,api,io,start+1,tmp,vice)
                assert before==after,(p,layout,'native output/status differs',
                                      [(i,a,b) for i,(a,b) in enumerate(zip(before,after)) if a!=b][:8])
                report['profiles'][p][layout]={'status':'PASS_48_NATIVE_CALLS',
                    'prepromotion_sha256':hashlib.sha256(before).hexdigest(),
                    'optimized_sha256':hashlib.sha256(after).hexdigest(),
                    'source_sha256':source_hash,'slot':slot,
                    'uses_real_REU':p=='v3_reu_512k'}
                report['total_native_public_calls']+=2*N
                print('ISQRT32 RESIDENT VICE',p,layout,'PASS',2*N,'calls',flush=True)
        assert report['total_native_public_calls']==len(PROFILES)*2*2*N
        print(json.dumps(report,indent=2,sort_keys=True))
if __name__=='__main__':main()
+format(io+0x10+k,'04X')]
    asm+=['txa','pha','jsr $5E30','php','pla','sta $C030','pla','tax',
          'lda $C030','sta $0780,x']
    for k in range(2):
        asm+=['lda $'+format(0xC008+k,'04X'),
              'sta $'+format(OUT+k*64,'04X')+',x']
    asm+=['inx','cpx #$18','beq done','jmp loop','done: jmp done']
    program,labels,_=Assembler().assemble('\n'.join(asm)+'\n')
    assert min(program)==H and max(program)<0x0C00
    for k,b in program.items():mem[k]=b
    for i,n in enumerate(E):
        for k in range(4):mem[IN+i+k*64]=(n>>(8*k))&255
    tag=profile+'_'+layout+'_'+str(port)
    image=tmp/(tag+'.prg');dump=tmp/(tag+'.dump');log=tmp/(tag+'.log')
    image.write_bytes(bytes((0,4))+mem[0x0400:0xD000])
    cmd=[vice,'-default','-console','-silent','-sounddev','dummy','-warp',
         '-remotemonitor','-remotemonitoraddress','127.0.0.1:'+str(port),
         '-initbreak','reset']
    reu=REU.get(profile)
    if reu is not None:
        assert reu.is_file()
        cmd+=['-reu','-reusize','512','-reuimage',str(reu)]
    with log.open('w') as output:
        proc=subprocess.Popen(cmd,cwd=tmp,stdout=output,stderr=output)
        try:
            conn=None
            for _ in range(180):
                try:
                    conn=socket.create_connection(('127.0.0.1',port),timeout=.25)
                    break
                except OSError:time.sleep(.06)
            if conn is None:raise RuntimeError(('VICE monitor timeout',profile,log.read_text()[-1600:]))
            conn.settimeout(1)
            try:
                command(conn,'load "'+str(image)+'" 0','Loading')
                command(conn,'break '+format(labels['done'],'04x'),'BREAK:')
                command(conn,'g 0b00','Stop on  exec')
                command(conn,'bsave "'+str(dump)+'" 0 0700 07bf','Saving')
                conn.sendall(b'quit\n')
            finally:conn.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=4)
            except subprocess.TimeoutExpired:proc.kill()
    if not dump.exists():raise RuntimeError((profile,layout,tag,log.read_text()[-1500:]))
    snapshot=dump.read_bytes()
    assert len(snapshot)==192
    for i,n in enumerate(E):
        root=snapshot[i]|(snapshot[64+i]<<8)
        assert root==math.isqrt(n),(profile,layout,i,hex(n),root)
        assert snapshot[128+i]&1==0,(profile,layout,i,'carry')
    return snapshot

def main():
    vice=os.getenv('VICE_WRAPPER')
    assert vice,'native qualification requires VICE_WRAPPER=x64sc'
    with tempfile.TemporaryDirectory(prefix='issue144_isqrt_resident_native_') as d:
        tmp=Path(d)
        report={'status':'PASS_NATIVE_VICE_ISQRT32_RESIDENT_V2V3','profiles':{},'total_native_public_calls':0,
                'physical_cycle_timing_measured':False,'caller_RAM_added':False,
                'normal_ZP_added':False,'reference_resident_PRGs_modified':False}
        for pi,p in enumerate(PROFILES):
            report['profiles'][p]={}
            for j,layout in enumerate(('reference','alternate')):
                std,opt,api,io,source_hash,slot=assembled(p,layout)
                start=24020+pi*4+j*2
                before=native(p,layout,std,start,tmp,vice)
                after=native(p,layout,opt,start+1,tmp,vice)
                assert before==after,(p,layout,'native output/status differs',
                                      [(i,a,b) for i,(a,b) in enumerate(zip(before,after)) if a!=b][:8])
                report['profiles'][p][layout]={'status':'PASS_48_NATIVE_CALLS',
                    'prepromotion_sha256':hashlib.sha256(before).hexdigest(),
                    'optimized_sha256':hashlib.sha256(after).hexdigest(),
                    'source_sha256':source_hash,'slot':slot,
                    'uses_real_REU':p=='v3_reu_512k'}
                report['total_native_public_calls']+=2*N
                print('ISQRT32 RESIDENT VICE',p,layout,'PASS',2*N,'calls',flush=True)
        assert report['total_native_public_calls']==len(PROFILES)*2*2*N
        print(json.dumps(report,indent=2,sort_keys=True))
if __name__=='__main__':main()
