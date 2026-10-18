#!/usr/bin/env python3
"""Paired matched-input signed24/24 Q0 hot path, full public ABI, two relocations."""
from __future__ import annotations
import json
import random
import tempfile
import unittest
from pathlib import Path
import math_builder
import selective_linker
from mini6502 import CPU
from test_selective_sdiv24 import reference, signed24

OPS = ("SDIV24", "SMOD24")
GUARD = "link:abs-qzero-guard"
BASE = "link:portable-zerozp"

def corpus():
    rng = random.Random(0x2424AB5)
    edges = (0, 1, 2, 3, 255, 65535, 65536, 0x7fffff,
             0x800000, 0x800001, 0xfffffe, 0xffffff)
    pairs = [(n, d) for n in edges for d in edges]
    pairs += [(rng.getrandbits(24), rng.getrandbits(24)) for _ in range(384)]
    # Force both zero-quotient and full restoring-loop domains.
    for _ in range(192):
        d = rng.randint(2, 0x7fffff)
        n = rng.randrange(d)
        if rng.randrange(2): n = (-n) & 0xffffff
        if rng.randrange(2): d = (-d) & 0xffffff
        pairs.append((n, d))
    for _ in range(192):
        d = rng.randint(1, 256)
        n = rng.randrange(1 << 24)
        pairs.append((n, d if rng.randrange(2) else (-d) & 0xffffff))
    return pairs

def compile_variant(td, variant, code, io):
    plan = math_builder.create_plan(math_builder.operation_index(), list(OPS),
       objective="size", zp_budget=0, ram_budget=480,
       pins={name: variant for name in OPS})
    where = Path(td) / variant.replace(":", "_")
    man = selective_linker.build(plan, where, memory={
        "code_base": code, "math_io": io, "scratch_base": io + 0x40})
    entries = {v["api"]: int(v["entry"][1:], 16) for v in man["operations"]}
    assert entries["MATH_SDIV24"] == entries["MATH_SMOD24"]
    assert man["resource_use"]["zero_page_bytes"] == 0
    assert man["resource_use"]["private_ram_scratch_bytes"] == 7
    assert len(man["link_order"]) == 1
    binary = (where / "math_selective.prg").read_bytes()
    mem = bytearray(65536)
    mem[code:code + len(binary) - 2] = binary[2:]
    return CPU(mem), entries["MATH_SDIV24"], man, len(binary)-2

def run(cpu, entry, io, case):
    n, d = case
    mem = cpu.mem
    mem[io + 16:io + 20] = n.to_bytes(3, "little") + b"\x5a"
    mem[io + 20:io + 24] = d.to_bytes(3, "little") + b"\xa5"
    mem[io + 24:io + 28] = b"\xcc\xcc\xcc\x39"
    mem[io + 28:io + 32] = b"\xdd\xdd\xdd\x59"
    cpu.c = (n ^ d) & 1
    cpu.d = 0
    sp = cpu.sp
    elapsed = cpu.call(entry, 100000)
    if cpu.sp != sp:
        raise AssertionError("Stack pointer changed")
    answer = (int.from_bytes(mem[io+24:io+27], "little"),
              int.from_bytes(mem[io+28:io+31], "little"), cpu.c)
    if answer != reference(n, d):
        raise AssertionError(("Incorrect signed result", n, d, answer, reference(n,d)))
    if (mem[io+27],mem[io+31],mem[io+19],mem[io+23]) != (0x39,0x59,0x5a,0xa5):
        raise AssertionError("High result byte or input modified")
    return elapsed

class Signed24QzeroTests(unittest.TestCase):
    def test_public_abi_and_matched_cycle_tradeoff_at_two_relocations(self):
        for code, io in ((0x8000,0xc000),(0x7123,0xc040)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as td:
                b, ep_b, bm, bsize = compile_variant(td, BASE, code, io)
                g, ep_g, gm, gsize = compile_variant(td, GUARD, code, io)
                self.assertEqual(bsize,325)
                self.assertEqual(gsize,387)
                self.assertEqual(bm["resource_use"]["main_ram_total_bytes"], 364)
                self.assertEqual(gm["resource_use"]["main_ram_total_bytes"], 426)
                # Inputs are identical; call entries use the exact same public map.
                inputs=corpus()
                deltas=[]
                baseline_cycles=[]
                qzero=[]
                for pair in inputs:
                    before=run(b,ep_b,io,pair)
                    after=run(g,ep_g,io,pair)
                    baseline_cycles.append(before)
                    delta=before-after
                    deltas.append(delta)
                    if signed24(pair[1]) and abs(signed24(pair[0]))<abs(signed24(pair[1])):
                        qzero.append(delta)
                self.assertTrue(qzero)
                self.assertGreater(min(qzero),0,"All true quotient-zero calls must improve")
                self.assertGreater(sum(deltas),0,"Mixed-domain mean must improve")
                result={"code":hex(code),"cases":len(deltas),
                        "baseline_mean":round(sum(baseline_cycles)/len(baseline_cycles),3),
                        "mean_saved":round(sum(deltas)/len(deltas),3),
                        "min_qzero_saved":min(qzero),"max_qzero_saved":max(qzero),
                        "worst_regression":-min(deltas),
                        "baseline_bytes":bsize,"guarded_bytes":gsize}
                print("SIGNED24_QZERO_PAIRED",json.dumps(result),flush=True)
if __name__=="__main__":
    unittest.main()
