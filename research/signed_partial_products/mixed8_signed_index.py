from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler,CPU,load_sparse
F=[(k*k)//4-64*k+4160 for k in range(511)]
G=[(k*k)//4-63*k-(k//2)+4096 for k in range(511)]
# reverse difference orientation: Grev[k]=G[510-k]
GR=list(reversed(G))
src='''*=$1000
mixed8_u_bound_s_index:
 ; A=unsigned u to bind, Y=raw signed s
 sta sm1
 sta sm3
 eor #$ff
 sta sm2
 sta sm4
 tya
 eor #$80
 tax
 sec
sm1=*+1
 lda $2000,x
sm2=*+1
 adc $2400,x
 tay
sm3=*+1
 lda $2200,x
sm4=*+1
 adc $2600,x
 rts
'''
a=Assembler();md,lab,_=a.assemble(src);base=load_sparse(md)
for k,v in enumerate(F):base[0x2000+k]=v&255;base[0x2200+k]=(v>>8)&255
for k,v in enumerate(GR):base[0x2400+k]=255-(v&255);base[0x2600+k]=255-((v>>8)&255)
tot=0;mn=999;mx=0;hist={};err=0;cerr=0
for u in range(256):
 for sraw in range(256):
  s=sraw if sraw<128 else sraw-256
  c=CPU(bytearray(base));c.a=u;c.y=sraw;cy=c.call(lab['mixed8_u_bound_s_index']);got=c.y|(c.a<<8);exp=(u*s)&0xffff
  if got!=exp:
   err+=1
   if err<5:print('ERR',u,sraw,hex(got),hex(exp))
  if c.c!=int(u*s>=0):cerr+=1
  tot+=cy;mn=min(mn,cy);mx=max(mx,cy);hist[cy]=hist.get(cy,0)+1
print(json.dumps({'errors':err,'carry_errors':cerr,'mean':tot/65536,'min':mn,'max':mx,'hist':hist,'code_bytes':max(md)-0x1000+1},indent=2))
