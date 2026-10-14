#!/usr/bin/env python3
"""Guarded Issue39 SEEK16 source-backed production staging and release seal."""
from pathlib import Path
import hashlib, json, csv, shutil, subprocess, sys
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from mini6502 import Assembler
import seek_kernel as SK, generate_seek_sources as GS
from stage_issue39_v1_3216_ool_release import reseal
P=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
K=('reference','alternate')
EVID='validation/review/ISSUE39_SEEK16_SCALE_NATIVE_2026-10-14.json'
CERT='validation/review/ISSUE39_SEEK16_SCALE_PRODUCTION_2026-10-14.json'
DOC='docs/ISSUE39_SEEK16_EUCLIDEAN_INIT_RELEASE_2026-10-14.md'
STAMP='2026-10-14 ISSUE39 SEEK16 EUCLIDEAN INIT LOOP RELEASE'
def h(b):return hashlib.sha256(b).hexdigest()
def run(script,*args):subprocess.run([sys.executable,str(R/'tools'/script),*args],cwd=R,check=True)
def resident(p):return R/p/'resident'/('math_'+p+'_game_math.prg')
def generated(p,k):
 d=(R/('build_hybrid' if p==P[-1] else 'build_source')/k/p)
 m=json.loads((d/'source_build_manifest.json').read_text())
 return d/m['output_prg']
def build():
 run('generate_sources.py')
 for k in K:
  run('assemble_sources.py','--profile','all','--config-kind',k)
  run('build_hybrid.py','--config-kind',k)
def check_delta(p,k,old,new):
 assert len(old)==len(new) and old[:2]==new[:2]
 base=P[0] if p==P[-1] else p
 cfg=(R/'relocatable_source'/base/('math_config_'+k+'.inc')).read_text()
 expr,note=GS.SCRATCH[base]
 _,labels,_=Assembler().assemble(cfg+'\n'+SK.library(base,GS.LAYOUTS[base],expr,note))
 start=labels['seek16_init']; size=312 if p in (P[0],P[-1]) else 271
 load=int.from_bytes(old[:2],'little')
 changed=[load+i for i,(a,b) in enumerate(zip(old[2:],new[2:])) if a!=b]
 # V1/V5 also repair the long-standing public SEEK-state/UDIV32 collision.
 # Only the clashing LOW rounds move from $1900 to $4D80;
 # both explicit redirect JMP operands point into the new island.
 seek=set(range(start,start+size))
 division=set()
 if p in (P[0],P[-1]) and k=='reference':
  division=(set(range(0x4d80,0x4fed)) | set(range(0x4569,0x456c))
            | set(range(0x4570,0x4573)))
 assert changed and all(a in seek or a in division for a in changed),(p,k,'unexpected modified address',changed[:45])
 assert any(a in seek for a in changed)
 if division:assert any(0x4d80<=a<=0x4fec for a in changed)
 return dict(first=hex(min(changed)),last=hex(max(changed)),changed_bytes=len(changed),
   ud32_state_collision_relocation=(p in (P[0],P[-1])))
