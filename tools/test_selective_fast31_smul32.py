#!/usr/bin/env python3
"""Exact full64 signed FAST31 direct-source ABI and relocations."""
from __future__ import annotations
import random
import unittest
from pathlib import Path
from mini6502 import CPU, Assembler
import selective_fast31_umul32 as fast

ROOT=Path(__file__).resolve().parents[1]
SOURCE="routines/multiply/smul32_fast31_public.asm"
ENTRY="FAST_SMUL32_FAST31"
EDGES=(0,1,2,255,256,65535,0x7fffffff,0x80000000,0x80000001,0xfffffffe,0xffffffff)
MASK=(1<<64)-1

def signed(x):
    return x-(1<<32) if x&0x80000000 else x

class SignedFAST31Tests(unittest.TestCase):
    def test_native_source_full_signed_product_two_maps(self):
        rng=random.Random(0xC6439531)
        pairs=[(a,b) for a in EDGES for b in EDGES]
        pairs.extend((rng.getrandbits(32),rng.getrandbits(32)) for _ in range(256))
        for start,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(start=start):
                memcode,entry,segments,end=fast.assemble(
                    start,io,zp,ROOT,source_path=SOURCE,entry_label=ENTRY)
                self.assertEqual(entry,start)
                self.assertEqual(set(memcode),set(range(start,end)))
                self.assertEqual(end-start,fast.layout(start)[1]-start)
                positions,_=fast.layout(start)
                src=fast.render(positions,io,zp,ROOT,source_path=SOURCE)
                _,labels,_=Assembler().assemble(src)
                smc={addr+1 for label,addr in labels.items() if label.startswith("SMC_")}
                self.assertEqual(len(smc),10)
                mem=bytearray(65536)
                for addr,value in memcode.items():mem[addr]=value
                cpu=CPU(mem)
                sp=cpu.sp
                sumcycles=0
                for i,(x,y) in enumerate(pairs):
                    xb=x.to_bytes(4,"little")
                    yb=y.to_bytes(4,"little")
                    mem[io:io+4]=xb
                    mem[io+4:io+8]=yb
                    mem[io+8:io+16]=b"\xa5"*8
                    cpu.c=i&1
                    cpu.d=0
                    sumcycles+=cpu.call(entry,12000)
                    expected=(signed(x)*signed(y))&MASK
                    got=int.from_bytes(mem[io+8:io+16],"little")
                    self.assertEqual(got,expected,(hex(start),hex(x),hex(y)))
                    self.assertEqual(mem[io:io+4],xb)
                    self.assertEqual(mem[io+4:io+8],yb)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,sp)
                self.assertTrue(all(mem[a]==b for a,b in memcode.items() if a not in smc))
                print("SMUL32 FAST31 SOURCE",hex(start),len(pairs),"mean CPU cycles",
                      round(sumcycles/len(pairs),3),flush=True)

if __name__=="__main__":
    unittest.main()
