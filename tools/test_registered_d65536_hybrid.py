#!/usr/bin/env python3
"""Registered D=$00010000 public-ABI and two-relocation source qualification.

The production operation-first builder must select this only when pinned or
when a measured workload requires it. Retain all historical variants.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

import math_builder
import selective_linker
import selective_speed_s3232 as signed
import selective_speed_u3232 as unsigned
from mini6502 import CPU, load_sparse

VARIANT="link:d65536-hybrid"
APIS=("MATH_SDIV32_32","MATH_SMOD32_32",
      "MATH_UDIV32_32","MATH_UMOD32_32")
PLACEMENTS=((0x8000,0xc000,0x50),(0x4123,0xc040,0x70))


def build_at(code,io,zp,root):
    index=math_builder.operation_index()
    pins={api[5:]:VARIANT for api in APIS}
    plan=math_builder.create_plan(
        index,list(APIS),objective="size",zp_budget=12,ram_budget=10000,
        pins=pins,validate_sources=True)
    with tempfile.TemporaryDirectory(prefix="d65536_link_") as td:
        out=Path(td)
        manifest=selective_linker.build(
            plan,out,memory={"code_base":code,"math_io":io,
                             "zp_base":zp,"scratch_base":io+0x40})
        binary=(out/"math_selective.prg").read_bytes()
    entries={row["api"]:int(row["entry"][1:],16) for row in manifest["operations"]}
    variants={row["api"]:row["variant"] for row in manifest["operations"]}
    if variants!={api:VARIANT for api in APIS} or set(entries)!=set(APIS):
        raise AssertionError("Installer did not export four pinned D65536 public entries")
    return binary,entries,manifest


class RegisteredD65536Tests(unittest.TestCase):
    def test_public_catalog_and_dependency_sha_are_attested(self):
        index=math_builder.operation_index()
        for api in APIS:
            options=index[api]["variants"]
            by_id={row["id"]:row for row in options}
            self.assertIn(VARIANT,by_id)
            self.assertIn("link:v2-hybrid-signed" if "_S" in api else
                          "link:v2-lowdivisor-hybrid",by_id)
            x=by_id[VARIANT]
            self.assertTrue(x["selective_link_ready"])
            self.assertEqual(x["source_path"],"tools/research_d65536_hybrid.py")
            self.assertGreaterEqual(len(x["dependency_sha256"]),3)
            math_builder.validate_sha(math_builder.ROOT,x)

    def test_both_relocations_shared_exports_and_full_qr_c(self):
        inputs=((0x80000001,0x10000),(0xffffffff,0x10000),
                (0x80000000,0x10000),(0x10001,0x10000),
                (0xffffffff,0xffff),(0,0),(0xffffffff,0),
                (0x80000001,0xffff0000),(0xffffffff,0xffffffff),
                (0x7fffffff,0x10001))
        for code,io,zp in PLACEMENTS:
            with self.subTest(code=hex(code)):
                binary,entries,manifest=build_at(code,io,zp,math_builder.ROOT)
                self.assertEqual(binary[:2],code.to_bytes(2,"little"))
                self.assertEqual(entries["MATH_SDIV32_32"],entries["MATH_SMOD32_32"])
                self.assertEqual(entries["MATH_UDIV32_32"],entries["MATH_UMOD32_32"])
                self.assertNotEqual(entries["MATH_SDIV32_32"],entries["MATH_UDIV32_32"])
                self.assertEqual(manifest["resource_use"]["zero_page_bytes"],12)
                executable={code+i:b for i,b in enumerate(binary[2:])}
                for api in APIS:
                    cpu=CPU(load_sparse(executable))
                    sp=cpu.sp
                    for i,(n,d) in enumerate(inputs):
                        nb=n.to_bytes(4,"little");db=d.to_bytes(4,"little")
                        cpu.mem[io+16:io+20]=nb
                        cpu.mem[io+20:io+24]=db
                        cpu.mem[io+24:io+32]=b'\x55'*8
                        cpu.a=(n+d+i)&255
                        cpu.x=(n>>8)&255;cpu.y=(d>>8)&255
                        cpu.c=i&1;cpu.d=0
                        cpu.call(entries[api],150000)
                        got=(int.from_bytes(cpu.mem[io+24:io+28],"little"),
                             int.from_bytes(cpu.mem[io+28:io+32],"little"),cpu.c)
                        want=(signed.reference(n,d) if api.startswith("MATH_S")
                              else (n//d if d else 0,n%d if d else 0,int(d==0)))
                        self.assertEqual(got,want,(api,hex(n),hex(d)))
                        self.assertEqual(bytes(cpu.mem[io+16:io+20]),nb)
                        self.assertEqual(bytes(cpu.mem[io+20:io+24]),db)
                        self.assertEqual(cpu.sp,sp)
                    self.assertTrue(all(cpu.mem[a]==b for a,b in executable.items()))


if __name__=="__main__":
    unittest.main()
