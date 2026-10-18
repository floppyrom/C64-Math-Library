#!/usr/bin/env python3
"""Matched 384-input complete public UMOD16 cycle/ABI proof for speed selection.

Compare the source-backed biased fast modulo kernel with the independent
zero-ZP direct chain. Both preserve N16/D16 and Q16; both return R16 and
C=1 only on divisor zero. This is a 6502 CPU-model measurement, not
native/physical C64 elapsed timing.
"""
from __future__ import annotations

import hashlib
import random
import tempfile
from pathlib import Path

from mini6502 import CPU

ROOT = Path(__file__).resolve().parents[1]
SEED = 0x1616C64
COUNT = 384
CORPUS_SHA256 = '2258e90b0e86173fc502c83e5ca8506f5adbe8704bd6f4aaeb006578877f4dcb'
EDGE = (0, 1, 2, 3, 7, 255, 256, 65535, 0x8000)
EXPECTED = frozenset(('link:biased', 'link:direct-zerozp'))
RESOURCES = {
    'link:biased': ((244, 18), 2, 0),
    'link:direct-zerozp': ((16, 945, 15), 0, 2),
}
DONORS = {
    'link:biased': ('routines/standalone_lab/portable/mod_u16_biased_carry.asm',),
    'link:direct-zerozp': ('routines/standalone_lab/portable/mod_u16_direct_zerozp.asm',),
}


def corpus():
    rng = random.Random(SEED)
    pairs = [(n, d) for n in EDGE for d in EDGE]
    while len(pairs) < COUNT:
        pairs.append((rng.getrandbits(16), rng.choice(
            (0, 1, 2, 255, 256, 65535, rng.getrandbits(16)))))
    return pairs


def bench_umod16(modules, base, io, scratch, root=ROOT, zp=0x50):
    """Return complete-call means for every source variant, fail-closed."""
    if set(modules) != EXPECTED:
        raise ValueError('UMOD16 candidate set changed; requalify')
    pairs = corpus()
    digest = hashlib.sha256(b''.join(n.to_bytes(2, 'little') +
                 d.to_bytes(2, 'little') for n, d in pairs)).hexdigest()
    if digest != CORPUS_SHA256:
        raise ValueError('UMOD16 deterministic operand corpus changed')
    import math_builder
    import selective_linker as linker
    index = math_builder.operation_index(root)
    means = {}
    sources = {}
    donors = {}
    for ident, spec in sorted(modules.items()):
        parts = tuple(n for _, n in spec['segments'])
        if (parts, spec['zp'], spec['scratch']) != RESOURCES[ident]:
            raise ValueError('UMOD16 source resource contract changed: ' + ident)
        if spec.get('requires_reu') or spec.get('requires_writable_code'):
            raise ValueError('UMOD16 unexpectedly requires REU or SMC')
        if spec.get('share_producer') or spec.get('multi_entry'):
            raise ValueError('UMOD16 unexpectedly claims shared image identity')
        for path in DONORS[ident]:
            if not (root / path).is_file():
                raise ValueError('UMOD16 source missing: ' + path)
        plan = math_builder.create_plan(index, ['UMOD16'], objective='size',
             ram_budget=1100, zp_budget=2, pins={'UMOD16': ident})
        with tempfile.TemporaryDirectory(prefix='umod16_perf_') as folder:
            target = Path(folder)
            manifest = linker.build(plan, target, root=root,
                   memory={'code_base': base, 'math_io': io,
                           'zp_base': zp, 'scratch_base': scratch})
            op = manifest['operations'][0]
            if op['api'] != 'MATH_UMOD16' or op['variant'] != ident:
                raise ValueError('UMOD16 pinned source changed')
            prg = (target / 'math_selective.prg').read_bytes()
            if prg[:2] != bytes((base & 255, base >> 8)):
                raise ValueError('UMOD16 linked origin changed')
            mem = bytearray(65536)
            mem[base:base+len(prg)-2] = prg[2:]
            cpu = CPU(mem)
            start_sp = cpu.sp
            before = bytes(mem[base:base+len(prg)-2])
            total = 0
            entry = int(op['entry'][1:], 16)
            for i, (n, d) in enumerate(pairs):
                numerator = n.to_bytes(2, 'little') + b'\xaa\xaa'
                divisor = d.to_bytes(2, 'little') + b'\xbb\xbb'
                cpu.mem[io+16:io+20] = numerator
                cpu.mem[io+20:io+24] = divisor
                cpu.mem[io+24:io+28] = b'\x55' * 4
                cpu.mem[io+28:io+32] = b'\x66' * 4
                cpu.d = 0
                cpu.c = (i ^ n ^ d) & 1
                total += cpu.call(entry, 500000)
                rem = int.from_bytes(cpu.mem[io+28:io+30], 'little')
                if (rem != (n % d if d else 0) or cpu.c != int(d == 0)
                    or cpu.mem[io+24:io+28] != b'\x55'*4
                    or cpu.mem[io+30:io+32] != b'\x66'*2
                    or cpu.mem[io+16:io+20] != numerator
                    or cpu.mem[io+20:io+24] != divisor
                    or cpu.sp != start_sp):
                    raise ValueError('UMOD16 public R/C/Q/input/SP failed: '
                                     + repr((ident, i, n, d, rem, cpu.c)))
            if bytes(mem[base:base+len(prg)-2]) != before:
                raise ValueError('UMOD16 unexpectedly mutated executable code')
            means[ident] = total / COUNT
            sources[ident] = hashlib.sha256((root / spec['source']).read_bytes()).hexdigest()
            donors[ident] = {path: hashlib.sha256((root / path).read_bytes()).hexdigest()
                             for path in DONORS[ident]}
    return {
        'basis': 'cpu-model-unsigned-16by16-mod-complete-public-r16-v1',
        'cases': COUNT, 'corpus_sha256': digest, 'cpu_model_only': True,
        'native_hardware_timing': False, 'mean_cycles': means,
        'code_origin': '$%04X' % base, 'io_origin': '$%04X' % io,
        'scratch_origin': '$%04X' % scratch, 'zp_origin': '$%02X' % zp,
        'source_sha256': sources, 'donor_sha256': donors,
        'note': 'Identical operands, R16/C, preserved N16/D16/Q16/stack; no REU/SMC; native VICE validation separate',
    }



if __name__ == '__main__':
    print('UMOD16 corpus:', CORPUS_SHA256)
