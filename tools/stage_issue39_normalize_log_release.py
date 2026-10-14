#!/usr/bin/env python3
"""Guarded Issue39 normalizer branch-collapse production stage (not final merge).

Only V1/V2/V5 NORMALIZE log-code pages can change in shipped PRGs. Require
1,073,960 exact public calls, unchanged outputs/precision and 320 genuine
native VICE calls. Keep V3/V4 REU binaries byte-identical. Re-run all pinned
unsigned rankings before regenerating standalone/index/performance metadata.
"""
from pathlib import Path
import csv,hashlib,json,subprocess,sys,shutil
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from assemble_sources import parse_config
from stage_issue39_v1_3216_ool_release import reseal
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
STOCK=(P[0],P[1],P[4])
OP="MATH_VEC2_NORMALIZE_Q8_8"
PROOF="validation/review/ISSUE39_NORMALIZE_BRANCH_COLLAPSE_RESEARCH_2026-10-14.json"
NATIVE="validation/review/ISSUE39_NORMALIZE_BRANCH_COLLAPSE_NATIVE_2026-10-14.json"
CERT="validation/review/ISSUE39_NORMALIZE_LOG_BRANCH_PRODUCTION_2026-10-14.json"
PATCH="validation/review/ISSUE39_NORMALIZE_LOG_BRANCH_PROVENANCE_2026-10-14.json"
DOC="docs/ISSUE39_NORMALIZE_LOG_BRANCH_RELEASE_2026-10-14.md"
KEY="issue39_normalize_log_branch_2026_10_14"
STAMP="2026-10-14 ISSUE39 NORMALIZE LOG-BRANCH REDUCTION PRODUCTION"
def sha(b):return hashlib.sha256(b).hexdigest()
def fh(p):return sha(p.read_bytes())
def py(name,*args):subprocess.run([sys.executable,str(R/"tools"/name),*args],check=True,cwd=R)
def shipped(p):return R/p/"resident"/("math_"+p+"_game_math.prg")
def built(p,kind):
    d=(R/("build_hybrid" if p==P[4] else "build_source")/kind/p)
    m=json.loads((d/"source_build_manifest.json").read_text())
    return d/m["output_prg"]
def rows(path):
    with path.open(newline="") as f:return list(csv.DictReader(f))
def rewrite_rows(path,profile,metric):
    if not path.exists():return
    arr=rows(path);count=0
    for item in arr:
        if item.get("profile") and item["profile"]!=profile:continue
        op=item.get("routine","")
        if op not in ("VEC2_NORMALIZE_Q8_8",OP):continue
        item["mean_cycles"]=str(metric["mean_cycles"])
        item["min_cycles"]=str(metric["min_cycles"])
        item["max_cycles"]=str(metric["max_cycles"])
        item["cases"]=str(metric["cases"])
        count+=1
    assert count==1,(path,profile,count)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(arr[0]),lineterminator="\n")
        w.writeheader();w.writerows(arr)
