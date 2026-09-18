#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import csv, json, hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU,REV,SIZE
REV[0xBF]=('lax','absy'); REV[0xAF]=('lax','abs')
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m']
PRG={p:ROOT/p/'resident'/f'math_{p}_game_math.prg' for p in PROFILES}
REU={'v3_reu_512k':ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu','v4_reu_16m':ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu'}
PUBCSV=ROOT/'docs/PUBLIC_API_COMPLETE.csv'
MATH_INIT_OLD=0x3280
NORMALIZE_ENTRY_OLD=0x5e39
NORMALIZE_END_OLD={
 'v1_balanced':0x5fc0,
 'v2_pareto_fast':0x5fb7,
 'v3_reu_512k':0x5f92,
 'v4_reu_16m':0x5f92,
}
NORMALIZE_NATIVE_REL={
 p:f'../../{p}/resident/vector/native/vec2_normalize_q8_8.asm'
 for p in PROFILES
}
# Source-backed immediate address fragments in the active reference images.
IMM_ADDR={
 'v1_balanced':{0x3000:0x8000,0x3004:0x8200,0x3020:0x8400,0x3026:0x8800,0x302C:0x8600,0x3032:0x8A00,0x30B0:0x9000,0x30B8:0x8E00,0x3280:0x9000,0x3288:0x8E00,0x4900:0x8400,0x4908:0x8800,0x4910:0x8600,0x4918:0x8A00,0x2000:0x8000,0x2004:0x8200,0x2100:0x8000,0x2104:0x8200,0x2300:0x9000,0x2308:0x8E00,0x4871:0x8E00,0x4877:0x9000,0x4959:0x8E00,0x495F:0x9000},
 'v2_pareto_fast':{0x30D0:0x7400,0x30D8:0x7200,0x3280:0x7400,0x3288:0x7200,0x3290:0x6000,0x3298:0x6400,0x32A0:0x6200,0x32A8:0x6600,0x32B0:0x6800,0x32B4:0x6A00},
 'v3_reu_512k':{0x30D0:0x7400,0x30D8:0x7200,0x3280:0x7400,0x3288:0x7200,0x3290:0x6000,0x3298:0x6400,0x32A0:0x6200,0x32A8:0x6600,0x39A0:0xC020,0x39A5:0xC020},
 'v4_reu_16m':{0x30D0:0x7400,0x30D8:0x7200,0x3280:0x7400,0x3288:0x7200,0x3290:0x6000,0x3298:0x6400,0x32A0:0x6200,0x32A8:0x6600,0x39A0:0xC020,0x39A5:0xC020},
}
IMM_LOW_PCS={0x39A0}
# Source-address regions. GAME_API is intentionally independently configurable.
REGIONS=[
 ('REG_LOW',0x1000,0x2fff),
 ('REG_API',0x3000,0x3fff),
 ('REG_KERNEL',0x4000,0x5dff),
 ('REG_GAME_API',0x5e00,0x5fff),
 ('REG_TABLE',0x6000,0x9bff),
 ('REG_GAME',0xc100,0xcc73),
]
REGION_DEFAULT={'REG_LOW':0x1000,'REG_API':0x3000,'REG_KERNEL':0x4000,'REG_GAME_API':0x5e00,'REG_TABLE':0x6000,'REG_GAME':0xc100}
LENGTHS={'REG_LOW':0x2000,'REG_API':0x1000,'REG_KERNEL':0x2000,'REG_GAME_API':0x200,'REG_TABLE':0x3c00,'REG_GAME':0xb74}

