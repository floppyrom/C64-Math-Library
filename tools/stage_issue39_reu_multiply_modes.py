#!/usr/bin/env python3
"""Publish comparable public REU multiply batch-cost architecture and evidence.

NO resident, REU image, public entry, resource or private OptiSearch edits.
Native VICE REU proof and postmerge main are separate qualification gates.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
PROFILES=("v3_reu_512k","v4_reu_16m")
PROOF=R/"validation/review/ISSUE39_REU_MULTIPLY_MATCHED_CORPUS_2026-10-14.json"
DOC=R/"docs/ISSUE39_REU_MULTIPLY_FAMILY_REVIEW_2026-10-14.md"
STAMP="2026-10-14 ISSUE39 REU MULTIPLY MODES THREE-MODE PUBLIC PROFILE AUDIT"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    report=json.loads(PROOF.read_text())
    assert report["status"]=="PASS_PUBLIC_REU_MULTIPLY_MODES"
    assert report["source_kinds"]==["published","reference","alternate"]
    assert report["reproducible_turbo_relocation_prior_calls"]==17196
    assert report["reproducible_turbo_boundary_prior_calls"]==3556
    stp=R/"RELEASE_STATUS.json"
    s=json.loads(stp.read_text())
    original_prg=dict(s["reference_prg_sha256"])
    original_reu=dict(s["reference_reu_sha256"])
    for p in PROFILES:
        assert sha(R/p/"resident"/f"math_{p}_game_math.prg")==original_prg[p]
        f="c64_math_v3_512k_game_math.reu" if p==PROFILES[0] else "c64_math_v4_16m_game_math.reu"
        assert sha(R/p/"reu"/f)==original_reu[p]
        all_maps=report["profiles"][p]
        for kind in ("published","reference","alternate"):
            row=all_maps[kind]
            for family,want in (("turbo16",33),("turbo32",41)):
                q=row[family]
                assert q["normal"]["arithmetic_carry_stack_inputs"]=="PASS"
                assert q["mode"]["arithmetic_carry_stack_inputs"]=="PASS"
                assert q["mode"]["saved_ZP_exactly_restored"] is True
                assert q["mode"]["second_batch_valid"] is True
                assert q["batch_vs_normal"]["crossover_calls"]==want,(p,kind,family,q["batch_vs_normal"])
                assert q["mode"]["begin_cycles"]+q["mode"]["end_cycles"]==(645 if family=="turbo16" else 697)
                assert q["mode"]["cases"]==(2097 if family=="turbo16" else 2192)
            if p==PROFILES[1]:
                q=row["v4_qs16"]
                assert q["mode"]["cases"]==2097 and q["mode"]["reu_mode_restored"]
                assert q["batch_vs_normal"]["beneficial"] is False
                assert q["mode"]["begin_cycles"]+q["mode"]["end_cycles"]==36
    assert report["total_public_product_calls"]==57759
    doc=("""# Issue #39 — REU multiply family: Turbo16, Turbo32 and V4 QS16

**Public ABI and resource-screen date:** 14 October 2026. Source and resident profile review only; **native raster-exact timing is not measured**. The private OptiSearch source is not published.

## Identical-input public-entry results

Every normal-vs-Turbo16 pair is the **same 2,097 inputs**; every normal-vs-Turbo32 pair is the **same 2,192 inputs**. V4 QS16 uses the identical Turbo16 corpus (2,097). The CPU model includes its deterministic REU DMA costs; entry to RTS includes the actual public wrapper, while caller JSR and input setup are excluded. Both V3 and V4 have identical measured Turbo/public vectors, as do both source relocation maps.

| Service | Normal public comparison | REU service | BEGIN + END | Break-even batch |
| --- | ---: | ---: | ---: | ---: |
| Turbo16 (V3/V4) | UMUL16 216.73391 cycles | 197.04626 cycles | 645 cycles | **33 calls** |
| Turbo32 (V3/V4) | UMUL32 693.45347 cycles | 676.18522 cycles | 697 cycles | **41 calls** |
| V4 QS16 | UMUL16 216.73391 cycles | 281.72675 cycles | 36 cycles | **None (slower every batch)** |

