#!/usr/bin/env python3
"""Strict reversible DIST8-only provenance view for archived binary audits.

Never treat an arbitrary binary with a novel hash as the archived parent.
Only accept the current certified DIST8 release image and invert its exact,
known-length patch at its exact resident address, pinning both SHA256 digests.
The returned bytes are for historical proof replay ONLY, not redistribution.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
KEY="issue39_dist8_shared_register_swap_2026_10_14"
RESEARCH=R/"validation/review/ISSUE39_DIST8_REGISTER_SWAP_RESEARCH_2026-10-14.json"
def sha(data):return hashlib.sha256(data).hexdigest()
def pre_dist8_bytes(profile:str,current:bytes)->bytes:
    state=json.loads((R/"RELEASE_STATUS.json").read_text())
    if KEY not in state:
        assert sha(current)==state["reference_prg_sha256"][profile],(profile,"unknown pre-DIST8 image")
        return current
    record=state[KEY]
    assert record["status"] in (
        "PASS_STAGED_NATIVE_VICE_PR_MAIN_CI_PENDING",
        "PASS_COMPLETED_POSTMERGE_MAIN_GREEN"),record["status"]
    research=json.loads(RESEARCH.read_text())["profiles"][profile]
    old_sha=record["old_production_prgs"][profile]
    new_sha=record["new_production_prgs"][profile]
    assert old_sha==research["baseline_prg_sha256"]
    assert new_sha==state["reference_prg_sha256"][profile]
    assert sha(current)==new_sha,(profile,"unknown current DIST8 binary")
    loc=int(research["patch_address"][1:],16)
    start=loc-int.from_bytes(current[:2],"little")+2
    before=bytes.fromhex(research["original_swap_bytes"])
    after=bytes.fromhex(research["replacement_swap_bytes"])
    assert len(before)==len(after)
    assert current[start:start+len(after)]==after,(profile,"candidate swap byte drift")
    restore=bytearray(current)
    restore[start:start+len(before)]=before
    assert sha(restore)==old_sha,(profile,"reconstructed archived PRG hash drift")
    return bytes(restore)
