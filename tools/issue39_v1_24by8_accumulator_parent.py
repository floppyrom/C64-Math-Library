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
from issue39_u24_txa_historical_parent import restore_pre_txa
from issue39_root_historical_parent import undo_root_release
from issue39_umul24_v1v5_historical_parent import undo_umul24_tailcall
PR78='28c7039614f77a2b3c9dd4d3b6ea4743b4e839eaee280bf6ee12285b18cad4b0'
OLD_SOURCE=R/'tools/candidates/issue39_v1_24by8_shared_subtraction.asm'
NEW_SOURCE=R/'tools/candidates/issue39_v1_24by8_accumulator.asm'
SMC_SOURCE=R/'tools/candidates/issue39_v1_24by8_accumulator_selfmod.asm'
PR81='cdc2ca502d664055f896d7ad1601e8dd994b61be33e24bde3e25fc0dcbee1cdd'
SMC='d6e013740a8c1ac8f35fa895b69afb8bf6226cde99f491a470b4518a7c6dfa9a'

def sha(b):return hashlib.sha256(b).hexdigest()
def undo_v1_3216_coldpath_for_historical_audit(prg: bytes) -> bytes:
    """Reverse ONLY the exact SHA-pinned PR100 V1 32/16 code displacement.

    Historical PR78/PR81 UDIV24 proofs must replay their true old binary
    rather than accepting a current V1 image with unrelated later 32/16 bytes.
    Verify that the inverse maps back to the immutable prior main digest.
    """
    parents={
        # V1 uses the optimized 32/16 arithmetic directly; V5 retains the
        # source-backed V1 island even while its public API uses a V2 donor.
        '9af44deda4a1527a0ea5ecc09a48e1ec4927a45099f7b2e26ced0f618274c0a4':
          '2567dccbc4e01f3d606e80126c8150c58e4f30b8b726ff38e116c6aaec644178',
        '0662a9644ee4ebb6df7a06f9c77a40ffb5308b69ecd5e6bc9c7d6250b5bd5750':
          '431824532ef218423b77bfc8353ccac8e380847c824f040aeffa5c7903c0ea2d',
    }
    old=parents.get(sha(prg))
    if old is None:return prg
    lo=int.from_bytes(prg[:2],'little')
    assert lo==0x1000
    off=lambda addr: 2+addr-lo
    raw=bytearray(prg)
    assert raw[off(0x4503):off(0x4505)]==bytes((0xb0,0xeb))
    assert raw[off(0x1b6a):off(0x1b6d)]==bytes.fromhex('4c6c45')
    cold=bytes(raw[off(0x44f0):off(0x44f7)])
    assert cold==bytes.fromhex('a900851a851b60')
    body=bytes(raw[off(0x4505):off(0x4574)])
    assert len(body)==111
    raw[off(0x450c):off(0x457b)]=body
    raw[off(0x4503):off(0x450c)]=bytes.fromhex('9007a900851a851b60')
    raw[off(0x44f0):off(0x44f7)]=bytes(7)
    raw[off(0x1b6a):off(0x1b6d)]=bytes.fromhex('4c7345')
    assert sha(raw)==old,('historical V1 32/16 inverse drift',sha(raw))
    return bytes(raw)

def restore_pr78(prg:bytes)->bytes:
    prg=undo_umul24_tailcall('v1_balanced',prg)
    prg=undo_root_release('v1_balanced',prg)
    prg=undo_v1_3216_coldpath_for_historical_audit(prg)
    prg=restore_pre_txa('v1_balanced',prg)
    if sha(prg)==PR78:return prg
    lo=int.from_bytes(prg[:2],'little')
    assert lo==0x1000
    off=2+0x1d00-lo
    if sha(prg)==SMC:
        pre=bytearray(prg)
        portable,labels,_=Assembler().assemble(NEW_SOURCE.read_text())
        smc,smc_labels,_=Assembler().assemble(SMC_SOURCE.read_text())
        assert len(portable)==61 and len(smc)==68 and labels['V1LAT_24_BY_8']==smc_labels['V1LAT_24_BY_8']==0x1d00
        assert pre[off:off+68]==bytes(smc[a] for a in range(0x1d00,0x1d00+68))
        assert pre[off+68:off+84]==bytes(16)
        pre[off:off+61]=bytes(portable[a] for a in range(0x1d00,0x1d00+61))
        pre[off+61:off+84]=bytes(23)
        assert sha(pre)==PR81
        prg=bytes(pre)
    assert sha(prg) in (PR78,PR81), ('unknown parent',sha(prg))
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
