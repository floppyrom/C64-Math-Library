#!/usr/bin/env python3
"""Source-only linker for a deliberately small, qualified 16-bit arithmetic subset.

Only published independently relocatable sources are eligible; no full-profile
image, fixed-address source mirror or unverified record is linked.
"""
from __future__ import annotations
import hashlib
import os
import tempfile
import itertools
import json
from pathlib import Path
import re
from mini6502 import Assembler
import selective_atan2 as atan2
import selective_fast_umul8 as fast8
import selective_speed
import selective_isqrt16 as sqrt16

ROOT = Path(__file__).resolve().parents[1]
MODULES = {
    "MATH_UDIV16": {
        "link:biased": {
            "source": "routines/standalone_lab/portable/div_u16_biased.asm",
            "segments": (("KERNEL_CODE", 323),),
            "entry": "FAST_UDIV16_BIASED", "zp": 2, "scratch": 0,
        },
    },
    "MATH_UMUL8": {
        "link:compact-zerozp": {
            "source": "routines/multiply/umul8_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 60),),
            "entry": "FAST_UMUL8_COMPACT", "zp": 0, "scratch": 3,
            "operand_layout": "xyz",
        },
        "link:quarter-square": {
            "source": "routines/multiply/umul8_quartersquare.asm",
            "segments": (("KERNEL_CODE", 73), ("Q_LO", 511), ("Q_HI", 511)),
            "entry": "FAST_UMUL8_QUARTERSQUARE", "zp": 0, "scratch": 2,
            "operand_layout": "xyz", "fast_umul8": True,
        },
    },
    "MATH_UMUL16": {
        "link:compact-zerozp": {
            "source": "routines/multiply/umul16_compact_zerozp.asm",
            "segments": (("KERNEL_CODE", 108),),
            "entry": "FAST_UMUL16_COMPACT", "zp": 0, "scratch": 6,
            "operand_layout": "xyz",
        },
    },
    "MATH_UMOD16": {
        "link:biased": {
            "source": "routines/standalone_lab/portable/mod_u16_biased_carry.asm",
            "segments": (("KERNEL_CODE", 244), ("KERNEL_ADAPTER", 18)),
            "entry": "FAST_UMOD16_PUBLIC", "zp": 2, "scratch": 0,
        },
        "link:direct-zerozp": {
            "source": "routines/standalone_lab/portable/mod_u16_direct_zerozp.asm",
            "segments": (("KERNEL_TABLE", 16), ("KERNEL_CODE", 945),
                         ("KERNEL_ADAPTER", 15)),
            "entry": "FAST_UMOD16_DIRECT_PUBLIC", "zp": 0, "scratch": 2,
        },
    },
    "MATH_UDIV32_32": {
        "link:zptail": {
            "source": "routines/standalone_lab/portable/div_u32_zptail.asm",
            "segments": (("KERNEL_CODE", 325), ("KERNEL_AUX", 219)),
            "entry": "FAST_UDIV32_PUBLIC", "zp": 4, "scratch": 0,
        },
        "link:aligned-zerozp": {
            "source": "routines/standalone_lab/portable/div_u32_aligned_nozp.asm",
            "segments": (("KERNEL_CODE", 325), ("KERNEL_AUX", 251)),
            "entry": "FAST_UDIV32_PUBLIC", "zp": 0, "scratch": 4,
        },
    },
    "MATH_ATAN2_8": {
        "link:compact": {
            "source": "routines/atan2/atan2_compact_opt.asm",
            "segments": (("KERNEL_CODE", 94), ("LOGTAB", 256),
                         ("ATANTAB", 256)),
            "entry": "atan2", "zp": 0, "scratch": 0, "atan2": "compact",
        },
        "link:sum-fast": {
            "source": "routines/atan2/atan2_sum_fast.asm",
            "segments": (("KERNEL_CODE", 85), ("LOGX", 256),
                         ("LOGY", 256), ("QPOS", 256), ("QNEG", 256)),
            "entry": "atan2", "zp": 0, "scratch": 0, "atan2": "sum-fast",
        },
    },
    "MATH_ISQRT16": {
        "link:square-table": {
            "source": "routines/roots/isqrt16_square_table.asm",
            "segments": (("KERNEL_CODE", 38), ("SQ_LO", 256),
                         ("SQ_HI", 256), ("SEED", 256)),
            "entry": "FAST_ISQRT16_TABLE", "zp": 0, "scratch": 0,
            "isqrt16": True, "operand_layout": "nz",
            "provenance": "V1/V2/V5 16-bit square-lookup kernel; tables regenerated",
        },
    },
    "MATH_UMOD32_32": {
        "link:aligned-zerozp": {
            "source": "routines/standalone_lab/portable/mod_u32_aligned_carry.asm",
            "segments": (("KERNEL_CODE", 250), ("KERNEL_AUX", 225),
                         ("KERNEL_ADAPTER", 21)),
            "entry": "FAST_UMOD32_ALIGNED_PUBLIC", "zp": 0, "scratch": 4,
        },
    },
}

