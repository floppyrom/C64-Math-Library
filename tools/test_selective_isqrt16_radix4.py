#!/usr/bin/env python3
"""Tableless 16-bit square root exhaustive proof and resource-speed selector."""
from __future__ import annotations
from math import isqrt
from pathlib import Path
import tempfile
import unittest
import math_builder
import selective_linker as linker
import selective_speed_isqrt16 as speed
from mini6502 import CPU

class ISQRT16LowRAMTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.index=math_builder.operation_index()

    def build(self,name='link:radix4-zerozp',obj='size',ram=1100,code=0x8000,io=0xc000):
        d=tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        kw={} if name is None else {'pins':{'ISQRT16':name}}
        plan=math_builder.create_plan(self.index,['ISQRT16'],objective=obj,
              ram_budget=ram,zp_budget=0,**kw)
        dest=Path(d.name)
        man=linker.build(plan,dest,memory={'code_base':code,'math_io':io,
              'scratch_base':io+32})
        return man,(dest/'math_selective.prg').read_bytes()

    def test_exhaustive_65536_with_tiny_memory(self):
        for code,io in ((0x8000,0xc000),(0x7123,0xc040)):
            with self.subTest(code=code):
                man,prg=self.build(code=code,io=io,ram=175)
                self.assertEqual(man['operations'][0]['variant'],'link:radix4-zerozp')
                self.assertEqual(man['resource_use']['zero_page_bytes'],0)
                self.assertEqual(man['resource_use']['main_ram_total_bytes'],175)
                cpu=CPU(bytearray(65536));cpu.mem[code:code+len(prg)-2]=prg[2:]
                saved=bytes(cpu.mem[code:code+len(prg)-2]);sp=cpu.sp
                entry=int(man['operations'][0]['entry'][1:],16)
                # Full unsigned domain once; second relocation samples page and root edges.
                inputs=range(65536) if code==0x8000 else [0,1,2,3,15,16,17,255,256,257,
                    1023,1024,1025,4095,4096,4097,16383,16384,16385,65534,65535]
                for n in inputs:
                    cpu.mem[io+16:io+18]=n.to_bytes(2,'little')
                    cpu.mem[io+8:io+10]=b'\x55\xaa'
                    cpu.x=(n*19)&255;cpu.y=(n*53)&255
                    before=cpu.x,cpu.y
                    cpu.d=0;cpu.c=n&1
                    cpu.call(entry,20000)
                    if ((cpu.mem[io+8],cpu.mem[io+9],cpu.c)!=(isqrt(n),0,0)
                        or (cpu.x,cpu.y,cpu.sp)!=(*before,sp)
                        or cpu.mem[io+16:io+18]!=n.to_bytes(2,'little')):
                        self.fail(f"ISQRT16 ABI regression at {code:04x}/{n}")
                self.assertEqual(bytes(cpu.mem[code:code+len(prg)-2]),saved)

    def test_speed_selects_correct_budget_and_provenance(self):
        for base,io in ((0x8000,0xc000),(0x7123,0xc040)):
            with self.subTest(base=base):
                man,_=self.build(None,'speed',1100,base,io)
                self.assertEqual(man['operations'][0]['variant'],'link:square-table')
                bench=man['cycle_model_benchmark']
                self.assertEqual(bench['cases'],speed.COUNT)
                self.assertEqual(bench['corpus_sha256'],speed.CORPUS_SHA256)
                self.assertLess(bench['mean_cycles']['link:square-table'],
                                bench['mean_cycles']['link:radix4-zerozp'])
                small,_=self.build(None,'speed',175,base,io)
                self.assertEqual(small['operations'][0]['variant'],'link:radix4-zerozp')
        with self.assertRaises(linker.LinkError):self.build(None,'size',174)

    def test_missing_and_resource_drift_fail_closed(self):
        name='MATH_ISQRT16';old=dict(linker.MODULES[name])
        try:
            del linker.MODULES[name]['link:radix4-zerozp']
            with self.assertRaisesRegex(linker.LinkError,'cycle-model measurement failed'):
                self.build(None,'speed')
        finally:linker.MODULES[name]=dict(old)
        try:
            linker.MODULES[name]['link:radix4-zerozp']=dict(old['link:radix4-zerozp'],scratch=0)
            with self.assertRaisesRegex(linker.LinkError,'cycle-model measurement failed'):
                self.build(None,'speed')
        finally:linker.MODULES[name]=dict(old)

if __name__=='__main__':unittest.main()
