#!/usr/bin/env python3
"""Comparable public DIST8_ACCURATE speed basis for two historical sources.

Identical deterministic signed-byte inputs and complete public output/ABI.
These are CPU-model cycles, NOT hardware wall time, and include all public
entry/return instructions. The original 512-byte major/minor lookup tables
are source-authenticated by the separate exhaustive qualification.
"""
from __future__ import annotations
import hashlib
import random
import tempfile
from pathlib import Path
from mini6502 import CPU
import selective_dist8_accurate as tables

ROOT = Path(__file__).resolve().parents[1]
SEED = 0xD1578
COUNT = 384
EDGE = (0, 1, 2, 7, 127, 128, 129, 255)
EXPECTED = frozenset(('link:v1-ram-tables', 'link:v2-zp-tables'))
RESOURCE = {'link:v1-ram-tables': ((66,), 0, 2),
            'link:v2-zp-tables': ((58,), 2, 0)}
DONOR = 'tools/selective_dist8_accurate.py'


def corpus():
    pairs = [(x,y) for x in EDGE for y in EDGE]
    rng = random.Random(SEED)
    while len(pairs) < COUNT:
        pairs.append((rng.randrange(256), rng.randrange(256)))
    return pairs


def bench_dist8_accurate(modules, base, io, scratch, root=ROOT, zp=0x50):
    if set(modules) != EXPECTED:
        raise ValueError('DIST8_ACCURATE source candidate set changed')
    pairs = corpus()
    digest = hashlib.sha256(bytes(v for pair in pairs for v in pair)).hexdigest()
    if digest != CORPUS_SHA256:
        raise ValueError('DIST8_ACCURATE deterministic corpus changed')
    import math_builder
    import selective_linker as linker
    idx = math_builder.operation_index(root)
    means = {}; sha = {}
    for ident,mod in sorted(modules.items()):
        if (tuple(n for _,n in mod['segments']),mod['zp'],mod['scratch']) != RESOURCE[ident]:
            raise ValueError('DIST8_ACCURATE resource contract changed '+ident)
        if not mod.get('dist8_accurate') or mod.get('requires_reu') or mod.get('requires_writable_code'):
            raise ValueError('DIST8_ACCURATE source contract changed '+ident)
        plan = math_builder.create_plan(idx, ['DIST8_ACCURATE'],
             objective='size', pins={'DIST8_ACCURATE':ident},
             ram_budget=1600, zp_budget=2)
        with tempfile.TemporaryDirectory(prefix='dist8_accurate_speed_') as temp:
            folder = Path(temp)
            man = linker.build(plan, folder, root=root, memory={
                'code_base':base, 'math_io':io, 'zp_base':zp,'scratch_base':scratch})
            entry = int(man['operations'][0]['entry'][1:],16)
            prg = (folder/'math_selective.prg').read_bytes()
            if prg[:2] != bytes((base&255,base>>8)):
                raise ValueError('DIST8_ACCURATE public origin changed')
            if man['resource_use']['shared_table_bytes']!=512:
                raise ValueError('DIST8_ACCURATE shared table resource changed')
            machine=bytearray(65536);machine[base:base+len(prg)-2]=prg[2:]
            table_base=int(man['shared_tables'][0]['start'][1:],16)
            if machine[table_base:table_base+512]!=tables.MAJOR_BYTES+tables.MINOR_BYTES:
                raise ValueError('DIST8_ACCURATE certified table bytes changed')
            original=bytes(machine[base:base+len(prg)-2]);cpu=CPU(machine)
            stack=cpu.sp;elapsed=0
            for x,y in pairs:
                machine[io]=x;machine[io+1]=0xa1
                machine[io+4]=y;machine[io+5]=0xb2
                machine[io+8]=0x47;machine[io+9]=0x58
                cpu.d=0;cpu.c=(x+y)&1
                elapsed+=cpu.call(entry,5000)
                ax=abs(x if x<128 else x-256)
                ay=abs(y if y<128 else y-256)
                value=(tables.MAJOR_BYTES[max(ax,ay)]+tables.MINOR_BYTES[min(ax,ay)])&255
                if ((machine[io+8],machine[io+9],cpu.c)!=(value,0x58,0)
                    or (machine[io],machine[io+1],machine[io+4],machine[io+5])!=(x,0xa1,y,0xb2)
                    or cpu.sp!=stack):
                    raise ValueError('DIST8_ACCURATE public ABI/carry/input failed '+repr((ident,x,y)))
            if bytes(machine[base:base+len(prg)-2])!=original:
                raise ValueError('DIST8_ACCURATE source code changed during calls')
            means[ident]=elapsed/COUNT
            sha[ident]=hashlib.sha256((root/mod['source']).read_bytes()).hexdigest()
    return {'basis':'cpu-model-dist8-accurate-complete-public-v1',
        'cases':COUNT,'corpus_sha256':digest,'cpu_model_only':True,
        'native_hardware_timing':False,'mean_cycles':means,
        'code_origin':'$%04X'%base,'io_origin':'$%04X'%io,
        'scratch_origin':'$%04X'%scratch,'zp_origin':'$%02X'%zp,
        'source_sha256':sha,'table_provenance_sha256':hashlib.sha256((root/DONOR).read_bytes()).hexdigest(),
        'note':'Identical signed-byte public distance inputs, R8/C, preserved inputs/output sentinel, full 512B certified tables'}

CORPUS_SHA256 = '990bd1cdd5658052c8d485df417d7da8d9ff8f683d34510030eecb3097820aff'

if __name__=='__main__':print('DIST8_ACCURATE corpus',CORPUS_SHA256)
