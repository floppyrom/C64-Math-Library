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
 # The unrolled low/high core moves, page-aligned, from $1900 to $7800;
 # both explicit redirect JMP operands point into the new island.
 seek=set(range(start,start+size))
 division=set()
 if p in (P[0],P[-1]) and k=='reference':
  division=set(range(0x7800,0x7bf8)) | set(range(0x446a,0x446d)) | set(range(0x4570,0x4573))
 assert changed and all(a in seek or a in division for a in changed),(p,k,'unexpected modified address',changed[:45])
 assert any(a in seek for a in changed)
 if division:assert any(0x7800<=a<=0x7bf7 for a in changed)
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
 assert prev['routines']==current['routines']
 assert prev['total_calls']==current['total_calls']==136335
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
  'private_optisearch_source_published':False}
 sfile.write_text(json.dumps(status,indent=2)+'\n')
 cert={'status':'PASS_NATIVE_VICE_STAGED_PR_MAIN_CI_PENDING',
  'profiles':measured,'image_delta':delta,'native_calls':240,'baseline_prgs':old,
  'candidate_prgs':new,'alternate_prgs':alt,'model_all_steps_exact':True,
  'no_reu_change':True,'no_zp_growth':True,'issue39_remains_open':True}
 (R/CERT).write_text(json.dumps(cert,indent=2,sort_keys=True)+'\n')
 table='| Profile | Before Euclidean INIT | After | Saved cycles |\n|---|---:|---:|---:|\n'
 table+=''.join(f"| {p} | {q['before_eucl']:.6f} | {q['after_eucl']:.6f} | {q['eucl_savings']:.6f} |\n" for p,q in measured.items())
 (R/DOC).write_text('# SEEK16 Euclidean INIT release, Issue #39\n\n'+
  'Source-backed conditional-loop optimization for V1–V5. Native x64sc old/new: '
  '240 public calls, real REU images for V3/V4; no hardware cycles timed. '
  'Official 408-move per-profile corpus confirms every frame, unchanged other '
  'SEEK operations and non-Euclidean INIT; same public ABI/ZP/resources.\n\n'+table+
  '\nProduction stage requires full PR/main green CI. SEEK family audit and '
  'OptiSearch candidate review remain open.\n')
 note=(STAMP+'\n- SEEK16 Euclidean INIT scale loop: one byte smaller, '
   'faster on CPU-model paired calls, unchanged major-axis INIT and SEEK8/STEP paths. '
   'Five profiles, two relocation maps, 240 baseline/candidate native VICE '
   'public calls, unchanged REU/ZP/ABI. Standalone mirrors, performance, '
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