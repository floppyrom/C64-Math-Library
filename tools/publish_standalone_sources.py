#!/usr/bin/env python3
"""Publish one exact, readable ASM source mirror for every stable public API entry.

The generated profile/standalone/*.asm files are audit/pick-up views of the
actual executable graph shipped in each profile after MATH_INIT. They preserve
the legacy fixed ABI while exposing the canonical typed naming scheme documented
in docs/NAMING_STANDARD.md.

Canonical integrated/relocatable build sources remain under relocatable_source/
and the profile builders. These generated mirrors are intentionally exact: every
reachable instruction carries its resident address and bytes.
"""
from __future__ import annotations
from pathlib import Path
import csv, json, re, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU, REV, SIZE

PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp']
REU_SIZE={'v3_reu_512k':512*1024,'v4_reu_16m':16*1024*1024}
DATA_SYMBOLS={'MATH_X','MATH_Y','MATH_Z','MATH_N','MATH_D','MATH_Q','MATH_R'}
EXTRA_PREFIXES=('MATH_REU_','TURBO','REU_')

# Jackasser/CSDb-style binary naming: operation + A type/width + B type/width + result.
# Division names append remainder width when the public call returns remainder too.
CANONICAL={
'MATH_UMUL8':'mul_u8_u8_u16','MATH_UMUL16':'mul_u16_u16_u32','MATH_UMUL24':'mul_u24_u24_u48','MATH_UMUL32':'mul_u32_u32_u64','MATH_UMUL32_READY':'mul_u32_u32_u64_ready',
'MATH_SMUL8':'mul_s8_s8_s16','MATH_SMUL16':'mul_s16_s16_s32','MATH_SMUL24':'mul_s24_s24_s48','MATH_SMUL32':'mul_s32_s32_s64','MATH_SMUL32_READY':'mul_s32_s32_s64_ready',
'MATH_UDIV8':'div_u8_u8_u8_8','MATH_UDIV16':'div_u16_u16_u16_16','MATH_UDIV24':'div_u24_u24_u24_24','MATH_UDIV32_16':'div_u32_u16_u32_16',
'MATH_UMOD8':'mod_u8_u8_u8','MATH_UMOD16':'mod_u16_u16_u16','MATH_UMOD24':'mod_u24_u24_u24','MATH_UMOD32_16':'mod_u32_u16_u16',
'MATH_SDIV8':'div_s8_s8_s8_8','MATH_SDIV16':'div_s16_s16_s16_16','MATH_SDIV24':'div_s24_s24_s24_24','MATH_SDIV32_16':'div_s32_s16_s32_16',
'MATH_SMOD8':'mod_s8_s8_s8','MATH_SMOD16':'mod_s16_s16_s16','MATH_SMOD24':'mod_s24_s24_s24','MATH_SMOD32_16':'mod_s32_s16_s16',
'MATH_UDIV32_32':'div_u32_u32_u32_32','MATH_UMOD32_32':'mod_u32_u32_u32','MATH_SDIV32_32':'div_s32_s32_s32_32','MATH_SMOD32_32':'mod_s32_s32_s32',
'MATH_UMUL16_SHR8':'mul_u16_u16_u24_shr8','MATH_SMUL16_SHR8':'mul_s16_s16_s24_shr8','MATH_UMUL32_SHR16':'mul_u32_u32_u48_shr16','MATH_SMUL32_SHR16':'mul_s32_s32_s48_shr16',
'MATH_UDIV16_SHL8':'div_u16_u16_u24_16_shl8','MATH_SDIV16_SHL8':'div_s16_s16_s24_16_shl8',
'MATH_URECIP16_Q16':'recip_u16_u24_q16','MATH_SIN8':'sin_u8_s8','MATH_COS8':'cos_u8_s8','MATH_SINCOS8':'sincos_u8_s8_s8',
'MATH_ATAN2_8':'atan2_s8_s8_u8','MATH_ISQRT16':'isqrt_u16_u16','MATH_ISQRT32':'isqrt_u32_u16','MATH_DIST8_FAST':'dist_s8_s8_u8_fast','MATH_DIST8_ACCURATE':'dist_s8_s8_u8_accurate',
'MATH_VEC2_NORMALIZE_Q8_8':'normalize_s16_s16_s16_s16_q8_8_to_q1_15',
}
ALIAS_OF={
'MATH_UMOD16':'MATH_UDIV16','MATH_UMOD24':'MATH_UDIV24','MATH_UMOD32_16':'MATH_UDIV32_16',
'MATH_SMOD8':'MATH_SDIV8','MATH_SMOD16':'MATH_SDIV16','MATH_SMOD24':'MATH_SDIV24','MATH_SMOD32_16':'MATH_SDIV32_16',
'MATH_UMOD32_32':'MATH_UDIV32_32','MATH_SMOD32_32':'MATH_SDIV32_32',
}

