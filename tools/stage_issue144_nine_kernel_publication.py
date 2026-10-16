#!/usr/bin/env python3
"""Issue144 P4 reproducible benchmark artifact promotion into permanent SOURCE records.

Only run after both independent benchmark matrix jobs pass. Validate two-map
CSV and JSON identities, 45 API/profile pairs in each, exactly 31,800 checked
public calls, checked frozen hashes and absence of measured negative savings.
Recalculate SHA256SUMS and PACKAGE_AUDIT with an exact whole-tree inventory;
verify package_audit.py produces identical audit bytes. This does not publish
default binaries or change historical PERFORMANCE.md.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
OPS=("MATH_ISQRT32","MATH_SEEK16_INIT","MATH_SMUL32_SHR16",
     "MATH_UMUL32_SHR16","MATH_SMUL32","MATH_UMUL32",
     "MATH_SMOD32_16","MATH_UMOD32_16","MATH_UDIV32_16")
COLUMNS=("profile","layout","routine","calls","frozen_mean","source_mean",
         "mean_saved","frozen_p95","source_p95","p05_saved",
         "worst_saved","best_saved","slower_calls",
         "frozen_prg_sha256","source_prg_sha256")
def h(data):return hashlib.sha256(data).hexdigest()
def load(layout,folder):
    csvfile=folder/f"ISSUE144_NINE_KERNEL_{layout}.csv"
    jsonfile=folder/f"ISSUE144_NINE_KERNEL_{layout}.json"
    assert csvfile.is_file() and jsonfile.is_file(),(layout,"missing passing CI artifacts")
    with csvfile.open(newline="") as fp:
        rd=csv.DictReader(fp); assert tuple(rd.fieldnames)==COLUMNS,rd.fieldnames
        rows=list(rd)
    details=json.loads(jsonfile.read_text())
    assert details["status"]=="PASS_NINE_KERNEL_MATCHED_CANDIDATE_RESEARCH"
    assert details["layout"]==layout
    assert details["source_binary_release_class"]=="candidate_not_shipped"
    assert details["physical_bus_timing_measured"] is False
    assert details["IRQ_NMI_certified"] is False
    assert len(rows)==len(details["benchmark_rows"])==45
    found={(x["profile"],x["routine"]) for x in rows}
    assert found=={(p,k) for p in PROFILES for k in OPS},(layout,len(found))
    assert sum(int(x["calls"]) for x in rows)==15900
    for x,y in zip(rows,details["benchmark_rows"]):
        assert (x["profile"],x["layout"],x["routine"])==(
                y["profile"],y["layout"],y["routine"])
        assert int(x["calls"])==y["calls"]
        assert int(x["slower_calls"])==y["slower_calls"]==0
        assert float(x["mean_saved"])>=0 and int(float(x["worst_saved"]))>=0
        assert len(x["source_prg_sha256"])==len(x["frozen_prg_sha256"])==64
        for key in ("frozen_mean","source_mean","mean_saved","p05_saved"):
            assert abs(float(x[key])-y[key])<1e-9,(layout,key,x[key],y[key])
    return rows,csvfile,jsonfile

def files(root):
    return sorted((p for p in root.rglob("*")
                   if p.is_file() and ".git" not in p.parts),
                  key=lambda p:str(p.relative_to(root)))

def seal(root):
    audit_file=root/"validation/PACKAGE_AUDIT.json"
    manifest_file=root/"SHA256SUMS.txt"
    orig=json.loads(audit_file.read_text())
    contents=[p for p in files(root) if p!=manifest_file]
    assert len(contents)>1960 and len(orig["checks"])==30
    orig["summary"]["file_count_excluding_checksum"]=len(contents)
    orig["summary"]["uncompressed_bytes_excluding_checksum"]=sum(p.stat().st_size for p in contents
                                                      if p!=audit_file)
    ck=next(v for v in orig["checks"] if v["check"]=="sha256_manifest_current")
    ck["detail"]={"bad":[],"missing":[],"extra":[],"entries":len(contents)}
    audit_file.write_text(json.dumps(orig,indent=2)+"\n")
    # Audit includes its own checksum record but cannot hash the manifest,
    # which by contract excludes itself. Its JSON includes the audit's bytes.
    contents=[p for p in files(root) if p!=manifest_file]
    orig["summary"]["uncompressed_bytes_excluding_checksum"]=sum(p.stat().st_size for p in contents)
    audit_file.write_text(json.dumps(orig,indent=2)+"\n")
    # Correct audit byte-total fixed point once; decimal lengths can change.
    for _ in range(5):
        total=sum(p.stat().st_size for p in contents)
        if orig["summary"]["uncompressed_bytes_excluding_checksum"]==total:break
        orig["summary"]["uncompressed_bytes_excluding_checksum"]=total
        audit_file.write_text(json.dumps(orig,indent=2)+"\n")
    else:raise AssertionError("package audit byte-total did not converge")
    assert orig["summary"]["uncompressed_bytes_excluding_checksum"]==sum(p.stat().st_size for p in contents)
    manifest_file.write_text("".join(f"{h(p.read_bytes())}  {p.relative_to(root).as_posix()}\n"
                                     for p in contents))
    audit_before=audit_file.read_bytes()
    p=subprocess.run([sys.executable,str(root/"tools/package_audit.py")],
                     cwd=root,capture_output=True,text=True)
    assert p.returncode==0,(p.stdout[-4000:],p.stderr[-4000:])
    assert audit_file.read_bytes()==audit_before,("package audit non-deterministic",)
    assert not (root/"PERFORMANCE.md").read_text().find("MATH_ISQRT32")==-1
    return {"entries":len(contents),"manifest_sha256":h(manifest_file.read_bytes()),
            "audit_sha256":h(audit_file.read_bytes()),"audit_checks":len(orig["checks"])}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--reference",required=True,type=Path)
    ap.add_argument("--alternate",required=True,type=Path)
    a=ap.parse_args()
    rowpairs={}
    for layout,where in (("reference",a.reference),("alternate",a.alternate)):
        rows,ci_csv,ci_json=load(layout,where)
        for field,subdir in ((ci_csv,"benchmarks"),(ci_json,"validation/review")):
            name=("ISSUE144_NINE_KERNEL_SOURCE_"+layout.upper()+"_2026-10-16"+field.suffix)
            dst=ROOT/subdir/name
            assert not dst.exists(),("refuse overwrite published data",dst)
            shutil.copy2(field,dst)
            # Python's default csv.writer emits CRLF; GitHub's diff --check
            # treats the carriage return as trailing whitespace. Re-encode
            # the *same* 45-row logical CSV using repository LF convention.
            if field.suffix==".csv":
                original=dst.read_bytes()
                assert b"\\r\\n" in original
                dst.write_bytes(original.replace(b"\\r\\n",b"\\n"))
            print("STAGED",dst.relative_to(ROOT),h(dst.read_bytes()),flush=True)
        rowpairs[layout]={(x["profile"],x["routine"]):x for x in rows}
    for key,a in rowpairs["reference"].items():
        b=rowpairs["alternate"][key]
        for field in ("calls","frozen_mean","source_mean","mean_saved",
                      "frozen_p95","source_p95","p05_saved","worst_saved",
                      "best_saved","slower_calls","frozen_prg_sha256"):
            assert a[field]==b[field],("reference/alternate mismatch",key,field)
    report={"status":"PASS_NINE_KERNEL_TWO_MAP_PERMANENT_EVIDENCE",
            "date":"2026-10-16","profiles":list(PROFILES),"apis":list(OPS),
            "source_candidate_only":True,"tagged_release":False,
            "physical_REU_VIC_DMA_elapsed_time_proven":False,
            "IRQ_NMI_reentrant_proven":False,
            "all_api_rows_per_map":45,"compared_public_calls_per_map":15900,
            "total_matched_public_calls":31800,
            "source_and_historical_PRG_hashes_per_row":True,
            "no_slowed_input_measured":True,
            "exact_same_result_both_relocation_maps":True,
            "source":"tools/issue144_nine_kernel_candidate_benchmark.py",
            "workflow":".github/workflows/issue144-nine-kernel-candidate.yml",
            "original_actions_run":38878974907}
    dst=ROOT/"validation/review/ISSUE144_NINE_KERNEL_CROSSMAP_2026-10-16.json"
    assert not dst.exists()
    dst.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    release=ROOT/"RELEASE_STATUS.json"
    status=json.loads(release.read_text())
    key="issue144_nine_kernel_source_candidate_benchmark_2026_10_16"
    assert key not in status
    status[key]={**report,
                 "reference_csv":"benchmarks/ISSUE144_NINE_KERNEL_SOURCE_REFERENCE_2026-10-16.csv",
                 "alternate_csv":"benchmarks/ISSUE144_NINE_KERNEL_SOURCE_ALTERNATE_2026-10-16.csv",
                 "crossmap_record":str(dst.relative_to(ROOT))}
    release.write_text(json.dumps(status,indent=2)+"\n")
    changelog_note=(
      "2026-10-16 ISSUE144 NINE-KERNEL MATCHED SOURCE-CANDIDATE SCORECARD\n"
      "- 31,800 same-input public model calls across V1-V5 and reference/alternate maps; all nine original expensive kernels, arithmetic and SEEK STEP oracle pass, zero measured slowdowns.\n"
      "- Source-vs-frozen mean savings: ISQRT32 V1/V5 -51, V2/V3 -47, V4 -135.205; SEEK16_INIT V1/V5 -1.913, V2 -14.029, V3/V4 -12.435; V2-V4 UDIV/UMOD32_16 -3.743 and SMOD32_16 -6.707. Four 32x32/SHR16 multiply APIs unchanged.\n"
      "- Both-map 45-row CSV/JSON and crossmap SHA-provenance permanently retained. CPU cycles only, not physical REU/VIC/DMA/IRQ timing; no frozen binaries or historical PERFORMANCE changes. Issue #144 remains open.\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        f=ROOT/name
        text=f.read_text()
        assert "ISSUE144 NINE-KERNEL MATCHED SOURCE-CANDIDATE SCORECARD" not in text
        f.write_text(changelog_note+text)
    sealed=seal(ROOT)
    print(json.dumps({"status":report["status"],**sealed},indent=2))
if __name__=="__main__":main()
