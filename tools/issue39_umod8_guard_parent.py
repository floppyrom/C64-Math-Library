#!/usr/bin/env python3
"""Reconstruct pre-UMOD8 optimized V1/V5 resident bytes with exact SHA-256.

Only two locations may differ: public UMOD8 first JMP and the previously
zero 128-byte REG_LOW+$0E00 island. This source-backed reversible capsule
keeps earlier PR57/59/60/61/62 correctness/timing proofs historically valid.
"""
import hashlib
from issue39_v1_u16_q2_parent import restore_v1_q2_parent
# PR67 changes six five-byte 16-bit branch slots in the V5 hybrid donor.
# To validate PR57/59/60/61/62's historically frozen SHA and cycle vectors,
# undo only those six SHA-pinned edits before restoring the older UMOD8 guard.
V5_PR67_CURRENT_SHA = '26981cc03b06d1a797917ae34a5d8969db466435fff496a758a262bac75b254b'
V5_PR67_PREVIOUS_SHA = 'bed1ee986857d045d452036d78d0d6cbdc078dbc3407f8a860a8fd54f8395fa2'
V5_PR67_RESTORE = (
    (0xB25F, '90034ce7b2'),
    (0xB27A, 'b0034c87b2'),
    (0xB295, 'b0034ca2b2'),
    (0xB884, 'b0034c92b8'),
    (0xB8A0, 'b0034caeb8'),
    (0xB8E4, 'b0034c76b8'),
)
def restore_v5_pr67_u16_parent(prg):
    current=hashlib.sha256(prg).hexdigest()
    if current==V5_PR67_PREVIOUS_SHA:return prg
    assert current==V5_PR67_CURRENT_SHA,('unsupported V5 source version',current)
    b=bytearray(prg);lo=int.from_bytes(b[:2],'little')
    assert lo==0x1000
    for address,old_hex in V5_PR67_RESTORE:
        off=2+address-lo
        before=bytes.fromhex(old_hex)
        expected=bytes((0x4c,before[3],before[4],0xea,0xea))
        assert b[off:off+5]==expected,(hex(address),b[off:off+5].hex(),expected.hex())
        b[off:off+5]=before
    reverted=bytes(b)
    assert hashlib.sha256(reverted).hexdigest()==V5_PR67_PREVIOUS_SHA
    return reverted
PARENT_SHA={
 'v1_balanced':'795cf2320f1fee8b097641bb87f3e2ff591b3c84329b700f35ec7d4ef9593387',
 'v5_hybrid_lowzp':'9f59d7f8eb8d5cd78d0f01867418e77db5e867e06b9b43afe34df36ccea82dc2'}
def restore_umod8_parent(profile,prg):
 if profile=='v1_balanced':prg=restore_v1_q2_parent(prg)
 if profile=='v5_hybrid_lowzp':prg=restore_v5_pr67_u16_parent(prg)
 expected=PARENT_SHA[profile]
 if hashlib.sha256(prg).hexdigest()==expected:return prg
 lo=int.from_bytes(prg[:2],'little')
 def offset(address):return 2+address-lo
 assert lo==0x1000
 assert prg[offset(0x3200):offset(0x3203)]==bytes.fromhex('4c001e'),profile
 assert prg[offset(0x1e00):offset(0x1e05)]==bytes.fromhex('ad14c0c920'),profile
 assert prg[offset(0x1e4d):offset(0x1e80)]==bytes(0x80-0x4d),profile
 b=bytearray(prg)
 b[offset(0x3200):offset(0x3203)]=bytes.fromhex('ad10c0')
 b[offset(0x1e00):offset(0x1e80)]=bytes(0x80)
 assert hashlib.sha256(b).hexdigest()==expected,(profile,hashlib.sha256(b).hexdigest(),expected)
 return bytes(b)
