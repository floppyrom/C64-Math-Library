#!/usr/bin/env python3
"""Research D<256 fast path on top of split/in-place/direct UDIV32/16."""
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

def d8_bit(i,q):
 return f"""
d8_{i}:
    rol {q}
    rol a
    bcs d8_take_{i}
    cmp $12
    bcc d8_no_{i}
d8_take_{i}:
    sbc $12
d8_no_{i}:
"""

def source():
 g=[]
 for i in range(8):g.append(tail_bit(i,'$19'))
 g.append("    rol $19\n")
 for i in range(8,16):g.append(tail_bit(i,'$18'))
 d8=[]
 idx=0
 for q in ('$11','$10','$19','$18'):
  for _ in range(8):
   d8.append(d8_bit(idx,q));idx+=1
  d8.append(f"    rol {q}\n")
 return f"""
*=$A800
candidate:
    lda $13
    bne general
    lda $12
    bne d8_dispatch
    jmp zero
d8_dispatch:
    jmp d8
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
d8:
    lda #0
{''.join(d8)}
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
 e=A['MATH_UDIV32_16'];assert cpu.mem[e+30]==0x20
 cpu.mem[e+30]=0x4c;cpu.mem[e+31]=lab['candidate']&255;cpu.mem[e+32]=lab['candidate']>>8

def group(seed,count,lo,hi):
 r=random.Random(seed);return [(r.getrandbits(32),r.randrange(lo,hi)) for _ in range(count)]

def run(cpu,e,vec):
 c=[];err=0;worst=[]
 for n,d in vec:
  wr(cpu.mem,0xC010,n,4);wr(cpu.mem,0xC014,d,2)
  cy=cpu.call(e,4_000_000);eq,er,ec=expected(n,d,32,16)
  got=(rd(cpu.mem,0xC018,4),rd(cpu.mem,0xC01C,2),cpu.c)
  if got!=(eq,er,ec):
   err+=1
   if err<5:print('ERR',hex(n),hex(d),got,(eq,er,ec))
  c.append(cy);worst.append((cy,n,d))
 return c,err,sorted(worst,reverse=True)[:8]

def st(c):return {'mean':sum(c)/len(c),'min':min(c),'max':max(c)}
def main():
 groups={
  'uniform16':group(1,50000,1,65536),
  'd8':group(2,30000,1,256),
  'd9':group(3,10000,256,512),
  'd10_12':group(4,10000,512,4096),
 }
 # deterministic hard boundaries
 hard=[]
 for d in list(range(1,33))+[63,127,128,129,254,255,256,257,511,512,1023,4095,65535]:
  for n in [0,1,d-1,d,d+1,0xffff,0xffffff,0xffffffff,max(0,0xffffffff-d),0xffffffff//2]:
   if 0<=n<=0xffffffff:hard.append((n,d))
 groups['hard']=hard
 out={'status':'PASS','groups':{}}
 for tag,vec in groups.items():
  rows={}
  for name,new in [('old',False),('candidate',True)]:
   cpu,A=load('v2_pareto_fast')
   if new:install(cpu,A)
   cyc,err,w=run(cpu,A['MATH_UDIV32_16'],vec);assert err==0
   rows[name]={**st(cyc),'worst':[(x,hex(n),hex(d)) for x,n,d in w],'cycles':cyc}
  d=[a-b for a,b in zip(rows['old']['cycles'],rows['candidate']['cycles'])]
  for x in rows.values():x.pop('cycles')
  out['groups'][tag]={'old':rows['old'],'candidate':rows['candidate'],'saved_mean':sum(d)/len(d),'min_saved':min(d),'max_saved':max(d),'slower':sum(x<0 for x in d)}
 print(json.dumps(out,indent=2))
 (ROOT/'validation/research').mkdir(exist_ok=True)
 (ROOT/'validation/research/UDIV32_16_D8_FAST.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