class LinkError(ValueError):
    pass


def available_variants(root=ROOT):
    result = {}
    for api, variants in MODULES.items():
        result[api] = []
        for ident, mod in variants.items():
            result[api].append({
                "id": ident, "kind": "selective-source-module",
                "build_targets": ["c64"],
                "source_path": mod["source"],
                "source_sha256": hashlib.sha256(
                    (root / mod["source"]).read_bytes()).hexdigest(),
                "dependency_sha256": ({
                    "routines/atan2/tables.py": hashlib.sha256(
                        (root / "routines/atan2/tables.py").read_bytes()).hexdigest()
                } if "atan2" in mod else {
                    "tools/selective_fast_umul8.py": hashlib.sha256(
                        (root / "tools/selective_fast_umul8.py").read_bytes()).hexdigest()
                } if mod.get("fast_umul8") else {
                    "tools/selective_isqrt16.py": hashlib.sha256(
                        (root / "tools/selective_isqrt16.py").read_bytes()).hexdigest()
                } if mod.get("isqrt16") else {}),
                "historical_provenance": mod.get("provenance"),
                "mean_cycles_reported": "",
                "zp_bytes_reported": mod["zp"],
                "stack_page_bytes_reported": 0,
                "validation_path": ("tools/test_selective_fast_umul8.py"
                                    if mod.get("fast_umul8") else
                                    "tools/test_selective_multiply.py"
                                    if mod.get("operand_layout") == "xyz" else
                          "V1-family 38-byte lookup kernel; three generated 256-byte tables, no ZP"
                          if mod.get("isqrt16") else
                                  "extracted square-lookup kernel; CPU/native qualification pending"
                                  if mod.get("isqrt16") else
                                    "tools/test_selective_isqrt16.py"
                                    if mod.get("isqrt16") else
                                    "routines/atan2/validate_optimized.py"
                                    if "atan2" in mod else
                                    "routines/standalone_lab/portable/verify.py"),
                "qualification": ("experimental new compact source; CPU/native validation pending"
                                  if mod.get("operand_layout") == "xyz" else
                                  "existing portable source; selective mixed-call validation pending"),
                "notes": ("73-byte quarter-square 8x8 code and 1022 exact table bytes; 2 RAM scratch, 0 ZP"
                          if mod.get("fast_umul8") else
                          "Compact portable shift-add multiply; not performance-ranked against table variants"
                          if mod.get("operand_layout") == "xyz" else
                          "Complete page-aligned ATAN2 lookup tables, exhaustive stock-C64 phase certification"
                          if "atan2" in mod else
                          "Standalone source with checked public carry semantics"),
                "resources_reported": {
                    "code_and_table_bytes": sum(s for _, s in mod["segments"]),
                    "scratch_bytes": mod["scratch"],
                },
                "selective_link_ready": True,
            })
    return result


def address(value, name):
    if isinstance(value, str):
        try:
            value = int(value[1:], 16) if value.startswith("$") else int(value, 0)
        except ValueError as e:
            raise LinkError(name + ": invalid address") from e
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 65535:
        raise LinkError(name + ": invalid 16-bit address")
    return value


