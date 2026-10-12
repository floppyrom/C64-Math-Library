#!/usr/bin/env python3
"""Seal the 68-byte writable-RAM standalone candidate and honest current release A/B.

No resident or public leaderboard binary changes. Archive the tested complete
public-entry A/B and standalone two-map code-integrity results with SHA pins.
"""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]
B='validation/review/ISSUE39_V1_24BY8_SMC_VS_61_PAIRED.json'
P='validation/review/ISSUE39_V1_24BY8_SMC_PORTABLE.json'
DOC='docs/ISSUE39_V1_UDIV24_ACCUMULATOR_SMC_SCREEN_2026-10-12.md'
V1='cdc2ca502d664055f896d7ad1601e8dd994b61be33e24bde3e25fc0dcbee1cdd'
TAG='2026-10-12 ISSUE39 V1 24/8 RAM SELF-MOD SPECIALIST CURRENT-61-SCREEN AND PORTABLE SOURCE'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(*argv):subprocess.run([str(x) for x in argv],cwd=R,check=True)
def seal():
 fs=sorted((p for p in R.rglob('*') if p.is_file()
   and '.git' not in p.parts and '__pycache__' not in p.parts and p.name!='SHA256SUMS.txt'),
   key=lambda p:str(p.relative_to(R)))
 (R/'SHA256SUMS.txt').write_text(''.join(sha(p)+'  '+str(p.relative_to(R))+'\n' for p in fs))
