#!/usr/bin/env python3
"""Seal the merged-PR #118–#124 closeout into BOTH public changelogs.

Research-stage "pending" entries are intentionally preserved as historical
snapshots. This is the current merge-status index. No compiled code, benchmark
number, OptiSearch file, or public ABI is altered.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from stage_issue39_v1_3216_ool_release import reseal

MARKER = "2026-10-14 — Issue #39 merged PR closeout (#118–#124)"
MAIN = "03ba4fc98893968c88e223682a1a7d09aa80b123"
ROWS = [
    (118, "33f364cfe0465a4df92e82dec1d94039ec2e1d5d",
     "V1/V5 UMUL24 rare-carry return: 1 CPU-model cycle saved for each of 10,324 paired inputs/profile; 384 native x64sc correctness calls, no extra resident/ZP bytes.",
     "Production change integrated; full PR and post-merge qualification passed."),
    (119, "4d913d9b5e5a4278fc1f04abcb1b3edba12d8fa6",
     "Unsigned multiply UMUL8/16/24/32 plus READY family completion; five-profile/relocation/READY ABI and OptiSearch resource-class audit.",
     "Completion certificate, changelogs and checksum publication; no further binary edits."),
    (120, "3f4da1ab061ad56f3745e3742a45b838321cf410",
     "Signed multiply SMUL8/16/24/32 plus READY family validation: exhaustive 8-bit signed domain on five profiles, 600 native x64sc public calls plus 120 READY preparations; OptiSearch donor screen.",
     "Qualified no-gain review: retained existing public-compatible implementations."),
    (121, "bfc43c2f6643a893304799683f73396e0eba3096",
     "Signed multiply family final release certification; prepared READY saves 25 cycles in V1/V5 but costs 3 cycles in V2–V4 compared on identical inputs.",
     "Status, release certificate and checksums sealed; no arithmetic binary edits."),
    (122, "ce4e7bcf785f8b0fb292be1b044adce9fa3c1978",
     "UMUL32_SHR16 and SMUL32_SHR16 fixed output return-tail optimisation: 2 CPU-model cycles saved per call on each of 4,361 paired operands/profile/map; 480 native x64sc before/after calls.",
     "Production binaries changed at exactly four bytes/profile, no resident span/ZP/stack growth; 16-bit SHR8 paths unchanged."),
    (123, "e9a3d6dabccb56de4908a7d21307b4928b735513",
     "Fixed multiply outputs family completion (UMUL16_SHR8, SMUL16_SHR8, UMUL32_SHR16, SMUL32_SHR16).",
     "Published permanent four-operation audit, completion certificate, docs, changelogs and SHA256SUMS; no additional binary edits."),
    (124, "03ba4fc98893968c88e223682a1a7d09aa80b123",
     "REU Turbo16/32 and V4 QS16 matched batch audit and V4 QS16 alternate relocation correction (symbolic I/O/ZP/bank references); 57,759 CPU-model public calls and 120 native x64sc REU-mode calls.",
     "Merged and post-merge main full-library/comparable/Turbo32/fixed-family checks green. REU *family completion* remains pending (Issue #39 checkbox open), despite merged fix."),
]

def main():
    state = json.loads((ROOT / "RELEASE_STATUS.json").read_text())
    for key in (
        "issue39_unsigned_multiply_family_2026_10_14",
        "issue39_signed_multiply_family_2026_10_14",
        "issue39_fixed_multiply_family_2026_10_14",
        "issue39_reu_multiply_modes_2026_10_14",
    ):
        assert key in state, f"missing public status row: {key}"
    assert state["issue39_unsigned_multiply_family_2026_10_14"]["completed"]
    assert state["issue39_signed_multiply_family_2026_10_14"]["family_complete"]
    assert state["issue39_fixed_multiply_family_2026_10_14"]["family_complete"]
    reu = state["issue39_reu_multiply_modes_2026_10_14"]
    assert reu["family_complete"] is False
    assert reu["native_VICE_calls"] == 120
    # Ensure all listed merges are ancestors of this branch and cannot be
    # confused with research-only draft PRs or unmerged candidates.
    for pr, sha, _, _ in ROWS:
        subprocess.run(["git", "merge-base", "--is-ancestor", sha, "HEAD"],
                       cwd=ROOT, check=True)
        print(f"VERIFIED MERGE PR #{pr}: {sha[:12]}", flush=True)
    title = f"## {MARKER}"
    header = (
        f"{title}\n\n"
        f"**Merged into \`main\` through \`{MAIN[:12]}\` (14 October 2026).** "
        "The entries below are **merge closeouts**, not preliminary research "
        "staging. Earlier notes farther down that say *CI pending* describe "
        "the state at the time of staging and are superseded by this section. "
        "Cycle improvements are deterministic **CPU-model** comparisons; "
        "native VICE correctness does not imply native cycle measurements. "
        "Private OptiSearch source remains unpublished.\n\n"
    )
    content = header
    for pr, sha, what, status in ROWS:
        content += (
            f"- **[PR #{pr}](https://github.com/floppyrom/C64-Math-Library/pull/{pr})** "
            f"(merge \`{sha[:12]}\`): {what} **Status:** {status}\n"
        )
    content += (
        "\n**Post-merge validation at PR #124 \`main\`:** full-library "
        "[#38540701276](https://github.com/floppyrom/C64-Math-Library/actions/runs/38540701276), "
        "comparable unsigned "
        "[#38540701196](https://github.com/floppyrom/C64-Math-Library/actions/runs/38540701196), "
        "Turbo32 "
        "[#38540701380](https://github.com/floppyrom/C64-Math-Library/actions/runs/38540701380), "
        "and fixed-output family "
        "[#38540701127](https://github.com/floppyrom/C64-Math-Library/actions/runs/38540701127) "
        "all **PASS**. Issue #39 remains open for REU final certification and "
        "subsequent families.\n\n---\n\n"
    )
    for filename in ("CHANGELOG.md", "CSDB_CHANGELOG.txt"):
        path = ROOT / filename
        original = path.read_text()
        if title not in original:
            # CSDB is plain text but Markdown remains legible as a text ledger;
            # links are explicit and the PR number is searchable.
            path.write_text(content + original)
        assert path.read_text().count(title) == 1
        for pr, *_ in ROWS:
            assert f"PR #{pr}" in path.read_text()
        print("MERGE CLOSEOUT ADDED", filename, flush=True)
    # Release package is shipped lean: no built source dirs.
    subprocess.run(["make", "clean"], cwd=ROOT, check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable, str(ROOT / "tools/package_audit.py")],
                       cwd=ROOT, check=True)
    # Verify published resident binaries were not changed by a docs-only PR.
    for p, expected in state["reference_prg_sha256"].items():
        candidate = ROOT / p / "resident" / f"math_{p}_game_math.prg"
        assert hashlib.sha256(candidate.read_bytes()).hexdigest() == expected
    print("ISSUE39 PR #118–#124 CHANGELOG MERGE CLOSEOUT AND PACKAGE SEAL PASS", flush=True)

if __name__ == "__main__":
    main()