REU_BANK_SYMBOL_BY_DEFAULT={
 0x00:'REU_UMUL8_LO_BANK', 0x01:'REU_UMUL8_HI_BANK',
 0x02:'REU_UDIV8_Q_BANK',  0x03:'REU_UDIV8_R_BANK',
 0x06:'REU_RECIP_LO_BANK', 0x07:'REU_RECIP_HI_BANK',
 0x08:'REU_ATAN2_BANK',     0x09:'REU_ISQRT16_BANK',
}
REU_BANK_KEYS=('REU_UMUL8_LO_BANK','REU_UMUL8_HI_BANK','REU_UDIV8_Q_BANK','REU_UDIV8_R_BANK','REU_TURBO16_BANK','REU_TURBO32_BANK','REU_RECIP_LO_BANK','REU_RECIP_HI_BANK','REU_ATAN2_BANK','REU_ISQRT16_BANK','REU_QS16_BASE_BANK')
TURBO_PUBLIC_OLD=(0x3800,0x3840,0x3880,0x38c0,0x3900,0x3960)
TURBO_PUBLIC_NAMES=('MATH_REU_UMUL16_BEGIN','MATH_REU_UMUL16','MATH_REU_UMUL16_END','MATH_REU_UMUL32_BEGIN','MATH_REU_UMUL32','MATH_REU_UMUL32_END')

def hx(v,w=4):return f'${v:0{w}X}'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def public_entries():
 out=[]
 with PUBCSV.open() as f:
  for r in csv.DictReader(f):out.append((r['entry'],int(r['address'][1:],16)))
 return out

def load_reference(profile):
 b=PRG[profile].read_bytes();load=b[0]|b[1]<<8
 raw=bytearray(65536);raw[load:load+len(b)-2]=b[2:]
 reu=bytearray(REU[profile].read_bytes()) if profile in REU else None
 init=CPU(bytearray(raw),reu=reu);init.d=0;init.call(MATH_INIT_OLD,2_000_000)
 return raw,init.mem

def trace(profile,mem):
 todo=[a for _,a in public_entries()]+[MATH_INIT_OLD];seen=set();unknown=[]
 if profile in REU: todo += list(TURBO_PUBLIC_OLD)
 while todo:
  pc=todo.pop()&0xffff
  if pc in seen:continue
  oc=mem[pc]
  if oc not in REV:unknown.append((pc,oc));continue
  seen.add(pc);op,mode=REV[oc];sz=SIZE[mode];nxt=(pc+sz)&0xffff
  if op in ('rts','rti','brk'):continue
  if mode=='rel':
   d=mem[pc+1];d=d-256 if d>=128 else d;todo.extend((nxt,(nxt+d)&0xffff));continue
  if op=='jmp':
   if mode=='abs':todo.append(mem[pc+1]|mem[pc+2]<<8)
   else:unknown.append((pc,oc))
   continue
  if op=='jsr':todo.extend((mem[pc+1]|mem[pc+2]<<8,nxt));continue
  todo.append(nxt)
 if unknown:raise RuntimeError(f'{profile}: untraceable stable code: {unknown[:8]}')
 return seen

def region_expr(a:int)->str|None:
 for name,s,e in REGIONS:
  if s<=a<=e:
   base=REGION_DEFAULT[name]
   return name if a==base else f'{name}+{hx(a-base)}'
 return None

def zp_spec(profile):
 if profile=='v1_balanced':return [('ZP_MAIN',0x02,0x20)]
 return [('ZP_MAIN',0x02,0x6a),('ZP_SMUL',0x80,0xf3)]

def addr_expr(profile,a:int)->str:
 if a<=0xff:
  for name,s,e in zp_spec(profile):
   if s<=a<=e:return name if a==s else f'{name}+{hx(a-s,2)}'
  return hx(a,2)
 ex=region_expr(a)
 if ex:return ex
 if 0xc000<=a<=0xc01f:return 'MATH_IO' if a==0xc000 else f'MATH_IO+{hx(a-0xc000,2)}'
 if 0xc020<=a<=0xc023:return 'REU_SCRATCH' if a==0xc020 else f'REU_SCRATCH+{hx(a-0xc020,2)}'
 if profile=='v1_balanced' and 0xc040<=a<=0xc057:return 'V1_SCRATCH' if a==0xc040 else f'V1_SCRATCH+{hx(a-0xc040,2)}'
 return hx(a)

def origin_expr(a:int)->str:
 ex=region_expr(a)
 if ex is None:raise ValueError(f'no static source region for {hx(a)}')
 return ex

