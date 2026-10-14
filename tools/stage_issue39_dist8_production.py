#!/usr/bin/env python3
"""Stage the proven Issue39 DIST8 shared-swap optimization for publication.

This guarded release is deliberately NOT the Issue39 distance-family closeout:
VEC2_NORMALIZE_Q8_8 remains to be audited. Gate source/public binary identity,
baseline provenance, native VICE, fixed ABI/memory and every non-DIST8 byte.
"""
from pathlib import Path
import hashlib,csv,json,subprocess,sys,shutil
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from mini6502 import CPU
from stage_issue39_v1_3216_ool_release import reseal
PROFILES=("v1_balanced","v2_pareto_fast","v3_reu_512k","v4_reu_16m","v5_hybrid_lowzp")
OPS=("MATH_DIST8_FAST","MATH_DIST8_ACCURATE")
NAMES={"MATH_DIST8_FAST":"DIST8_FAST","MATH_DIST8_ACCURATE":"DIST8_ACCURATE"}
EVID="validation/review/ISSUE39_DIST8_REGISTER_SWAP_RESEARCH_2026-10-14.json"
NATIVE="validation/review/ISSUE39_DIST8_SOURCE_NATIVE_2026-10-14.json"
CERT="validation/review/ISSUE39_DIST8_PRODUCTION_2026-10-14.json"
DOC="docs/ISSUE39_DIST8_REGISTER_SWAP_RELEASE_2026-10-14.md"
KEY="issue39_dist8_shared_register_swap_2026_10_14"
STAMP="2026-10-14 ISSUE39 DIST8 SHARED REGISTER-SWAP SOURCE RELEASE"
def sha(data):return hashlib.sha256(data).hexdigest()
def file_sha(path):return sha(path.read_bytes())
def subprocess_py(script,*args):
    subprocess.run([sys.executable,str(R/"tools"/script),*args],cwd=R,check=True)
def new_prg(p):
    d=(R/"build_hybrid/reference" if p=="v5_hybrid_lowzp" else R/"build_source/reference")/p
    man=json.loads((d/"source_build_manifest.json").read_text())
    return d/man["output_prg"]
def published(p):return R/p/"resident"/("math_"+p+"_game_math.prg")
def update_perf_table(path,p,means):
    if not path.exists():return
    with path.open(newline="") as f: lines=list(csv.DictReader(f))
    assert lines
    cols=list(lines[0])
    count=0
    for row in lines:
        name=row.get("routine")
        if name and not name.startswith("MATH_"): name="MATH_"+name
        if name not in OPS:continue
        if "profile" in row and row["profile"]!=p:continue
        d=means[p][name]
        row["mean_cycles"]=str(d["mean"])
        row["min_cycles"]=str(d["min"])
        row["max_cycles"]=str(d["max"])
        row["cases"]="65536"
        count+=1
    assert count==2,(str(path),p,count)
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols,lineterminator="\n");w.writeheader();w.writerows(lines)
def full_cpu_cycles(p,expected):
    from validate_smul24_directout import parse_inc
    b=published(p).read_bytes()
    load=int.from_bytes(b[:2],"little")
    mem=bytearray(65536);mem[load:load+len(b)-2]=b[2:]
    reu={"v3_reu_512k":"c64_math_v3_512k_game_math.reu",
         "v4_reu_16m":"c64_math_v4_16m_game_math.reu"}.get(p)
    reub=bytearray((R/p/"reu"/reu).read_bytes()) if reu else None
    c=CPU(mem,reu=reub);c.d=0
    api=parse_inc(R/p/"resident"/"math_api.inc")
    c.call(api["MATH_INIT"],2_000_000)
    out={}
    for op in OPS:
        total=0;low=10**9;high=0
        for x in range(256):
            for y in range(256):
                c.mem[api["MATH_X"]]=x;c.mem[api["MATH_Y"]]=y
                c.c=(x^y)&1;c.d=0
                n=c.call(api[op],2_000_000)
                assert c.mem[api["MATH_X"]]==x and c.mem[api["MATH_Y"]]==y
                assert c.c==0 and c.sp==0xfd
                total+=n;low=min(low,n);high=max(high,n)
        mean=total/65536
        assert abs(mean-expected[op]["mean_candidate_cpu_model_cycles"])<1e-10,(
            p,op,mean,expected[op]["mean_candidate_cpu_model_cycles"])
        out[op]={"mean":mean,"min":low,"max":high}
        print(p,op,"released CPU cycles",mean,low,high,flush=True)
    return out