def region(name, start, count, zp=False):
    end = start + count - 1
    if count <= 0 or start < 0 or end > (255 if zp else 65535):
        raise LinkError(name + ": region exceeds address space")
    if zp:
        if start < 2:
            raise LinkError(name + ": 6510 processor port collision")
    else:
        if start <= 0x01ff:
            raise LinkError(name + ": overlaps system zero/stack page")
        if start <= 0xdfff and end >= 0xd000:
            raise LinkError(name + ": overlaps I/O region")
        if start <= 0xbfff and end >= 0xa000:
            raise LinkError(name + ": BASIC ROM RAM underlay not supported")
        if end >= 0xe000:
            raise LinkError(name + ": KERNAL ROM RAM underlay not supported")
    return (name, start, end)


def check_nonoverlap(regions):
    for i, (name, start, end) in enumerate(regions):
        for other, a, b in regions[i+1:]:
            if max(start, a) <= min(end, b):
                raise LinkError(name + " overlaps " + other)


def custom_reserved(data, key, zp=False):
    raw = data.get(key, [])
    if not isinstance(raw, list):
        raise LinkError(key + ": expected a list")
    result = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict) or "start" not in item or "end" not in item:
            raise LinkError(key + ": expected objects with start/end")
        first = address(item["start"], key + ".start")
        last = address(item["end"], key + ".end")
        if not first <= last <= (255 if zp else 65535):
            raise LinkError(key + ": inverted or out-of-range reservation")
        name = item.get("name", "reserved_" + str(i))
        if not isinstance(name, str) or not name.strip():
            raise LinkError(key + ": invalid reservation label")
        result.append((name, first, last))
    return result


def projected_end(start, items):
    """Actual compact PRG span, including required ATAN2 page alignment."""
    cursor = start
    for _, _, mod in items:
        if "atan2" in mod:
            _, cursor = atan2.layout(mod["atan2"], cursor)
        elif mod.get("isqrt16"):
            _, cursor = sqrt16.layout(cursor)
        else:
            cursor += sum(length for _, length in mod["segments"])
    return cursor


def place_modules(items, start):
    """Minimize ATAN2 alignment waste over all attainable modulo-256 offsets.

    One table-aligned module is currently supported. Ordinary kernels have
    unconstrained placement. A 256-state subset-sum DP identifies the globally
    minimum padding at the aligned module's code/table boundary. This remains
    O(256 * number_of_modules), not factorial when the catalog expands.
    """
    aligned = [item for item in items if "atan2" in item[2] or item[2].get("isqrt16")]
    ordinary = [item for item in items if "atan2" not in item[2] and not item[2].get("isqrt16")]
    if not aligned:
        return ordinary
    if len(aligned) != 1:
        # Deterministic conservative layout for multiple table-aligned kernels.
        # Exact span is still budgeted; optimal multi-aligned ordering is future work.
        return ordinary + sorted(aligned, key=lambda item: item[0])
    atan = aligned[0]
    code_bytes = (atan2.KINDS[atan[2]["atan2"]]["code_bytes"]
                  if "atan2" in atan[2] else sqrt16.CODE_BYTES)
    # Track one deterministic set of indices per possible prefix address.
    # Item order remains stable within the selected prefix and suffix.
    states = {start % 256: ()}
    for i, item in enumerate(ordinary):
        nbytes = sum(length for _, length in item[2]["segments"])
        expanded = dict(states)
        for residue, indices in states.items():
            new_residue = (residue + nbytes) % 256
            candidate = indices + (i,)
            if (new_residue not in expanded or
                    candidate < expanded[new_residue]):
                expanded[new_residue] = candidate
        states = expanded
    best = min(states, key=lambda residue: (
        -(residue + code_bytes) % 256, states[residue]))
    before_indices = set(states[best])
    before = [item for i, item in enumerate(ordinary) if i in before_indices]
    after = [item for i, item in enumerate(ordinary) if i not in before_indices]
    return before + [atan] + after

