#!/usr/bin/env python3
"""Verify independently liftable 68-byte NMOS 6510 RAM-only 24÷8 SMC source.

The caller must enforce N2>0, D1=D2=0, 0<D0<256 and own writable code RAM.
"""
from pathlib import Path
import argparse,hashlib,json,random,sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from mini6502 import Assembler,CPU
from validate_unsigned_division import wr,rd
SOURCE=R/'routines/standalone_lab/portable/div_u24_by_u8_selfmod.asm'
MAPS=(0x8000,0x830f)
N=0xc010;D=0xc014;Q=0xc018;REM=0xc01c
rng=random.Random(0x24680A1)
cases=[((rng.randrange(1,256)<<16)|rng.randrange(65536),d)
       for d in range(1,256) for _ in range(12)]
cases += [((hi<<16)|lo,d) for hi in (1,127,128,255)
          for lo in (0,1,0x7fff,0xffff) for d in (1,2,3,7,127,128,255)]
report={'status':'PASS','scope':'precondition-only portable writable-RAM selfmod',
        'core_bytes':68,'core_normal_zp':0,'stack_growth':0,
        'cases_per_map':len(cases),'full_calls':0,'maps':{},'failures':0}
for start in MAPS:
    text=SOURCE.read_text().replace('KERNEL_CODE = $8000','KERNEL_CODE = '+chr(36)+f'{start:04X}')
    image,labels,_=Assembler().assemble(text)
    assert len(image)==68 and sorted(image)==list(range(start,start+68))
    entry=labels['FAST_UDIV24_BY8_RAM_SMC']
    cpat=labels['CPAT']+1;spat=labels['SPAT']+1
    assert cpat in image and spat in image
    initial=bytes(image[a] for a in sorted(image))
    c=CPU(bytearray(65536));c.d=0
    for a,b in image.items():c.mem[a]=b
    cycles_list=[];before_code=dict(image)
    for n,d in cases:
        wr(c.mem,N,n,3);wr(c.mem,D,d,3)
        c.mem[0xc013]=0xa5;c.mem[0xc017]=0x5a;c.mem[0xc01f]=0xd7
        sp=c.sp;c.c=1;c.d=0
        cycles=c.call(entry,1_000_000)
        assert (rd(c.mem,Q,3),rd(c.mem,REM,3),c.c)==(n//d,n%d,0),(hex(start),n,d)
        assert rd(c.mem,N,3)==n and rd(c.mem,D,3)==d
        assert (c.mem[0xc013],c.mem[0xc017],c.mem[0xc01f])==(0xa5,0x5a,0xd7)
        assert c.sp==sp
        assert c.mem[cpat]==c.mem[spat]==d
        assert all(c.mem[a]==b for a,b in before_code.items() if a not in (cpat,spat))
        cycles_list.append(cycles)
    report['full_calls']+=len(cases)
    report['maps'][f'{start:04X}']={'cases':len(cases),'mean_cycles':sum(cycles_list)/len(cycles_list),
       'min_cycles':min(cycles_list),'max_cycles':max(cycles_list),
       'code_sha256_initial':hashlib.sha256(initial).hexdigest(),
       'patched_opcode_operands':[f'{cpat:04X}',f'{spat:04X}']}
    print('SMC PORTABLE',hex(start),'PASS',len(cases),flush=True)
assert report['full_calls']==len(cases)*len(MAPS)
print('ISSUE39 PORTABLE 24/8 SMC VERIFIED',report['full_calls'],'calls',flush=True)
parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path);args=parser.parse_args()
if args.out:args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
