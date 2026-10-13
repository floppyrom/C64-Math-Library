#!/usr/bin/env python3
"""Reconstruct exact pre-PR97 parent binaries from SHA-pinned offline deltas.

Historical regression code MUST compare the original old/new PR78/PR81
sources rather than silently treating a newly optimized resident as its
historical baseline. No git/network or mutable base reference needed.
"""
from pathlib import Path
from issue39_root_historical_parent import undo_root_release
from issue39_umul24_v1v5_historical_parent import undo_umul24_tailcall
import hashlib,json
R=Path(__file__).resolve().parents[1]
LEDGER=R/'validation/review/ISSUE39_U24_TXA_PARENT_RESTORATION.json'
def sha(data):return hashlib.sha256(data).hexdigest()
def restore_pre_txa(profile,prg):
    prg=undo_umul24_tailcall(profile,prg)
    prg=undo_root_release(profile,prg)
    record=json.loads(LEDGER.read_text())
    assert record['status']=='PASS_REVERSIBLE_SHA_PINNED_PARENT_DELTA'
    row=record['profiles'][profile]
    digest=sha(prg)
    if digest==row['old_sha256']:return prg
    if digest!=row['current_sha256']:
        # The caller may be replaying an even older exact PR78/PR81 parent.
        # It remains the caller's responsibility to verify that parent SHA.
        return prg
    assert len(prg)==row['prg_length']
    old=bytearray(prg)
    for part in row['changed_runs']:
        loc=part['offset'];payload=bytes.fromhex(part['old_bytes_hex'])
        assert 0<=loc and loc+len(payload)<=len(old)
        old[loc:loc+len(payload)]=payload
    assert sha(old)==row['old_sha256'],(profile,'not exact historical parent')
    return bytes(old)
if __name__=='__main__':
    import sys
    from pathlib import Path
    profile=sys.argv[1]
    p=R/profile/'resident'/f'math_{profile}_game_math.prg'
    old=restore_pre_txa(profile,p.read_bytes())
    print(profile,'EXACT HISTORICAL RESTORE',sha(old),flush=True)
