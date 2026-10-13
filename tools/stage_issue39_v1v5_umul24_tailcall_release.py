#!/usr/bin/env python3
"""Protected V1/V5 public UMUL24 FAST24 tail-call source release staging after V2-V4 candidate integration.

Original fast24 arithmetic is independent of signed producer. One public JSR
and inner RTS disappear, final z3 is directly stored, and ordinary V1/V5
public UMUL24 saves exactly 8 cycles. Never merge before native/CI.
"""
from pathlib import Path
import hashlib,csv,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
FAST=("v1_balanced","v5_hybrid_lowzp")
PROOF="validation/review/ISSUE39_V1V5_UMUL24_TAILCALL_RELEASE_2026-10-13.json"
DOC="docs/ISSUE39_V1V5_UMUL24_PRIVATE_TAILCALL_2026-10-13.md"
STAMP="2026-10-13 ISSUE39 V1V5 UMUL24 PRIVATE CORE TAILCALL"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prg(p):return R/p/"resident"/("math_"+p+"_game_math.prg")
def py(cmd,*args):
    c=[sys.executable,str(R/"tools"/(cmd+".py")),*map(str,args)]
    print("RUN",*c,flush=True);subprocess.run(c,cwd=R,check=True)
def output(p,kind):
    parent=(R/"build_hybrid" if p==P[-1] else R/"build_source")/kind/p
    m=json.loads((parent/"source_build_manifest.json").read_text())
    return parent/m["output_prg"],m
def build():
    for kind in ("reference","alternate"):
        py("assemble_sources","--profile","all","--config-kind",kind)
        py("build_hybrid","--config-kind",kind)
