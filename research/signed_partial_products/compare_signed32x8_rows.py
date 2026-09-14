from pathlib import Path
import sys,random,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler,CPU,load_sparse
BIAS=202
F=[(k*k)//4-64*k+4160 for k in range(511)]
G=[(k*k)//4-63*k-(k//2)+4096 for k in range(511)]
UQ=[(k*k)//4+BIAS*(k&1) for k in range(511)]
UN=[((255-k)*(255-k))//4+BIAS*((255-k)&1) for k in range(511)]

def make(direct):
    table_lo='$3000' if direct else '$2000'; table_hi='$3200' if direct else '$2200'; neg_lo='$3400' if direct else '$2400'; neg_hi='$3600' if direct else '$2600'
    lines=['*=$1000','row:',' sta $38']
    if direct:
        lines += [' eor #$80',' sta f1',' sta f3',' eor #$ff',' sta f2',' sta f4']
    else:
        lines += [' sta f1',' sta f3',' eor #$ff',' sta f2',' sta f4']
    lines += [' lda #0',' sta $30',' sta $31',' sta $32',' sta $33',' sta $34']
    for j in range(4):
        lines += [f' ldx ${0x20+j:02x}',' sec','f1=*+1',f' lda {table_lo},x','f2=*+1',f' adc {neg_lo},x',' sta $35','f3=*+1',f' lda {table_hi},x','f4=*+1',f' adc {neg_hi},x',' sta $36']
        if direct:
            lines += [' lda #$ff',' adc #0',' sta $37']
        lines += [' clc',f' lda ${0x30+j:02x}',' adc $35',f' sta ${0x30+j:02x}',f' lda ${0x31+j:02x}',' adc $36',f' sta ${0x31+j:02x}']
        for k in range(j+2,5):
            lines += [f' lda ${0x30+k:02x}',(' adc $37' if direct else ' adc #0'),f' sta ${0x30+k:02x}']
    if not direct:
        lines += [' bit $38',' bpl done',' sec',' lda $31',' sbc $20',' sta $31',' lda $32',' sbc $21',' sta $32',' lda $33',' sbc $22',' sta $33',' lda $34',' sbc $23',' sta $34','done:']
    lines += [' rts']
    # use unique operand labels issue: repeated f1 labels not allowed; all products can share same scalar binding but each instruction has own operand byte.
    # replace duplicate labels with stage-specific and binder patch all.
    src='\n'.join(lines)+'\n'
    # Rebuild cleaner by replacing occurrence labels with unique names then binder stores all.
    # Parse stages manually from generated text.
    for name in ['f1','f2','f3','f4']:
        n=0
        while f'{name}=*+1' in src:
            src=src.replace(f'{name}=*+1',f'{name}_{n}=*+1',1); n+=1
    # binder currently stores undefined f1..; replace binder block with stores to all 4 stage operands for each polarity.
    if direct:
        bind=[' sta $38',' eor #$80']
    else:
        bind=[' sta $38']
    for i in range(4):bind += [f' sta f1_{i}',f' sta f3_{i}']
    bind += [' eor #$ff']
    for i in range(4):bind += [f' sta f2_{i}',f' sta f4_{i}']
    old=' sta $38\n'+(' eor #$80\n sta f1\n sta f3\n eor #$ff\n sta f2\n sta f4' if direct else ' sta f1\n sta f3\n eor #$ff\n sta f2\n sta f4')
    src=src.replace(old,'\n'.join(bind))
    return src

a=Assembler();mems={};labs={};sources={}
for direct in [False,True]:
    src=make(direct);sources[direct]=src;md,lab,_=a.assemble(src);base=load_sparse(md);labs[direct]=lab
    if direct:
        GR=list(reversed(G))
        for k,v in enumerate(F):base[0x3000+k]=v&255;base[0x3200+k]=(v>>8)&255
        for k,v in enumerate(G):base[0x3400+k]=255-(v&255);base[0x3600+k]=255-((v>>8)&255)
        # NOTE signed scalar bound, unsigned x index uses original G, as test_mixed8_regabi.
    else:
        for k,v in enumerate(UQ):base[0x2000+k]=v&255;base[0x2200+k]=(v>>8)&255
        for k,v in enumerate(UN):base[0x2400+k]=255-(v&255);base[0x2600+k]=255-((v>>8)&255)
    mems[direct]=base
(Path(__file__).resolve().parent/'sources/signed32x8_direct.a').write_text(sources[True]);(Path(__file__).resolve().parent/'sources/signed32x8_baseline.a').write_text(sources[False])
vals=[0,1,2,3,0xff,0x100,0x101,0xffff,0x10000,0xffffff,0x7fffffff,0x80000000,0xffffff00,0xffffffff]
rng=random.Random(0x163232);pairs=[]
for s in range(256):
 for x in vals:pairs.append((x,s))
for _ in range(100000):pairs.append((rng.getrandbits(32),rng.randrange(256)))
res={}
for direct in [False,True]:
 base=mems[direct];lab=labs[direct];tot=0;mn=99999;mx=0;err=0
 for x,sraw in pairs:
  ss=sraw if sraw<128 else sraw-256;c=CPU(bytearray(base));
  for j in range(4):c.mem[0x20+j]=(x>>(8*j))&255
  c.a=sraw;cy=c.call(lab['row'],5000);got=sum(c.mem[0x30+j]<<(8*j) for j in range(5));exp=(x*ss)&((1<<40)-1)
  if got!=exp:
   err+=1
   if err<4:print('ERR',direct,hex(x),sraw,hex(got),hex(exp))
  tot+=cy;mn=min(mn,cy);mx=max(mx,cy)
 res['direct' if direct else 'baseline']={'cases':len(pairs),'errors':err,'mean':tot/len(pairs),'min':mn,'max':mx,'code_bytes':max(Assembler().assemble(sources[direct])[0])-0x1000+1,'table_bytes':2044}
print(json.dumps(res,indent=2))
