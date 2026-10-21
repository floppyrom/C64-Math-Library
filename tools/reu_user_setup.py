#!/usr/bin/env python3
"""Explicit, fail-closed operation-first Turbo16 REU add-on coordinator.

Builds a **two-PRG project**, not one implicitly accelerated math entry.
Normal MATH_UMUL16 remains a stock-C64 fallback. Only the separate REU
INSTALL/BEGIN/CALL/END entries use REU. The global stock linker is given
the exact REU RAM/ZP reservations *before* choosing its allocations.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import reu_turbo16_standalone_package as reu

IMAGE_RES = {"name":"__math_reu_turbo16_image","start":"$3000","end":"$77FF"}
IO_RES = {"name":"__math_reu_turbo16_io","start":"$C000","end":"$C01F"}
ZP_RES = {"name":"__math_reu_turbo16_zp","start":"$3E","end":"$B7"}
GENERATED = ((IMAGE_RES, "user_reserved"), (IO_RES, "user_reserved"),
             (ZP_RES, "user_zp_reserved"))
ZP_COST = 122
RAM_COST = (reu.LIMIT-reu.BASE)+32


class REUSetupError(ValueError):
    pass


def map_for_stock(original):
    if not isinstance(original, dict):
        raise REUSetupError("Memory config must be an object")
    memory = copy.deepcopy(original)
    for item in memory.get("reserved", []) + memory.get("zp_reserved", []):
        if not isinstance(item, dict) or item.get("name") in {
                x["name"] for x,_ in GENERATED}:
            raise REUSetupError("Application memory reservation collides with a generated REU owner name")
    memory.setdefault("math_io", "$C040")
    memory.setdefault("zp_base", "$B8")
    memory.setdefault("reserved", [])
    memory.setdefault("zp_reserved", [])
    if not isinstance(memory["reserved"], list) or not isinstance(memory["zp_reserved"], list):
        raise REUSetupError("Application reservations must be arrays")
    memory["reserved"].extend((copy.deepcopy(IMAGE_RES),copy.deepcopy(IO_RES)))
    memory["zp_reserved"].append(copy.deepcopy(ZP_RES))
    return memory


def stock_manifest_without_generated_reservations(manifest):
    clean = copy.deepcopy(manifest)
    m = clean["memory_map"]
    for entry, bucket in GENERATED:
        saved = m[bucket]
        actual = [x for x in saved if x.get("name") == entry["name"]]
        if actual != [entry]:
            raise REUSetupError("Global linker did not preserve REU reservation: "+entry["name"])
        m[bucket] = [x for x in saved if x.get("name") != entry["name"]]
    return clean


def _budget(total, extra, name):
    if total is None:
        return None
    if type(total) is not int or total < extra:
        raise REUSetupError("Insufficient "+name+" budget for REU reservation of "+str(extra))
    return total-extra


def qualified_hardware(config):
    if not isinstance(config, dict) or not isinstance(config.get("hardware"), dict):
        raise REUSetupError("Missing explicit hardware.reu.turbo16 configuration")
    if set(config["hardware"]) != {"reu"} or set(config["hardware"]["reu"]) != {"turbo16"}:
        raise REUSetupError("Unknown or unsupported hardware requirements")
    setting = config["hardware"]["reu"]["turbo16"]
    if not isinstance(setting, dict) or set(setting) != {"capacity_kib","bank","reserved_banks"}:
        raise REUSetupError("Invalid Turbo16 hardware selection contract")
    if setting["capacity_kib"] not in (512,16384):
        raise REUSetupError("Turbo16 REU supports 512KiB or 16MiB only")
    if type(setting["bank"]) is not int or type(setting["reserved_banks"]) is not list:
        raise REUSetupError("Invalid Turbo16 REU bank declarations")
    if any(type(b) is not int for b in setting["reserved_banks"]):
        raise REUSetupError("Invalid reserved REU bank")
    if "UMUL16" not in config.get("operations",[]):
        raise REUSetupError("Select UMUL16 to retain the stock-C64 fallback")
    return setting


def install(config, index, plan, folder, linker):
    """Physically reserve REU first, then build both PRGs before publishing."""
    hw = qualified_hardware(config)
    # Never let the normal linker spend bytes owned by the optional overlay.
    constraints = config["constraints"]
    expected_zp = _budget(constraints["max_zp_bytes"], ZP_COST, "ZP")
    expected_ram = _budget(constraints["max_ram_bytes"], RAM_COST, "RAM")
    if (plan["constraints"]["max_zp_bytes"] != expected_zp or
            plan["constraints"]["max_ram_bytes"] != expected_ram):
        raise REUSetupError("Selector must optimize against budgets net of the full REU resources")
    memory = map_for_stock(config.get("memory", {}))
    stock = linker.build(plan, folder, memory=memory)
    checked = stock_manifest_without_generated_reservations(stock)
    reu_manifest, reu_prg = reu.build(
        hw["capacity_kib"], hw["bank"], stock_manifest=checked,
        reserved_reu_banks=hw["reserved_banks"])
    use = stock["resource_use"]
    total_zp = use["zero_page_bytes"] + ZP_COST
    total_ram = use["main_ram_total_bytes"] + RAM_COST
    for key,value in (("max_zp_bytes",total_zp),("max_ram_bytes",total_ram)):
        ceiling = constraints[key]
        if ceiling is not None and value > ceiling:
            raise REUSetupError("Linked stock and Turbo16 REU exceeded "+key)
    project = {
        "schema":"operation-first-turbo16-reu-optin-two-prg-v1",
        "status":"SOURCE_LINKED_REU_OPTIN_NO_IRQ_VIC_OR_TIMING_CERTIFICATE",
        "explicit_reu_optin":True,
        "stock_remains_default":True,
        "hardware":{"reu":{"turbo16":copy.deepcopy(hw)}},
        "stock_prg":"math_selective.prg",
        "reu_prg":"turbo16_reu.prg",
        "load_both_prgs_then_explicitly_call_install":True,
        "stock_prg_sha256":stock["prg_sha256"],
        "reu_prg_sha256":reu_manifest["prg_sha256"],
        "combined_resource_use":{
            "main_ram_total_bytes":total_ram,
            "zero_page_bytes":total_zp,
            "reu_exclusive_bank_count":1,
            "reu_exclusive_bytes":65536,
            "reu_mirror_probe_bytes":reu_manifest["claimed_resources"]["alias_guard_bytes"],
        },
        "reu_entrypoints":reu_manifest["public_exports"],
        "physical_memory_bound_by_stock_linker":True,
        "native_vice_qualified_for_standalone_reu":True,
        "mixed_stock_reu_vic_irq_qualified":False,
        "all_historical_speed_parity_qualified":False,
    }
    (folder/"turbo16_reu.prg").write_bytes(reu_prg)
    (folder/"turbo16_reu_manifest.json").write_text(
        json.dumps(reu_manifest,indent=2,sort_keys=True)+"\n")
    (folder/"math_project_manifest.json").write_text(
        json.dumps(project,indent=2,sort_keys=True)+"\n")
    with (folder/"math_reu_turbo16.inc").open("w") as out:
        out.write("; Optional Turbo16 REU requires runtime INSTALL and guarded batches.\n")
        out.write("MATH_REU_TURBO16_IO = $C000\n")
        for name,value in sorted(reu_manifest["public_exports"].items()):
            out.write("MATH_"+name+" = "+value+"\n")
    if hashlib.sha256((folder/"turbo16_reu.prg").read_bytes()).hexdigest() != project["reu_prg_sha256"]:
        raise REUSetupError("Staged REU PRG SHA mismatch")
    return stock
