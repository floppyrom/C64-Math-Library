#!/usr/bin/env python3
"""Strict SHA-verified inverse of Issue39 stock NORMALIZE code publication.

Only accepts a live shipped image or its uniquely certified immediately
preceding image. Restores exact changed byte offsets recorded by the guarded
production publisher; never downloads a historical PRG or trusts an unknown SHA.
Intended for historical math proofs, never for distributing old binaries.
"""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
KEY="issue39_normalize_branch_collapse_2026_10_14"
def sha(b):return hashlib.sha256(b).hexdigest()
def pre_normalize_bytes(profile,current):
 st=json.loads((R/"RELEASE_STATUS.json").read_text())
 if KEY not in st:return current
 record=st[KEY]
 assert record["status"] in (
  "PASS_STAGED_PR_MAIN_CI_PENDING",
  "PASS_COMPLETED_POSTMERGE_MAIN_GREEN"),record["status"]
 before=record["old_resident_sha256"][profile]
 after=record["new_resident_sha256"][profile]
 d=sha(current)
 if d==before:return current
 assert d==after,(profile,"unknown input to normalize historical inverse",d)
 paths=json.loads((R/record["reversible_parent_bytes"]).read_text())
 assert paths["old_prgs"][profile]==before
 assert paths["new_prgs"][profile]==after
 if profile not in paths["profiles"]:
  assert before==after
  return current
 row=paths["profiles"][profile]
 assert row["old_sha256"]==before and row["candidate_sha256"]==after
 assert row["file_len"]==len(current)
 restored=bytearray(current)
 last=-1
 for index,old_byte in row["original_bytes_at_changed_offsets"]:
  assert 2<=index<len(restored) and 0<=old_byte<=255
  assert index>last
  restored[index]=old_byte
  last=index
 assert sha(restored)==before,(profile,"archived normalization image reconstruction mismatch")
 return bytes(restored)
