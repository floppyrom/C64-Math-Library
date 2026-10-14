#!/usr/bin/env python3
"""Issue #39: bounded SEEK8 INIT rate-synthesis research, NOT production code.

The library's SEEK8_INIT repeated-add loop determines
(whole,rem) = divmod(speed_integer * minor_delta, major_delta).
A potential constant-bound binary implementation takes seven shift-add
rounds plus eight quotient/restoring rounds. This tests register-width
carry behavior exhaustively, including the rem(k+1) plane. No code-size,
real 6502 cycle or public ABI/resource improvement is claimed here.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
from pathlib import Path

R=Path(__file__).resolve().parents[1]
DEST=R/"validation/review/ISSUE39_SEEK8_BINARY_RATE_RESEARCH_2026-10-14.json"

def synthesize(dmaj:int,dmin:int,speed:int)->tuple[int,int]:
    """Simulate NMOS 6502 8-bit register/borrow behavior, not Python divmod."""
    assert 1<=dmaj<=255 and 0<=dmin<=dmaj and 0<=speed<=126
    multiplier_lo=dmin
    multiplier_hi=0
    product_lo=0
    product_hi=0
    multiplier_bits=speed
    for _ in range(7):
        take=multiplier_bits&1
        multiplier_bits>>=1
        if take:
            low_sum=product_lo+multiplier_lo
            product_lo=low_sum&255
            product_hi=(product_hi+multiplier_hi+(low_sum>>8))&255
        shiftcarry=multiplier_lo>>7
        multiplier_lo=(multiplier_lo<<1)&255
        multiplier_hi=((multiplier_hi<<1)&255)|shiftcarry
    remainder=product_hi
    whole=0
    for _ in range(8):
        incoming=(product_lo>>7)&1
        product_lo=(product_lo<<1)&255
        rem9=(remainder<<1)|incoming
        overflow=rem9>255
        rem8=rem9&255
        if overflow or rem8>=dmaj:
            remainder=(rem8-dmaj)&255
            whole=((whole<<1)|1)&255
        else:
            remainder=rem8
            whole=(whole<<1)&255
    return whole,remainder

def existing_repeated_add(dmaj:int,dmin:int,speed:int)->tuple[int,int]:
    """Emulate the existing 8-bit ADC/BCS/CMP/SBC loop for paired spot checks."""
    a=0
    whole=0
    for _ in range(speed):
        mixed=a+dmin
        carry=mixed>255
        a=mixed&255
        if carry or a>=dmaj:
            a=(a-dmaj)&255
            whole+=1
    return whole,a

def additional_plane(major,minor,whole,rem):
    a=rem+minor
    return (whole+int(a>=major),a-major if a>=major else a)

def prove(smoke=False):
    h=hashlib.sha256()
    count=0
    random_compat=random.Random(0x39A80)
    paired=0
    speeds=(0,1,2,3,7,15,31,63,64,126) if smoke else range(127)
    for dmaj in range(1,256):
        for dmin in range(dmaj+1):
            for k in speeds:
                whole,rem=synthesize(dmaj,dmin,k)
                assert (whole,rem)==divmod(k*dmin,dmaj),(dmaj,dmin,k,whole,rem)
                nxt=additional_plane(dmaj,dmin,whole,rem)
                assert nxt==divmod((k+1)*dmin,dmaj),(dmaj,dmin,k,"next plane",nxt)
                assert 0<=whole<=126 and 0<=rem<dmaj
                if k in (0,1,3,15,63,126) and (dmaj+dmin)%13==0:
                    assert (whole,rem)==existing_repeated_add(dmaj,dmin,k)
                    paired+=1
                h.update(bytes((dmaj,dmin,k,whole,rem)))
                count+=1
    for _ in range(40000):
        dmaj=random_compat.randrange(1,256)
        dmin=random_compat.randrange(dmaj+1)
        speed=random_compat.randrange(127)
        assert synthesize(dmaj,dmin,speed)==existing_repeated_add(dmaj,dmin,speed)
        paired+=1
    return {
        "status":"PASS_MATH_RESEARCH_ONLY_NOT_PRODUCTION",
        "full_domain":not smoke,
        "rate_cases":count,
        "old_8bit_loop_paired_cases":paired,
        "canonical_tuple_digest_sha256":h.hexdigest(),
        "domain":{"dmaj":"1..255","dmin":"0..dmaj","speed_integer":"0..126"},
        "fractional_speed":"existing extra rem(k+1) plane exact",
        "complexity":{"current":"0..126 repeated-add rounds","candidate":"7 shift/add and 8 quotient rounds"},
        "assembly_transplant_certified":False,
        "code_bytes_measured":False,
        "cpu_cycles_measured":False,
        "native_vice_tested":False,
        "public_abi_resource_qualified":False,
        "production_merged":False,
        "private_optisearch_source_included":False,
        "note":"Next gate: hand-lower to 6502, preserve X/public IO/19-byte scratch and all 8 object slots; benchmark normal and high-speed distributions, native x64sc and both source relocation maps."
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--smoke",action="store_true")
    args=a.parse_args()
    record=prove(args.smoke)
    DEST.parent.mkdir(parents=True,exist_ok=True)
    DEST.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
    print("SEEK8 RATE RESEARCH",record["status"],record["rate_cases"],
          "rate samples /",record["old_8bit_loop_paired_cases"],"old-loop paired",flush=True)
if __name__=="__main__":main()
