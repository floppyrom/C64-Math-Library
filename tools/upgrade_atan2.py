#!/usr/bin/env python3
"""Install and exhaustively certify the 2026-09-17 stock-C64 ATAN2 upgrade.

V1 uses a 512-byte / zero-ZP compact signed-log implementation.
V2/V3 use a 1280-byte / zero-ZP four-quadrant implementation.
V4 remains the exact REU lookup path.

The 256-byte signed-magnitude log page is generated once.  Nonzero magnitudes
use a deliberately compressed log quantizer; zero is a sentinel.  V1 uses one
first-quadrant table plus cheap quadrant repair.  V2/V3 spend three extra pages
so the final quadrant angle is returned directly.
"""
from __future__ import annotations
from pathlib import Path
import collections, csv, hashlib, json, math, re, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from mini6502 import Assembler, CPU

PROFILES = ('v1_balanced','v2_pareto_fast','v3_reu_512k')
PRG = {p: next((ROOT/p/'resident').glob('*game_math.prg')) for p in PROFILES}
PUBLIC_ATAN = 0x5E2A
PUBLIC_ISQRT16 = 0x5E2D
X0,Y0,Z0 = 0xC000,0xC004,0xC008

# Exhaustively selected quantizer family.  floor(11.63*log2(m)) gives an
# 81-code finite span; every finite difference class spans at most two rounded
# phase values, therefore one table byte can keep the public result within
# one 1/256-turn unit.  Offset 82 leaves y=0 indices outside every finite
# difference code, so horizontal axes travel through the normal lookup path.
LOG_SCALE = 11.63
LOG_OFFSET = 82

# Fast donor pages are chosen from page-aligned holes that remain free after the
# direct-signed SMUL8 upgrade. V5 later remaps donor $4700 to the V1-free
# REG_KERNEL+$1700 page ($5700 reference); $5500/$5F00 are shared.
LOG_PAGE = 0x9600
Q0_PAGE = 0x9700
Q1_PAGE = 0x5500
Q2_PAGE = 0x5F00
Q3_PAGE = 0x4700


def signed8(v:int)->int: return v if v < 128 else v-256

def exact_phase(x:int,y:int)->int:
    if x==0 and y==0: return 0
    return round((math.atan2(y,x)%(2*math.pi))*128/math.pi)&255

def phase_error(a:int,b:int)->int: return min((a-b)&255,(b-a)&255)

def load_prg(path:Path):
    b=path.read_bytes(); lo=b[0]|(b[1]<<8); hi=lo+len(b)-3
    mem=bytearray(65536); mem[lo:hi+1]=b[2:]
    return mem,lo,hi

def write_prg(mem:bytearray,lo:int,hi:int,path:Path):
    path.write_bytes(bytes((lo&255,lo>>8))+bytes(mem[lo:hi+1]))

def jmp_target(mem:bytearray,addr:int)->int:
    if mem[addr] != 0x4C: raise RuntimeError(f'expected JMP at ${addr:04X}')
    return mem[addr+1] | (mem[addr+2]<<8)


def build_tables():
    q=[0]+[math.floor(LOG_SCALE*math.log2(m)) for m in range(1,129)]
    if max(q[1:])-min(q[1:]) != 81: raise RuntimeError('unexpected log quantizer span')
    log=[0]*256
    for raw in range(256):
        m=abs(signed8(raw))
        log[raw]=0 if m==0 else LOG_OFFSET+q[m]

    groups=collections.defaultdict(list)
    for x in range(1,129):
        for y in range(1,129):
            idx=(q[x]-q[y])&255
            groups[idx].append(round(math.atan2(y,x)*128/math.pi))
    base=[0]*256
    max_span=0
    for idx,vals in groups.items():
        lo,hi=min(vals),max(vals); max_span=max(max_span,hi-lo)
        base[idx]=(lo+hi)//2
    if max_span > 2: raise RuntimeError(f'quantizer angle class span {max_span} > 2')

    # y=0 is nonnegative and reaches Q0/Q1.  Its log-difference indices occupy
    # $52-$A3, outside the finite difference ranges $00-$51/$AF-$FF.
    for m in range(1,129): base[LOG_OFFSET+q[m]]=0

    q0=list(base)
    q1=[(128-v)&255 for v in base]
    q2=[(128+v)&255 for v in base]
    q3=[(-v)&255 for v in base]
    # Make the y=0 semantics explicit in the two reachable pages.
    for m in range(1,129):
        idx=LOG_OFFSET+q[m]; q0[idx]=0; q1[idx]=128
    return bytes(log),bytes(base),bytes(q0),bytes(q1),bytes(q2),bytes(q3),q,max_span


