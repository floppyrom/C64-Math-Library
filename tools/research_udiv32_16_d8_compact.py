#!/usr/bin/env python3
"""Compact looped D<256 path on the split/in-place/direct UDIV32/16 candidate."""
from pathlib import Path
import random,sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import load,wr,rd,expected

def tail_bit(i,q):
 return f"""
g{i}:
    rol {q}
    rol $16
    rol a
    bcs gf{i}
    cmp $13
    bcc gn{i}
    bne gt{i}
    ldx $16
    cpx $12
    bcc gn{i}
gt{i}:
    tax
    lda $16
    sbc $12
    sta $16
    txa
    sbc $13
    bcs gn{i}
gf{i}:
    tax
    lda $16
    sbc $12
    sta $16
    txa
    sbc $13
    sec
gn{i}:
"""

def source():
 g=[]
 for i in range(8):g.append(tail_bit(i,'$19'))
 g.append("    rol $19\n")
 for i in range(8,16):g.append(tail_bit(i,'$18'))
 return f"""
*=$A800
candidate:
    lda $13
    bne general
    lda $12
    beq d8_zero_stub
    jmp d8
d8_zero_stub:
    jmp zero
general:
    jsr $420C
    bcc nz
    jmp zero
nz:
    lda $17
{''.join(g)}
    rol $18
    sta $C01D
    lda $18
    sta $C018
    lda $19
    sta $C019
    lda $14
    sta $C01A
    lda $15
    sta $C01B
    lda $16
    sta $C01C
    clc
    rts

; Compact 32/8 restoring divider. N bytes already live in $18,$19,$10,$11.
; Process one quotient byte at a time from MSB to LSB. A is the 8-bit residual.
d8:
    lda #0
    ldy #4
    ldx #8
d8_b3:
    rol $11
    rol a
    bcs d8_force3
    cmp $12
    bcc d8_next3
    sbc $12
    bcs d8_next3
d8_force3:
    sbc $12
    sec
d8_next3:
    dex
    bne d8_b3
    rol $11
    ldx #8
d8_b2:
    rol $10
    rol a
    bcs d8_force2
    cmp $12
    bcc d8_next2
    sbc $12
    bcs d8_next2
d8_force2:
    sbc $12
    sec
d8_next2:
    dex
    bne d8_b2
    rol $10
    ldx #8
d8_b1:
    rol $19
    rol a
    bcs d8_force1
    cmp $12
    bcc d8_next1
    sbc $12
    bcs d8_next1
d8_force1:
    sbc $12
    sec
d8_next1:
    dex
    bne d8_b1
    rol $19
    ldx #8
d8_b0:
    rol $18
    rol a
    bcs d8_force0
    cmp $12
    bcc d8_next0
    sbc $12
    bcs d8_next0
d8_force0:
    sbc $12
    sec
d8_next0:
    dex
    bne d8_b0
    rol $18
    sta $C01C
    lda #0
    sta $C01D
    lda $18
    sta $C018
    lda $19
    sta $C019
    lda $10
    sta $C01A
    lda $11
    sta $C01B
    clc
    rts
zero:
    lda #0
    sta $C018
    sta $C019
    sta $C01A
    sta $C01B
    sta $C01C
    sta $C01D
    sec
    rts
"""

def install(cpu,A):
 mem,lab,_=Assembler().assemble(source())
 for a,b in mem.items():cpu.mem[a]=b
 e=A['MATH_UDIV32_16']; cpu.mem[e+30]=0x4c;cpu.mem[e+31]=lab['candidate']&255;cpu.mem[e+32]=lab['candidate']>>8
 return max(mem)-min(mem)+1

def make():
 r=random.Random(0xD8C0); groups={}
 groups['uniform16']=[(r.getrandbits(32),r.randrange(1,65536)) for _ in range(40000)]
 groups['d8']=[(r.getrandbits(32),r.randrange(1,256)) for _ in range(30000)]
 hard=[]
 for d in list(range(1,33))+[63,127,128,129,254,255,256,257,511,65535]:
  for n in [0,1,d-1,d,d+1,0xffff,0xffffff,0xffffffff,max(0,0xffffffff-d),0x7fffffff]:
   if 0<=n<=0xffffffff:hard.append((n,d))
 groups['hard']=hard
 return groups

def run(cpu,e,vec):
 cc=[];err=0
 for n,d in vec:
  wr(cpu.mem,0xC010,n,4);wr(cpu.mem,0xC014,d,2)
  cy=cpu.call(e,4_000_000); eq,er,ec=expected(n,d,32,16)
  if (rd(cpu.mem,0xC018,4),rd(cpu.mem,0xC01C,2),cpu.c)!=(eq,er,ec):err+=1
  cc.append(cy)
 return cc,err

def st(c):return {'mean':sum(c)/len(c),'min':min(c),'max':max(c)}
def main():
 out={'status':'PASS','groups':{}}
 for tag,vec in make().items():
  rows={}
  for name,new in [('old',False),('compact',True)]:
   cpu,A=load('v2_pareto_fast');size=install(cpu,A) if new else None
   c,e=run(cpu,A['MATH_UDIV32_16'],vec);assert e==0
   rows[name]=(c,size)
  d=[a-b for a,b in zip(rows['old'][0],rows['compact'][0])]
  out['groups'][tag]={'old':st(rows['old'][0]),'compact':{**st(rows['compact'][0]),'research_image_bytes':rows['compact'][1]},'saved_mean':sum(d)/len(d),'min_saved':min(d),'max_saved':max(d),'slower':sum(x<0 for x in d)}
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
