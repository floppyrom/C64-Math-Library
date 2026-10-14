#!/usr/bin/env python3
"""Source-integrate qualified 2-cycle 32x32 SHR16 signed/unsigned adapters.

Requires successful source A/B research. Enforces exactly four rewritten
bytes per resident, unchanged resident span, public ABI and resource budgets.
Native x64sc and independent PR/main CI are STILL required.
"""
from __future__ import annotations
from pathlib import Path
import csv,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from screen_issue39_fixed_shr16_tail import P,SOURCE,TYPES,OPS,patch,build,prg,paired,sha
from benchmark_multiply_refresh import CORPORA
from stage_issue39_v1_3216_ool_release import reseal
STAMP="2026-10-14 ISSUE39 FIXED OUTPUT SHR16 REDUNDANT CARRY TAIL"
RECORD="validation/review/ISSUE39_FIXED_SHR16_RETURN_TAIL_PRODUCTION_2026-10-14.json"
DOCUMENT="docs/ISSUE39_FIXED_SHR16_RETURN_TAIL_2026-10-14.md"
def run(name,*args):
    cmd=[sys.executable,str(ROOT/"tools"/(name+".py")),*map(str,args)]
    print("RUN",*cmd,flush=True)
    subprocess.run(cmd,cwd=ROOT,check=True)
def resident(p):return ROOT/p/"resident"/("math_"+p+"_game_math.prg")
def rewrite_perf(table):
    path=ROOT/"PERFORMANCE.md"
    lines=path.read_text().splitlines()
    for routine in ("MATH_UMUL32_SHR16","MATH_SMUL32_SHR16"):
        hits=[i for i,line in enumerate(lines) if line.startswith("| `"+routine+"` |")]
        assert len(hits)==1,(routine,hits)
        pieces=lines[hits[0]].split("|")
        for i,p in enumerate(P):
            pieces[3+i]=" "+format(table[p][routine]["mean_cycles"],".6f")+" "
        lines[hits[0]]="|".join(pieces)
    path.write_text("\n".join(lines)+"\n")
    for p in P:
        perf=ROOT/p/"PUBLIC_PERFORMANCE.csv"
        if not perf.exists():continue
        with perf.open(newline="") as f:rows=list(csv.DictReader(f))
        for operation in ("math_umul32_shr16","math_smul32_shr16"):
            matches=[r for r in rows if r.get("operation")==operation]
            if matches:
                m=table[p]["MATH_"+operation[5:].upper()]
                matches[0].update(avg_cycles=format(m["mean_cycles"],".6f"),
                                  min_cycles=str(m["min_cycles"]),
                                  max_cycles=str(m["max_cycles"]),
                                  cases=str(m["cases"]),
                                  evidence="2026-10-14 full-output carry-neutral SHR16 tail paired output corpus")
        if rows:
            with perf.open("w",newline="") as f:
                wr=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n")
                wr.writeheader();wr.writerows(rows)
