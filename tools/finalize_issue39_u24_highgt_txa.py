#!/usr/bin/env python3
"""Publish source-backed generic U24 live-X high-quotient evidence without promotion."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'validation/review/ISSUE39_U24_HIGHGT_LIVE_X_SCREEN.json'
DOC=ROOT/'docs/ISSUE39_U24_HIGHGT_LIVE_X_2026-10-13.md'
PROFILES=('v1_balanced','v2_pareto_fast')
OPS=('MATH_UDIV24','MATH_UMOD24')
TAG='2026-10-13 ISSUE39 GENERIC U24 HIGH-GT TXA SOURCE AUDIT'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def checksum():
 files=sorted((x for x in ROOT.rglob('*') if x.is_file() and '.git' not in x.parts
  and '__pycache__' not in x.parts and x.name!='SHA256SUMS.txt'),key=lambda x:str(x.relative_to(ROOT)))
 (ROOT/'SHA256SUMS.txt').write_text(''.join(sha(x)+'  '+str(x.relative_to(ROOT))+'\n' for x in files))
def main():
 a=json.loads(Path(sys.argv[1]).read_text())
 state=json.loads((ROOT/'RELEASE_STATUS.json').read_text())
 assert a['status']=='PASS_SOURCE_BACKED_HIGHGT_LIVE_X_RESEARCH'
 assert (a['paired_inputs'],a['cpu_calls'])==(34088,68176)
 assert set(a['profiles'])==set(PROFILES)
 assert not a['resident_changed'] and not a['public_api_changed']
 assert a['normal_zp_growth']==a['native_vice_calls']==0
 rows=[];concise={}
 for p in PROFILES:
  data=a['profiles'][p];res=ROOT/p/'resident'/('math_'+p+'_game_math.prg')
  assert sha(res)==data['resident_sha256']==state['reference_prg_sha256'][p]
  assert data['code']['source_edit']=='high_gt LDA N2 -> TXA'
  concise[p]={}
  for op in OPS:
   groups=data['routines'][op]
   assert len(groups)==8
   c=groups['official_common'];h=groups['n2_greater_d2']
   assert c['cases']==(4753 if op==OPS[0] else 1553)
   assert c['max_regression']<=3
   if p=='v1_balanced' or op==OPS[0]:
    assert c['slower']==0 and c['delta_mean']<0
   rows.append('| '+p+' | '+op[5:]+' | '+str(c['cases'])+' | '+format(c['delta_mean'],'+.6f')+
    ' | '+str(c['faster'])+' / '+str(c['slower'])+' | '+format(h['delta_mean'],'+.6f')+' |')
   concise[p][op]={'official_delta':c['delta_mean'],'official_faster':c['faster'],
    'official_slower':c['slower'],'highgt_delta':h['delta_mean']}
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 REPORT.write_text(json.dumps(a,indent=2,sort_keys=True)+'\n')
 doc=[
 '# Issue #39: generic U24 high-quotient live-X substitution',
 '',
 '13 October 2026. Source-backed research, not production promotion.',
 '',
 'Both V1 and V2 24-bit quotient paths first execute illegal NMOS LAX N2,',
 'putting N2 into A and X. On the N2>D2 high_gt path X remains unchanged',
 'until the high-byte subtract. Replace LDA N2 (4 cycles, 3 bytes) with',
 'TXA (2 cycles, 1 byte) immediately before SBC D2. This is a generic',
 'operand class, not a small-divisor caller-specialist. No new scratch.',
 '',
 'The existing V1 and V2 full monolithic sources were expanded and assembled',
 'before and after the single source mutation. The original source-built',
 'memory exactly matched current SHA-pinned V1/V2 resident program bytes.',
 'The candidate retained all stable public API addresses.',
 '',
 '**34,088 identical-input pairs, 68,176 emulated 6502 executions**,',
 'zero promised Q/R/carry/operand/high-R/scratch/stack discrepancies.',
 'Tests included official same-input pairs, N2>D2, N2=D2, N2<D2,',
 'nonzero D8/high N2, uniform operands, structured edges, zero divisor.',
 'Uncontracted Q3 side effects were counted separately.',
 '',
 '| Profile | Public API | Official cases | Delta mean cycles | Faster / slower | N2>D2 delta |',
 '|---|---|---:|---:|---:|---:|']+rows+[
 '',
 'Negative candidate-minus-original delta means faster. V1 UDIV24 and',
 'UMOD24 both gained without an observed slower official input; V2 UDIV24',
 'also gained without a slower input. V2 dedicated remainder-only UMOD24',
 'had a small layout/branch-phase tradeoff (13 faster, 18 slower), not',
 'an unconditional no-regression proof.',
 '',
 '**No default promotion yet.** Integration requires reference/alternate',
 'symbolic source rebuilds, V3/V4 inherited-source updates, V5 imported',
 'V2 donor repacking, resource-island integrity, native VICE correctness',
 'and full post-merge release CI. All resident binaries stay unchanged.',
 '',
 'Reproducer: tools/screen_issue39_u24_highgt_txa.py',
 'Evidence: validation/review/ISSUE39_U24_HIGHGT_LIVE_X_SCREEN.json',
 'Source roots: relocatable_source/v1_balanced/udiv24_direct_repose_balanced.inc',
 'and relocatable_source/v2_pareto_fast/udiv24_direct_repose.inc.',
 'Private OptiSearch tools and data are not published.',
 'Cycle figures exclude VIC/REU DMA bus contention.',
 '',
 'Issue #39 remains OPEN; unsigned DIV/MOD family not complete.'
 ]
 DOC.write_text('\n'.join(doc)+'\n')
 log=(TAG+'\n'
 '- Source-reassembled V1/V2 unrestricted UDIV24 high-byte subtraction with preserved prior LAX-held X: LDA N2 -> TXA, saving 2 CPU cycles and 2 instruction bytes on reached high_gt path. '+str(concise)+'\n'
 '- '+format(a['paired_inputs'],',')+' identical input pairs / '+format(a['cpu_calls'],',')+' full CPU calls, source-built original matched current resident SHA; zero Q24/R24/carry/input/high sentinel/stack mismatches. No resident/API/normal-ZP changes or native timing claims. V3/V4/V5 builds pending source promotion. Both changelogs, docs, release metadata/hashes updated; issue #39 OPEN. '+str(DOC.relative_to(ROOT))+'\n\n')
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  p=ROOT/name
  if TAG not in p.read_text():p.write_text(log+p.read_text())
 ref='- Generic 24-bit live-X high-quotient source proof: '+str(DOC.relative_to(ROOT))+'. Not promoted to stable residents.'
 for name in ('README.md','USER_MANUAL.md'):
  p=ROOT/name
  if ref not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+ref+'\n')
 state['issue39_u24_live_x_highgt_2026_10_13']={
  'status':'PASS_SOURCE_PROOF_NOT_PROMOTED',
  'report':str(REPORT.relative_to(ROOT)),'report_sha256':sha(REPORT),
  'documentation':str(DOC.relative_to(ROOT)),
  'reproducer':'tools/screen_issue39_u24_highgt_txa.py',
  'paired_inputs':a['paired_inputs'],'cpu_calls':a['cpu_calls'],
  'profiles':concise,'normal_zp_growth':0,'native_vice_calls':0,
  'resident_images_changed':False,'stable_API_changed':False,
  'unsigned_family_complete':False}
 if isinstance(state.get('documentation'),dict):
  p=ROOT/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=p.stat().st_size,
   user_manual_lines=len(p.read_text().splitlines()),user_manual_sha256=sha(p))
 (ROOT/'RELEASE_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=ROOT,check=True)
 for _ in range(3):
  checksum()
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=ROOT,check=True)
 subprocess.run([sys.executable,'tools/validate_public_catalog.py'],cwd=ROOT,check=True)
 print('ISSUE39 GENERIC U24 HIGHGT SOURCE AUDIT SEALED',flush=True)
if __name__=='__main__':main()
