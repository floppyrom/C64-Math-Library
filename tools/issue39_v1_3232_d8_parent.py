#!/usr/bin/env python3
"""Normalize V1's current 32/32 D8 binary to its exact merged PR61 parent.

Old certificates must be tested on their historical parent image. Reverse only
the new 32/32 branch and previously unowned 128-byte REG_LOW D8 island.
"""
import hashlib
from issue39_umod8_guard_parent import restore_umod8_parent
PR61_SHA='67d709a3006e5529d49b579be20747b292f466679ea42ac24fd5384e4d71879e'
def restore_pr61(blob:bytes)->bytes:
    blob=restore_umod8_parent('v1_balanced',blob)
    lo=blob[0]|blob[1]<<8
    if hashlib.sha256(blob).hexdigest()==PR61_SHA:return blob
    a=lambda x:2+x-lo
    assert blob[a(0x6859):a(0x685c)]==bytes.fromhex('4c801d')
    assert blob[a(0x1d80):a(0x1d84)]==bytes.fromhex('ad16c00d')
    assert len(blob)==49042
    b=bytearray(blob)
    b[a(0x6859):a(0x685c)]=bytes.fromhex('4c00c1')
    b[a(0x1d80):a(0x1e00)]=bytes(128)
    assert hashlib.sha256(b).hexdigest()==PR61_SHA,'historical V1 PR61 SHA mismatch'
    return bytes(b)