PROFILE_EXTRAS={
 'v3_reu_512k':{
  'MATH_REU_UMUL16_BEGIN':'mul_u16_u16_u32_turbo_begin','MATH_REU_UMUL16':'mul_u16_u16_u32_turbo','MATH_REU_UMUL16_END':'mul_u16_u16_u32_turbo_end',
  'MATH_REU_UMUL32_BEGIN':'mul_u32_u32_u64_turbo_begin','MATH_REU_UMUL32':'mul_u32_u32_u64_turbo','MATH_REU_UMUL32_END':'mul_u32_u32_u64_turbo_end'},
 'v4_reu_16m':{
  'MATH_REU_UMUL16_BEGIN':'mul_u16_u16_u32_turbo_begin','MATH_REU_UMUL16':'mul_u16_u16_u32_turbo','MATH_REU_UMUL16_END':'mul_u16_u16_u32_turbo_end',
  'MATH_REU_UMUL32_BEGIN':'mul_u32_u32_u64_turbo_begin','MATH_REU_UMUL32':'mul_u32_u32_u64_turbo','MATH_REU_UMUL32_END':'mul_u32_u32_u64_turbo_end',
  'MATH_REU_QS16_BEGIN':'mul_u16_u16_u32_qs16_begin','MATH_REU_QS16':'mul_u16_u16_u32_qs16','MATH_REU_QS16_END':'mul_u16_u16_u32_qs16_end'}
}

def api(profile):
 out={}
 for line in (ROOT/profile/'resident/math_api.inc').read_text().splitlines():
  m=re.match(r'\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)',line)
  if m: out[m.group(1)]=int(m.group(2),16)
 return out

def initialized(profile):
 p=next((ROOT/profile/'resident').glob('math_*_game_math.prg'))
 b=p.read_bytes(); load=b[0]|b[1]<<8
 mem=bytearray(65536); mem[load:load+len(b)-2]=b[2:]
 reu_path={'v3_reu_512k':ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu','v4_reu_16m':ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu'}.get(profile)
 if reu_path and reu_path.exists(): r=bytearray(reu_path.read_bytes())
 elif profile in REU_SIZE: r=bytearray(REU_SIZE[profile])
 else: r=None
 vals=api(profile); c=CPU(mem,reu=r); c.d=0; c.call(vals['MATH_INIT'],2_000_000)
 return c.mem,vals,p

def trace(mem,start):
 todo=[start]; seen=set()
 while todo:
  pc=todo.pop()&0xffff
  if pc in seen: continue
  oc=mem[pc]
  if oc not in REV: raise RuntimeError(f'bad opcode ${oc:02X} at ${pc:04X}')
  seen.add(pc); op,mode=REV[oc]; nxt=(pc+SIZE[mode])&0xffff
  if op in ('rts','rti','brk'): continue
  if mode=='rel':
   d=mem[pc+1]; d=d-256 if d>=128 else d; target=(nxt+d)&0xffff
   # Known bounded alignment branches whose physical fallthrough is unrelated data.
   if pc in (0x4124,0x41AC): todo.append(target)
   else: todo.extend((nxt,target))
  elif op=='jmp':
   if mode!='abs': raise RuntimeError(f'indirect JMP at ${pc:04X}')
   todo.append(mem[pc+1]|mem[pc+2]<<8)
  elif op=='jsr': todo.extend((mem[pc+1]|mem[pc+2]<<8,nxt))
  else: todo.append(nxt)
 return seen

def operand(mem,pc,op,mode,code):
 if mode=='imp': return ''
 if mode=='acc': return ' a'
 if mode=='imm': return f' #${mem[pc+1]:02X}'
 if mode=='rel':
  d=mem[pc+1]; d=d-256 if d>=128 else d; return f' L{(pc+2+d)&0xffff:04X}'
 if mode in ('zp','zpx','zpy','indx','indy'):
  a=mem[pc+1]; base=f'${a:02X}'
  return {'zp':f' {base}','zpx':f' {base},x','zpy':f' {base},y','indx':f' ({base},x)','indy':f' ({base}),y'}[mode]
 a=mem[pc+1]|mem[pc+2]<<8
 target=f'L{a:04X}' if a in code and op in ('jmp','jsr') else f'${a:04X}'
 return {'abs':f' {target}','absx':f' {target},x','absy':f' {target},y','ind':f' ({target})'}[mode]

