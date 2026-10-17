#!/usr/bin/env python3
"""Native VICE paired old/new 32/16 public DIV/MOD unrolling qualification."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from native_selective_u3216 import native,N
from test_selective_u3216_unrolled import assemble,BASE,SOURCE

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to a native x64sc binary")
    calls=0
    with tempfile.TemporaryDirectory(prefix="native_u3216_unrolled_") as d:
        root=Path(d)
        for k,(code,io,scratch) in enumerate(((0x8000,0xc000,0xc020),
                                            (0x7123,0xc040,0xc080))):
            digests={}
            for candidate,source in ((False,BASE),(True,SOURCE)):
                image,entry=assemble(source,code,io,scratch)
                memory=bytearray(65536)
                for addr,byte in image.items():
                    memory[addr]=byte
                for public_api in ("UDIV32_16","UMOD32_16"):
                    tag="u3216_%s_%s_%04x"%(
                        "unrolled" if candidate else "baseline",
                        public_api.lower(),code)
                    digest=native(vice,bytearray(memory),entry,code,io,tag,
                                  9750+calls//N,root)
                    calls+=N
                    digests[(candidate,public_api)]=digest
                    print("NATIVE U3216 UNROLLED",
                          "fast" if candidate else "baseline",
                          public_api,hex(code),N,digest,flush=True)
            for api in ("UDIV32_16","UMOD32_16"):
                if digests[(False,api)]!=digests[(True,api)]:
                    raise RuntimeError("Old/new native Q/R/C outputs differ: "+api)
    assert calls==8*N,calls
    print("NATIVE UNROLLED U3216 TWO MAPS OLD/NEW Q/R/C PASS",calls)

if __name__=="__main__":
    main()
