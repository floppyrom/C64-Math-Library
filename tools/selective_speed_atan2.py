#!/usr/bin/env python3
"""Matched complete-public-ABI ATAN2_8 speed measurements (CPU model only)."""
from __future__ import annotations
import hashlib
import random
import tempfile
from pathlib import Path
from mini6502 import CPU

ROOT=Path(__file__).resolve().parents[1]
SEED=0xA7A22027
COUNT=384
EXPECTED=frozenset(('link:compact','link:sum-fast'))
RESOURCES={
    'link:compact': ((94,256,256),0,0,'compact'),
    'link:sum-fast': ((85,256,256,256,256),0,0,'sum-fast'),
}
CORPUS_SHA256='37033402d5f21c0be3cf81ae59222d02a52cdd8d06ca48d0e4a1b1476f94aaa3'
OUTPUT_SHA256='0b006a71a2955f0fa35628f3c746cb6ea8edc52f338728fe6fd5b4456a05e42a'

def corpus():
    r=random.Random(SEED)
    edges=(0,1,127,128,255)
    return [(x,y) for x in edges for y in edges]+[(r.randrange(256),r.randrange(256)) for _ in range(COUNT-25)]

def bench_atan2(modules,base,io,scratch,root=ROOT,zp=0x50):
    if set(modules)!=EXPECTED:
        raise ValueError('ATAN2_8 incomplete comparable source candidates')
    pairs=corpus()
    digest=hashlib.sha256(bytes(v for pair in pairs for v in pair)).hexdigest()
    if digest!=CORPUS_SHA256:raise ValueError('ATAN2_8 corpus changed')
    import math_builder,selective_linker
    names=math_builder.operation_index(root)
    means={};sources={};table_provenance={};results={}
    for ident, spec in sorted(modules.items()):
        sections=tuple(n for _,n in spec['segments'])
        lengths,zp_count,scratch_count,which=RESOURCES[ident]
        if (sections,spec['zp'],spec['scratch'],spec.get('atan2'))!=(lengths,zp_count,scratch_count,which):
            raise ValueError('ATAN2_8 resource or source kind changed')
        if spec.get('requires_reu') or spec.get('requires_writable_code'):
            raise ValueError('ATAN2_8 unexpected SMC/REU requirement')
        with tempfile.TemporaryDirectory(prefix='atan2_speed_') as tmp:
            folder=Path(tmp)
            plan=math_builder.create_plan(names,['ATAN2_8'],objective='size',zp_budget=0,
                ram_budget=1500,pins={'ATAN2_8':ident})
            man=selective_linker.build(plan,folder,root=root,memory={'code_base':base,
                'math_io':io,'zp_base':zp,'scratch_base':scratch})
            op=man['operations'][0]
            if op['api']!='MATH_ATAN2_8' or op['variant']!=ident:
                raise ValueError('ATAN2_8 linker pin changed')
            prg=(folder/'math_selective.prg').read_bytes()
            if prg[:2]!=bytes((base&255,base>>8)):
                raise ValueError('ATAN2_8 PRG origin differs from selection')
            machine=bytearray(65536);machine[base:base+len(prg)-2]=prg[2:]
            program=bytes(machine[base:base+len(prg)-2]);cpu=CPU(machine)
            total=0;outs=bytearray();sp=cpu.sp
            entry=int(op['entry'][1:],16)
            for i,(x,y) in enumerate(pairs):
                machine[io]=x;machine[io+1]=0x5a
                machine[io+4]=y;machine[io+5]=0xa5
                machine[io+8]=0xee;machine[io+9]=0x3c
                cpu.d=0;cpu.c=(i+x+y)&1
                total+=cpu.call(entry,20000)
                value=machine[io+8];outs.append(value)
                if (cpu.a,cpu.c,cpu.sp,machine[io+9],machine[io],machine[io+1],
                    machine[io+4],machine[io+5])!=(value,0,sp,0x3c,x,0x5a,y,0xa5):
                    raise ValueError(f'ATAN2_8 public ABI failed for {ident}: {i} {x} {y}')
            if bytes(machine[base:base+len(prg)-2])!=program:
                raise ValueError('ATAN2_8 code or tables mutated')
            fingerprint=hashlib.sha256(outs).hexdigest()
            if fingerprint!=OUTPUT_SHA256:
                raise ValueError('ATAN2_8 published phase mapping changed')
            means[ident]=total/COUNT
            sources[ident]=hashlib.sha256((root/spec['source']).read_bytes()).hexdigest()
            table_provenance[ident]=hashlib.sha256((root/'routines/atan2/tables.py').read_bytes()).hexdigest()
            results[ident]=fingerprint
    return {'basis':'cpu-model-atan2-8-full-public-phase-v1',
        'cases':COUNT,'corpus_sha256':digest,'output_sha256':OUTPUT_SHA256,
        'cpu_model_only':True,'native_hardware_timing':False,
        'mean_cycles':means,'source_sha256':sources,'table_provenance_sha256':table_provenance,
        'code_origin':f'${base:04X}','io_origin':f'${io:04X}',
        'scratch_origin':f'${scratch:04X}','zp_origin':f'${zp:02X}',
        'note':'Fixed signed xy public phase/A/C, preserved input and code, exact original tables'}
