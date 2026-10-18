#!/usr/bin/env python3
"""Comparable public ABI 24/24 DIV+MOD CPU-model source performance.

384 identical input pairs, complete quotient/remainder/zero carry, stack,
public N/D bytes and sentinel protection. V2 donor is certified writable SMC
and must not be compared to register-only historical timing figures.
"""
from __future__ import annotations
import hashlib
import random
import tempfile
from pathlib import Path
from mini6502 import CPU

ROOT=Path(__file__).resolve().parents[1]
SEED=0x2424CC64
COUNT=384
EDGE_N=(0,1,2,3,127,128,255,256,65535,65536,0x7fffff,0x800000,0xffffff)
EDGE_D=(0,1,2,3,7,255,256,65535,65536,0xffffff)
CORPUS_SHA256='e9643acad59e0783d3e7e9c4f1e95cc302a16cb264b865813ddf7a514ca00590'
EXPECTED=frozenset(('link:portable-restoring','link:v2-repose-fast'))
RESOURCES={
    'link:portable-restoring':((190,),0,4,'unsigned-24by24-restoring'),
    'link:v2-repose-fast':((1244,217),3,0,'unsigned-24by24-v2-repose'),
}
DONORS={
    'link:portable-restoring':('routines/divide/u24_by_u24_restoring_selective.asm',),
    'link:v2-repose-fast':('tools/selective_udiv24_v2.py',
        'relocatable_source/v2_pareto_fast/udiv24_direct_repose.inc',
        'routines/divide/u24_v2_repose_selective.asm'),
}

def corpus():
    rng=random.Random(SEED)
    pairs=[(n,d) for n in EDGE_N for d in EDGE_D]
    while len(pairs)<COUNT:
        n=rng.getrandbits(24)
        d=rng.choice((*EDGE_D,rng.getrandbits(24),rng.getrandbits(24)))
        pairs.append((n,d))
    assert len(pairs)==COUNT
    return pairs


def benchmark(api,modules,base,io,scratch,root=ROOT,zp=0x50):
    if api not in ('MATH_UDIV24','MATH_UMOD24') or set(modules)!=EXPECTED:
        raise ValueError(api+': incomplete complete-public-call candidate set')
    pairs=corpus()
    digest=hashlib.sha256(b''.join(n.to_bytes(3,'little')+d.to_bytes(3,'little')
                                    for n,d in pairs)).hexdigest()
    if digest!=CORPUS_SHA256:
        raise ValueError('U24 corpus changed; rerun full qualification')
    import math_builder
    import selective_linker as linker
    index=math_builder.operation_index(root)
    means={}; source_sha={}; donor_sha={}
    for ident,mod in sorted(modules.items()):
        segments,zp_count,scratch_count,producer=RESOURCES[ident]
        if (tuple(n for _,n in mod['segments']),mod['zp'],mod['scratch'])!=(segments,zp_count,scratch_count):
            raise ValueError(api+': resource contract changed '+ident)
        if not mod.get('multi_entry') or mod.get('share_producer')!=producer:
            raise ValueError(api+': shared public Q/R source identity changed '+ident)
        if ident=='link:v2-repose-fast':
            if not mod.get('requires_writable_code') or not mod.get('udiv24_v2'):
                raise ValueError(api+': historical V2 writable source contract changed')
        elif mod.get('requires_writable_code'):
            raise ValueError(api+': portable source requires unexpected code writes')
        for donor in DONORS[ident]:
            if not (root/donor).is_file():
                raise ValueError(api+': missing donor '+donor)
        operation=api.removeprefix('MATH_')
        plan=math_builder.create_plan(index,[operation],objective='size',
              ram_budget=1493,zp_budget=3,pins={operation:ident})
        with tempfile.TemporaryDirectory(prefix='bench_u24_') as td:
            path=Path(td)
            man=linker.build(plan,path,root=root,memory={
                'code_base':base,'math_io':io,'zp_base':zp,'scratch_base':scratch})
            chosen=man['operations'][0]
            if chosen['api']!=api or chosen['variant']!=ident:
                raise ValueError(api+': pinned public source changed')
            prg=(path/'math_selective.prg').read_bytes()
            if prg[:2]!=bytes((base&255,base>>8)):
                raise ValueError(api+': image origin changed')
            mem=bytearray(65536);mem[base:base+len(prg)-2]=prg[2:]
            cpu=CPU(mem);entry=int(chosen['entry'][1:],16)
            sp=cpu.sp;code_copy=bytes(mem[base:base+len(prg)-2]);total=0
            for i,(n,d) in enumerate(pairs):
                nb=n.to_bytes(3,'little')+b'\x6a'
                db=d.to_bytes(3,'little')+b'\xa9'
                cpu.mem[io+16:io+20]=nb;cpu.mem[io+20:io+24]=db
                cpu.mem[io+24:io+28]=b'\x55'*4;cpu.mem[io+28:io+32]=b'\x66'*4
                cpu.c=(n^d^i)&1;cpu.d=0
                total+=cpu.call(entry,70000)
                q=int.from_bytes(cpu.mem[io+24:io+27],'little')
                r=int.from_bytes(cpu.mem[io+28:io+31],'little')
                if ((q,r,cpu.c)!=(n//d if d else 0,n%d if d else 0,int(not d))
                    or cpu.mem[io+16:io+20]!=nb or cpu.mem[io+20:io+24]!=db
                    or cpu.mem[io+27]!=0x55 or cpu.mem[io+31]!=0x66 or cpu.sp!=sp):
                    raise ValueError(api+': public Q/R/C/input/SP failed '+repr((ident,i,n,d,q,r,cpu.c)))
            if ident=='link:portable-restoring' and bytes(mem[base:base+len(prg)-2])!=code_copy:
                raise ValueError(api+': compact source mutated executable')
            means[ident]=total/COUNT
            source_sha[ident]=hashlib.sha256((root/mod['source']).read_bytes()).hexdigest()
            donor_sha[ident]={path:hashlib.sha256((root/path).read_bytes()).hexdigest()
                              for path in DONORS[ident]}
    return {'basis':'cpu-model-unsigned-24by24-complete-public-q24-r24-v1-'+api.lower(),
        'cases':COUNT,'corpus_sha256':digest,'cpu_model_only':True,
        'native_hardware_timing':False,'code_origin':'$%04X'%base,
        'io_origin':'$%04X'%io,'scratch_origin':'$%04X'%scratch,
        'zp_origin':'$%02X'%zp,'mean_cycles':means,
        'source_sha256':source_sha,'donor_sha256':donor_sha,
        'note':'Fixed-input public Q24/R24/C and N/D/SP through RTS; V2 writable SMC; hardware timing not claimed'}

def bench_udiv24(modules,base,io,scratch,root=ROOT,zp=0x50):
    return benchmark('MATH_UDIV24',modules,base,io,scratch,root,zp)

def bench_umod24(modules,base,io,scratch,root=ROOT,zp=0x50):
    return benchmark('MATH_UMOD24',modules,base,io,scratch,root,zp)
