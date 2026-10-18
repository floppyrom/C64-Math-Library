#!/usr/bin/env python3
"""Generate the linker-relocatable 0-ZP V2 16/16 divider from canonical source.

Remove ONLY the original fixed-address JMP stubs and rebind the already
source-qualified N/D/Q/R symbols. The entire 1481-byte NMOS arithmetic code
remains otherwise identical to the published V2 donor.
"""
from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT/'relocatable_source/v2_pareto_fast/udiv16_direct_fast.inc'
DEST = ROOT/'routines/divide/udiv16_v2_zerozp.asm'
ORIGINAL = CANONICAL.read_text(encoding='utf-8')
START = '* = MATH_IO-$0800'
assert ORIGINAL.count(START)==1
src = ORIGINAL[ORIGINAL.index(START):].replace(START, '* = KERNEL_CODE', 1)
for old,new in [('MATH_N','INPUT_NUM'),('MATH_D','INPUT_DIV'),('MATH_Q','OUTPUT_QUOT'),('MATH_R','OUTPUT_REM')]:
    src=src.replace(old,new)
header = '''; Relocatable 0-ZP historical V2 size-fast unsigned 16/16 public divider.
; Canonical source: relocatable_source/v2_pareto_fast/udiv16_direct_fast.inc
; Original fixed-address public JMP stubs omitted. Source original remainder.
; Returns complete Q16, R16, C (D=0). Caller inputs are untouched, CLD required.
; NMOS 6510 LAX/ANC, no writable code; no ZP, scratch, or init.
!cpu 6510
KERNEL_CODE = $8000
INPUT_NUM = $C010
INPUT_DIV = $C014
OUTPUT_QUOT = $C018
OUTPUT_REM = $C01C
'''
DEST.write_text(header+src)
print('GENERATED',DEST.relative_to(ROOT),'from source SHA256',hashlib.sha256(CANONICAL.read_bytes()).hexdigest())