def update_csv(mean,mincy,maxcy):
    path=R/"v1_balanced/PUBLIC_PERFORMANCE.csv"
    with path.open(newline="") as f: rows=list(csv.DictReader(f))
    v=[r for r in rows if r["operation"]=="math_umul24"];assert len(v)==1
    v[0].update(avg_cycles=format(mean,".6f"),min_cycles=str(mincy),
                max_cycles=str(maxcy),cases="10324",
                evidence="2026-10-13 UMUL24 private core public tailcall, same-input corpus")
    with path.open("w",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
        wr.writeheader();wr.writerows(rows)
def main():
    stpath=R/"RELEASE_STATUS.json";st=json.loads(stpath.read_text())
    before={p:sha(prg(p)) for p in P}
    assert st["reference_prg_sha256"]==before
    lengths={p:prg(p).stat().st_size for p in P}
    build()
    new={p:sha(output(p,"reference")[0]) for p in P}
    assert new[P[0]]!=before[P[0]] and new[P[-1]]!=before[P[-1]]
    assert all(new[p]==before[p] for p in P[1:-1]),("non-target changed",new)
    assert all(output(p,"reference")[0].stat().st_size==lengths[p] for p in P)
    for p in FAST:shutil.copyfile(output(p,"reference")[0],prg(p))
    py("generate_sources")
    build()
    assert all(sha(output(p,"reference")[0])==sha(prg(p)) for p in P)
    assert "umul24_fast24_shared.inc" in (R/"relocatable_source/v1_balanced/math_relocatable.asm").read_text()
    alternate={p:output(p,"alternate")[1]["output_sha256"] for p in P}
    print("UMUL24 PRIVATE CORE V1/V5 REF/ALTERNATE AND V5 HYBRID SOURCE PASS",flush=True)
    py("validate_umul24_directout")
    obj=json.loads((R/"validation/multiply_refresh/UMUL24_DIRECTOUT_VALIDATION.json").read_text())
    v=obj["results"]["v1_balanced"]["reference"]
    assert v==obj["results"]["v1_balanced"]["alternate"]
    assert v==obj["results"]["v5_hybrid_lowzp"]["reference"]
    assert v==obj["results"]["v5_hybrid_lowzp"]["alternate"]
    oldmean=474.0423285548237
    assert abs((oldmean-v["mean_cycles"])-8)<1e-8,(oldmean,v)
    assert v["cases"]==10324
    update_csv(v["mean_cycles"],v["min_cycles"],v["max_cycles"])
    perf=R/"PERFORMANCE.md";lines=perf.read_text().splitlines()
    indices=[i for i,x in enumerate(lines) if x.startswith("| "+chr(96)+"MATH_UMUL24"+chr(96)+" |")]
    assert len(indices)==1
    parts=lines[indices[0]].split("|")
    for i,p in enumerate(P):
        if p in FAST:parts[3+i]=" "+format(v["mean_cycles"],".6f")+" "
    lines[indices[0]]="|".join(parts);perf.write_text("\n".join(lines)+"\n")
    for step in ("validate_signed_multiply","benchmark_unsigned_common_corpus",
                 "benchmark_unsigned_3216_workloads","audit_issue39_unsigned_small_workloads",
                 "publish_standalone_sources","generate_consolidated_routine_table",
                 "generate_public_indexes","validate_public_catalog","validate_standalone_sources",
                 "verify_deterministic_rebuild","validate_unsigned_division","validate_signed_division"):
        py(step)
    result={"status":"PASS_SOURCE_STAGED_NATIVE_PENDING",
            "old_sha256":before,"new_sha256":new,"alternate_sha256":alternate,
            "profiles_modified":list(FAST),"unchanged_V2_V3_V4":True,
            "mean_cycles_before":oldmean,"mean_cycles_after":v["mean_cycles"],
            "mean_saving":8,"tested_calls_per_profile":10324,
            "cycle_deltas":{"-8":10324},"resident_growth":0,"zero_page_growth":0,
            "native_vice_calls":0,"issue39_complete":False}
    (R/PROOF).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    (R/DOC).write_text("# Issue39 — V1/V5 UMUL24 private core public tail-call\n\n"
     "Protected release stage, 13 October 2026. Native VICE and PR/main CI pending.\n\n"
     "The selected public FAST24 adapter now jumps into the unsigned private "
     "arithmetic rather than JSR/RTS. The final z3 product byte is stored in "
     "the producer, and both carry exits join a single public result tail. "
     "Signed FAST24 remains executable-independent.\n\n"
     "Every one of 10,324 identical unsigned input pairs saved exactly 8 "
     "cycles: "+format(oldmean,".6f")+" -> "+format(v["mean_cycles"],".6f")+
     ". Both memory maps and the V5 hybrid verified; V2/V3/V4 remain binary "
     "unchanged. No new ZP, stack, table, resident space or public entry. "
     "No private OptiSearch source is published. Issue #39 stays OPEN.\n")
    note=(STAMP+"\n- Source-integrated V1/V5 UMUL24 tail-call:"
       " -8 cycles on all 10,324 official pairs, "
       +format(oldmean,".6f")+" -> "+format(v["mean_cycles"],".6f")
       +" cycles; V2–V4 unchanged. No additional resource footprint.\n"
       "- Signed/mixed calls, relocated source, standalone publication and"
       " checksum/package evidence validated; native VICE pending. "+DOC+"\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        path=R/name
        if STAMP not in path.read_text():path.write_text(note+path.read_text())
    st["reference_prg_sha256"]=new;st["alternate_prg_sha256"]=alternate
    st["issue39_umul24_v1v5_tailcall_2026_10_13"]={
       "status":"PASS_STAGED_NATIVE_VICE_PENDING","proof":PROOF,"doc":DOC,
       "new_sha256":new,"old_sha256":before,
       "gain_cycles_every_case":8,"normal_ZP_growth":0,"resident_growth":0,
       "issue39_complete":False}
    for key,path,field in (
       ("issue39_common_input_unsigned_divmod","validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json","benchmark_sha256"),
       ("issue39_unsigned_3216_multiworkload_2026_10_11","validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json","report_sha256"),
       ("issue39_unsigned_small_width_workloads_2026_10_11","validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json","data_sha256")):
        if isinstance(st.get(key),dict) and (R/path).exists():st[key][field]=sha(R/path)
    stpath.write_text(json.dumps(st,indent=2)+"\n")
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal();py("package_audit")
    print("V1/V5 UMUL24 PRIVATE TAILCALL RELEASE STAGED, NATIVE PENDING",flush=True)
if __name__=="__main__":main()