The batch crossover is strictly defined as the first integer `n` satisfying `BEGIN + n * REU_CALL + END < n * NORMAL_CALL`, without counting operand marshalling or caller JSR. V4 QS16 remains valuable as an architectural example of two REU table fetches implementing `Q(x+y)-Q(abs(x-y))`, **not** as a fast multiply tier. Do not compare these 2026-10-14 same-input means with older random-seed means as if benchmark populations were identical.

## Public interface, ownership, alternatives

- **Turbo16:** 122-byte self-modifying executable-ZP overlay, public wrapper binds x/y, writes the 32-bit result directly into public Z. It saves approximately 19.68766 model cycles per operation versus same-corpus normal UMUL16, but first needs a 300-cycle BEGIN and finishes with a 345-cycle END. These include deterministic REU SWAP cost. No stack-page executable reservation.
- **Turbo32:** 135-byte stack-free executable-ZP overlay, resident register bind and direct low/high result paths. Same-corpus 32-bit saving approximately 17.26825 cycles per call; BEGIN 326, END 371. It cannot be substituted for the normal entry outside BEGIN/END or run concurrently with ordinary math sharing its ZP. Avoid equating a privately benchmarked unwrapped 614-cycle kernel with the public ~676-cycle REU CALL.
- **V4 QS16:** four-byte REU record AUTOLOAD, with 2× four-byte lookups for each product. Although BEGIN/END cost only 18 cycles each, per-call time is higher than the direct public route; the current 16 MiB table and 24-bit REU address requirements also constrain hardware compatibility.

For **each** Turbo mode, the audit checks signed-free unsigned products, carry C=0, preserved X/Y buffers, stack balance, 122/135 ZP byte ownership, exact ZP restoration, and successful second-batch reinstallation of the modified overlay. It also confirms that ordinary calls after END remain valid because the real resident ZP state is restored (not invented sentinel bytes). For QS16, it verifies that END restores the ordinary one-byte REU mode. There is no blanket license to call normal math routines inside a Turbo overlay interval.

### Relocation and comparison coverage

The new audit exercises **57,759 installed/source-built public product calls** over V3 and V4, published/reference/alternate builds. The prior independent relocation certificate already qualified 17,164 products plus 32 lifecycle calls, and the origin/bank boundary sweep qualified 3,556 additional products. Reference/alternate Turbo cycle vectors, BEGIN/END cycles and output contract must match bit-for-bit. ZP origins $02-$85 (Turbo16) and $02-$79 (Turbo32), and 512 KiB/16 MiB bank endpoints, remain distinct tested resource classes.

### OptiSearch transplantation decision

The normal multiply-family optimization already screened OptiSearch native quarter-square, sign-lifetime and 32-bit low-resource records. REU overlays are another ABI/resource class: native unwrapped fastest records or stack-page-dependent candidates are not valid substitute public CALL implementations without full binder, overlay lifetime, REU transfer, ZP ownership and mixed-call proof. No additional compatible REU-mode architecture beating the selected current Turbo16/32 paths has been established by the current evidence. This is a **documented no-gain audit**, not a claim of exhaustive optimization search.

### Publication criterion

