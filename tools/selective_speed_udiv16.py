#!/usr/bin/env python3
"""Comparable UDIV16 V1-biased versus canonical V2 zero-ZP full public Q/R/C.

CPU model only; native VICE correctness is qualified separately. This adapter
fails closed on donor/source drift and exact operation/resource contracts.
"""
from __future__ import annotations
import hashlib, random, tempfile
from pathlib import Path
from mini6502 import CPU
ROOT=Path(__file__).resolve().parents[1]
SEED=0x163232
COUNT=384
EDGE=(0,1,2,3,7,255,256,257,511,65535,32768)
EXPECTED=frozenset(('link:biased','link:v2-zerozp'))
RESOURCE={'link:biased':((323,),2,0),'link:v2-zerozp':((1481,),0,0)}
CANON='relocatable_source/v2_pareto_fast/udiv16_direct_fast.inc'
GEN='tools/generate_selective_udiv16_v2.py'

def corpus():
    r=random.Random(SEED)
    return [(n,d) for n in EDGE for d in EDGE]+[(r.randrange(65536),r.randrange(65536)) for _ in range(COUNT-len(EDGE)**2)]

def bench_udiv16(modules,base,io,scratch,root=ROOT,zp=0x50):
    if set(modules)!=EXPECTED: raise ValueError('UDIV16 candidate source set changed')
    pairs=corpus()
    digest=hashlib.sha256(b''.join(n.to_bytes(2,'little')+d.to_bytes(2,'little') for n,d in pairs)).hexdigest()
    if digest!=CORPUS_SHA256: raise ValueError('UDIV16 fixed input corpus changed')
    import math_builder,selective_linker as linker
    index=math_builder.operation_index(root)
    means={};source_sha={};deps={}
    canon=(root/CANON).read_text(encoding='utf-8')
    start='* = MATH_IO-$0800'
    if canon.count(start)!=1: raise ValueError('V2 canonical entry source changed')
    body=canon[canon.index(start):].replace(start,'* = KERNEL_CODE',1)
    for before,after in [('MATH_N','INPUT_NUM'),('MATH_D','INPUT_DIV'),('MATH_Q','OUTPUT_QUOT'),('MATH_R','OUTPUT_REM')]: body=body.replace(before,after)
    generated=(root/modules['link:v2-zerozp']['source']).read_text(encoding='utf-8')
    if not generated.endswith(body): raise ValueError('V2 zero-ZP generated source differs from donor')
    for ident,spec in sorted(modules.items()):
        shape=(tuple(n for _,n in spec['segments']),spec['zp'],spec['scratch'])
        if shape!=RESOURCE[ident]: raise ValueError('UDIV16 source resource contract drift '+ident)
        if spec.get('requires_reu') or spec.get('requires_writable_code'):
            raise ValueError('UDIV16 unexpected optional memory requirement')
        if ident=='link:v2-zerozp' and not spec.get('udiv16_v2'):
            raise ValueError('UDIV16 canonical source flag lost')
        if ident=='link:biased' and spec.get('udiv16_v2'):
            raise ValueError('UDIV16 biased donor identity changed')
        plan=math_builder.create_plan(index,['UDIV16'],objective='size',
            ram_budget=1800,zp_budget=2,pins={'UDIV16':ident})
        with tempfile.TemporaryDirectory(prefix='udiv16_cycle_') as td:
            folder=Path(td)
            man=linker.build(plan,folder,root=root,memory={'code_base':base,'math_io':io,
                'scratch_base':scratch,'zp_base':zp})
            op=man['operations'][0]
            if op['variant']!=ident:raise ValueError('UDIV16 pinned source mismatch')
            prg=(folder/'math_selective.prg').read_bytes()
            mem=bytearray(65536);mem[base:base+len(prg)-2]=prg[2:]
            initial=bytes(mem[base:base+len(prg)-2]);cpu=CPU(mem);sp=cpu.sp
            entry=int(op['entry'][1:],16);ticks=0
            for i,(n,d) in enumerate(pairs):
                nb=n.to_bytes(2,'little')+b'\xa5\x5a'
                db=d.to_bytes(2,'little')+b'\x5a\xa5'
                mem[io+16:io+20]=nb;mem[io+20:io+24]=db
                mem[io+24:io+28]=b'\x55'*4;mem[io+28:io+32]=b'\x66'*4
                cpu.d=0;cpu.c=(n^d^i)&1
                ticks+=cpu.call(entry,1000000)
                q=int.from_bytes(mem[io+24:io+26],'little')
                r=int.from_bytes(mem[io+28:io+30],'little')
                want=(n//d if d else 0,n%d if d else 0,int(not d))
                if ((q,r,cpu.c)!=want or mem[io+16:io+20]!=nb or mem[io+20:io+24]!=db
                    or mem[io+26:io+28]!=b'\x55'*2 or mem[io+30:io+32]!=b'\x66'*2 or cpu.sp!=sp):
                    raise ValueError(f'UDIV16 Q/R/C/input/sentinel/SP changed: {ident} {i} {n} {d}')
            if bytes(mem[base:base+len(prg)-2])!=initial:
                raise ValueError('UDIV16 kernel mutated its code')
            means[ident]=ticks/COUNT
            source_sha[ident]=hashlib.sha256((root/spec['source']).read_bytes()).hexdigest()
    for dep in (CANON,GEN):deps[dep]=hashlib.sha256((root/dep).read_bytes()).hexdigest()
    return {'basis':'cpu-model-udiv16-full-public-qr-v1', 'cases':COUNT,
        'corpus_sha256':digest,'cpu_model_only':True,'native_hardware_timing':False,
        'mean_cycles':means,'source_sha256':source_sha,'donor_sha256':deps,
        'code_origin':f'${base:04X}','io_origin':f'${io:04X}',
        'note':'Complete Q16/R16/C public ABI, immutable input/stack/code; 0-ZP donor is resource alternate, not claimed faster'}

CORPUS_SHA256 = 'e473a9872d63db4728f3d682dddf1d3642b1e157d0803f65672f36ff4d5be292'
if __name__=='__main__':print('UDIV16 CORPUS',CORPUS_SHA256)
