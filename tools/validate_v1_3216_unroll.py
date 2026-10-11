#!/usr/bin/env python3
"""Issue39: paired V1 public UDIV32/16 and UMOD32/16 two-loop unroll certificate."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from benchmark_unsigned_common_corpus import SPECS,corpus
from benchmark_unsigned_3216_workloads import WORKLOADS,pairs
from validate_unsigned_division import wr,rd,expected,api
OPNAMES=('MATH_UDIV32_16','MATH_UMOD32_16')
PRG=ROOT/'v1_balanced/resident/math_v1_balanced_game_math.prg'
b=PRG.read_bytes();lo=b[0]|b[1]<<8
assert b[2+0x446a-lo:2+0x446d-lo] == bytes.fromhex('4c 6d 1b')
assert b[2+0x4570-lo:2+0x4573-lo] == bytes.fromhex('4c 00 19')
assert (0x1cf7-0x1900+1)==1016
new=bytearray(65536);new[lo:lo+len(b)-2]=b[2:]
old=new.copy();old[0x446a:0x446d]=bytes.fromhex('ca d0 e3');old[0x4570:0x4573]=bytes.fromhex('ca d0 d1');old[0x1900:0x1cf8]=bytes(1016)
cpus=(CPU(old),CPU(new))
for cpu in cpus:cpu.d=0;cpu.call(0x3280,2_000_000)
assert cpus[1].mem[0x1900:0x1cf8]==new[0x1900:0x1cf8], 'MATH_INIT overwrote unroll'
A=api('v1_balanced')
report={'status':'PASS','candidate_sha256':hashlib.sha256(b).hexdigest(),
        'method':'identical source-backed 6502 public cycles, reconstruct parent in memory',
        'island':'$1900-$1CF7','new_code_bytes':1016,'normal_zp_growth':0,
        'routines':{},'paired_inputs':0,'paired_calls':0,'mismatches':0,'regressions':0}
for name in OPNAMES:
 spec=next(s for s in SPECS if s[0]==name)
 cases=[('common',[(n,d) for n,d,_ in corpus(name,spec[1],spec[2],spec[5],spec[7])[1]])]
 cases += [(work,pairs(work)) for work in WORKLOADS]
 report['routines'][name]={}
 for label,inputs in cases:
  cycles=[[],[]];equal=faster=slower=0
  for n,d in inputs:
   got=[]
   for i,cpu in enumerate(cpus):
    wr(cpu.mem,0xC010,n,4);wr(cpu.mem,0xC014,d,2)
    cyc=cpu.call(A[name],4_000_000);cycles[i].append(cyc)
    got.append((rd(cpu.mem,0xC018,4),rd(cpu.mem,0xC01C,2),cpu.c,rd(cpu.mem,0xC010,4),rd(cpu.mem,0xC014,2)))
   eq,er,ec=expected(n,d,32,16)
   assert got[0]==got[1],(name,label,hex(n),hex(d),got)
   assert got[1][1:]==(er,ec,n,d) and (name=='MATH_UMOD32_16' or got[1][0]==eq)
   delta=cycles[1][-1]-cycles[0][-1]
   faster+=delta<0;equal+=delta==0;slower+=delta>0
   assert delta<=0,(name,label,hex(n),hex(d),delta)
  ncase=len(inputs)
  data={'cases':ncase,'mean_parent_cycles':sum(cycles[0])/ncase,
        'mean_candidate_cycles':sum(cycles[1])/ncase,'faster':faster,'equal':equal,'slower':slower,
        'max_speedup_cycles':max(x-y for x,y in zip(*cycles))}
  report['routines'][name][label]=data
  report['paired_inputs']+=ncase;report['paired_calls']+=2*ncase
  print(name,label,f"{data['mean_parent_cycles']:.6f}->{data['mean_candidate_cycles']:.6f}",
        'faster',faster,'unchanged',equal,'slower',slower,flush=True)
assert report['routines']['MATH_UDIV32_16']['common']['cases']==2729
assert report['routines']['MATH_UMOD32_16']['common']['cases']==1705
assert abs(report['routines']['MATH_UDIV32_16']['common']['mean_candidate_cycles']-825.8739465005497)<0.00001
assert abs(report['routines']['MATH_UMOD32_16']['common']['mean_candidate_cycles']-843.6299120234604)<0.00001
out=ROOT/'validation/review/V1_UDIV32_16_DUAL_UNROLL.json';out.write_text(json.dumps(report,indent=2)+'\n')
print('V1 32/16 TWO-LOOP UNROLL PASS',report['paired_inputs'],'paired inputs',report['paired_calls'],'machine calls')
