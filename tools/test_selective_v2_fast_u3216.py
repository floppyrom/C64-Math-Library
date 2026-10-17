#!/usr/bin/env python3
"""Canonical V2 size-fast 32/16 native donor, public ABI, CPU cycle proof."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU,load_sparse
import selective_v2_fast_u3216 as fast
import selective_speed_u3216 as speed
from test_selective_u3216_unrolled import assemble as assemble_zerozp, SOURCE as ZEROZP

class V2Sizefast3216Tests(unittest.TestCase):
    def test_public_qr_c_native_donor_adapter_two_relocations(self):
        corpus=speed.corpus()
        self.assertEqual(len(corpus),speed.COUNT)
        for code,io,zp,scratch in ((0x8000,0xc000,0x50,0xc020),
                                   (0x7123,0xc040,0x70,0xc080)):
            with self.subTest(code=code):
                image,labels,slots=fast.assemble(code,io,zp)
                entry=labels[fast.PUB_ENTRY]
                self.assertEqual(entry,labels["FAST_UMOD32_16_V2"])
                self.assertEqual(set(slots),{"FAST16","TAIL16","PUBLIC"})
                self.assertLess(sum(size for _,size in slots.values()),2300)
                mem=load_sparse(image)
                cpu=CPU(mem)
                baseline,base_entry=assemble_zerozp(ZEROZP,code,io,scratch)
                reference=CPU(load_sparse(baseline))
                cycles_fast=cycles_ref=0
                sp=cpu.sp;ref_sp=reference.sp
                for i,(n,d) in enumerate(corpus):
                    for repetition in range(2):
                        nb=n.to_bytes(4,"little");db=d.to_bytes(2,"little")
                        for machine in (cpu,reference):
                            machine.mem[io+16:io+20]=nb
                            machine.mem[io+20:io+22]=db
                            machine.mem[io+24:io+28]=b"\x55"*4
                            machine.mem[io+28:io+32]=b"\x66\x66\x69\xab"
                            machine.d=0
                            machine.c=(i^repetition^n^d)&1
                        cycles_fast+=cpu.call(entry,25000)
                        cycles_ref+=reference.call(base_entry,25000)
                        expected=(n//d if d else 0,n%d if d else 0,int(d==0))
                        for machine,stack in ((cpu,sp),(reference,ref_sp)):
                            got=(int.from_bytes(machine.mem[io+24:io+28],"little"),
                                 int.from_bytes(machine.mem[io+28:io+30],"little"),
                                 machine.c)
                            self.assertEqual(got,expected,(hex(code),hex(n),hex(d)))
                            self.assertEqual(machine.mem[io+16:io+20],nb)
                            self.assertEqual(machine.mem[io+20:io+22],db)
                            self.assertEqual(machine.mem[io+30:io+32],b"\x69\xab")
                            self.assertEqual(machine.sp,stack)
                self.assertTrue(all(cpu.mem[a]==b for a,b in image.items()))
                mean_fast=cycles_fast/(2*len(corpus))
                mean_ref=cycles_ref/(2*len(corpus))
                self.assertLess(mean_fast,mean_ref)
                print("V2 SIZEFAST PUBLIC U3216",hex(code),
                      "slots",slots,
                      "mean_fast",mean_fast,"mean_unrolled",mean_ref,
                      "ratio",mean_ref/mean_fast,flush=True)

if __name__=="__main__":
    unittest.main()
