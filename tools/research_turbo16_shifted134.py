#!/usr/bin/env python3
from pathlib import Path
import random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler,CPU

CAND=ROOT/'relocatable_source/turbo/turbo16_shifted134_candidate.asm'
PRG=ROOT/'v3_reu_512k/resident/math_v3_reu_512k_game_math.prg'
MATH_IO=0xC000; MATH_INIT=0x3280
BASE=0x3E; REG_TABLE=0x6000
cfg=f'''REG_TABLE = $6000
MATH_IO = $C000
TURBO16_ZP_BASE = $003E
'''
wrapper=r'''
* = $4000
T16X_PUBLIC_TEST:
    ldx MATH_IO+$05
    lda MATH_IO+$00
    sta+1 T16X_x0
    lda MATH_IO+$01
    sta+1 T16X_x1
    stx+1 T16X_y1
    ldy MATH_IO+$04
    jsr T16X_umult_ax1
    sta MATH_IO+$0A
    stx MATH_IO+$09
    sty MATH_IO+$0B
    lda+1 T16X_z0
    sta MATH_IO+$08
    clc
    rts
'''
mem,labels,const=Assembler().assemble(cfg+CAND.read_text()+wrapper)
size=labels['T16X_zp_end']-labels['T16X_zp_start']
print('candidate_zp_bytes',size)
for n in ['T16X_umult','T16X_umult_ax1','T16X_x0','T16X_x1','T16X_y1','T16X_z0','T16X_zp_end']:
    print(n,hex(labels.get(n,const.get(n))))

def load_prg(path):
    b=path.read_bytes(); ld=b[0]|b[1]<<8
    m=bytearray(65536);m[ld:ld+len(b)-2]=b[2:];return m

m=load_prg(PRG); c=CPU(m); c.d=0; c.call(MATH_INIT,2_000_000)
for a,v in mem.items(): c.mem[a]=v

BIAS=202
# The resident library's four common multiply planes use complemented negative
# rows for ADC. shifted134 was qualified against the publication form with
# plain negative-square rows and SBC, so install all six exact candidate planes
# for this isolated A/B benchmark rather than accidentally mixing conventions.
for i in range(511):
    q=(i*i)//4 + BIAS*(i&1)
    j=255-i
    nq=(j*j)//4 + BIAS*(j&1)
    c.mem[REG_TABLE+0x1000+i]=q&255
    c.mem[REG_TABLE+0x1200+i]=(q>>8)&255
    c.mem[REG_TABLE+0x1400+i]=nq&255
    c.mem[REG_TABLE+0x1600+i]=(nq>>8)&255
    c.mem[REG_TABLE+0x0800+i]=((q+256)>>8)&255
    c.mem[REG_TABLE+0x0A00+i]=(nq+1)&255

def wr16(a,v):
    c.mem[a]=v&255;c.mem[a+1]=(v>>8)&255
def rd32(a):
    return sum(c.mem[a+i]<<(8*i) for i in range(4))

edge=[0,1,2,3,0xff,0x100,0x101,0x7fff,0x8000,0xfffe,0xffff]
pairs=[(a,b) for a in edge for b in edge]
rng=random.Random(0x54313658)
pairs += [(rng.randrange(65536),rng.randrange(65536)) for _ in range(20000)]
tot=0;mn=10**9;mx=0
for x,y in pairs:
    wr16(MATH_IO,x);wr16(MATH_IO+4,y)
    cy=c.call(labels['T16X_PUBLIC_TEST'],100000)
    got=rd32(MATH_IO+8)
    if got != x*y: raise AssertionError((hex(x),hex(y),hex(got),hex(x*y)))
    tot+=cy;mn=min(mn,cy);mx=max(mx,cy)
print('PASS',len(pairs),'public_mean',f'{tot/len(pairs):.6f}','min',mn,'max',mx)