This research review and same-input CPU proof do not by themselves certify native REU behaviour. Keep Issue #39's REU multiply checkbox **open until** native x64sc V3/V4 and QS16 mode proof, exact-head full CI and comparable benchmarks, checksum seal and postmerge main qualification have passed. Remaining trig/distance/seek families remain open irrespective of REU completion.
""")
    DOC.parent.mkdir(parents=True,exist_ok=True)
    DOC.write_text(doc)
    guide=R/"docs/REU_GUIDE.md"
    old=guide.read_text()
    old=old.replace("Turbo16 swaps a 113-byte kernel","Turbo16 swaps a 122-byte kernel")
    start="Turbo32's optimized public CALL measures 684.185 cycles versus 690.235 for normal UMUL32; with 326-cycle BEGIN and 371-cycle END, the batch crossover is 116 products."
    end="On the same 2,192-input corpus Turbo32 CALL measures 676.185 model cycles versus normal UMUL32 693.453; with 326-cycle BEGIN and 371-cycle END, the first strictly profitable batch is 41 products. These means are corpus-specific."
    assert start in old
    old=old.replace(start,end)
    a=old.index("Current UMUL16 speed guidance:")
    b=old.index("## VICE examples",a)
    replacement=("Current matched-input speed guidance (14 October 2026, same public-call corpus):\n\n"
      "```text\n"
      "normal UMUL16             216.734 model cycles per call (2,097 pairs)\n"
      "Turbo16 CALL              197.046 model cycles; BEGIN + END = 645\n"
      "Turbo16 batch crossover   33+ products, strictly faster in the model\n"
      "normal UMUL32             693.453 model cycles per call (2,192 pairs)\n"
      "Turbo32 CALL              676.185 model cycles; BEGIN + END = 697\n"
      "Turbo32 batch crossover   41+ products, strictly faster in the model\n"
      "QS16 CALL                 281.727 model cycles; BEGIN + END = 36\n"
      "QS16 batch crossover      none; specialized functional option only\n"
      "```\n\n"
      "These are same-corpus CPU-model results, **not native raster-time measurements**. "
      "See [REU multiply family review](ISSUE39_REU_MULTIPLY_FAMILY_REVIEW_2026-10-14.md).\n\n")
    guide.write_text(old[:a]+replacement+old[b:])
    changenote=(STAMP+"\n- Same-input REU multiply architecture: V3/V4 Turbo16 "
        "197.046 public model cycles vs ordinary 216.734, 645 lifecycle cycles, "
        "33-call crossover; Turbo32 676.185 vs 693.453, 697 lifecycle, "
        "41-call crossover; V4 QS16 281.727 vs 216.734, no speed crossover. "
        "57,759 public product calls across installed/reference/alternate V3/V4, "
        "plus prior 17,196 Turbo relocation API and 3,556 boundary calls. "
        "No resident/REU/ABI/stack/ZP growth, no private source publication. "
        "Native VICE REU and full PR/main qualification pending.\n"
        "- docs/ISSUE39_REU_MULTIPLY_FAMILY_REVIEW_2026-10-14.md\n\n")
    for name in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
        p=R/name
        if STAMP not in p.read_text():p.write_text(changenote+p.read_text())
    readme=R/"README.md"
    if "ISSUE39_REU_MULTIPLY_FAMILY_REVIEW_2026-10-14.md" not in readme.read_text():
        readme.write_text(readme.read_text()+"\nThe [REU Turbo16/Turbo32 and V4 QS16 matched-input multiply audit](docs/ISSUE39_REU_MULTIPLY_FAMILY_REVIEW_2026-10-14.md) documents batch break-even, pointer ownership and REU-specific hardware caveats.\n")
    s["issue39_reu_multiply_modes_2026_10_14"]={
        "status":"PASS_REU_CPU_MODEL_SOURCE_MAPS_NATIVE_PENDING","family_complete":False,
        "modes":["MATH_REU_UMUL16","MATH_REU_UMUL32","MATH_REU_QS16"],
        "profiles":list(PROFILES),"cpu_model_product_calls":report["total_public_product_calls"],
        "prior_relocation_api_calls":17196,"prior_boundary_product_calls":3556,
        "turbo16_crossover_calls":33,"turbo32_crossover_calls":41,
        "v4_qs16_speed_crossover":None,"source_maps":["published","reference","alternate"],
        "native_cycle_timing_measured":False,"private_optisearch_source_published":False,
        "resident_or_reu_image_modified":False,"ABI_or_ZP_growth":0,
        "published_prg_sha256":{p:original_prg[p] for p in PROFILES},
        "published_reu_sha256":{p:original_reu[p] for p in PROFILES},
        "documentation":"docs/ISSUE39_REU_MULTIPLY_FAMILY_REVIEW_2026-10-14.md",
        "evidence":"validation/review/ISSUE39_REU_MULTIPLY_MATCHED_CORPUS_2026-10-14.json",
        "issue39_remains_open":True}
    stp.write_text(json.dumps(s,indent=2)+"\n")
    subprocess.run(["make","clean"],cwd=R,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(R/"tools/package_audit.py")],cwd=R,check=True)
    assert all(sha(R/p/"resident"/f"math_{p}_game_math.prg")==original_prg[p] for p in PROFILES)
    print("REU THREE-MODE SAME-CORPUS SOURCE AUDIT SEALED; NATIVE REU PENDING",flush=True)
if __name__=="__main__":main()
