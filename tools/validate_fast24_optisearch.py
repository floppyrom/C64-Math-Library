#!/usr/bin/env python3
"""Optional FAST24 rerun with the user's independent OptiSearchV2 toolchain.

The normal library build and CI do not depend on OptiSearch. This audit accepts
an extracted 2026-10-06 archive and independently checks native result/cycles.
"""
from pathlib import Path
import argparse,hashlib,json,random,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU

def signed(x):
    return x-(1<<24) if x&0x800000 else x

def prepare(mem,s,x,y):
    for label,shift in (('x0',0),('x1',8),('x2',16)):
        mem[s[label]]=x>>shift&255
    mem[s['y0']]=y&255;mem[s['y1']]=y>>8&255

def output(mem,s,y,a,x):
    return sum(mem[s[f'r{i}']]<<(8*i) for i in range(3))|(y<<24)|(a<<32)|(x<<40)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--optisearch',type=Path,required=True)
    parser.add_argument('--baseline',type=Path,help='optional old FAST24 source for identical-input A/B timing')
    args=parser.parse_args()
    external=args.optisearch.resolve()
    for directory in (external/'mathlib_product/src',external/'src'):
        sys.path.insert(0,str(directory))
    from mathlibgen import core
    from optisearchv2.machines.c64 import C64Machine
    from optisearchv2.qualification.emulator import CPUState,EmulatorSnapshot,Reduced6502

    source=ROOT/'routines/multiply/mul_s24_s24_s48_fast24.asm'
    def assemble(path):
        asm=core._acme_mini().Assembler(path.read_text(),str(path));asm.assemble()
        mem=bytearray(65536)
        for address,value in asm.mem.items():mem[address]=value
        return mem,asm.syms,len(asm.mem)
    image,s,size=assemble(source)
    cpu=CPU(bytearray(image))
    baseline=None
    if args.baseline:
        old,old_symbols,_=assemble(args.baseline)
        baseline=(CPU(old),old_symbols)
    rng=random.Random(0xC0FFEE);cycles=[];old_cycles=[]
    for index in range(30000):
        x=rng.randrange(1<<24);y=rng.randrange(1<<24)
        engines=[(cpu,s,cycles)]+([(baseline[0],baseline[1],old_cycles)] if baseline else [])
        for engine,symbols,timings in engines:
            prepare(engine.mem,symbols,x,y);engine.y=y>>16;engine.c=index&1
            timings.append(engine.call(symbols['smul24_composed']))
            assert output(engine.mem,symbols,engine.y,engine.a,engine.x)==(signed(x)*signed(y))&((1<<48)-1)

    edges=(0,1,2,127,128,255,256,65535,65536,0x7fffff,0x800000,0x800001,0xffffff)
    pairs=[(x,y) for x in edges for y in edges]
    rng=random.Random(1234)
    pairs += [(rng.getrandbits(24),rng.getrandbits(24)) for _ in range(4096)]
    machine=C64Machine();machine.ram[:]=image
    machine.ram[0]=0x2f;machine.ram[1]=0x34
    independent_cpu=CPU(bytearray(image))
    for index,(x,y) in enumerate(pairs):
        prepare(machine.ram,s,x,y);prepare(independent_cpu.mem,s,x,y)
        machine.ram[0x1fc]=0xff;machine.ram[0x1fd]=0xfe
        other=Reduced6502(EmulatorSnapshot(machine,CPUState(pc=s['smul24_composed'],sp=0xfb,y=y>>16,p=0x20|(index&1))),record_trace=False)
        other.run(stop_pc=0xff00,max_instructions=20000)
        independent_cpu.y=y>>16;independent_cpu.c=index&1
        cy=independent_cpu.call(s['smul24_composed'])
        want=(signed(x)*signed(y))&((1<<48)-1)
        assert output(machine.ram,s,other.cpu.y,other.cpu.a,other.cpu.x)==want
        assert output(independent_cpu.mem,s,independent_cpu.y,independent_cpu.a,independent_cpu.x)==want
        assert cy==other.cpu.cycles,(x,y,cy,other.cpu.cycles)
        assert other.cpu.sp==0xfd

    report={'status':'PASS','source':str(source.relative_to(ROOT)),
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'uniform_cases':len(cycles),'uniform_seed':'0xC0FFEE',
        'mean_cycles':sum(cycles)/len(cycles),'min_cycles':min(cycles),'max_cycles':max(cycles),
        'code_bytes':s['code_end']-s['code_start'],'init_bytes':s['init_end']-s['init'],
        'zp_bytes':s['zp_end']-s['zp_start'],'occupied_total_bytes':size,
        'independent_oracle':'OptiSearchV2 Reduced6502 with C64 RAM banking; comparison to library mini6502 and Python signed product',
        'independent_cases':len(pairs),'independent_seed':1234,'independent_cycle_or_result_mismatches':0}
    if old_cycles:
        saved=[a-b for a,b in zip(old_cycles,cycles)]
        report.update(before_mean=sum(old_cycles)/len(old_cycles),min_saved=min(saved),max_saved=max(saved))
        assert min(saved)>=0
    path=ROOT/'validation/records/SMUL24_OPTISEARCH_ORACLE.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
