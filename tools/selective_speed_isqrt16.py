#!/usr/bin/env python3
"""Matched complete-public-call ISQRT16 square-table vs radix4 CPU model.

Both sources use identical 384 full-domain input pairs and a complete Z16/C
public ABI, with input, stack, output sentinel and code immutability checks.
Cycle observations are simulated 6502 cycles, not physical C64 timings.
"""
from __future__ import annotations
import hashlib
import random
import tempfile
from math import isqrt
from pathlib import Path
from mini6502 import CPU

ROOT = Path(__file__).resolve().parents[1]
SEED = 0x164DE64
COUNT = 384
EDGE = (0,1,2,3,7,15,16,17,63,64,65,127,128,255,256,257,1023,1024,1025,
        4095,4096,4097,16383,16384,16385,32767,32768,65534,65535)
EXPECTED = frozenset(('link:square-table', 'link:radix4-zerozp'))
SHAPE = {
    'link:square-table': ((38,256,256,256), 0, 0, True),
    'link:radix4-zerozp': ((137,), 0, 6, False),
}


def corpus():
    rng = random.Random(SEED)
    return list(EDGE) + [rng.randrange(65536) for _ in range(COUNT-len(EDGE))]


def bench_isqrt16(modules, base, io, scratch, root=ROOT, zp=0x50):
    if set(modules) != EXPECTED:
        raise ValueError('ISQRT16 incomplete source-qualified variant catalog')
    inputs = corpus()
    digest = hashlib.sha256(b''.join(n.to_bytes(2,'little') for n in inputs)).hexdigest()
    if digest != CORPUS_SHA256:
        raise ValueError('ISQRT16 comparable operand corpus drifted')
    import math_builder, selective_linker as linker
    index = math_builder.operation_index(root)
    means, sha = {}, {}
    for ident, module in sorted(modules.items()):
        lens, zpn, temp, aligned = SHAPE[ident]
        if (tuple(length for _,length in module['segments']), module['zp'],
            module['scratch'], bool(module.get('isqrt16'))) != (lens,zpn,temp,aligned):
            raise ValueError('ISQRT16 source/placement contract drifted: '+ident)
        if module.get('requires_writable_code') or module.get('requires_reu'):
            raise ValueError('ISQRT16 unqualified hardware dependency')
        plan = math_builder.create_plan(index, ['ISQRT16'], objective='size',
            zp_budget=0, ram_budget=1100, pins={'ISQRT16':ident})
        with tempfile.TemporaryDirectory(prefix='isqrt16_speed_') as tmp:
            folder = Path(tmp)
            linked = linker.build(plan, folder, root=root, memory={
                'code_base':base, 'math_io':io, 'scratch_base':scratch,'zp_base':zp})
            op = linked['operations'][0]
            if op['variant'] != ident:
                raise ValueError('ISQRT16 source pin not retained')
            prg = (folder/'math_selective.prg').read_bytes()
            if prg[:2] != bytes((base&255,base>>8)):
                raise ValueError('ISQRT16 relocation contract failed')
            mem = bytearray(65536)
            mem[base:base+len(prg)-2] = prg[2:]
            code_original = bytes(mem[base:base+len(prg)-2])
            cpu = CPU(mem)
            entry = int(op['entry'][1:], 16)
            total = 0
            for i,n in enumerate(inputs):
                inp = n.to_bytes(2,'little')+b'\xa5\x5a'
                mem[io+16:io+20] = inp
                mem[io+8:io+12] = b'\x55\xaa\x66\xbb'
                cpu.d = 0; cpu.c = i & 1
                cpu.x = (13+i*17)&255; cpu.y = (19+i*31)&255
                sp=cpu.sp
                total += cpu.call(entry, 20000)
                if ((mem[io+8], mem[io+9], cpu.c) != (isqrt(n),0,0)
                    or mem[io+10:io+12] != b'\x66\xbb'
                    or mem[io+16:io+20] != inp
                    or cpu.sp!=sp):
                    raise ValueError(f'ISQRT16 full ABI failed: {ident}, input={n}')
            if bytes(mem[base:base+len(prg)-2]) != code_original:
                raise ValueError('ISQRT16 mutated executable/table memory')
            means[ident] = total/COUNT
            sha[ident] = hashlib.sha256((root/module['source']).read_bytes()).hexdigest()
    return {'basis':'cpu-model-isqrt16-full-public-z16-v1',
        'cases':COUNT,'corpus_sha256':digest,
        'cpu_model_only':True,'native_hardware_timing':False,
        'mean_cycles':means,'source_sha256':sha,
        'code_origin':f'${base:04X}','io_origin':f'${io:04X}',
        'scratch_origin':f'${scratch:04X}','zp_origin':f'${zp:02X}',
        'note':'Full Z16/C public ABI, input/SP/sentinel preservation, code and table immutable'}

CORPUS_SHA256 = '32570e8b82c82b425548d46aeac245ce7083a7f48973550d7e4e41720334e89c'
