#!/usr/bin/env python3
"""Publish a no-unconditional-promotion decision for the Repose UMOD16 donor."""
from pathlib import Path
import csv,hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1]
E='validation/review/ISSUE39_UMOD16_BIASED_CURRENT_MAIN.json'
D='docs/ISSUE39_UMOD16_BIASED_CURRENT_MAIN_DECISION_2026-10-12.md'
TAG='2026-10-12 ISSUE39 UMOD16 BIASED OPTISEARCH DONOR CURRENT-MAIN SCREEN'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seal():
 fs=sorted((p for p in R.rglob('*') if p.is_file()
            and '.git' not in p.parts and '__pycache__' not in p.parts
            and p.name!='SHA256SUMS.txt'),key=lambda p:str(p.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.relative_to(R)}\n' for p in fs))
def main():
 src=Path(sys.argv[1]);assert src.exists()
 record=json.loads(src.read_text())
 assert record['status']=='PASS' and record['total_calls']==27280
 assert record['resident_changes'] is False
 assert record['corpus_size_per_profile']==1705
 assert record['extra_zp_bytes']==2 and record['nested_jsr_stack_bytes']==2
 profiles=('v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
 placements=('aligned_e000','unaligned_e108')
 for p in profiles:
  for k in placements:
   x=record['profiles'][p][k]
   assert x['cases']==1705 and x['slower']==1391 and x['faster']==314
   assert x['Q16_output_different_cases']==667
   assert abs(x['resident_mean']-198.60117302052785)<1e-8
   assert abs(x['standalone_mean']-185.82639296187682)<1e-8
 (R/E).parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(src,R/E)
 a=record['profiles']['v2_pareto_fast']['aligned_e000']
 edges=a['class_means']['edges'];random=a['class_means']['random']
 assert edges['count']==529 and random['count']==1024
 md=f"""# Issue #39: OptiSearch biased UMOD16 vs current V2–V5 residents

**12 October 2026. Decision: retain as a separate standalone specialist;
do not promote as the default resident.** This is an API/resource screen,
not a statement that the donor is mathematically incorrect.

The original Repose/OptiSearch `division.u16-biased-zp-stable-illegal`
donor, adapted for carry handling, is already published at
`routines/standalone_lab/portable/mod_u16_biased_carry.asm`.
This screen sources that same editable NMOS 6510 assembly, assembles
two RAM-backed copies at $E000/$E400 and $E108/$E500, allocates two
additional ZP bytes $70-$71, and compares against the actual V2,
V3, V4 and V5 `MATH_UMOD16` public entry images on **identical**
1,705 inputs per profile/placement: 27,280 complete 6502 calls.

All R16, carry including divide-by-zero, N/D input preservation and
SP oracle checks pass. **No resident binary was modified.**

| Input class | Inputs | Current resident cycles | Portable donor cycles |
|---|---:|---:|---:|
| All official pairs | 1,705 | {a['resident_mean']:.6f} | {a['standalone_mean']:.6f} |
| Structured edges | {edges['count']} | {edges['resident_mean']:.6f} | {edges['standalone_mean']:.6f} |
| Uniform random | {random['count']} | {random['resident_mean']:.6f} | {random['standalone_mean']:.6f} |
| Stress cases | 24 | {a['class_means']['stress']['resident_mean']:.6f} | {a['class_means']['stress']['standalone_mean']:.6f} |
| Divisor zero | 128 | {a['class_means']['zero']['resident_mean']:.6f} | {a['class_means']['zero']['standalone_mean']:.6f} |

The weighted overall mean improves **12.774780 cycles**, but
**1,391/1,705 tested inputs become slower**, including the vast majority
of random operands (resident 80.490234 vs donor 111.772461 cycles).
The donor is faster on 314 cases and tied on none. The existing public
Q16 buffer and donor Q16 buffer have different contents on **667**
cases per profile, so byte-identical current-program behavior is not
established. Whether Q16 is formally guaranteed by each remainder-only
profile is a separate ABI decision; do not silently equate these effects.

The donor requires **262 external code-RAM bytes, 2 additional ZP bytes
and an extra nested JSR frame (2 stack bytes)**. The two chosen external
placements only work on a C64 when RAM is actually visible under
$E000. These extra resources and memory banking were not accepted
into any fixed-profile contract or source-resident layout. Mini6502
instruction cycles exclude REU DMA and native VIC bus contention.

**Verdict:** useful independent Repose-generated standalone option;
not a universal speed or Pareto-record replacement for V2–V5.
The user can select it if workload is edge/narrow-divisor heavy and
the caller owns the extra RAM/ZP/stack. Further source synthesis would
need to preserve the target Q side effect where required, reduce the
random-input penalty, verify owned code space/ZP and undergo native
full-resident, relocation, mixed-call and five-profile release gates.

Permanent evidence: `{E}`. Reproduce:
`python3 tools/screen_issue39_umod16_biased_standalone.py --out /tmp/issue39_umod16_biased.json`.
The V1 UMOD16 alias is intentionally excluded because its
quotient-producing ABI differs. **Leave issue #39 open** until the
remaining unsigned DIV/MOD no-gain and width/profile screens are done.
"""
 (R/D).write_text(md)
 f=R/'routines/standalone_lab/CANDIDATE_BACKLOG.csv'
 with f.open(newline='') as stream:rows=list(csv.DictReader(stream))
 match=[r for r in rows if r['identifier']=='umod16_biased_carry']
 assert len(match)==1
 match[0]['status']='source_backed_27280_pair_profile_screen'
 match[0]['resident_decision']='not_default_1391_of_1705_slower_667_Q_differences'
 match[0]['follow_up']='ABI_compatible_random_latency_and_2ZP_262RAM_stack_budget'
 with f.open('w',newline='') as stream:
  w=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
  w.writeheader();w.writerows(rows)
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  p=R/name
  note=f"""{TAG}
- Independently re-screened Repose/OptiSearch standalone UMOD16 biased donor against current V2–V5 UMOD16 complete entries: 27,280 same-input emulator calls across two RAM layouts, exact remainder/carry, inputs and stack.
- Overall 198.601173→185.826393 cycle mean but 1,391/1,705 inputs slower, random input 80.490234→111.772461 and 667 Q16 differences; +262 code RAM, +2 ZP and nested JSR stack. Retain as a standalone specialist, NOT default resident replacement.
- Report {D}; no resident binaries, public performance rankings or stable ABI modified. Issue #39 remains open.
"""
  if TAG not in p.read_text():p.write_text(note+'\n'+p.read_text())
 p=R/'routines/standalone_lab/README.md'
 note=f'Current V2–V5 UMOD16 biased public-ABI/identical-input screen: [{D}](../../{D}). The 185.826-cycle corpus mean hides 1,391/1,705 slower cases and extra RAM/ZP/stack; no resident promotion.'
 if note not in p.read_text():p.write_text(p.read_text().rstrip()+'\n\n'+note+'\n')
 status=R/'RELEASE_STATUS.json';obj=json.loads(status.read_text())
 obj['issue39_umod16_biased_current_main_2026_10_12']={
  'status':'PASS_STANDALONE_NO_RESIDENT_PROMOTION','documentation':D,'evidence':E,
  'evidence_sha256':sha(R/E),'paired_emulator_calls':27280,
  'profiles_evaluated':list(profiles),'placements':list(placements),
  'mean_resident_cycles':a['resident_mean'],
  'mean_standalone_cycles':a['standalone_mean'],
  'inputs_slower':a['slower'],'Q16_output_different_cases':a['Q16_output_different_cases'],
  'resident_prgs_changed':False,'unsigned_family_complete':False}
 status.write_text(json.dumps(obj,indent=2)+'\n')
 subprocess.run(['make','clean'],cwd=R,check=True)
 for _ in range(3):
  seal();subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
 print('ISSUE39 UMOD16 BIASED PUBLICATION STAGED',sha(R/E),flush=True)
if __name__=='__main__':main()
