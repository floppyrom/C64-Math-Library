#!/usr/bin/env python3
"""Score measured public-call arithmetic traces against per-frame cycle budgets.

This is an offline trace scorer; it does not synthesize measurements from
historical means. JSR costs are added explicitly to entry-through-RTS cycles.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

PAL_FRAME_CYCLES = 19656
COLUMNS = ("frame", "call", "operation", "input_id", "cycles", "variant",
           "measurement_basis", "placement")


@dataclass(frozen=True)
class Call:
    frame: int
    ordinal: int
    operation: str
    input_id: str
    cycles: int
    variant: str

    @property
    def key(self) -> tuple[int, int, str, str]:
        return self.frame, self.ordinal, self.operation, self.input_id


def load_trace(path: Path) -> tuple[list[Call], dict]:
    """Refuse ambiguous inputs, mixed timing bases, or mixed source choices."""
    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None or not set(COLUMNS).issubset(reader.fieldnames):
            raise ValueError(f"{path}: required CSV columns: {', '.join(COLUMNS)}")
        slots = set()
        calls = []
        bases, placements = set(), set()
        variants: dict[str, str] = {}
        for line, record in enumerate(reader, 2):
            try:
                frame = int(record["frame"])
                ordinal = int(record["call"])
                cycles = int(record["cycles"])
            except (ValueError, TypeError) as exc:
                raise ValueError(f"{path}:{line}: invalid frame/call/cycles integer") from exc
            if frame < 0 or ordinal < 0 or cycles < 0:
                raise ValueError(f"{path}:{line}: negative frame/call/cycles")
            slot = frame, ordinal
            if slot in slots:
                raise ValueError(f"{path}:{line}: duplicate call slot {slot}")
            slots.add(slot)
            for field in ("operation", "input_id", "variant", "measurement_basis", "placement"):
                if not record[field] or not record[field].strip():
                    raise ValueError(f"{path}:{line}: empty {field}")
            op = record["operation"].strip()
            variant = record["variant"].strip()
            if op in variants and variants[op] != variant:
                raise ValueError(f"{path}:{line}: inconsistent variant for {op}")
            variants[op] = variant
            bases.add(record["measurement_basis"].strip())
            placements.add(record["placement"].strip())
            calls.append(Call(frame, ordinal, op, record["input_id"].strip(), cycles, variant))
    if not calls or len(bases) != 1 or len(placements) != 1:
        raise ValueError(f"{path}: empty trace or mixed timing bases / placements")
    return calls, {"measurement_basis": bases.pop(), "placement": placements.pop(),
                   "variants": dict(sorted(variants.items()))}


def nearest_rank(values: list[int], percent: int) -> int:
    return sorted(values)[math.ceil(len(values) * percent / 100) - 1]


def score(calls: list[Call], metadata: dict, *, frame_count: int | None = None,
          budget: int = PAL_FRAME_CYCLES, jsr_cycles: int = 6) -> dict:
    if budget <= 0 or jsr_cycles < 0:
        raise ValueError("Budget must be positive and JSR cost nonnegative")
    if frame_count is None:
        frame_count = max(c.frame for c in calls) + 1
    if frame_count <= 0 or any(c.frame >= frame_count for c in calls):
        raise ValueError("Frame count does not cover entire trace")
    frame_costs = [0] * frame_count
    per_frame_op: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    per_op: dict[str, list[int]] = defaultdict(list)
    for c in calls:
        cost = c.cycles + jsr_cycles
        frame_costs[c.frame] += cost
        per_frame_op[c.frame][c.operation] += cost
        per_op[c.operation].append(cost)
    peak = max(range(frame_count), key=lambda f: frame_costs[f])
    hottest = sorted(({"operation": op, "cycles": cycles,
                       "share_percent": round(cycles * 100 / frame_costs[peak], 3)}
                      for op, cycles in per_frame_op[peak].items()),
                     key=lambda d: (-d["cycles"], d["operation"])) if frame_costs[peak] else []
    operations = sorted(({"operation": op, "calls": len(values),
                          "total_cycles": sum(values),
                          "mean_call_cycles": round(sum(values) / len(values), 3),
                          "max_call_cycles": max(values),
                          "peak_frame_cycles": max(per_frame_op[f].get(op, 0)
                                                   for f in range(frame_count)),
                          "variant": metadata["variants"][op]}
                         for op, values in per_op.items()),
                        key=lambda d: (-d["total_cycles"], d["operation"]))
    return {"measurement_basis": metadata["measurement_basis"],
            "placement": metadata["placement"],
            "jsr_cycles_per_call": jsr_cycles, "budget_cycles": budget,
            "frames": frame_count, "calls": len(calls),
            "total_math_cycles": sum(frame_costs),
            "mean_frame_math_cycles": round(sum(frame_costs) / frame_count, 3),
            "p95_frame_math_cycles": nearest_rank(frame_costs, 95),
            "peak_frame": peak, "peak_frame_math_cycles": frame_costs[peak],
            "peak_frame_math_headroom_cycles": budget - frame_costs[peak],
            "over_budget_frames": sum(c > budget for c in frame_costs),
            "peak_hotspots": hottest, "operations": operations,
            "frame_math_cycles": frame_costs,
            "qualification": "Measured math public calls plus JSR; excludes input stores, IRQ, VIC, REU DMA and other frame work"}


def compare_calls(before: list[Call], after: list[Call], bmeta: dict, ameta: dict) -> None:
    if bmeta["measurement_basis"] != ameta["measurement_basis"] or bmeta["placement"] != ameta["placement"]:
        raise ValueError("Cannot compare differing timing bases or placements")
    b, a = {c.key for c in before}, {c.key for c in after}
    if b != a:
        raise ValueError(f"Paired traces require identical calls/inputs/frames: missing={len(b-a)} extra={len(a-b)}")


def analyze(baseline_path: Path, candidate_path: Path | None = None, *,
            frame_count: int | None = None, budget: int = PAL_FRAME_CYCLES,
            jsr_cycles: int = 6) -> dict:
    baseline, bm = load_trace(baseline_path)
    if candidate_path is None:
        return {"baseline": score(baseline, bm, frame_count=frame_count,
                                  budget=budget, jsr_cycles=jsr_cycles)}
    candidate, cm = load_trace(candidate_path)
    compare_calls(baseline, candidate, bm, cm)
    count = (frame_count if frame_count is not None
             else max(max(c.frame for c in baseline), max(c.frame for c in candidate)) + 1)
    before = score(baseline, bm, frame_count=count, budget=budget, jsr_cycles=jsr_cycles)
    after = score(candidate, cm, frame_count=count, budget=budget, jsr_cycles=jsr_cycles)
    before_slots = {c.key: c.cycles for c in baseline}
    after_slots = {c.key: c.cycles for c in candidate}
    frame_savings = [old - new for old, new in zip(
        before["frame_math_cycles"], after["frame_math_cycles"])]
    call_regression = max((after_slots[k] - cost
                           for k, cost in before_slots.items()), default=0)
    return {"baseline": before, "candidate": after,
            "comparison": {"paired_calls": len(baseline),
                           "total_math_cycles_saved": before["total_math_cycles"] - after["total_math_cycles"],
                           "peak_frame_math_cycles_saved": before["peak_frame_math_cycles"] - after["peak_frame_math_cycles"],
                           "peak_frame_changed": before["peak_frame"] != after["peak_frame"],
                           "baseline_peak_frame_cycles_saved": frame_savings[before["peak_frame"]],
                           "regressed_frames": sum(delta < 0 for delta in frame_savings),
                           "max_frame_regression_cycles": max(0, -min(frame_savings)),
                           "max_public_call_regression_cycles": max(0, call_regression),
                           "over_budget_frames_saved": before["over_budget_frames"] - after["over_budget_frames"]}}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--candidate", type=Path)
    p.add_argument("--frame-count", type=int)
    p.add_argument("--budget", type=int, default=PAL_FRAME_CYCLES)
    p.add_argument("--jsr-cycles", type=int, default=6)
    p.add_argument("--out", type=Path, help="optional JSON report")
    args = p.parse_args()
    try:
        report = analyze(args.baseline, args.candidate, frame_count=args.frame_count,
                         budget=args.budget, jsr_cycles=args.jsr_cycles)
    except (OSError, ValueError) as error:
        p.error(str(error))
    result = json.dumps(report, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(result, encoding="utf-8")
    else:
        print(result, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
