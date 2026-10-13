#!/usr/bin/env python3
"""Issue39 unsigned-multiply: V2 UMUL8 public-only direct-result research.

Manual independent architecture: let a private 8x8 quarter-square core
store its low result to MATH_Z+0 directly; public wrapper stores high result
to MATH_Z+1. Unchanged public entry address / call convention / ZP budget.

The modified kernel is installed at $E100 in the test-only flat CPU model.
That location is NOT owned by any public resident and therefore this is
NOT a production build or a native VICE / real hardware certification.
The original shared native kernel at $5300 remains byte-for-byte untouched.
"""
from __future__ import annotations
import argparse,hashlib,json,math,random,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import load,rd,wr

PROFILE='v2_pareto_fast'
API=0x3000
ORIGINAL_KERNEL=0x5300
CANDIDATE_KERNEL=0xe100
MATH_X=0xc000
MATH_Y=0xc004
MATH_Z=0xc008
SCRATCH_LOW=0x3d
SEED=0x3908
SOURCE="""* = $E100
UMUL8_DIRECT:
    sec
    stx $39
    stx $3B
    tya
    sbc $39
    tax
    lda ($39),y
    bcc NEG
    sbc $6800,x
    sta $C008
    lda ($3B),y
    sbc $6A00,x
    rts
NEG:
    sbc $6C00,x
    sta $C008
    lda ($3B),y
    sbc $6D00,x
    rts
"""
PRIVATE,LABELS,_=Assembler().assemble(SOURCE)
assert min(PRIVATE)==CANDIDATE_KERNEL and max(PRIVATE)<CANDIDATE_KERNEL+64
assert LABELS['UMUL8_DIRECT']==CANDIDATE_KERNEL

WRAPPER=bytes((0xAE,0x00,0xC0,0xAC,0x04,0xC0,
               0x20,CANDIDATE_KERNEL&255,CANDIDATE_KERNEL>>8,
               0x8D,0x09,0xC0,0x18,0x60))
ORIGINAL_WRAPPER=bytes((0xAE,0x00,0xC0,0xAC,0x04,0xC0,
                        0x20,0x00,0x53,0x8D,0x09,0xC0,
                        0xA5,SCRATCH_LOW,0x8D,0x08,0xC0,0x18,0x60))
assert len(ORIGINAL_WRAPPER)==19 and len(WRAPPER)==14

def sha(b):return hashlib.sha256(b).hexdigest()

def load_models():
    old,entries=load(PROFILE)
    new,new_entries=load(PROFILE)
    assert entries==new_entries and entries['MATH_UMUL8']==API
    image=(ROOT/PROFILE/'resident'/f'math_{PROFILE}_game_math.prg').read_bytes()
    state=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
    assert sha(image)==state['reference_prg_sha256'][PROFILE]
    assert bytes(old.mem[API:API+19])==ORIGINAL_WRAPPER,('changed public wrapper baseline')
    assert bytes(new.mem[CANDIDATE_KERNEL:CANDIDATE_KERNEL+64])==bytes(64),(
        'experimental address already initialized; refuse overlay')
    new.mem[API:API+19]=WRAPPER+bytes([0xea]*(19-len(WRAPPER)))
    for k,v in PRIVATE.items():new.mem[k]=v
    assert bytes(old.mem[ORIGINAL_KERNEL:ORIGINAL_KERNEL+0x23])==(
           bytes(new.mem[ORIGINAL_KERNEL:ORIGINAL_KERNEL+0x23]))
    return old,new,entries,sha(image)

def one(cpu,x,y,entry):
    wr(cpu.mem,MATH_X,x+0x5500,2)
    wr(cpu.mem,MATH_Y,y+0xAA00,2)
    cpu.mem[MATH_Z:MATH_Z+4]=bytes((0xAB,0xCD,0x93,0x71))
    cpu.d=0
    cpu.c=1 if ((x^y)&1) else 0
    sp=cpu.sp
    cycles=cpu.call(entry,1200)
    z=rd(cpu.mem,MATH_Z,2)
    assert z==x*y,(hex(x),hex(y),hex(z),hex(x*y))
    assert cpu.c==0 and cpu.sp==sp,('carry/stack',x,y,cpu.c,cpu.sp,sp)
    assert rd(cpu.mem,MATH_X,2)==(x+0x5500)
    assert rd(cpu.mem,MATH_Y,2)==(y+0xAA00)
    assert bytes(cpu.mem[MATH_Z+2:MATH_Z+4])==bytes((0x93,0x71))
    return cycles,(z,cpu.c,bytes(cpu.mem[MATH_X:MATH_X+2]),
                   bytes(cpu.mem[MATH_Y:MATH_Y+2]),
                   bytes(cpu.mem[MATH_Z+2:MATH_Z+4]),cpu.sp)