def render(profile,name,mem,vals,prg_name):
 code=trace(mem,vals[name]); pcs=sorted(code); targets=set()
 for pc in pcs:
  op,mode=REV[mem[pc]]
  if mode=='rel':
   d=mem[pc+1]; d=d-256 if d>=128 else d; targets.add((pc+2+d)&0xffff)
  if op in ('jmp','jsr') and mode=='abs':
   t=mem[pc+1]|mem[pc+2]<<8
   if t in code: targets.add(t)
 targets.add(vals[name]); canonical=CANONICAL.get(name,PROFILE_EXTRAS.get(profile,{}).get(name,name.lower()))
 rel=('relocatable_source/v1_balanced/math_relocatable.asm + tools/build_hybrid.py' if profile=='v5_hybrid_lowzp' else f'relocatable_source/{profile}/math_relocatable.asm')
 lines=[
  f'; {canonical} — exact executable source mirror for {profile}',
  f'; Legacy API: {name} at ${vals[name]:04X}',
  '; GENERATED by tools/publish_standalone_sources.py. Do not hand-edit.',
  f'; Shipped image: {profile}/resident/{prg_name}',
  f'; Canonical integrated/relocatable source: {rel}',
  '; This file contains every executable instruction statically reachable from the public entry after MATH_INIT.',
  '; Shared immutable lookup/data tables and REU payload data are intentionally not duplicated here.',
  '; The address/byte annotations make this a mechanically auditable source view of the shipped executable.',
  f'; Reachable instructions: {len(code)}.',
 ]
 if name in ALIAS_OF: lines.append(f'; NOTE: legacy alias entry; semantic producer is {ALIAS_OF[name]}.')
 lines += ['!cpu 6510','']
 prev=None
 for pc in pcs:
  op,mode=REV[mem[pc]]; sz=SIZE[mode]
  if prev!=pc: lines += [f'; ---- executable island ${pc:04X} ----',f'* = ${pc:04X}']
  if pc==vals[name]:
   lines.append(f'{canonical}:')
   lines.append(f'{name}:')
  elif pc in targets: lines.append(f'L{pc:04X}:')
  bs=' '.join(f'{mem[pc+i]:02X}' for i in range(sz))
  if op=='lax': text=f'    !byte $A7, ${mem[pc+1]:02X}    ; LAX zp'
  elif op=='anc': text=f'    !byte $0B, ${mem[pc+1]:02X}    ; ANC #imm'
  else: text=f'    {op}{operand(mem,pc,op,mode,code)}'
  lines.append(f'{text:<38} ; @{pc:04X} {bs}')
  prev=pc+sz
 lines.append('')
 return '\n'.join(lines),len(code)

def filename(name,profile=None):
 c=CANONICAL.get(name,PROFILE_EXTRAS.get(profile or '',{}).get(name,name.lower()))
 return f'{c}__{name.lower()}.asm' if name in ALIAS_OF else f'{c}.asm'

def readme(profile, rows):
 body=['# Standalone public routines','',
 f'This directory exposes every stable public routine shipped by **{profile}** as one readable `.asm` file.',
 'The files are generated exact executable source mirrors, not jump-only placeholders. Each mirror contains every instruction statically reachable from that public entry after `MATH_INIT`, with resident address and byte annotations.',
 '',
 'The historical `MATH_*` ABI remains supported. New code should prefer the typed canonical names documented in `docs/NAMING_STANDARD.md`. For multiplication the form is `mul_<A>_<B>_<result>`; division that returns a remainder uses `div_<A>_<B>_<quotient>_<remainder-bits>`.',
 '',
 '**Important:** immutable lookup tables and REU payload data are shared by the profile and are not duplicated into every mirror. The canonical integrated relocatable sources remain under `relocatable_source/`. These standalone files are designed for inspection, extraction, adaptation, and exact comparison with the shipped image.',
 '', '| Legacy API | Canonical name | File | Alias of | Reachable instructions |','|---|---|---|---|---:|']
 for r in rows:
  body.append(f"| `{r['legacy_api']}` | `{r['canonical_name']}` | `{r['file']}` | {('`'+r['alias_of']+'`') if r['alias_of'] else ''} | {r['reachable_instructions']} |")
 body += ['', 'The machine-readable version of this table is `MANIFEST.csv`.','']
 return '\n'.join(body)

def main():
 all_report={'status':'PASS','profiles':{},'canonical_names':CANONICAL,'profile_extras':PROFILE_EXTRAS}
 for p in PROFILES:
  names=dict(CANONICAL); names.update(PROFILE_EXTRAS.get(p,{})); expected=set(names)
  mem,vals,prg=initialized(p); missing=sorted(expected-set(vals))
  if missing: raise RuntimeError(f'{p}: missing API symbols {missing}')
  out=ROOT/p/'standalone'; out.mkdir(parents=True,exist_ok=True); rows=[]
  for name in names:
   text,n=render(p,name,mem,vals,prg.name); fn=filename(name,p); (out/fn).write_text(text)
   rows.append({'legacy_api':name,'canonical_name':names[name],'file':fn,'alias_of':ALIAS_OF.get(name,''),'entry_address':f'${vals[name]:04X}','reachable_instructions':n})
  with (out/'MANIFEST.csv').open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
  (out/'README.md').write_text(readme(p,rows))
  all_report['profiles'][p]={'callable_entries':len(rows),'files':len(rows),'aliases':sum(bool(r['alias_of']) for r in rows),'rows':rows}
 (ROOT/'validation/STANDALONE_SOURCE_AUDIT.json').write_text(json.dumps(all_report,indent=2)+'\n')
 print('PUBLISHED',sum(len(CANONICAL)+len(PROFILE_EXTRAS.get(p,{})) for p in PROFILES),'standalone public source mirrors')

if __name__=='__main__': main()
