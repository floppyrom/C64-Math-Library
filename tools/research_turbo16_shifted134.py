#!/usr/bin/env python3
from pathlib import Path
import random,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler,CPU

CAND=ROOT/'relocatable_source/turbo/turbo16_shifted134_candidate.asm'
PRG=ROOT/'v3_reu_512k/resident/math_v3_reu_512k_game_math.prg'
REU=ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu'
MATH_IO=0xC000; MATH_INIT=0x3280
T16_BEGIN=0x3800; T16_CALL=0x3840; T16_END=0x3880
BASE=0x3E; REG_TABLE=0x6000
cfg=f'''REG_TABLE = $6000
MATH_IO = $C000
TURBO16_ZP_BASE = $003E
'''
wrapper=r'''
* = $4000
T16X_PUBLIC_TEST:
    ldx MATH_IO+$05
    lda MATH_IO+$00
    sta+1 T16X_x0
    lda MATH_IO+$01
    sta+1 T16X_x1
    stx+1 T16X_y1
    ldy MATH_IO+$04
    jsr T16X_umult_ax1
    sta MATH_IO+$0A
    stx MATH_IO+$09
    sty MATH_IO+$0B
    lda+1 T16X_z0
    sta MATH_IO+$08
    clc
    rts
'''
mem,labels,const=Assembler().assemble(cfg+CAND.read_text()+wrapper)
size=labels['T16X_zp_end']-labels['T16X_zp_start']
print('candidate_zp_bytes',size)
for n in ['T16X_umult','T16X_umult_ax1','T16X_x0','T16X_x1','T16X_y1','T16X_z0','T16X_zp_end']:
    print(n,hex(labels.get(n,const.get(n))))

def load_prg(path):
    b=path.read_bytes(); ld=b[0]|b[1]<<8
    m=bytearray(65536);m[ld:ld+len(b)-2]=b[2:];return m

m=load_prg(PRG); c=CPU(m,reu=bytearray(REU.read_bytes())); c.d=0; c.call(MATH_INIT,2_000_000)

def wr16(a,v):
    c.mem[a]=v&255;c.mem[a+1]=(v>>8)&255
def rd32(a):
    return sum(c.mem[a+i]<<(8*i) for i in range(4))

edge=[0,1,2,3,0xff,0x100,0x101,0x7fff,0x8000,0xfffe,0xffff]
pairs=[(a,b) for a in edge for b in edge]
rng=random.Random(0x54313658)
pairs += [(rng.randrange(65536),rng.randrange(65536)) for _ in range(20000)]

# Measure the shipped Turbo16 public API on exactly the same corpus before
# installing the research candidate or changing any resident table bytes.
c.call(T16_BEGIN,2_000_000)
base_tot=0;base_mn=10**9;base_mx=0
for x,y in pairs:
    wr16(MATH_IO,x);wr16(MATH_IO+4,y)
    cy=c.call(T16_CALL,100000)
    got=rd32(MATH_IO+8)
    if got != x*y: raise AssertionError(('baseline',hex(x),hex(y),hex(got),hex(x*y)))
    base_tot+=cy;base_mn=min(base_mn,cy);base_mx=max(base_mx,cy)
c.call(T16_END,2_000_000)
base_mean=base_tot/len(pairs)
print('BASELINE',len(pairs),'public_mean',f'{base_mean:.6f}','min',base_mn,'max',base_mx)

for a,v in mem.items(): c.mem[a]=v

BIAS=202
# The resident library's four common multiply planes use complemented negative
# rows for ADC. shifted134 was qualified against the publication form with
# plain negative-square rows and SBC, so install all six exact candidate planes
# for this isolated A/B benchmark rather than accidentally mixing conventions.
for i in range(511):
    q=(i*i)//4 + BIAS*(i&1)
    j=255-i
    nq=(j*j)//4 + BIAS*(j&1)
    c.mem[REG_TABLE+0x1000+i]=q&255
    c.mem[REG_TABLE+0x1200+i]=(q>>8)&255
    c.mem[REG_TABLE+0x1400+i]=nq&255
    c.mem[REG_TABLE+0x1600+i]=(nq>>8)&255
    c.mem[REG_TABLE+0x0800+i]=((q+256)>>8)&255
    c.mem[REG_TABLE+0x0A00+i]=(nq+1)&255

