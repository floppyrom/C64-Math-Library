#!/usr/bin/env python3
"""Install the direct signed-domain quarter-square SMUL8 kernel.

The former native SMUL8 paths owned private executable code but still formed an
unsigned 8x8 product and corrected its high byte.  This refresh forms the signed
product directly with Q(a+b)-Q(a-b).

Only the two Q(a+b) planes are new.  Q(a-b) reuses the one's-complement
negative-square planes already shipped for UMUL24: the existing table at index i
contains ~Q(255-i), and the signed binding makes 255-i == a-b.  This cuts the
incremental table cost from 2044 to 1022 useful bytes.

No executable ZP or hardware stack page is reserved.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler,CPU
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m']
# new signed-sum low/high, existing UMUL24 complemented-difference low/high
TABLES={
 'v1_balanced':(0x6000,0x6200,0x8800,0x8A00),
 'v2_pareto_fast':(0x2600,0x6E00,0x6400,0x6600),
 'v3_reu_512k':(0x6800,0x6A00,0x6400,0x6600),
 'v4_reu_16m':(0x6800,0x6A00,0x6400,0x6600),
}
# Stale four-plane prototype locations from development; harmless/no-op on a
# clean pre-upgrade tree, and makes the tool idempotent during reproduction.
CLEAN_EXTRA={
 'v1_balanced':(0x6400,0x6600),
 'v2_pareto_fast':(0x9C00,0x9E00),
 'v3_reu_512k':(0x6C00,0x6E00),
 'v4_reu_16m':(0x6C00,0x6E00),
}
BIAS=202;ENTRY=0x3B80;X0=0xC000;Y0=0xC004;Z0=0xC008;Z1=0xC009

def sha(b):return hashlib.sha256(b).hexdigest()
def kernel(a,b,nl,nh):
 src=f'''*=$3b80
smul8_direct:
 lda $c000
 eor #$80
 sta sm1
 sta sm3
 eor #$ff
 sta sm2
 sta sm4
 lda $c004
 eor #$80
 tax
 sec
sm1=*+1
 lda ${a:04x},x
sm2=*+1
 adc ${nl:04x},x
 sta $c008
sm3=*+1
 lda ${b:04x},x
sm4=*+1
 adc ${nh:04x},x
 sta $c009
 clc
 rts
'''
 m,l,_=Assembler().assemble(src);return bytes(m[x] for x in range(ENTRY,max(m)+1)),l,src

def sumplane(high=False):
 out=[]
 for n in range(-256,255):
  q=(n*n)//4+BIAS*(n&1);out.append((q>>8)&255 if high else q&255)
 return bytes(out)
def exhaustive(mem):
 total=0;mn=999;mx=0;hist={};errs=0
 for x in range(256):
  sx=x if x<128 else x-256
  for y in range(256):
   sy=y if y<128 else y-256;m=bytearray(mem);m[X0]=x;m[Y0]=y;c=CPU(m);c.call(ENTRY,500)
   got=m[Z0]|m[Z1]<<8;exp=(sx*sy)&0xffff
   if got!=exp or c.c!=0:
    errs+=1
    if errs<5:print('ERR',x,y,hex(got),hex(exp),c.c)
   total+=c.cycles;mn=min(mn,c.cycles);mx=max(mx,c.cycles);hist[c.cycles]=hist.get(c.cycles,0)+1
 return {'cases':65536,'errors':errs,'mean_cycles':total/65536,'min_cycles':mn,'max_cycles':mx,'histogram':hist}

def main():
 rep={'status':'PASS','algorithm':'direct signed-domain quarter-square with shared complemented difference planes','parity_bias':BIAS,'profiles':{}}
 for p in PROFILES:
  path=ROOT/p/'resident'/f'math_{p}_game_math.prg';bb=path.read_bytes();load=bb[0]|bb[1]<<8;end=load+len(bb)-2;mem=bytearray(65536);mem[load:end]=bb[2:];before=sha(bb)
  slo,shi,nlo,nhi=TABLES[p];code,lab,src=kernel(slo,shi,nlo,nhi);assert len(code)==46
  mem[0x2000:0x2100]=bytes(0x100)
  # The 46-byte kernel fits in the stable 48-byte SMUL8 API slot, removing the old 3-cycle JMP stub.
  mem[0x3B80:0x3BB0]=bytes(0x30);mem[ENTRY:ENTRY+len(code)]=code
  # Clear only development-only extra planes. Never clear shared UMUL24 planes.
  for a in CLEAN_EXTRA[p]:mem[a:a+0x200]=bytes(0x200)
  # V2 $2600 used to contain the obsolete private unsigned clone; overwrite the full page pair.
  for a in (slo,shi):mem[a:a+0x200]=bytes(0x200)
  mem[slo:slo+511]=sumplane(False);mem[shi:shi+511]=sumplane(True)
  ev=exhaustive(mem)
  if ev['errors']:raise SystemExit(p+' failed')
  out=bytes((load&255,load>>8))+bytes(mem[load:end]);path.write_bytes(out)
  rep['profiles'][p]={'before_sha256':before,'after_sha256':sha(out),'entry':'$3B80','code_bytes':46,'zp_bytes':0,'stack_page_reserved_bytes':0,'new_table_useful_bytes':1022,'new_table_reserved_bytes':1024,'new_tables':[f'${slo:04X}-${slo+0x1FE:04X}',f'${shi:04X}-${shi+0x1FE:04X}'],'shared_difference_tables':[f'${nlo:04X}-${nlo+0x1FE:04X}',f'${nhi:04X}-${nhi+0x1FE:04X}'],'validation':ev}
  print(p,'PASS',f"{ev['mean_cycles']:.9f}",ev['min_cycles'],ev['max_cycles'])
 out=ROOT/'validation/review/SMUL8_DIRECT_SIGNED_UPGRADE.json';out.write_text(json.dumps(rep,indent=2)+'\n');print('WROTE',out.relative_to(ROOT))
if __name__=='__main__':main()
