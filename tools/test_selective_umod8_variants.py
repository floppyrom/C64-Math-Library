#!/usr/bin/env python3
"""Exhaustive V2/V5 8-bit unsigned-modulo historical link qualification.

Checks exact original instruction opcode stream, relocated writable operands,
all 256x256 input/divisor pairs at two independent code/zero-page origins,
public Q preservation, signed-mode neutrality (unsigned inputs), and C error.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
from mini6502 import CPU

VARIANTS={
 "link:v2-unrolled-fallback": {
  "size":229, "mirror":"v2_pareto_fast", "parts":("5323","3203","5200"),
  "patch":(218,222), "entry":"FAST_UMOD8_V2",
 },
 "link:v5-unrolled-hybrid": {
  "size":205, "mirror":"v5_hybrid_lowzp", "parts":("1E00","3203","B000"),
  "patch":(194,198), "entry":"FAST_UMOD8_V5",
 },
}


def mirror_opcode_stream(profile, sections):
    """Mirror is opcode/length oracle, independent of reordered relocation."""
    src=(ROOT/profile/"standalone"/"mod_u8_u8_u8.asm").read_text()
    result=[]
    for section in sections:
        if section=="3203":
            # Ignore original 3-byte public entry JMP at $3200.
            fragment=src.split("; ---- executable island $3200 ----",1)[1].split("; ---- executable island",1)[0]
            fragment=fragment[fragment.index("L3203:"):]
        else:
            fragment=src.split("; ---- executable island $"+section+" ----",1)[1].split("; ---- executable island",1)[0]
        for line in fragment.splitlines():
            m=re.search(r"; @([A-Fa-f0-9]{4}) ([A-Fa-f0-9 ]+)$",line)
            if m:
                data=bytes.fromhex(m.group(2))
                result.append((data[0],len(data)))
    return result


class HistoricalUMOD8FastVariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()

    def make(self,folder,variant,origin=0x8000,io=0xc000,zp=0x50):
        plan=math_builder.create_plan(
            self.index,["UMOD8"],zp_budget=2,
            ram_budget=VARIANTS[variant]["size"]+32,
            pins={"UMOD8":variant})
        return selective_linker.build(
            plan,Path(folder),
            memory={"code_base":origin,"math_io":io,"zp_base":zp})

    def test_public_metadata_and_distinct_historical_provenance(self):
        variants={x["id"]:x for x in selective_linker.available_variants()["MATH_UMOD8"]}
        self.assertEqual(set(variants),
                         {"link:v1-fast-fallback",*VARIANTS})
        for name,info in VARIANTS.items():
            entry=variants[name]
            self.assertTrue(entry["requires_writable_code"])
            self.assertEqual(entry["resources_reported"]["code_and_table_bytes"],info["size"])
            self.assertEqual(entry["zp_bytes_reported"],2)
            self.assertEqual(entry["validation_path"],"tools/test_selective_umod8.py")
            self.assertIn("Original V",entry["historical_provenance"])

    def test_opcode_parity_all_unsigned_pairs_and_relocations(self):
        for variant, info in VARIANTS.items():
            for origin,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
                with self.subTest(variant=variant,origin=origin),tempfile.TemporaryDirectory() as folder:
                    result=self.make(folder,variant,origin,io,zp)
                    resource=result["resource_use"]
                    self.assertEqual(resource["zero_page_bytes"],2)
                    self.assertEqual(resource["main_ram_total_bytes"],info["size"]+32)
                    self.assertEqual(result["operations"][0]["entry"],"$%04X"%origin)
                    prg=(Path(folder)/"math_selective.prg").read_bytes()
                    self.assertEqual(hashlib.sha256(prg).hexdigest(),result["prg_sha256"])
                    cpu=CPU(bytearray(65536))
                    cpu.mem[origin:origin+len(prg)-2]=prg[2:]
                    original=bytes(cpu.mem[origin:origin+info["size"]])
                    program=mirror_opcode_stream(info["mirror"],info["parts"])
                    self.assertEqual(sum(n for _,n in program),info["size"])
                    offset=0
                    for opcode,n in program:
                        self.assertEqual(cpu.mem[origin+offset],opcode,
                                         (variant,origin,offset))
                        offset+=n
                    stack=cpu.sp
                    for divisor in range(256):
                        for numerator in range(256):
                            cpu.mem[io+16:io+20]=bytes((numerator,0x12,0x34,0x56))
                            cpu.mem[io+20:io+24]=bytes((divisor,0x65,0x43,0x21))
                            cpu.mem[io+24:io+28]=b"\x8a"*4
                            cpu.mem[io+28:io+32]=b"\x9b"*4
                            cpu.c=(numerator^divisor)&1
                            cpu.d=0
                            cpu.call(origin,30000)
                            self.assertEqual((cpu.mem[io+28],cpu.c),
                                             (numerator%divisor if divisor else 0,int(divisor==0)),
                                             (variant,origin,numerator,divisor))
                            self.assertEqual(cpu.mem[io+24:io+28],b"\x8a"*4)
                            self.assertEqual(cpu.mem[io+29:io+32],b"\x9b"*3)
                            self.assertEqual(cpu.mem[io+16:io+20],
                                             bytes((numerator,0x12,0x34,0x56)))
                            self.assertEqual(cpu.mem[io+20:io+24],
                                             bytes((divisor,0x65,0x43,0x21)))
                            self.assertEqual(cpu.sp,stack)
                        changed={i for i in range(info["size"])
                                 if cpu.mem[origin+i]!=original[i]}
                        self.assertLessEqual(changed,set(info["patch"]),
                                             ("modified code beyond two writable operands",variant,origin,changed))
                    self.assertEqual(
                        bytes(cpu.mem[origin:origin+info["patch"][0]]),
                        original[:info["patch"][0]])

    def test_resource_budgets_and_independent_pins(self):
        for variant,info in VARIANTS.items():
            with self.subTest(variant=variant),tempfile.TemporaryDirectory() as folder:
                plan=math_builder.create_plan(
                    self.index,["UMOD8"],zp_budget=2,
                    ram_budget=info["size"]+31,pins={"UMOD8":variant})
                with self.assertRaisesRegex(selective_linker.LinkError,"budget"):
                    selective_linker.build(plan,Path(folder))
                self.assertFalse((Path(folder)/"math_selective.prg").exists())
                man=self.make(folder,variant)
                self.assertEqual(man["link_exports"],["MATH_UMOD8"])
                self.assertEqual(man["operations"][0]["variant"],variant)
        with tempfile.TemporaryDirectory() as folder:
            plan=math_builder.create_plan(self.index,["UMOD8"],zp_budget=2,ram_budget=189)
            man=selective_linker.build(plan,Path(folder))
            self.assertEqual(man["operations"][0]["variant"],"link:v1-fast-fallback")


if __name__=="__main__":
    unittest.main()
