#!/usr/bin/env python3
"""Reconstruct pre-UMOD8 optimized V1/V5 resident bytes with exact SHA-256.

Only two locations may differ: public UMOD8 first JMP and the previously
zero 128-byte REG_LOW+$0E00 island. This source-backed reversible capsule
keeps earlier PR57/59/60/61/62 correctness/timing proofs historically valid.
"""
import hashlib
PARENT_SHA={
 'v1_balanced':'795cf2320f1fee8b097641bb87f3e2ff591b3c84329b700f35ec7d4ef9593387',
 'v5_hybrid_lowzp':'9f59d7f8eb8d5cd78d0f01867418e77db5e867e06b9b43afe34df36ccea82dc2'}
def restore_umod8_parent(profile,prg):
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
