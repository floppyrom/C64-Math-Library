#!/usr/bin/env python3
"""Issue #144: signed 32x32 SHR16 direct clone/hybrid public-entry screen.

Research only: stock V2/V3/V4 resident binaries, tables and stock signed/
unsigned producers are left intact. Redirect the ordinary signed public JMP
in disposable memory to independently assembled wrapper code, paired against
the stock public entry on exactly identical operand vectors. No private
OptiSearch sources or unverified production promotion.
"""
from __future__ import annotations
import argparse, hashlib, json, statistics, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mini6502 import Assembler
from benchmark_multiply_refresh import CORPORA, load
from issue144_shr16_independent_clone import (
    PROFILES, assemble as unsigned_assemble, installed_mem, before_blob, sha)
from issue144_shr16_direct_slice_overlay_research import run, metrics

INPUTS = "MATH_SMUL32_SHR16"
ENTRY = 0x5E15
DEFAULT_JMP = bytes((0x4C, 0x0C, 0xC5))
SOURCE = "optional/issue144_signed_shr16_hybrid/research_signed_shr16.asm"
EVIDENCE = "validation/review/ISSUE144_SIGNED_SHR16_HYBRID_RESEARCH.json"
VARIANTS = {
    "correct_all": "MATH_SMUL32_SHR16_CORRECT_ALL",
    "negative_pair_fallback": "MATH_SMUL32_SHR16_HYBRID",
}

def quadrant(x, y):
    return ("N" if (x & 0x80000000) else "P") + ("N" if (y & 0x80000000) else "P")

def stats_signed(values):
    values = list(values)
    ordered = sorted(values)
    return {
        "cases": len(values),
        "mean_cycles": sum(values) / len(values),
        "median_cycles": statistics.median(values),
        "p95_cycles": ordered[int(0.95 * (len(values) - 1))],
        "minimum": ordered[0],
        "maximum": ordered[-1],
        "cycle_vector_sha256": sha(
            b"".join(int(x).to_bytes(4, "little", signed=True) for x in values))
    }

def install_signed(cpu, signed_code, label):
    assert bytes(cpu.mem[ENTRY:ENTRY+3]) == DEFAULT_JMP
    assert label < 0x1000
    for pc, b in signed_code.items():
        assert 0x0E50 <= pc < 0x1000
        assert cpu.mem[pc] == 0, ("nonempty chosen RAM", hex(pc))
        cpu.mem[pc] = b
    cpu.mem[ENTRY+1:ENTRY+3] = bytes((label & 255, label >> 8))
    assert bytes(cpu.mem[ENTRY:ENTRY+3]) == bytes((0x4C,label&255,label>>8))

