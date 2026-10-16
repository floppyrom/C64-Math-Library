#!/usr/bin/env python3
"""Exact 256-byte signed SINE8 lookup table from all five shipped V1-V5 PRGs.

The bytes are a retained, source-locked binary-data extraction at C64 $9400.
All five publicly shipped 56-entry PRG images contain the same 256 bytes.
Do not synthesize floats or use host-dependent rounding: binary parity matters.
"""
from __future__ import annotations

SINE_HEX = (
    "000306090c101316191c1f2225282b2e313336393c3f414447494c4e51535558"
    "5a5c5e60626466686a6b6d6f70717374757678797a7a7b7c7d7d7e7e7e7f7f7f"
    "7f7f7f7f7e7e7e7d7d7c7b7a7a79787675747371706f6d6b6a68666462605e5c"
    "5a585553514e4c494744413f3c393633312e2b2825221f1c191613100c090603"
    "00fdfaf7f4f0edeae7e4e1dedbd8d5d2cfcdcac7c4c1bfbcb9b7b4b2afadaba8"
    "a6a4a2a09e9c9a9896959391908f8d8c8b8a8887868685848383828282818181"
    "8181818182828283838485868687888a8b8c8d8f9091939596989a9c9ea0a2a4"
    "a6a8abadafb2b4b7b9bcbfc1c4c7cacdcfd2d5d8dbdee1e4e7eaedf0f4f7fafd"
)
SINE_BYTES = bytes.fromhex(SINE_HEX)
assert len(SINE_BYTES) == 256


def emit(address: int):
    """Page-aligned shared immutable table for SIN8/COS8/SINCOS8 links."""
    if address & 255 or not 0 <= address <= 0xFF00:
        raise ValueError("SINE8 shared table must fit one aligned 256-byte page")
    return dict(zip(range(address, address + 256), SINE_BYTES))