def compact_source(org:int)->str:
    # Q2 uses EOR #$80: ATANTAB values are 0..64, so this is exact and two
    # cycles cheaper than CLC/ADC #$80.
    return f'''X0=$C000\nY0=$C004\nZ0=$C008\nLOGTAB=$9600\nATANTAB=$9700\n.org ${org:04X}\natan2:\n    ldx X0\n    bne x_nonzero\n    ldx Y0\n    beq zero\n    bmi x0_yneg\n    lda #$40\n    bne axis_store\nx0_yneg:\n    lda #$C0\n    bne axis_store\nzero:\n    lda #$00\naxis_store:\n    sta Z0\n    clc\n    rts\nx_nonzero:\n    sec\n    bmi xneg\n    lda LOGTAB,x\n    ldx Y0\n    bmi xpyn\n    sbc LOGTAB,x\n    tax\n    lda ATANTAB,x\n    sta Z0\n    clc\n    rts\nxpyn:\n    sbc LOGTAB,x\n    tax\n    lda ATANTAB,x\n    eor #$ff\n    clc\n    adc #$01\n    sta Z0\n    clc\n    rts\nxneg:\n    lda LOGTAB,x\n    ldx Y0\n    bmi xnyn\n    sbc LOGTAB,x\n    tax\n    lda ATANTAB,x\n    eor #$ff\n    clc\n    adc #$81\n    sta Z0\n    clc\n    rts\nxnyn:\n    sbc LOGTAB,x\n    tax\n    lda ATANTAB,x\n    eor #$80\n    sta Z0\n    clc\n    rts\n'''


def fast_source(org:int)->str:
    # SEC is hoisted before the X-sign branch.  LDA/LDX/branches preserve C, so
    # all four duplicated subtract/lookup paths share it with no cycle tax.
    return f'''X0=$C000\nY0=$C004\nZ0=$C008\nLOGTAB=$9600\nQ0=$9700\nQ1=$5500\nQ2=$5F00\nQ3=$4700\n.org ${org:04X}\natan2:\n    ldx X0\n    bne x_nonzero\n    ldx Y0\n    beq zero\n    bmi x0_yneg\n    lda #$40\n    bne axis_store\nx0_yneg:\n    lda #$C0\n    bne axis_store\nzero:\n    lda #$00\naxis_store:\n    sta Z0\n    clc\n    rts\nx_nonzero:\n    sec\n    bmi xneg\n    lda LOGTAB,x\n    ldx Y0\n    bmi xpyn\n    sbc LOGTAB,x\n    tax\n    lda Q0,x\n    sta Z0\n    clc\n    rts\nxpyn:\n    sbc LOGTAB,x\n    tax\n    lda Q3,x\n    sta Z0\n    clc\n    rts\nxneg:\n    lda LOGTAB,x\n    ldx Y0\n    bmi xnyn\n    sbc LOGTAB,x\n    tax\n    lda Q1,x\n    sta Z0\n    clc\n    rts\nxnyn:\n    sbc LOGTAB,x\n    tax\n    lda Q2,x\n    sta Z0\n    clc\n    rts\n'''


