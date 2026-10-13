#!/usr/bin/env python3
"""Reseal SHA provenance of independently reproduced historic DIV/MOD proofs.

The root release changes only the stock resident ISQRT16 island, yet older
arithmetic report bodies pin the complete pre-root resident hash. Run the
complete independent unsigned qualification pipeline, ensure every changed
proof value is *only* a verified old-resident -> new-resident SHA replacement,
and refresh historical certificate hashes in RELEASE_STATUS. Do not relax
arithmetic validation or rewrite earlier cycle measurements.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from issue39_root_historical_parent import ROOT_IMAGES
from stage_issue39_v1_3216_ool_release import reseal

STEPS=(
 "benchmark_unsigned_common_corpus",
 "validate_v5_umod24_frontend",
 "validate_v5_umod16_frontend",
 "validate_udiv32_qone_bound",
 "validate_udiv32_q23_bound",
 "validate_v1_3216_unroll",
 "audit_issue39_zero_high_bypass",
 "audit_v5_3232_narrow_delegate",
 "audit_issue39_unsigned_small_workloads",
 "audit_issue39_v1_24narrow_rejection",
 "audit_v1_udiv24_byte8",
 "audit_v1_3232_d8_delegate",
 "audit_issue39_v1v5_umod8_guard",
 "benchmark_unsigned_3216_workloads",
 "generate_public_indexes",
 "validate_public_catalog",
)
SHA_TRANSITIONS={old:new for old,new,_,_ in ROOT_IMAGES.values()}
def sha(blob):return hashlib.sha256(blob).hexdigest()
def oldfile(path):
    r=subprocess.run(["git","show","HEAD:"+path],cwd=ROOT,
       capture_output=True,check=False)
    return r.stdout if r.returncode==0 else None
def changed_keypaths(a,b,path=()):
    if type(a)!=type(b):return [(path,a,b)]
    if isinstance(a,dict):
        if set(a)!=set(b):return [(path+".keys",sorted(a),sorted(b))]
        return sum((changed_keypaths(a[k],b[k],(*path,k)) for k in a),[])
    if isinstance(a,list):
        if len(a)!=len(b):return [(path+".length",len(a),len(b))]
        return sum((changed_keypaths(a[i],b[i],(*path,i)) for i in range(len(a))),[])
    return [] if a==b else [(path,a,b)]
def main():
    current=json.loads((ROOT/"RELEASE_STATUS.json").read_text())
    assert current["issue39_integer_roots_source_release_2026_10_13"]["status"]=="PASS_NATIVE_VICE_SOURCE_INSTALLED_PR_CI_PENDING"
    for profile,(old,new,_,_) in ROOT_IMAGES.items():
        img=ROOT/profile/"resident"/("math_"+profile+"_game_math.prg")
        assert sha(img.read_bytes())==new
    for tool in STEPS:
        print("RESCORE/VALIDATE",tool,flush=True)
        subprocess.run([sys.executable,str(ROOT/"tools"/(tool+".py"))],
                       check=True,cwd=ROOT)
    dirty=subprocess.check_output(["git","diff","--name-only","--","validation/review",
                                  "benchmarks","validation/PUBLIC_SOURCE_CATALOG_AUDIT.json"],
                                 cwd=ROOT,text=True).splitlines()
    print("CHANGED_REPRODUCED_REPORTS",dirty,flush=True)
    verified=[]
    for rel in dirty:
        before_bytes=oldfile(rel)
        assert before_bytes is not None,(rel,"new/unexpected untracked report")
        after_bytes=(ROOT/rel).read_bytes()
        if rel.endswith(".csv"):
            assert before_bytes==after_bytes,(rel,"unexpected numerical CSV drift")
            continue
        if not rel.endswith(".json"):
            assert before_bytes==after_bytes,(rel,"unexpected non-JSON report drift")
            continue
        before=json.loads(before_bytes);after=json.loads(after_bytes)
        changes=changed_keypaths(before,after)
        assert changes,(rel,"JSON formatting change without evidence change")
        for key,ov,nv in changes:
            assert isinstance(ov,str) and isinstance(nv,str)
            assert SHA_TRANSITIONS.get(ov)==nv,(
              rel,key,"non-root provenance changed",str(ov)[:50],str(nv)[:50])
        verified.append({"file":rel,"sha256_before":sha(before_bytes),
                         "sha256_after":sha(after_bytes),
                         "root_sha_only_changes":len(changes)})
    # Refresh references that point to the previous *report* hash, never
    # overwrite the dated historical benchmark's own prior-resident fields.
    for record in current.values():
        if not isinstance(record,dict):continue
        for k,v in list(record.items()):
            if not (isinstance(v,str) and k.endswith("sha256")):continue
            for p in verified:
                if v==p["sha256_before"]:
                    record[k]=p["sha256_after"]
    path=ROOT/"validation/review/ISSUE39_ROOTS_LEGACY_PROVENANCE_RESEAL.json"
    path.write_text(json.dumps({"status":"PASS_ONLY_SHA_PIN_CHANGES",
       "source_modified_root_profiles":list(ROOT_IMAGES),
       "replayed_proof_tools":list(STEPS),
       "reproduced_reports":verified,
       "arithmetic_binary_change_since_root_release":False},indent=2)+"\n")
    (ROOT/"RELEASE_STATUS.json").write_text(json.dumps(current,indent=2)+"\n")
    note=("2026-10-13 ISSUE39 ROOT RELEASE HISTORIC DIV/MOD HASH RESEAL\n"
          "- Replayed all comparable unsigned proofs with exactly the same"
          " division code. Historical reports updated only their full-resident"
          " provenance hashes for the ISQRT16-only byte-island release;"
          " numeric results, ABI, operands and cycle-stream hashes remained"
          " unchanged. validation/review/ISSUE39_ROOTS_LEGACY_PROVENANCE_RESEAL.json.\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        f=ROOT/name
        if "ISSUE39 ROOT RELEASE HISTORIC DIV/MOD HASH RESEAL" not in f.read_text():
            f.write_text(note+f.read_text())
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(ROOT/"tools/package_audit.py")],
                       cwd=ROOT,check=True)
    print("ISSUE39 ROOT RELEASE HISTORICAL PROVENANCE EXACTLY RESEALED",flush=True)
if __name__=="__main__":main()
