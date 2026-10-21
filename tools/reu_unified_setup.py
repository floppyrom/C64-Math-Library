#!/usr/bin/env python3
"""Unified one-service operation-first REU physical allocator and packager.

Turbo16 retains its existing public installation contract. Turbo32 and QS16
are separately source-built modules: never embed a legacy V3/V4 resident PRG.
A single REU service can be selected per project until concurrency has its own
verified cross-service ZP, C64 image and bank allocator.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import reu_turbo32_standalone_package as t32
import reu_qs16_standalone_package as q16

SERVICES={
    "turbo32":{
        "fallback":"UMUL32",
        "zp":(0x0a,0x90),
        "default_zp":"$91",
        "ram":18464,
        "default_bank":{512:4,16384:200},
        "module":t32,
    },
    "qs16":{
        "fallback":"UMUL16",
        "zp":(0x4e,0x5d),
        "default_zp":"$5E",
        "ram":18468,
        "default_bank":{16384:200},
        "module":q16,
    },
}

class UnifiedREUError(ValueError):
    pass


def qualified_hardware(config):
    if config.get("target")!="c64":
        raise UnifiedREUError("REU modules require C64 target")
    r=config.get("hardware",{}).get("reu")
    if (not isinstance(r,dict) or len(r)!=1 or
        next(iter(r),None) not in SERVICES or
        set(config["hardware"])!={"reu"}):
        raise UnifiedREUError("Select exactly one qualified hardware REU service")
    name,setting=next(iter(r.items()))
    if (not isinstance(setting,dict) or
        set(setting)!={"capacity_kib","bank","reserved_banks"}):
        raise UnifiedREUError("Incomplete "+name+" configuration")
    spec=SERVICES[name]
    capacity,bank,other=(setting[k] for k in ("capacity_kib","bank","reserved_banks"))
    if (type(capacity) is not int or capacity not in spec["default_bank"] or
        type(bank) is not int or
        not isinstance(other,list) or any(type(a) is not int for a in other)):
        raise UnifiedREUError("Unsupported REU tier or bank declarations")
    if spec["fallback"] not in config.get("operations",[]):
        raise UnifiedREUError(name+" requires "+spec["fallback"]+
                              " normal stock-C64 fallback")
    spec["module"].check_claims(capacity,bank,reserved_reu_banks=other)
    return name,setting


def requirements(config):
    name,_=qualified_hardware(config)
    spec=SERVICES[name]
    return {"zero_page_bytes":spec["zp"][1]-spec["zp"][0]+1,
            "main_ram_total_bytes":spec["ram"]}


def _mapped_stock_memory(config,name):
    spec=SERVICES[name]
    original=config.get("memory",{})
    if not isinstance(original,dict):
        raise UnifiedREUError("Memory configuration must be an object")
    import copy
    memory=copy.deepcopy(original)
    reserved=memory.setdefault("reserved",[])
    zpreserved=memory.setdefault("zp_reserved",[])
    if not isinstance(reserved,list) or not isinstance(zpreserved,list):
        raise UnifiedREUError("Memory reservations must be arrays")
    reserved_names={"__reu_service_prg","__reu_service_io","__reu_service_scratch"}
    if any(not isinstance(x,dict) or x.get("name") in reserved_names
           for x in reserved+zpreserved):
        raise UnifiedREUError("Invalid or duplicate REU memory reservation")
    reserved += [
        {"name":"__reu_service_prg","start":"$3000","end":"$77FF"},
        {"name":"__reu_service_io","start":"$C000","end":"$C01F"},
    ]
    if name=="qs16":
        reserved.append({"name":"__reu_service_scratch",
                         "start":"$C020","end":"$C023"})
    zp0,zp1=spec["zp"]
    zpreserved.append({"name":"__reu_service_zp",
                       "start":"$%02X"%zp0,"end":"$%02X"%zp1})
    memory.setdefault("math_io","$C040")
    memory.setdefault("zp_base",spec["default_zp"])
    return memory


def install(config,index,plan,folder:Path,linker):
    name,hw=qualified_hardware(config)
    spec=SERVICES[name]
    required=requirements(config)
    for dimension,budget in (("zero_page_bytes","max_zp_bytes"),
                             ("main_ram_total_bytes","max_ram_bytes")):
        initial=config["constraints"][budget]
        reduced=plan["constraints"][budget]
        expected=None if initial is None else initial-required[dimension]
        if reduced!=expected:
            raise UnifiedREUError("Stock selector did not reserve "+dimension)
    memory=_mapped_stock_memory(config,name)
    stock=linker.build(plan,folder,memory=memory)
    module_manifest,prg=spec["module"].build(
        hw["capacity_kib"],hw["bank"],reserved_reu_banks=hw["reserved_banks"])
    usage=stock["resource_use"]
    sum_ram=usage["main_ram_total_bytes"]+required["main_ram_total_bytes"]
    sum_zp=usage["zero_page_bytes"]+required["zero_page_bytes"]
    for value,k in ((sum_ram,"max_ram_bytes"),(sum_zp,"max_zp_bytes")):
        ceiling=config["constraints"][k]
        if ceiling is not None and value>ceiling:
            raise UnifiedREUError("Global operation-first REU budget exceeded")
    path=name+"_reu.prg"
    (folder/path).write_bytes(prg)
    (folder/(name+"_reu_manifest.json")).write_text(
        json.dumps(module_manifest,indent=2,sort_keys=True)+"\n")
    public=module_manifest["public_exports"]
    with (folder/("math_reu_"+name+".inc")).open("w") as stream:
        stream.write("; REU service requires explicit successful INSTALL and guarded calls.\n")
        for api,address in sorted(public.items()):
            stream.write("MATH_"+api+" = "+address+"\n")
    stock_hash=hashlib.sha256((folder/"math_selective.prg").read_bytes()).hexdigest()
    if stock_hash!=stock["prg_sha256"]:
        raise UnifiedREUError("Stock program hash mismatch")
    if hashlib.sha256((folder/path).read_bytes()).hexdigest()!=module_manifest["prg_sha256"]:
        raise UnifiedREUError("REU program hash mismatch")
    project={
        "schema":"operation-first-reu-module-project-v1",
        "service":name,"one_reu_service_at_a_time":True,
        "status":"SOURCE_BUILT_REU_OPTIN_NO_IRQ_VIC_CONCURRENCY_CERTIFICATE",
        "hardware":{"reu":{name:hw}},
        "stock_remains_default":True,
        "stock_prg":"math_selective.prg",
        "stock_prg_sha256":stock_hash,
        "reu_prg":path,"reu_prg_sha256":module_manifest["prg_sha256"],
        "source_built_service":True,
        "full_historical_resident_dependency":False,
        "physical_memory_bound_by_stock_linker":True,
        "combined_resource_use":{
            "main_ram_total_bytes":sum_ram,
            "zero_page_bytes":sum_zp,
            "exclusive_reu_banks":module_manifest["claims"].get(
                "reu_banks",[hw["bank"]]),
            "reu_device_io2_exclusive":True,
        },
        "reu_entrypoints":public,
        "native_mixed_irq_vic_qualified":False,
        "service_manifest":name+"_reu_manifest.json",
    }
    (folder/"math_project_manifest.json").write_text(
        json.dumps(project,indent=2,sort_keys=True)+"\n")
    return stock
