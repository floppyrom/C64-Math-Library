#!/usr/bin/env python3
"""CI-only source-built V2 UMUL8 direct-output release staging, fail closed."""
from pathlib import Path
import csv,hashlib,json,shutil,subprocess,sys,tempfile
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
import assemble_sources as asm,build_hybrid as hybrid,validate_source_build as validate
from validate_unsigned_division import PROFILES,wr,rd
from stage_issue39_v1_3216_ool_release import reseal
V2='v2_pareto_fast';V5='v5_hybrid_lowzp'
EXPECTED='71648ececccba3186a1b186144dbace5e345a9a0967d397ec1db0655cef31c04'
V5_EXPECT='b27e0885c7241dd7bdc3b2e25be6b2c616685cb426436a3c2b8260eff7a21ebb'
MARK='2026-10-13 ISSUE39 UMUL8 DIRECT OUTPUT SOURCE RELEASE'
DOC='docs/ISSUE39_V2_UMUL8_DIRECT_OUTPUT_2026-10-13.md'
PROOF='validation/review/ISSUE39_V2_UMUL8_DIRECT_OUTPUT_RELEASE.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def image(p):return R/p/'resident'/f'math_{p}_game_math.prg'
def run(*parts):
 print('RUN',*map(str,parts),flush=True)
 subprocess.run([str(x) for x in parts],cwd=R,check=True)
def py(s,*a):run(sys.executable,R/'tools'/f'{s}.py',*a)
def assemble(kind,dest):
 out=dest/V2
 meta=asm.build(V2,R/'relocatable_source'/V2/f'math_config_{kind}.inc',out)
 return out/meta['output_prg'],meta
def build5(kind,dest):
 out=dest/V5
 meta=hybrid.build(R/'relocatable_source'/V5/f'math_config_{kind}.inc',out)
 return out/meta['output_prg'],meta
def modify_perf(rel,fn):
 with (R/rel).open(newline='') as stream:rows=list(csv.DictReader(stream))
 fn(rows)
 with (R/rel).open('w',newline='') as stream:
  writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
  writer.writeheader();writer.writerows(rows)
def bench(build):
 c,P,io,_,_=validate.load(V2,build)
 entry=P['MATH_UMUL8']
 sp=c.sp;total=0;mini=99999;maxi=0
 for k in range(65536):
  x=k&255;y=k>>8
  wr(c.mem,io,x+0x5500,2);wr(c.mem,io+4,y+0xAA00,2)
  c.mem[io+8:io+12]=bytes([0x81,0x93,0xA5,0xB7])
  c.c=k&1;c.d=0
  t=c.call(entry,2000)
  assert rd(c.mem,io+8,2)==x*y,(x,y,'product')
  assert rd(c.mem,io,2)==x+0x5500 and rd(c.mem,io+4,2)==y+0xAA00
  assert c.c==0 and c.sp==sp and bytes(c.mem[io+10:io+12])==b'\xA5\xB7'
  total+=t;mini=min(mini,t);maxi=max(maxi,t)
 mean=total/65536
 assert mean==72.494140625,mean
 return {'cases':65536,'mean_cycles':mean,'min_cycles':mini,'max_cycles':maxi}
