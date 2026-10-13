#!/usr/bin/env python3
"""Research-only manual ISQRT16 seed/compare architecture and ISQRT32 composition.

Exact public resident ABI. Stable public MATH_ISQRT16 is temporarily redirected
in the flat 6502 test model to RAM-under-ROM $E100; seed table at $E200.
$9800/$9900 are *validated* shipped square planes, not silently fabricated.
This overlay is NOT a loadable resident, not native VICE qualified and must
never be shipped unchanged. Confidential OptiSearch source is not used.
"""
from __future__ import annotations
import argparse, hashlib, json, math, random, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,load,wr,rd
from validate_isqrt32_fast import cases as root32cases

IS16=0x5e2d
IS32=0x5e30
CODE=0xe100
SEED=0xe200
N=0xc010
Z=0xc008
SEEDS=bytes(math.isqrt((hi<<8)+255) for hi in range(256))
CODE_SRC="""* = $E100
ISQRT16_SEED_REFINE:
    ldx $C011
    ldy $E200,x
TRY_SQUARE:
    lda $C011
    cmp $9900,y
    bcc PREVIOUS
    bne STORE
    lda $C010
    cmp $9800,y
    bcc PREVIOUS
STORE:
    sty $C008
    lda #0
    sta $C009
    clc
    rts
PREVIOUS:
    dey
    bpl TRY_SQUARE
    brk
"""
BYTES,LABELS,_=Assembler().assemble(CODE_SRC)
assert min(BYTES)==CODE and max(BYTES)<SEED and LABELS['ISQRT16_SEED_REFINE']==CODE

def digest(b):return hashlib.sha256(b).hexdigest()

def samples16(count:int):
    rng=random.Random(0xC6395216)
    fixed=[0,1,2,3,4,7,8,9,15,16,255,256,257,65534,65535]
    for r in (0,1,2,3,7,15,16,31,63,127,128,254,255):
        for d in (-2,-1,0,1,2):
            n=r*r+d
            if 0<=n<65536:fixed.append(n)
    fixed += [rng.randrange(65536) for _ in range(count)]
    return list(dict.fromkeys(fixed))

def samples32(count:int):
    rng=random.Random(0xC6395232)
    fixed=root32cases()[:140]
    for r in (0,1,2,3,15,127,255,256,257,1023,4095,16383,32767,65535):
        for d in (-1,0,1):
            n=r*r+d
            if 0<=n<=0xffffffff:fixed.append(n)
    fixed += [rng.getrandbits(32) for _ in range(count)]
    return list(dict.fromkeys(fixed))

def load_both(profile):
    orig,entries=load(profile)
    test,ep=load(profile)
    assert entries==ep
    assert entries['MATH_ISQRT16']==IS16 and entries['MATH_ISQRT32']==IS32
    prg=ROOT/profile/'resident'/f'math_{profile}_game_math.prg'
    sha=digest(prg.read_bytes())
    status=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
    assert sha==status['reference_prg_sha256'][profile],(profile,'PRG SHA mismatch')
    expected_lo=bytes((i*i)&255 for i in range(256))
    expected_hi=bytes((i*i)>>8 for i in range(256))
    actual=(bytes(orig.mem[0x9800:0x9900]),bytes(orig.mem[0x9900:0x9a00]))
    assert actual==(expected_lo,expected_hi),(
       profile,'square plane is not a source-owned 256x2 table',
       digest(actual[0]),digest(actual[1]))
    assert bytes(test.mem[IS16:IS16+1])==bytes([0x4c]),'public ISQRT16 is not JMP'
    assert all(test.mem[a]==0 for a in list(BYTES)+list(range(SEED,SEED+256))),(
        profile,'test overlay clobbers pre-existing RAM; reject')
    test.mem[IS16:IS16+3]=bytes((0x4c,CODE&255,CODE>>8))
    for a,v in BYTES.items():test.mem[a]=v
    test.mem[SEED:SEED+256]=SEEDS
    return orig,test,sha