def main():
    # A direct standalone invocation must not silently use a stale
    # generated assembly tree. Regenerate and rebuild before touching PRGs.
    subprocess_py("generate_sources.py")
    for _kind in ("reference","alternate"):
        subprocess_py("assemble_sources.py","--profile","all","--config-kind",_kind)
        subprocess_py("build_hybrid.py","--config-kind",_kind)
    stp=R/"RELEASE_STATUS.json"
    st=json.loads(stp.read_text())
    research=json.loads((R/EVID).read_text())
    native=json.loads((R/NATIVE).read_text())
    assert research["status"]=="PASS_EXHAUSTIVE_RESEARCH_NOT_PRODUCTION"
    assert native["status"]=="PASS_NATIVE_DIST8_OLD_NEW_SOURCE_MATCH"
    assert native["public_calls"]==480 and not native["native_cycle_timing_measured"]
    assert st.get(KEY) is None,"DIST8 already published; do not restage without review"
    original={}
    candidate={}
    for p in PROFILES:
        old=published(p).read_bytes();fresh=new_prg(p).read_bytes()
        row=research["profiles"][p]
        assert sha(old)==row["baseline_prg_sha256"]==st["reference_prg_sha256"][p]
        assert sha(fresh)==native["profiles"][p]["MATH_DIST8_FAST"]["new_prg_sha256"]
        assert old[:2]==fresh[:2] and len(old)==len(fresh)
        load=int.from_bytes(old[:2],"little")
        loc=int(row["patch_address"][1:],16)
        offset=loc-load+2
        before=bytes.fromhex(row["original_swap_bytes"])
        after=bytes.fromhex(row["replacement_swap_bytes"])
        assert old[offset:offset+len(before)]==before and fresh[offset:offset+len(after)]==after
        diffs=[i for i,(a,b) in enumerate(zip(old,fresh)) if a!=b]
        assert len(diffs) in (8,10) and all(offset<=i<offset+len(before) for i in diffs),(p,diffs)
        assert all(row["routines"][op]["cases"]==65536 and row["routines"][op]["bytewise_equal"] for op in OPS)
        original[p]=sha(old);candidate[p]=sha(fresh)
        shutil.copyfile(new_prg(p),published(p))
    # Benchmark ALL 65536 signed-byte pairs/profile and both public DIST8 APIs
    # on the actual prospective shipped resident images.
    measured={}
    for p in PROFILES:
        measured[p]=full_cpu_cycles(p,research["profiles"][p]["routines"])
    for p in PROFILES[:4]:
        update_perf_table(R/p/"PUBLIC_PERFORMANCE_GAME_MATH.csv",p,measured)
        update_perf_table(R/"docs/PERFORMANCE_GAME_MATH_FINAL.csv",p,measured)
    perf=R/"PERFORMANCE.md"
    doc=perf.read_text()
    for op in OPS:
        line=next(x for x in doc.splitlines() if x.startswith("| `"+op+"` |"))
        bits=line.split("|")
        for idx,p in enumerate(PROFILES):
            bits[idx+3]=f" {measured[p][op]['mean']:.6f} "
        doc=doc.replace(line,"|".join(bits))
    perf.write_text(doc)
    # The provenance input is now the shipped optimized binary. Its canonical
    # regeneration must round-trip to EXACTLY the same PRG for all five profiles.
    subprocess_py("generate_sources.py")
    for kind in ("reference","alternate"):
        subprocess_py("assemble_sources.py","--profile","all","--config-kind",kind)
        subprocess_py("build_hybrid.py","--config-kind",kind)
    for p in PROFILES:
        assert file_sha(new_prg(p))==candidate[p],(p,"canonical source roundtrip mismatch")
    alt={}
    for p in PROFILES:
        d=(R/"build_hybrid/alternate" if p=="v5_hybrid_lowzp" else R/"build_source/alternate")/p
        man=json.loads((d/"source_build_manifest.json").read_text())
        alt[p]=file_sha(d/man["output_prg"])
    # Regenerate exact standalone mirrors, reachable-byte/resource summaries
    # and public catalog indexes instead of editing one textual listing.
    subprocess_py("publish_standalone_sources.py")
    subprocess_py("generate_consolidated_routine_table.py")
    subprocess_py("generate_public_indexes.py")
    st["reference_prg_sha256"]=candidate
    st["alternate_prg_sha256"]=alt
    if isinstance(st.get("hybrid_v5"),dict):
        st["hybrid_v5"]["reference_prg_sha256"]=candidate["v5_hybrid_lowzp"]
        st["hybrid_v5"]["alternate_prg_sha256"]=alt["v5_hybrid_lowzp"]
    st[KEY]={"status":"PASS_STAGED_NATIVE_VICE_PR_MAIN_CI_PENDING",
       "public_diffs_only_in_DIST8_swap":True,"new_production_prgs":candidate,
       "old_production_prgs":original,"baseline_reconstruction":EVID,
       "native_proof":NATIVE,"native_vice_calls":480,
       "cpu_model_pair_calls":1310720,"release_cpu_model_calls":655360,
       "source_reference_alternate_parity_calls":119220,
       "resource_memory_growth_bytes":0,"normal_zp_growth_bytes":0,
       "reu_images_modified":False,"native_cycle_timing_measured":False,
       "document":DOC,"certificate":CERT,
       "routines":list(OPS),"measured":measured,
       "distance_normalization_family_complete":False,"issue39_remains_open":True}
    stp.write_text(json.dumps(st,indent=2)+"\n")
    summary={"status":"PASS_STAGED_NATIVE_VICE_PR_MAIN_CI_PENDING",
        "old_prgs":original,"new_prgs":candidate,"alternate_prgs":alt,
        "native_reference_equivalence_public_calls":480,
        "exhaustive_before_after_public_calls":1310720,
        "production_cpu_model_public_calls":655360,
        "source_map_parity_public_calls":119220,
        "changed_bytes_by_profile":{"v1_balanced":10,"v2_pareto_fast":8,
           "v3_reu_512k":8,"v4_reu_16m":8,"v5_hybrid_lowzp":10},
        "native_cycles_measured":False,"normal_zp_growth":0,
        "binary_length_growth":0,"reu_images_changed":False,
        "family_complete":False,"issue39_complete":False,"cycles":measured}
    (R/CERT).write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    text=("# Issue #39 — source-backed DIST8 shared ordering optimization\n\n"
     "DIST8_FAST and DIST8_ACCURATE reuse a magnitude-ordering exchange. "
     "The old stack-based PHA/PLA swap has been replaced by TAX/LDA/STA/STX/"
     "an early RTS with fixed-width NOP padding; the no-swap BCC still targets "
     "the previous RTS. Four architecture-specific relocatable modules cover "
     "V1/V5 absolute scratch and V2/V3/V4 zero page.\n\n"
     "Exhaustive signed-byte paired old/new emulator proof: 655,360 input/API/profile "
     "pairs (1,310,720 executions), preserving public inputs, result, flags, stack "
     "and scratch bytes. New distributed images were benchmarked on an additional "
     "655,360 calls. Reference/alternate generated source testing covered 119,220 "
     "calls and native x64sc baseline/source parity covered 480 public calls. "
     "Native cycle timing was not measured. The published PRGs change only 8 "
     "or 10 bytes within the original swap body, with identical lengths and "
     "no added ZP, REU, code area or stack-page reservation.\n\n"
     "| Profile | Mean FAST CPU cycles | Mean ACCURATE CPU cycles |\n"
     "|---|---:|---:|\n"+ "".join(f"| {p} | {measured[p]['MATH_DIST8_FAST']['mean']:.6f} | "
     f"{measured[p]['MATH_DIST8_ACCURATE']['mean']:.6f} |\n" for p in PROFILES)+
     "\nSource, public standalone mirrors, performance data, SHA256 and the "
     "release status have been synchronized. **Independent PR/main CI must still "
     "pass; this is not the completion of the DIST8+NORMALIZE family.**\n")
    (R/DOC).write_text(text)
    note=(f"## {STAMP}\n\n"
          "Source-integrated DIST8_FAST/DIST8_ACCURATE common stack-swap elimination "
          "(TAX/LDA/STA/STX) for V1–V5. Exact 1,310,720 old/new emulator calls; "
          "119,220 reference/alternate model calls; 480 native x64sc "
          "baseline/candidate calls; production exhaustive 655,360 calls. "
          "Saves 9 cycles on the swap branch in V1/V5 and 8 in V2–V4 "
          "(CPU model, not VICE timing). PRG lengths, stable ABI, REU and ZP "
          "unchanged. Standalone, metrics and package checksums synchronized. "
          "Independent PR/main CI pending; Issue39 still open for normalization "
          "and seek. See `"+DOC+"`.\n\n---\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        path=R/name
        if STAMP not in path.read_text():path.write_text(note+path.read_text())
    # Three-pass seal includes the generated package audit itself.
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal()
        subprocess_py("package_audit.py")
    print("ISSUE39 DIST8 RESIDENT + STANDALONE + PERFORMANCE RELEASE STAGED",flush=True)
if __name__=="__main__":main()
