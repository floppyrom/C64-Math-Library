#!/usr/bin/env python3
"""Prove that installing the seek kernels changed nothing else in the images.

Compares every resident PRG (and V3/V4 REU image) with the last pre-seek
release commit and requires every changed byte to lie inside the seek code
islands (including the eight JMP slots) or the seek object state. Earlier
evidence recorded against the pre-seek images (for example the 2026-09-21
size refresh) therefore still describes every other routine byte-for-byte.

Writes validation/movement/SEEK_BINARY_DELTA.json.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from mini6502 import Assembler  # noqa: E402
import seek_kernel as K  # noqa: E402

PRE_SEEK = 'cfc89cfc2f0208a2ea4f21b10de02974b9ee65bb'  # "smaller normalize and ATAN2 without timing regressions"
PROFILES = ['v1_balanced', 'v2_pareto_fast', 'v3_reu_512k', 'v4_reu_16m', 'v5_hybrid_lowzp']
REU = {'v3_reu_512k': 'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu',
       'v4_reu_16m': 'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu'}


def sha(b):
    return hashlib.sha256(b).hexdigest()


def git_bytes(path):
    return subprocess.check_output(['git', 'show', f'{PRE_SEEK}:{path}'], cwd=ROOT)


def image(b):
    lo = b[0] | b[1] << 8
    m = bytearray(65536)
    m[lo:lo + len(b) - 2] = b[2:]
    return lo, len(b), m


def owned(profile):
    src_profile = 'v1_balanced' if profile == 'v5_hybrid_lowzp' else profile
    cfg = (ROOT / 'relocatable_source' / src_profile / 'math_config_reference.inc').read_text()
    text = cfg + (ROOT / profile / 'resident/movement/native/seek_dda.asm').read_text()
    mem, _, const = Assembler().assemble(text)
    own = set(mem)
    own |= set(range(const['SEEK8_STATE'], const['SEEK8_STATE'] + K.S8_BYTES))
    own |= set(range(const['SEEK16_STATE'], const['SEEK16_STATE'] + K.S16_BYTES))
    return own, len(mem)


def main():
    out = {'status': 'PASS', 'pre_seek_commit': PRE_SEEK, 'profiles': {}}
    for p in PROFILES:
        rel = f'{p}/resident/math_{p}_game_math.prg'
        old = git_bytes(rel)
        new = (ROOT / rel).read_bytes()
        lo0, n0, m0 = image(old)
        lo1, n1, m1 = image(new)
        assert (lo0, n0) == (lo1, n1), (p, 'PRG span changed')
        own, code = owned(p)
        diff = [a for a in range(65536) if m0[a] != m1[a]]
        outside = [a for a in diff if a not in own]
        assert not outside, (p, 'changes outside seek-owned bytes', [hex(a) for a in outside[:8]])
        row = {'pre_seek_prg_sha256': sha(old), 'current_prg_sha256': sha(new), 'prg_span_bytes': n1 - 2,
               'changed_bytes': len(diff), 'changed_outside_seek': 0, 'seek_code_bytes_incl_jmp_slots': code}
        if p in REU:
            same = git_bytes(REU[p]) == (ROOT / REU[p]).read_bytes()
            assert same, (p, 'REU image changed')
            row['reu_image_unchanged'] = True
        out['profiles'][p] = row
        print(p, 'changed', len(diff), 'bytes, all seek-owned')
    path = ROOT / 'validation/movement/SEEK_BINARY_DELTA.json'
    path.write_text(json.dumps(out, indent=1) + '\n')
    print('SEEK BINARY DELTA PASS')


if __name__ == '__main__':
    main()
