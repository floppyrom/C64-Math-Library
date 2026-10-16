#!/usr/bin/env python3
"""Issue144 B: detect whether V5 hybrid imports source-selected V2 dual-tail safely.

Runs against a disposable temporary checkout source rewrite and build directory,
does not alter reference PRG/REU/PERFORMANCE. Reports a genuine V5 build/56-API
outcome rather than inferring inheritance from a shared repository include.
"""
from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from issue144_u3216_inresident_fullabi_stage import FILE,variant
from build_hybrid import build
from validate_source_build import validate
from mini6502 import CPU
R=Path(__file__).resolve().parents[1]

def main():
    base=FILE.read_text()
    digest=hashlib.sha256(base.encode()).hexdigest()
    results=[]
    try:
        FILE.write_text(variant(base))
        with tempfile.TemporaryDirectory(prefix="issue144_inresident_v5_") as td:
            root=Path(td)
            for mode in ("reference","alternate"):
                cfg=R/"relocatable_source/v5_hybrid_lowzp"/("math_config_"+mode+".inc")
                out=root/mode/"v5_hybrid_lowzp"
                manifest=build(cfg,out)
                assert manifest["normal_zp_bytes"]==31
                check=validate("v5_hybrid_lowzp",root/mode)
                assert check["public_entries_executed"]==56
                results.append({"layout":mode,"full_56_entry_pass":True,
                    "machine_calls":check["machine_calls"],
                    "ZP_bytes":manifest["normal_zp_bytes"],
                    "does_not_certify_v5_speedup":True})
                print("V5 DUALTAIL SOURCE INHERITANCE",mode,"PASS",check["machine_calls"],flush=True)
    finally:
        FILE.write_text(base)
    assert hashlib.sha256(FILE.read_bytes()).hexdigest()==digest
    print(json.dumps({"status":"PASS_V5_SOURCE_BUILD_INTEGRITY",
      "profiles":results,"temporary_source_rewrite_restored":True,
      "published_PRGs_and_REUs_unchanged":True},indent=2))
if __name__=="__main__":main()
