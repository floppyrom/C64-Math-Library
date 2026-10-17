#!/usr/bin/env python3
"""Ready32 operation-first aliases are safe, fully signed/unsigned, and deduplicated."""
from __future__ import annotations
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker
from mini6502 import CPU

MULS=("UMUL32","UMUL32_READY","SMUL32","SMUL32_READY")
ALL=MULS+("UMUL24","SMUL24")
EDGES=(0,1,2,255,256,65535,0x7fffffff,0x80000000,0xffffffff)
def signed(v):return v-(1<<32) if v&0x80000000 else v
def operands():
    rng=random.Random(0x2432c64)
    return [(x,y) for x in EDGES for y in EDGES]+[
        (rng.getrandbits(32),rng.getrandbits(32)) for _ in range(480)]

class Ready32Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index=math_builder.operation_index()
    def plan(self, names, budget=None):
        return math_builder.create_plan(self.index,list(names),objective="size",
                                       zp_budget=0,ram_budget=budget)

    def test_shared_safe_fallback_and_mixed_invalidation(self):
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080),
                                (0x830f,0xc100,0xc140)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                man=selective_linker.build(self.plan(ALL,924),Path(td),
                    memory={"code_base":code,"math_io":io,"scratch_base":scratch})
                self.assertEqual(man["resource_use"]["image_span_bytes"],880)
                self.assertEqual(man["resource_use"]["main_ram_total_bytes"],924)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],12)
                self.assertEqual(man["resource_use"]["zero_page_bytes"],0)
                self.assertEqual(len(man["link_order"]),4)
                ep={x["api"]:int(x["entry"][1:],16) for x in man["operations"]}
                self.assertEqual(ep["MATH_UMUL32_READY"],ep["MATH_UMUL32"])
                self.assertEqual(ep["MATH_SMUL32_READY"],ep["MATH_SMUL32"])
                prg=(Path(td)/"math_selective.prg").read_bytes()
                mem=bytearray(65536)
                mem[code:code+880]=prg[2:]
                before=bytes(mem[code:code+880])
                cpu=CPU(mem);sp=cpu.sp
                for i,(x,y) in enumerate(operands()):
                    xb=x.to_bytes(4,"little");yb=y.to_bytes(4,"little")
                    mem[io:io+4]=xb;mem[io+4:io+8]=yb
                    cpu.d=0
                    # Deliberately clobber shared call-exclusive RAM with two
                    # other operators between ordinary and READY calls.
                    for api in ("UMUL32","UMUL24","SMUL24","UMUL32_READY",
                                "SMUL32","UMUL24","SMUL24","SMUL32_READY"):
                        cpu.c=(i+x+y)&1
                        cpu.call(ep["MATH_"+api],180000)
                        if api.startswith("UMUL32"):
                            result=x*y
                            out_bytes=8
                        elif api.startswith("SMUL32"):
                            result=(signed(x)*signed(y))&((1<<64)-1)
                            out_bytes=8
                        else:
                            continue
                        self.assertEqual(int.from_bytes(mem[io+8:io+8+out_bytes],"little"),
                                         result,(code,api,x,y))
                        self.assertEqual(cpu.c,0,(code,api,x,y,"carry"))
                        self.assertEqual(bytes(mem[io:io+4]),xb)
                        self.assertEqual(bytes(mem[io+4:io+8]),yb)
                        self.assertEqual(cpu.sp,sp)
                self.assertEqual(bytes(mem[code:code+880]),before)
        with tempfile.TemporaryDirectory() as td:
            both=selective_linker.build(self.plan(MULS,541),Path(td))
            self.assertEqual(both["resource_use"]["main_ram_total_bytes"],541)
            self.assertEqual(len(both["link_order"]),2)
            with self.assertRaises(selective_linker.LinkError):
                selective_linker.build(self.plan(MULS,540),Path(td)/"low")

if __name__=="__main__":
    unittest.main()
