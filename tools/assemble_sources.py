#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse,re,json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import Assembler
from source_relocation import PROFILES,hx,REGIONS,REGION_DEFAULT,PRG,REU,REU_BANK_KEYS
REQ=['REG_LOW','REG_API','REG_KERNEL','REG_GAME_API','REG_TABLE','REG_GAME','MATH_IO','REU_SCRATCH','V1_SCRATCH','ZP_MAIN','ZP_SMUL','TURBO16_ZP_BASE','TURBO32_ZP_BASE']+list(REU_BANK_KEYS)
def parse_config(path):
 vals={}
 for raw in Path(path).read_text().splitlines():
  s=raw.split(';',1)[0].strip()
  if not s:continue
  m=re.fullmatch(r'([A-Z][A-Z0-9_]*)\s*=\s*(\$[0-9A-Fa-f]+|0x[0-9A-Fa-f]+|\d+)',s)
  if not m:raise ValueError(f'unsupported config line: {raw}')
  v=m.group(2);vals[m.group(1)]=int(v[1:],16) if v.startswith('$') else int(v,0)
 miss=[x for x in REQ if x not in vals]
 if miss:raise ValueError(f'missing config symbols: {miss}')
 return vals

def ranges(profile,v):
 out=[]
 b=PRG[profile].read_bytes();load=b[0]|b[1]<<8;end=load+len(b)-3
 # Claim exactly the source-backed resident intervals present in this profile.
 # REG_GAME_API remains independently relocatable even though it occupies the
 # reference public game-API span at $5E00-$5E3B.
 counts={}
 for name,os,oe in REGIONS:
  cs=max(os,load);ce=min(oe,end)
  if cs>ce:continue
  ns=v[name]+(cs-REGION_DEFAULT[name]);ne=v[name]+(ce-REGION_DEFAULT[name])
  counts[name]=counts.get(name,0)+1
  label=name if counts[name]==1 else f'{name}_{counts[name]}'
  out.append((label,ns,ne,'main'))
 out.append(('MATH_IO',v['MATH_IO'],v['MATH_IO']+0x1f,'main'))
 if profile in ('v3_reu_512k','v4_reu_16m'):out.append(('REU_SCRATCH',v['REU_SCRATCH'],v['REU_SCRATCH']+3,'main'))
 if profile=='v1_balanced':out.append(('V1_SCRATCH',v['V1_SCRATCH'],v['V1_SCRATCH']+0x17,'main'))
 if profile=='v1_balanced':out.append(('ZP_MAIN',v['ZP_MAIN'],v['ZP_MAIN']+0x1e,'zp'))
 else:
  out.append(('ZP_MAIN',v['ZP_MAIN'],v['ZP_MAIN']+0x68,'zp'))
  out.append(('ZP_SMUL',v['ZP_SMUL'],v['ZP_SMUL']+0x73,'zp'))
 return out

def validate_config(profile,v):
 validate_reu_banks(profile,v)
 for n in ('REG_LOW','REG_API','REG_KERNEL','REG_TABLE','REG_GAME'):
  if v[n]&0xff:raise ValueError(f'{n} must be page aligned')
 rs=ranges(profile,v)
 for n,s,e,space in rs:
  lim=0xff if space=='zp' else 0xffff
  if not (0<=s<=e<=lim):raise ValueError(f'{n} out of {space} address space: {hx(s)}-{hx(e)}')
 for n,s,e,space in rs:
  if space=='zp' and s<=1:raise ValueError(f'{n} overlaps reserved $00-$01 6510 processor port')
 main=[x for x in rs if x[3]=='main'];zp=[x for x in rs if x[3]=='zp']
 for group in (main,zp):
  for i,a in enumerate(group):
   for b in group[i+1:]:
    if max(a[1],b[1])<=min(a[2],b[2]):raise ValueError(f'collision: {a[0]} {hx(a[1])}-{hx(a[2])} with {b[0]} {hx(b[1])}-{hx(b[2])}')
 for n,s,e,_ in main:
  if max(s,0xdf00)<=min(e,0xdfff):raise ValueError(f'{n} overlaps REU/C64 I/O page $DF00-$DFFF')
 if profile in ('v3_reu_512k','v4_reu_16m'):
  t16s=v['TURBO16_ZP_BASE'];t16e=t16s+112
  t32s=v['TURBO32_ZP_BASE'];t32e=t32s+134
  if not (2<=t16s<=t16e<=0xff):raise ValueError(f'TURBO16_ZP_BASE invalid: {hx(t16s,2)}-{hx(t16e,2)}')
  if not (2<=t32s<=t32e<=0xff):raise ValueError(f'TURBO32_ZP_BASE invalid: {hx(t32s,2)}-{hx(t32e,2)}')
  # Overlay ranges may overlap normal scratch and each other: BEGIN/END makes
  # them explicit mutually exclusive ownership modes.  $00-$01 remain forbidden.
 return rs

