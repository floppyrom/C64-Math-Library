#!/usr/bin/env python3
"""Research candidate: split the constrained UDIV32/16 low-word tail into two
independent 8-bit source/quotient phases.

The shipped tail rotates both quotient bytes on every bit.  The two bytes are
independent once the high-word UDIV16 has produced R<D: process ln1 into lq1,
then ln0 into lq0.  This removes one ZP ROL from each of the 16 bit steps while
leaving the arithmetic decision tree unchanged.
"""
from pathlib import Path
import random,sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from validate_unsigned_division import load,wr,rd,edge,expected

P='v2_pareto_fast'
CAND=0xA800
DIV16=0x420C

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

def source():
    blocks=[]
    for i in range(8): blocks.append(bit_block(i,'$1B'))
    blocks.append("    rol $1B\n")
    for i in range(8,16): blocks.append(bit_block(i,'$1A'))
    return f"""
* = $A800
candidate:
    jsr $420C
    bcc nonzero
    jmp zero
nonzero:
    lda $18
    sta $1A
    lda $19
    sta $1B
    lda $17
{''.join(blocks)}
    rol $1A
    sta $17
    clc
    rts
zero:
    lda #0
    sta $1A
    sta $1B
    rts
"""

def cases():
    out=[(n,d) for n in edge(32) for d in edge(16)]
    r=random.Random(0x32160007)
    out += [(r.getrandbits(32),r.getrandbits(16)) for _ in range(50000)]
    out += [(r.getrandbits(32),0) for _ in range(256)]
    # Quotient and divisor-width boundaries, including the current slow region.
    for d in [1,2,3,7,15,16,31,127,255,256,257,511,1023,4095,65535]:
        for q in [0,1,2,3,7,15,255,256,257,65535,65536,0xFFFFFF]:
            for z in (-1,0,1):
                n=d*q+z
                if 0<=n<=0xffffffff: out.append((n,d))
    return list(dict.fromkeys(out))

def run(cpu,entry,vec):
    cyc=[]; errors=0
    for n,d in vec:
        wr(cpu.mem,0xC010,n,4);wr(cpu.mem,0xC014,d,2)
        before_n=bytes(cpu.mem[0xC010:0xC014]);before_d=bytes(cpu.mem[0xC014:0xC016])
        c=cpu.call(entry,4_000_000)
        eq,er,ec=expected(n,d,32,16)
        got=(rd(cpu.mem,0xC018,4),rd(cpu.mem,0xC01C,2),cpu.c)
        if got!=(eq,er,ec) or bytes(cpu.mem[0xC010:0xC014])!=before_n or bytes(cpu.mem[0xC014:0xC016])!=before_d:
            errors+=1
            if errors<5: print('ERROR',hex(n),hex(d),got,(eq,er,ec))
        cyc.append(c)
    return {'cases':len(vec),'errors':errors,'mean':sum(cyc)/len(cyc),'min':min(cyc),'max':max(cyc),'cycles':cyc}

def main():
    base,A=load(P)
    cand,A2=load(P)
    mem,lab,_=Assembler().assemble(source())
    for a,b in mem.items(): cand.mem[a]=b
    entry=A2['MATH_UDIV32_16']
    # Existing wrapper's JSR $4E00.
    assert cand.mem[entry+30:entry+33]==bytes((0x20,0x00,0x4e)),cand.mem[entry:entry+64]
    cand.mem[entry+31]=lab['candidate']&255;cand.mem[entry+32]=lab['candidate']>>8
    vec=cases()
    old=run(base,A['MATH_UDIV32_16'],vec)
    new=run(cand,entry,vec)
    assert old['errors']==0 and new['errors']==0
    delta=[a-b for a,b in zip(old['cycles'],new['cycles'])]
    out={
      'status':'PASS','candidate':'split-byte constrained tail','cases':len(vec),
      'old':{k:v for k,v in old.items() if k!='cycles'},
      'new':{k:v for k,v in new.items() if k!='cycles'},
      'saved_mean':sum(delta)/len(delta),'min_saved':min(delta),'max_saved':max(delta),
      'slower_cases':sum(x<0 for x in delta),'equal_cases':sum(x==0 for x in delta)
    }
    print(json.dumps(out,indent=2))
    (ROOT/'validation/research').mkdir(parents=True,exist_ok=True)
    (ROOT/'validation/research/UDIV32_16_SPLIT_TAIL.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
