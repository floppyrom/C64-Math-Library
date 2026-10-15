#!/usr/bin/env python3
"""Research: avoid copying 32-bit input words for ISQRT16-derived ISQRT32 seed."""
import re,sys,random,math,hashlib,json,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import load,wr,rd
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v5_hybrid_lowzp')

def build(p):
    txt=(ROOT/p/'standalone/isqrt_u32_u16.asm').read_text()
    names=re.findall(r'(?m)^; ---- executable island \$([0-9A-F]+) ----$',txt)
    chunks=re.split(r'(?m)^; ---- executable island \$[0-9A-F]+ ----\n',txt)[1:]
    assert len(chunks)==len(names),(names,len(chunks))
    src=dict(zip(names,chunks))
    seednames=[x for x in names if x not in ('5E2D','CB40') and int(x,16)<0xC960]
    assert len(seednames)==1,(p,seednames)
    seedname=seednames[0]
    seed=src[seedname]
    seed=seed.replace('* = $'+seedname,'* = $0C90')
    seed=seed.replace('$C011','$C013').replace('$C010','$C012')
    # Seed relative JMP symbolic labels assemble automatically.
    main=src['CB40']
    main=main.replace('* = $CB40','* = $0C00')
    start=main.index('    ldx $C008')
    # Drop original high-word -> low-word copy, $5B/$5C preserve, ISQRT16 call, restore,
    # replaced by a direct high-word seed that never overwrites input.
    label_start=main.index('LCB40:')
    main=main[:label_start]+ 'LCB40:\n    jsr L'+seedname+'\n' +main[start:]
    other_names=[t for t in names if t not in ('5E2D','CB40',seedname)]
    assert len(other_names)==1,(p,other_names)
    refine=other_names[0]
    main=main.replace('jsr L'+refine,'jsr $'+refine)
    # Drop original machine-address annotations: relocated source is not at those addresses.
    main=re.sub(r'\s+; @[0-9A-Fa-f]{4}.*$', '', main, flags=re.M)
    seed=re.sub(r'\s+; @[0-9A-Fa-f]{4}.*$', '', seed, flags=re.M)
    asm='!cpu 6510\n'+main+'\n'+seed
    code,labels,_=Assembler().assemble(asm)
    assert min(code)==0x0C00 and max(code)<0x0D00,(hex(min(code)),hex(max(code)),len(code))
    assert labels['LCB40']==0x0C00 and labels['L'+seedname]==0x0C90
    return asm,code

def test(p,limit):
    asm,code=build(p)
    (ROOT/'optional/issue144_isqrt32_highword_direct').mkdir(parents=True,exist_ok=True)
    (ROOT/'optional/issue144_isqrt32_highword_direct'/f'{p}.asm').write_text(asm)
    baseline,api=load(p);opt,_=load(p)
    assert api['MATH_ISQRT32']==0x5e30
    for k,v in code.items():
        assert opt.mem[k]==0,(p,hex(k),'RAM overlap')
        opt.mem[k]=v
    opt.mem[0x5e31:0x5e33]=bytes([0x00,0x0C])
    rng=random.Random(0x144153212)
    edges=[0,1,2,3,4,15,16,17,255,256,257,0xFFFF,0x10000,0x10001,0x7FFFFFFF,0x80000000,0xFFFFFFFE,0xFFFFFFFF]
    inputs=edges + [rng.getrandbits(32) for _ in range(limit)]
    cycles_old=[];cycles_new=[]
    for i,n in enumerate(inputs):
        for c in (baseline,opt):wr(c.mem,0xC010,n,4)
        ca=baseline.call(0x5e30,1000000)
        cb=opt.call(0x5e30,1000000)
        a=rd(baseline.mem,0xC008,2);b=rd(opt.mem,0xC008,2)
        assert (a,b)==(math.isqrt(n),)*2,(p,i,hex(n),a,b)
        assert (baseline.c,opt.c)==(0,0)
        assert rd(opt.mem,0xc010,4)==n
        cycles_old.append(ca);cycles_new.append(cb)
    diffs=[a-b for a,b in zip(cycles_old,cycles_new)]
    return {'profile':p,'sample':len(inputs),'old_mean':statistics.mean(cycles_old),'new_mean':statistics.mean(cycles_new),'gain_mean':statistics.mean(diffs),'gain_min':min(diffs),'gain_max':max(diffs),'code_bytes':len(code),'source_sha':hashlib.sha256(asm.encode()).hexdigest()}
if __name__=='__main__':
    all=[]
    for p in PROFILES:
        a=test(p,1024)
        print(a,flush=True);all.append(a)
    print('PASS',len(all)*1042)
