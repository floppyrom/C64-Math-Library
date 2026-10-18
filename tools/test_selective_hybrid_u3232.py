#!/usr/bin/env python3
"""Direct-source ordinary public Q32/R32/C hybrid validation at two relocations."""
from __future__ import annotations

from pathlib import Path
import random
import unittest

from mini6502 import CPU,load_sparse
import selective_hybrid_u3232 as hybrid
import selective_linker
import selective_speed_u3232 as speed

ROOT=Path(__file__).resolve().parents[1]
MASK=(1<<32)-1

def pairs():
    rng=random.Random(0x32321618)
    result=speed.corpus()
    result.extend((rng.getrandbits(32),rng.randrange(0,1<<16))
                  for _ in range(160))
    result.extend((rng.getrandbits(32),rng.randrange(1<<16,1<<32))
                  for _ in range(160))
    result.extend((n,d) for n in
        (0,1,65535,65536,0x7fffffff,0x80000000,0xffffffff)
                  for d in (0,1,2,255,256,65535,65536,0x80000000,0xffffffff))
    return result

class HybridU3232Tests(unittest.TestCase):
    def test_source_hashes_and_packed_layout(self):
        hashes=hybrid.source_sha256()
        self.assertEqual(set(hashes),{hybrid.FAST_SOURCE,hybrid.WIDE_SOURCE})
        self.assertTrue(all(len(s)==64 for s in hashes.values()))
        self.assertEqual(hybrid.ZP_BYTES,12)
        self.assertEqual(hybrid.IMAGE_BYTES,3200)
        for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
            image,labels,ranges,end=hybrid.assemble(code,io,zp)
            self.assertEqual(set(image),set(range(code,end)))
            self.assertEqual(end-code,3200)
            self.assertEqual(labels[hybrid.API_DIV],labels[hybrid.API_MOD])
            self.assertEqual(labels[hybrid.API_DIV],code+hybrid.DISPATCH_OFFSET)
            self.assertNotEqual(labels["V2_LOW_ENTRY"],labels["WIDE_ENTRY"])
            self.assertEqual(len(ranges),1)
            with self.assertRaises(ValueError):
                hybrid.assemble(code,io,0)

    def test_unrestricted_full32_public_equivalence_and_divisor_gain(self):
        corpus=pairs()
        self.assertGreaterEqual(len(corpus),700)
        for code,io,zp,scratch in ((0x8000,0xc000,0x50,0xc020),
                                   (0x7123,0xc040,0x70,0xc080)):
            with self.subTest(code=code):
                image,labels,_,_=hybrid.assemble(code,io,zp)
                base=selective_linker.MODULES["MATH_UDIV32_32"]["link:zptail"]
                old,baseline=speed.assemble_source(
                    "MATH_UDIV32_32","link:zptail",
                    base,code,io,scratch,zp,ROOT)
                cpu=CPU(load_sparse(image))
                reference=CPU(load_sparse(old))
                sp=cpu.sp;ref_sp=reference.sp
                delta={"low":[],"wide":[]}
                for i,(n,d) in enumerate(corpus):
                    nb=n.to_bytes(4,"little")
                    db=d.to_bytes(4,"little")
                    expected=(n//d if d else 0,n%d if d else 0,int(d==0))
                    for mach in (cpu,reference):
                        mach.mem[io+16:io+20]=nb
                        mach.mem[io+20:io+24]=db
                        mach.mem[io+24:io+28]=b"\x55"*4
                        mach.mem[io+28:io+32]=b"\x66"*4
                        mach.c=(n^d^i)&1;mach.d=0
                    candidate_cycles=cpu.call(labels[hybrid.API_DIV],150000)
                    reference_cycles=reference.call(baseline,150000)
                    for machine,original_sp in ((cpu,sp),(reference,ref_sp)):
                        got=(int.from_bytes(machine.mem[io+24:io+28],"little"),
                             int.from_bytes(machine.mem[io+28:io+32],"little"),
                             machine.c)
                        self.assertEqual(got,expected,
                                         (hex(code),hex(n),hex(d),got,expected))
                        self.assertEqual(machine.mem[io+16:io+20],nb)
                        self.assertEqual(machine.mem[io+20:io+24],db)
                        self.assertEqual(machine.sp,original_sp)
                    delta["low" if d<65536 else "wide"].append(
                        candidate_cycles-reference_cycles)
                self.assertTrue(all(cpu.mem[addr]==byte for addr,byte in image.items()))
                self.assertTrue(all(reference.mem[addr]==byte for addr,byte in old.items()))
                self.assertGreater(len(delta["low"]),200)
                self.assertGreater(len(delta["wide"]),250)
                low_mean=sum(delta["low"])/len(delta["low"])
                high_mean=sum(delta["wide"])/len(delta["wide"])
                overall=sum(sum(x) for x in delta.values())/len(corpus)
                self.assertLess(low_mean,0)
                self.assertLess(overall,0)
                print("HYBRID FULL32",hex(code),"cases",len(corpus),
                      "low_mean_delta",round(low_mean,3),
                      "wide_mean_delta",round(high_mean,3),
                      "full_mean_delta",round(overall,3),
                      "code_bytes",len(image),"zp",hybrid.ZP_BYTES,flush=True)

if __name__=="__main__":
    unittest.main()
