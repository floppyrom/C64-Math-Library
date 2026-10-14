#!/usr/bin/env python3
"""Exact SHA-pinned inverse of stock NORMALIZE-only source optimization.

Research/historical-validation compatibility only. The production PRG is
never modified. Accept the certified old SHA or the certified new SHA, and
restore precisely the prior 1024-byte normalizer island; verify prior SHA.
Reject arbitrary unknown current-image hashes, but leave genuine frozen
historical images to their own separate SHA-pinned inverse adapters.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
KEY="issue39_normalize_log_branch_2026_10_14"
def sha(b):return hashlib.sha256(b).hexdigest()
def pre_normalize_bytes(profile:str,blob:bytes)->bytes:
    st=json.loads((R/"RELEASE_STATUS.json").read_text())
    state=st.get(KEY)
    if state is None:return blob
    proof=json.loads((R/state["inverse_provenance"]).read_text())
    assert proof["status"]=="PASS_SHA_PINNED_NORMALIZE_ONLY_REVERSIBLE"
    if profile not in proof["profiles"]:return blob
    record=proof["profiles"][profile]
    assert record["old_sha256"]==state["old_resident_sha256"][profile]
    assert record["new_sha256"]==state["candidate_resident_sha256"][profile]
    digest=sha(blob)
    if digest==record["old_sha256"]:return blob
    if digest!=record["new_sha256"]:return blob # already historical parent; never rewrite
    original=bytes.fromhex(record["original_region_hex"])
    assert len(original)==1024
    ld=int.from_bytes(blob[:2],"little")
    assert ld==int(record["resident_load"][1:],16)==0x1000
    lo=int(record["normalizer_code_start"][1:],16)
    hi=int(record["normalizer_code_stop_exclusive"][1:],16)
    start=2+lo-ld
    stop=2+hi-ld
    assert stop-start==len(original)
    assert sha(blob[start:stop])==record["candidate_region_sha256"],(
        profile,"modified resident normalizer code drift")
    restored=bytearray(blob)
    restored[start:stop]=original
    assert sha(restored)==record["old_sha256"],(
        profile,"normalizer archived resident digest mismatch",sha(restored))
    return bytes(restored)
