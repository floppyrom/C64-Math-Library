#!/usr/bin/env python3
"""Native x64sc V2 Pareto-Fast donor with independently staged public Q/R/C."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import selective_v2_fast_u3216 as fast
from native_selective_u3216 import native,N

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER requires a native x64sc binary")
    total=0
    with tempfile.TemporaryDirectory(prefix="native_u3216_v2_") as d:
        root=Path(d)
        for k,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            machine,labels,slots=fast.assemble(code,io,zp)
            memory=bytearray(65536)
            for addr,val in machine.items():
                memory[addr]=val
            results=[]
            for j,api in enumerate(("UDIV32_16","UMOD32_16")):
                entry=labels["FAST_"+api+"_V2"]
                checksum=native(vice,bytearray(memory),entry,code,io,
                    "v2_sizefast_%s_%04x"%(api.lower(),code),
                    9890+k*2+j,root)
                total+=N;results.append(checksum)
                print("NATIVE V2 FAST 32/16",api,hex(code),N,
                      checksum,slots,flush=True)
            if results[0]!=results[1]:
                raise RuntimeError("V2 fast public quotient/modulo output hashes differ")
    assert total==4*N
    print("NATIVE V2 32/16 PUBLIC Q/R/C TWO MAP PASS",total)

if __name__=="__main__":
    main()