def turbo_zp_expr(profile,pc,a:int)->str|None:
 if profile not in REU or a>0xff:return None
 # Turbo32 stack-free 135-byte overlay: resident binder/summation and public
 # CALL wrapper all reference the swapped ZP image at reference $0A-$90.
 if ((0x1000<=pc<0x1174) or (0x3900<=pc<0x3950)) and 0x0a<=a<=0x90:
  off=a-0x0a;return 'TURBO32_ZP_BASE' if off==0 else f'TURBO32_ZP_BASE+{hx(off,2)}'
 if 0x3840<=pc<0x3880:
  mapping={0x54:0x16,0x62:0x24,0x72:0x34,0x40:0x02,0xae:0x70}
  if a in mapping:return 'TURBO16_ZP_BASE' if mapping[a]==0 else f'TURBO16_ZP_BASE+{hx(mapping[a],2)}'
 if 0x3900<=pc<0x3960:
  mapping={0x1b:0x11,0x29:0x1f,0x39:0x2f,0x49:0x3f,0x60:0x56,0x0d:0x03,0x15:0x0b,
           0x75:0x6b,0x76:0x6c,0x77:0x6d,0x72:0x68,0x73:0x69,0x74:0x6a}
  if a in mapping:return 'TURBO32_ZP_BASE' if mapping[a]==0 else f'TURBO32_ZP_BASE+{hx(mapping[a],2)}'
 return None

def operand_text(profile,pc,op,mode,raw,branch_prefix='L'):
 if mode=='imp':return ''
 if mode=='acc':return ''
 if mode=='imm':
  if profile in REU:
   if pc==0x3800:return ' #<TURBO16_ZP_BASE'
   if pc==0x3805:return ' #>TURBO16_ZP_BASE'
   if pc==0x3810:return ' #REU_TURBO16_BANK'
   if pc==0x38c0:return ' #<TURBO32_ZP_BASE'
   if pc==0x38c5:return ' #>TURBO32_ZP_BASE'
   if pc==0x38d0:return ' #REU_TURBO32_BANK'
  # REU bank selectors used by the stable API are assembly-time symbols.  Only
  # treat an immediate as a bank selector when it directly feeds $DF06; this
  # avoids confusing unrelated constants with bank numbers.
  if profile in REU and pc+4 < len(raw) and raw[pc+2]==0x8D and raw[pc+3]==0x06 and raw[pc+4]==0xDF:
   v=raw[pc+1]
   # VEC2_NORMALIZE_Q8_8 uses the upper half of the relocatable Turbo16
   # REU bank for its 32 KiB direct ratio-index table. Keep the selector
   # symbolic when regenerating canonical source so alternate/custom maps
   # remain relocatable rather than freezing the reference bank number.
   if op=='lda' and pc==0x5e39:
    return ' #REU_TURBO16_BANK'
   if op=='lda' and v in REU_BANK_SYMBOL_BY_DEFAULT:
    # V3 has no stable consumers for the V4-only banks, but harmless symbols
    # are still present in the config for a common schema.
    return f' #{REU_BANK_SYMBOL_BY_DEFAULT[v]}'
   if profile=='v4_reu_16m' and op=='ora' and v==0x10:
    return ' #REU_QS16_BASE_BANK'
  if pc in IMM_ADDR[profile]:
   target=IMM_ADDR[profile][pc];ex=addr_expr(profile,target);frag='<' if pc in IMM_LOW_PCS else '>'
   return f' #{frag}{ex}'
  return f' #{hx(raw[pc+1],2)}'
 if mode=='rel':
  d=raw[pc+1];d=d-256 if d>=128 else d;t=(pc+2+d)&0xffff
  return f' {branch_prefix}{t:04X}'
 if mode in ('zp','zpx','zpy','indx','indy'):
  ex=turbo_zp_expr(profile,pc,raw[pc+1]) or addr_expr(profile,raw[pc+1])
  if mode=='zp':return f' {ex}'
  if mode=='zpx':return f' {ex},x'
  if mode=='zpy':return f' {ex},y'
  if mode=='indx':return f' ({ex},x)'
  if mode=='indy':return f' ({ex}),y'
 if mode in ('abs','absx','absy','ind'):
  t=raw[pc+1]|raw[pc+2]<<8;ex=turbo_zp_expr(profile,pc,t) or addr_expr(profile,t)
  if mode=='abs':return f' {ex}'
  if mode=='absx':return f' {ex},x'
  if mode=='absy':return f' {ex},y'
  if mode=='ind':return f' ({ex})'
 raise ValueError((op,mode))

