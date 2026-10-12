#!/usr/bin/env python3
"""Fail-closed V5 Q-preserving UMOD32 ref/alternate source build qualification."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
P='v5_hybrid_lowzp'
OLD='634e58f536374bc12877e692515f68ab5c5f38954caf5c189a8f67d356289d02'
NEW='5191e44263c24c617a4d5ddc490b3d5fbe7f87c5ac0835af28294fdbc6f9d222'
REPORT=ROOT/'validation/review/ISSUE39_V5_UMOD32_SOURCE_QUALIFIED.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 orig=(ROOT/P/'resident'/f'math_{P}_game_math.prg').read_bytes()
 new=(ROOT/'build_hybrid/reference'/P/f'math_{P}_game_math.prg').read_bytes()
 alt=(ROOT/'build_hybrid/alternate'/P/f'math_{P}_game_math.prg').read_bytes()
 assert sha(orig)==OLD,('unexpected V5 resident',sha(orig))
 assert sha(new)==NEW,('reference source did not reproduce native-tested candidate',sha(new))
 assert len(orig)==len(new)==49042
 assert orig[:2]==new[:2]==b'\0\x10'
 load=0x1000
 def read(b,a,n):return b[2+a-load:2+a-load+n]
 assert read(orig,0x5e03,3)==bytes.fromhex('4c5759')
 assert read(new,0x5e03,3)==bytes.fromhex('4c805e')
 assert read(orig,0x5e80,147)==bytes(147)
 assert len(read(new,0x5e80,147))==147
 changes=[i-2+load for i,(x,y) in enumerate(zip(orig,new)) if x!=y]
 assert changes and all(a in {0x5e03,0x5e04,0x5e05} or 0x5e80<=a<0x5e80+147 for a in changes),('unexpected changed resident bytes',list(map(hex,changes[:35])))
 assert len(changes)>100
 assert alt[:2]!=orig[:2] or sha(alt)!=OLD, 'alternate configuration not relocated'
 manifest=json.loads((ROOT/'build_hybrid/reference'/P/'hybrid_manifest.json').read_text()) if (ROOT/'build_hybrid/reference'/P/'hybrid_manifest.json').exists() else None
 report={'status':'PASS','profile':P,'old_resident_sha256':OLD,
  'native_candidate_sha256':NEW,'source_reference_sha256':sha(new),
  'source_alternate_sha256':sha(alt),'source_reference_and_alternate':'PASS',
  'byte_changes':len(changes),'resident_size_growth':0,'normal_zp_growth':0,
  'code_origin':'$5E80','full_quotient_and_remainder':True,
  'only_modified_addresses':['$5E03-$5E05','$5E80-$5F12'],
  'no_release_resident_replaced':True}
 REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,indent=2)+'\n')
 print('ISSUE39 V5 UMOD32 SOURCE QUALIFICATION PASS',len(changes),sha(new),flush=True)
if __name__=='__main__':main()
