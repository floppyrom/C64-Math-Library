#!/usr/bin/env python3
"""Native VICE proof of both signed24 shared Q/R variants on the same corpus."""
from __future__ import annotations
import hashlib
import os
import tempfile
from pathlib import Path
import math_builder
import selective_linker
from native_selective_sdiv24 import N, STRIDE, verify

OPS = ("SDIV24", "SMOD24")
PAIRS = (("link:portable-zerozp", 325, 364),
         ("link:abs-qzero-guard", 387, 426))

def main():
    vice=os.environ.get("VICE_WRAPPER", "")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must identify native x64sc")
    catalog=math_builder.operation_index()
    with tempfile.TemporaryDirectory(prefix="sdiv24_qzero_native_") as t:
        folder=Path(t)
        for k,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            seen={}
            for n,(variant,bytes_expected,budget) in enumerate(PAIRS):
                plan=math_builder.create_plan(catalog,list(OPS),
                    objective="size",zp_budget=0,ram_budget=budget,
                    pins={api:variant for api in OPS})
                sub=folder/("source_%d_%d"%(k,n))
                man=selective_linker.build(plan,sub,memory={
                    "code_base":code,"math_io":io,"scratch_base":io+0x40})
                entries={r["api"]:int(r["entry"][1:],16) for r in man["operations"]}
                assert entries == {"MATH_SDIV24":code,"MATH_SMOD24":code},entries
                assert man["resource_use"]["image_span_bytes"]==bytes_expected
                assert man["resource_use"]["main_ram_total_bytes"]==budget
                assert man["resource_use"]["zero_page_bytes"]==0
                assert len(man["link_order"])==1
                image=(sub/"math_selective.prg").read_bytes()
                digest=verify(vice,image,code,code,io,
                    "signed24_%04x_%s"%(code,n),8130+2*k+n,sub)
                # The public ABI specifies carry but not incidental N/Z/V/I
                # processor flags. Normalize the saved PHP status column to C
                # before comparing otherwise identical native output streams.
                raw=bytearray((sub/("signed24_%04x_%s"%(code,n)+".bin")).read_bytes())
                for i in range(N):
                    raw[6*STRIDE+i] &= 1
                canonical=hashlib.sha256(raw).hexdigest()
                seen[variant]=canonical
                print("NATIVE SIGNED24",hex(code),variant,N,
                      "PASS",digest,"public-ABI",canonical,flush=True)
            assert seen[PAIRS[0][0]]==seen[PAIRS[1][0]], (
                "public output differs for matched native operands",seen)
    print("NATIVE SIGNED24 QZERO PAIRED TWO-MAP PASS",4*N,flush=True)

if __name__=="__main__":
    main()
