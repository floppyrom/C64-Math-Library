#!/usr/bin/env python3
"""Source-assembled same-corpus cycle comparison of historical V1, V2, V5 UMOD8."""
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import random
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"tools"))
import math_builder
import selective_linker
from mini6502 import CPU

SOURCE_VARIANTS=("link:v1-fast-fallback","link:v2-unrolled-fallback",
                 "link:v5-unrolled-hybrid")
EDGES=(0,1,2,3,7,15,16,31,32,63,64,127,128,255)
SEED=0xC6450D8


def corpus():
    rng=random.Random(SEED)
    cases=[(n,d) for d in EDGES for n in EDGES]
    cases.extend((rng.randrange(256), rng.choice(range(3,32)))
                 for _ in range(500))
    cases.extend((rng.randrange(256), rng.randrange(256))
                 for _ in range(1000-len(cases)))
    assert len(cases)==1000
    return cases


def reference(n,d):
    return (n%d,0) if d else (0,1)


class UMOD8MatchedCycles(unittest.TestCase):
    def test_same_corpus_sources_and_cycles(self):
        idx=math_builder.operation_index()
        pairs=corpus()
        checksum=hashlib.sha256(bytes(z for n,d in pairs for z in (n,d))).hexdigest()
        results={}
        for variant in SOURCE_VARIANTS:
            with self.subTest(variant=variant),tempfile.TemporaryDirectory() as tmp:
                plan=math_builder.create_plan(
                    idx,["UMOD8"],pins={"UMOD8":variant},zp_budget=2,ram_budget=261)
                result=selective_linker.build(plan,Path(tmp))
                image=(Path(tmp)/"math_selective.prg").read_bytes()
                start=int.from_bytes(image[:2],"little")
                entry=int(result["operations"][0]["entry"][1:],16)
                cpu=CPU(bytearray(65536))
                cpu.mem[start:start+len(image)-2]=image[2:]
                cycles=0
                smalldiv_cycles=0
                smalldiv_calls=0
                stack=cpu.sp
                for n,d in pairs:
                    cpu.mem[0xc010]=n
                    cpu.mem[0xc014]=d
                    cpu.mem[0xc018:0xc01c]=b"\x55"*4
                    cpu.mem[0xc01c]=0x66
                    cpu.c=(n^d)&1
                    cpu.d=0
                    elapsed=cpu.call(entry,12000)
                    self.assertEqual((cpu.mem[0xc01c],cpu.c),reference(n,d))
                    self.assertEqual(cpu.mem[0xc018:0xc01c],b"\x55"*4)
                    self.assertEqual((cpu.mem[0xc010],cpu.mem[0xc014]),(n,d))
                    self.assertEqual(cpu.sp,stack)
                    cycles+=elapsed
                    if 3<=d<32:
                        smalldiv_cycles+=elapsed
                        smalldiv_calls+=1
                results[variant]={
                    "mean_cycles": cycles/len(pairs),
                    "small_divisor_mean_cycles": smalldiv_cycles/smalldiv_calls,
                    "small_divisor_cases": smalldiv_calls,
                    "cases":len(pairs),"source_sha256":next(
                        v["source_sha256"] for v in plan["operations"][0]["available_source_variants"]
                        if v["id"]==variant),
                    "code_bytes":result["resource_use"]["code_and_tables_bytes"],
                    "zero_page_bytes":result["resource_use"]["zero_page_bytes"]
                }
        # Do not claim automatic best-speed selection from a single corpus.
        # Both variants must be measured on IDENTICAL cases and pass the ABI.
        self.assertEqual(results[SOURCE_VARIANTS[0]]["code_bytes"],157)
        self.assertEqual(results[SOURCE_VARIANTS[1]]["code_bytes"],229)
        self.assertEqual(results[SOURCE_VARIANTS[2]]["code_bytes"],205)
        self.assertEqual({x["cases"] for x in results.values()},{1000})
        self.assertEqual(len({x["source_sha256"] for x in results.values()}),3)
        self.assertTrue(all(x["mean_cycles"]>0 and x["small_divisor_mean_cycles"]>0
                            for x in results.values()))
        print(json.dumps({"basis":"UMOD8 same-input source-assembled 6502 CPU model",
                          "corpus_sha256":checksum,
                          "not_native_hardware_timing":True,
                          "measurements":results},indent=2,sort_keys=True))


if __name__=="__main__":
    unittest.main()
