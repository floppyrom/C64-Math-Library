#!/usr/bin/env python3
"""Reconstruct exact merged PR78 V1 parent before historical unsigned audits.

Only the 84-byte V1 $1D00 island is normalized; all other bytes remain identical.
This is intentionally NOT a production code path.
"""
from __future__ import annotations
from pathlib import Path
import hashlib,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from mini6502 import Assembler
PR78='28c7039614f77a2b3c9dd4d3b6ea4743b4e839eaee280bf6ee12285b18cad4b0'
OLD_SOURCE=R/'tools/candidates/issue39_v1_24by8_shared_subtraction.asm'
NEW_SOURCE=R/'tools/candidates/issue39_v1_24by8_accumulator.asm'

def sha(b):return hashlib.sha256(b).hexdigest()
def restore_pr78(prg:bytes)->bytes:
    if sha(prg)==PR78:return prg
    lo=int.from_bytes(prg[:2],'little')
    assert lo==0x1000
    off=2+0x1d00-lo
    old,l,_=Assembler().assemble(OLD_SOURCE.read_text())
    new,n,_=Assembler().assemble(NEW_SOURCE.read_text())
    assert l['V1LAT_24_BY_8']==n['V1LAT_24_BY_8']==0x1d00
    assert len(old)==69 and len(new)==61
    assert prg[off:off+61]==bytes(new[a] for a in range(0x1d00,0x1d00+61))
    assert prg[off+61:off+84]==bytes(23)
    out=bytearray(prg)
    out[off:off+69]=bytes(old[a] for a in range(0x1d00,0x1d00+69))
    out[off+69:off+84]=bytes(15)
    assert sha(out)==PR78,('cannot restore precise PR78 parent',sha(out))
    return bytes(out)
