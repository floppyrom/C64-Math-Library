#!/usr/bin/env python3
"""Generate and certify the logarithmic ratio tables using only Python's stdlib.

L(v) = floor(127.85 log2(v) + 0.5) - 895; a normalized major byte always has
0 <= L(major) < 128, so its high byte is implicit. Four pages map a log
difference to one of 256 component pairs. The pairs are chosen from the
intersection of every mapped cell's angular and component error intervals.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from normalize_model import reduced_cells

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "validation/normalize/LOG_RATIO_TABLE_DESIGN.json"
CERT = ROOT / "validation/normalize/LOG_RATIO_FULL_DOMAIN_PRECISION_CERTIFICATE.json"


def design_tables():
    logs = [math.floor(127.85 * math.log2(max(1, v)) + 0.5) - 895 for v in range(256)]
    zero = 1024
    low, high = [999.0] * 1025, [-999.0] * 1025
    cells = 0
    for major, minor, lo, hi in reduced_cells():
        index = logs[major] - logs[minor] if minor else zero
        assert 0 <= index <= zero
        low[index] = min(low[index], lo)
        high[index] = max(high[index], hi)
        cells += 1
    assert cells == 723073
    active = [i for i in range(1025) if low[i] <= high[i]]
    amin, amax = {}, {}
    for i in active:
        # Reserve rounding margin below the public 0.3621-degree / 202-LSB limits.
        amin[i], amax[i] = high[i] - .3614, low[i] + .3614
        cl, ch = math.cos(math.radians(low[i])), math.cos(math.radians(high[i]))
        sl, sh = math.sin(math.radians(low[i])), math.sin(math.radians(high[i]))
        amin[i] = max(amin[i], math.degrees(math.acos(min(1, ch + 200.5 / 32767))),
                      math.degrees(math.asin(max(0, sh - 200.5 / 32767))))
        amax[i] = min(amax[i], math.degrees(math.acos(max(0, cl - 200.5 / 32767))),
                      math.degrees(math.asin(min(1, sl + 200.5 / 32767))))
        assert amin[i] <= amax[i], i
    # Optimal interval stabbing: every component direction must hit its cells'
    # allowed angle intervals. Split the widest remaining groups to use 256 codes.
    groups, left = [], set(active)
    while left:
        point = min(amax[i] for i in left)
        group = sorted((i for i in left if amin[i] <= point), key=lambda i: ((low[i] + high[i]) / 2, i))
        groups.append(group)
        left.difference_update(group)
    minimum_groups = len(groups)
    assert minimum_groups <= 256
    while len(groups) < 256:
        choices = [(max(high[i] for i in g) - min(low[i] for i in g), j)
                   for j, g in enumerate(groups) if len(g) > 1]
        _, j = max(choices)
        g = groups[j]
        groups[j:j + 1] = [g[:len(g) // 2], g[len(g) // 2:]]
    comps, indices = [], [0] * 1025
    max_angle = max_component = max_length = 0.0
    for j, g in enumerate(groups):
        a, z = max(amin[i] for i in g), min(amax[i] for i in g)
        angle = max(a, min(z, (max(high[i] for i in g) + min(low[i] for i in g)) / 2))
        pair = [round(32767 * math.cos(math.radians(angle))), round(32767 * math.sin(math.radians(angle)))]
        comps.append(pair)
        actual = math.degrees(math.atan2(pair[1], pair[0]))
        max_length = max(max_length, abs(math.hypot(*pair) / 32767 - 1))
        for i in g:
            indices[i] = j
            for endpoint in (low[i], high[i]):
                max_angle = max(max_angle, abs(actual - endpoint))
                r = math.radians(endpoint)
                max_component = max(max_component, abs(pair[0] - 32767 * math.cos(r)),
                                    abs(pair[1] - 32767 * math.sin(r)))
    assert indices[zero] == 0
    assert all(a > 0 and b > 0 for a, b in comps)  # sign tails return C=0
    assert max_angle <= .3621 and math.ceil(max_component) <= 202
    data = {"scale": 127.85, "log_bias": 895, "log_rounding": "floor(value+0.5)",
            "logs": logs, "indices": indices[:1024],
            "zero_index": indices[zero], "comps": comps}
    certificate = {"status": "PASS", "profiles": ["v1_balanced", "v2_pareto_fast", "v5_hybrid_lowzp"],
                   "mapping": "index=LUT[L(major)-L(minor)]; minor=0 uses zero_index; L(v)=floor(127.85*log2(v)+0.5)-895",
                   "cells": cells, "component_pairs": len(comps), "minimum_groups": minimum_groups,
                   "max_angle_deg": max_angle, "max_component_float": max_component,
                   "max_component_ceil": math.ceil(max_component), "max_relative_unit_length_error": max_length,
                   "angular_contract_deg": .3621, "component_contract_lsb": 202}
    return data, certificate


def plane(address, values):
    lines = [f"* = {address}"]
    for i in range(0, len(values), 16):
        lines.append("    !byte " + ", ".join(f"${v & 255:02X}" for v in values[i:i + 16]))
    return "\n".join(lines) + "\n"


def assembly_tables(profile, data):
    if profile in ("v3_reu_512k", "v4_reu_16m"):
        old = json.loads((ROOT / "validation/normalize/COMPONENT_TABLE_DESIGN.json").read_text())
        comps = old["comps"]
        addresses = [f"REG_TABLE+${offset:04X}" for offset in (0x800, 0x900, 0xa00, 0xb00)]
        text = "; Existing exact-ratio Q1.15 component planes, generated from COMPONENT_TABLE_DESIGN.json.\n"
    else:
        comps = data["comps"]
        lowzp = profile != "v2_pareto_fast"
        addresses = (["REG_TABLE", "REG_TABLE+$0100", "REG_TABLE+$0200", "REG_TABLE+$0300"] if lowzp else
                     ["REG_LOW+$1400", "REG_LOW+$1700", "REG_KERNEL+$0700", "REG_KERNEL+$0D00"])
        loghigh = "REG_TABLE+$0400" if lowzp else "REG_LOW+$0A00"
        text = "; Generated by tools/generate_normalize_tables.py; certified signed-Q8.8 domain.\n"
        text += "; Four ratio-index pages, one log-low page, one log-high page, four component pages.\n"
        text += plane("REG_LOW", data["indices"])
        text += plane("REG_LOW+$0400", data["logs"])
        text += plane(loghigh, [x >> 8 for x in data["logs"]])
    for i, address in enumerate(addresses):
        text += plane(address, [(v[i // 2] >> (8 * (i % 2))) & 255 for v in comps])
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify reproducibility without writing")
    args = parser.parse_args()
    data, cert = design_tables()
    data_text = json.dumps(data, indent=2) + "\n"
    cert["table_design_sha256"] = hashlib.sha256(data_text.encode()).hexdigest()
    files = {TARGET: data_text, CERT: json.dumps(cert, indent=2) + "\n"}
    for p in ("v1_balanced", "v2_pareto_fast", "v3_reu_512k", "v4_reu_16m", "v5_hybrid_lowzp"):
        files[ROOT / p / "resident/vector/native/vec2_normalize_tables.asm"] = assembly_tables(p, data)
    for path, text in files.items():
        if args.check:
            assert path.read_text() == text, f"stale generated normalizer tables: {path}"
        else:
            path.write_text(text)
    print(f"NORMALIZE TABLES PASS {cert['cells']} cells, {cert['max_angle_deg']:.9f} deg, {cert['max_component_ceil']} LSB")


if __name__ == "__main__":
    main()
