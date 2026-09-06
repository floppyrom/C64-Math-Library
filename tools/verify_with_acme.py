#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse,hashlib,json,os,shutil,subprocess,tempfile,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from assemble_sources import build,parse_config,_assemble_overlay
from source_relocation import PROFILES

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(description='Verify source builds with real ACME and compare byte-for-byte with the bundled independent assembler.')
 ap.add_argument('--acme',type=Path,default=Path(os.environ.get('ACME','acme')))
 ap.add_argument('--kind',choices=['reference','alternate','all'],default='all')
 ap.add_argument('--out',type=Path,default=ROOT/'validation/acme')
 a=ap.parse_args(); acme=shutil.which(str(a.acme)) or (str(a.acme) if a.acme.exists() else None)
 if not acme:raise SystemExit('ACME not found; pass --acme /path/to/acme or set ACME')
 kinds=['reference','alternate'] if a.kind=='all' else [a.kind];a.out.mkdir(parents=True,exist_ok=True);rows=[]
 with tempfile.TemporaryDirectory(prefix='c64math-acme-') as td0:
  td=Path(td0)
  for kind in kinds:
   for p in PROFILES:
    cfg=ROOT/'relocatable_source'/p/f'math_config_{kind}.inc'; internal=build(p,cfg,td/'internal'/kind/p)
    stage=td/'stage'/kind/p;stage.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'relocatable_source'/p/'math_relocatable.asm',stage/'math_relocatable.asm');shutil.copy2(cfg,stage/'math_config.inc')
    out=stage/'acme.prg';cp=subprocess.run([acme,'-f','cbm','-o',str(out),'math_relocatable.asm'],cwd=stage,text=True,capture_output=True)
    if cp.returncode:raise RuntimeError(f'ACME failed {p}/{kind}:\n{cp.stdout}\n{cp.stderr}')
    ip=td/'internal'/kind/p/internal['output_prg'];same=out.read_bytes()==ip.read_bytes()
    if not same:raise AssertionError(f'ACME/internal mismatch: {p}/{kind}')
    refsame=None
    if kind=='reference':
     ref=ROOT/p/'resident'/f'math_{p}_game_math.prg';refsame=out.read_bytes()==ref.read_bytes()
     if not refsame:raise AssertionError(f'ACME reference does not reproduce corrected resident PRG: {p}')
    row={'profile':p,'map':kind,'status':'PASS','acme_sha256':sha(out),'internal_sha256':sha(ip),'byte_identical':same,'reference_prg_identical':refsame,'acme_stdout':cp.stdout.strip(),'acme_stderr':cp.stderr.strip()};rows.append(row)
    print(p,kind,'PASS',row['acme_sha256'])
 overlay_rows=[]
 # Independently assemble both relocatable ZP overlays with real ACME and compare
 # byte-for-byte against the included assembler for both REU profiles/maps.
 for kind in kinds:
  for p in ('v3_reu_512k','v4_reu_16m'):
   cfgp=ROOT/'relocatable_source'/p/f'math_config_{kind}.inc';vals=parse_config(cfgp)
   for name,basekey in (('turbo16','TURBO16_ZP_BASE'),('turbo32','TURBO32_ZP_BASE')):
    internal_bytes,_=_assemble_overlay(name,vals)
    stage=td/'overlay'/kind/p/name;stage.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/'relocatable_source'/'turbo'/f'{name}_overlay.asm',stage/f'{name}_overlay.asm')
    wrapper=stage/'wrapper.asm';wrapper.write_text(f'REG_TABLE=${vals["REG_TABLE"]:04x}\n{basekey}=${vals[basekey]:02x}\n!source "{name}_overlay.asm"\n')
    out=stage/'overlay.bin';cp=subprocess.run([acme,'-f','plain','-o',str(out),'wrapper.asm'],cwd=stage,text=True,capture_output=True)
    if cp.returncode:raise RuntimeError(f'ACME overlay failed {p}/{kind}/{name}:\n{cp.stdout}\n{cp.stderr}')
    same=out.read_bytes()==internal_bytes
    if not same:raise AssertionError(f'ACME/internal overlay mismatch: {p}/{kind}/{name}')
    ref_overlay_same=None
    if kind=='reference':
     reufn='c64_math_v3_512k_game_math.reu' if p=='v3_reu_512k' else 'c64_math_v4_16m_game_math.reu'
     refreu=(ROOT/p/'reu'/reufn).read_bytes(); bank=4 if name=='turbo16' else 5
     ref_overlay_same=out.read_bytes()==refreu[bank*0x10000:bank*0x10000+len(internal_bytes)]
     if not ref_overlay_same:raise AssertionError(f'ACME reference overlay does not reproduce bundled REU bytes: {p}/{name}')
    overlay_rows.append({'profile':p,'map':kind,'overlay':name,'status':'PASS','bytes':len(internal_bytes),'sha256':sha(out),'byte_identical':True,'reference_overlay_identical':ref_overlay_same})
 boundary_rows=[]
 # Edge geometries independently verify the bundled assembler's full supported
 # Turbo origin range, including Turbo16 at $8F and Turbo32 at $0F.
 for name,basekey,base,table in (('turbo16','TURBO16_ZP_BASE',0x02,0x4000),('turbo16','TURBO16_ZP_BASE',0x8f,0x6000),('turbo32','TURBO32_ZP_BASE',0x02,0x4000),('turbo32','TURBO32_ZP_BASE',0x0f,0x6000)):
  vals=parse_config(ROOT/'relocatable_source'/'v3_reu_512k'/'math_config_reference.inc');vals[basekey]=base;vals['REG_TABLE']=table
  internal_bytes,_=_assemble_overlay(name,vals)
  stage=td/'overlay_boundary'/name/f'{base:02x}';stage.mkdir(parents=True,exist_ok=True)
  shutil.copy2(ROOT/'relocatable_source'/'turbo'/f'{name}_overlay.asm',stage/f'{name}_overlay.asm')
  wrapper=stage/'wrapper.asm';wrapper.write_text(f'REG_TABLE=${table:04x}\n{basekey}=${base:02x}\n!source "{name}_overlay.asm"\n')
  out=stage/'overlay.bin';cp=subprocess.run([acme,'-f','plain','-o',str(out),'wrapper.asm'],cwd=stage,text=True,capture_output=True)
  if cp.returncode:raise RuntimeError(f'ACME boundary overlay failed {name}/${base:02X}:\n{cp.stdout}\n{cp.stderr}')
  if out.read_bytes()!=internal_bytes:raise AssertionError(f'ACME/internal boundary overlay mismatch: {name}/${base:02X}')
  boundary_rows.append({'overlay':name,'zp_base':f'${base:02X}','reg_table':f'${table:04X}','status':'PASS','bytes':len(internal_bytes),'sha256':sha(out),'byte_identical':True})
 result={'status':'PASS','assembler':subprocess.run([acme,'--version'],text=True,capture_output=True).stdout.splitlines()[0].strip(),'checks':rows,'overlay_checks':overlay_rows,'overlay_boundary_checks':boundary_rows}
 (a.out/'ACME_SOURCE_BUILD_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
