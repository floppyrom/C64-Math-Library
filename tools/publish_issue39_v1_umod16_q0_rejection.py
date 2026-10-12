#!/usr/bin/env python3
"""Publish and seal issue39's V1 UMOD16 strict-vs-loose negative candidate.

Runs only on isolated PR branch. No shipped source or machine code changes.
The test is first rerun to establish full deterministic public-ABI evidence.
"""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
DOC='docs/ISSUE39_V1_UMOD16_REPOSE_Q0_FRONTEND_REJECTION_2026-10-12.md'
AUDIT='validation/review/ISSUE39_V1_UMOD16_Q0_FASTPATH_REJECTED.json'
TAG='2026-10-12 ISSUE39 V1 UMOD16 OPTISEARCH Q0 ABI NO-GAIN'
def digest(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def py(name):
 print('RUN',name,flush=True)
 subprocess.run([sys.executable,'tools/'+name+'.py'],cwd=ROOT,check=True)
def checksum():
 fs=sorted((p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and p.name!='SHA256SUMS.txt'),key=lambda p:str(p.relative_to(ROOT)))
 (ROOT/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.relative_to(ROOT)}\n' for f in fs))
def main():
 original_hashes={p:digest(f'{p}/resident/math_{p}_game_math.prg') for p in ('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')}
 statep=ROOT/'RELEASE_STATUS.json';state=json.loads(statep.read_text())
 assert original_hashes==state['reference_prg_sha256'],'a source binary changed before evidence-only publication'
 py('screen_issue39_v1_umod16_q0_rejection')
 data=json.loads((ROOT/AUDIT).read_text())
 assert data['status']=='REJECT' and data['resident_files_modified'] is False
 assert data['resident_sha256']==original_hashes['v1_balanced']
 assert data['total_calls']==11259
 official=data['workloads']['official_shared_1705']
 assert official['cases']==1705
 loose=official['candidate']['loose'];strict=official['candidate']['strict']
 assert loose['q_mismatches']==768 and loose['r_c_errors']==0
 assert loose['mean_delta_cycles']<0
 assert strict['q_mismatches']==0 and strict['r_c_errors']==0 and strict['input_errors']==0
 assert strict['mean_delta_cycles']>0
 assert strict['slower']==1620 and strict['faster']==85
 doc=f"""# Issue #39 — V1 UMOD16 quotient-zero shortcut: API-complete no-gain screen

**12 October 2026** · **Decision: reject both experimental front ends.**
The unsigned DIV/MOD family remains open. No shipped routine bytes or source
are modified by this screen.

## Why this experiment matters

Following Repose's 11 October OptiSearch challenge, two manually designed,
ephemeral V1 modulo front ends were tested at the unchanged public
`MATH_UMOD16=$3220` entry, forwarding non-zero quotients to the existing
323-byte, shared V1 divider at $4200. The experimental code was placed only
in an *in-memory* copy of the unused $1E80 region; no resource ownership
claim or permanently free allocation is inferred from zero bytes alone.

The 34-byte **loose** variant returns correct remainder and carry on
quotient-zero inputs while omitting quotient writes. The 42-byte **strict**
variant writes Q16 and R16 as the current V1 alias does. V1's
`USER_MANUAL.md` describes `MATH_UMOD16` as a UDIV16 alias that produces
both Q and R. **Do not erase that existing V1 behavior merely to improve
a remainder-only benchmark.** V2–V5 use separately qualified remainder-only
modulo front ends in some profiles; their documented contracts and resource
envelopes must be evaluated individually, not assumed identical to V1.

## Public entry 6502 performance on the official identical-input corpus

Each variant was measured against the current merged PR #68 V1 resident,
SHA-256 `{original_hashes['v1_balanced']}`. All three variants received
**exactly 1,705 identical (N16,D16) pairs**.

| Candidate | Mean delta vs shipped V1 | Faster | Slower | Q output mismatches |
|---|---:|---:|---:|---:|
| Loose remainder-only | {loose['mean_delta_cycles']:+.6f} cycles | {loose['faster']} | {loose['slower']} | {loose['q_mismatches']} |
| Strict V1 Q16+R16 | {strict['mean_delta_cycles']:+.6f} cycles | {strict['faster']} | {strict['slower']} | 0 |

Negative deltas mean faster. Loose candidate remainder, carry, N and D were
correct on every sampled pair; it nevertheless violated the V1 quotient
side effect **768 times**. Strict candidate corrected every such output
difference, but averaged **{strict['mean_delta_cycles']:.6f} extra cycles**
and allocated eight more bytes than loose for the missing Q writes.

## Additional input classes and verdict

The executable screen also covers the seven fixed 256-pair workloads from
`tools/audit_issue39_unsigned_small_workloads.py`: uniform, small-divisor,
quotient-zero, quotient-one, quotient-2–7, power-of-two divisor, and divide
by zero. Total **11,259** original/loose/strict V1 public calls, including
768 unchanged `MATH_UDIV16` comparison calls. All strict arithmetic,
Q/R, carry, preserved-input, and out-of-range sentinel checks pass; this
is therefore a **performance/resource no-gain**, not an arithmetic failure.

The strict gate is slower on the quotient-zero workload too (mean
{data['workloads']['quotient_zero']['candidate']['strict']['mean_delta_cycles']:+.6f}
cycles), because correctly writing Q nullifies the nominal low-byte-copy
saving. Other quotient workloads also incur fallback dispatch penalties.
No public speed/size Pareto improvement exists in this tested architecture.

**OptiSearch context:** Repose's `umod16_biased` and `umod16_direct`
implementations were assessed separately and had success-case carry
violations under C64ML's public contract. The new screen is a *manual*
architecture derived from that finding, not a copied private OptiSearch
generator, and does not attribute the original package's cycles to itself.

The next credible unsigned family work must target the internal 16-bit
short-quotient arithmetic or the 24/32-bit quotient-class tails, and preserve
the fixed profile's actual public outputs, relocation and RAM ownership.
Report: `{AUDIT}`. Generator: `tools/screen_issue39_v1_umod16_q0_rejection.py`.
"""
 (ROOT/DOC).write_text(doc)
 blurb=f'- Issue #39 V1 UMOD16 OptiSearch-inspired q0 gate no-gain: [ABI and same-input rejection]({DOC}); current shipped division code unchanged.'
 for name in ('README.md','USER_MANUAL.md'):
  p=ROOT/name;s=p.read_text()
  if blurb not in s:p.write_text(s.rstrip()+'\n\n'+blurb+'\n')
 record=f"""{TAG}
- Rejected V1 UMOD16 remainder-only q=0 frontend under existing Q16+R16 alias contract. Hand-written 34-byte shortcut seems {abs(loose['mean_delta_cycles']):.6f} cycles faster on 1,705 shared inputs but leaves incorrect Q16 in 768 cases; compliant 42-byte variant is {strict['mean_delta_cycles']:.6f} cycles slower with 1,620 regressions and only 85 wins. Seven additional quotient-class workloads screened: 11,259 total public calls, strict output/flags/input exact, unchanged UDIV16. Repose's original binary not imported. No resident binaries or stable source changed, the unsigned family audit remains open. Details: {DOC}.
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  p=ROOT/name;s=p.read_text()
  if TAG not in s:p.write_text(record+'\n'+s)
 state=json.loads(statep.read_text())
 state['issue39_v1_umod16_q0_no_gain_2026_10_12']={
  'status':'REJECT','document':DOC,'evidence':AUDIT,
  'case_count_official':official['cases'],'total_public_emulator_calls':data['total_calls'],
  'loose_mean_delta':loose['mean_delta_cycles'],'loose_quotient_mismatches':loose['q_mismatches'],
  'strict_mean_delta':strict['mean_delta_cycles'],
  'strict_faster':strict['faster'],'strict_slower':strict['slower'],
  'new_resident_binaries':False,'unsigned_family_complete':False,
  'audit_sha256':digest(AUDIT),'screen_source_sha256':digest('tools/screen_issue39_v1_umod16_q0_rejection.py')
 }
 if isinstance(state.get('documentation'),dict):
  um=ROOT/'USER_MANUAL.md';state['documentation'].update(
   user_manual_bytes=um.stat().st_size,user_manual_lines=len(um.read_text().splitlines()),
   user_manual_sha256=hashlib.sha256(um.read_bytes()).hexdigest())
 statep.write_text(json.dumps(state,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=ROOT,check=True)
 for i in range(4):
  checksum();py('package_audit')
  if all(line.split('  ',1)[0]==digest(line.split('  ',1)[1]) for line in (ROOT/'SHA256SUMS.txt').read_text().splitlines()):break
 else:raise AssertionError('no stable package/checksum state')
 py('validate_public_catalog')
 assert all(digest(f'{p}/resident/math_{p}_game_math.prg')==h for p,h in original_hashes.items())
 checksum();py('package_audit')
 print('ISSUE39 V1 UMOD16 NEGATIVE AUDIT PUBLISHED AND SEALED: NO CODE CHANGE',flush=True)
if __name__=='__main__':main()
