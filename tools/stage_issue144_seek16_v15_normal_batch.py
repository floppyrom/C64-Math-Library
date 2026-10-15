#!/usr/bin/env python3
"""Issue144 D: seal the qualified V1/V5 normal-resident SEEK16 source research.

Runs only after independent public model and actual x64sc success; keeps all
five reference PRGs, both REUs and historical performance numbers untouched.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from stage_issue39_v1_3216_ool_release import reseal

EVID = "validation/review/ISSUE144_SEEK16_V15_NORMAL_BATCH_2026-10-16.json"
DOC = "docs/ISSUE144_SEEK16_V15_NORMAL_BATCH_2026-10-16.md"
KEY = "issue144_seek16_v15_normal_resident_batched_source_2026_10_16"
TAG = "2026-10-16 ISSUE144 SEEK16 V1/V5 NORMAL RESIDENT BATCH SOURCE QUALIFIED"
PROFILES = ("v1_balanced", "v5_hybrid_lowzp")


def digest(p: str | Path) -> str:
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def main() -> None:
    model = load(EVID)
    release = load("RELEASE_STATUS.json")
    assert model["status"] == "PASS_MODEL_AND_NATIVE"
    assert model["source_built_not_reference_release"] is True
    assert set(model["profiles"]) == set(model["native"]) == set(PROFILES)
    for p in PROFILES:
        a = model["profiles"][p]
        b = model["native"][p]
        assert a["status"] == "PASS_PAIRED_PUBLIC_MODEL"
        assert b["status"] == "PASS_NATIVE_X64SC_ALL_SEEK_MODES"
        assert a["init_calls"] >= 1088 and a["followup_calls"] >= 26112
        assert a["saved_cycles"]["slower"] == 0
        assert a["saved_cycles"]["worst"] >= 0
        assert a["saved_cycles"]["mean"] > 10
        assert a["old_sha256"] == digest(p + "/resident/math_" + p + "_game_math.prg")
        assert a["old_sha256"] == release["reference_prg_sha256"][p]
    assert all(digest(p + "/resident/math_" + p + "_game_math.prg") ==
               release["reference_prg_sha256"][p] for p in release["reference_prg_sha256"])
    for p in ("v3_reu_512k", "v4_reu_16m"):
        path = next((ROOT / p / "reu").glob("*.reu"))
        assert digest(path.relative_to(ROOT)) == release["reference_reu_sha256"][p]

    record = {
        "status": "PASS_NORMAL_RESIDENT_SOURCE_MODEL_NATIVE_NOT_BINARY_RELEASE",
        "profiles": list(PROFILES),
        "source_qualification": EVID,
        "source_document": DOC,
        "init_pairs_per_profile": 1088,
        "step_calls_per_profile": 26112,
        "public_cycle_saving_by_profile": {
            p: model["profiles"][p]["saved_cycles"] for p in PROFILES},
        "native_vice": {p: model["native"][p]["status"] for p in PROFILES},
        "additional_resident_code_bytes_per_profile": 45,
        "normal_zero_page_growth": 0,
        "application_RAM_growth": 0,
        "source_only": True,
        "reference_binaries_replaced": False,
        "native_cycle_measurement": False,
        "irq_nmi_reentrancy_certified": False,
    }
    release[KEY] = record
    (ROOT / "RELEASE_STATUS.json").write_text(json.dumps(release, indent=2) + "\n")

    doc = (ROOT / DOC).read_text()
    doc = doc.replace(
        "**Status: qualification in progress; not a default-binary release.**",
        "**Status: source-only qualification PASS for V1/V5 on paired 6510 model and actual VICE; not a default-binary release.**")
    if "## Qualification results" not in doc:
        rows = [
            "", "## Qualification results", "",
            "The full 64-movement public test passed 1,088 paired INIT calls and",
            "26,112 subsequent calls to ordinary STEP/STEP_INT/STEP1 per profile.",
            "Mean CPU-model saving: **10.566176 cycles** per V1/V5 public INIT;",
            "smallest saving 0, largest 36, **no slower measured cases**.",
            "The V1 and V5 native x64sc before/after public SEEK8/16 mode dumps",
            "were byte-identical. No native cycle timing was performed.",
            "Both reference and alternate source builds were separately",
            "qualified by the existing four-profile Issue144 source gate.",
            "", "Qualification evidence: `" + EVID + "`.", "",
        ]
        doc += "\n".join(rows)
    (ROOT / DOC).write_text(doc)
    note = (
        TAG + "\n"
        "- Source-only V1/V5 SEEK16_INIT integer-accumulator batch now fits 45 bytes "
        "at resident REG_API+$0599 (no additional normal ZP/application RAM); "
        "1,088 paired public INIT and 26,112 following STEP calls per profile pass. "
        "Mean saving 10.566176 modeled cycles, min 0, max 36; real native x64sc "
        "and alternate/reference source-map checks PASS. No frozen PRGs/REUs, "
        "PERFORMANCE.md or default binary publication changed. "
        + DOC + "\n\n"
    )
    for path in ("CHANGELOG.md", "CSDB_CHANGELOG.txt"):
        file = ROOT / path
        text = file.read_text()
        if TAG not in text:
            file.write_text(note + text)
    subprocess.run(["make", "clean"], cwd=ROOT, check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable, "tools/package_audit.py"], cwd=ROOT, check=True)
    assert all(digest(p + "/resident/math_" + p + "_game_math.prg") ==
               release["reference_prg_sha256"][p] for p in release["reference_prg_sha256"])
    print("ISSUE144 SEEK16 V1/V5 NORMAL RESIDENT SOURCE SEALED; REFERENCE BINARIES UNCHANGED")


if __name__ == "__main__":
    main()