def emit_instruction(profile,pc,raw,branch_targets):
 oc=raw[pc];op,mode=REV[oc]
 label=(f'L{pc:04X}:\n' if pc in branch_targets else '')
 if op=='lax':
  if mode=='zp':
   ex=addr_expr(profile,raw[pc+1]); return label+f'    !byte $A7, {ex}    ; LAX zp\n'
  if mode in ('abs','absy'):
   t=raw[pc+1]|raw[pc+2]<<8; ex=addr_expr(profile,t); opc='$AF' if mode=='abs' else '$BF'; comment='LAX abs' if mode=='abs' else 'LAX abs,Y'
   return label+f'    !byte {opc}, <{ex}, >{ex}    ; {comment}\n'
  raise RuntimeError(f'{profile}: unsupported LAX mode {mode} at {hx(pc)}')
 if op=='anc':return label+f'    !byte $0B, {hx(raw[pc+1],2)}    ; ANC #imm\n'
 force=''
 if mode in ('zp','zpx','zpy','indx','indy') and turbo_zp_expr(profile,pc,raw[pc+1]) is not None: force='+1'
 return label+f'    {op}{force}{operand_text(profile,pc,op,mode,raw)}\n'

def emit_core_image(profile,tm):
 # Decode installed $80-$F3 core but emit it at the stored source-image address $CC00.
 starts=[];pc=0x80
 while pc<=0xf3:
  oc=tm[pc]
  if oc not in REV:raise RuntimeError(f'{profile}: bad core opcode at {hx(pc,2)}')
  starts.append(pc);pc+=SIZE[REV[oc][1]]
 if pc!=0xf4:raise RuntimeError(f'{profile}: core decode did not end at $F4: {hx(pc)}')
 btargets=set()
 for pc in starts:
  op,mode=REV[tm[pc]]
  if mode=='rel':
   d=tm[pc+1];d=d-256 if d>=128 else d;btargets.add((pc+2+d)&0xffff)
 lines=['; MATH_INIT-installed native SMUL16 executable-ZP image, assembled symbolically.']
 lines.append(f'* = {origin_expr(0xcc00)}')
 for pc in starts:
  srcpc=0xcc00+(pc-0x80);oc=tm[pc];op,mode=REV[oc]
  if pc in btargets:lines.append(f'ZC{pc:02X}:')
  if op=='lax': lines.append(f'    !byte $A7, {addr_expr(profile,tm[pc+1])}    ; LAX zp')
  elif op=='anc':lines.append(f'    !byte $0B, {hx(tm[pc+1],2)}    ; ANC #imm')
  elif mode=='rel':
   d=tm[pc+1];d=d-256 if d>=128 else d;t=(pc+2+d)&0xffff;lines.append(f'    {op} ZC{t:02X}')
  else:
   # Use source PC only for immediate semantic metadata; core has none in IMM_ADDR.
   lines.append(f'    {op}{operand_text(profile,srcpc,op,mode,tm,branch_prefix="ZC")}')
 return lines