def main():
    old_state=json.loads((R/"RELEASE_STATUS.json").read_text())
    assert KEY not in old_state
    research=json.loads((R/PROOF).read_text())
    native=json.loads((R/NATIVE).read_text())
    assert research["status"]=="PASS_LOG_BRANCH_COLLAPSE_RESEARCH_NOT_RELEASED"
    assert research["new_public_model_calls"]==1073960
    assert native["status"]=="PASS_NATIVE_VICE_NORMALIZE_BRANCH_COLLAPSE"
    assert native["baseline_and_candidate_calls"]==320
    old_parity=json.loads((R/"validation/normalize/NORMALIZE_PROFILE_PARITY_107396.json").read_text())
    old_common=json.loads((R/"validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json").read_text())
    old_u3216=json.loads((R/"validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json").read_text())
    old_csv=rows(R/"benchmarks/UNSIGNED_3216_WORKLOAD_AUDIT.csv")
    old_prgs={p:shipped(p).read_bytes() for p in P}
    assert {p:sha(old_prgs[p]) for p in P}==old_state["reference_prg_sha256"]
    subprocess.run(["make","normalize"],cwd=R,check=True)
    new_parity=json.loads((R/"validation/normalize/NORMALIZE_PROFILE_PARITY_107396.json").read_text())
    assert new_parity["status"]==old_parity["status"]=="PASS"
    assert new_parity["corpus_sha256"]==old_parity["corpus_sha256"]
    assert new_parity["corpus_vectors"]==old_parity["corpus_vectors"]==107396
    evidence={"status":"PASS_STAGED_NATIVE_VICE_PR_MAIN_CI_PENDING",
       "binary_source":"candidate reference-map source builds",
       "source_model_calls":1073960,"native_vice_calls":320,
       "normalizer_code_bytes_old":881,"normalizer_code_bytes_new":865,
       "stock_code_bytes_saved":16,"normal_zp_growth":0,
       "resident_binary_length_growth":0,
       "REU_images_changed":False,"native_cycles_measured":False,
       "public_abi_changed":False,
       "old_sha256":{},"candidate_sha256":{},"profiles":{}}
    inverse={"status":"PASS_SHA_PINNED_NORMALIZE_ONLY_REVERSIBLE",
       "provenance_parent":"merged PR131 main", "profiles":{}}
    candidate={}
    for oldrow,newrow in zip(old_parity["profiles"],new_parity["profiles"]):
        p=oldrow["profile"];assert newrow["profile"]==p
        for kind in ("reference","alternate"):
            a=oldrow[kind];b=newrow[kind]
            for k in ("backend","cases","output_sha256","max_angle_deg",
                      "max_component_lsb","output_errors","carry_errors",
                      "input_preserve_errors","entry"):
                assert a[k]==b[k],(p,kind,k)
            assert newrow["cycle_vector_mismatches"]==newrow["output_vector_mismatches"]==0
            expected=research["profiles"][p][kind]["candidate_mean_cycles"]
            assert abs(b["mean_cycles"]-expected)<1e-10,(p,kind,b["mean_cycles"],expected)
            delta=a["mean_cycles"]-b["mean_cycles"]
            assert (delta>0.5 if p in STOCK else abs(delta)<1e-10),(p,delta)
        old=old_prgs[p];fresh=built(p,"reference").read_bytes()
        assert len(old)==len(fresh) and old[:2]==fresh[:2]
        oldsha=sha(old);newsha=sha(fresh)
        assert native["profiles"][p]["baseline_sha256"]==oldsha
        assert native["profiles"][p]["candidate_sha256"]==newsha
        assert newsha!=oldsha if p in STOCK else newsha==oldsha
        evidence["old_sha256"][p]=oldsha
        evidence["candidate_sha256"][p]=newsha
        candidate[p]=newsha
        changed=[i for i,(a,b) in enumerate(zip(old,fresh)) if a!=b]
        if p in STOCK:
            cfg=parse_config(R/"relocatable_source"/p/"math_config_reference.inc")
            low=cfg["REG_LOW"]
            base=int.from_bytes(old[:2],"little")
            start=low+0x500-base+2
            stop=low+0x900-base+2
            assert start>=2 and stop<=len(old),(p,start,stop,len(old))
            assert changed and all(start<=i<stop for i in changed),(
                p,"outside normalize code quadrants",changed[:24])
            inverse["profiles"][p]={
                "resident_load":f"${base:04X}",
                "normalizer_code_start":f"${low+0x500:04X}",
                "normalizer_code_stop_exclusive":f"${low+0x900:04X}",
                "original_region_hex":old[start:stop].hex(),
                "original_sha256":oldsha,"new_sha256":newsha,
                "candidate_region_sha256":sha(fresh[start:stop]),
                "changed_byte_count":len(changed)}
            shutil.copyfile(built(p,"reference"),shipped(p))
        else:
            assert not changed,(p,"REU backend drift")
        evidence["profiles"][p]={
            "changed_bytes":len(changed),
            "reference_mean_old":oldrow["reference"]["mean_cycles"],
            "reference_mean_candidate":newrow["reference"]["mean_cycles"],
            "model_saving_mean":oldrow["reference"]["mean_cycles"]-newrow["reference"]["mean_cycles"],
            "reference_output_sha256":newrow["reference"]["output_sha256"],
            "reference_alternate_cycles_equal":True}
        print("NORMALIZE RELEASE CANDIDATE",p,"changed",len(changed),flush=True)
    (R/PATCH).write_text(json.dumps(inverse,indent=2,sort_keys=True)+"\n")
    # Canonical source generation must reconstruct every proposed shipped PRG
    # EXACTLY, including unchanged REU profiles; alternate builds must remain
    # relocatable and deterministic.
    py("generate_sources.py")
    for kind in ("reference","alternate"):
        py("assemble_sources.py","--profile","all","--config-kind",kind)
        py("build_hybrid.py","--config-kind",kind)
    for p in P:
        assert fh(built(p,"reference"))==candidate[p],(p,"canonical reconstruction changed")
    # Refresh provenance for unrelated unsigned routines by rerunning, rather
    # than simply rewriting their old SHA fields.
    py("benchmark_unsigned_common_corpus.py")
    common=json.loads((R/"validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json").read_text())
    assert common["status"]=="PASS" and common["routines"]==old_common["routines"]
    assert common["total_calls"]==old_common["total_calls"]==136335
    for p in P:
        assert common["sources"][p]["resident_sha256"]==candidate[p]
    py("benchmark_unsigned_3216_workloads.py")
    workload=json.loads((R/"validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json").read_text())
    assert workload["status"]=="PASS" and workload["total_calls"]==old_u3216["total_calls"]==30720
    assert workload["workloads"]==old_u3216["workloads"]
    assert all(workload["profile_resident_sha256"][p]==candidate[p] for p in P)
    new_csv=rows(R/"benchmarks/UNSIGNED_3216_WORKLOAD_AUDIT.csv")
    assert len(old_csv)==len(new_csv)==60
    for a,b in zip(old_csv,new_csv):
        assert {k:v for k,v in a.items() if k!="resident_sha256"}=={
           k:v for k,v in b.items() if k!="resident_sha256"}
    for p in STOCK:
        metric=next(row["reference"] for row in new_parity["profiles"] if row["profile"]==p)
        rewrite_rows(R/p/"PUBLIC_PERFORMANCE_GAME_MATH.csv",p,metric)
        # The consolidated game-math CSV is V1–V4 only; V5 is represented
        # by the full PERFORMANCE.md and generated public indexes.
        if p!=P[4]:
            rewrite_rows(R/"docs/PERFORMANCE_GAME_MATH_FINAL.csv",p,metric)
    perfpath=R/"PERFORMANCE.md"
    perf=perfpath.read_text()
    row=next(line for line in perf.splitlines() if line.startswith("| `"+OP+"` |"))
    bits=row.split("|")
    for i,p in enumerate(P):
        m=next(x["reference"]["mean_cycles"] for x in new_parity["profiles"] if x["profile"]==p)
        bits[i+3]=f" {m:.6f} "
    perfpath.write_text(perf.replace(row,"|".join(bits)))
    py("publish_standalone_sources.py")
    py("generate_consolidated_routine_table.py")
    py("generate_public_indexes.py")
    st=old_state
    st["reference_prg_sha256"]=candidate
    alt={}
    for p in P:alt[p]=fh(built(p,"alternate"))
    st["alternate_prg_sha256"]=alt
    if isinstance(st.get("hybrid_v5"),dict):
        st["hybrid_v5"]["reference_prg_sha256"]=candidate[P[4]]
        st["hybrid_v5"]["alternate_prg_sha256"]=alt[P[4]]
    st["vec2_normalize_q8_8"]["mean_cycles"]={
       p:next(row["reference"]["mean_cycles"] for row in new_parity["profiles"] if row["profile"]==p) for p in P}
    st["vec2_normalize_q8_8"]["log_branch_dispatch_code_bytes"]=865
    st["vec2_normalize_q8_8"]["log_branch_dispatch_shrink_bytes"]=16
    st["vec2_normalize_q8_8"]["issue39_branch_optimization"]=KEY
    st["issue39_common_input_unsigned_divmod"]["benchmark_sha256"]=fh(R/"validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json")
    st["issue39_unsigned_3216_multiworkload_2026_10_11"]["report_sha256"]=fh(R/"validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json")
    st[KEY]={"status":"PASS_STAGED_NATIVE_VICE_PR_MAIN_CI_PENDING",
       "public_abi_unchanged":True,"source_relocation_stable":True,
       "source_model_cases":1073960,"native_vice_calls":320,
       "full_precision_cells":723073,"code_bytes_saved":16,
       "stock_profiles":list(STOCK),"old_resident_sha256":evidence["old_sha256"],
       "candidate_resident_sha256":candidate,"inverse_provenance":PATCH,
       "research":PROOF,"native_evidence":NATIVE,"production_certificate":CERT,
       "distance_normalization_family_complete":False,
       "issue39_remains_open_for_seek":True}
    (R/"RELEASE_STATUS.json").write_text(json.dumps(st,indent=2)+"\n")
    (R/CERT).write_text(json.dumps(evidence,indent=2,sort_keys=True)+"\n")
    d=R/"docs/VEC2_NORMALIZE_Q8_8.md"
    txt=d.read_text()
    m=new_parity["profiles"][0]["reference"]
    before="**160.150080** | 0.73% | 84–302 | 881"
    for baseval in ("161.332256",):
        frac=100*(float(baseval)-m["mean_cycles"])/float(baseval)
    after=f"**{m['mean_cycles']:.6f}** | {frac:.2f}% | {m['min_cycles']}–{m['max_cycles']} | 865"
    assert txt.count(before)==3
    txt=txt.replace(before,after)
    intro=(f"**Issue39 logarithmic-branch optimization (14 October 2026):** "
           f"V1/V2/V5 reduce eight unconditional branch-pair decisions to eight "
           f"single BEQ tests, shrinking stock code 881→865 bytes and saving "
           f"{evidence['profiles'][P[0]]['model_saving_mean']:.6f} model cycles "
           f"per 107,396-input public call while keeping exact signed outputs, "
           f"precision and four-byte ZP union. Native x64sc baseline/candidate "
           f"proof covers 320 calls. V3/V4 REU backend is byte-identical. "
           f"Independent PR/main CI pending.\n\n")
    d.write_text(intro+txt)
    (R/DOC).write_text(
      "# Issue39 normalization logarithmic-branch production staging\n\n"
      "The released candidate removes one redundant conditional branch at "
      "each of eight logarithmic ratio dispatch sites in V1/V2/V5. Both "
      "states of each original branch pair are equivalent to the new BEQ; "
      "no output state, carry, scratch or public input changes.\n\n"
      f"Exhaustive model: {research['new_public_model_calls']} signed public calls "
      f"on both reference and alternate maps. Native x64sc: {native['baseline_and_candidate_calls']} "
      "old/new calls, exact public outputs/flags/input preservation. Code "
      "shrinks by 16 bytes per stock implementation without enlarging "
      "resident images; both REU profiles remain unchanged.\n\n"
      "Reproduced 136,335 unsigned DIV/MOD common-corpus and 30,720 UDIV32/16 "
      "workload machine calls with identical numeric metrics; provenance "
      "SHA renewed only after rebenchmark. Historical whole-PRG auditors "
      f"can reconstruct the old exact SHA-pinned resident from `{PATCH}`.\n\n"
      "**Not complete:** independent PR/main CI and migration of archived "
      "parent-only arithmetic proof adapters. Do not merge until green. "
      "Distance/normalization and Issue39 remain open.\n"
    )
    log=(f"## {STAMP}\n\n"
       "Staged smaller log-normalize source for V1/V2/V5: 8 redundant "
       "conditional branch pairs removed, -16 bytes per source, mean "
       f"{m['mean_cycles']:.6f} vs 160.150080 CPU-model cycles (-1.021286). "
       "1,073,960 signed ref/alternate model calls, 320 baseline/candidate "
       "native VICE calls, unchanged full-domain precision and four-byte "
       "ZP; REU profiles untouched. Updated standalone, performance, "
       "corpus provenance, checksum files. Independent PR/main CI pending; "
       f"see `{DOC}`.\n\n---\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        p=R/name
        if STAMP not in p.read_text():p.write_text(log+p.read_text())
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal()
        py("package_audit.py")
    print("ISSUE39 NORMALIZE BRANCH STOCK SOURCE RELEASE STAGED; CI PENDING",flush=True)
if __name__=="__main__":main()
