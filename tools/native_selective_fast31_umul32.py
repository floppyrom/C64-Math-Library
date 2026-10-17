#!/usr/bin/env python3
"""Two-map VICE r46284 validation of the independent source-adapted FAST31 core."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import selective_fast31_umul32 as fast
from native_selective_umul32 import run_native,N

ROOT=Path(__file__).resolve().parents[1]

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to native x64sc")
    total=0
    with tempfile.TemporaryDirectory(prefix="umul32_fast31_native_") as td:
        folder=Path(td)
        for k,(base,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            memory,entry,segments,end=fast.assemble(base,io,zp,ROOT)
            prg=bytes((base&255,base>>8))+bytes(memory[x] for x in range(base,end))
            digest=run_native(vice,prg,entry,base,io,
                              "umul32_fast31_%04x"%base,9050+k,folder)
            total+=N
            print("NATIVE FAST31 UMUL32",hex(base),N,"PASS",digest,flush=True)
    assert total==2*N
    print("NATIVE FAST31 UMUL32 TWO MAPS PASS",total)

if __name__=="__main__":
    main()