def generate_source(profile,outpath:Path):
 raw,tm=load_reference(profile);seen=trace(profile,tm)
 b=PRG[profile].read_bytes();prg_load=b[0]|b[1]<<8;prg_end=prg_load+len(b)-3
 main_seen={pc for pc in seen if pc>=0x100}
 # Turbo32's 135-ZP overlay calls two ordinary-RAM helper blocks that are not
 # reachable while the normal ZP image is installed. Decode them explicitly so
 # relocation rewrites their ZP and REG_LOW references symbolically rather than
 # publishing them as opaque reference-map bytes.
 if profile in REU:
  for _s,_e in ((0x1000,0x1045),(0x1100,0x1174)):
   _pc=_s
   while _pc<_e:
    _oc=raw[_pc]
    if _oc not in REV: raise RuntimeError(f'{profile}: bad Turbo32 resident opcode at {hx(_pc)}: {hx(_oc,2)}')
    main_seen.add(_pc);_pc+=SIZE[REV[_oc][1]]
   if _pc!=_e: raise RuntimeError(f'{profile}: Turbo32 resident decode ended at {hx(_pc)}, expected {hx(_e)}')
 # Stable main code must decode from raw exactly. Init only installs the separate ZP core.
 for pc in main_seen:
  if raw[pc]!=tm[pc]:raise RuntimeError(f'{profile}: unexpected self-modified main opcode {hx(pc)}')
 btargets=set()
 for pc in main_seen:
  op,mode=REV[raw[pc]]
  if mode=='rel':
   d=raw[pc+1];d=d-256 if d>=128 else d;btargets.add((pc+2+d)&0xffff)
 lines=[
  '; GENERATED CANONICAL SOURCE. Builds the stable 46-entry API from symbolic assembly source.',
  '; The fixed FINAL PRG is provenance/reference only. This file is the relocatable build input.',
  '; Compatible with the included source assembler; syntax is intentionally ACME-style.',
  '!cpu 6510','!source "math_config.inc"',''
 ]
 # Public symbols for linker/API use.
 lines += ['; Public API symbols']
 for name,a in public_entries():lines.append(f'{name} = {addr_expr(profile,a)}')
 if profile in REU:
  for name,a in zip(TURBO_PUBLIC_NAMES,TURBO_PUBLIC_OLD): lines.append(f'{name} = {addr_expr(profile,a)}')
 lines += [f'MATH_INIT = {addr_expr(profile,MATH_INIT_OLD)}','MATH_X = MATH_IO','MATH_Y = MATH_IO+$04','MATH_Z = MATH_IO+$08','MATH_N = MATH_IO+$10','MATH_D = MATH_IO+$14','MATH_Q = MATH_IO+$18','MATH_R = MATH_IO+$1C','']
 # Emit every static region. Reachable code becomes symbolic instructions; other bytes remain data.
 # The SMUL16 source image is emitted separately as code, not raw data.
 code_bytes=set()
 for pc in main_seen:
  sz=SIZE[REV[raw[pc]][1]];code_bytes.update(range(pc,pc+sz))
 core_img=range(0xcc00,0xcc74) if profile!='v1_balanced' else range(0,0)
 core_set=set(core_img)
 for name,s,e in REGIONS:
  # Emit only bytes that are actually present in this profile's resident PRG.
  s=max(s,prg_load);e=min(e,prg_end)
  if s>e:continue
  # REG_KERNEL appears twice; section each old interval at its own symbolic offset.
  lines += ['',f'; Source interval {hx(s)}-{hx(e)}',f'* = {origin_expr(s)}']
  a=s;data=[];data_start=None
  def flush():
   nonlocal data,data_start
   if not data:return
   # emit 16-byte rows
   for i in range(0,len(data),16):lines.append('    !byte '+', '.join(hx(x,2) for x in data[i:i+16]))
   data=[];data_start=None
  while a<=e:
   if a==NORMALIZE_ENTRY_OLD:
    flush()
    lines += [
      '; Canonical standalone VEC2 normalization backend for this profile.',
      f'!source "{NORMALIZE_NATIVE_REL[profile]}"',
    ]
    a=NORMALIZE_END_OLD[profile]+1
    continue
   if a in core_set:
    flush()
    if a==0xcc00:lines.extend(emit_core_image(profile,tm))
    a=0xcc74;continue
   if a in main_seen:
    flush();lines.append(emit_instruction(profile,a,raw,btargets).rstrip('\n'));a+=SIZE[REV[raw[a]][1]];continue
   # If this is an operand byte of code, it should have been skipped by advancing from start.
   if a in code_bytes:raise RuntimeError(f'{profile}: stranded code byte {hx(a)}')
   data.append(raw[a]);a+=1
  flush()
 outpath.parent.mkdir(parents=True,exist_ok=True);outpath.write_text('\n'.join(lines)+'\n')
 return {'profile':profile,'source':str(outpath.relative_to(ROOT)),'reachable_instructions':len(seen),'source_sha256':sha(outpath)}

