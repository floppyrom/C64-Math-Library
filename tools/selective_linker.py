#!/usr/bin/env python3
"""Source-only linker for a deliberately small, qualified 16-bit arithmetic subset.

Only published independently relocatable sources are eligible; no full-profile
image, fixed-address source mirror or unverified record is linked.
"""
from __future__ import annotations
import hashlib
import itertools
import json
from pathlib import Path
import re
from mini6502 import Assembler

ROOT = Path(__file__).resolve().parents[1]
MODULES = {
    "MATH_UDIV16": {
        "link:biased": {
            "source": "routines/standalone_lab/portable/div_u16_biased.asm",
            "segments": (("KERNEL_CODE", 323),),
            "entry": "FAST_UDIV16_BIASED", "zp": 2, "scratch": 0,
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
                "source_path": mod["source"],
                "source_sha256": hashlib.sha256(
                    (root / mod["source"]).read_bytes()).hexdigest(),
                "historical_provenance": None,
                "mean_cycles_reported": "",
                "zp_bytes_reported": mod["zp"],
                "stack_page_bytes_reported": 0,
                "validation_path": "routines/standalone_lab/portable/verify.py",
                "qualification": "existing portable source; selective mixed-call testing",
                "notes": "Standalone source with checked public carry semantics",
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


def choose(names, pins, objective, zp_budget, ram_budget=None):
    """Optimize *the whole selection*, sharing nonreentrant scratch ownership."""
    options = []
    for api in names:
        if api not in MODULES:
            raise LinkError(api + ": no qualified selective source yet")
        variants = MODULES[api]
        if api in pins:
            if pins[api] not in variants:
                raise LinkError(api + ": selected variant is not link-ready")
            variants = {pins[api]: variants[pins[api]]}
        options.append([(api, ident, mod) for ident, mod in sorted(variants.items())])

    if objective == "speed":
        raise LinkError("Speed-optimized selective builds need verified same-corpus cycle measurements; choose size/zp/balanced or pin a variant")
    best_score = None
    best = None
    for combination in itertools.product(*options):
        zp = max(mod["zp"] for _, _, mod in combination)
        scratch = max(mod["scratch"] for _, _, mod in combination)
        code = sum(n for _, _, mod in combination for _, n in mod["segments"])
        ram = code + 32 + scratch
        if zp_budget is not None and zp > zp_budget:
            continue
        if ram_budget is not None and ram > ram_budget:
            continue
        # Never combine unrelated benchmark corpora into a fake speed score.
        if objective == "zp":
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
    if plan["target"] != "c64":
        raise LinkError("No qualified selective modules for requested hardware")
    names = [op["api"] for op in plan["operations"]]
    if not names:
        raise LinkError("No selected operations")
    pins = {op["api"]: op["pinned_variant"] for op in plan["operations"]
            if op["pinned_variant"]}
    constraints = plan["constraints"]
    zp_budget = constraints["max_zp_bytes"]
    ram_budget = constraints["max_ram_bytes"]
    modules = choose(names, pins, plan["objective"], zp_budget, ram_budget)
    zp_bytes = max(mod["zp"] for _, mod in modules.values())
    scratch = max(mod["scratch"] for _, mod in modules.values())
    size = sum(length for _, mod in modules.values() for _, length in mod["segments"])
    occupied_ram = size + 32 + scratch
    if zp_budget is not None and zp_bytes > zp_budget:
        raise LinkError("ZP budget too small")
    if ram_budget is not None and occupied_ram > ram_budget:
        raise LinkError("RAM budget too small (includes public 32-byte I/O)")

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
    }
    if zp_bytes:
        constants["TEMP_ZP"] = zb
    if scratch:
        constants["TEMP_RAM"] = sb
    binary = {}
    entries, detail = {}, []
    pc = code
    for api in names:
        ident, module = modules[api]
        locations = dict(constants)
        expected = set()
        ranges = []
        for seg, length in module["segments"]:
            locations[seg] = pc
            ranges.append({"name": seg, "start": "$%04X" % pc, "bytes": length})
            expected.update(range(pc, pc + length))
            pc += length
        try:
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
            "source": module["source"],
            "sha256": hashlib.sha256((root / module["source"]).read_bytes()).hexdigest(),
            "segments": ranges, "zp_bytes": module["zp"], "scratch_bytes": module["scratch"],
        })
    if set(binary) != set(range(code, code + size)):
        raise LinkError("Linked code is not compact and contiguous")
    prg = bytes((code & 255, code >> 8)) + bytes(
        binary[addr] for addr in range(code, code + size))
    exports = [
        "; Generated selective C64 math library (CLD required; non-reentrant)",
        "; Registers volatile; N/D preserved; carry set iff divisor zero",
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
    manifest = {
        "schema": "c64-math-selective-binary-v1",
        "status": "selective_binary_emitted",
        "target": "c64",
        "selection_objective": plan["objective"],
        "selection_basis": "global code/RAM/ZP resource optimization; cycle-speed not certified",
        "operations": detail,
        "link_exports": sorted(entries),
        "typed_exports": sorted(x["canonical_name"] for x in plan["operations"]),
        "resource_use": {
            "code_and_tables_bytes": size, "public_io_bytes": 32,
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
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "math_selective.prg").write_bytes(prg)
    (outdir / "math_api.inc").write_text("\n".join(exports) + "\n")
    (outdir / "selective_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    return manifest