def patch_profile(profile:str,tables):
    log,base,q0,q1,q2,q3,_,_=tables
    path=PRG[profile]; mem,lo,hi=load_prg(path)
    atan=jmp_target(mem,PUBLIC_ATAN); isqrt=jmp_target(mem,PUBLIC_ISQRT16)
    src=compact_source(atan) if profile=='v1_balanced' else fast_source(atan)
    code,labels,const=Assembler().assemble(src)
    if min(code)!=atan or max(code)>=isqrt: raise RuntimeError(f'{profile}: ATAN2 body does not fit stable slot')
    for a,v in code.items(): mem[a]=v
    for a in range(max(code)+1,isqrt): mem[a]=0
    mem[LOG_PAGE:LOG_PAGE+256]=log
    if profile=='v1_balanced':
        mem[Q0_PAGE:Q0_PAGE+256]=base
    else:
        mem[Q0_PAGE:Q0_PAGE+256]=q0
        mem[Q1_PAGE:Q1_PAGE+256]=q1
        mem[Q2_PAGE:Q2_PAGE+256]=q2
        mem[Q3_PAGE:Q3_PAGE+256]=q3
    write_prg(mem,lo,hi,path)
    return {'atan_body':f'${atan:04X}-${max(code):04X}','isqrt16_body':f'${isqrt:04X}',
            'code_bytes':len(code),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def validate_profile(profile:str):
    mem,_,_=load_prg(PRG[profile]); cpu=CPU(mem); cpu.d=0
    total=0; mn=10**9; mx=0; failures=0; maxerr=0; ed=collections.Counter();cd=collections.Counter()
    for rx in range(256):
        sx=signed8(rx)
        for ry in range(256):
            sy=signed8(ry); cpu.mem[X0]=rx; cpu.mem[Y0]=ry
            cyc=cpu.call(PUBLIC_ATAN); got=cpu.mem[Z0]; exp=exact_phase(sx,sy); er=phase_error(got,exp)
            total+=cyc; mn=min(mn,cyc); mx=max(mx,cyc); cd[cyc]+=1; ed[er]+=1; maxerr=max(maxerr,er)
            if er>1: failures+=1
    return {'cases':65536,'mean_cycles':total/65536,'min_cycles':mn,'max_cycles':mx,
            'cycle_distribution':{str(k):v for k,v in sorted(cd.items())},
            'max_phase_error':maxerr,'error_distribution':{str(k):v for k,v in sorted(ed.items())},
            'failures_gt_1':failures,'status':'PASS' if failures==0 else 'FAIL'}


def update_perf(profile:str,r):
    path=ROOT/profile/'PUBLIC_PERFORMANCE_GAME_MATH.csv'
    rows=list(csv.DictReader(path.open())); fields=list(rows[0])
    found=False
    for row in rows:
        if row['routine']=='ATAN2_8':
            row['cases']=str(r['cases']); row['mean_cycles']=repr(r['mean_cycles']); row['min_cycles']=str(r['min_cycles']); row['max_cycles']=str(r['max_cycles']); found=True
    if not found: raise RuntimeError(f'{profile}: ATAN2 row missing')
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)


def main():
    tables=build_tables(); result={'status':'PASS','date':'2026-09-17','algorithm':{
        'log_scale':LOG_SCALE,'log_offset':LOG_OFFSET,'finite_log_span':max(tables[6][1:])-min(tables[6][1:]),
        'max_first_quadrant_class_span':tables[7],
        'compact_tables_bytes':512,'fast_tables_bytes':1280,'zp_bytes':0,
        'fast_extra_pages_reference':['$5500','$5F00','$4700'],
        'v5_q3_remap_note':'V5 maps donor $4700 to REG_KERNEL+$1700 ($5700 reference); Q1/Q2 remain at $5500/$5F00. These pages are free in the current direct-SMUL8 V1 base.'},'profiles':{}}
    for p in PROFILES:
        install=patch_profile(p,tables); val=validate_profile(p)
        if val['status']!='PASS': raise RuntimeError(f'{p}: ATAN2 exhaustive validation failed')
        update_perf(p,val); result['profiles'][p]={**install,**val,'tier':'compact_512B' if p=='v1_balanced' else 'fast_1280B'}
        print(p, result['profiles'][p]['tier'], f"{val['mean_cycles']:.6f}", val['min_cycles'], val['max_cycles'], install['code_bytes'],'B code')
    out=ROOT/'validation/ATAN2_UPGRADE_VALIDATION.json';out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS ->',out)

if __name__=='__main__': main()