def config_values(profile,alternate=False):
 if not alternate:
  d=dict(REGION_DEFAULT);d.update(MATH_IO=0xc000,REU_SCRATCH=0xc020,V1_SCRATCH=0xc040,ZP_MAIN=0x02,ZP_SMUL=0x80,TURBO16_ZP_BASE=0x3e,TURBO32_ZP_BASE=0x0a)
  d.update(REU_UMUL8_LO_BANK=0,REU_UMUL8_HI_BANK=1,REU_UDIV8_Q_BANK=2,REU_UDIV8_R_BANK=3,REU_TURBO16_BANK=4,REU_TURBO32_BANK=5,
           REU_RECIP_LO_BANK=6,REU_RECIP_HI_BANK=7,REU_ATAN2_BANK=8,REU_ISQRT16_BANK=9,REU_QS16_BASE_BANK=0x10)
 else:
  d={'REG_LOW':0x9000,'REG_API':0xb000,'REG_KERNEL':0x2000,'REG_GAME_API':0x7c00,'REG_TABLE':0x4000,'REG_GAME':0x8000,'MATH_IO':0xc800,'REU_SCRATCH':0xc820,'V1_SCRATCH':0xc840,'ZP_MAIN':0x07,'ZP_SMUL':0x70,'TURBO16_ZP_BASE':0x40,'TURBO32_ZP_BASE':0x06}
  if profile=='v3_reu_512k':
   # Strong proof within 512 KiB: permute every operational bank, including
   # relocating the Turbo overlay banks from 4/5 to 0/1.
   d.update(REU_UMUL8_LO_BANK=2,REU_UMUL8_HI_BANK=3,REU_UDIV8_Q_BANK=4,REU_UDIV8_R_BANK=5,REU_TURBO16_BANK=0,REU_TURBO32_BANK=1,
            REU_RECIP_LO_BANK=6,REU_RECIP_HI_BANK=7,REU_ATAN2_BANK=8,REU_ISQRT16_BANK=9,REU_QS16_BASE_BANK=0x10)
  elif profile=='v4_reu_16m':
   # Move stable data well away from the default banks, relocate both Turbo
   # overlay banks, and move the 8-bank quarter-square region as a unit.
   d.update(REU_UMUL8_LO_BANK=0x20,REU_UMUL8_HI_BANK=0x21,REU_UDIV8_Q_BANK=0x22,REU_UDIV8_R_BANK=0x23,REU_TURBO16_BANK=0x28,REU_TURBO32_BANK=0x29,
            REU_RECIP_LO_BANK=0x24,REU_RECIP_HI_BANK=0x25,REU_ATAN2_BANK=0x26,REU_ISQRT16_BANK=0x27,REU_QS16_BASE_BANK=0x30)
  else:
   d.update(REU_UMUL8_LO_BANK=0,REU_UMUL8_HI_BANK=1,REU_UDIV8_Q_BANK=2,REU_UDIV8_R_BANK=3,REU_TURBO16_BANK=4,REU_TURBO32_BANK=5,
            REU_RECIP_LO_BANK=6,REU_RECIP_HI_BANK=7,REU_ATAN2_BANK=8,REU_ISQRT16_BANK=9,REU_QS16_BASE_BANK=0x10)
 return d

def write_config(profile,path,alternate=False):
 vals=config_values(profile,alternate);lines=['; Assembly-time memory/REU map. Edit values subject to docs/SOURCE_RELOCATION.md constraints.']
 for k in ('REG_LOW','REG_API','REG_KERNEL','REG_GAME_API','REG_TABLE','REG_GAME','MATH_IO','REU_SCRATCH','V1_SCRATCH','ZP_MAIN','ZP_SMUL','TURBO16_ZP_BASE','TURBO32_ZP_BASE'):
  lines.append(f'{k} = {hx(vals[k],2 if k.startswith("ZP_") else 4)}')
 lines.append('')
 lines.append('; Stable API REU bank assignments. V1/V2 ignore these values.')
 for k in REU_BANK_KEYS: lines.append(f'{k} = {hx(vals[k],2)}')
 path.write_text('\n'.join(lines)+'\n');return vals