def main():
 a=json.loads(Path(sys.argv[1]).read_text())
 p=json.loads(Path(sys.argv[2]).read_text())
 assert sha(R/'v1_balanced/resident/math_v1_balanced_game_math.prg')==V1
 assert a['status']=='PASS' and a['original_v1_sha256']==V1
 assert a['old_core_bytes']==61 and a['new_core_bytes']==68
 assert a['paired_machine_calls']==48388 and a['regressions']==0
 assert a['normal_zp_growth']==0 and a['stack_growth']==0 and not a['abi_changed']
 assert p['status']=='PASS' and p['full_calls']==6344
 assert p['core_bytes']==68 and p['core_normal_zp']==0
 assert set(p['maps'])=={'8000','830F'} and p['failures']==0
 summaries={}
 for op,old_mean,new_mean in (('MATH_UDIV24',166.19019566589523,165.228277),
                               ('MATH_UMOD24',234.43335479716677,231.489375)):
  groups=a['routines'][op]
  canonical=groups['canonical'];target=groups['full_n24_d8']
  assert canonical['slower']==0 and abs(canonical['before_mean']-old_mean)<1e-9
  assert abs(canonical['after_mean']-new_mean)<0.0000015
  assert target['cases']==4080 and target['faster']==4080 and target['slower']==0
  assert abs(target['before_mean']-976.35)<1e-8
  assert abs(target['after_mean']-927.9343137254902)<0.000003
  summaries[op]=canonical
 for name,record in ((B,a),(P,p)):
  dest=R/name;dest.parent.mkdir(parents=True,exist_ok=True)
  dest.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
 docs=f"""# Issue #39: 68-byte RAM self-modifying 24÷8 specialist vs the released 61-byte core

**2026-10-12 — SCREENING-ONLY, not a resident replacement.** Rebuilt the
merged V1 PR #81 source-backed resident at SHA256 {V1} and compared an
in-memory copy replacing *only* the original $1D00 84-byte code island
with the optional 68-byte self-modifying candidate. The shipped 61-byte
non-self-modifying source, every profile PRG and public ABI remain unchanged.

The specialist caches D0 in two instruction operands (\`CMP #imm\` and
\`SBC #imm\`) once per call. Its loop then avoids repeated absolute D0 reads.
This is attractive for a C64 game/demo that controls **writable executable
RAM**, but **unsafe from ROM, non-reentrant, and dependent on caller ownership**.
Its precondition is exactly N2>0, D1=D2=0 and 0<D0<256; this code alone is
**not** a generic 24÷24 division/modulo routine and does not guard D=0.

| Full public-entry corpus | Released 61-byte code | RAM-only 68-byte | Cases |
|---|---:|---:|---:|
| UDIV24 canonical | {summaries['MATH_UDIV24']['before_mean']:.6f} | {summaries['MATH_UDIV24']['after_mean']:.6f} | {summaries['MATH_UDIV24']['cases']} |
| UMOD24 canonical | {summaries['MATH_UMOD24']['before_mean']:.6f} | {summaries['MATH_UMOD24']['after_mean']:.6f} | {summaries['MATH_UMOD24']['cases']} |
| 24/8 N2>0 stress (each API) | 976.350000 | 927.934314 | 4,080 |

The paired research screen ran **48,388 full public-entry 6502 executions**,
checking Q/R/C, unchanged N/D, Q3/R3 sentinels and stack, with **no incorrect
or slower comparisons**, including all seven fixed workload classes and
controls for wide divisors and N2=0. The narrow-divisor stress improves by
48.415686 cycles per input in that specific distribution. These are
**emulated CPU cycle counts**, not VIC-bus-inclusive native measurements.
Earlier separate native x64sc verification covered 128 *isolated core calls*;
no full-resident native validation or native cycle timing of the 68-byte
self-modifying alternative is claimed.

**Independently liftable source:** \`routines/standalone_lab/portable/div_u24_by_u8_selfmod.asm\`.
Its \`KERNEL_CODE\`, \`MATH_N\`, \`MATH_D\`, \`MATH_Q\`, \`MATH_R\` origins
are source constants you can change to disjoint writable RAM. The portable
proof checks **6,344 complete calls at $8000 and unaligned $830F**, including
two self-patched instruction operands and absence of other code writes, with
no normal ZP and no additional stack frame. The 68-byte routine is an optional
specialist; no 24/24 caller can invoke it unconditionally.

**Source/evidence:** \`tools/candidates/issue39_v1_24by8_accumulator_selfmod.asm\`,
\`tools/screen_issue39_v1_24by8_accumulator_selfmod.py\`,
\`tools/verify_issue39_v1_24by8_accumulator_selfmod_portable.py\`,
\`{B}\`, and \`{P}\`.

**Decision:** preserve BOTH the shipping 61-byte non-SMC routine and
liftable 68-byte SMC alternative. Do not call this a universal replacement,
misrepresent the number of code bytes, or close the unsigned DIV/MOD stage
of issue #39. Attribution: a manual C64ML optimization of the shared
short-divisor architecture from Repose-derived code; does not redistribute
private OptiSearch software.
"""
 (R/DOC).write_text(docs)
 f=R/'routines/standalone_lab/CANDIDATE_BACKLOG.csv'
 with f.open(newline='') as h:rows=list(csv.DictReader(h))
 key='udiv24_d8_accumulator_smc'
 if not any(x['identifier']==key for x in rows):
  rows.append({'identifier':key,
    'source':'portable/div_u24_by_u8_selfmod.asm',
    'status':'public_48388_paired_plus_6344_portable_2map',
    'standalone_finding':'68B_RAM_SMC_927.934_D8_stress_vs_61B_976.350',
    'resident_decision':'no_unconditional_promotion_ROM_nonreentrant',
    'follow_up':'optional_24by8_RAM_specialist_gate_required'})
 with f.open('w',newline='') as h:
  writer=csv.DictWriter(h,fieldnames=list(rows[0]),lineterminator='\n')
  writer.writeheader();writer.writerows(rows)
 link='- [68-byte writable-RAM SMC 24÷8 specialist](div_u24_by_u8_selfmod.asm): code is independently usable with N2>0, D1=D2=0, D0>0, but not ROM-safe or re-entrant; 6,344 paired-mapped source calls tested. See [current-61-vs-SMC proof](../../../'+DOC+').'
 f=R/'routines/standalone_lab/portable/README.md'
 if link not in f.read_text():f.write_text(f.read_text().rstrip()+'\n\n'+link+'\n')
 ln='- Issue #39 published SMC specialist vs 61-byte V1 resident: '+DOC+'. The 68-byte RAM-only routine remains independent and is not shipped in V1–V5.'
 for name in ('README.md','USER_MANUAL.md'):
  f=R/name
  if ln not in f.read_text():f.write_text(f.read_text().rstrip()+'\n\n'+ln+'\n')
 log=f"""{TAG}
- Source-backed 68-byte writable-RAM/self-modifying optional V1 24/8 producer tested against actual released 61-byte core, not the older PR78 69-byte baseline. 48,388 full public 6502 old/new calls and 6,344 independent two-map standalone calls pass, zero arithmetic/flag/input/stack errors or slower pairs.
- Canonical UDIV24 166.190196->{summaries['MATH_UDIV24']['after_mean']:.6f}, UMOD24 234.433355->{summaries['MATH_UMOD24']['after_mean']:.6f}; 4080-pair N24/D8 976.350000->927.934314. Retain in standalone portfolio, **NOT** shipped resident, requires writable RAM/exclusive non-reentrant code and N2>0,D1=D2=0,D0>0. Both changelogs, research evidence, catalog, documentation, SHA256SUMS updated; no profile binary changes. Issue #39 stays OPEN. {DOC}
"""
 for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
  f=R/name
  if TAG not in f.read_text():f.write_text(log+'\n'+f.read_text())
 status=R/'RELEASE_STATUS.json';st=json.loads(status.read_text())
 assert st['reference_prg_sha256']['v1_balanced']==V1
 st['issue39_v1_24by8_ram_smc_specialist_2026_10_12']={
  'status':'PASS_RESEARCH_ONLY_NOT_RESIDENT','documentation':DOC,
  'resident_61_sha256':V1,'paired_public_calls':a['paired_machine_calls'],
  'portable_standalone_calls':p['full_calls'],'paired_regressions':a['regressions'],
  'smc_code_bytes':68,'released_code_bytes':61,
  'normal_zp_growth':0,'stack_growth':0,
  'evidence':{B:sha(R/B),P:sha(R/P)},
  'official_candidate_means':{op:summaries[op]['after_mean'] for op in summaries},
  'installed_binary_changed':False,'unsigned_family_complete':False}
 if isinstance(st.get('documentation'),dict):
  f=R/'USER_MANUAL.md'
  st['documentation'].update(user_manual_bytes=f.stat().st_size,
    user_manual_lines=len(f.read_text().splitlines()),user_manual_sha256=sha(f))
 status.write_text(json.dumps(st,indent=2)+'\n')
 run('make','clean')
 for _ in range(3):
  seal();run(sys.executable,'tools/package_audit.py')
 run(sys.executable,'tools/validate_public_catalog.py')
 run(sys.executable,'tools/validate_standalone_sources.py')
 assert sha(R/'v1_balanced/resident/math_v1_balanced_game_math.prg')==V1
 print('RAM SELF-MOD DIVMOD RESEARCH PUBLICATION PASS; RESIDENT UNCHANGED',flush=True)
if __name__=='__main__':main()
