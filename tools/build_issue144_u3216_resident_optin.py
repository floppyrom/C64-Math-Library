#!/usr/bin/env python3
"""Issue144 B explicit opt-in normal-resident dual-tail V2/V3/V4 source builder.

Avoids modifying the working repository by cloning the minimal release package
into a private temporary directory, then patching only that temporary source.
Builds all 56-entry public API source layouts and runs the full source validator
before copying the finished candidate PRG/REU/API manifests to --out.

V1 and V5 are intentionally forbidden: the V5 linker cannot currently import
the auxiliary low-divisor code without relocating its target. The V2–V4
artifact is *optional*, not a change to frozen reference images/PERFORMANCE.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from issue144_u3216_inresident_fullabi_stage import variant,FILE
from issue144_u3216_inresident_dualtail_model import builds,NBYTES
PROFILES=("v2_pareto_fast","v3_reu_512k","v4_reu_16m")

def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as fin:
        for b in iter(lambda:fin.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def clone_ignore(source,names):
    forbidden={".git","__pycache__",".pytest_cache",".venv","build_source",
               "build_u3216","build_alternate","build_issue144_inresident",
               "build_issue144_dualtail_optin"}
    return [x for x in names if x in forbidden]

def call(cmd,folder):
    x=subprocess.run(cmd,cwd=folder,capture_output=True,text=True)
    if x.returncode:
        raise RuntimeError("Failed: "+str(cmd)+"\n"+x.stdout[-2500:]+"\n"+x.stderr[-3500:])
    return x.stdout

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile",choices=(*PROFILES,"all"),default="all")
    ap.add_argument("--config-kind",choices=("reference","alternate"),default="reference")
    ap.add_argument("--out",type=Path,default=ROOT/"build_issue144_dualtail_optin")
    a=ap.parse_args()
    selected=PROFILES if a.profile=="all" else (a.profile,)
    output=a.out.resolve()
    if output==ROOT or output==ROOT/"relocatable_source":
        raise ValueError("Output must be a dedicated directory, not the repository root")
    original_sha=sha(FILE)
    selected_results=[]
    with tempfile.TemporaryDirectory(prefix="c64ml_u3216_resident_build_") as td:
        clone=Path(td)/"source"
        shutil.copytree(ROOT,clone,ignore=clone_ignore)
        same_src=clone/"relocatable_source/division/udiv32_16_split_direct.inc"
        existing=same_src.read_text()
        assert hashlib.sha256(existing.encode()).hexdigest()==original_sha
        patched=variant(existing)
        same_src.write_text(patched)
        for profile in selected:
            # Preflight current-source direct resident geometry, exact ABI,
            # preserve original reference images under immutable package.
            _,trial,api,config,size=builds(profile,a.config_kind)
            assert size==NBYTES
            target=clone/"generated"
            x=call([sys.executable,"tools/assemble_sources.py",
               "--profile",profile,"--config-kind",a.config_kind,
               "--out",str(target)],clone)
            checked=clone/"candidate_validation"/profile
            y=call([sys.executable,"tools/validate_source_build.py",
               profile,"--build",str(target/a.config_kind),
               "--out",str(checked)],clone)
            evidence=json.loads((checked/(profile+"_alternate_validation.json")).read_text())
            assert evidence["public_entries_executed"]==56
            assert evidence["machine_calls"]==21678
            folder=target/a.config_kind/profile
            dest=output/a.config_kind/profile
            dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():shutil.rmtree(dest)
            shutil.copytree(folder,dest)
            (dest/"U3216_LOWTAIL_SELECTED_SOURCE.inc").write_text(patched)
            p=dest/("math_"+profile+"_game_math.prg")
            assert p.exists()
            row={"profile":profile,"layout":a.config_kind,
                 "status":"PASS_56_ENTRY_SOURCE_ONLY_OPTION",
                 "public_calls":evidence["machine_calls"],
                 "public_api_entries":evidence["public_entries_executed"],
                 "candidate_prg_sha256":sha(p),
                 "selected_division_source_sha256":hashlib.sha256(patched.encode()).hexdigest(),
                 "source_region":"REG_LOW+$0C00",
                 "owned_secondary_code_bytes":NBYTES,"extra_caller_RAM":0,"extra_ZP":0,
                 "v5_safe_to_import":False,
                 "reference_PRGs_REUs_unchanged":True}
            (dest/"ISSUE144_B_OPTIONAL_BUILD.json").write_text(json.dumps(row,indent=2)+"\n")
            selected_results.append(row)
            print("IN-RESIDENT U3216 OPTIN BUILT",profile,a.config_kind,
                  evidence["machine_calls"],"verified public calls",flush=True)
    assert sha(FILE)==original_sha,"Original repository source was unexpectedly modified"
    print(json.dumps({"status":"PASS_U3216_RESIDENT_OPTIONAL_BUILDER",
         "profiles":selected_results,"destination":str(output),
         "working_repository_source_untouched":True,
         "v1_v5_not_selected":True},indent=2))
if __name__=="__main__":main()