def main():
    stpath=ROOT/"RELEASE_STATUS.json";st=json.loads(stpath.read_text())
    before={p:sha(resident(p).read_bytes()) for p in P}
    assert st["reference_prg_sha256"]==before,"source tree is not unmodified target main"
    existing=st.get("issue39_fixed_shr16_clc_2026_10_14")
    if existing and existing.get("new_sha256")==before:
        assert existing["source_paired_gain_every_case"]==2
        subprocess.run(["make","clean"],cwd=ROOT,check=True)
        for _ in range(3):
            reseal()
            run("package_audit")
        print("FIXED SHR16 REPEAT SEAL PASS",flush=True)
        return
    oldbytes={p:resident(p).read_bytes() for p in P}
    for p in SOURCE:
        path=ROOT/"relocatable_source"/p/"math_relocatable.asm"
        old=path.read_text()
        path.write_text(patch(old))
    build()
    changes={}
    candidate={}
    corpus=CORPORA["shift32"]
    assert len(corpus)==4361
    research={"status":"PASS_SOURCE_A_B",
      "old_sha256":before,"pairs_per_profile_per_op_per_map":len(corpus),
      "native_timing_measured":False,"profiles":{}}
    for p in P:
        data=prg(p,"reference")
        assert len(data)==len(oldbytes[p])
        delta=[i for i,(a,b) in enumerate(zip(oldbytes[p],data)) if a!=b]
        assert len(delta)==4,(p,"unexpected code delta",delta)
        code_addresses=[int.from_bytes(data[:2],"little")+i-2 for i in delta]
        assert all(0xc000<=a<0xd000 for a in code_addresses),(p,code_addresses)
        changes[p]=[hex(x) for x in code_addresses]
        candidate[p]=data
        research["profiles"][p]={"code_delta":changes[p]}
        for k in TYPES:
            checks=paired(p,k,oldbytes[p],prg(p,k),corpus)
            research["profiles"][p][k]=checks
        print("PRODUCTION PREINSTALL A/B",p,"PASS",len(corpus),"per operation and relocation",flush=True)
    # Validate source-generated reference/alternate 16-bit SHR8 adapters unchanged.
    run("validate_mul16_shr8_register")
    for p in P:shutil.copyfile(ROOT/"build_hybrid/reference"/p/"math_"+p+"_game_math.prg" if False else "/dev/null","/dev/null") if False else None
    for p in P:resident(p).write_bytes(candidate[p])
    run("generate_sources")
    build()
    assert all(prg(p,"reference")==resident(p).read_bytes() for p in P),"source regeneration drift"
    # Source tests produce new merged fixed-shift corpus and benchmark for both outputs.
    run("benchmark_multiply_refresh")
    benchmark=json.loads((ROOT/"validation/multiply_refresh/MULTIPLY_REFRESH_BENCHMARK.json").read_text())
    assert benchmark["status"]=="PASS"
    profiles=benchmark["profiles"]
    for p in P:
        for op in ("MATH_UMUL32_SHR16","MATH_SMUL32_SHR16"):
            # Every 32-bit fixed-output operation saves 2 CPU cycles for each input.
            entry=research["profiles"][p]["reference"][op]
            mean=profiles[p][op]["mean_cycles"]
            assert abs(mean-entry["new_mean_cycles"])<0.0000001,(p,op,mean,entry)
            assert abs(entry["old_mean_cycles"]-entry["new_mean_cycles"]-2)<1e-9
    rewrite_perf(profiles)
    for step in ("validate_signed_multiply","validate_smul24_directout",
      "benchmark_unsigned_common_corpus","benchmark_unsigned_3216_workloads",
      "audit_issue39_unsigned_small_workloads",
      "publish_standalone_sources","generate_consolidated_routine_table",
      "generate_public_indexes","validate_public_catalog",
      "validate_standalone_sources","verify_deterministic_rebuild",
      "validate_unsigned_division","validate_signed_division"):
        run(step)
    after={p:sha(resident(p).read_bytes()) for p in P}
    assert all(after[p]!=before[p] for p in P)
    alternate={}
    for p in P:
        srcdir=(ROOT/"build_hybrid" if p==P[-1] else ROOT/"build_source")/"alternate"/p
        m=json.loads((srcdir/"source_build_manifest.json").read_text())
        alternate[p]=m["output_sha256"]
    report={"status":"PASS_SOURCE_PRODUCTION_NATIVE_PENDING",
      "before_prg_sha256":before,"after_prg_sha256":after,
      "alternate_prg_sha256":alternate,"code_delta_four_bytes_per_profile":changes,
      "resource_growth_ZP":0,"resident_span_growth":0,"stack_growth":0,
      "public_ABI_changed":False,"private_optisearch_source_published":False,
      "mean_gain_each_call_cycles":2,"native_cycle_timing_measured":False,
      "native_VICE_qualification_pending":True,
      "source_same_operand":research,"fixed16_registered_adapter_unchanged":True}
    path=ROOT/RECORD;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    doc=ROOT/DOCUMENT
    doc.write_text("# Issue39 fixed multiply output 32-bit return-tail production stage\n\n"
      "The full signed and unsigned SMUL32/UMUL32 public calls return with carry "
      "clear. In the two 32x32->48 shifted-result adapters, six absolute "
      "LDA/STA overlapping result moves preserve carry. The adapter's "
      "trailing redundant `CLC; RTS` can therefore be encoded as "
      "`RTS; NOP` without changing source address, resident footprint "
      "or public flags contract. No additional code or zero-page is needed.\n\n"
      "Each of 4,361 identical source A/B inputs for **both routines**, "
      "all five profiles and **both relocations** saves **exactly two "
      "CPU-model cycles**. Correct 48-bit shifted signed/unsigned results, "
      "C=0, caller inputs, and stack checked on every case. No full-width "
      "multiply producer was changed. Signed/unsigned 16-bit SHR8 adapter "
      "already consumes X/A/Y register returns and remains unchanged.\n\n"
      "**This is staged until actual native VICE and independent CI pass.** "
      "No native cycle measurement is claimed. The private OptiSearch "
      "source is excluded. Issue #39 remains open.\n")
    note=(STAMP+"\n- 32-bit fixed-output UMUL32_SHR16 and "
      "SMUL32_SHR16: removed redundant CLC following C=0 full-product "
      "producer. Matched -2 CPU-model cycles for all 4,361 cases per "
      "operation/profile/map; five profiles, both relocations, exactly four "
      "code-byte substitutions/profile; no resident, ABI, ZP or persistent "
      "stack growth. Native VICE and postmerge checks PENDING.\n"
      "- UMUL16_SHR8 and SMUL16_SHR8 retained the existing qualified "
      "register-output adapters without code changes. "+DOCUMENT+"\n\n")
    for f in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        dest=ROOT/f
        if STAMP not in dest.read_text():dest.write_text(note+dest.read_text())
    st["reference_prg_sha256"]=after
    st["alternate_prg_sha256"]=alternate
    st["issue39_fixed_shr16_clc_2026_10_14"]={
      "status":"PASS_STAGED_NATIVE_CI_PENDING",
      "gain_cpu_cycles_per_call":2,
      "source_paired_gain_every_case":2,
      "matched_inputs_per_profile_per_map":4361,
      "profile_count":5,
      "routines":["MATH_UMUL32_SHR16","MATH_SMUL32_SHR16"],
      "fixed16_unchanged":True,"new_sha256":after,"old_sha256":before,
      "abi_growth":0,"normal_ZP_growth":0,"resident_growth":0,
      "native_VICE_calls":0,"document":DOCUMENT,"proof":RECORD}
    for key,path,field in (
      ("issue39_common_input_unsigned_divmod","validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json","benchmark_sha256"),
      ("issue39_unsigned_3216_multiworkload_2026_10_11","validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json","report_sha256"),
      ("issue39_unsigned_small_width_workloads_2026_10_11","validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json","data_sha256")):
       if isinstance(st.get(key),dict) and (ROOT/path).exists():st[key][field]=sha((ROOT/path).read_bytes())
    stpath.write_text(json.dumps(st,indent=2)+"\n")
    subprocess.run(["make","clean"],cwd=ROOT,check=True)
    for _ in range(3):
        reseal();run("package_audit")
    print("ISSUE39 FIXED SHR16 SOURCE PRODUCER PASS; NATIVE VICE AND FULL CI PENDING",flush=True)
if __name__=="__main__":main()
