#!/usr/bin/env python3
"""Execute both independently linked historical V3 signed24 entry points in native VICE."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path

from native_selective_sdiv24 import N, verify
from test_selective_sdiv24_v3 import V3, load

def main():
    vice=os.environ.get("VICE_WRAPPER", "")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must identify native x64sc")
    with tempfile.TemporaryDirectory(prefix="v3_signed24_relocated_") as temp:
        for k,(code,io,zp) in enumerate(((0x8000,0xc000,0x40),(0x7123,0xc040,0x60))):
            home=Path(temp)/("%04x"%code)
            home.mkdir(parents=True,exist_ok=True)
            cpu,entry,manifest,size,labels=load(home,V3,code,io,zp)
            self_source=(home/V3.split(":")[-1]/"math_selective.prg").read_bytes()
            assert size==1897
            assert manifest["resource_use"]["zero_page_bytes"]==9
            assert len(manifest["link_order"])==1
            for i,api in enumerate(("MATH_SDIV24","MATH_SMOD24")):
                port=8200+k*2+i
                tag="v3_signed24_%04x_%s"%(code,api)
                digest=verify(vice,self_source,entry[api],code,io,tag,port,home)
                print("NATIVE V3 SIGNED24",api,hex(code),N,"PASS",digest,flush=True)
    print("NATIVE V3 SIGNED24 RELOCATED TWO-ENTRY TWO-MAP PASS",4*N,flush=True)

if __name__=="__main__":
    main()
