#!/usr/bin/env python3
"""Stage V1/V5 source-integrated UMUL8 direct output on an isolated PR branch.

Fail closed: require current-main baseline hashes, exact 11-byte production
deltas, full source roundtrip, exhaustive public results and no V2-V4 changes.
Do not merge without separate native VICE proof and green post-stage PR CI.
"""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import subprocess
import sys

R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
from benchmark_multiply_refresh import load,CORPORA,run_full

PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k",
          "v4_reu_16m","v5_hybrid_lowzp")
FAST=("v1_balanced","v5_hybrid_lowzp")
BEFORE={"v1_balanced":"03d2e67a399c31ce7b8456521bcd9cb30a48ef051baa6a9ac50c23cf0bfd0829",
        "v5_hybrid_lowzp":"e7546665bc68faf3d6021db91a77bcdf4d32b4d800530264840f443066ad8ffb"}
AFTER={"v1_balanced":"6057085c39e6fbe777ceea09e78cf4bcd05cc1606dffcbc5ee8e3ae2d32e56e0",
       "v5_hybrid_lowzp":"a29e07795b0dd4e6817ca1adb164603a2afabb4b413b7928ec0da5d753609f01"}
PROOF="validation/review/ISSUE39_V1V5_UMUL8_DIRECTOUT_PRODUCTION_2026-10-13.json"
DOC="docs/ISSUE39_V1V5_UMUL8_DIRECT_OUTPUT_PRODUCTION_2026-10-13.md"
MARK="2026-10-13 ISSUE39 V1/V5 UMUL8 DIRECT-OUTPUT SOURCE PRODUCTION"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def image(profile):return R/profile/"resident"/f"math_{profile}_game_math.prg"
def py(tool,*args):
    cmd=[sys.executable,str(R/"tools"/(tool+".py")),*map(str,args)]
    print("RUN",*cmd,flush=True)
    subprocess.run(cmd,cwd=R,check=True)
def output(profile,kind):
    base=(R/"build_hybrid" if profile==PROFILES[-1] else R/"build_source")/kind/profile
    info=json.loads((base/"source_build_manifest.json").read_text())
    return base/info["output_prg"],info
def build():
    for kind in ("reference","alternate"):
        py("assemble_sources","--profile","all","--config-kind",kind)
        py("build_hybrid","--config-kind",kind)
def integrate_generator():
    p=R/"tools/source_relocation.py";s=p.read_text()
    begin=s.index("'v1_balanced':(",s.index("MULTIPLY_REFRESH_INCLUDES"))
    end=s.index("'v2_pareto_fast':(",begin)
    region=s[begin:end]
    assert "'umul8_directout.inc'" not in region,"already integrated"
    if "'umul8_directout_trial.inc'" in region:
        updated=region.replace("'umul8_directout_trial.inc'","'umul8_directout.inc'",1)
    else:
        tail="'umul16_shr8_reg_return.inc'),"
        assert region.count(tail)==1,repr(region)
        updated=region.replace(tail,tail[:-2]+",\\n  'umul8_directout.inc'),")
    s=s[:begin]+updated+s[end:]
    trial=R/"relocatable_source/v1_balanced/umul8_directout_trial.inc"
    assert trial.is_file()
    canon=trial.with_name("umul8_directout.inc")
    assert not canon.exists(), "production include already exists unexpectedly"
    canon.write_text("; Canonical zero-growth V1/V5 UMUL8 direct public result.\n"
                     + "\n".join(trial.read_text().splitlines()[2:])+"\n")
    p.write_text(s)
def update_csv(result):
    p=R/"v1_balanced/PUBLIC_PERFORMANCE.csv"
    with p.open(newline="") as f:rows=list(csv.DictReader(f))
    matches=[r for r in rows if r["operation"]=="math_umul8"];assert len(matches)==1
    matches[0].update(avg_cycles=f'{result["mean_cycles"]:.6f}',
                      min_cycles=str(result["min_cycles"]),max_cycles=str(result["max_cycles"]),
                      cases="65536",edge_cases="65536",
                      evidence="2026-10-13 V1/V5 direct output exhaustive 8x8 common corpus")
    with p.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(rows)
def perf_md(mean):
    p=R/"PERFORMANCE.md";lines=p.read_text().splitlines()
    matches=[i for i,l in enumerate(lines) if l.startswith("| "+chr(96)+"MATH_UMUL8"+chr(96)+" |")]
    assert len(matches)==1
    fields=lines[matches[0]].split("|")
    for col in (3,7):fields[col]=" "+f"{mean:.6f}"+" "
    lines[matches[0]]="|".join(fields)
    p.write_text("\n".join(lines)+"\n")
