#!/usr/bin/env python3
"""Issue39: public ABI A/B for 32÷16 dispatching N<65536 to existing 16÷16.

Ephemeral RAM overlay, NOT production source. Complete resident images, identical
input pairs, both 32/16 public APIs, five profiles, exact full Q/R/C/N/D/SP
and sentinel behavior. Existing public entry starts with LDA MATH_N; restore
it in the rejecting branch, then enter at original entry+3.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,json,random,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,load,api,wr,rd,expected
from benchmark_unsigned_common_corpus import corpus,SPECS
from benchmark_unsigned_3216_workloads import WORKLOADS,pairs as width_pairs
N,D,Q,REM=0xc010,0xc014,0xc018,0xc01c
DIV=0x31b0
MOD=0x3226
DELEGATE=0x3140
OVERLAY=0xe100
SOURCE="""* = $E100
N16_GATE:
    lda $C012
    ora $C013
    bne ORIGINAL
    jsr $3140
    lda #0
    sta $C01A
    sta $C01B
    rts
ORIGINAL:
    lda $C010
    jmp $31B3
"""
CODE,LABELS,_=Assembler().assemble(SOURCE)
assert len(CODE)==26 and LABELS['N16_GATE']==OVERLAY and LABELS['ORIGINAL']==OVERLAY+20
OPS=('MATH_UDIV32_16','MATH_UMOD32_16')
def inputs(op):
    spec=next(x for x in SPECS if x[0]==op)
    result={'official':[(n,d) for n,d,_ in corpus(op,spec[1],spec[2],spec[5],spec[7])[1]]}
    result.update({name:width_pairs(name) for name in WORKLOADS})
    rng=random.Random(0x3216a000+(0 if op==OPS[0] else 1))
    result['n16_target']=[(rng.randrange(1<<16),rng.randrange(1<<16)) for _ in range(1024)]
    result['n16_small_d']=[(rng.randrange(1<<16),rng.randrange(1,256)) for _ in range(512)]
    result['n24_target']=[(rng.randrange(1<<24),rng.randrange(1<<16)) for _ in range(512)]
    result['n32_target']=[(rng.randrange(1<<32),rng.randrange(1<<16)) for _ in range(512)]
    result['n16_zero_divisor']=[(rng.randrange(1<<16),0) for _ in range(64)]
    return result
def sample(cpu,entry,n,d):
    m=cpu.mem
    wr(m,N,n,4);wr(m,D,d,2)
    wr(m,Q,0xa9c6d8e5,4)
    wr(m,REM,0x5a721bc3,4)
    m[0xc013]=n>>24
    m[0xc017]=0x75
    m[0xc020]=0xa6
    cpu.d=0;sp=cpu.sp
    cycles=cpu.call(entry,4_000_000)
    q,r,c=expected(n,d,32,16)
    got=(rd(m,Q,4),rd(m,REM,4),cpu.c,rd(m,N,4),rd(m,D,2),
         m[0xc017],m[0xc020],cpu.sp)
    # The public 32/16 divider and its modulo alias both materialize Q32.
    assert got[0]==q and got[1]&0xffff==r and got[2]==c
    assert got[3:]==(n,d,0x75,0xa6,sp)
    return cycles,got
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path)
    a=p.parse_args()
    state=json.loads((R/'RELEASE_STATUS.json').read_text())
    report={'status':'PASS_RESEARCH_SCREEN','source':str(Path(__file__).relative_to(R)),
      'overlay_assembly':SOURCE,'overlay_address':hex(OVERLAY),
      'overlay_code_bytes':26,'patched_public_bytes':3,
      'normal_zp_growth':0,'extra_stack_frame_on_n16':2,
      'resident_binary_changed':False,'ROM_visible_overlay_not_qualified':True,
      'native_vice_calls':0,'instruction_timing_not_bus_timing':True,
      'profiles':{},'totals':{'old_new_calls':0,'compared_input_pairs':0,'mismatches':0}}
    for profile in PROFILES:
        live=(R/profile/'resident'/('math_'+profile+'_game_math.prg')).read_bytes()
        h=hashlib.sha256(live).hexdigest()
        assert h==state['reference_prg_sha256'][profile],(profile,h)
        base,entries=load(profile)
        new,check=load(profile)
        assert entries==check and entries['MATH_UDIV32_16']==DIV and entries['MATH_UMOD32_16']==MOD
        assert bytes(base.mem[DIV:DIV+3])==bytes.fromhex('ad10c0')
        assert bytes(base.mem[MOD:MOD+3])==bytes.fromhex('4cb031')
        assert not any(new.mem[x] for x in CODE)
        new.mem[DIV:DIV+3]=bytes((0x4c,OVERLAY&255,OVERLAY>>8))
        for address,byte in CODE.items():new.mem[address]=byte
        entry={'resident_sha256':h,'routines':{}}
        for op in OPS:
            entry['routines'][op]={}
            for group,vec in inputs(op).items():
                totals=[0,0];delta=[];by_n16=defaultdict(list)
                hinput=hashlib.sha256();hcycles=hashlib.sha256()
                for n,d in vec:
                    hinput.update(n.to_bytes(4,'little')+d.to_bytes(2,'little'))
                    prior,pa=sample(base,entries[op],n,d)
                    newer,na=sample(new,entries[op],n,d)
                    assert pa==na,(profile,op,group,hex(n),hex(d),pa,na)
                    hcycles.update(prior.to_bytes(4,'little')+newer.to_bytes(4,'little'))
                    totals[0]+=prior;totals[1]+=newer
                    diff=newer-prior;delta.append(diff)
                    by_n16['numerator_16' if n<65536 else 'numerator_wide'].append(diff)
                ncase=len(vec)
                row={'cases':ncase,'input_sha256':hinput.hexdigest(),'cycles_pair_sha256':hcycles.hexdigest(),
                    'baseline_mean':totals[0]/ncase,'candidate_mean':totals[1]/ncase,
                    'mean_delta':(totals[1]-totals[0])/ncase,
                    'faster':sum(d<0 for d in delta),'slower':sum(d>0 for d in delta),
                    'equal':sum(d==0 for d in delta),'max_regression':max(delta),
                    'max_speedup':-min(delta),
                    'by_numerator_width':{k:{'count':len(v),'mean_delta':sum(v)/len(v),
                        'faster':sum(x<0 for x in v),'slower':sum(x>0 for x in v)} for k,v in by_n16.items()}}
                entry['routines'][op][group]=row
                report['totals']['compared_input_pairs']+=ncase
                report['totals']['old_new_calls']+=2*ncase
                print(profile,op,group,ncase,'delta',f"{row['mean_delta']:+.3f}",
                    'f/s',row['faster'],row['slower'],flush=True)
        report['profiles'][profile]=entry
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('ISSUE39 N16 IN 32/16 PUBLIC TRANSPLANT SCREEN PASS',report['totals'],flush=True)
if __name__=='__main__':main()