def validate_reu_banks(profile,v):
 if profile not in ('v3_reu_512k','v4_reu_16m'): return
 singles=['REU_UMUL8_LO_BANK','REU_UMUL8_HI_BANK','REU_UDIV8_Q_BANK','REU_UDIV8_R_BANK','REU_TURBO16_BANK','REU_TURBO32_BANK','REU_RECIP_LO_BANK','REU_RECIP_HI_BANK']
 if profile=='v4_reu_16m': singles += ['REU_ATAN2_BANK','REU_ISQRT16_BANK']
 for k in singles+['REU_QS16_BASE_BANK']:
  if not 0<=v[k]<=0xff: raise ValueError(f'{k} must be an 8-bit REU bank number')
 if len({v[k] for k in singles}) != len(singles): raise ValueError('REU single-bank assignments collide')
 if profile=='v3_reu_512k':
  if any(v[k]>7 for k in singles): raise ValueError('V3 is a 512 KiB image: all active banks must be 0..7')
 else:
  q=v['REU_QS16_BASE_BANK']
  if q & 7: raise ValueError('REU_QS16_BASE_BANK must be aligned to an 8-bank boundary')
  if q>0xf8: raise ValueError('REU_QS16_BASE_BANK eight-bank range exceeds 16 MiB REU')
  qset=set(range(q,q+8))
  for k in singles:
   if v[k] in qset: raise ValueError(f'{k} collides with QS16 bank range')

def _assemble_overlay(name,v):
 src=ROOT/'relocatable_source'/'turbo'/f'{name}_overlay.asm'; text=src.read_text()
 basekey='TURBO16_ZP_BASE' if name=='turbo16' else 'TURBO32_ZP_BASE'
 base=v[basekey]; refbase=0x3e if name=='turbo16' else 0x0a; length=113 if name=='turbo16' else 135
 def cfg_for(b):
  vals={'REG_LOW':v['REG_LOW'],'REG_TABLE':v['REG_TABLE'],'TURBO16_ZP_BASE':v['TURBO16_ZP_BASE'],'TURBO32_ZP_BASE':v['TURBO32_ZP_BASE']};vals[basekey]=b
  return '\n'.join(f'{k} = {hx(val,2 if k.endswith("ZP_BASE") else 4)}' for k,val in vals.items())+'\n'
 def exact(mem):
  return bool(mem) and min(mem)==base and max(mem)==base+length-1 and not any(a<base or a>=base+length for a in mem)
 # Normal path: the bundled assembler converges to the ACME layout directly.
 mem,labels,const=Assembler().assemble(cfg_for(base)+text)
 if not exact(mem):
  # At the absolute top of page zero (notably Turbo16 base $8F), a forward
  # local label can transiently look like $0100 and be widened to absolute
  # addressing. Seed local forward symbols from the validated reference-layout
  # offsets and retry; real ACME independently verifies the resulting bytes.
  _,rl,_=Assembler().assemble(cfg_for(refbase)+text)
  local={k:a for k,a in rl.items() if refbase<=a<refbase+length}
  seed='\n'.join(f'{k} = {hx(base+(a-refbase),4)}' for k,a in sorted(local.items()))+'\n'
  mem,labels,const=Assembler().assemble(cfg_for(base)+seed+text)
 if not exact(mem): raise ValueError(f'{name} overlay layout is not exactly {length} bytes at {hx(base,2)}')
 return bytes(mem.get(a,0) for a in range(base,base+length)),labels

