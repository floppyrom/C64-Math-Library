#!/usr/bin/env python3
"""Exact historical DIST8_ACCURATE 256+256-byte tables from all five PRGs.

The original V1–V5 resident files have identical contents at $9A00 and $9B00.
These literal bytes are immutable release reference data: no approximation or
floating-point regeneration. The first table indexes max(abs(X),abs(Y)),
the second indexes min(abs(X),abs(Y)), added modulo 256.
"""
from __future__ import annotations

MAJOR_HEX = (
    "00010203040506070809090a0b0c0d0e0f101112131415161718191a1b1c1c1d"
    "1e1f202122232425262728292a2b2c2d2e2f2f303132333435363738393a3b3c"
    "3d3e3f40414142434445464748494a4b4c4d4e4f50515253545455565758595a"
    "5b5c5d5e5f60616263646566676768696a6b6c6d6e6f70717273747576777879"
    "7a7a7b7c7d7e7f808182838485868788898a8b8c8c8d8e8f9091929394959697"
    "98999a9b9c9d9e9f9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b2b3b4b5"
    "b6b7b8b9babbbcbdbebfc0c1c2c3c4c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4"
    "d5d6d7d7d8d9dadbdcdddedfe0e1e2e3e4e5e6e7e8e9eaeaebecedeeeff0f1f2"
)
MINOR_HEX = (
    "00000101020203030304040505050606070708080809090a0a0a0b0b0c0c0d0d"
    "0d0e0e0f0f0f1010111112121213131414141515161617171718181919191a1a"
    "1b1b1c1c1c1d1d1e1e1f1f1f2020212121222223232424242525262626272728"
    "282929292a2a2b2b2b2c2c2d2d2e2e2e2f2f3030303131323233333334343535"
    "363636373738383839393a3a3b3b3b3c3c3d3d3d3e3e3f3f4040404141424242"
    "434344444545454646474747484849494a4a4a4b4b4c4c4c4d4d4e4e4f4f4f50"
    "50515152525253535454545555565657575758585959595a5a5b5b5c5c5c5d5d"
    "5e5e5e5f5f6060616161626263636364646565666666676768686869696a6a6b"
)
MAJOR_BYTES = bytes.fromhex(MAJOR_HEX)
MINOR_BYTES = bytes.fromhex(MINOR_HEX)
assert len(MAJOR_BYTES) == len(MINOR_BYTES) == 256


def emit(address: int):
    """Two contiguous page-aligned immutable lookup tables."""
    if address & 255 or not 0 <= address <= 0xFE00:
        raise ValueError("DIST8 lookup pair must fit two aligned pages")
    return dict(zip(range(address, address + 512), MAJOR_BYTES + MINOR_BYTES))
