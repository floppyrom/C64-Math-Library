#!/usr/bin/env python3
"""Pinned native x64sc public Q32/R32/C verification of *installed* D65536.

Source qualification differs from the previous research-only assembler
because the emitted PRG comes from the ordinary operation-first installer.
Each relocation and every public alias is checked in native VICE.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile

import native_research_d65536 as original_native
from test_registered_d65536_hybrid import APIS, PLACEMENTS, build_at

CODES=PLACEMENTS


def verify(vice):
    if not vice or not Path(vice).is_file():
        raise ValueError("Pinned r46284 VICE_WRAPPER required")
    original_native.native_unsigned.VICE=Path(vice)
    output=[]
    with tempfile.TemporaryDirectory(prefix="d65536_registered_") as td:
        folder=Path(td)
        for placement,(code,io,zp) in enumerate(CODES):
            binary,entries,manifest=build_at(code,io,zp,original_native.research.ROOT)
            memory=bytearray(65536)
            memory[code:code+len(binary)-2]=binary[2:]
            mapping={"INPUT_NUM":io+16,"INPUT_DIV":io+20,
                     "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28}
            for op_index,api in enumerate(APIS):
                is_signed=api.startswith("MATH_S")
                tag=f"d65536_link_{placement}_{api.lower()}"
                port=15900+placement*8+op_index
                pairs=original_native.inputs(is_signed)
                if is_signed:
                    from unittest.mock import patch
                    with patch.object(original_native.native_signed,"pairs",
                                      return_value=pairs):
                        digest=original_native.native_signed.verify(
                            vice,binary,entries[api],code,io,tag,port,folder)
                    count=96
                else:
                    from unittest.mock import patch
                    with patch.object(original_native.native_unsigned,"operands",
                                      return_value=pairs):
                        result=original_native.native_unsigned.check(
                            memory,entries[api],32,mapping,tag,port,folder,False)
                    digest,count=result["output_sha256"],result["cases"]
                if count!=96:
                    raise AssertionError("Incomplete native public-ABI corpus")
                output.append({
                    "placement":"$%04X/$%04X/$%02X"%(code,io,zp),
                    "api":api,"variant":"link:d65536-hybrid",
                    "calls":count,"output_sha256":digest,
                    "linked_binary_sha256":hashlib.sha256(binary).hexdigest(),
                    "source_sha256":hashlib.sha256(
                        (original_native.research.ROOT/"tools/research_d65536_hybrid.py").read_bytes()).hexdigest(),
                    "zero_page_bytes":manifest["resource_use"]["zero_page_bytes"],
                })
                print("NATIVE INSTALLED D65536",tag,count,"PASS",flush=True)
    for api in APIS:
        captures=[row["output_sha256"] for row in output if row["api"]==api]
        if len(captures)!=2 or len(set(captures))!=1:
            raise AssertionError("Public ABI output digest changed under relocation")
    return {
        "schema":"registered-d65536-native-two-relocation-full-public-abi-v1",
        "native_vice":True,"target_relocations":2,
        "public_operations":list(APIS),"source_qualified_production_installer":True,
        "full_pal_24_frame_performance_measured_by_this_test":False,
        "real_50hz_application_certified":False,
        "results":output,
    }


def main():
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    report=verify(os.environ.get("VICE_WRAPPER",""))
    result=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(result,encoding="utf-8")
    else:
        print(result,end="")


if __name__=="__main__":
    main()
