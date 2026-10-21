#!/usr/bin/env python3
"""Source-built Turbo32 actual 135-byte DMA SWAP and guard CPU-model proof."""
import hashlib
import random
import unittest

from mini6502 import CPU
import reu_turbo32_standalone_package as turbo


class Turbo32Standalone(unittest.TestCase):
    def test_source_packaged_reu_swaps_zp_and_multiply_in_reused_batches(self):
        for capacity, bank in ((512, 4), (16384, 200)):
            with self.subTest(capacity=capacity):
                manifest, prg = turbo.build(capacity, bank)
                self.assertEqual(len(prg), 2 + turbo.LIMIT - turbo.BASE)
                self.assertEqual(hashlib.sha256(prg).hexdigest(),
                                 manifest["prg_sha256"])
                self.assertFalse(manifest["reu_native_qualified"])
                mem = bytearray(65536)
                mem[turbo.BASE:turbo.LIMIT] = prg[2:]
                mem[1] = 0x35
                seed = bytes((i * 73 + 19) & 255 for i in range(turbo.N))
                mem[turbo.ZP:turbo.ZP+turbo.N] = seed
                state = turbo.STATE
                reu = bytearray(capacity * 1024)
                cpu = CPU(mem, reu=reu)
                stack = cpu.sp
                entries = {key:int(address[1:],16)
                           for key,address in manifest["public_exports"].items()}
                cpu.call(entries["T32_REU_INSTALL"], 100000)
                self.assertEqual(cpu.c, 0, "REU install failed")
                self.assertEqual(mem[state+1], 1)
                self.assertEqual(cpu.sp, stack)
                for batch in range(2):
                    cpu.i = batch
                    cpu.call(entries["T32_REU_CALL"])
                    self.assertEqual(cpu.c, 1, "CALL before BEGIN accepted")
                    cpu.call(entries["T32_REU_BEGIN"], 100000)
                    self.assertEqual(cpu.c, 0)
                    self.assertEqual(mem[state], 1)
                    self.assertEqual(cpu.sp, stack)
                    self.assertNotEqual(mem[turbo.ZP:turbo.ZP+turbo.N], seed)
                    cpu.call(entries["T32_REU_BEGIN"])
                    self.assertEqual(cpu.c, 1, "nested BEGIN accepted")
                    rng = random.Random(20261021 + batch)
                    cases = [(0,0), (1,1), (0xffffffff,0xffffffff),
                             (0x12345678,0x98765432)]
                    cases += [(rng.getrandbits(32),rng.getrandbits(32))
                              for _ in range(50)]
                    for a,b in cases:
                        mem[turbo.IO:turbo.IO+4] = a.to_bytes(4,"little")
                        mem[turbo.IO+4:turbo.IO+8] = b.to_bytes(4,"little")
                        cpu.d = 0
                        cpu.call(entries["T32_REU_CALL"], 20000)
                        product = int.from_bytes(mem[turbo.IO+8:turbo.IO+16],"little")
                        self.assertEqual(product,a*b,(a,b))
                        self.assertEqual(cpu.c,0)
                        self.assertEqual(cpu.sp,stack)
                    cpu.call(entries["T32_REU_END"], 100000)
                    self.assertEqual(cpu.c,0)
                    self.assertEqual(cpu.sp,stack)
                    self.assertEqual(cpu.i,batch)
                    self.assertEqual(bytes(mem[turbo.ZP:turbo.ZP+turbo.N]),seed)
                    self.assertEqual(mem[state],0)
                    cpu.call(entries["T32_REU_END"])
                    self.assertEqual(cpu.c,1, "unbalanced END accepted")

    def test_reject_invalid_claims_before_assembling(self):
        for args in (
            {"capacity":512,"bank":8},
            {"capacity":256,"bank":4},
            {"capacity":512,"bank":4,"reserved_zp":((0x20,0x30),)},
            {"capacity":512,"bank":4,"reserved_ram":((0x3500,0x3600),)},
            {"capacity":512,"bank":4,"reserved_ram":((0xc000,0xc010),)},
            {"capacity":512,"bank":4,"reserved_reu_banks":(4,)},
            {"capacity":16384,"bank":200,"reserved_reu_banks":(72,)},
        ):
            with self.subTest(args=args):
                with self.assertRaises(turbo.Turbo32Error):
                    turbo.check_claims(**args)


if __name__ == "__main__":
    unittest.main()
