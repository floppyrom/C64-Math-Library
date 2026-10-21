#!/usr/bin/env python3
"""Build independently relocatable Turbo16 arithmetic fragments, not a REU backend.

The source-backed 122-byte executable ZP kernel and public CALL binder are
assembled at caller-specified locations. Table generation, DMA BEGIN/END,
REU bank ownership and actual selectable packaging are NOT implemented.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from mini6502 import Assembler

ROOT=Path(__file__).resolve().parents[1]
SOURCE=(Path("relocatable_source/turbo/turbo16_overlay.asm"),
        Path("relocatable_source/turbo/turbo16_runtime.asm"))
ZP_LENGTH=122
TABLE_BYTES=2048

class FragmentError(ValueError):
    pass

def check_regions(zp,io,table,api):
    if not 2<=zp<=0x85: raise FragmentError("Turbo16 122-byte overlay must fit zero page")
    if not 0x200<=io<=0xffe0: raise FragmentError("Invalid public I/O address")
    if not 0x200<=table<=0xe800 or table%256:
        raise FragmentError("Square-table region must be page aligned and fit RAM")
    if not 0x200<=api<=0xf700 or api%64:
        raise FragmentError("Public CALL binder must have aligned 64-byte slot")
    blocks={"public_io":(io,io+31),
            "square_tables":(table+0x1000,table+0x17ff),
            "call_binder":(api+0x840,api+0x87f)}
    for name,(start,end) in blocks.items():
        if not 0x200<=start<=end<=0xffff or start<=0xdfff and end>=0xd000:
            raise FragmentError("Unsafe C64 RAM/I/O placement: "+name)
    names=list(blocks)
    for i,name in enumerate(names):
        a=blocks[name]
        for other in names[i+1:]:
            b=blocks[other]
            if a[0]<=b[1] and b[0]<=a[1]:
                raise FragmentError("Physical module collision: "+name+"/"+other)

def locked_source(root,relative):
    path=root/relative
    content=path.read_bytes()
    digest=hashlib.sha256(content).hexdigest()
    hashes={}
    for line in (root/"SHA256SUMS.txt").read_text("utf-8").splitlines():
        if len(line)>=67 and line[64:66]=="  ":
            hashes[line[66:]]=line[:64]
    if hashes.get(relative.as_posix())!=digest:
        raise FragmentError("SHA-qualified original Turbo16 source changed: "+str(relative))
    return content.decode("utf-8"),digest

def assemble(zp=0x3e,io=0xc000,table=0x6000,api=0x3000,root=ROOT):
    """Return exact executable fragment bytes and source provenance."""
    check_regions(zp,io,table,api)
    overlay,overlay_sha=locked_source(root,SOURCE[0])
    binder,binder_sha=locked_source(root,SOURCE[1])
    header="\n".join(("REG_TABLE = $%04X" % table,
                     "TURBO16_ZP_BASE = $%04X" % zp,
                     "MATH_IO = $%04X" % io,
                     "MATH_X = $%04X" % io,
                     "MATH_Y = $%04X" % (io+4),
                     "REG_API = $%04X" % api))+"\n"
    try:
        memory,labels,_=Assembler().assemble(header+overlay+"\n"+binder)
    except (ValueError,KeyError,AssertionError) as exc:
        raise FragmentError("Source-backed assembly failed: "+str(exc)) from exc
    main=api+0x840
    zp_set={x for x in memory if x<0x100}
    main_set=set(memory)-zp_set
    if zp_set!=set(range(zp,zp+ZP_LENGTH)):
        raise FragmentError("Overlay is not exactly 122 contiguous executable ZP bytes")
    if labels.get("umult_ax1")!=zp+2 or labels.get("T16_PUBLIC_CALL")!=main:
        raise FragmentError("Turbo16 public CALL/overlay ABI placement changed")
    if not main_set or main_set!=set(range(main,max(main_set)+1)) or len(main_set)>64:
        raise FragmentError("Public CALL wrapper escaped its 64-byte slot")
    chunks={"turbo16_zp_overlay.bin":bytes(memory[i] for i in range(zp,zp+ZP_LENGTH)),
            "turbo16_call_binder.bin":bytes(memory[i] for i in range(main,max(main_set)+1))}
    data={
        "schema":"modular-turbo16-arithmetic-fragments-v1",
        "status":"ASSEMBLED_SOURCE_FRAGMENTS_NO_NATIVE_REU_BACKEND",
        "reference_sources_sha256":{str(SOURCE[0]):overlay_sha,str(SOURCE[1]):binder_sha},
        "source_code_link_qualified":False,
        "reu_dma_begin_end_implemented":False,
        "may_mix_historical_resident_with_selective_prg":False,
        "exclusive_zp_start":"$%02X"%zp,
        "exclusive_zp_bytes":ZP_LENGTH,
        "call_entry":"$%04X"%main,
        "math_io":"$%04X"%io,
        "required_square_tables":[
            "$%04X"%(table+offset) for offset in (0x1000,0x1200,0x1400,0x1600)],
        "required_square_table_bytes":TABLE_BYTES,
        "memory_dependencies_not_yet_resolved":True,
        "segment_sha256":{name:hashlib.sha256(blob).hexdigest()
                          for name,blob in sorted(chunks.items())},
        "segment_bytes":{name:len(blob) for name,blob in sorted(chunks.items())},
    }
    return data,chunks

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zp-base",type=lambda x:int(x,0),default=0x3e)
    ap.add_argument("--math-io",type=lambda x:int(x,0),default=0xc000)
    ap.add_argument("--table-base",type=lambda x:int(x,0),default=0x6000)
    ap.add_argument("--api-base",type=lambda x:int(x,0),default=0x3000)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args(argv)
    if args.out.exists():
        ap.exit(2,"Turbo16 fragment: refusing to overwrite existing output\n")
    try:
        report,chunks=assemble(args.zp_base,args.math_io,args.table_base,args.api_base)
    except (OSError,FragmentError) as exc:
        ap.exit(2,"Turbo16 fragment: "+str(exc)+"\n")
    args.out.mkdir(parents=True)
    for name,blob in chunks.items():
        (args.out/name).write_bytes(blob)
    (args.out/"fragment_manifest.json").write_text(
        json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("Source-assembled Turbo16 arithmetic fragments:",args.out)
    print("No REU DMA/backend or selectable kernel is claimed.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