NORMALIZE_RECIP = (254, 251, 247, 243, 239, 236, 232, 228, 224, 221, 218, 214, 211, 207, 204, 201, 198, 195, 191, 188, 185, 182, 179, 176, 173, 170, 168, 165, 162, 159, 157, 154, 152, 149, 147, 144, 142, 139, 138, 135, 133, 131, 128, 126, 124, 122, 120, 118, 115, 113, 111, 110, 107, 105, 102, 101, 100, 97, 96, 93, 92, 89, 88, 86, 85, 83, 80, 78, 77, 75, 73, 73, 70, 68, 68, 66, 64, 62, 60, 60, 58, 55, 55, 53, 51, 51, 48, 48, 45, 45, 43, 42, 40, 39, 37, 36, 36, 33, 32, 32, 29, 28, 28, 26, 24, 23, 23, 21, 20, 18, 17, 16, 16, 14, 13, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2, 0, 0, 0)

def build_reu_image(profile,v,outpath):
 if profile not in REU:return None
 src=REU[profile].read_bytes();bank=0x10000;snap=bytes(src);img=bytearray(src)
 roles=[('REU_UMUL8_LO_BANK',0),('REU_UMUL8_HI_BANK',1),('REU_UDIV8_Q_BANK',2),('REU_UDIV8_R_BANK',3),('REU_RECIP_LO_BANK',6),('REU_RECIP_HI_BANK',7)]
 if profile=='v4_reu_16m':roles += [('REU_ATAN2_BANK',8),('REU_ISQRT16_BANK',9)]
 turbo16,_=_assemble_overlay('turbo16',v);turbo32,_=_assemble_overlay('turbo32',v)
 # Clear every operational source/target bank before repopulating from the
 # immutable reference snapshot. This makes alternate-bank validation strong.
 clear={old for _,old in roles}|{4,5}|{v[k] for k,_ in roles}|{v['REU_TURBO16_BANK'],v['REU_TURBO32_BANK']}
 if profile=='v4_reu_16m':
  clear |= set(range(0x10,0x18))|set(range(v['REU_QS16_BASE_BANK'],v['REU_QS16_BASE_BANK']+8))
 for bno in clear: img[bno*bank:(bno+1)*bank]=b'\x00'*bank
 for k,old in roles:
  new=v[k];img[new*bank:(new+1)*bank]=snap[old*bank:(old+1)*bank]
 if profile=='v4_reu_16m':
  q=v['REU_QS16_BASE_BANK']
  for i,old in enumerate(range(0x10,0x18)):img[(q+i)*bank:(q+i+1)*bank]=snap[old*bank:(old+1)*bank]
 img[v['REU_TURBO16_BANK']*bank:v['REU_TURBO16_BANK']*bank+len(turbo16)]=turbo16
 # VEC2 normalize direct-ratio index table.  The Turbo16 overlay occupies
 # only the low bytes of its bank; the normalizer owns $8000-$FFFF.
 # Address = (normalized_major << 8) | normalized_minor.
 if len(turbo16) >= 0x8000: raise ValueError('Turbo16 overlay collides with normalize ratio table')
 nb=v['REU_TURBO16_BANK']*bank
 for major in range(0x80,0x100):
  k=NORMALIZE_RECIP[major-0x80]
  row=nb+(major<<8)
  for minor in range(0x100):
   img[row+minor]=(minor+((minor*k)>>8)+1)&0xff
 img[v['REU_TURBO32_BANK']*bank:v['REU_TURBO32_BANK']*bank+len(turbo32)]=turbo32
 # Metadata lives in the unused final page of the logical Turbo32 bank so it
 # can move without consuming a ninth bank in V3.
 img[v['REU_TURBO32_BANK']*bank+0xff00:v['REU_TURBO32_BANK']*bank+0x10000]=snap[5*bank+0xff00:6*bank]
 outpath=Path(outpath);outpath.parent.mkdir(parents=True,exist_ok=True);outpath.write_bytes(img)
 return {'file':outpath.name,'sha256':hashlib.sha256(img).hexdigest(),'bytes':len(img),
         'turbo16_bank':hx(v['REU_TURBO16_BANK'],2),'turbo32_bank':hx(v['REU_TURBO32_BANK'],2),
         'turbo16_zp':f'{hx(v["TURBO16_ZP_BASE"],2)}-{hx(v["TURBO16_ZP_BASE"]+112,2)}',
         'turbo32_zp':f'{hx(v["TURBO32_ZP_BASE"],2)}-{hx(v["TURBO32_ZP_BASE"]+134,2)}',
         'turbo16_sha256':hashlib.sha256(turbo16).hexdigest(),'turbo32_sha256':hashlib.sha256(turbo32).hexdigest(),
         'normalize_ratio_bank':hx(v['REU_TURBO16_BANK'],2),
         'normalize_ratio_range':'$8000-$FFFF',
         'normalize_ratio_sha256':hashlib.sha256(img[nb+0x8000:nb+0x10000]).hexdigest()}

