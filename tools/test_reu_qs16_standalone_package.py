#!/usr/bin/env python3
"""QS16 self-contained REU table install and public arithmetic CPU-model proof."""
import hashlib
import random
import unittest

from mini6502 import CPU
import reu_qs16_standalone_package as q16
from reu_remaining_source_modules import qs16_table


class QS16NativeSourceBuilder(unittest.TestCase):
    def test_16m_reu_build_initializes_all_table_bytes_and_two_batches(self):
        report, prg = q16.build()
        self.assertEqual(len(prg), 2 + q16.LIMIT - q16.BASE)
        self.assertEqual(hashlib.sha256(prg).hexdigest(),report["prg_sha256"])
        self.assertFalse(report["reu_native_qualified"])
        self.assertFalse(report["legacy_reu_image_needed"])
        mem=bytearray(65536)
        mem[q16.BASE:q16.LIMIT]=prg[2:]
        mem[1]=0x35
        seed=bytes((0xb2+i*73)&255 for i in range(16))
        mem[0x4e:0x5e]=seed
        reu=bytearray(16*1024*1024)
        cpu=CPU(mem,reu=reu)
        stack=cpu.sp
        symbols={name:int(value[1:],16)
                 for name,value in report["public_exports"].items()}
        cpu.call(symbols["Q16_REU_INSTALL"], 12000000)
        self.assertEqual(cpu.c,0,"QS16 table generation/readback failed")
        self.assertEqual(mem[q16.READY],1)
        self.assertEqual(mem[q16.ACTIVE],0)
        self.assertEqual(cpu.sp,stack)
        self.assertEqual(bytes(mem[0x4e:0x5e]),seed)
        start=q16.TABLE_BANK*65536
        expect=qs16_table()
        self.assertEqual(reu[start:start+len(expect)],expect)
        self.assertEqual(hashlib.sha256(expect).hexdigest(),
                         report["expected_table_sha256"])
        self.assertEqual(
            reu[start+len(expect):start+len(expect)+4],
            ((131071*131071)//4).to_bytes(4,"little"))
        for batch in range(2):
            cpu.call(symbols["Q16_REU_CALL"])
            self.assertEqual(cpu.c,1)
            cpu.call(symbols["Q16_REU_BEGIN"])
            self.assertEqual(cpu.c,0)
            self.assertEqual(mem[q16.ACTIVE],1)
            cpu.call(symbols["Q16_REU_BEGIN"])
            self.assertEqual(cpu.c,1)
            cases=[(0,0),(1,1),(0xffff,0xffff),(0x1234,0x9876)]
            rng=random.Random(20261021+batch)
            cases.extend((rng.randrange(65536),rng.randrange(65536))
                         for _ in range(50))
            for a,b in cases:
                mem[q16.IO:q16.IO+2]=a.to_bytes(2,"little")
                mem[q16.IO+4:q16.IO+6]=b.to_bytes(2,"little")
                cpu.d=0
                cpu.call(symbols["Q16_REU_CALL"], 8000)
                got=int.from_bytes(mem[q16.IO+8:q16.IO+12],"little")
                self.assertEqual(got,a*b,(a,b))
                self.assertEqual(cpu.c,0)
                self.assertEqual(cpu.sp,stack)
            cpu.call(symbols["Q16_REU_END"])
            self.assertEqual(cpu.c,0)
            self.assertEqual(mem[q16.ACTIVE],0)
            self.assertEqual(bytes(mem[0x4e:0x5e]),seed)
            cpu.call(symbols["Q16_REU_END"])
            self.assertEqual(cpu.c,1)

    def test_missing_reu_fails_without_table_generation(self):
        info,prg=q16.build()
        mem=bytearray(65536)
        mem[q16.BASE:q16.LIMIT]=prg[2:]
        mem[1]=0x35
        cpu=CPU(mem,reu=None)
        install=int(info["public_exports"]["Q16_REU_INSTALL"][1:],16)
        cpu.call(install,20000)
        self.assertEqual(cpu.c,1)
        self.assertEqual(mem[q16.READY],0)

    def test_invalid_physical_ownership_fail_closed(self):
        for kw in (
            {"capacity":512},
            {"bank":16},
            {"bank":201},
            {"bank":249},
            {"reserved_ram":((0x7000,0x73ff),)},
            {"reserved_ram":((0xc020,0xc023),)},
            {"reserved_zp":((0x4e,0x5d),)},
            {"reserved_reu_banks":(200,)},
            {"reserved_reu_banks":(72,)},
        ):
            with self.subTest(config=kw):
                with self.assertRaises(q16.QS16PackageError):
                    q16.check_claims(**kw)


if __name__=="__main__":
    unittest.main()
