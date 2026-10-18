#!/usr/bin/env python3
"""Paired public-ABI and cycle screen for V2-magnitude signed 32/16 producer."""
from __future__ import annotations

import hashlib
import random
import re
import unittest
from pathlib import Path

from mini6502 import Assembler, CPU, load_sparse
import research_signed_v2_u3216 as candidate
from test_selective_sdiv32_16 import N_EDGE, D_EDGE, reference

ROOT = Path(__file__).resolve().parents[1]
CASES = 384
SEED = 0x5D321603


def corpus():
    rng = random.Random(SEED)
    pairs = [(n, d) for n in N_EDGE for d in D_EDGE]
    pairs.extend((rng.getrandbits(32), rng.getrandbits(16))
                 for _ in range(CASES-len(pairs)))
    if len(pairs) != CASES:
        raise ValueError("Signed 32/16 paired corpus changed")
    return pairs


def portable_image(code, io, ram):
    source = (ROOT / "routines/divide/sdiv32_16_smod32_16_zerozp.asm").read_text()
    values = {"KERNEL_CODE": code, "INPUT_NUM": io+16, "INPUT_DIV": io+20,
              "OUTPUT_QUOT": io+24, "OUTPUT_REM": io+28, "TEMP_RAM": ram}
    for label, addr in values.items():
        source, changed = re.subn(r"(?m)^" + label + r"\s*=\s*\$[0-9a-fA-F]+$",
                                  label + " = $%04X" % addr, source)
        if changed != 1:
            raise AssertionError("Missing portable relocation symbol: " + label)
    return Assembler().assemble(source)


def public_call(cpu, entry, io, n, d, first_c):
    mem = cpu.mem
    nbytes = n.to_bytes(4, "little")
    dbytes = d.to_bytes(2, "little") + b"\x7c\x6b"
    mem[io+16:io+20] = nbytes
    mem[io+20:io+24] = dbytes
    mem[io+24:io+28] = b"\xcc" * 4
    mem[io+28:io+32] = b"\xdd\xdd\x49\x59"
    cpu.d = 0
    cpu.c = first_c
    cpu.a, cpu.x, cpu.y = (n ^ d)&255, (n>>8)&255, (d>>8)&255
    before_sp = cpu.sp
    cycles = cpu.call(entry, 150000)
    output = (int.from_bytes(mem[io+24:io+28], "little"),
              int.from_bytes(mem[io+28:io+30], "little"), cpu.c)
    if output != reference(n, d):
        raise AssertionError(("bad quotient/remainder/carry", hex(n), hex(d), output, reference(n,d)))
    if (bytes(mem[io+16:io+20]) != nbytes or
            bytes(mem[io+20:io+24]) != dbytes or
            bytes(mem[io+30:io+32]) != b"\x49\x59" or cpu.sp != before_sp):
        raise AssertionError(("public input, high output, or stack modified", hex(n), hex(d)))
    return cycles


class SignedV2MagnitudeResearch(unittest.TestCase):
    def test_source_relocation_paired_abi_cycle_frontier(self):
        pairs = corpus()
        digest = hashlib.sha256(b"".join(
            n.to_bytes(4,"little")+d.to_bytes(2,"little") for n,d in pairs)).hexdigest()
        for code, io, zp in ((0x8000,0xC000,0x50),(0x7123,0xC040,0x70)):
            with self.subTest(code=code):
                donor, labels, meta = candidate.assemble(code, io, zp)
                compact, clabels, _ = portable_image(code, io, io+0x40)
                self.assertEqual(meta["scratch_zp_bytes"],12)
                self.assertEqual(meta["ordinary_ram_scratch_bytes"],0)
                self.assertEqual(meta["image_span_bytes"],candidate.IMAGE_BYTES)
                self.assertEqual(labels[candidate.ENTRY],labels["FAST_SMOD32_16_V2MAG"])
                self.assertEqual(len(compact),260)
                cpu = CPU(load_sparse(donor))
                basecpu = CPU(load_sparse(compact))
                donor_before = bytes(cpu.mem[code:code+candidate.IMAGE_BYTES])
                before = []
                after = []
                for i,(n,d) in enumerate(pairs):
                    old = public_call(basecpu,clabels["FAST_SDIV32_16_ZEROZP"],io,n,d,i&1)
                    new = public_call(cpu,labels[candidate.ENTRY],io,n,d,i&1)
                    before.append(old)
                    after.append(new)
                self.assertEqual(
                    bytes(cpu.mem[code:code+candidate.IMAGE_BYTES]),
                    donor_before, "Historical source and adapter unexpectedly modified executable")
                faster=sum(new<old for old,new in zip(before,after))
                slower=sum(new>old for old,new in zip(before,after))
                print("SIGNED_V2_MAGNITUDE_PAIRED",{
                    "placement":"$%04X/$%04X"%(code,io),
                    "pairs":len(pairs),"corpus_sha256":digest,
                    "portable_mean":round(sum(before)/len(before),3),
                    "historical_v2_magnitude_mean":round(sum(after)/len(after),3),
                    "cycles_saved":sum(before)-sum(after),
                    "max_regression":max(new-old for old,new in zip(before,after)),
                    "faster_calls":faster,"slower_calls":slower,
                    "zero_page":meta["scratch_zp_bytes"],
                    "packed_bytes":meta["image_span_bytes"]},flush=True)
                # Correctness is mandatory. This research candidate must also
                # beat the compact producer on the balanced identical corpus.
                self.assertGreater(sum(before),sum(after))


if __name__=="__main__":
    unittest.main()
