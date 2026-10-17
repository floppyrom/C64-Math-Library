#!/usr/bin/env python3
"""First-pass exact public-ABI qualification for transplanted native FAST31 UMUL32."""
from __future__ import annotations
import random
import unittest
from pathlib import Path
from mini6502 import CPU
import selective_fast31_umul32 as fast

ROOT=Path(__file__).resolve().parents[1]
EDGES=(0,1,2,3,255,256,65535,65536,0x7fffffff,0x80000000,0xfffffffe,0xffffffff)

class Fast31PublicTests(unittest.TestCase):
    def test_canonical_convolution_table_data(self):
        r=fast.tables()
        self.assertEqual(len(r),4)
        self.assertTrue(all(len(p)==511 for p in r))

    def test_two_relocated_public_c64_maps(self):
        rng=random.Random(0x643175)
        pairs=[(a,b) for a in EDGES for b in EDGES]
        pairs += [(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(160)]
        for origin,io,zp in ((0x8000,0xc000,0x50),
                             (0x7123,0xc040,0x70)):
            with self.subTest(origin=origin):
                image,entry,segments,end=fast.assemble(origin,io,zp,ROOT)
                self.assertEqual(set(image),set(range(origin,end)))
                self.assertEqual(entry,origin)
                self.assertLessEqual(end-origin,2816)
                mem=bytearray(65536)
                for addr,value in image.items():mem[addr]=value
                cpu=CPU(mem)
                stack=cpu.sp
                for i,(x,y) in enumerate(pairs):
                    xb=x.to_bytes(4,"little");yb=y.to_bytes(4,"little")
                    mem[io:io+4]=xb
                    mem[io+4:io+8]=yb
                    mem[io+8:io+16]=b"\xa5"*8
                    cpu.d=0
                    cpu.c=i&1
                    ticks=cpu.call(entry,10000)
                    got=int.from_bytes(mem[io+8:io+16],"little")
                    self.assertEqual(got,x*y,(origin,x,y))
                    self.assertEqual(mem[io:io+4],xb)
                    self.assertEqual(mem[io+4:io+8],yb)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,stack)
                    self.assertLess(ticks,3000)

if __name__=="__main__":
    unittest.main()
