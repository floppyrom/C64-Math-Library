#!/usr/bin/env python3
"""Issue 144: actual placed NMOS-6510 quotient-digit producer (REU + UMUL8).

Research-only performance rejection gate. This is ONE radix-256 digit with
normalized divisor and incoming remainder (0<=R<D); NOT a complete UDIV32_16.
Uses a 64KiB q0,t0 lookup stored in V4 REU bank $20, one 2-byte DMA transfer,
the shipped public MATH_UMUL8 for the low product, and bounded 17-bit
correction code. Checks the *assembled* output, C, scratch and same-call CPU
instruction timing. REU bus occupancy / VIC contention is not modeled.
No existing resident image, ABI, REU release image or OptiSearch source changes.
"""
from __future__ import annotations
import hashlib
import json
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler
from benchmark_multiply_refresh import load
from issue144_u3216_radix256_numerical_research import LOOKUP_Q_R

ASM="""
!cpu 6510
* = $0D00
digit:
    ; $70/$71=R; $72/$73=normalized D ($8000..$FFFF); $74=incoming digit
    ; $75=output quotient digit; $76/$77=REU q0,t0; $79..$7B=signed temp
    ; Table record offset = ((Dhi-128)<<9) + (Rhi<<1):
    ; Low = Rhi<<1; high= (Dhi<<1 with carry from Rhi<<1).
    lda $71
    asl
    sta $df04
    lda $73
    rol
    sta $df05
    lda #$20
    sta $df06
    lda #$76
    sta $df02
    lda #$00
    sta $df03
    lda #$02
    sta $df07
    lda #$00
    sta $df08
    sta $df0a
    lda #$91
    sta $df01
    ; q0 * divisor-low, using certified public 8x8 -> 16-bit producer
    lda $76
    sta $75
    sta $c000
    lda $72
    sta $c004
    jsr $3000

    ; T = ((t0+Rlo)<<8) + nextByte - (q0*Dlo), signed 24-bit
    clc
    lda $77
    adc $70
    sta $7a
    lda #$00
    adc #$00
    sta $7b
    lda $74
    sec
    sbc $c008
    sta $79
    lda $7a
    sbc $c009
    sta $7a
    lda $7b
    sbc #$00
    sta $7b

negative_check:
    lda $7b
    bpl positive_check
    dec $75
    clc
    lda $79
    adc $72
    sta $79
    lda $7a
    adc $73
    sta $7a
    lda $7b
    adc #$00
    sta $7b
    jmp negative_check

positive_check:
    lda $7b
    bne positive_take
    lda $7a
    cmp $73
    bcc finish
    bne positive_take
    lda $79
    cmp $72
    bcc finish
positive_take:
    inc $75
    sec
    lda $79
    sbc $72
    sta $79
    lda $7a
    sbc $73
    sta $7a
    lda $7b
    sbc #$00
    sta $7b
    jmp positive_check
finish:
    lda $79
    sta $70
    lda $7a
    sta $71
    clc
    rts
"""

def vectors():
    r=random.Random(0x144D6510)
    v=[]
    for d in [0x8000,0x8001,0x80ff,0x9001,0xbf55,0xff00,0xff01,0xfffe,0xffff]:
        for rem in [0,1,2,127,128,255,256,257,d//2,max(0,d-257),d-2,d-1]:
            if rem<d:
                for byte in [0,1,127,128,255]:
                    v.append((rem,byte,d))
    v += [(r.randrange(d:=r.randrange(32768,65536)),r.randrange(256),d)
          for _ in range(3500)]
    return v

def percentile(a,p):
    return sorted(a)[round((len(a)-1)*p)]

def main():
    code,labels,_=Assembler().assemble(ASM)
    start=labels["digit"]
    assert min(code)==0x0d00 and max(code)<0x1000
    c,api=load("v4_reu_16m")
    assert api["MATH_UMUL8"]==0x3000
    assert len(c.reu)>=0x210000
    assert all(b==0 for b in c.reu[0x200000:0x210000]), "REU bank $20 already used: refuse ownership"
    c.reu[0x200000:0x210000]=LOOKUP_Q_R
    for pc,val in code.items(): c.mem[pc]=val
    cycles=[];by_fix={};corrections=Counter()
    corpus=hashlib.sha256();vectors_list=vectors()
    for i,(rem,byte,d) in enumerate(vectors_list):
        corpus.update(rem.to_bytes(2,"little")+bytes((byte,))+d.to_bytes(2,"little"))
        assert 0<=rem<d
        c.mem[0x70]=rem&255;c.mem[0x71]=rem>>8
        c.mem[0x72]=d&255;c.mem[0x73]=d>>8
        c.mem[0x74]=byte;c.mem[0x75]=0
        c.c=i&1;c.d=0
        sp=c.sp
        cy=c.call(start,5000)
        q=c.mem[0x75]
        got=c.mem[0x70]+(c.mem[0x71]<<8)
        expected_q,expected_r=divmod((rem<<8)|byte,d)
        assert (q,got)==(expected_q,expected_r),(
            i,hex(rem),hex(d),byte,q,got,expected_q,expected_r)
        assert c.c==0 and c.sp==sp and c.d==0
        assert c.mem[0x72]==d&255 and c.mem[0x73]==d>>8 and c.mem[0x74]==byte
        # Actual correction count from the table seed; this does not depend on
        # CPU implementation and is checked against the normalized oracle.
        addr=(((d>>8)-128)<<9)|((rem>>8)<<1)
        seed=LOOKUP_Q_R[addr]
        fix=expected_q-seed
        assert -2<=fix<=2
        corrections[fix]+=1
        cycles.append(cy)
        by_fix.setdefault(fix,[]).append(cy)
    result={"status":"PASS_REAL_ASSEMBLED_NMOS6510_MODEL",
            "scope":"ONE digit only, not all 32/16 public producer",
            "profile":"v4_reu_16m",
            "cases":len(cycles),"corpus_sha256":corpus.hexdigest(),
            "start":hex(start),"code_bytes":len(code),
            "code_sha256":hashlib.sha256(bytes(code[a] for a in sorted(code))).hexdigest(),
            "extra_normal_zp_bytes":16,"scratch":"$70-$7F (outside current normal ZP pools)",
            "reu_table_bank":"$20","reu_lookup_bytes":65536,
            "uses_certified_MATH_UMUL8":True,
            "mean_cycles_one_digit":statistics.mean(cycles),
            "median_cycles_one_digit":statistics.median(cycles),
            "p95_cycles_one_digit":percentile(cycles,.95),
            "max_cycles_one_digit":max(cycles),
            "min_cycles_one_digit":min(cycles),
            "cycles_by_quotient_correction":{
                str(k):{"cases":len(v),"mean":statistics.mean(v),
                        "max":max(v)} for k,v in sorted(by_fix.items())},
            "correction_counts":dict(sorted(corrections.items())),
            "cycles_exclude_caller_JSR_and_REU_bus_wait":True,
            "full32_divide_saving_proven":False,
            "normal_public_ABI_qualified":False,
            "native_VICE_qualified":False,
            "production_binary_changed":False,
            "private_optisearch_published":False}
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