def run(limit):
    original,candidate,entries,h=load_models()
    # Machine-code exact same-input comparisons. The wrapper uses both
    # entry carry states; incoming C is not part of the multiply's result.
    hist={}
    diffs=[];cycles_before=cycles_after=0
    changed_scratch_count=0
    examples=[]
    for n in range(limit):
        x=n&255;y=n>>8
        old_v,oldout=one(original,x,y,API)
        new_v,newout=one(candidate,x,y,API)
        assert newout==oldout,(x,y,'ABI',newout,oldout)
        diff=new_v-old_v
        hist[diff]=hist.get(diff,0)+1
        diffs.append(diff)
        cycles_before+=old_v;cycles_after+=new_v
        if original.mem[SCRATCH_LOW]!=candidate.mem[SCRATCH_LOW]:
            changed_scratch_count+=1
        if len(examples)<8 and (x==0 or y==0 or x==255 or y==255):
            examples.append({'x':x,'y':y,'before':old_v,'candidate':new_v,'delta':diff})
    assert not any(v>0 for v in diffs),'candidate regresses'
    assert all(v==-6 for v in diffs),('unexpected timing geometry',hist)
    # Interference exercise: after public UMUL8, run the full ordinary
    # public UMUL16 and verify it overwrites its own result correctly.
    rng=random.Random(SEED)
    mixed=0
    for _ in range(4096):
        x=rng.randrange(256);y=rng.randrange(256)
        one(original,x,y,API);one(candidate,x,y,API)
        a=rng.randrange(65536);b=rng.randrange(65536)
        for cpu in (original,candidate):
            wr(cpu.mem,MATH_X,a,2);wr(cpu.mem,MATH_Y,b,2)
            cpu.d=0;sp=cpu.sp
            cpu.call(entries['MATH_UMUL16'],3000)
            assert rd(cpu.mem,MATH_Z,4)==a*b
            assert cpu.c==0 and cpu.sp==sp
        mixed+=1
    return {
      'status':'PASS_RESEARCH_ONLY_NOT_INSTALLED',
      'baseline_profile':PROFILE,'base_resident_sha256':h,
      'entry':hex(API),'private_candidate_code_location':hex(CANDIDATE_KERNEL),
      'code_bytes':len(PRIVATE),
      'new_normal_zero_page_bytes':0,
      'extra_candidate_executable_bytes':len(PRIVATE),
      'source_owned_production_placement':False,
      'native_vice_calls':0,'public_same_input_calls':limit*2,
      'exhaustive':limit==65536,
      'mixed_post_UMUL8_UMUL16_calls':mixed*2,
      'mean_before':cycles_before/limit,'mean_candidate':cycles_after/limit,
      'mean_delta':(cycles_after-cycles_before)/limit,
      'delta_histogram':{str(k):v for k,v in sorted(hist.items())},
      'scratch_byte_changed_for_cases':changed_scratch_count,
      'public_output_correct':True,'caller_inputs_preserved':True,
      'incoming_carry_covered':True,'examples':examples,
      'production_suitability':'PENDING relocation, source ownership, VICE and full mixed-call contracts',
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cases',type=int,default=65536)
    ap.add_argument('--out',type=Path)
    arg=ap.parse_args()
    assert 1<=arg.cases<=65536
    report=run(arg.cases)
    if arg.out:
        arg.out.parent.mkdir(parents=True,exist_ok=True)
        arg.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('UMUL8 V2 PUBLIC DIRECT-OUTPUT PROOF',report['status'],
          report['public_same_input_calls'],
          'baseline',report['mean_before'],'candidate',report['mean_candidate'],
          'delta',report['mean_delta'],'mixed',report['mixed_post_UMUL8_UMUL16_calls'],flush=True)

if __name__=='__main__':main()
