#!/usr/bin/env python3
"""Exercise actual relocated historical V2 biased quarter-square UMUL24 core."""
from __future__ import annotations
import hashlib
import random
import unittest
from mini6502 import CPU
import selective_v2_fast_umul24 as emitter

EDGE=(0,1,2,3,7,127,128,255,256,257,65535,65536,
      0x7fffff,0x800000,0x800001,0xfffffe,0xffffff)
MASK48=(1<<48)-1


def corpus():
    pairs=[(x,y) for x in EDGE for y in EDGE]
    rng=random.Random(0x5A24682)
    pairs.extend((rng.getrandbits(24),rng.getrandbits(24))
                 for _ in range(512-len(pairs)))
    assert len(pairs)==512
    return pairs


class HistoricalFastUMUL24(unittest.TestCase):
    def test_exact_biased_table_planes(self):
        tables=emitter.planes()
        self.assertEqual(tuple(map(len,tables)),(511,511,511,511))
        self.assertEqual(emitter.BIAS,0xca)
        for n in range(511):
            q=(n*n)//4+emitter.BIAS*(n&1)
            self.assertEqual((tables[0][n],tables[1][n]),
                             (q&255,(q>>8)&255))
            self.assertNotEqual(q&255,255)
        self.assertEqual(len(emitter.provenance()),64)

    def test_canonical_fast_v2_public_api_at_two_placements(self):
        for code,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x70)):
            with self.subTest(origin=code):
                image,labels,ranges,end=emitter.assemble(code,io,zp)
                self.assertEqual(len(image),end-code)
                self.assertEqual(labels[emitter.PUBLIC],code)
                self.assertEqual(len([s for s in ranges
                    if s["name"] in emitter.TABLES]),4)
                memory=bytearray(65536)
                for address,value in image.items():
                    memory[address]=value
                cpu=CPU(memory);sp=cpu.sp
                samples=[]
                for i,(x,y) in enumerate(corpus()):
                    xb=x.to_bytes(3,"little");yb=y.to_bytes(3,"little")
                    memory[io:io+4]=xb+bytes([0x6a])
                    memory[io+4:io+8]=yb+bytes([0xa5])
                    memory[io+8:io+16]=bytes([0xcc]*6+[0x49,0x59])
                    cpu.a=(x^i)&255;cpu.x=(y>>8)&255
                    cpu.y=(i*19)&255
                    cpu.c=i&1;cpu.d=0
                    cycles=cpu.call(labels[emitter.PUBLIC],100000)
                    got=int.from_bytes(memory[io+8:io+14],"little")
                    self.assertEqual(got,(x*y)&MASK48,(code,i,hex(x),hex(y)))
                    self.assertEqual(memory[io+14:io+16],bytes((0x49,0x59)))
                    self.assertEqual(memory[io:io+4],xb+bytes([0x6a]))
                    self.assertEqual(memory[io+4:io+8],yb+bytes([0xa5]))
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,sp)
                    samples.append(cycles)
                print("RELOCATED V2 UMUL24",hex(code),
                      "calls",len(samples),
                      "mean",round(sum(samples)/len(samples),3),
                      "max",max(samples),
                      "code_slot",emitter.CODE_SLOT,
                      "ZP",emitter.ZP_BYTES,flush=True)


if __name__=="__main__":
    unittest.main()
