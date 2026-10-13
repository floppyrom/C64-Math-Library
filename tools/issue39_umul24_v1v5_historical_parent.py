#!/usr/bin/env python3
"""Strict old/new SHA-pinned V1/V5 UMUL24 tailcall historical inverse.

For frozen PR78/PR81, PR68/PR71, PR97 and division audits ONLY.
Current source-built 24x24 multiplication remains untouched in the release.
This reverse mapping uses the exact immutable PR105 SHA and cannot accept an
unknown binary or a change outside the documented 0x2700..0x2FFF fast core.
"""
from pathlib import Path
import hashlib,subprocess
ROOT=Path(__file__).resolve().parents[1]
PR105_PARENT="c9acb83a7e33a6af43fafb0eddf868af6311499f"
PUBLISHED={
    "v1_balanced":(
      "41d744c2aaf06a5d40cfece1c16255576950a8e6e3328d5fe4196c0ac753171e",
      "03d2e67a399c31ce7b8456521bcd9cb30a48ef051baa6a9ac50c23cf0bfd0829"),
    "v5_hybrid_lowzp":(
      "b27e0885c7241dd7bdc3b2e25be6b2c616685cb426436a3c2b8260eff7a21ebb",
      "e7546665bc68faf3d6021db91a77bcdf4d32b4d800530264840f443066ad8ffb")
}
def sha(blob:bytes)->str:return hashlib.sha256(blob).hexdigest()
def undo_umul24_tailcall(profile:str,blob:bytes)->bytes:
    if profile not in PUBLISHED:return blob
    previous,candidate=PUBLISHED[profile]
    digest=sha(blob)
    if digest!=candidate:return blob
    rel=f"{profile}/resident/math_{profile}_game_math.prg"
    old=subprocess.check_output(["git","show",f"{PR105_PARENT}:{rel}"],cwd=ROOT)
    assert sha(old)==previous,(profile,"frozen previous resident SHA mismatch")
    assert len(old)==len(blob) and old[:2]==blob[:2],(profile,"PRG geometry changed")
    start=int.from_bytes(old[:2],"little")
    assert start==0x1000,(profile,start)
    changed=[start+i for i,(a,b) in enumerate(zip(old[2:],blob[2:])) if a!=b]
    assert changed and all(0x2700<=pc<0x3000 for pc in changed),(
      profile,"unexpected non-UMUL24 source-island change",list(map(hex,changed[:20])))
    return old
if __name__=="__main__":
    import sys
    p=sys.argv[1]
    b=(ROOT/p/"resident"/f"math_{p}_game_math.prg").read_bytes()
    result=undo_umul24_tailcall(p,b)
    assert sha(result)==PUBLISHED[p][0]
    print("UMUL24 EXACT HISTORICAL INVERSE PASS",p)