_SOURCE_RE=re.compile(r'^\s*!source\s+"([^"]+)"\s*(?:;.*)?$',re.I)

def expand_source_file(path, preserve_config_include=False, _stack=()):
 path=Path(path).resolve()
 if path in _stack:
  chain=' -> '.join(str(x) for x in _stack+(path,))
  raise ValueError(f'recursive !source include: {chain}')
 out=[]
 for line in path.read_text().splitlines():
  st=line.strip()
  m=_SOURCE_RE.match(st)
  if not m:
   out.append(line);continue
  rel=m.group(1)
  target=(path.parent/rel).resolve()
  if target.name=='math_config.inc':
   if preserve_config_include:out.append(line)
   continue
  if not target.exists():raise FileNotFoundError(f'!source target not found from {path}: {rel}')
  out.append(f'; BEGIN !source "{rel}"')
  out.extend(expand_source_file(target,preserve_config_include,_stack+(path,)).splitlines())
  out.append(f'; END !source "{rel}"')
 return '\n'.join(out)+'\n'

def preprocess(src,config):
 cfg=Path(config).read_text().rstrip()+'\n'
 expanded=expand_source_file(src,preserve_config_include=False)
 body=[]
 for line in expanded.splitlines():
  st=line.strip().lower()
  if st.startswith('!cpu'):continue
  body.append(line)
 return cfg+'\n'.join(body)+'\n'

def source_dependencies(path,_seen=None):
 path=Path(path).resolve();seen=set() if _seen is None else _seen;out=[]
 for line in path.read_text().splitlines():
  m=_SOURCE_RE.match(line.strip())
  if not m:continue
  target=(path.parent/m.group(1)).resolve()
  if target.name=='math_config.inc' or target in seen:continue
  if not target.exists():raise FileNotFoundError(f'!source target not found from {path}: {m.group(1)}')
  seen.add(target);out.append(target);out.extend(source_dependencies(target,seen))
 return out

def write_prg(mem,path):
 lo=min(mem);hi=max(mem);b=bytes((lo&255,lo>>8))+bytes(mem.get(a,0) for a in range(lo,hi+1));Path(path).write_bytes(b);return lo,hi

