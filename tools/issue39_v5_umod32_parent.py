#!/usr/bin/env python3
"""SHA-pinned historical V5 parent reconstruction after PR71 UMOD32 frontend.

Only for frozen pre-PR71 audits. Never undo resident bytes for release use.
"""
from hashlib import sha256
OLD='634e58f536374bc12877e692515f68ab5c5f38954caf5c189a8f67d356289d02'
NEW='5191e44263c24c617a4d5ddc490b3d5fbe7f87c5ac0835af28294fdbc6f9d222'
def digest(b):return sha256(b).hexdigest()
def restore_v5_umod32_parent(prg:bytes)->bytes:
    current=digest(prg)
    if current==OLD:return prg
    assert current==NEW,('unrecognized V5 UMOD32 parent image',current)
    b=bytearray(prg)
    lo=int.from_bytes(b[:2],'little')
    assert lo==0x1000 and len(b)==49042
    def off(a):return 2+a-lo
    assert b[off(0x5e03):off(0x5e06)]==bytes.fromhex('4c805e')
    assert any(b[off(0x5e80):off(0x5e80+147)])
    b[off(0x5e03):off(0x5e06)]=bytes.fromhex('4c5759')
    b[off(0x5e80):off(0x5e80+147)]=bytes(147)
    output=bytes(b)
    assert digest(output)==OLD,('restored V5 historical SHA mismatch',digest(output))
    return output