def pareto_resource_variants(variants):
    """Prune memory-dominated variants only for automatic selection.

    An algorithm using no more code/table bytes, scratch RAM, or zero page
    always has a memory layout no worse after page-padding optimization.
    Performance ranking is intentionally outside this resource-only rule.
    """
    candidates = list(sorted(variants.items()))
    sizes = {
        key: (sum(length for _, length in spec["segments"]),
              spec["scratch"], spec["zp"])
        for key, spec in candidates
    }
    # Pruning is sound only across identical layout classes. All current
    # ATAN2 data segments are full pages, but future emitters may impose
    # other code/table alignment or placement constraints.
    layout_classes = {
        key: (("page-aligned", len(spec["segments"]) - 1)
              if "atan2" in spec or spec.get("isqrt16") else ("contiguous", 0))
        for key, spec in candidates
    }
    keep = {}
    for key, variant in candidates:
        mine = sizes[key]
        dominated = any(
            other != key and
            layout_classes[other] == layout_classes[key] and
            all(a <= b for a, b in zip(sizes[other], mine)) and
            (any(a < b for a, b in zip(sizes[other], mine)) or other < key)
            for other, _ in candidates
        )
        if not dominated:
            keep[key] = variant
    return keep


def choose(names, pins, objective, zp_budget, ram_budget=None, code_base=0x8000, cycle_metrics=None):
    """Optimize *the whole selection*, sharing nonreentrant scratch ownership."""
    options = []
    for api in names:
        if api not in MODULES:
            raise LinkError(api + ": no qualified selective source yet")
        variants = MODULES[api]
        if api in pins:
            if pins[api] not in variants:
                raise LinkError(api + ": selected variant is not link-ready")
            # An expert pin can select a memory-dominated algorithm for other
            # benefits (e.g. ATAN2 sum-fast's published speed improvement).
            variants = {pins[api]: variants[pins[api]]}
        elif objective != "speed":
            variants = pareto_resource_variants(variants)
        options.append([(api, ident, mod) for ident, mod in sorted(variants.items())])

    if objective == "speed" and not cycle_metrics:
        raise LinkError("Speed selection requires an authenticated same-corpus cycle model")
    best_score = None
    best = None
    for combination in itertools.product(*options):
        zp = max(mod["zp"] for _, _, mod in combination)
        scratch = max(mod["scratch"] for _, _, mod in combination)
        code = projected_end(code_base, place_modules(combination, code_base)) - code_base
        ram = code + 32 + scratch
        if zp_budget is not None and zp > zp_budget:
            continue
        if ram_budget is not None and ram > ram_budget:
            continue
        # Never combine unrelated benchmark corpora into a fake speed score.
        if objective == "speed":
            try:
                measured_cycles = sum(
                    cycle_metrics[api][ident] for api, ident, _ in combination)
            except KeyError as exc:
                raise LinkError("Selected variants lack a comparable cycle model") from exc
            metric = (measured_cycles, ram, zp)
        elif objective == "zp":
            metric = (zp, ram, code)
        elif objective == "balanced":
            metric = (ram + 8 * zp, ram, zp)
        else:  # size, exactly measured RAM footprint
            metric = (ram, zp, code)
        fingerprint = tuple(ident for _, ident, _ in combination)
        score = (*metric, fingerprint)
        if best_score is None or score < best_score:
            best_score = score
            best = {api: (ident, mod) for api, ident, mod in combination}
    if best is None:
        raise LinkError("No certified variant combination fits RAM/ZP budgets")
    return best

def relocate_source(mod, locations, root):
    src = (root / mod["source"]).read_text(encoding="utf-8")
    used = {k for k, _ in mod["segments"]}
    if mod.get("operand_layout") == "xyz":
        used |= {"INPUT_X", "INPUT_Y", "OUTPUT_Z"}
    else:
        used |= {"INPUT_NUM", "INPUT_DIV", "OUTPUT_QUOT", "OUTPUT_REM"}
    if mod["zp"]:
        used.add("TEMP_ZP")
    if mod["scratch"]:
        used.add("TEMP_RAM")
    for key in used:
        if key not in locations:
            raise LinkError("Missing address symbol: " + key)
        pattern = r"(?m)^" + re.escape(key) + r"\s*=\s*\$[0-9a-fA-F]+\s*$"
        src, n = re.subn(pattern, key + " = $%04X" % locations[key], src)
        if n != 1:
            raise LinkError(mod["source"] + ": cannot safely patch " + key)
    return src


