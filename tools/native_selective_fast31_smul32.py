#!/usr/bin/env python3
"""Native VICE signed32 FAST31 public adapter, 2 independent relocations."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
import selective_fast31_umul32 as fast
from native_selective_smul32 import run_native,N

ROOT=Path(__file__).resolve().parents[1]
SOURCE="routines/multiply/smul32_fast31_public.asm"
ENTRY="FAST_SMUL32_FAST31"

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to native x64sc")
    total=0
    with tempfile.TemporaryDirectory(prefix="native_smul32_fast31_") as d:
        folder=Path(d)
        for i,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            memory,entry,segments,end=fast.assemble(code,io,zp,ROOT,
                                                    source_path=SOURCE,
                                                    entry_label=ENTRY)
            prg=bytes((code&255,code>>8))+bytes(memory[p] for p in range(code,end))
            digest=run_native(vice,prg,entry,code,io,
                              "smul32_fast31_%04x"%code,9250+i,folder)
            total+=N
            print("NATIVE SMUL32 FAST31",hex(code),N,"PASS",digest,flush=True)
    assert total==2*N
    print("NATIVE SMUL32 FAST31 TWO MAPS PASS",total)

if __name__=="__main__":
    main()