def main():
    statefile=R/"RELEASE_STATUS.json";state=json.loads(statefile.read_text())
    old={p:sha(image(p)) for p in PROFILES}
    assert old==state["reference_prg_sha256"],"baseline changed"
    assert all(old[p]==BEFORE[p] for p in FAST),"wrong V1/V5 baseline"
    integrate_generator()
    py("generate_sources");build()
    new={p:sha(output(p,"reference")[0]) for p in PROFILES}
    assert all(new[p]==AFTER[p] for p in FAST),("candidate drift",new)
    assert all(new[p]==old[p] for p in PROFILES[1:4]),"non-target profiles changed"
    delta={}
    for p in FAST:
        a=image(p).read_bytes();b=output(p,"reference")[0].read_bytes()
        assert len(a)==len(b) and a[:2]==b[:2],"resident growth"
        origin=int.from_bytes(a[:2],"little")
        diffs={origin+i for i,(x,y) in enumerate(zip(a[2:],b[2:])) if x!=y}
        required={0x3014,0x3015,*range(0x4714,0x471d)}
        assert diffs==required,(p,"unexpected changed bytes",sorted(map(hex,diffs)))
        delta[p]=len(diffs)
        shutil.copyfile(output(p,"reference")[0],image(p))
    py("generate_sources");build()
    assert all(sha(output(p,"reference")[0])==sha(image(p)) for p in PROFILES),"source roundtrip"
    assert all(len(output(p,"alternate")[1]["public_entries"])==56 for p in FAST)
    alternate={p:output(p,"alternate")[1]["output_sha256"] for p in PROFILES}
    for kind in ("reference","alternate"):
        py("validate_source_build","v1_balanced","--build",f"build_source/{kind}",
           "--out",f"validation/issue39_umul8_v1v5/{kind}")
    means={}
    for p in FAST:
        cpu,api=load(p)
        res=run_full(cpu,api,"MATH_UMUL8",8,CORPORA[8])
        assert res["cases"]==65536 and res["errors"]==0
        assert abs(res["mean_cycles"]-84.490234375)<1e-9,(p,res)
        means[p]=res
    assert means[FAST[0]]==means[FAST[1]],means
    update_csv(means[FAST[0]])
    perf_md(means[FAST[0]]["mean_cycles"])
    for step in ("validate_signed_multiply","benchmark_unsigned_common_corpus",
                 "benchmark_unsigned_3216_workloads","audit_issue39_unsigned_small_workloads",
                 "publish_standalone_sources","generate_consolidated_routine_table",
                 "generate_public_indexes","validate_public_catalog",
                 "validate_standalone_sources","verify_deterministic_rebuild",
                 "validate_unsigned_division","validate_signed_division"):
        py(step)
    report={"status":"SOURCE_STAGED_CURRENT_NATIVE_256_PASS_PR_CI_PENDING",
       "date":"2026-10-13","profiles_modified":FAST,
       "old_sha256":{p:old[p] for p in FAST},
       "new_sha256":{p:new[p] for p in FAST},
       "paired_cycles_before":90.490234375,
       "paired_cycles_after":84.490234375,
       "paired_savings_each":6,"exhaustive_pairs_per_profile":65536,
       "native_vice_current_source_calls":256,
       "native_vice_cycles_measured":False,
       "unchanged_profiles":[p for p in PROFILES if p not in FAST],
       "changed_bytes_per_profile":delta,
       "extra_normal_zp":0,"resident_size_growth":0,
       "alternate_sha256":{p:alternate[p] for p in FAST},
       "issue39_complete":False}
    evidence=R/PROOF;evidence.parent.mkdir(parents=True,exist_ok=True)
    evidence.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    doc=R/DOC
    doc.write_text("# Issue39 V1/V5 UMUL8 direct-output production stage\n\n"
      "13 October 2026. Source and deployable PRGs staged on the PR branch. "
      "Pending full PR and post-merge main CI. Issue #39 remains open.\n\n"
      "The low product byte goes directly to public MATH_Z in the quarter-square core, "
      "eliminating an intermediate ZP store and public reload. "
      "The final public tail is CLC/RTS. Exact 11-byte delta in each resident. "
      "No ZP, resident length, table, stack or stable ABI growth.\n\n"
      "Identical complete 65,536-pair public-input model: "
      "90.490234375 to 84.490234375 cycles on V1 and V5 "
      "(six cycles saved on every input). The historical published V1 average "
      "90.494644 came from a different harness and must not be used for paired "
      "subtraction. Both source maps checked, complete 56-entry V1 relocation "
      "screen passed, and current-main x64sc replay had 256 old/new public calls "
      "with all guaranteed invariants identical; native cycle timing was not measured. "
      "V2, V3 and V4 residents are unchanged. No private OptiSearch material is published.\n")
    note=(MARK+"\n- V1 and V5 UMUL8 low-result direct store: exhaustive public same-input "
       "six-cycle gain, 90.490234375 to 84.490234375 cycles; current-source "
       "256-call native VICE public replay passed. Eleven byte substitutions "
       "per resident, no resource growth, V2-V4 unchanged. "
       "Full PR/main CI pending. "+DOC+"\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        f=R/name
        if MARK not in f.read_text():f.write_text(note+f.read_text())
    state["reference_prg_sha256"]=new
    state["alternate_prg_sha256"]=alternate
    state["issue39_v1v5_umul8_directout_research_2026_10_13"]["status"]="PROMOTED_AS_SOURCE_STAGED_PR_CI_PENDING"
    state["issue39_v1v5_umul8_directout_production_2026_10_13"]=report
    for key,path,keyname in (
      ("issue39_common_input_unsigned_divmod","validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json","benchmark_sha256"),
      ("issue39_unsigned_3216_multiworkload_2026_10_11","validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json","report_sha256"),
      ("issue39_unsigned_small_width_workloads_2026_10_11","validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json","data_sha256")):
        if isinstance(state.get(key),dict) and (R/path).exists():state[key][keyname]=sha(R/path)
    statefile.write_text(json.dumps(state,indent=2)+"\n")
    # The preflight's scratch trees must not enter the user distribution.
    for f in ("build_umul8_before","build_umul8_after"):
        shutil.rmtree(R/f,ignore_errors=True)
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal()
        py("package_audit")
    print("ISSUE39 V1/V5 UMUL8 PRODUCTION STAGE PASS",flush=True)
if __name__=="__main__":
    main()