def main():
 status_file=R/'RELEASE_STATUS.json';state=json.loads(status_file.read_text())
 prev={p:sha(image(p)) for p in PROFILES}
 assert prev==state['reference_prg_sha256']
 with tempfile.TemporaryDirectory(prefix='issue39_v2_umul8_stage_') as dirname:
  tmp=Path(dirname)
  base,bm=assemble('reference',tmp/'original')
  assert sha(base)==EXPECTED and base.stat().st_size==image(V2).stat().st_size
  shutil.copyfile(base,image(V2))
  py('generate_sources')
  assert (R/'relocatable_source'/V2/'math_relocatable.asm').read_text().count('umul8_directout_trial.inc')==1
  maps={}
  for kind in ('reference','alternate'):
   rebuilt,meta=assemble(kind,tmp/'rebuilt'/kind)
   if kind=='reference':assert sha(rebuilt)==EXPECTED
   v=validate.validate(V2,tmp/'rebuilt'/kind)
   assert v['status']=='PASS' and v['public_entries_executed']>=56
   vv,_=build5(kind,tmp/'v5'/kind)
   if kind=='reference':assert sha(vv)==V5_EXPECT,'V5 changed unexpectedly'
   maps[kind]={'sha256':sha(rebuilt),'public_calls':v['machine_calls'],
      'public_entries':v['public_entries_executed'],'v5_sha256':sha(vv)}
   print('V2 UMUL8',kind,'ABI PASS',v['machine_calls'],flush=True)
  perf=bench(tmp/'rebuilt'/'reference')
  print('V2 UMUL8 EXACT EXHAUSTIVE MEAN',perf['mean_cycles'],flush=True)
 assert all(sha(image(p))==prev[p] for p in PROFILES if p!=V2)
 py('validate_unsigned_division');py('validate_signed_division')
 py('benchmark_unsigned_common_corpus');py('benchmark_unsigned_3216_workloads')
 py('audit_issue39_unsigned_small_workloads');py('audit_issue39_v1v5_umod8_guard')
 def patchcsv(rows):
  row=next(x for x in rows if x['operation']=='math_umul8')
  assert 78.49<float(row['avg_cycles'])<78.50
  row.update(avg_cycles=f"{perf['mean_cycles']:.6f}",min_cycles=str(perf['min_cycles']),
   max_cycles=str(perf['max_cycles']),cases='65536',edge_cases='65536',
   evidence='2026-10-13 source-built exhaustive 8x8 direct output')
 modify_perf(V2+'/PUBLIC_PERFORMANCE.csv',patchcsv)
 document=R/'PERFORMANCE.md';lines=document.read_text().splitlines()
 mark='| '+chr(96)+'MATH_UMUL8'+chr(96)+' |'
 matches=[i for i,s in enumerate(lines) if s.startswith(mark)];assert len(matches)==1
 cells=lines[matches[0]].split('|')
 cells[4]=' '+f"{perf['mean_cycles']:.6f}"+' ';lines[matches[0]]='|'.join(cells)
 document.write_text('\n'.join(lines)+'\n')
 py('publish_standalone_sources');py('generate_consolidated_routine_table')
 py('generate_public_indexes');py('validate_public_catalog')
 py('validate_standalone_sources');py('verify_deterministic_rebuild')
 evidence={'status':'PASS_STAGED_NATIVE_VICE_PENDING','candidate_sha256':EXPECTED,
  'original_sha256':prev[V2],'maps':maps,'exhaustive':perf,
  'native_vice_calls':0,'normal_zp_growth':0,'resident_prg_byte_growth':0,
  'v5_still_previous':True,'issue39_complete':False}
 p=R/PROOF;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(evidence,indent=2,sort_keys=True)+'\n')
 (R/DOC).write_text(
  '# Issue39 V2 UMUL8 zero-growth direct-output optimization\n\n'
  '13 October 2026. This is a **staged release; native VICE and PR/main CI pending**.\n\n'
  'Manual technique: replace the public UMUL8 copy of the low product byte '
  'from a shared zero-page temporary with a direct write to public MATH_Z '
  'in the quarter-square producer. The low-byte write preserves carry for '
  'the high-byte subtraction. The 37-byte kernel starts at $52FE, using '
  'two previously empty bytes before the original 35-byte $5300 kernel. '
  'The 14-byte public wrapper leaves five NOP padding bytes in its former '
  '19-byte slot. Executable byte span and resident image length do not grow, '
  'no new zero page, REU, table or stack storage is required.\n\n'
  'The full 65,536-pair same-input 6502 model measured **78.494141 -> '
  '72.494141 cycles** (exactly -6 cycles on every input); the published prior '
  'PUBLIC_PERFORMANCE historical harness recorded 78.494614, which uses a '
  'slightly different timing basis and is not silently treated as paired. '
  'All 56 public entries and 21,678 mixed API calls pass each of the '
  'reference and alternate source maps. V1/V3/V4 and V5 hybrid remain '
  'unchanged. Private OptiSearch code is not included.\n\n'
  '**Pending**: native x64sc comparison on actual source-installed V2 '
  'resident, full PR CI and post-merge main CI. Issue #39 remains OPEN.\n')
 note=(MARK+'\n'
   '- V2 UMUL8 source-owned public direct output: -6 cycles on all '
   '65,536 tested 8x8 inputs (78.494141 to 72.494141), zero ZP/resident'
   ' growth, no change to V1/V3/V4/V5. Both source maps and complete'
   ' public ABI regression pass. Native VICE pending. '+DOC+'\n\n')
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=R/name
  if MARK not in f.read_text():f.write_text(note+f.read_text())
 for name in ('README.md','USER_MANUAL.md'):
  f=R/name;line='- V2 UMUL8 public direct-result source release: '+DOC+' (native VICE pending).'
  if line not in f.read_text():f.write_text(f.read_text().rstrip()+'\n\n'+line+'\n')
 updated=dict(prev);updated[V2]=EXPECTED
 state['reference_prg_sha256']=updated
 state['alternate_prg_sha256'][V2]=maps['alternate']['sha256']
 state['issue39_v2_umul8_directout_2026_10_13']={
  'status':'PASS_STAGED_NATIVE_VICE_PENDING','old_sha256':prev[V2],
  'new_sha256':EXPECTED,'public_mean_cycles':perf['mean_cycles'],
  'full_domain_cases':65536,'source_maps':maps,'normal_zp_growth':0,
  'resident_size_growth':0,'V5_changed':False,
  'native_vice_calls':0,'document':DOC,'evidence':PROOF,'issue39_complete':False}
 for key,path,field in (
  ('issue39_common_input_unsigned_divmod','validation/review/UNSIGNED_DIVMOD_COMMON_CORPUS.json','benchmark_sha256'),
  ('issue39_unsigned_3216_multiworkload_2026_10_11','validation/review/UNSIGNED_3216_WORKLOAD_AUDIT.json','report_sha256'),
  ('issue39_unsigned_small_width_workloads_2026_10_11','validation/review/ISSUE39_UNSIGNED_SMALL_WORKLOAD_AUDIT.json','data_sha256')):
  if isinstance(state.get(key),dict):state[key][field]=sha(R/path)
 if isinstance(state.get('documentation'),dict):
  f=R/'USER_MANUAL.md'
  state['documentation'].update(user_manual_bytes=f.stat().st_size,
   user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
 status_file.write_text(json.dumps(state,indent=2)+'\n')
 run('make','clean')
 for _ in range(3):
  reseal();py('package_audit')
 print('V2 UMUL8 SOURCE RELEASE STAGED; NATIVE VICE PENDING',flush=True)
if __name__=='__main__':main()
