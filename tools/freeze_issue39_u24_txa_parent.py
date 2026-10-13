#!/usr/bin/env python3
"""Freeze exact pre-TXA parent reconstruction patches for historical proofs.

The immutable public Git parent is used ONCE to create a permanent offline
byte-delta ledger, so historical PR78/PR81 checks remain reproducible without
Git history, the web, or a stale pre-release current resident.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
PARENT='c88416430737bfb84903b9af5acba96e71a7605b'
PROFILES=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
OUT=R/'validation/review/ISSUE39_U24_TXA_PARENT_RESTORATION.json'
DOC=R/'docs/ISSUE39_U24_TXA_SOURCE_INTEGRATION_2026-10-13.md'
def sha(data):return hashlib.sha256(data).hexdigest()
def fsha(p):return sha(Path(p).read_bytes())
def checksum():
 files=sorted((x for x in R.rglob('*') if x.is_file() and '.git' not in x.parts
  and '__pycache__' not in x.parts and x.name!='SHA256SUMS.txt'),key=lambda x:str(x.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(fsha(x)+'  '+str(x.relative_to(R))+'\n' for x in files))
def main():
 statusp=R/'RELEASE_STATUS.json'
 state=json.loads(statusp.read_text())
 release=state['issue39_u24_txa_production_source_2026_10_13']
 assert release['status']=='PASS_SOURCE_AND_NATIVE_VICE_QUALIFIED'
 profiles={}
 for p in PROFILES:
  fn=f'{p}/resident/math_{p}_game_math.prg'
  old=subprocess.run(['git','show',PARENT+':'+fn],cwd=R,capture_output=True,check=True).stdout
  current=(R/fn).read_bytes()
  assert sha(old)==release['before_reference_sha256'][p]
  assert sha(current)==release['after_reference_sha256'][p]
  assert len(old)==len(current)
  runs=[];i=0
  while i<len(old):
   if old[i]==current[i]:
    i+=1;continue
   a=i
   while i<len(old) and old[i]!=current[i]:i+=1
   runs.append({'offset':a,'old_bytes_hex':old[a:i].hex()})
  assert runs,(p,'no changes')
  rebuilt=bytearray(current)
  for run in runs:
   a=run['offset'];before=bytes.fromhex(run['old_bytes_hex'])
   rebuilt[a:a+len(before)]=before
  assert bytes(rebuilt)==old,(p,'historical parent delta replay')
  profiles[p]={'current_sha256':sha(current),'old_sha256':sha(old),
    'prg_length':len(old),'changed_byte_count':sum(len(bytes.fromhex(x['old_bytes_hex'])) for x in runs),
    'changed_runs':runs,'run_count':len(runs)}
  print('PINNED OFFLINE U24 PARENT',p,profiles[p]['changed_byte_count'],'byte changes',len(runs),'regions',flush=True)
 payload={'status':'PASS_REVERSIBLE_SHA_PINNED_PARENT_DELTA',
    'historical_parent_commit':PARENT,
    'purpose':'Preserve isolated old V1 24by8 PR78/PR81 audit inputs after unrelated generic U24 promotion',
    'profiles':profiles,'same_length_PRGs':True,'production_residents_changed_by_this_ledger':False}
 OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
 doc=DOC.read_text()
 note=('\nHistorical 24/8 regression checks use a SHA-verified **offline parent\n'
       'restoration ledger** in validation/review/ISSUE39_U24_TXA_PARENT_RESTORATION.json.\n'
       'It reconstructs the exact pre-optimization complete residents from the\n'
       'new shipped ones, preserving the original PR78/PR81 benchmark tests;\n'
       'the historical test is never simply disabled or reinterpreted.\n')
 if 'offline parent' not in doc:DOC.write_text(doc.rstrip()+'\n'+note)
 release['historical_parent_restoration_report']=str(OUT.relative_to(R))
 release['historical_parent_restoration_sha256']=fsha(OUT)
 release['historical_parent_restoration_status']='PASS_ALL_FIVE_EXACT_PARENT_SHAS'
 state['documentation']['user_manual_sha256']=fsha(R/'USER_MANUAL.md')
 statusp.write_text(json.dumps(state,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  checksum();subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 checksum()
 subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 print('ISSUE39 U24 TXA OFFLINE PARENT DELTA FROZEN',flush=True)
if __name__=='__main__':main()