def build(profile,config,outdir):
 vals=parse_config(config);claims=validate_config(profile,vals)
 src=ROOT/'relocatable_source'/profile/'math_relocatable.asm';text=preprocess(src,config)
 mem,labels,const=Assembler().assemble(text)
 outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
 prg=outdir/f'math_{profile}_source_built.prg';lo,hi=write_prg(mem,prg)
 reu_info=build_reu_image(profile,vals,outdir/f'c64_math_{profile}_source_built.reu')
 # Public include is source-level expressions resolved to concrete selected map for callers.
 pubnames=[]
 import csv
 with (ROOT/'docs/PUBLIC_API_COMPLETE.csv').open() as f:
  for r in csv.DictReader(f):pubnames.append(r['entry'])
 inc=outdir/'math_api.inc';lines=['; GENERATED from source-level assembly configuration',f'MATH_INIT = {hx(labels.get("MATH_INIT",const.get("MATH_INIT")))}']
 for n in pubnames:
  val=const.get(n,labels.get(n));lines.append(f'{n:<24} = {hx(val)}')
 if profile in REU:
  for n in ('MATH_REU_UMUL16_BEGIN','MATH_REU_UMUL16','MATH_REU_UMUL16_END','MATH_REU_UMUL32_BEGIN','MATH_REU_UMUL32','MATH_REU_UMUL32_END'):
   val=const.get(n,labels.get(n));lines.append(f'{n:<24} = {hx(val)}')
  lines += [f'TURBO16_ZP_BASE          = {hx(vals["TURBO16_ZP_BASE"],2)}',f'TURBO32_ZP_BASE          = {hx(vals["TURBO32_ZP_BASE"],2)}',f'REU_TURBO16_BANK         = {hx(vals["REU_TURBO16_BANK"],2)}',f'REU_TURBO32_BANK         = {hx(vals["REU_TURBO32_BANK"],2)}']
 for n,off in [('MATH_X',0),('MATH_Y',4),('MATH_Z',8),('MATH_N',0x10),('MATH_D',0x14),('MATH_Q',0x18),('MATH_R',0x1c)]:lines.append(f'{n:<24} = {hx(vals["MATH_IO"]+off)}')
 inc.write_text('\n'.join(lines)+'\n')
 deps=source_dependencies(src)
 expanded_source=expand_source_file(src,preserve_config_include=False).encode()
 man={'profile':profile,'status':'BUILT_FROM_SOURCE','config':str(Path(config).relative_to(ROOT)) if Path(config).is_relative_to(ROOT) else str(config),'output_prg':prg.name,'output_load':hx(lo),'output_end':hx(hi),'output_sha256':hashlib.sha256(prg.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'expanded_source_sha256':hashlib.sha256(expanded_source).hexdigest(),'included_sources':{str(x.relative_to(ROOT)):hashlib.sha256(x.read_bytes()).hexdigest() for x in deps},'public_entries':{n:hx(const.get(n,labels.get(n))) for n in pubnames},'math_init':hx(const.get('MATH_INIT',labels.get('MATH_INIT'))),'public_io':f'{hx(vals["MATH_IO"])}-{hx(vals["MATH_IO"]+0x1f)}','reu_scratch':f'{hx(vals["REU_SCRATCH"])}-{hx(vals["REU_SCRATCH"]+3)}','reu_banks':{k:hx(vals[k],2) for k in REU_BANK_KEYS},'turbo_config':({'turbo16_zp':f'{hx(vals["TURBO16_ZP_BASE"],2)}-{hx(vals["TURBO16_ZP_BASE"]+112,2)}','turbo32_zp':f'{hx(vals["TURBO32_ZP_BASE"],2)}-{hx(vals["TURBO32_ZP_BASE"]+134,2)}'} if profile in REU else None),'reu_image':reu_info,'claims':[(n,hx(s),hx(e),sp) for n,s,e,sp in claims]}
 (outdir/'source_build_manifest.json').write_text(json.dumps(man,indent=2)+'\n');return man

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--profile',choices=PROFILES+['all'],default='all');ap.add_argument('--config-kind',choices=['reference','alternate'],default='reference');ap.add_argument('--config',type=Path);ap.add_argument('--out',type=Path,default=ROOT/'build_source');a=ap.parse_args();ps=PROFILES if a.profile=='all' else [a.profile];res=[]
 for p in ps:
  cfg=a.config or ROOT/'relocatable_source'/p/f'math_config_{a.config_kind}.inc'
  m=build(p,cfg,a.out/a.config_kind/p);res.append(m);print(p,a.config_kind,'BUILT',m['output_sha256'])
 (a.out/a.config_kind/'BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','config_kind':a.config_kind,'profiles':res},indent=2)+'\n')
if __name__=='__main__':main()