def main():
 n=json.loads((R/EVID).read_text())
 assert n['status']=='PASS_NATIVE_VICE_PAIRED_SEEK16_INIT' and n['public_calls']==240
 sfile=R/'RELEASE_STATUS.json';status=json.loads(sfile.read_text())
 old={p:h(resident(p).read_bytes()) for p in P}
 assert old==status['reference_prg_sha256']
 prior=json.loads((R/'validation/movement/SEEK_PROFILE_BENCHMARK.json').read_text())
 run('generate_seek_sources.py');run('generate_seek_sources.py','--check');build()
 new={p:h(generated(p,'reference').read_bytes()) for p in P}
 alt={p:h(generated(p,'alternate').read_bytes()) for p in P}
 delta={}
 for p in P:
  assert old[p]!=new[p]
  assert n['profiles'][p]['old_prg']==old[p] and n['profiles'][p]['candidate_prg']==new[p]
  # Shipped original PRG is in the reference map only. Alternate PRGs use
  # different load addresses/spans; PR #134 already paired old/new alternates
  # independently and the full alternate public validation runs below.
  delta[p]={'reference':check_delta(p,'reference',resident(p).read_bytes(),
           generated(p,'reference').read_bytes()),
           'alternate':{'candidate_sha256':alt[p],
                        'same_input_old_new_verified_in_research_pr134':True}}
 # Diagnostic gate: V1 UDIV32 must remain callable after relocating its
 # low-round island, before any SEEK-state writes are made.
 from mini6502 import CPU
 def diag_udiv32(blob, who):
  from native_issue39_signed_multiply_family import api
  a=api(P[0]);ld=int.from_bytes(blob[:2],'little')
  m=bytearray(65536);m[ld:ld+len(blob)-2]=blob[2:]
  c=CPU(m);c.d=0;c.call(a['MATH_INIT'],2000000)
  visited=[];step0=CPU.step
  def trace(self):
   pc=self.pc
   if pc in (0x4569,0x4570,0x1900,0x4d80,0x1b6d,0x4fed,0x4fef):
    visited.append((hex(pc),self.a,self.x,self.y))
   return step0(self)
  CPU.step=trace
  try:
   c.mem[a['MATH_N']]=1;c.mem[a['MATH_D']]=1
   n=c.call(a['MATH_UDIV32_16'],2000000)
  finally:CPU.step=step0
  q=c.mem[a['MATH_Q']]|c.mem[a['MATH_Q']+1]<<8
  rem=c.mem[a['MATH_R']]|c.mem[a['MATH_R']+1]<<8
  print('ISSUE136 DIAG',who,'q',q,'r',rem,'carry',c.c,'cycles',n,
        'visited',visited[:25], 'jmp4569',m[0x4569:0x456c].hex(),
        'jmp4570',m[0x4570:0x4573].hex(),'low4',m[0x4d80:0x4d88].hex(),flush=True)
 old_blob=resident(P[0]).read_bytes();new_blob=generated(P[0],'reference').read_bytes()
 old_block=old_blob[0x1900-0x1000+2:0x1b6d-0x1000+2]
 new_block=new_blob[0x4d80-0x1000+2:0x4fed-0x1000+2]
 mism=[(hex(i),hex(x),hex(y)) for i,(x,y) in enumerate(zip(old_block,new_block)) if x!=y]
 print('ISSUE136 LOW BYTE ALIGN',len(old_block),len(new_block),'mismatches',len(mism),'first',mism[:32],flush=True)
 diag_udiv32(old_blob,'old')
 diag_udiv32(new_blob,'candidate')
 # Both independently relocatable source maps and all foreign-access
 # memory-island checks must pass before touching a published PRG.
 for k in K:
  run('validate_source_build.py','all','--build',str(R/'build_source'/k),
      '--out','validation/source_relocation/'+k)
 run('validate_seek_placement.py')
 for p in P:shutil.copyfile(generated(p,'reference'),resident(p))
 run('benchmark_seek_profiles.py')
 b=json.loads((R/'validation/movement/SEEK_PROFILE_BENCHMARK.json').read_text())
 assert b['status']=='PASS' and b['prg_sha256']==new
 measured={}
 for p in P:
  a=prior['profiles'][p]; c=b['profiles'][p]
  for op in ('MATH_SEEK8_INIT','MATH_SEEK8_STEP','MATH_SEEK8_STEP_INT',
             'MATH_SEEK8_STEP1','MATH_SEEK16_STEP','MATH_SEEK16_STEP_INT',
             'MATH_SEEK16_STEP1'):
   assert a[op]==c[op],(p,op)
  x=a['MATH_SEEK16_INIT'];y=c['MATH_SEEK16_INIT']
  for typ in ('major_axis_speed','integer_speed','one_pixel'):
   assert x[typ]==y[typ],(p,typ)
  assert y['euclidean_speed']['mean_cycles']<x['euclidean_speed']['mean_cycles']
  measured[p]=dict(old_mean=x['mean_cycles'],new_mean=y['mean_cycles'],
    before_eucl=x['euclidean_speed']['mean_cycles'],
    after_eucl=y['euclidean_speed']['mean_cycles'],
    eucl_savings=x['euclidean_speed']['mean_cycles']-y['euclidean_speed']['mean_cycles'])
 # Public front-door performance table.
 perf=R/'PERFORMANCE.md';rows=perf.read_text().splitlines(keepends=True);seen=0
 for i,line in enumerate(rows):
  if line.startswith('| `MATH_SEEK16_INIT` |'):
   cols=line.rstrip('\n').split('|')
   assert len(cols)==9
   for j,p in enumerate(P):cols[j+3]=f" {measured[p]['new_mean']:.6f} "
   rows[i]='|'.join(cols)+'\n';seen+=1
 assert seen==1;perf.write_text(''.join(rows))
 doc=R/'docs/SEEK_DDA.md';rows=doc.read_text().splitlines(keepends=True);seen=0
 for i,line in enumerate(rows):
  if line.startswith('| `MATH_SEEK16_INIT`, Euclidean speed |'):
   rows[i]='| `MATH_SEEK16_INIT`, Euclidean speed | '+' | '.join(
     f"{b['profiles'][p]['MATH_SEEK16_INIT']['euclidean_speed']['mean_cycles']:.1f}" for p in P)+' |\n'
   seen+=1
 assert seen==1;doc.write_text(''.join(rows))
 # Re-extract and reconstruct all updated source images to guarantee roundtrip.
 build()
 for p in P:assert h(generated(p,'reference').read_bytes())==new[p]
 run('publish_standalone_sources.py')
 run('generate_consolidated_routine_table.py')
 # The common same-input unsigned corpus contains pinned whole-image hashes.
 cp=R/'validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json'
 prev=json.loads(cp.read_text());run('benchmark_unsigned_common_corpus.py')
 current=json.loads(cp.read_text())
 # Moving the V1 low-round loop changes branch page phases slightly.
 # Preserve identical input corpora and arithmetic results, and allow ONLY
 # measured, tightly bounded cycle shifts in known transitive V1 beneficiaries.
 assert prev['total_calls']==current['total_calls']==136335
 assert prev['profile_order']==current['profile_order']==list(P)
 assert prev['contract']==current['contract']
 allowed={'MATH_UDIV32_16','MATH_UMOD32_16','MATH_UDIV32_32',
          'MATH_UMOD32_32','MATH_UDIV16_SHL8'}
 timing_deltas={}
 assert prev['routines'].keys()==current['routines'].keys()
 for op,oldop in prev['routines'].items():
  newop=current['routines'][op]
  for key in ('status','random_seed','cases_per_profile','total_calls','same_cases_sha256'):
   assert oldop[key]==newop[key],(op,'comparability contract',key)
  for profile in P:
   a=oldop['metrics'][profile];z=newop['metrics'][profile]
   if a==z:continue
   assert profile=='v1_balanced' and op in allowed,(op,profile,'unexpected cycle metric delta',a,z)
   diff=z['mean_cycles']-a['mean_cycles']
   assert abs(diff)<1.0,(op,'unacceptable average-cycle drift',diff)
   assert abs(z['p95_cycles']-a['p95_cycles'])<=8,(op,'p95 drift')
   assert abs(z['max_cycles']-a['max_cycles'])<=8,(op,'worst drift')
   timing_deltas[op]={'profile':profile,'old_mean_cycles':a['mean_cycles'],
                     'new_mean_cycles':z['mean_cycles'],'delta_cycles':diff}
 assert timing_deltas,('missing transitive V1 page-phase measurements')
 print('ISSUE136 COMMON-CORPUS TIMING DELTAS',timing_deltas,flush=True)
 # The routine tables must reflect the new same-input benchmark rather than
 # retaining the old V1 timing/PRG hashes from earlier generated rows.
 run('generate_consolidated_routine_table.py')
 # Also refresh the hand-curated quick performance table for changed V1 calls.
 performance=R/'PERFORMANCE.md';lines=performance.read_text().splitlines(keepends=True)
 for op in timing_deltas:
  marker='| '+chr(96)+op+chr(96)+' |'
  hits=[i for i,line in enumerate(lines) if line.startswith(marker)]
  assert len(hits)==1,(op,'missing public performance row',len(hits))
  i=hits[0];parts=lines[i].rstrip('\n').split('|')
  assert len(parts)==9
  parts[3]=f" {current['routines'][op]['metrics']['v1_balanced']['mean_cycles']:.6f} "
  lines[i]='|'.join(parts)+'\n'
 performance.write_text(''.join(lines))
 # Run the new complete-state interleaving gate before publication.
 run('validate_issue136_seek_divmod_mixed.py')
 run('generate_public_indexes.py')
 status['reference_prg_sha256']=new;status['alternate_prg_sha256']=alt
 if isinstance(status.get('hybrid_v5'),dict):
  status['hybrid_v5']['reference_prg_sha256']=new[P[-1]]
  status['hybrid_v5']['alternate_prg_sha256']=alt[P[-1]]
 if isinstance(status.get('issue39_common_input_unsigned_divmod'),dict):
  status['issue39_common_input_unsigned_divmod']['benchmark_sha256']=h(cp.read_bytes())
 status['issue39_seek16_euclid_scale_2026_10_14']={
  'status':'PASS_NATIVE_VICE_STAGED_PR_MAIN_CI_PENDING',
  'candidate_prg_sha256':new,'alternate_prg_sha256':alt,
  'native_public_calls':240,'resource_growth_bytes':0,'reu_modified':False,
  'native_cycle_timing_measured':False,'seek_family_complete':False,
  'issue39_open':True,'document':DOC,'certificate':CERT,
  'issue136_v1v5_division_seek_collision_repaired':True,
  'issue136_relocation':'UDIV32 low $1900-$1B6C -> $4D80-$4FEC',
  'mixed_seek_divmod_proof':'validation/review/ISSUE136_SEEK_DIVMOD_MIXED_PROOF.json',
  'transitive_v1_division_timing_deltas':timing_deltas,
  'private_optisearch_source_published':False}
 sfile.write_text(json.dumps(status,indent=2)+'\n')
 cert={'status':'PASS_NATIVE_VICE_STAGED_PR_MAIN_CI_PENDING',
  'profiles':measured,'image_delta':delta,'native_calls':240,'baseline_prgs':old,
  'candidate_prgs':new,'alternate_prgs':alt,'model_all_steps_exact':True,
  'no_reu_change':True,'no_zp_growth':True,'issue39_remains_open':True,
  'issue136_collision_repaired':True,
  'transitive_v1_division_timing_deltas':timing_deltas,
  'mixed_seek_divmod_public_calls':18280,'mixed_seek_step_calls':13580}
 (R/CERT).write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n')
 table='| Profile | Before Euclidean INIT | After | Saved cycles |\n|---|---:|---:|---:|\n'
 table+=''.join(f"| {p} | {q['before_eucl']:.6f} | {q['after_eucl']:.6f} | {q['eucl_savings']:.6f} |\n" for p,q in measured.items())
 (R/DOC).write_text('# SEEK16 Euclidean INIT release, Issue #39\n\n'+
  'Source-backed conditional-loop optimization for V1–V5. Native x64sc old/new: '
  '240 public calls, real REU images for V3/V4; no hardware cycles timed. '
  'Official 408-move per-profile corpus confirms every frame, unchanged other '
  'SEEK operations and non-Euclidean INIT; same public ABI/ZP/resources.\n\n'+
  'Issue #136 safety repair: V1/V5 UDIV32/16 low-round code was moved from '
  '$1900-$1B6C to shared free $4D80-$4FEC, preserving public SEEK position '
  'arrays and all API addresses. Full 408-byte movement state survived '
  '18,280 interleaved DIV/MOD public calls and 13,580 SEEK steps in the '
  'CPU-model regression (not native timing).\n\n'+
  'Transitive V1 division timing changes on the same-input corpus: '+
  json.dumps(timing_deltas,sort_keys=True)+'\n\n'+table+
  '\nProduction stage requires full PR/main green CI. SEEK family audit and '
  'OptiSearch candidate review remain open.\n')
 note=(STAMP+'\n- SEEK16 Euclidean INIT scale loop: one byte smaller, '
   'faster on CPU-model paired calls, unchanged major-axis INIT and SEEK8/STEP paths. '
   'Five profiles, two relocation maps, 240 baseline/candidate native VICE '
   'public calls. Repaired Issue #136 V1/V5 UDIV32/SEEK state collision '
   'by moving the low-round island to $4D80-$4FEC, preserving the public ABI. '
   'Passed 18,280 mixed DIV/MOD public calls and 13,580 SEEK steps. '
   'Rebenchmarked transitive V1 timing; unchanged REU/ZP. Standalone mirrors, performance, '
   'package audit and checksums regenerated. PR/main CI pending; Issue #39 '
   'still open for SEEK family. '+DOC+'\n\n')
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=R/name
  if STAMP not in f.read_text():f.write_text(note+f.read_text())
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  reseal();run('package_audit.py')
 print('SEEK16 PRODUCTION CANDIDATE STAGED; FAMILY STILL OPEN')
if __name__=='__main__':main()