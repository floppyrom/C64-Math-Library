#!/usr/bin/env python3
"""Source-assembled URECIP16_Q16 CPU-model ABI/resource/relocation regression."""
from __future__ import annotations
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mini6502 import CPU
import math_builder
import selective_linker as linker

EDGE = (0, 1, 2, 3, 4, 5, 7, 15, 16, 31, 32, 127, 128, 255,
        256, 257, 511, 512, 1023, 1024, 4095, 4096, 8192,
        16384, 21845, 21846, 32767, 32768, 32769, 65534, 65535)

def corpus():
    rng = random.Random(0xC6416ECA)
    return list(EDGE) + list(range(0, 300)) + list(range(65000, 65536)) + [
        rng.randrange(65536) for _ in range(1300)
    ]

class ReciprocalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = math_builder.operation_index()

    def plan(self, ops=("URECIP16_Q16",), ram=132):
        return math_builder.create_plan(self.index, list(ops), objective="size",
                                        zp_budget=0, ram_budget=ram)

    def test_public_abi_and_two_memory_maps(self):
        for code, io, scratch in ((0x8000, 0xc000, 0xc020),
                                  (0x7123, 0xc040, 0xc080),
                                  (0x830f, 0xc100, 0xc140)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as td:
                man = linker.build(self.plan(), Path(td), memory={
                    "code_base": code, "math_io": io, "scratch_base": scratch})
                res = man["resource_use"]
                self.assertEqual(res["image_span_bytes"], 99)
                self.assertEqual(res["main_ram_total_bytes"], 132)
                self.assertEqual(res["private_ram_scratch_bytes"], 1)
                self.assertEqual(res["zero_page_bytes"], 0)
                self.assertEqual(man["operations"][0]["variant"], "link:compact-zerozp")
                image = (Path(td) / "math_selective.prg").read_bytes()
                self.assertEqual(image[:2], code.to_bytes(2, "little"))
                self.assertEqual(len(image), 101)
                mem = bytearray(65536)
                mem[code:code+99] = image[2:]
                original = bytes(mem[code:code+99])
                cpu = CPU(mem)
                entry = int(man["operations"][0]["entry"][1:], 16)
                stack = cpu.sp
                for d in corpus():
                    divisor = d.to_bytes(2, "little") + bytes((0x6b, 0x7c))
                    mem[io+20:io+24] = divisor
                    mem[io+16:io+20] = bytes((0x55,0xaa,0x33,0xcc))
                    mem[io+24:io+28] = bytes((0xde,0xad,0xbe,0xef))
                    mem[io+28:io+32] = bytes((0x12,0x34,0x56,0x78))
                    cpu.d = 0
                    cpu.c = (d ^ code) & 1
                    cpu.call(entry, 50000)
                    got = int.from_bytes(mem[io+24:io+27], "little")
                    self.assertEqual((got, cpu.c),
                                     (65536//d if d else 0, int(d == 0)),
                                     (code, d))
                    self.assertEqual(mem[io+27], 0xef)
                    self.assertEqual(bytes(mem[io+28:io+32]), bytes((0x12,0x34,0x56,0x78)))
                    self.assertEqual(bytes(mem[io+16:io+20]), bytes((0x55,0xaa,0x33,0xcc)))
                    self.assertEqual(bytes(mem[io+20:io+24]), divisor)
                    self.assertEqual(cpu.sp, stack)
                self.assertEqual(bytes(mem[code:code+99]), original)

    def test_shared_scratch_across_arithmetic_and_budget(self):
        with tempfile.TemporaryDirectory() as td:
            combined = self.plan(("URECIP16_Q16", "UDIV16_SHL8", "UMUL16"), ram=380)
            man = linker.build(combined, Path(td))
            self.assertEqual(man["resource_use"]["zero_page_bytes"], 0)
            self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"], 6)
            self.assertEqual(man["resource_use"]["main_ram_total_bytes"], 374)
            entries = {op["api"]: int(op["entry"][1:],16) for op in man["operations"]}
            image = (Path(td)/"math_selective.prg").read_bytes()
            mem = bytearray(65536)
            mem[0x8000:0x8000+len(image)-2] = image[2:]
            cpu = CPU(mem)
            rng = random.Random(0xC6416E)
            for _ in range(360):
                d = rng.randrange(65536)
                n = rng.randrange(65536)
                mem[0xc014:0xc016] = d.to_bytes(2, "little")
                mem[0xc010:0xc012] = n.to_bytes(2, "little")
                cpu.d = 0
                cpu.call(entries["MATH_URECIP16_Q16"], 50000)
                self.assertEqual(int.from_bytes(mem[0xc018:0xc01b], "little"),
                                 65536//d if d else 0)
                cpu.call(entries["MATH_UDIV16_SHL8"], 50000)
                self.assertEqual(int.from_bytes(mem[0xc018:0xc01b], "little"),
                                 (n<<8)//d if d else 0)
                x,y = rng.randrange(65536), rng.randrange(65536)
                mem[0xc000:0xc002] = x.to_bytes(2, "little")
                mem[0xc004:0xc006] = y.to_bytes(2, "little")
                cpu.call(entries["MATH_UMUL16"], 50000)
                self.assertEqual(int.from_bytes(mem[0xc008:0xc00c], "little"), x*y)
            with self.assertRaises(linker.LinkError):
                linker.build(self.plan(ram=131), Path(td)/"no_room")
            self.assertFalse((Path(td)/"no_room").exists())

if __name__ == "__main__":
    unittest.main()
