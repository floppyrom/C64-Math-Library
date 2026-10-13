#!/usr/bin/env python3
"""Reversible exact V2 UMUL8 source upgrade for historical arithmetic screens.

Only applicable to two immutable SHA-pinned V2 resident images, and only when
ALL byte changes are owned by the public UMUL8 wrapper and its shifted kernel.
Never used in released multiplication or general caller pathways.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,subprocess
R=Path(__file__).resolve().parents[1]
PARENT="ed0d0330c8130cb0adb6c7e8d3d62b9ca8bb9ab7"
OLD="8b52fe47c4d6aff5331a5d3a4aca73e34d84696a5aa83dba14c48f62a4ee9d92"
NEW="71648ececccba3186a1b186144dbace5e345a9a0967d397ec1db0655cef31c04"
PROFILE="v2_pareto_fast"
def sha(blob):return hashlib.sha256(blob).hexdigest()
def undo_current_v2_umul8(profile,blob):
    if profile!=PROFILE:return blob
    dig=sha(blob)
    if dig==OLD:return blob
    if dig!=NEW:return blob
    p=f"{PROFILE}/resident/math_{PROFILE}_game_math.prg"
    original=subprocess.check_output(["git","show",PARENT+":"+p],cwd=R)
    assert sha(original)==OLD,('immutable parent not accessible',sha(original))
    assert len(original)==len(blob) and original[:2]==blob[:2]
    load=int.from_bytes(blob[:2],'little')
    assert load==0x1000
    changed=[load+i for i,(a,b) in enumerate(zip(original[2:],blob[2:])) if a!=b]
    assert changed
    assert all((0x3000<=pc<0x3013) or (0x52FE<=pc<0x5323)
               for pc in changed),('unexpected delta outside UMUL8 source islands',
                                 list(map(hex,changed[:20])))
    assert sha(original)==OLD
    return original
if __name__=='__main__':
    b=(R/PROFILE/'resident'/f'math_{PROFILE}_game_math.prg').read_bytes()
    assert sha(undo_current_v2_umul8(PROFILE,b))==OLD
    print('V2 UMUL8 SHA-PINNED HISTORICAL RESTORATION PASS')
