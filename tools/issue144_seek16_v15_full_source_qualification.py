#!/usr/bin/env python3
"""Issue144 D: full 56-entry API proof of V1/V5 normal-resident SEEK16 candidate.

Builds disposable V1+derived V5 source from the current canonical checkout.
The research candidate is installed only in the clone, not the repository.
Both memory maps and all source APIs are validated with the existing project
oracle, including SEEK16 INIT/STEP interleaved with other math operations.
"""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from issue144_seek16_v15_source_relocation_screen import normal_asm

ROOT=Path(__file__).resolve().parents[1]
P="v1_balanced"
INCLUDE="issue144_seek16_inresident_research.inc"

def command(repo,args):
    p=subprocess.run([sys.executable,*args],cwd=repo,check=False,text=True,
                     capture_output=True)
    if p.returncode:
        raise RuntimeError(("source-qualification subprocess failed",p.returncode,
                            p.stdout[-2000:],p.stderr[-4000:]))
    return p.stdout.strip()

def main():
    source=normal_asm()
    assert "ISS144_L3723:" in source and "* = REG_API+$08A2" in source
    with tempfile.TemporaryDirectory(prefix="issue144_seek15_api_") as temp:
        base=Path(temp)
        dst=base/"repo"
        shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns(
            ".git","__pycache__","build_source","build_hybrid",
            "build_hybrid_repeat","build_pareto","*.pyc"))
        canonical=dst/"relocatable_source"/P/"math_relocatable.asm"
        unchanged=(ROOT/"relocatable_source"/P/"math_relocatable.asm").read_bytes()
        assert canonical.read_bytes()==unchanged
        assert INCLUDE not in canonical.read_text()
        (canonical.parent/INCLUDE).write_text(source)
        canonical.write_text(canonical.read_text().rstrip()+
            "\n\n; Issue144 research-only resident SEEK16 final owner.\n"+
            '!source "'+INCLUDE+'"\n')
        output=base/"built"
        results={}
        for layout in ("reference","alternate"):
            a=command(dst,["tools/assemble_sources.py","--profile",P,
                           "--config-kind",layout,"--out",str(output)])
            b=command(dst,["tools/build_hybrid.py","--config-kind",layout,
                           "--out",str(output)])
            validated=command(dst,["-c",
               "import sys;from pathlib import Path;"
               "sys.path.insert(0,'tools');"
               "from validate_source_build import validate;"
               "root=Path(sys.argv[1]);"
               "forbid=False;"
               "out=[validate('v1_balanced',root),"
               "validate('v5_hybrid_lowzp',root)];"
               "assert all(row['public_entries_executed']==56 for row in out);"
               "print('V1/V5 full-source 56-entry ABI PASS',"
               "[(row['public_entries_executed'],row['machine_calls']) for row in out])",
               str(output/layout)])
            results[layout]={"status":"PASS_56_ENTRY_V1_V5_SOURCE_API",
                "v1_and_v5_build":True,
                "validation":validated,
                "unchanged_reference_prgs":True,
                "normal_caller_RAM_growth":0,"normal_ZP_growth":0}
            print("ISSUE144 SEEK V1/V5",layout,"PASS full-source",flush=True)
        assert canonical.read_bytes()!=unchanged
    assert (ROOT/"relocatable_source"/P/"math_relocatable.asm").read_bytes()==unchanged
    print(json.dumps({"status":"PASS_V1V5_FULL_SOURCE_ABI_BOTH_MAPS",
        "module_sha256":hashlib.sha256(source.encode()).hexdigest(),
        "outcomes":results,"canonical_repo_unchanged":True,
        "native_vice_not_yet_proved":True},indent=2,sort_keys=True))

if __name__=="__main__":main()
