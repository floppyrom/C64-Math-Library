#!/usr/bin/env python3
"""Exact SHA-pinned inverse of the 2026-10-13 in-place ISQRT16 replacement.

Historic DIV/MOD screens must evaluate original historical machine-code
images, not reject a newer resident because an unrelated square-root
implementation changed. Only bytes within the old ISQRT16 source-owned island
may differ. This helper does NOT modify any production binary.

git-show references an IMMUTABLE commit, and SHA-256 of both old and new
residents is verified. CI must check out full history; never accept a moving
branch as historical source.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,subprocess
R=Path(__file__).resolve().parents[1]
PARENT="f7164dd07223f2f1761dfe6260293af3420357fa"
ROOT_IMAGES={
 "v1_balanced":(
  "9af44deda4a1527a0ea5ecc09a48e1ec4927a45099f7b2e26ced0f618274c0a4",
  "41d744c2aaf06a5d40cfece1c16255576950a8e6e3328d5fe4196c0ac753171e",
  0xC8DB,0xCA24),
 "v2_pareto_fast":(
  "c3c0898bc61a9836e7f58d1b51088ccc644613bf68d9e4199aa1243c4f164c84",
  "8b52fe47c4d6aff5331a5d3a4aca73e34d84696a5aa83dba14c48f62a4ee9d92",
  0xC836,0xC966),
 "v3_reu_512k":(
  "7ec22f5272b54c129a80e4989a8e28246336c11e6e9b442c1e271d0258a7727a",
  "52565df27dc892be9da8e12b8ac6267179debbd3d521331d7cd3d0a49ced2755",
  0xC841,0xC971),
 "v5_hybrid_lowzp":(
  "0662a9644ee4ebb6df7a06f9c77a40ffb5308b69ecd5e6bc9c7d6250b5bd5750",
  "b27e0885c7241dd7bdc3b2e25be6b2c616685cb426436a3c2b8260eff7a21ebb",
  0xC8DB,0xCA24)
}
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def historical_image(profile:str):
    assert profile in ROOT_IMAGES,profile
    expected_old,_,_,_=ROOT_IMAGES[profile]
    rel=f"{profile}/resident/math_{profile}_game_math.prg"
    old=subprocess.check_output(["git","show",f"{PARENT}:{rel}"],cwd=R)
    assert sha(old)==expected_old,("historical root donor SHA drift",profile,sha(old))
    return old
def undo_root_release(profile:str,blob:bytes)->bytes:
    # V2 public UMUL8 changed independently after the root release. Revert
    # its exact source-owned byte islands before historical root/div replay.
    if profile=='v2_pareto_fast':
        from issue39_v2_umul8_parent import undo_current_v2_umul8
        blob=undo_current_v2_umul8(profile,blob)
    if profile not in ROOT_IMAGES:return blob
    old_sha,new_sha,lo,hi=ROOT_IMAGES[profile]
    digest=sha(blob)
    if digest==old_sha:return blob
    if digest!=new_sha:return blob
    old=historical_image(profile)
    assert len(old)==len(blob) and old[:2]==blob[:2],(profile,"image geometry")
    load=int.from_bytes(blob[:2],"little")
    assert load==0x1000,(profile,hex(load))
    changed=[load+i for i,(a,b) in enumerate(zip(old[2:],blob[2:])) if a!=b]
    assert changed and all(lo<=x<hi for x in changed),(
       profile,"integer-root source changed outside preserved code island",changed[:20])
    assert sha(old)==old_sha
    return old
if __name__=="__main__":
    import sys
    p=sys.argv[1]
    b=(R/p/"resident"/f"math_{p}_game_math.prg").read_bytes()
    assert sha(undo_root_release(p,b))==ROOT_IMAGES[p][0]
    print("HISTORICAL ROOT INVERSE PASS",p)
