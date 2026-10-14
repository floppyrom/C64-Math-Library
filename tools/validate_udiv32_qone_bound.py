#!/usr/bin/env python3
"""Permanent Issue #39 32/32 bounded quotient-one source and comparable-cycle gate."""
from pathlib import Path
import json
import sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from common_corpus_ranking import load_common
from validate_unsigned_division import load,wr,rd,expected
report=load_common(R)
required={
    # PR100 V1 32/16 hot-path fallthrough is invoked by bounded 32/32
    # fallback calls. Recompute on exactly the official same-input corpus;
    # V5 keeps its independent V2 donor and therefore its original means.
    'MATH_UDIV32_32':(335.7610846463906,2729),
    'MATH_UMOD32_32':(399.57360703812316,1705)}
v5_means={'MATH_UDIV32_32':275.01319164529133,
          'MATH_UMOD32_32':299.58299120234600}
cert=json.loads((R/'validation/review/ISSUE39_SEEK16_SCALE_PRODUCTION_2026-10-14.json').read_text())
legacy_means={'MATH_UDIV32_32':335.7508244778307,
              'MATH_UMOD32_32':399.55718475073314}
for name,(expected_mean,cases) in required.items():
    evidence=cert['transitive_v1_division_timing_deltas'][name]
    assert evidence['old_mean_cycles']==legacy_means[name]
    assert evidence['new_mean_cycles']==expected_mean
    assert 0<=evidence['delta_cycles']<1,(name,'unexpected transitive timing shift')
    info=report['routines'][name]
    assert info['cases_per_profile']==cases
    assert abs(info['metrics']['v1_balanced']['mean_cycles']-expected_mean)<1e-10
    assert abs(info['metrics']['v5_hybrid_lowzp']['mean_cycles']-v5_means[name])<1e-10
cases=[
 (0xffffffff,0x80000000), (0xffffffff,0x7fffffff),
 (0xe1234567,0x71000000), (0x90000000,0x60000000),
 (0xffffffff,0x40000000), (0xffffffff,0x00000001),
 (0x80000000,0x40000000), (0x40000000,0x40000000),
 (0x30000000,0x80000000), (0x00000000,0x00000000),
 (0x89abcdef,0x00000000), (0x01020304,0x00001234),
 (0x7fffffff,0x40000000), (0xffffffff,0x70000000),
 (0x02000000,0x01000000), (0xffff0000,0x77777777)]
for p in ('v1_balanced','v5_hybrid_lowzp'):
    cpu,entries=load(p)
    mem=cpu.mem
    # Reference source-build V1/V5 must share the bounded q1 helper in the
    # original code island and the unchanged public 32/32 gate.
    assert bytes(mem[0x59d6:0x59d9])==b'\x4c\x10\x68',p
    assert bytes(mem[0x6810:0x6813])==b'\xad\x17\xc0',p
    for name in required:
        for n,d in cases:
            eq,er,ec=expected(n,d,32,32,0)
            wr(mem,0xc010,n,4);wr(mem,0xc014,d,4)
            cycles=cpu.call(entries[name],4_000_000)
            val=(rd(mem,0xc018,4),rd(mem,0xc01c,4),cpu.c)
            if name=='MATH_UMOD32_32':assert val[1:]==(er,ec),(p,name,hex(n),hex(d),val,er,ec)
            else:assert val==(eq,er,ec),(p,name,hex(n),hex(d),val,eq,er,ec)
            assert rd(mem,0xc010,4)==n and rd(mem,0xc014,4)==d
print('V1/V5 UDIV32_32/UMOD32_32 BOUNDED HIGH-QONE SOURCE: PASS')