def sample(cpu,entry,n,width):
    nn=width//8
    wr(cpu.mem,N,n,nn)
    before=bytes(cpu.mem[N:N+nn])
    wr(cpu.mem,Z,0xA6B5D4C3,4)
    cpu.d=0
    sp=cpu.sp
    cy=cpu.call(entry,2_000_000)
    got=rd(cpu.mem,Z,2)
    assert got==math.isqrt(n),(width,hex(n),got,math.isqrt(n))
    assert bytes(cpu.mem[N:N+nn])==before,('N overwritten',hex(n))
    assert cpu.c==0 and cpu.sp==sp,('flags/stack',hex(n),cpu.c,cpu.sp,sp)
    assert bytes(cpu.mem[Z+2:Z+4])==bytes((0xB5,0xA6)),('output sentinel',hex(n))
    return cy,(got,cpu.c,sp,bytes(cpu.mem[N:N+nn]))

def compare(baseline,candidate,entry,cases,width):
    old=[];new=[];hash_inputs=hashlib.sha256()
    for n in cases:
        a,av=sample(baseline,entry,n,width)
        b,bv=sample(candidate,entry,n,width)
        assert av==bv,('public discrepancy',entry,hex(n),av,bv)
        old.append(a);new.append(b);hash_inputs.update(n.to_bytes(width//8,'little'))
    differences=[b-a for a,b in zip(old,new)]
    return {
      'cases':len(cases),'input_sha256':hash_inputs.hexdigest(),
      'baseline_mean_cycles':sum(old)/len(old),
      'candidate_mean_cycles':sum(new)/len(new),
      'mean_delta_cycles':sum(differences)/len(differences),
      'faster':sum(x<0 for x in differences),
      'equal':sum(x==0 for x in differences),
      'slower':sum(x>0 for x in differences),
      'max_regression':max(differences),
      'max_speedup':-min(differences),
      'old_cycles_sha256':digest(json.dumps(old).encode()),
      'new_cycles_sha256':digest(json.dumps(new).encode())}

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--random16',type=int,default=2304)
    p.add_argument('--random32',type=int,default=720)
    p.add_argument('--out',type=Path)
    args=p.parse_args()
    v16=samples16(args.random16);v32=samples32(args.random32)
    report={
      'status':'PASS_RESEARCH_ONLY_NOT_PROMOTED',
      'source':str(Path(__file__).relative_to(ROOT)),
      'experiment':'manually derived high-byte upper-root seed with downward exact square table comparison',
      'overlay_under_rom':hex(CODE),'seed_table_under_rom':hex(SEED),
      'seed_table_bytes':len(SEEDS),'code_bytes':len(BYTES),
      'existing_square_plane_bytes_reused':512,
      'zero_page_growth':0,'native_vice_calls':0,
      'hardware_bus_timing_measured':False,
      'profiles':{},'old_new_6502_calls':0,
    }
    for profile in PROFILES:
        baseline,candidate,h=load_both(profile)
        u16=compare(baseline,candidate,IS16,v16,16)
        u32=compare(baseline,candidate,IS32,v32,32)
        report['profiles'][profile]={
          'resident_sha256':h,'isqrt16':u16,'isqrt32_composition':u32}
        report['old_new_6502_calls']+=2*(len(v16)+len(v32))
        print(profile,'ISQRT16',u16['cases'],'old',round(u16['baseline_mean_cycles'],3),
              'new',round(u16['candidate_mean_cycles'],3),
              'delta',round(u16['mean_delta_cycles'],3),
              '32bit composition delta',round(u32['mean_delta_cycles'],3),flush=True)
    if args.out:
       args.out.parent.mkdir(parents=True,exist_ok=True)
       args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('ISSUE39 ISQRT16 MANUAL PUBLIC ENTRY SCREEN PASS',
          report['old_new_6502_calls'],'calls',flush=True)

if __name__=='__main__': main()
