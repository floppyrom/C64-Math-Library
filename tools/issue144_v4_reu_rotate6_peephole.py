#!/usr/bin/env python3
"""Issue144 V4 REU ISQRT32 highword address nibble: 6x ASL => LSR,ROR,ROR,BCC skip.

Exact in-place six-byte patch, same N/Z/C, no code/ZP/data RAM addition.
CPU-model + actual 16 MiB REU image; no physical REU/VIC bus timing claim.
"""
from __future__ import annotations
import sys,math,hashlib,json,statistics,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
from validate_unsigned_division import load,wr,rd
from issue144_isqrt32_direct_seed_canonical import corpus
from mini6502 import Assembler
import hashlib
PROFILE='v4_reu_16m';ADDRS=(0xC90B,0xC924);ORIG=b'\x0a'*6;CAND=b'\x4a\x6a\x6a\x90\x01\xea'

def pure_byte_check():
    from mini6502 import CPU
    for a in range(4):
        for c0 in range(2):
            out=[]
            for code in (ORIG,CAND):
                mem=bytearray(65536);mem[0x800:0x806]=code
                mem[0x806]=0x60
                cpu=CPU(mem);cpu.a=a;cpu.c=c0
                cpu.call(0x800,100)
                out.append((cpu.a,cpu.c,cpu.n,cpu.z,cpu.v,cpu.x,cpu.y))
            assert out[0]==out[1],(a,c0,out)
    print('SOURCE BYTEFLAGS PASS 8 initial cases')

def calc():
    pure_byte_check()
    a,api=load(PROFILE);b,_=load(PROFILE)
    asm=(ROOT/'optional/issue144_v4_reu_isqrt_rotate6/v4_reu_16m.asm').read_text()
    program,labels,_=Assembler().assemble(asm)
    assert len(program)==88 and all(b.mem[at]==0 for at in program)
    for at,byte in program.items():b.mem[at]=byte
    source_before={at:bytes(b.mem[at:at+6]) for at in ADDRS}
    begin_cycles=b.call(labels['ISQRT32_V4_REU_ROT6_BEGIN'])
    assert begin_cycles==66
    patch_info=[]
    for addr in ADDRS:
        assert bytes(a.mem[addr:addr+6])==ORIG,(hex(addr),bytes(a.mem[addr:addr+6]).hex())
        assert source_before[addr]==ORIG
        assert bytes(b.mem[addr:addr+6])==CAND
        patch_info.append({'address':hex(addr),'original':ORIG.hex(),'candidate':CAND.hex()})
    vec=corpus();old=[];new=[]
    for idx,n in enumerate(vec):
        for cpu in (a,b):wr(cpu.mem,0xC010,n,4)
        before=a.call(api['MATH_ISQRT32'],1000000)
        after=b.call(api['MATH_ISQRT32'],1000000)
        root=math.isqrt(n)
        assert rd(a.mem,0xC008,2)==rd(b.mem,0xC008,2)==root,(idx,n,'root')
        assert rd(a.mem,0xC010,4)==rd(b.mem,0xC010,4)==n
        assert a.c==b.c==0 and a.sp==b.sp
        assert a.x==b.x and a.y==b.y,(idx,'xy')
        assert (a.n,a.z,a.v,a.d)==(b.n,b.z,b.v,b.d),(idx,'flags')
        assert before-after==6,(idx,n,before,after)
        old.append(before);new.append(after)
        if idx%199==0:
            n16=(n+0x1135)&65535
            for cpu in (a,b):
                wr(cpu.mem,0xC010,n16,4)
                cpu.call(api['MATH_ISQRT16'],1000000)
                assert rd(cpu.mem,0xC008,2)==math.isqrt(n16)
    assert bytes(b.mem[0xC90B:0xC911])==CAND and bytes(b.mem[0xC924:0xC92A])==CAND
    end_cycles=b.call(labels['ISQRT32_V4_REU_ROT6_END'])
    assert end_cycles==56 and all(bytes(b.mem[addr:addr+6])==ORIG for addr in ADDRS)
    for n in vec[:64]:
        wr(b.mem,0xC010,n,4);b.call(api['MATH_ISQRT32'],1000000)
        assert rd(b.mem,0xC008,2)==math.isqrt(n)
    def stats(arr):
        sorted_arr=sorted(arr)
        return {'mean':statistics.mean(arr),'median':statistics.median(arr),'p95':sorted_arr[int((len(arr)-1)*.95)],'min':min(arr),'max':max(arr),'vector_sha256':hashlib.sha256(b''.join(v.to_bytes(4,'little') for v in arr)).hexdigest()}
    report={'status':'PASS_CPU_MODEL_V4_REU_ISQRT32_NO_EXTRA_RESOURCES','profile':PROFILE,'canonical_corpus':len(vec),'before':stats(old),'after':stats(new),'gain_cycles_on_every_input':6,'original_resident_data_changed':False,'real_16MiB_REU_payload_loaded':True,'old_extra_ZP':0,'new_extra_ZP':0,'net_executable_bytes_growth':0,'source_installer_bytes':len(program),'enable_cycles':begin_cycles,'disable_cycles':end_cycles,'patch':patch_info,'source_sha256':hashlib.sha256(asm.encode()).hexdigest(),'unpromoted_native_pending':True,'physical_REU_bus_cycles_not_measured':True}
    print('V4 REU ALL INPUTS PASS',len(vec),'cycles',report['before']['mean'],'->',report['after']['mean'])
    out=ROOT/'validation/review/ISSUE144_V4_REU_ISQRT32_ROTATE6_MODEL.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':calc()
