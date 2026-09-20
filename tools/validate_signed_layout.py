#!/usr/bin/env python3
"""Validate the all-native-signed executable ownership contract.

Native signed means a signed API owns its executable arithmetic path and never
enters the corresponding unsigned executable engine. Immutable lookup data may
be shared. This validator traces reachable 6502 instructions after MATH_INIT and
requires zero instruction-address overlap for every signed/unsigned API pair.
"""
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU, REV, SIZE

PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp']
PAIR_NAMES=[
 ('MATH_SMUL8','MATH_UMUL8'),('MATH_SMUL16','MATH_UMUL16'),
 ('MATH_SMUL24','MATH_UMUL24'),('MATH_SMUL32','MATH_UMUL32'),
 ('MATH_SMUL32_READY','MATH_UMUL32_READY'),
 ('MATH_SDIV8','MATH_UDIV8'),('MATH_SDIV16','MATH_UDIV16'),
 ('MATH_SDIV24','MATH_UDIV24'),('MATH_SDIV32_16','MATH_UDIV32_16'),
 ('MATH_SDIV32_32','MATH_UDIV32_32'),
 ('MATH_SMUL16_SHR8','MATH_UMUL16_SHR8'),
 ('MATH_SMUL32_SHR16','MATH_UMUL32_SHR16'),
 ('MATH_SDIV16_SHL8','MATH_UDIV16_SHL8'),
]
REU={
 'v3_reu_512k':ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu',
 'v4_reu_16m':ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu',
}
checks=[]
def ck(name,cond,detail=None):
    if not cond: raise AssertionError(f'{name}: {detail}')
    checks.append({'check':name,'status':'PASS','detail':detail})

def api(profile):
    out={}
    for line in (ROOT/profile/'resident/math_api.inc').read_text().splitlines():
        m=re.match(r'\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)',line)
        if m: out[m.group(1)]=int(m.group(2),16)
    return out

def initialized(profile):
    path=next((ROOT/profile/'resident').glob('math_*_game_math.prg'))
    b=path.read_bytes(); lo=b[0]|b[1]<<8
    mem=bytearray(65536); mem[lo:lo+len(b)-2]=b[2:]
    reu=bytearray(REU[profile].read_bytes()) if profile in REU else None
    c=CPU(mem,reu=reu); c.d=0
    vals=api(profile)
    c.call(vals['MATH_INIT'],2_000_000)
    return c.mem,vals

def trace(mem,start):
    todo=[start]; seen=set()
    while todo:
        pc=todo.pop()&0xffff
        if pc in seen: continue
        oc=mem[pc]
        if oc not in REV: raise RuntimeError(f'untraceable opcode ${oc:02X} at ${pc:04X}')
        seen.add(pc); op,mode=REV[oc]; nxt=(pc+SIZE[mode])&0xffff
        if op in ('rts','rti','brk'): continue
        if mode=='rel':
            d=mem[pc+1]; d=d-256 if d>=128 else d; target=(nxt+d)&0xffff
            if pc in (0x4124,0x41AC): todo.append(target)
            else: todo.extend((nxt,target))
        elif op=='jmp':
            if mode!='abs': raise RuntimeError(f'indirect JMP at ${pc:04X}')
            todo.append(mem[pc+1]|mem[pc+2]<<8)
        elif op=='jsr': todo.extend((mem[pc+1]|mem[pc+2]<<8,nxt))
        else: todo.append(nxt)
    return seen

profiles_out={}
for p in PROFILES:
    resident=ROOT/p/'resident'; s=resident/'signed'
    ck(f'{p}_signed_readme',(s/'README.md').exists())
    ck(f'{p}_signed_link_map',(s/'SIGNED_LINK_MAP.json').exists())
    ck(f'{p}_no_legacy_native_signed',not (resident/'native_signed').exists())
    ck(f'{p}_no_unsigned_derived_tree',not (s/'multiply/unsigned_derived').exists())
    lm=json.loads((s/'SIGNED_LINK_MAP.json').read_text())
    cls=lm.get('signed_multiply_classification',{})
    ck(f'{p}_four_mul_widths',set(cls)=={'8','16','24','32'},sorted(cls))
    for bits,rec in cls.items(): ck(f'{p}_smul{bits}_native_kind',rec.get('kind')=='native_signed_kernel',rec)
    for k,rec in lm.get('division',{}).items(): ck(f'{p}_sdiv{k}_native_kind',rec.get('kind')=='native_signed_kernel',rec)
    mem,vals=initialized(p); pairs=[]
    for sn,un in PAIR_NAMES:
        ck(f'{p}_{sn}_symbol',sn in vals)
        ck(f'{p}_{un}_symbol',un in vals)
        st=trace(mem,vals[sn]); ut=trace(mem,vals[un]); overlap=sorted(st&ut)
        ck(f'{p}_{sn}_zero_unsigned_exec_overlap',not overlap,
           {'signed_instructions':len(st),'unsigned_instructions':len(ut),'overlap':[f'${x:04X}' for x in overlap[:16]]})
        pairs.append({'signed':sn,'unsigned':un,'signed_instructions':len(st),'unsigned_instructions':len(ut),'overlap':0})
    profiles_out[p]={'pairs':pairs}

for p in ('v2_pareto_fast','v3_reu_512k','v4_reu_16m'):
    n=ROOT/p/'resident/signed/multiply/native'
    ck(f'{p}_smul16_source',(n/'smul16_practical_116zp.a').exists())
    ck(f'{p}_smul16_relocation',(n/'smul16_practical_116zp.relocation.json').exists())

for f in ('docs/SIGNED_IMPLEMENTATIONS.md','docs/SIGNED_IMPLEMENTATION_REFERENCE.md','docs/SIGNED_IMPLEMENTATION_SELECTION.csv','docs/SIGNED_IMPLEMENTATION_VALIDATION.md','docs/PERFORMANCE_SIGNED_IMPLEMENTATIONS.csv','tools/validate_signed_multiply.py','tools/validate_signed_division.py','tools/upgrade_native_signed.py'):
    ck('present_'+Path(f).name,(ROOT/f).exists(),f)

out={'status':'PASS','definition':'signed path owns executable arithmetic engine; immutable tables may be shared; corresponding unsigned executable instructions may not be entered','profiles':profiles_out,'checks':checks,'summary':{'profiles':5,'api_pairs_per_profile':len(PAIR_NAMES),'zero_overlap_comparisons':len(PROFILES)*len(PAIR_NAMES),'checks_passed':len(checks),'taxonomy':['native_signed_kernel']}}
p=ROOT/'validation/review/SIGNED_LAYOUT_VALIDATION.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2)+'\n')
print('SIGNED LAYOUT PASS',len(checks),'checks;',out['summary']['zero_overlap_comparisons'],'zero-overlap comparisons')
