#!/usr/bin/env python3
"""CPU-model REU SWAP BEGIN/CALL/END experiment for source-assembled Turbo16.

This module actually executes a source-assembled 6510 controller with $92
REU SWAP, validates full zero-page restoration, nested-state rejection,
and repeated multiplication batches. The lookup-table bytes in this test
are extracted only from the frozen V3 reference PRG; independent table
generation, native-VICE timings and stock builder integration remain TODO.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random

from mini6502 import Assembler, CPU, load_sparse
import reu_turbo16_fragment as fragment
import reu_turbo16_source_tables as source_tables

ROOT=Path(__file__).resolve().parents[1]
CONTROLLER=Path("relocatable_source/turbo/turbo16_swap_controller.asm")
TABLE_OFFSETS=(0x1000,0x1200,0x1400,0x1600)
N=122
BANK_SIZE=65536

class SwapError(ValueError):
    pass


def valid_plan(*,zp,io,table,api,ctrl,state,bank,reu_bytes=524288):
    fragment.check_regions(zp,io,table,api)
    if reu_bytes not in (524288, 16777216):
        raise SwapError("Only checked REU 512KiB or 16MiB tiers")
    if not 0<=bank<reu_bytes//BANK_SIZE:
        raise SwapError("Turbo16 bank outside installed REU hardware tier")
    if not 0x200<=ctrl<=0xff80 or ctrl&0x7f:
        raise SwapError("DMA controller needs 128-byte-aligned RAM slot")
    blocks={
        "public_io":(io,io+31),
        "square_tables":(table+0x1000,table+0x17ff),
        "call_binder":(api+0x840,api+0x87f),
        "dma_controller":(ctrl,ctrl+127),
        "dma_state":(state,state),
    }
    if not 0x200<=state<=0xffff:
        raise SwapError("Invalid DMA state RAM address")
    for name,(lo,hi) in blocks.items():
        if not 0x200<=lo<=hi<=0xffff or lo<=0xdfff and hi>=0xd000:
            raise SwapError("Illegal C64 RAM or I/O placement for "+name)
    for i,(name,a) in enumerate(blocks.items()):
        for other,b in list(blocks.items())[i+1:]:
            if a[0]<=b[1] and b[0]<=a[1]:
                raise SwapError("Resource overlap: "+name+"/"+other)


def assemble(zp=0x3e,io=0xc000,table=0x6000,api=0x3000,
             ctrl=0x3a00,state=0xc040,bank=4,reu_bytes=524288):
    valid_plan(zp=zp,io=io,table=table,api=api,ctrl=ctrl,
               state=state,bank=bank,reu_bytes=reu_bytes)
    arithmetic,parts=fragment.assemble(zp=zp,io=io,table=table,api=api)
    src,sha=fragment.locked_source(ROOT,CONTROLLER)
    head=("\n".join([
        "REU_CTRL_BASE = $%04X"%ctrl,
        "T16_STATE = $%04X"%state,
        "TURBO16_ZP_BASE = $%04X"%zp,
        "REU_TURBO16_BANK = $%02X"%bank,
        "T16_PUBLIC_CALL = $%04X"%(api+0x840),
    ])+"\n")
    try:
        mem,labels,_=Assembler().assemble(head+src)
    except (ValueError,KeyError,AssertionError) as exc:
        raise SwapError("DMA SWAP source assembly failed: "+str(exc)) from exc
    expected={
        "begin":labels.get("T16_SWAP_BEGIN"),
        "call":labels.get("T16_SWAP_CALL"),
        "end":labels.get("T16_SWAP_END"),
    }
    if expected["begin"]!=ctrl or None in expected.values():
        raise SwapError("Missing source-backed lifecycle symbol")
    if len(set(expected.values()))!=3:
        raise SwapError("Lifecycle entries alias unexpectedly")
    if set(mem)!=set(range(ctrl,ctrl+len(mem))) or len(mem)>128:
        raise SwapError("DMA controller escaped its reserved slot")
    controller=bytes(mem[addr] for addr in range(ctrl,ctrl+len(mem)))
    parts=dict(parts)
    parts["turbo16_dma_swap_controller.bin"]=controller
    manifest={
        "schema":"turbo16-reu-swapped-lifecycle-experiment-v1",
        "status":"CPU_MODEL_SWAP_LIFECYCLE_NOT_NATIVE_VICE_NOT_BUILDER_LINK_READY",
        "controller_source_sha256":sha,
        "controller_source":str(CONTROLLER),
        "arithmetic_source_sha256":arithmetic["reference_sources_sha256"],
        "entrypoints":{name:"$%04X"%value for name,value in expected.items()},
        "controlled_executable_zp":["$%02X"%zp,"$%02X"%(zp+N-1)],
        "public_io":"$%04X"%io,
        "dma_state":"$%04X"%state,
        "reu_bank":bank,
        "reu_capacity_bytes":reu_bytes,
        "dma_type":"REU command $92 C64/REU SWAP",
        "independent_quarter_square_tables_implemented":False,
        "source_linker_reu_variant_available":False,
        "native_vice_qualified":False,
        "not_safe_to_nest":True,
        "irq_must_not_touch_exclusive_zp_during_active_mode":True,
        "segment_sha256":{name:hashlib.sha256(blob).hexdigest()
                          for name,blob in sorted(parts.items())},
    }
    return manifest,parts,mem,{k:v for k,v in expected.items()}


def source_qualified_tables():
    """Build exact 4x512 Turbo16 planes from V3/V4 SOURCE, not reference PRGs.

    This is still a literal source extraction, not a mathematical independent
    generator and not a native-VICE-validated REU installer.
    """
    manifest, chunks = source_tables.materialize()
    if manifest["total_bytes"] != 2048 or manifest["native_reu_backend_available"]:
        raise SwapError("Source-qualified Turbo16 table contract changed")
    planes = tuple(chunks[name] for name in source_tables.NAMES)
    if len(planes) != 4 or any(len(plane) != 512 for plane in planes):
        raise SwapError("Incorrect source-table payload length")
    return manifest, planes


def cpu_model_proof(zp=0x3e,io=0xc000,table=0x6000,api=0x3000,
                    ctrl=0x3a00,state=0xc040,bank=4,reu_bytes=524288):
    manifest,parts,control,labels=assemble(
        zp,io,table,api,ctrl,state,bank,reu_bytes)
    table_manifest, table_planes = source_qualified_tables()
    mem=load_sparse(control)
    for filename,addr in (
        ("turbo16_call_binder.bin",api+0x840),
    ):
        blob=parts[filename]
        mem[addr:addr+len(blob)]=blob
    for base,plane in zip(TABLE_OFFSETS,table_planes):
        mem[table+base:table+base+512]=plane
    initial_zp=bytes(((i*73+19)&255 for i in range(N)))
    mem[zp:zp+N]=initial_zp
    mem[state]=0
    reu=bytearray(reu_bytes)
    reu[bank*BANK_SIZE:bank*BANK_SIZE+N]=parts["turbo16_zp_overlay.bin"]
    cpu=CPU(mem,reu=reu)
    stack=cpu.sp
    io_pairs=[(0,0),(1,1),(0xffff,0xffff),(0xff00,0x0101),
              (0x1234,0x9876),(0,0xffff),(0xffff,0)]
    rng=random.Random(0xC64E2026)
    io_pairs += [(rng.randrange(65536),rng.randrange(65536)) for _ in range(105)]
    dig=hashlib.sha256()
    batch_stats=[]
    for batch in range(2):
        prior_irq=batch&1
        loaded_before=bytes(reu[bank*BANK_SIZE:bank*BANK_SIZE+N])
        cpu.i=prior_irq
        # A no-BEGIN call cannot execute through invalid ZP contents.
        if batch==0:
            cpu.call(labels["call"])
            if cpu.c!=1:raise SwapError("Uninitialized CALL was not rejected")
            cpu.call(labels["end"])
            if cpu.c!=1:raise SwapError("Uninitialized END was not rejected")
        begin=cpu.call(labels["begin"])
        if cpu.c or cpu.i!=prior_irq or cpu.sp!=stack:
            raise SwapError("BEGIN failed to preserve caller flags/stack")
        if cpu.mem[state]!=1 or bytes(cpu.mem[zp:zp+N])!=loaded_before:
            raise SwapError("BEGIN did not load executable ZP overlay")
        if bytes(reu[bank*BANK_SIZE:bank*BANK_SIZE+N])!=initial_zp:
            raise SwapError("BEGIN did not save the exact caller zero page in REU")
        before_zp=bytes(cpu.mem[zp:zp+N])
        before_reu=bytes(reu[bank*BANK_SIZE:bank*BANK_SIZE+N])
        cpu.call(labels["begin"])
        if cpu.c!=1 or bytes(cpu.mem[zp:zp+N])!=before_zp or (
           bytes(reu[bank*BANK_SIZE:bank*BANK_SIZE+N])!=before_reu):
            raise SwapError("Nested BEGIN corrupted overlay state")
        cycles=[]
        for x,y in io_pairs:
            for ofs in range(2):
                cpu.mem[io+ofs]=(x>>(8*ofs))&255
                cpu.mem[io+4+ofs]=(y>>(8*ofs))&255
            cpu.d=0
            cpu.c=(x+y)&1
            delta=cpu.call(labels["call"],5000)
            q=sum(cpu.mem[io+8+k]<<(8*k) for k in range(4))
            if q!=x*y or cpu.c!=0 or cpu.sp!=stack:
                raise SwapError("Wrong Turbo16 product/Carry/stack: "+
                                repr((batch,x,y,q,x*y,cpu.c)))
            if (cpu.mem[io]|cpu.mem[io+1]<<8)!=x or (
               cpu.mem[io+4]|cpu.mem[io+5]<<8)!=y:
                raise SwapError("Turbo16 modified public input")
            dig.update(bytes((x&255,x>>8,y&255,y>>8)))
            dig.update(q.to_bytes(4,"little"))
            cycles.append(delta)
        active_overlay=bytes(cpu.mem[zp:zp+N])
        end=cpu.call(labels["end"])
        if cpu.c or cpu.sp!=stack or cpu.i!=prior_irq:
            raise SwapError("END failed to restore caller flags/stack")
        if cpu.mem[state]!=0 or bytes(cpu.mem[zp:zp+N])!=initial_zp:
            raise SwapError("END failed to restore all 122 bytes of caller zero page")
        if bytes(reu[bank*BANK_SIZE:bank*BANK_SIZE+N])!=active_overlay:
            raise SwapError("END did not preserve SMC-patched executable overlay in REU")
        batch_stats.append({"calls":len(cycles),"begin_model_cycles":begin,
                            "end_model_cycles":end,
                            "mean_call_cycles":sum(cycles)/len(cycles),
                            "max_call_cycles":max(cycles),
                            "zero_page_exact_restoration":True,
                            "reu_overlay_persisted_with_live_smc_operands":True,
                            "nested_begin_rejected":True})
    return {**manifest,"proof_status":"CPU_MODEL_FULL_ARITHMETIC_AND_DMA_SWAP_TWO_BATCHES",
            "test_only_table_fixture":None,
            "lookup_table_provenance":"SHA-locked literal V3/V4 source, no resident PRG required",
            "source_table_hashes":table_manifest["plane_sha256"],
            "historical_table_source_hashes":table_manifest["reference_sources_sha256"],
            "test_only_table_planes":4,
            "test_only_table_bytes":2048,
            "arithmetic_calls":sum(x["calls"] for x in batch_stats),
            "batch_evidence":batch_stats,
            "result_digest_sha256":dig.hexdigest()}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args(argv)
    if args.out.exists():
        ap.exit(2,"REU DMA prototype: refusing to overwrite output\n")
    try:
        proof=cpu_model_proof()
    except (SwapError,fragment.FragmentError,OSError,ValueError) as exc:
        ap.exit(2,"REU DMA prototype: "+str(exc)+"\n")
    args.out.mkdir(parents=True)
    (args.out/"turbo16_reu_swap_cpu_model.json").write_text(
        json.dumps(proof,indent=2,sort_keys=True)+"\n")
    print("Proved Turbo16 SWAP in CPU model; no native REU backend qualified.")
    return 0


if __name__=="__main__":raise SystemExit(main())
