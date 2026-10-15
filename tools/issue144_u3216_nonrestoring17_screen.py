#!/usr/bin/env python3
"""Issue #144 B: independent assembled 6510 non-restoring 17-bit low-tail screen.

An all-domain alternative to V2/V3/V4's 16 unrolled restoring quotient bits.
Unlike a domain guard, it uses signed-17-bit add/sub each iteration. Two identical
oracle-seeded remainder inputs are compared on exactly the same N32/D16 corpus.

Research-only: this is neither a full public call nor a viable improvement
until the 6510 cycle gate passes. All tests and source are public/independent.
"""
from __future__ import annotations
import argparse,hashlib,json,random,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU,Assembler
from issue144_u3216_shared_take_tail_research import source as stock_source,inputs

START=0x2070
STOP=0x07ff

def nonrestoring_source():
    # $30-$31 D16; $32 and $35 = residual R16; $36 = signed
    # extension byte FF when R<0 and 00 when R>=0.
    # Qlow/Qhigh source/quotient reuse $33/$34, exactly like stock.
    # S=FF or 00 between iterations. After left shift S becomes FE/FF
    # or 00/01, preserving the sign of the previous signed residual.
    out=["* = $2070","lda #0","sta $36","clc"]
    for i in range(16):
        q="$34" if i<8 else "$33"
        out += [
            f"STEP_{i}:",
            f"rol {q}","rol $32","rol $35","rol $36",
            f"bmi ADD_{i}",
            "sec","lda $32","sbc $30","sta $32",
            "lda $35","sbc $31","sta $35",
            "lda $36","sbc #0","sta $36",
            f"jmp TEST_{i}",
            f"ADD_{i}:",
            "clc","lda $32","adc $30","sta $32",
            "lda $35","adc $31","sta $35",
            "lda $36","adc #0","sta $36",
            f"TEST_{i}:",
            "lda $36",f"bmi NEG_{i}","sec",f"jmp NEXT_{i}",
            f"NEG_{i}:","clc",f"NEXT_{i}:",
        ]
        if i==7:
            out.append("rol $34")
    out += ["rol $33","lda $36","bpl DONE","clc",
            "lda $32","adc $30","sta $32",
            "lda $35","adc $31","sta $35",
            "DONE:","jmp $07FF"]
    return "\n".join(out)+"\n"

def assembled(text):
    code,labels,_=Assembler().assemble(text)
    assert min(code)==START
    assert STOP not in code
    return code

def execute(code,n,d):
    assert 1<=d<=65535
    seed=(n>>16)%d
    m=bytearray(65536)
    for addr,val in code.items():m[addr]=val
    for addr,val in ((0x30,d&255),(0x31,d>>8),
                     (0x32,seed&255),(0x35,seed>>8),
                     (0x33,n&255),(0x34,(n>>8)&255)):
        m[addr]=val
    cpu=CPU(m,pc=START,sp=255,d=0)
    for _ in range(1600):
        if cpu.pc==STOP:break
        cpu.step()
    else:raise AssertionError(("nonterminating",hex(n),hex(d),hex(cpu.pc)))
    assert cpu.sp==255 and cpu.d==0
    assert m[0x30]==(d&255) and m[0x31]==(d>>8)
    q=m[0x33]|m[0x34]<<8
    rem=m[0x32]|m[0x35]<<8
    return q,rem,cpu.cycles,m[0x36]

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--random-extra",type=int,default=0)
    args=a.parse_args()
    original=assembled(stock_source("shared"))
    candidate=assembled(nonrestoring_source())
    # One whole iteration always derives its quotient bit from final
    # 17-bit sign, not a speculative compare or data-dependent fallback.
    corpus=inputs()
    rng=random.Random(0x144B17)
    corpus.extend((rng.getrandbits(32),rng.randrange(1,65536)) for _ in range(args.random_extra))
    delta=[];t0=[];t1=[];by_domain={"D8":[],"lowD16":[],"highD16":[]}
    for i,(n,d) in enumerate(corpus):
        stock=execute(original,n,d)
        trial=execute(candidate,n,d)
        want=((n//d)&0xffff,n%d)
        assert stock[:2]==trial[:2]==want,("incorrect",i,hex(n),hex(d),stock,trial,want)
        assert trial[3] in (0,255),("17-bit sign invariant",i,hex(n),hex(d),trial)
        diff=stock[2]-trial[2]
        t0.append(stock[2]);t1.append(trial[2]);delta.append(diff)
        domain="D8" if d<256 else ("lowD16" if d<32768 else "highD16")
        by_domain[domain].append(diff)
    def report(v):
        s=sorted(v)
        return {"pairs":len(v),"mean_saved":statistics.mean(v),
                "p05_saved":s[int(.05*(len(s)-1))],
                "p95_saved":s[int(.95*(len(s)-1))],
                "worst_saved":s[0],"best_saved":s[-1],
                "slower":sum(z<0 for z in v),"equal":sum(z==0 for z in v)}
    summary={
      "status":"PASS_EXACT_ASSEMBLED_LOW16_NONRESTORING_SCREEN",
      "research_only":True,
      "full_public_abi_qualified":False,
      "native_vice_qualified":False,
      "public_reference_prgs_modified":False,
      "optisearch_private_code_included":False,
      "pairs":len(corpus),
      "corpus_sha256":hashlib.sha256(b"".join(n.to_bytes(4,"little")+d.to_bytes(2,"little") for n,d in corpus)).hexdigest(),
      "stock_lowtail_bytes":len(original),
      "candidate_lowtail_bytes":len(candidate),
      "stock_mean_cycles":statistics.mean(t0),
      "nonrestoring_mean_cycles":statistics.mean(t1),
      "summary":report(delta),
      "by_divisor_class":{k:report(v) for k,v in by_domain.items()},
      "decision":"PROMOTION_SCREEN_PASS" if statistics.mean(delta)>25 and min(delta)>=-5 and len(candidate)<=len(original)+64
                 else "REJECT_DEFAULT_PROMOTION_PARETO_OR_SIZE",
    }
    print(json.dumps(summary,sort_keys=True,indent=2))

if __name__=="__main__":main()
