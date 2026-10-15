#!/usr/bin/env python3
"""Seal Issue144 22-byte all-domain quotient-complete 32/16 narrow-N opt-in.

The uniform-full-width slowdown is intentionally retained in the public
record: it is not a general performance promotion or API replacement.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from stage_issue39_v1_3216_ool_release import reseal
from validate_unsigned_division import PROFILES
SRC='optional/issue144_u32_16_narrow_guard/guard.asm'
MODEL='validation/review/ISSUE144_U32DIV32_16_NARROW_N_RESEARCH.json'
VICE='validation/review/ISSUE144_U32DIV32_16_NARROW_GUARD_NATIVE_VICE.json'
DOC='docs/ISSUE144_UNSIGNED32_16_NARROW_NUMERATOR_GUARD_2026-10-15.md'
STAMP='2026-10-15 ISSUE144 UNSIGNED 32/16 FULL Q R NARROW NUMERATOR OPTIN'
OPS=('MATH_UDIV32_16','MATH_UMOD32_16')
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 model,native=read(MODEL),read(VICE)
 state=read('RELEASE_STATUS.json')
 assert model['status']=='PASS_FULL_QR_C_ALL_PROFILES_WORKLOAD_DEPENDENT'
 assert native['status']=='PASS_NATIVE_ALL_FIVE_FULL_QR_C_NARROW_GUARD'
 assert model['paired_cpu_calls']==12800 and model['baseline_and_candidate_cpu_calls']==25600
 assert native['native_old_and_candidate_calls']==480
 assert model['code_bytes']==native['code_bytes']==22
 assert model['source_sha256']==native['source_sha256']==sha(SRC)
 assert set(model['profiles'])==set(native['profiles'])==set(PROFILES)
 prior_prg=dict(state['reference_prg_sha256'])
 prior_reu=dict(state.get('reference_reu_sha256',{}))
 ops_table=[];metrics={}
 for p in PROFILES:
  assert set(model['profiles'][p])==set(native['profiles'][p])==set(OPS)
  metrics[p]={}
  for op in OPS:
   a=model['profiles'][p][op]
   assert set(a)=={'uniform','small10pct','small50pct','small100pct','q0q1'}
   assert sum(q['cases'] for q in a.values())==1280
   assert all(native['profiles'][p][op][k]==24 for k in ('baseline_native_calls','candidate_native_calls'))
   assert native['profiles'][p][op]['complete_Q32_R16_C_inputs_stack_equal']
   uniform=a['uniform']['paired_savings_cycles']
   assert uniform['mean']==-14+(3 if op=='MATH_UMOD32_16' else 0)
   assert uniform['min']==uniform['max']==uniform['mean']
   assert a['small10pct']['saved_mean']>0
   assert a['small50pct']['saved_mean']>a['small10pct']['saved_mean']
   assert a['small100pct']['saved_mean']>a['small50pct']['saved_mean']
   for kind,row in a.items():
    assert row['cases']==256
    assert row['saved_min']<=row['saved_mean']<=row['saved_max']
   metrics[p][op]={kind:round(row['saved_mean'],6) for kind,row in a.items()}
   ops_table.append('| '+p+' | '+op.replace('MATH_','')+' | '+ ' | '.join(f"{a[k]['saved_mean']:.2f}" for k in ('uniform','small10pct','small50pct','small100pct','q0q1'))+' |')
  assert sha(p+'/resident/math_'+p+'_game_math.prg')==prior_prg[p]
 lines=[
  '# Issue144 B: 22-byte guarded 32÷16 unsigned full-output Pareto option',
  '',
  '**Correct on the entire unsigned 32-bit numerator / 16-bit divisor domain.**',
  '**Not a default performance optimization.** This opt-in dispatches to',
  'existing MATH_UDIV16 when the upper numerator word is zero, clearing',
  'both upper quotient bytes first. Otherwise it dispatches to the',
  'original MATH_UDIV32_16. In either case output is the same full Q32,',
  'R16, C including the original D16=0 divide-by-zero contract.',
  'The ordinary public MATH_UMOD32_16 alias returns a quotient too:',
  'this fast path preserves that full output, **not** remainder-only.',
  '',
  '## Same-input public-call CPU-model savings in cycles',
  '',
  'Positive values mean faster. Negative values mean SLOWER.',
  'Uniform means pseudorandom full-width N32; small10/50/100pct',
  'means a controlled fraction of numerators have zero upper word.',
  'All workloads also include explicitly seeded D=0 cases.',
  '',
  '| Profile | Comparable API | Uniform | Small 10% | Small 50% | Small 100% | Quotient 0/1 |',
  '|---|---|---:|---:|---:|---:|---:|',*ops_table,'',
  'Each workload has 256 fixed-seed identical operand pairs/profile/API,',
  '**12,800 paired comparisons / 25,600 baseline+candidate CPU calls**.',
  'Each pair passes complete Q32, R16, carry, unchanged input N/D,',
  'decimal flag cleared and balanced stack. Both signed-looking top-bit',
  'and divisor-zero inputs are included. No new normal zero page.',
  'Native real x64sc: **480 baseline+guard calls across V1–V5**',
  'pass exact Q/R/C, inputs and stack, including D=0 and full N32.',
  'Native CPU cycles are **not** measured.',
  '',
  '### Performance threshold and calling contract',
  '',
  'For fully uniform full-width numerators, the 22-byte guard',
  'costs **14 extra CPU-model cycles/call** compared with public UDIV32_16,',
  'or 11 extra versus UMOD32_16. It must NOT be installed as the default.',
  'It becomes useful for workloads with enough known-narrow N32:',
  '10% narrow in the measured 256-case mixtures saved ~21–29 cycles/call',
  'for UDIV and ~24–32 for UMOD, while always-narrow saved',
  '~349–446 (UDIV) and ~352–449 (UMOD). These are workload-specific.',
  'The routine is a direct callable $0C80 source example. The application',
  'must verify $0C80..$0C95 is actually free; the library does not reserve it.',
  'The caller can JSR the optional address, or select this source in a',
  'custom builder and measure its actual application-specific input mix.',
  '',
  '**A, X, Y and N/Z/V are volatile under the documented public ABI.**',
  'They can differ between the original full-width producer and UDIV16.',
  'A program relying on exact X/Y or N/Z/V values (despite the documented',
  'volatile contract) must NOT substitute this path. The CPU proof',
  'counts these differences transparently. Carry, Q/R, inputs and stack',
  'are exact. Do not use reentrantly or with overlapping IRQ/NMI math:',
  'the helper reuses normal resident ZP, self-modifying state and tables.',
  'Call MATH_INIT as required by the resident profile. No new REU data.',
  '',
  'Source: '+SRC,
  'Same-input reproducible benchmark: tools/issue144_u32div_smallnumerator_screen.py',
  'Native VICE harness: tools/native_issue144_u32_16_narrow_guard.py',
  'CPU proof: '+MODEL,
  'Native proof: '+VICE,
  'Normal five resident PRGs, REUs, public symbol addresses, normal',
  'zero-page usage and regular PERFORMANCE leaderboard remain unchanged.',
  'No private OptiSearch generator source included.',
 ]
 doc=R/DOC;doc.parent.mkdir(parents=True,exist_ok=True)
 doc.write_text('\n'.join(lines)+'\n')
 (R/'optional/issue144_u32_16_narrow_guard/README.md').write_text('# Full-output signed-agnostic unsigned 32÷16 narrow-numerator option\n\nSee ../../'+DOC+'; **slower on uniformly full-width inputs**.\n')
 state['issue144_unsigned32_16_narrow_guard_full_qr_2026_10_15']={
  'status':'PASS_MODEL_NATIVE_WORKLOAD_SPECIALIST_NOT_PROMOTED',
  'all_numerators_valid':True,'two_apis_qualified':list(OPS),
  'paired_model_calls':12800,'native_original_candidate_calls':480,
  'extra_normal_ZP':0,'code_bytes':22,'narrow_guard_full_width_regression_cycles':14,
  'A_X_Y_N_Z_V_volatile_and_can_differ':True,
  'ordinary_production_PRGs_REUs_unchanged':True,
  'native_cycles_measured':False,'source':SRC,'documentation':DOC,'CPU_proof':MODEL,'VICE_proof':VICE,
  'workload_mean_cycle_savings':metrics}
 (R/'RELEASE_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
 note=(STAMP+'\n- Source-only 22-byte all-input UDIV32_16/UMOD32_16 full-Q/R/C guarded narrow-numerator option: 12,800 same-input paired CPU model cases and 480 native x64sc calls PASS. Saves ~21–32 cycles on 10% narrow workload (V1–V5) but COSTS 14/11 cycles per uniform full-width call; deliberately not a default promotion. Documented volatile X/Y/NZV may differ; no shipped resident PRGs, REUs, ordinary ZP/ABI or PERFORMANCE change. '+DOC+'\n\n')
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  path=R/name
  if STAMP not in path.read_text():path.write_text(note+path.read_text())
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 assert all(sha(p+'/resident/math_'+p+'_game_math.prg')==value for p,value in prior_prg.items())
 assert dict(read('RELEASE_STATUS.json').get('reference_reu_sha256',{}))==prior_reu
 print('ISSUE144 22B UDIV32_16 / UMOD32_16 WORKLOAD-PARETO SOURCE AND RELEASE SEALED')
if __name__=='__main__':main()
