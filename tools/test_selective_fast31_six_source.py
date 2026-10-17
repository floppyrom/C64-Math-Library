#!/usr/bin/env python3
"""One 512-byte FAST31 arithmetic island now exports all six 32x32 APIs."""
from __future__ import annotations
import random
import unittest
from pathlib import Path
from mini6502 import CPU,Assembler
import selective_fast31_umul32 as fast31

ROOT=Path(__file__).resolve().parents[1]
SOURCE="routines/multiply/mul32_fast31_shared_public.asm"
OPS=("UMUL32","UMUL32_READY","UMUL32_SHR16",
     "SMUL32","SMUL32_READY","SMUL32_SHR16")
ENTRIES={
    "UMUL32":"FAST_UMUL32_FAST31",
    "UMUL32_READY":"FAST_UMUL32_FAST31",
    "UMUL32_SHR16":"FAST_UMUL32_SHR16_FAST31",
    "SMUL32":"FAST_SMUL32_FAST31",
    "SMUL32_READY":"FAST_SMUL32_FAST31",
    "SMUL32_SHR16":"FAST_SMUL32_SHR16_FAST31",
}
EDGES=(0,1,2,255,256,65535,65536,0x7fffffff,0x80000000,0xffffffff)
MASK=(1<<64)-1

def signed(x):
    return x-(1<<32) if x&0x80000000 else x

class FAST31SixTests(unittest.TestCase):
    def test_six_entries_and_no_extra_code_or_lookup_pages(self):
        rng=random.Random(0x6FA5132)
        pairs=[(a,b) for a in EDGES for b in EDGES]
        pairs.extend((rng.getrandbits(32),rng.getrandbits(32)) for _ in range(196))
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            with self.subTest(code=code):
                memcode,entry,ranges,end=fast31.assemble(
                    code,io,zp,ROOT,source_path=SOURCE,
                    entry_label="FAST_UMUL32_FAST31")
                self.assertEqual(entry,code)
                self.assertEqual(end,fast31.layout(code)[1])
                self.assertEqual(len(memcode),end-code)
                self.assertEqual(len(ranges),6)
                src=fast31.render(fast31.layout(code)[0],io,zp,ROOT,SOURCE)
                _,labels,_=Assembler().assemble(src)
                entrypoints={k:labels[v] for k,v in ENTRIES.items()}
                self.assertEqual(entrypoints["UMUL32"],entrypoints["UMUL32_READY"])
                self.assertEqual(entrypoints["SMUL32"],entrypoints["SMUL32_READY"])
                self.assertEqual(len(set(entrypoints.values())),4)
                self.assertTrue(all(code<=v<code+512 for v in entrypoints.values()))
                print("FAST31 SIX entry offsets",hex(code),
                    {k:hex(v-code) for k,v in entrypoints.items()},flush=True)
                smc={p+1 for k,p in labels.items() if k.startswith("SMC_")}
                self.assertEqual(len(smc),10)
                mem=bytearray(65536)
                for p,b in memcode.items():mem[p]=b
                cpu=CPU(mem);sp=cpu.sp
                for i,(x,y) in enumerate(pairs):
                    for op in OPS:
                        xb=x.to_bytes(4,"little");yb=y.to_bytes(4,"little")
                        mem[io:io+4]=xb;mem[io+4:io+8]=yb
                        mem[io+8:io+16]=b"\xa5"*8
                        cpu.d=0;cpu.c=(i^x^y)&1
                        cpu.call(entrypoints[op],12000)
                        prod=((signed(x)*signed(y))&MASK) if op.startswith("SMUL") else x*y
                        expect=prod>>16 if op.endswith("SHR16") else prod
                        width=6 if op.endswith("SHR16") else 8
                        got=int.from_bytes(mem[io+8:io+8+width],"little")
                        self.assertEqual(got,expect,(op,hex(code),hex(x),hex(y)))
                        self.assertEqual(mem[io:io+4],xb)
                        self.assertEqual(mem[io+4:io+8],yb)
                        self.assertEqual(cpu.c,0)
                        self.assertEqual(cpu.sp,sp)
                self.assertTrue(all(mem[p]==b for p,b in memcode.items() if p not in smc))

if __name__=="__main__":
    unittest.main()
