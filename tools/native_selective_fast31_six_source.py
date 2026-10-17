#!/usr/bin/env python3
"""Native VICE proof of all six FAST31 public API entrypoints in one PRG."""
from __future__ import annotations
import os
import tempfile
from pathlib import Path
from mini6502 import Assembler
import selective_fast31_umul32 as fast31
from native_selective_umul32 import run_native as run_u, N
from native_selective_smul32 import run_native as run_s
from native_selective_umul32_shr16 import run_native as run_ushr
from native_selective_smul32_shr16 import run_native as run_sshr
from test_selective_fast31_six_source import ENTRIES

ROOT=Path(__file__).resolve().parents[1]
SOURCE="routines/multiply/mul32_fast31_shared_public.asm"

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must name installed x64sc")
    total=0
    with tempfile.TemporaryDirectory(prefix="native_fast31_six_") as tmp:
        folder=Path(tmp)
        for k,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x70))):
            image,entry,_,end=fast31.assemble(
                code,io,zp,ROOT,source_path=SOURCE)
            src=fast31.render(fast31.layout(code)[0],io,zp,ROOT,SOURCE)
            _,labels,_=Assembler().assemble(src)
            prg=bytes((code&255,code>>8))+bytes(image[i] for i in range(code,end))
            for idx,(op,name) in enumerate(ENTRIES.items()):
                run=(run_s if op.startswith("SMUL") else run_u)
                if op.endswith("SHR16"):
                    run=run_sshr if op.startswith("SMUL") else run_ushr
                proof=run(vice,prg,labels[name],code,io,
                          "fast31_six_%s_%04x"%(op.lower(),code),
                          9550+k*len(ENTRIES)+idx,folder)
                total+=N
                print("NATIVE FAST31 SIX",op,hex(code),N,"PASS",proof,flush=True)
    assert total==len(ENTRIES)*2*N
    print("NATIVE FAST31 SIX 2-MAP PASS",total)

if __name__=="__main__":
    main()
