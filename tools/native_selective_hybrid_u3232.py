#!/usr/bin/env python3
"""Native VICE validation: V2-fast 32/16 and unrestricted 32/32 composed source."""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"routines/standalone_lab/portable"))

from native_vice import VICE,check
import selective_hybrid_u3232 as hybrid

def main():
    if not os.environ.get("VICE_WRAPPER") or not VICE.is_file():
        raise RuntimeError("VICE_WRAPPER must point to the real x64sc emulator")
    total=0
    with tempfile.TemporaryDirectory(prefix="native_u3232_v2hybrid_") as tmp:
        directory=Path(tmp)
        for i,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            packed,labels,_,end=hybrid.assemble(code,io,zp)
            mem=bytearray(65536)
            for addr,byte in packed.items():
                mem[addr]=byte
            mapping={"INPUT_NUM":io+16,"INPUT_DIV":io+20,
                     "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28}
            for j,(name,entry) in enumerate(((hybrid.API_DIV,labels[hybrid.API_DIV]),
                                             (hybrid.API_MOD,labels[hybrid.API_MOD]))):
                result=check(bytearray(mem),entry,32,mapping,
                             "v2hybrid_%s_%04x"%(name.lower(),code),
                             9970+i*2+j,directory,False)
                total+=result["cases"]
                print("NATIVE V2 32/32 HYBRID",name,hex(code),result["cases"],
                      "PASS",flush=True)
    assert total==384,total
    print("NATIVE V2 32/32 HYBRID BOTH EXPORTS TWO MAPS PASS",total)

if __name__=="__main__":
    main()
