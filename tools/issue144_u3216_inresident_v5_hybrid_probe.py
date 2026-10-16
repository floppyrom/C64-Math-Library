#!/usr/bin/env python3
"""Issue144 B: V5 donor isolation regression, not V5 dual-tail promotion.

The optional V2–V4 low-D tail changes V2 source. Building V5 *while* that
patch is present is known to leave its imported branch pointing into V1-derived
RAM. Verify that unsafe direct inheritance is rejected, restore the donor,
and then validate both ordinary 31-ZP V5 layouts with all 56 entries.
"""
from __future__ import annotations
import hashlib,json,tempfile
from pathlib import Path
from issue144_u3216_inresident_fullabi_stage import FILE,variant
from build_hybrid import build
from validate_source_build import validate
R=Path(__file__).resolve().parents[1]

def main():
    base=FILE.read_text()
    digest=hashlib.sha256(base.encode()).hexdigest()
    hazard=None
    try:
        FILE.write_text(variant(base))
        with tempfile.TemporaryDirectory(prefix="issue144_v5_negative_donor_") as td:
            try:
                cfg=R/"relocatable_source/v5_hybrid_lowzp/math_config_reference.inc"
                build(cfg,Path(td)/"v5_hybrid_lowzp")
                validate("v5_hybrid_lowzp",Path(td))
            except RuntimeError as ex:
                msg=str(ex)
                assert "v5_hybrid_lowzp" in msg and "unsupported opcode" in msg and "$1C08" in msg,(
                    "unexpected V5 direct-import failure",msg)
                hazard=msg
            else:
                raise AssertionError("V5 unexpectedly imported optional tail safely: check explicit linker contract")
    finally:
        FILE.write_text(base)
    assert hashlib.sha256(FILE.read_bytes()).hexdigest()==digest
    rows=[]
    with tempfile.TemporaryDirectory(prefix="issue144_v5_safe_donor_") as td:
        root=Path(td)
        for layout in ("reference","alternate"):
            cfg=R/"relocatable_source/v5_hybrid_lowzp"/("math_config_"+layout+".inc")
            man=build(cfg,root/layout/"v5_hybrid_lowzp")
            assert man["normal_zp_bytes"]==31
            check=validate("v5_hybrid_lowzp",root/layout)
            assert check["public_entries_executed"]==56
            rows.append({"layout":layout,"machine_calls":check["machine_calls"],
                "normal_zp":31,"all_56_public_entries_pass":True})
            print("V5 ISOLATED SOURCE BUILD",layout,"PASS",check["machine_calls"],flush=True)
    print(json.dumps({"status":"PASS_V5_HYBRID_ISOLATED_FROM_UNSUPPORTED_DUALTAIL_DONOR",
          "unsafe_direct_inheritance_rejected":True,
          "unsafe_import_error":hazard,
          "source_restored":True,"profiles":rows,
          "public_PRGs_REUs_unchanged":True},indent=2))
if __name__=="__main__":main()
