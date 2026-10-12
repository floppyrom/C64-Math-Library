#!/usr/bin/env python3
"""Issue #39: can an N24 operand reuse the resident unsigned 24/24 divider?

Research only. This script executes both *real* 32/16 public entrypoints
and a 30-byte, noninstalled N24->UDIV24 adapter at two actual RAM locations.
It restores the public DIV/MOD state including D2/R2 and checks stack balance.
No production source or resident binary is modified.
"""
import argparse, hashlib, json, random, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import PROFILES,load,wr,rd
N,D,Q,R=0xC010,0xC014,0xC018,0xC01C
OPS=('MATH_UDIV32_16','MATH_UMOD32_16')
SRC="""* = $%04X
N24_TO_U24:
    lda $C01E
    pha
    lda $C016
    pha
    lda #0
    sta $C016
    jsr $3170
    pla
    sta $C016
    pla
    sta $C01E
    lda #0
    sta $C01B
    rts
"""
def inputs():
    g=random.Random(0x20263924)
    return {
      'n24_d8':[(g.randrange(1<<24),g.randrange(1,256)) for _ in range(128)],
      'n24_dhi':[(g.randrange(1<<24),g.randrange(256,1<<16)) for _ in range(128)],
      'n16_dhi':[(g.randrange(1<<16),g.randrange(256,1<<16)) for _ in range(128)],
      'q0':[(g.randrange(1<<14),g.randrange(1<<14,1<<16)) for _ in range(128)],
      'zero':[(g.randrange(1<<24),0) for _ in range(32)],
      'edges':[(n,d) for n in (0,1,255,256,65535,65536,(1<<24)-1)
                     for d in (0,1,255,256,65535)]}
def sample(cpu,entry,n,d):
    mem=cpu.mem
    wr(mem,N,n,4);wr(mem,D,d,2)
    mem[0xC016]=0x75;mem[0xC017]=0xA6;mem[0xC020]=0x49
    wr(mem,Q,0xA9C6D8E5,4);wr(mem,R,0x5A721BC3,4)
    cpu.d=0;sp=cpu.sp
    ticks=cpu.call(entry,4_000_000)
    state=(rd(mem,Q,4),rd(mem,R,4),cpu.c,rd(mem,N,4),
           rd(mem,D,2),mem[0xC016],mem[0xC017],mem[0xC020],cpu.sp)
    assert state[3:]==(n,d,0x75,0xA6,0x49,sp),(entry,n,d,'preserve',state)
    assert state[0]==(n//d if d else 0)
    assert state[1]&0xFFFF==(n%d if d else 0)
    assert state[2]==int(d==0)
    return ticks,state
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    release=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
    result={'status':'PASS_RESEARCH_NO_DEFAULT_PROMOTION','source':'tools/screen_issue39_n24_u24_donor.py',
       'candidate_precondition':'N < 2**24','candidate_code_bytes':30,
       'candidate_additional_stack_bytes':4,'overlay_ram_addresses':['0800','0B00'],
       'source_or_resident_modified':False,'native_vice_calls':0,
       'cycle_model':'pure 6502 instructions, no VIC/REU bus contention',
       'profiles':{},'compared_pairs':0,'cpu_calls':0,'abi_errors':0}
    for profile in PROFILES:
        image=ROOT/profile/'resident'/f'math_{profile}_game_math.prg'
        sha=hashlib.sha256(image.read_bytes()).hexdigest()
        assert sha==release['reference_prg_sha256'][profile],(profile,sha)
        base,entries=load(profile);cand,check=load(profile)
        assert entries==check and entries['MATH_UDIV24']==0x3170
        assert entries['MATH_UDIV32_16']==0x31B0
        assert entries['MATH_UMOD32_16']==0x3226
        report={'resident_sha256':sha,'operations':{}}
        for address in (0x0800,0x0B00):
            code,labels,_=Assembler().assemble(SRC%address)
            assert len(code)==30 and labels['N24_TO_U24']==address
            assert all(cand.mem[x]==0 for x in code),(profile,hex(address),'RAM in use')
            for a,b in code.items():cand.mem[a]=b
            for op in OPS:
                groups={}
                for name,vec in inputs().items():
                    diff=[];input_hash=hashlib.sha256();cycle_hash=hashlib.sha256()
                    for n,d in vec:
                        input_hash.update(n.to_bytes(4,'little')+d.to_bytes(2,'little'))
                        t0,v0=sample(base,entries[op],n,d)
                        t1,v1=sample(cand,address,n,d)
                        assert v0==v1,(profile,hex(address),op,name,n,d,v0,v1)
                        diff.append(t1-t0)
                        cycle_hash.update(t0.to_bytes(4,'little')+t1.to_bytes(4,'little'))
                        result['compared_pairs']+=1;result['cpu_calls']+=2
                    groups[name]={'cases':len(vec),'mean_delta':sum(diff)/len(diff),
                        'faster':sum(v<0 for v in diff),'slower':sum(v>0 for v in diff),
                        'equal':sum(v==0 for v in diff),'best_gain':-min(diff),
                        'worst_regression':max(diff),
                        'input_sha256':input_hash.hexdigest(),
                        'paired_cycles_sha256':cycle_hash.hexdigest()}
                report['operations'][f'{op}_{address:04X}']=groups
            for address_byte in code:cand.mem[address_byte]=0
        result['profiles'][profile]=report
        print(profile,'PASS; UDIV32_16+UMOD32_16; two RAM placements',flush=True)
    assert result['compared_pairs']==11580 and result['cpu_calls']==23160
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('ISSUE39 N24/U24 donor screen PASS',result['cpu_calls'],flush=True)
if __name__=='__main__':main()
