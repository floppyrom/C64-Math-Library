#!/usr/bin/env python3
"""A/B current UDIV32/16 against split-byte in-place and direct-public variants."""
from pathlib import Path
import random,sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import load,wr,rd,edge,expected

def bit_block(i,q):
    return f"""
b{i}:
    rol {q}
    rol $16
    rol a
    bcs force{i}
    cmp $13
    bcc no{i}
    bne take{i}
    ldx $16
    cpx $12
    bcc no{i}
take{i}:
    tax
    lda $16
    sbc $12
    sta $16
    txa
    sbc $13
    bcs no{i}
force{i}:
    tax
    lda $16
    sbc $12
    sta $16
    txa
    sbc $13
    sec
no{i}:
"""

def body(direct=False):
    blocks=[]
    for i in range(8): blocks.append(bit_block(i,'$19'))
    blocks.append("    rol $19\n")
    for i in range(8,16): blocks.append(bit_block(i,'$18'))
    finish = """
    rol $18
""" + ("""
    sta $C01D
    lda $18
    sta $C018
    lda $19
    sta $C019
    lda $14
    sta $C01A
    lda $15
    sta $C01B
    lda $16
    sta $C01C
    clc
    rts
zero:
    lda #0
    sta $C018
    sta $C019
    sta $C01A
    sta $C01B
    sta $C01C
    sta $C01D
    sec
    rts
""" if direct else """
    sta $17
    clc
    rts
zero:
    lda #0
    sta $18
    sta $19
    rts
""")
    return f"""
* = $A800
candidate:
    jsr $420C
    bcc nonzero
    jmp zero
nonzero:
    lda $17
{''.join(blocks)}
{finish}
"""

def vectors():
    out=[(n,d) for n in edge(32) for d in edge(16)]
    r=random.Random(0x32160008)
    out += [(r.getrandbits(32),r.getrandbits(16)) for _ in range(100000)]
    out += [(r.getrandbits(32),0) for _ in range(256)]
    for d in [1,2,3,7,15,16,31,127,255,256,257,511,1023,4095,16383,32767,65535]:
        for q in [0,1,2,3,7,15,255,256,257,65535,65536,0xFFFFFF,0xffffffff]:
            for z in (-1,0,1):
                n=d*q+z
                if 0<=n<=0xffffffff: out.append((n,d))
    return list(dict.fromkeys(out))

def install(cpu,api,direct=False):
    mem,lab,_=Assembler().assemble(body(direct))
    for a,b in mem.items(): cpu.mem[a]=b
    e=api['MATH_UDIV32_16']
    assert cpu.mem[e+30:e+33]==bytes((0x20,0x00,0x4e))
    cpu.mem[e+31]=lab['candidate']&255;cpu.mem[e+32]=lab['candidate']>>8
    if direct:
        cpu.mem[e+30]=0x4c
    else:
        assert cpu.mem[e+33:e+40]==bytes((0xA5,0x1A,0x8D,0x18,0xC0,0xA5,0x1B))
        cpu.mem[e+34]=0x18
        cpu.mem[e+39]=0x19

def run(cpu,e,vec):
    cyc=[];err=0
    for n,d in vec:
        wr(cpu.mem,0xC010,n,4);wr(cpu.mem,0xC014,d,2)
        bn=bytes(cpu.mem[0xC010:0xC014]);bd=bytes(cpu.mem[0xC014:0xC016])
        cy=cpu.call(e,4_000_000); eq,er,ec=expected(n,d,32,16)
        got=(rd(cpu.mem,0xC018,4),rd(cpu.mem,0xC01C,2),cpu.c)
        if got!=(eq,er,ec) or bytes(cpu.mem[0xC010:0xC014])!=bn or bytes(cpu.mem[0xC014:0xC016])!=bd:
            err+=1
            if err<5: print('ERR',hex(n),hex(d),got,(eq,er,ec))
        cyc.append(cy)
    return cyc,err

def stats(c): return {'mean':sum(c)/len(c),'min':min(c),'max':max(c)}
def main():
    vec=vectors(); variants={}
    for name,direct in [('old',None),('split_inplace',False),('split_inplace_direct',True)]:
        cpu,A=load('v2_pareto_fast')
        if direct is not None: install(cpu,A,direct)
        c,e=run(cpu,A['MATH_UDIV32_16'],vec);assert e==0
        variants[name]=c
    old=variants['old'];out={'status':'PASS','cases':len(vec),'variants':{}}
    for name,c in variants.items():
        d=[a-b for a,b in zip(old,c)]
        out['variants'][name]={**stats(c),'saved_mean':sum(d)/len(d),'min_saved':min(d),'max_saved':max(d),'slower':sum(x<0 for x in d)}
    print(json.dumps(out,indent=2))
    (ROOT/'validation/research').mkdir(parents=True,exist_ok=True)
    (ROOT/'validation/research/UDIV32_16_SPLIT_TAIL_V2.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
