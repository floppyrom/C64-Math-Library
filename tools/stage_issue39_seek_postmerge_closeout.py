#!/usr/bin/env python3
"""Issue39 final, independently observed main postmerge closeout.

Publishes a SHA- and Actions-run-pinned final certificate, changelog,
RELEASE_STATUS and package manifest. No routine, resident PRG or REU changes.
"""
from __future__ import annotations
import hashlib,json,os,subprocess,sys,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal

REPO="floppyrom/C64-Math-Library"
MERGE="d296ace693543025f8aba582a0c933c867939a3a"
RUNS={"full_library":38633755150,"comparable_unsigned":38633755164,
      "fixed_multiply":38633754914}
DOC="docs/ISSUE39_SEEK_FAMILY_COMPLETION_2026-10-14.md"
CERT="validation/review/ISSUE39_SEEK_FAMILY_POSTMERGE_MAIN_CERT_2026-10-14.json"
STAMP="2026-10-14 ISSUE39 CAMPAIGN MAIN POSTMERGE CERTIFICATION"
P=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")

def sha(data):return hashlib.sha256(data).hexdigest()
def get_run(run_id):
    headers={"User-Agent":"C64ML-Issue39-Postmerge-Cert/1.0",
             "Accept":"application/vnd.github+json"}
    if os.getenv("GH_API_TOKEN"):
        headers["Authorization"]="Bearer "+os.environ["GH_API_TOKEN"]
    req=urllib.request.Request(
       f"https://api.github.com/repos/{REPO}/actions/runs/{run_id}",
       headers=headers)
    with urllib.request.urlopen(req,timeout=30) as fh:body=json.load(fh)
    assert body["head_sha"]==MERGE,(run_id,"incorrect merged SHA",body["head_sha"])
    assert body["event"]=="push",(run_id,"not postmerge")
    assert body["status"]=="completed" and body["conclusion"]=="success",(
        run_id,"main postmerge workflow not green",body["status"],body["conclusion"])
    return {"id":run_id,"status":"success","commit":MERGE,
            "url":body["html_url"],"event":"push","workflow":body["name"]}

def main():
    verified={name:get_run(run_id) for name,run_id in RUNS.items()}
    statepath=R/"RELEASE_STATUS.json"
    state=json.loads(statepath.read_text())
    previous=state["issue39_seek_family_completion_2026_10_14"]
    assert previous["status"]=="PASS_FAMILY_AUDIT_MAIN_POSTMERGE_PENDING"
    assert previous["all_eight_public_ops_audited"]
    assert previous["native_step_calls"]==640
    audit=json.loads((R/previous["certificate"]).read_text())
    assert audit["status"]=="PASS_FAMILY_AUDIT_WITH_NO_NEW_PRODUCTION_CANDIDATE"
    assert audit["binary_unchanged"] and audit["abi_unchanged"]
    benchmark=json.loads((R/"validation/movement/SEEK_PROFILE_BENCHMARK.json").read_text())
    assert benchmark["status"]=="PASS"
    assert state["reference_prg_sha256"]==benchmark["prg_sha256"]
    for p in P:
        src=R/p/"resident"/f"math_{p}_game_math.prg"
        assert sha(src.read_bytes())==benchmark["prg_sha256"][p],p
    status="PASS_COMPLETE_POSTMERGE_MAIN_GREEN"
    previous.update({"status":status,"main_ci_postmerge_certified":True,
                     "issue39_closeout_pending":False,
                     "postmerge_main_commit":MERGE,"main_run_ids":RUNS,
                     "postmerge_certificate":CERT})
    state["issue39_campaign_completion_2026_10_14"]={
      "status":status,"all_existing_families_audited":True,
      "all_issue39_family_checkboxes_complete":True,
      "seek_family_public_variants":8,
      "main_commit":MERGE,"runs":RUNS,"certificate":CERT,
      "private_optisearch_published":False,
      "production_prgs_and_reu_unchanged_in_closeout":True}
    statepath.write_text(json.dumps(state,indent=2)+"\n")
    proof={"status":status,"main_merge_commit":MERGE,
           "verified_postmerge_runs":verified,
           "public_profile_prg_sha256":benchmark["prg_sha256"],
           "seek_audit":"validation/review/ISSUE39_SEEK_FAMILY_FINAL_AUDIT_2026-10-14.json",
           "native_evidence":"validation/review/ISSUE39_SEEK_ALL_MODES_NATIVE_VICE_2026-10-14.json",
           "all_slot_evidence":"validation/review/ISSUE39_SEEK_ALL_SLOTS_RESEARCH_2026-10-14.json",
           "stable_abi":True,"production_prgs_unchanged":True,
           "reu_unchanged":True,"native_cycle_timing_measured":False,
           "optisearch_private_code_published":False,
           "no_new_shortcut_promoted":True}
    (R/CERT).write_text(json.dumps(proof,indent=2,sort_keys=True)+"\n")
    docfile=R/DOC
    footer=("\n## Independently verified main post-merge closeout\n\n"
            "All existing Issue #39 optimization families have now been "
            "audited, with released improvements and no additional "
            "qualified SEEK specialist. This is not a global proof of "
            "algorithmic optimality. The following push-triggered "
            "post-merge main runs passed on commit "+MERGE+":\n\n"
            +"\n".join("- "+name+": "+row["url"] for name,row in verified.items())
            +"\n\nFinal certificate: "+CERT+"\n")
    old_doc=docfile.read_text()
    if "## Independently verified main post-merge closeout" not in old_doc:
        docfile.write_text(old_doc+footer)
    note=(STAMP+"\n- Completed the full Issue #39 audit: all eight"
          " SEEK8/16 public operations qualified with V1-V5 reference"
          "/alternate sources, native VICE/REU checks and 408-byte"
          " mixed-state safety. Three independent main push workflows"
          " green at "+MERGE+" (full library, comparable unsigned,"
          " fixed multiply). No additional unqualified shortcut,"
          " no public ABI/PRG/REU/ZP changes; rejected V2 memory"
          " overlap documented, private OptiSearch excluded."
          " Final status, evidence and package SHA256 sealed. "+CERT+"\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        path=R/name
        if STAMP not in path.read_text():path.write_text(note+path.read_text())
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,"tools/package_audit.py"],cwd=R,check=True)
    print("ISSUE39 POSTMERGE CERTIFICATION GREEN, READY FOR CLOSURE",flush=True)

if __name__=="__main__":main()
