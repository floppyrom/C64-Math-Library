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
# Production UMUL8 was released after the frozen UMUL24/roots certificates.
# Historical audits require their *exact* old input image. Undo only the 11
# SHA-pinned bytes in the two disjoint UMUL8 islands, never a production PRG.
UMUL8_RELEASE_IMAGES={
    "v1_balanced":(
      "03d2e67a399c31ce7b8456521bcd9cb30a48ef051baa6a9ac50c23cf0bfd0829",
      "6057085c39e6fbe777ceea09e78cf4bcd05cc1606dffcbc5ee8e3ae2d32e56e0"),
    "v5_hybrid_lowzp":(
      "e7546665bc68faf3d6021db91a77bcdf4d32b4d800530264840f443066ad8ffb",
      "a29e07795b0dd4e6817ca1adb164603a2afabb4b413b7928ec0da5d753609f01"),
}
UMUL8_OLD_PUBLIC=bytes.fromhex("a5 14 8d 08 c0 18 60")
UMUL8_NEW_PUBLIC=bytes.fromhex("18 60 8d 08 c0 18 60")
UMUL8_OLD_CORE=bytes.fromhex("85 14 b1 12 fd 00 82 60 00")
UMUL8_NEW_CORE=bytes.fromhex("8d 08 c0 b1 12 fd 00 82 60")

def undo_umul8_release(profile:str,blob:bytes)->bytes:
    if profile not in UMUL8_RELEASE_IMAGES:return blob
    previous,current=UMUL8_RELEASE_IMAGES[profile]
    digest=sha(blob)
    if digest==previous:return blob
    if digest!=current:return blob
    lo=int.from_bytes(blob[:2],'little')
    assert lo==0x1000 and len(blob)==49042,(profile,"unexpected resident geometry")
    at=lambda addr: 2+addr-lo
    assert blob[at(0x3014):at(0x301b)]==UMUL8_NEW_PUBLIC,(profile,"UMUL8 public tail drift")
    assert blob[at(0x4714):at(0x471d)]==UMUL8_NEW_CORE,(profile,"UMUL8 core drift")
    old=bytearray(blob)
    old[at(0x3014):at(0x301b)]=UMUL8_OLD_PUBLIC
    old[at(0x4714):at(0x471d)]=UMUL8_OLD_CORE
    restored=bytes(old)
    assert sha(restored)==previous,(profile,"UMUL8 historical inverse drift",sha(restored))
    return restored

# Each research inverse is exactly pinned to the final pre-PR118 main
# resident. It may only affect frozen historical test replay; no PRGs change.
RARECARRY_PARENT="fa5457729d764ffc9c24f8cb5bde2e5790eb79fe"
RARECARRY_IMAGES={
    "v1_balanced":(
        "f18253b37f2b537062b9caa2990497becb0c3a76c7e79dcbb728227cfa80c1f7",
        "6057085c39e6fbe777ceea09e78cf4bcd05cc1606dffcbc5ee8e3ae2d32e56e0"),
    "v5_hybrid_lowzp":(
        "2c4f3494dd89ab883818fc1c006e603f620078df21bc3b9d8326b5a60773ad90",
        "a29e07795b0dd4e6817ca1adb164603a2afabb4b413b7928ec0da5d753609f01"),
}
# Later fixed-output SHR16 producer changes are confined to two cold
# carry-clear tails. Historical UDIV24/UMOD24 research replays the immutable
# pre-SHR16 parent; never alter the new deployable resident.
FIXED_SHR16_PARENT="bfc43c2f6643a893304799683f73396e0eba3096"
FIXED_SHR16_IMAGES={
    "v1_balanced":(
      "1ec65b1fcf87b7424325cc64a410401698f51ed04fb8c1fba861fa41457f9a82",
      "f18253b37f2b537062b9caa2990497becb0c3a76c7e79dcbb728227cfa80c1f7",
      (0xc573,0xc574,0xc59c,0xc59d)),
    "v5_hybrid_lowzp":(
      "2ca2e91a494c806d60e705ac0c3ec49fc3f85c0c967a3c405eb5b0b46bd2afcc",
      "2c4f3494dd89ab883818fc1c006e603f620078df21bc3b9d8326b5a60773ad90",
      (0xc573,0xc574,0xc59c,0xc59d))
}
def undo_fixed_shr16_release(profile:str,blob:bytes)->bytes:
    row=FIXED_SHR16_IMAGES.get(profile)
    if row is None or sha(blob)!=row[0]:return blob
    rel=f"{profile}/resident/math_{profile}_game_math.prg"
    old=subprocess.check_output(["git","show",f"{FIXED_SHR16_PARENT}:{rel}"],cwd=ROOT)
    assert sha(old)==row[1],(profile,"fixed-shift old resident hash drift")
    assert len(blob)==len(old) and blob[:2]==old[:2]
    start=int.from_bytes(blob[:2],"little")
    assert start==0x1000
    deltas=tuple(start+i for i,(a,b) in enumerate(zip(old[2:],blob[2:])) if a!=b)
    assert deltas==row[2],(profile,"fixed-shift changed outside two return tails",deltas)
    for index,addr in enumerate(deltas):
        k=2+addr-start
        assert old[k]==(0x18 if index%2==0 else 0x60)
        assert blob[k]==(0x60 if index%2==0 else 0xea)
    return old

def undo_rarecarry_release(profile:str,blob:bytes)->bytes:
    blob=undo_fixed_shr16_release(profile,blob)
    row=RARECARRY_IMAGES.get(profile)
    if row is None or sha(blob)!=row[0]:return blob
    rel=f"{profile}/resident/math_{profile}_game_math.prg"
    old=subprocess.check_output(["git","show",f"{RARECARRY_PARENT}:{rel}"],cwd=ROOT)
    assert sha(old)==row[1],(profile,"rarecarry parent SHA drift")
    assert len(blob)==len(old) and blob[:2]==old[:2]
    start=int.from_bytes(blob[:2],"little")
    assert start==0x1000
    delta=[start+i for i,(a,b) in enumerate(zip(old[2:],blob[2:])) if a!=b]
    assert delta and all(0x2700<=pc<0x3000 for pc in delta),(
        profile,"rarecarry changed outside FAST24",list(map(hex,delta[:24])))
    return old

def undo_umul24_tailcall(profile:str,blob:bytes)->bytes:
    blob=undo_rarecarry_release(profile,blob)
    blob=undo_umul8_release(profile,blob)
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