def build(plan, outdir, memory=None, root=ROOT):
    if plan.get("schema") != "math-selection-plan-v2":
        raise LinkError("Unsupported selection plan schema; regenerate with current math_builder")
    if plan["target"] != "c64":
        raise LinkError("No qualified selective modules for requested hardware")
    names = [op["api"] for op in plan["operations"]]
    if not names or len(set(names)) != len(names):
        raise LinkError("Selected operations must be nonempty and unique")
    pins = {op["api"]: op["pinned_variant"] for op in plan["operations"]
            if op["pinned_variant"]}
    constraints = plan["constraints"]
    zp_budget = constraints["max_zp_bytes"]
    ram_budget = constraints["max_ram_bytes"]
    memory = memory or {}
    if not isinstance(memory, dict):
        raise LinkError("memory: expected a map")
    supported = {"code_base", "math_io", "zp_base", "scratch_base",
                 "reserved", "zp_reserved"}
    unknown = set(memory) - supported
    if unknown:
        raise LinkError("Unknown memory parameters: " + ", ".join(sorted(unknown)))
    code = address(memory.get("code_base", 0x8000), "code_base")
    io = address(memory.get("math_io", 0xc000), "math_io")
    zb = address(memory.get("zp_base", 0x50), "zp_base")
    sb = address(memory.get("scratch_base", io + 32), "scratch_base")
    cycle_model = None
    per_operation_cycles = None
    if plan["objective"] == "speed":
        if names != ["MATH_UMUL8"]:
            raise LinkError(
                "Measured automatic speed selection currently supports UMUL8 alone; "
                "other operations require comparable certified cycle corpora")
        try:
            cycle_model = selective_speed.bench_umul8(
                MODULES["MATH_UMUL8"], code, io, sb, root)
        except (ValueError, OSError, RuntimeError) as exc:
            raise LinkError("UMUL8 cycle-model measurement failed: " + str(exc)) from exc
        per_operation_cycles = {"MATH_UMUL8": cycle_model["mean_cycles"]}
    modules = choose(names, pins, plan["objective"], zp_budget, ram_budget,
                     code_base=code, cycle_metrics=per_operation_cycles)
    zp_bytes = max(mod["zp"] for _, mod in modules.values())
    scratch = max(mod["scratch"] for _, mod in modules.values())
    build_order = place_modules([(api, ident, mod)
                                 for api, (ident, mod) in modules.items()], code)
    size = projected_end(code, build_order) - code
    occupied_ram = size + 32 + scratch
    if zp_budget is not None and zp_bytes > zp_budget:
        raise LinkError("ZP budget too small")
    if ram_budget is not None and occupied_ram > ram_budget:
        raise LinkError("RAM budget too small (including alignment padding and I/O)")
    blocks = [region("code", code, size), region("public I/O", io, 32)]
    if scratch:
        blocks.append(region("scratch", sb, scratch))
    main_reserved = custom_reserved(memory, "reserved")
    zp_reserved = custom_reserved(memory, "zp_reserved", zp=True)
    check_nonoverlap(blocks + main_reserved)
    if zp_bytes:
        check_nonoverlap([region("scratch ZP", zb, zp_bytes, zp=True)] + zp_reserved)

    constants = {
        "INPUT_NUM": io + 16, "INPUT_DIV": io + 20,
        "OUTPUT_QUOT": io + 24, "OUTPUT_REM": io + 28,
        "INPUT_X": io, "INPUT_Y": io + 4, "OUTPUT_Z": io + 8,
    }
    if zp_bytes:
        constants["TEMP_ZP"] = zb
    if scratch:
        constants["TEMP_RAM"] = sb
    binary = {}
    entries, detail = {}, []
    pc = code
    for api, ident, module in build_order:
        operation = next(op for op in plan["operations"] if op["api"] == api)
        link_sources = [v for v in operation["available_source_variants"]
                        if v["id"] == ident and v["selective_link_ready"]]
        if len(link_sources) != 1:
            raise LinkError(api + ": selected source not authorized by plan")
        source_path = (root / module["source"]).resolve()
        if not source_path.is_relative_to(root.resolve()):
            raise LinkError(api + ": source escapes repository")
        exact_digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if exact_digest != link_sources[0]["source_sha256"]:
            raise LinkError(api + ": source changed since selection plan")
        dep_provenance = []
        for dep, digest in link_sources[0].get("dependency_sha256", {}).items():
            dep_path = (root / dep).resolve()
            if not dep_path.is_relative_to(root.resolve()) or not dep_path.is_file():
                raise LinkError(api + ": missing/unsafe source dependency")
            actual_dep_sha = hashlib.sha256(dep_path.read_bytes()).hexdigest()
            if actual_dep_sha != digest:
                raise LinkError(api + ": source dependency changed since selection plan")
            dep_provenance.append({"source_path": dep, "sha256": actual_dep_sha})
        if "atan2" in module and [x["source_path"] for x in dep_provenance] != [
                "routines/atan2/tables.py"]:
            raise LinkError(api + ": ATAN2 table generator provenance missing")
        if module.get("fast_umul8") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_fast_umul8.py"]:
            raise LinkError(api + ": quarter-square table generator provenance missing")
        if module.get("isqrt16") and [x["source_path"] for x in dep_provenance] != [
                "tools/selective_isqrt16.py"]:
            raise LinkError(api + ": integer-root table generator provenance missing")
        locations = dict(constants)
        expected = set()
        ranges = []
        try:
            if "atan2" in module or module.get("fast_umul8") or module.get("isqrt16"):
                if "atan2" in module:
                    machine, entry, ranges, end = atan2.assemble(
                        module["atan2"], pc, io, root)
                elif module.get("isqrt16"):
                    machine, entry, ranges, end = sqrt16.assemble(pc, io, root)
                else:
                    machine, entry, ranges, end = fast8.assemble(pc, io, sb, root)
                expected = set()
                for seg in ranges:
                    start = int(seg["start"][1:], 16)
                    expected.update(range(start, start + seg["bytes"]))
                labels = {module["entry"]: entry}
                pc = end
            else:
                for seg, length in module["segments"]:
                    locations[seg] = pc
                    ranges.append({"name": seg, "start": "$%04X" % pc, "bytes": length})
                    expected.update(range(pc, pc + length))
                    pc += length
                machine, labels, _ = Assembler().assemble(
                    relocate_source(module, locations, root))
        except Exception as e:
            raise LinkError("Assembly failed for " + api + ": " + str(e)) from e
        if set(machine) != expected:
            raise LinkError(api + ": assembled segment sizes differ from contract")
        if module["entry"] not in labels or labels[module["entry"]] not in machine:
            raise LinkError(api + ": entry label not in assembled image")
        if set(machine) & set(binary):
            raise LinkError(api + ": module overlaps existing code")
        binary.update(machine)
        entries[api] = labels[module["entry"]]
        detail.append({
            "api": api, "variant": ident, "entry": "$%04X" % entries[api],
            "dependencies": dep_provenance, "scratch_lifetime": "exclusive_call",
            "source": module["source"],
            "sha256": hashlib.sha256((root / module["source"]).read_bytes()).hexdigest(),
            "segments": ranges, "zp_bytes": module["zp"], "scratch_bytes": module["scratch"],
            "operand_layout": module.get("operand_layout", "ndqr"),
        })
    if pc != code + size:
        raise LinkError("Incorrect linked image span")
    # ATAN2 lookup pages need page alignment. Gaps are explicit zero-filled
    # PRG padding and are counted in RAM usage, not silently reusable memory.
    padding = size - len(binary)
    if padding < 0 or any(a < code or a >= pc for a in binary):
        raise LinkError("Linked image outside declared span")
    prg = bytes((code & 255, code >> 8)) + bytes(
        binary.get(addr, 0) for addr in range(code, code + size))
    exports = [
        "; Generated selective C64 math library (CLD required; non-reentrant)",
        "; All public inputs preserved; A/X/Y and processor flags may be volatile.",
        "; DIV/MOD: unsigned N/D in MATH_N/MATH_D, quotient/remainder Q/R;",
        "; carry set iff D=0. UMOD leaves quotient untouched.",
        "; UMUL8: unsigned 8-bit MATH_X/Y => unsigned 16-bit MATH_Z;",
        "; UMUL16: unsigned 16-bit MATH_X/Y => unsigned 32-bit MATH_Z;",
        "; ISQRT16: unsigned MATH_N 16-bit => floor(sqrt(N)) in MATH_Z 16-bit, C=0.",
        "; ATAN2_8: signed 8-bit MATH_X/Y low bytes => phase MATH_Z low byte",
        "; and A, C clear. Initial carry ignored.",
        "MATH_X = $%04X" % io, "MATH_Y = $%04X" % (io + 4),
        "MATH_Z = $%04X" % (io + 8),
        "MATH_N = $%04X" % (io + 16), "MATH_D = $%04X" % (io + 20),
        "MATH_Q = $%04X" % (io + 24), "MATH_R = $%04X" % (io + 28),
    ]
    exports += [api + " = $%04X" % addr for api, addr in entries.items()]
    # Preserve the stable typed ABI aliases when generating a tiny library.
    for operation in plan["operations"]:
        canonical = operation["canonical_name"]
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", canonical):
            raise LinkError("Unsafe typed operation alias: " + canonical)
        exports.append(canonical + " = " + operation["api"])
    toolchain_paths = ("tools/math_builder.py", "tools/selective_linker.py",
                       "tools/selective_atan2.py", "tools/selective_fast_umul8.py",
                       "tools/selective_speed.py", "tools/selective_isqrt16.py",
                       "tools/mini6502.py")
    toolchain_hashes = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in toolchain_paths
    }
    manifest = {
        "schema": "c64-math-selective-binary-v1",
        "toolchain_sha256": toolchain_hashes,
        "status": "selective_binary_emitted",
        "target": "c64",
        "selection_objective": plan["objective"],
        "selection_basis": ("same-corpus measured CPU-model cycles for UMUL8"
                            if cycle_model else
                            "global code/RAM/ZP resource optimization; cycle-speed not certified"),
        "cycle_model_benchmark": cycle_model,
        "operations": detail,
        "link_order": [api for api, _, _ in build_order],
        "link_exports": sorted(entries),
        "typed_exports": sorted(x["canonical_name"] for x in plan["operations"]),
        "resource_use": {
            "code_and_tables_bytes": len(binary), "image_span_bytes": size,
            "alignment_padding_bytes": padding, "public_io_bytes": 32,
            "private_ram_scratch_bytes": scratch,
            "main_ram_total_bytes": occupied_ram, "zero_page_bytes": zp_bytes,
            "persistent_stack_page_bytes": 0,
        },
        "memory_map": {
            "code_start": "$%04X" % code,
            "code_end": "$%04X" % (pc - 1),
            "math_io_start": "$%04X" % io,
            "scratch_start": "$%04X" % sb if scratch else None,
            "zp_start": "$%02X" % zb if zp_bytes else None,
            "user_reserved": [dict(name=n, start="$%04X" % a, end="$%04X" % b)
                              for n, a, b in main_reserved],
            "user_zp_reserved": [dict(name=n, start="$%02X" % a, end="$%02X" % b)
                                 for n, a, b in zp_reserved],
        },
        "nonreentrant": True, "rom_underlay_enabled": False,
        "prg_sha256": hashlib.sha256(prg).hexdigest(),
        "note": "New selective binaries require full CPU/native qualification before general release.",
    }
    # All assembly, resource and provenance checks must succeed before any
    # publication. Stage all outputs first; commit the manifest last, as a
    # completion marker for consumers of this experimental build directory.
    outdir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".math_stage_", dir=outdir) as temp:
        stage = Path(temp)
        (stage / "math_selective.prg").write_bytes(prg)
        (stage / "math_api.inc").write_text("\n".join(exports) + "\n")
        (stage / "selective_manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n")
        if hashlib.sha256((stage / "math_selective.prg").read_bytes()).hexdigest() != manifest["prg_sha256"]:
            raise LinkError("Staged PRG checksum mismatch")
        for name in ("math_selective.prg", "math_api.inc",
                     "selective_manifest.json"):
            os.replace(stage / name, outdir / name)
    return manifest
