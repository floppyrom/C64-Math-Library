#!/usr/bin/env python3
"""Issue39 V5 32/32 quotient-preserving remainder frontend A/B screen.

The V5 documented UMOD32_32 alias supplies Q32 and R32, unlike V2-V4's
remainder-only alias. A transposed V2 frontend must therefore materialize Q.
Candidate lives in an existing zero hole and chains N>D to V5's original
shared gate; no shipping resident or source modified by this program.
"""
from __future__ import annotations
from pathlib import Path
import sys,random,json,hashlib
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler,CPU
from validate_unsigned_division import load,wr,rd,expected
from benchmark_unsigned_common_corpus import corpus,band
P='v5_hybrid_lowzp';API=0x5E03;GATE=0x5957;DST=0x5E80
SHA='634e58f536374bc12877e692515f68ab5c5f38954caf5c189a8f67d356289d02'
OUT=ROOT/'validation/review/ISSUE39_V5_UMOD3232_QPRESERVING_FRONTEND_SCREEN.json'
N,D,Q,R=0xC010,0xC014,0xC018,0xC01C
SRC=f"""* = ${DST:04X}
V5_RM3232_NEW:
    lda ${N+3:04X}
    cmp ${D+3:04X}
    bcc V5_RM3232_ZERO
    bne V5_RM3232_FALLBACK
    lda ${N+2:04X}
    cmp ${D+2:04X}
    bcc V5_RM3232_ZERO
    bne V5_RM3232_FALLBACK
    lda ${N+1:04X}
    cmp ${D+1:04X}
    bcc V5_RM3232_ZERO
    bne V5_RM3232_FALLBACK
    lda ${N:04X}
    cmp ${D:04X}
    bcc V5_RM3232_ZERO
    bne V5_RM3232_FALLBACK
    ; N=D: Only here can divisor be zero without N>D. Keep carry flag
    ; and complete quotient/remainder outputs as V5's alias promises.
    lda ${D:04X}
    ora ${D+1:04X}
    ora ${D+2:04X}
    ora ${D+3:04X}
    beq V5_RM3232_FALLBACK
    ldx #0
    lda #1
    sta ${Q:04X}
    stx ${Q+1:04X}
    stx ${Q+2:04X}
    stx ${Q+3:04X}
    stx ${R:04X}
    stx ${R+1:04X}
    stx ${R+2:04X}
    stx ${R+3:04X}
    clc
    rts
V5_RM3232_ZERO:
    ldx #0
    stx ${Q:04X}
    stx ${Q+1:04X}
    stx ${Q+2:04X}
    stx ${Q+3:04X}
    lda ${N:04X}
    sta ${R:04X}
    lda ${N+1:04X}
    sta ${R+1:04X}
    lda ${N+2:04X}
    sta ${R+2:04X}
    lda ${N+3:04X}
    sta ${R+3:04X}
    clc
    rts
V5_RM3232_FALLBACK:
    jmp ${GATE:04X}
"""
def main():
 oldimg=(ROOT/P/'resident'/f'math_{P}_game_math.prg').read_bytes()
 assert hashlib.sha256(oldimg).hexdigest()==SHA,('unexpected V5 source',hashlib.sha256(oldimg).hexdigest())
 cpu,a=load(P);alt,b=load(P)
 assert a==b and a['MATH_UMOD32_32']==API
 code,labels,_=Assembler().assemble(SRC)
 start,end=min(code),max(code)+1
 assert start==DST and end<=0x5F40,(hex(start),hex(end),'outside zero island')
 assert all(alt.mem[z]==0 for z in code),('overlapping initialized region')
 assert bytes(cpu.mem[API:API+3])==bytes.fromhex('4c5759'),('public stub changed')
 alt.mem[API:API+3]=bytes((0x4C,DST&255,DST>>8))
 for pc,value in code.items():alt.mem[pc]=value
 _,common=corpus('MATH_UMOD32_32',32,32,0,1024)
 cases=[(n,d,'official') for n,d,_ in common]
 rnd=random.Random(0x39883232)
 for _ in range(512):
  n=rnd.randrange(1<<32);d=rnd.randrange(1<<32)
  cases.append((n,d,'random'))
  cases.append((d,d,'equality'))
  cases.append((n,0,'divide_zero'))
  if d:
   cases.append((d-1,d,'qzero'))
   cases.append((min(0xffffffff,d+1),d,'qone_or_more'))
 for n in [0,1,2,255,65535,0x80000000,0xffffffff]:
  for d in [0,1,2,255,65535,0x80000000,0xffffffff]:
   cases.append((n,d,'boundary'))
 diff=[];cats=defaultdict(list);failures=[];groups=Counter();initialQ=0xCBA98765;initialR=0x6A558137
 for n,d,k in cases:
  eq,er,ec=expected(n,d,32,32)
  observed=[]
  for c in (cpu,alt):
   wr(c.mem,N,n,4);wr(c.mem,D,d,4);wr(c.mem,Q,initialQ,4);wr(c.mem,R,initialR,4)
   c.mem[0xC030]=0xA5
   cycles=c.call(API,4_000_000)
   observed.append((cycles,(rd(c.mem,Q,4),rd(c.mem,R,4),c.c,rd(c.mem,N,4),rd(c.mem,D,4),c.mem[0xC030])))
  want=(eq,er,ec,n,d,0xA5)
  if observed[0][1]!=want or observed[1][1]!=want:
   if len(failures)<6:failures.append({'n':hex(n),'d':hex(d),'got':observed,'want':want})
  x=observed[1][0]-observed[0][0];diff.append(x);cats[band(n,d,0)].append(x)
  groups['faster' if x<0 else 'tie' if x==0 else 'slower']+=1
 assert not failures,failures
 assert len(diff)==len(cases)
 result={'status':'PASS' if sum(diff)<0 else 'REJECT_NO_MEAN_GAIN',
  'operation':'MATH_UMOD32_32','profile':P,'alias_Q32_R32_written':True,
  'full_resident_sha256':SHA,'ephemeral_source_program':SRC,
  'entry':hex(API),'new_entry':hex(DST),'fallback':hex(GATE),
  'candidate_length_bytes':len(code),'last_byte':hex(end-1),
  'no_shipped_bytes_modified':True,'normal_zp_growth':0,
  'mean_delta_cycles':sum(diff)/len(diff),'mean_saving_cycles':-sum(diff)/len(diff),
  'counts':dict(groups),'tested_cases':len(diff),'total_old_new_calls':2*len(diff),
  'official_case_count':len(common),'errors':0,
  'classes':{key:{'cases':len(v),'mean_delta':sum(v)/len(v),
       'faster':sum(i<0 for i in v),'slower':sum(i>0 for i in v),
       'max_regression':max(v),'best_saving':-min(v)} for key,v in cats.items()},
  'next_gate':'If candidate is useful, source-qualify V5 hybrid builder relocation & native x64sc; never merge unvalidated research.'}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print('ISSUE39 V5 UMOD32 Q PRESERVING',result['status'],'calls',len(cases),
       'mean_delta',result['mean_delta_cycles'],'fast/tie/slow',dict(groups),
       'bytes',len(code),flush=True)
if __name__=='__main__':main()