def check_profile(profile, signed_code, labels, clone, pairs):
    reference, public_api = load(profile)
    assert public_api[INPUTS] == ENTRY
    assert bytes(reference.mem[ENTRY:ENTRY+3]) == DEFAULT_JMP
    old_source, _, _, _, _ = unsigned_assemble()
    before_blob(profile, old_source)
    machines = {}
    for kind, name in VARIANTS.items():
        c, api = load(profile)
        assert api == public_api
        installed_mem(c, clone)
        install_signed(c, signed_code, labels[name])
        machines[kind] = c

    old_cycles = []
    cycles = {k: [] for k in VARIANTS}
    groups = defaultdict(lambda: {"stock":[], **{k:[] for k in VARIANTS}})
    deltas = {k:[] for k in VARIANTS}
    for index, (x,y) in enumerate(pairs):
        # Equal preceding-call schedule in baseline and every candidate.
        if index % 17 == 0 or index % 23 == 0:
            xx, yy = pairs[(index*109+13) % len(pairs)]
            for machine in [reference, *machines.values()]:
                if index % 17 == 0:
                    run(machine, public_api, "MATH_UMUL32", xx, yy)
                if index % 23 == 0:
                    run(machine, public_api, "MATH_SMUL32", xx, yy)
        stock, raw_output = run(reference, public_api, INPUTS, x, y)
        old_cycles.append(stock)
        q = quadrant(x, y)
        groups[q]["stock"].append(stock)
        for kind, machine in machines.items():
            new, value = run(machine, public_api, INPUTS, x, y)
            assert value == raw_output, (profile, kind, index)
            cycles[kind].append(new)
            deltas[kind].append(stock-new)
            groups[q][kind].append(new)
        if index % 600 == 0:
            print("ISSUE144 SIGNED SCREEN", profile, index, flush=True)

    # Restore and re-test the original signed entry plus ordinary paths.
    for machine in machines.values():
        machine.mem[ENTRY+1:ENTRY+3] = DEFAULT_JMP[1:]
        assert bytes(machine.mem[ENTRY:ENTRY+3]) == DEFAULT_JMP
        for x,y in pairs[:min(80,len(pairs))]:
            run(machine, public_api, INPUTS, x,y)
            run(machine, public_api, "MATH_UMUL32", x,y)
            run(machine, public_api, "MATH_SMUL32", x,y)

    return {
        "profile": profile,
        "status": "PASS_MODEL_PUBLIC_ENTRY_SEQUENTIAL_SIGNED_48BIT",
        "pairs": len(pairs),
        "stock": metrics(old_cycles),
        "variants": {kind: {
             "timing": metrics(cycles[kind]),
             "savings_stock_minus_candidate": stats_signed(deltas[kind]),
             "faster_cases": sum(x>0 for x in deltas[kind]),
             "equal_cases": sum(x==0 for x in deltas[kind]),
             "slower_cases": sum(x<0 for x in deltas[kind]),
        } for kind in VARIANTS},
        "quadrants": {q: {
             "count": len(v["stock"]),
             "stock": metrics(v["stock"]),
             **{kind: {
               "cycles": metrics(v[kind]),
               "paired_savings": stats_signed(
                   a-b for a,b in zip(v["stock"],v[kind]))
               } for kind in VARIANTS}
          } for q,v in sorted(groups.items())},
        "other_multiply_calls_interleaved": True,
        "both_public_signed_and_unsigned_restored_and_retested": True,
        "stock_producer_executable_stays_independent": True,
        "native_vice_qualified": False,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=2409)
    a = parser.parse_args()
    assert 1 <= a.limit <= len(CORPORA[32])
    original, clone, _, source, changes = unsigned_assemble()
    assert changes["high"] == 6
    asm_source = (ROOT/SOURCE).read_text()
    signed_code, labels, _ = Assembler().assemble(asm_source)
    assert 0x0E50 <= min(signed_code) < max(signed_code) < 0x1000
    assert labels["MATH_SMUL32_SHR16_CORRECT_ALL"] == 0x0E50
    assert labels["MATH_SMUL32_SHR16_HYBRID"] == 0x0EB0
    assert not set(signed_code).intersection(clone)
    pairs = CORPORA[32][:a.limit]
    record = {
      "status": "PASS_RESEARCH_MODEL_ONLY_NO_PROMOTION",
      "public_entry": "$5E15", "baseline_destination": "$C50C",
      "stock_unsigned_clone_entry": "$0E03",
      "input_pairs_sha256":sha(
        b"".join(x.to_bytes(4,"little")+y.to_bytes(4,"little") for x,y in pairs)),
      "source_sha256":sha(asm_source.encode()),
      "unsigned_clone_source_sha256":sha(source.encode()),
      "signed_reserved_span":[hex(min(signed_code)),hex(max(signed_code))],
      "emitted_signed_bytes":len(signed_code),
      "profiles":{}, "private_optisearch_source_included":False,
      "default_shipped_prgs_changed":False,
      "native_cycles_measured":False,
      "native_vice_qualified":False,
    }
    for profile in PROFILES:
        result = check_profile(profile,signed_code,labels,clone,pairs)
        record["profiles"][profile] = result
        for kind in VARIANTS:
            delta = result["variants"][kind]["savings_stock_minus_candidate"]
            print("RESULT", profile,kind,"mean-saved",
                  round(delta["mean_cycles"],3),"worst-saving",delta["minimum"],
                  "best-saving",delta["maximum"],flush=True)
    dest=ROOT/EVIDENCE
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print("ISSUE144 SIGNED SHR16 RESEARCH MODEL PASS",a.limit*len(PROFILES))

if __name__ == "__main__":
    main()
