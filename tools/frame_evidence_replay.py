#!/usr/bin/env python3
"""Replay the exact qualified public-call frame benchmark before trusting cycles.

Never trust the source/PRG SHA alone as proof of latency: those hashes do not
authenticate claims about frame scheduling, call counts, peaks or p95.
Re-execute the registered 3-operation deterministic source-linked benchmark
at every reported relocation and require complete byte-value JSON equality.

No generalization to arbitrary 56-API traces is implied; a new trace producer
must be explicitly registered and qualified before frame-objective adoption.
"""
from __future__ import annotations

import json
import re
from mixed_frame_frontier import EvidenceError

REGISTERED_BASIS = "three-operation same-input linked source math-only frames"


def address(raw, label):
    if not isinstance(raw, str) or re.fullmatch(r"\$[0-9A-F]{4}", raw) is None:
        raise EvidenceError("Invalid fixed-width measured address: " + label)
    return int(raw[1:], 16)


def replay(report):
    """Return a newly executed source-linked report or raise EvidenceError.

    Unlike a report checksum, this checks that actual measured frame costs,
    selected source hashes and PRG provenance are still true *now*.
    """
    from mixed3_frame_parity import OPS, compare

    if not isinstance(report, dict) or report.get("basis") != REGISTERED_BASIS:
        raise EvidenceError("Unsupported/unattested frame benchmark producer")
    if report.get("operations") != list(OPS):
        raise EvidenceError("This benchmark requires exact three-operation ABI order")
    locations = report.get("placements")
    if not isinstance(locations, list) or len(locations) != 2:
        raise EvidenceError("Require two independent registered benchmark relocations")
    measured = []
    seen = set()
    for original in locations:
        if not isinstance(original, dict):
            raise EvidenceError("Malformed benchmark location")
        code = address(original.get("code"), "code")
        io = address(original.get("io"), "math_io")
        zp = address(original.get("zp_base"), "zp_base")
        scratch = address(original.get("scratch_base"), "scratch_base")
        if (code, io, zp, scratch) in seen or scratch != io + 0x40:
            raise EvidenceError("Duplicated relocation or invalid benchmark scratch position")
        seen.add((code, io, zp, scratch))
        # This calls math_builder and the real source linker, runs 150 public
        # UMUL32/SMUL32/ISQRT16 calls for every one of eight source plans,
        # and remeasures all 24 frames using the qualified CPU model.
        measured.append(compare(code, io, zp))
    regenerated = {"basis": REGISTERED_BASIS, "operations": list(OPS),
                   "placements": measured}
    if report != regenerated:
        raise EvidenceError(
            "Frame evidence disagrees with fresh source-linked public-call replay "
            "(input corpus, source/PRG hash, frame cycles or RAM/ZP)")
    return regenerated


def main():
    import argparse
    from pathlib import Path
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", required=True, type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args()
    try:
        regenerated = replay(json.loads(a.report.read_text(encoding="utf-8")))
    except (ValueError, OSError) as exc:
        ap.error(str(exc))
    proof = {
        "schema": "frame-source-replay-proof-v1",
        "benchmark": REGISTERED_BASIS,
        "reexecuted": True,
        "placements": len(regenerated["placements"]),
        "operations": regenerated["operations"],
        "input_corpus_sha256": regenerated["placements"][0]["input_corpus_sha256"],
        "report_sha256": __import__("hashlib").sha256(
            json.dumps(regenerated, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest(),
        "cpu_model_only": True, "physical_pal_feasibility_claim": False,
    }
    output = json.dumps(proof, sort_keys=True, indent=2) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
