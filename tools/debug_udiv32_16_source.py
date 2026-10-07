#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import validate_source_build as V

for kind in ('reference','alternate'):
  for p in ('v2_pareto_fast','v3_reu_512k','v4_reu_16m'):
    c,P,I,M,_=V.load(p,ROOT/'build_u3216'/kind)
    N=I+0x10;D=I+0x14;Q=I+0x18;R=I+0x1c
    for ent in ('MATH_UDIV32_16','MATH_UMOD32_16'):
      for a,d in V.pairs(32,0xE000+32,8)[:24]:
        d &= V.MASK(16)
        V.wr(c,N,a,4);V.wr(c,D,d,2)
        ns=V.snap(c,N,4);ds=V.snap(c,D,2)
        cy=c.call(P[ent],2_000_000)
        q=V.rd(c,Q,4);r=V.rd(c,R,2)
        ok=(c.c==1 and q==0 and r==0) if d==0 else (c.c==0 and (q,r)==divmod(a,d))
        if not ok or V.snap(c,N,4)!=ns or V.snap(c,D,2)!=ds:
          print('FAIL',kind,p,ent,hex(a),hex(d),'got',hex(q),hex(r),c.c,'exp',divmod(a,d) if d else (0,0),'cycles',cy)
          print('entry',hex(P[ent]),'bytes',bytes(c.mem[P[ent]:P[ent]+8]).hex())
          raise SystemExit(1)
    print('PASS',kind,p)
print('DEBUG UDIV32/16 ALIASES PASS')