tot=0;mn=10**9;mx=0
for x,y in pairs:
    wr16(MATH_IO,x);wr16(MATH_IO+4,y)
    cy=c.call(labels['T16X_PUBLIC_TEST'],100000)
    got=rd32(MATH_IO+8)
    if got != x*y: raise AssertionError((hex(x),hex(y),hex(got),hex(x*y)))
    tot+=cy;mn=min(mn,cy);mx=max(mx,cy)
cand_mean=tot/len(pairs)
print('PASS',len(pairs),'public_mean',f'{cand_mean:.6f}','min',mn,'max',mx,
      'delta_vs_baseline',f'{cand_mean-base_mean:.6f}')


# Control experiment: keep the current Turbo16 arithmetic/table convention,
# but make the private overlay public-output aware so the wrapper can tail-jump.
# This tests whether ABI traffic, rather than arithmetic, is the larger target.
base_src=(ROOT/'relocatable_source/turbo/turbo16_overlay.asm').read_text()
base_src=base_src.replace('        sta+1 z0\n','        sta MATH_IO+$08\n')
old_tail='''        clc
        txa
_z1_part2:
        adc #0
        tax
_z2_part1:
        lda #0
_z2_part2:
        adc #0
        bcs _final_carry
        rts
_final_carry:
        iny
        rts
'''
new_tail='''        clc
        txa
_z1_part2:
        adc #0
        tax
        stx MATH_IO+$09
_z2_part1:
        lda #0
_z2_part2:
        adc #0
        sta MATH_IO+$0A
        bcc _direct_no_carry
        iny
_direct_no_carry:
        sty MATH_IO+$0B
        clc
        rts
'''
if old_tail not in base_src: raise AssertionError('Turbo16 tail pattern changed')
base_src=base_src.replace(old_tail,new_tail).replace('\nz0:    !byte 0\n','\n')
direct_wrapper=r'''
* = $4100
T16D_PUBLIC_TEST:
    ldx MATH_IO+$05
    lda MATH_IO+$00
    sta+1 x0
    lda MATH_IO+$01
    sta+1 x1
    stx+1 y1
    ldy MATH_IO+$04
    jmp umult_ax1
'''
dmem,dlabels,dconst=Assembler().assemble(cfg+base_src+direct_wrapper)
dzp=[a for a in dmem if BASE <= a <= 0xff]
dsize=max(dzp)-min(dzp)+1
print('directout_zp_bytes',dsize)
print('directout_labels',
      'entry',hex(dlabels['umult_ax1']),
      'x0',hex(dlabels['x0']),
      'x1',hex(dlabels['x1']),
      'y1',hex(dlabels['y1']))
m2=load_prg(PRG); c2=CPU(m2,reu=bytearray(REU.read_bytes())); c2.d=0;c2.call(MATH_INIT,2_000_000)
for a,v in dmem.items(): c2.mem[a]=v
d_tot=0;d_mn=10**9;d_mx=0
for x,y in pairs:
    c2.mem[MATH_IO]=x&255;c2.mem[MATH_IO+1]=(x>>8)&255
    c2.mem[MATH_IO+4]=y&255;c2.mem[MATH_IO+5]=(y>>8)&255
    cy=c2.call(dlabels['T16D_PUBLIC_TEST'],100000)
    got=sum(c2.mem[MATH_IO+8+i]<<(8*i) for i in range(4))
    if got != x*y: raise AssertionError(('directout',hex(x),hex(y),hex(got),hex(x*y)))
    d_tot+=cy;d_mn=min(d_mn,cy);d_mx=max(d_mx,cy)
d_mean=d_tot/len(pairs)
print('DIRECTOUT',len(pairs),'public_mean',f'{d_mean:.6f}','min',d_mn,'max',d_mx,
      'delta_vs_baseline',f'{d_mean-base_mean:.6f}',
      'delta_vs_shifted134',f'{d_mean-cand_mean:.6f}')
