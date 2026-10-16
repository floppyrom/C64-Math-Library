#!/usr/bin/env python3
"""Issue144: immutable, verified, versioned five-profile candidate distribution.

Does not overwrite the seven historical default PRG/REU images or PERFORMANCE.md.
Physical REU/VIC/IRQ safety is not certified by CPU-model tests.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, os, re, sys
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from issue144_isqrt32_release_candidate import create, frozen_seals, PROFILES

REU={"v3_reu_512k":524288,"v4_reu_16m":16777216}
DATE=(2026,10,16,0,0,0)
def sha(x):return hashlib.sha256(x).hexdigest()
def record(x):return (json.dumps(x,indent=2,sort_keys=True)+'\n').encode()

def render_benchmark(rows):
    columns=("profile","corpus_inputs","frozen_mean_cycles","current_source_mean_cycles",
             "saved_mean_cycles","frozen_p95","current_p95","minimum_saved",
             "maximum_saved","slower_inputs","source_prg_sha256")
    buf=io.StringIO(newline='')
    w=csv.writer(buf,lineterminator='\n');w.writerow(columns)
    for p in rows:
        m=p["isqrt32_same_input"]
        w.writerow((p["profile"],m["samples"],f'{m["frozen_mean_cycles"]:.6f}',
            f'{m["candidate_mean_cycles"]:.6f}',f'{m["mean_saved_cycles"]:.6f}',
            m["frozen_p95_cycles"],m["candidate_p95_cycles"],
            m["minimum_saved_cycles"],m["maximum_saved_cycles"],
            m["slower_calls"],p["candidate_prg_sha256"]))
    return buf.getvalue().encode()

def collect(stage,version,revision):
    files={};results={};frozen=frozen_seals()
    for layout in ("reference","alternate"):
        base=stage/layout
        report=json.loads((base/"ISSUE144_RELEASE_CANDIDATE.json").read_text())
        assert report["status"]=="PASS_SOURCE_BUILT_CANDIDATE_NOT_SHIPPED"
        assert report["historical_binaries_unchanged"] and report["performance_md_unchanged"]
        assert report["frozen_sha256"]==frozen
        assert len(report["profiles"])==5
        assert {x["profile"] for x in report["profiles"]}==set(PROFILES)
        results[layout]=report
        files[f"qualification/{layout}.json"]=record(report)
        for item in report["profiles"]:
            p=item["profile"];dir=base/"profiles"/p
            assert item["public_abi_entries_executed"]==56
            assert item["public_model_calls"]>=21000
            manifest=json.loads((dir/"source_build_manifest.json").read_text())
            prg=base/item["candidate_prg"]
            assert prg.parent==dir and prg.name==manifest["output_prg"]
            assert sha(prg.read_bytes())==manifest["output_sha256"]==item["candidate_prg_sha256"]
            assert len(manifest["public_entries"])==56
            for f in (prg,dir/"math_api.inc",dir/"source_build_manifest.json"):
                assert f.is_file()
                files[f"profiles/{layout}/{p}/{f.name}"]=f.read_bytes()
            if p in REU:
                reu=base/item["candidate_reu"]
                assert reu.parent==dir and reu.stat().st_size==REU[p]
                assert sha(reu.read_bytes())==item["candidate_reu_sha256"]
                assert manifest["reu_image"]["sha256"]==item["candidate_reu_sha256"]
                files[f"profiles/{layout}/{p}/{reu.name}"]=reu.read_bytes()
            else:
                assert item["candidate_reu"] is None
    a,b=results["reference"],results["alternate"]
    assert a["same_input_isqrt_corpus_sha256"]==b["same_input_isqrt_corpus_sha256"]
    for row in a["profiles"]:
        m=row["isqrt32_same_input"]
        assert m["samples"]>=400 and m["slower_calls"]==0
        assert m["mean_saved_cycles"]>0
        if row["profile"]=="v4_reu_16m":
            assert 133.0<m["mean_saved_cycles"]<138.0,"V4 source must include PR192 16-cycle DMA promotion"
    files["benchmarks/ISQRT32_MATCHED_INPUTS.csv"]=render_benchmark(a["profiles"])
    total=sum(x["public_model_calls"] for q in results.values() for x in q["profiles"])
    summary={"version":version,"source_commit":revision,
        "qualification":"CANDIDATE_NOT_SHIPPED_DEFAULT","five_profiles":list(PROFILES),
        "memory_maps":["reference","alternate"],"public_entries_per_profile":56,
        "public_calls_checked":total,"root_corpus_sha256":a["same_input_isqrt_corpus_sha256"],
        "frozen_historical_binary_sha256":frozen,
        "native_vice_root_qualification":"separate pinned x64sc CI required",
        "physical_pal_ntsc_vic_reu_dma_measured":False,
        "irq_nmi_reentrancy_certified":False,
        "production_default_promoted":False}
    files["QUALIFICATION_SUMMARY.json"]=record(summary)
    files["README.md"]=(
        f"# C64 Math Library {version}\n\nSource revision {revision}.\n\n"
        "Source-built candidate ONLY. The seven historical packaged PRG/REU"
        " files and the existing published PERFORMANCE.md have not changed.\n\n"
        "Each memory map includes five PRGs, V3/V4 REUs, caller math_api.inc"
        " headers and 56-entry source-build manifests. Never pair an alternate"
        " caller header with a reference-map binary. The benchmark CSV uses the"
        " same 438 N32 operands for old and new public ISQRT32 calls.\n\n"
        "CPU model cycles exclude physical DMA/bus stalls and IRQ/NMI latency."
        " A separate native VICE qualification is needed, and actual hardware"
        " testing remains unperformed. This ZIP is not a tagged default release.\n").encode()
    return files

def pack(dst,files,revision):
    index={"source_revision":revision,"status":"PASS_SOURCE_CANDIDATE",
           "files":{p:{"sha256":sha(content),"size":len(content)}
                    for p,content in sorted(files.items())}}
    files={**files,"MANIFEST_SHA256.json":record(index)}
    with ZipFile(dst,"w",ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
        for path in sorted(files):
            info=ZipInfo(path,DATE)
            info.compress_type=ZIP_DEFLATED
            info.external_attr=0o100644<<16
            info.create_system=3
            z.writestr(info,files[path],compress_type=ZIP_DEFLATED,compresslevel=9)

def verify(dst,revision=None):
    with ZipFile(dst) as z:
        assert z.testzip() is None
        names=z.namelist()
        assert len(names)==len(set(names))
        ix=json.loads(z.read("MANIFEST_SHA256.json"))
        assert ix["status"]=="PASS_SOURCE_CANDIDATE"
        if revision is not None: assert ix["source_revision"]==revision
        assert set(ix["files"])|{"MANIFEST_SHA256.json"}==set(names)
        for name,meta in ix["files"].items():
            posix=PurePosixPath(name)
            assert not posix.is_absolute() and '..' not in posix.parts
            data=z.read(name)
            assert len(data)==meta["size"] and sha(data)==meta["sha256"],name
        for layout in ("reference","alternate"):
            report=json.loads(z.read(f"qualification/{layout}.json"))
            assert len(report["profiles"])==5
            for row in report["profiles"]:
                p=row["profile"];base=f"profiles/{layout}/{p}"
                prg=f"{base}/{Path(row['candidate_prg']).name}"
                assert sha(z.read(prg))==row["candidate_prg_sha256"]
                assert f"{base}/math_api.inc" in ix["files"]
                assert f"{base}/source_build_manifest.json" in ix["files"]
                if p in REU:
                    reu=f"{base}/{Path(row['candidate_reu']).name}"
                    assert len(z.read(reu))==REU[p]
    return {"status":"PASS","files":len(ix["files"]),
            "sha256":sha(dst.read_bytes()),"source_revision":ix["source_revision"]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--version")
    parser.add_argument("--out",type=Path)
    parser.add_argument("--verify",type=Path)
    parser.add_argument("--revision",default=os.environ.get("SOURCE_REVISION",os.environ.get("GITHUB_SHA","local")))
    a=parser.parse_args()
    if a.verify:
        print(json.dumps(verify(a.verify,None if a.revision=="local" else a.revision),indent=2))
        return
    if not a.version or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}",a.version) or not a.out:
        parser.error("need --version SAFE_NAME --out OUTSIDE_REPOSITORY")
    out=a.out.resolve()
    assert not out.is_relative_to(ROOT),"Do not write distributables into the source tree"
    out.mkdir(parents=True,exist_ok=True)
    archive=out/f"C64-Math-Library-{a.version}.zip"
    assert not archive.exists(),"Refuse to overwrite an already-published candidate"
    with TemporaryDirectory(prefix="issue144_package_",dir=out) as d:
        stage=Path(d)
        for layout in ("reference","alternate"):
            create(layout,stage/layout,layout=="reference")
        files=collect(stage,a.version,a.revision)
        pack(archive,files,a.revision)
    result=verify(archive,a.revision)
    (out/(archive.name+".sha256")).write_text(result["sha256"]+"  "+archive.name+"\n")
    (out/"DISTRIBUTION_STATUS.json").write_bytes(record({
        **result,"version":a.version,"release_class":"candidate_only",
        "physical_vic_reu_dma_irq_certified":False}))
    print(json.dumps({"status":"PASS_VERSIONED_CANDIDATE_NOT_SHIPPED",
                      "archive":str(archive),**result},indent=2))

if __name__=="__main__":
    main()
