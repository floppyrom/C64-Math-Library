#!/usr/bin/env python3
"""One-shot issue39 publication: protect fastest-profile rankings from mixed seeds."""
from pathlib import Path
import hashlib,json
from common_corpus_ranking import EXPECTED, load_common, REPORT
ROOT=Path(__file__).resolve().parents[1]
d=load_common(ROOT)

def rewrite_table():
    f=ROOT/'PERFORMANCE.md'; lines=f.read_text().splitlines()
    for name in EXPECTED:
        matches=[i for i,s in enumerate(lines) if s.startswith('| `'+name+'` |')]
        assert len(matches)==1,(name,matches)
        i=matches[0]; parts=lines[i].split('|')
        assert len(parts)==9,(name,len(parts))
        for j,profile in enumerate(d['profile_order']):
            parts[j+3]=f" {d['routines'][name]['metrics'][profile]['mean_cycles']:.6f} "
        lines[i]='|'.join(parts)
    heading='## Shipped profile means'
    disclaimer=(
      '**Benchmark basis:** The unsigned DIV/MOD rows (UDIV8/16/24/32_16/32_32, '
      'UMOD counterparts and UDIV16_SHL8) now use **identical input pairs for all five profiles**. '
      'These common-corpus averages are reproducible but workload-dependent: see '
      '[the same-input results](benchmarks/UNSIGNED_COMMON_PROFILE_RESULTS.csv) '
      'for per-profile p95/worst-case, and the '
      '[audit methodology](docs/ISSUE39_BENCHMARK_COMPARABILITY_AUDIT_2026-10-11.md). '
      'The remaining published routine rows retain their existing distinct benchmark corpora '
      'and should not be treated as automatically comparable until independently certified. '
      'For V3/V4 REU-assisted functions, instruction cycles exclude external DMA/bus wait time.**'
    )
    # Link under the fastest-profile paragraph, no repeated disclaimer on rerun.
    marker='**Benchmark basis:** The unsigned DIV/MOD rows'
    if marker not in '\n'.join(lines):
        idx=next(i for i,s in enumerate(lines) if s.startswith(heading))
        lines[idx:idx]=[disclaimer,'']
    f.write_text('\n'.join(lines)+'\n')

rewrite_table()
f=ROOT/'benchmarks/README.md';text=f.read_text()
needle='- [`UNSIGNED_COMMON_PROFILE_RESULTS.csv`](UNSIGNED_COMMON_PROFILE_RESULTS.csv)'
if needle not in text:
    text=text.replace('The human-readable summary',needle+': 55 apples-to-apples cross-profile observations (11 unsigned APIs × 5 profiles), deterministic identical inputs, with p95/worst-case cycles and SHA-256 case/provenance hashes. Ranking winners for these 11 APIs in `BEST_PROFILE_RESULTS.csv` now use this comparable basis, not the old different-seed profile means.\n\nThe human-readable summary')
    text+='\n**Important:** `PUBLIC_PROFILE_RESULTS.csv` and consolidated legacy tables retain the independent per-profile validation seeds. Their numerical differences are not proof of faster code. Workload class, call frequency, ZP, and external REU DMA costs still matter.\n'
    f.write_text(text)
f=ROOT/'README.md';txt=f.read_text()
marker='Issue #39 same-input performance ranking audit'
if marker not in txt:
    f.write_text(txt.rstrip()+'\n\n- '+marker+': [methodology](docs/ISSUE39_BENCHMARK_COMPARABILITY_AUDIT_2026-10-11.md), [profile comparison](benchmarks/UNSIGNED_COMMON_PROFILE_RESULTS.csv). Unsigned `BEST_PROFILE_RESULTS.csv` entries are now based on matching operands.\n')
f=ROOT/'USER_MANUAL.md';txt=f.read_text()
if marker not in txt:
    f.write_text(txt.rstrip()+'\n\n- '+marker+': use common operands and workload classes before deciding which fixed profile is fastest; see `benchmarks/UNSIGNED_COMMON_PROFILE_RESULTS.csv`. V1 24-bit heavy quotient tails differ markedly from V2–V5, and REU cycle counts do not include DMA bus time.\n')
marker='2026-10-11 ISSUE39 COMMON-INPUT UNSIGNED DIVMOD RANKING AUDIT'
entry=f'''{marker}
- Corrects a benchmark-methodology issue: the legacy unsigned family validator deliberately varies random input seeds per profile, making its individual cycle means unsuitable for direct V1–V5 ranking.
- Adds a separate 136,335-call common-input machine-code audit covering 11 public unsigned DIV/MOD APIs and all V1–V5 reference residents, with result/carry/input preservation checks and workload-class, p95, max, mean timings.
- Changes `benchmarks/BEST_PROFILE_RESULTS.csv` to choose winners using identical-input data for these 11 routines, while preserving legacy independent validation/performance rows for extra correctness coverage.
- Publishes `benchmarks/UNSIGNED_COMMON_PROFILE_RESULTS.csv`, a permanent generator and verification gate, documentation, performance table correction, source SHA and corpus fingerprints.
- V1 UDIV24 slow paths are genuine when quotient >255: V1 2,098.8 vs V2 859.9 mean on that slice. In contrast V1 UDIV16 156.348 vs V2–V5 161.761, demonstrating workload-dependent ranking. V3/V4 UDIV24 and UMOD24 cycle vectors match V2 on identical inputs.
- No arithmetic routines or public ABI changed; unsigned family #39 remains open pending remaining architecture audits and no-gain decisions.
- See `docs/ISSUE39_BENCHMARK_COMPARABILITY_AUDIT_2026-10-11.md`.
'''
for fn in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
    f=ROOT/fn
    if marker not in f.read_text():f.write_text(entry+'\n'+f.read_text())
status=ROOT/'RELEASE_STATUS.json';out=json.loads(status.read_text());out['date']='2026-10-11'
out['issue39_common_input_unsigned_divmod']={'status':'PASS','validated_calls':d['total_calls'],
   'routine_count':len(d['routines']),'profile_count':len(d['profile_order']),
   'public_abi_changed':False,'arithmetic_binaries_changed':False,
   'documentation':'docs/ISSUE39_BENCHMARK_COMPARABILITY_AUDIT_2026-10-11.md',
   'benchmark_proof':REPORT,'benchmark_sha256':hashlib.sha256((ROOT/REPORT).read_bytes()).hexdigest(),
   'common_best_profile_ranking':True,'unsigned_family_completed':False}
if isinstance(out.get('documentation'),dict):
    p=ROOT/'USER_MANUAL.md';out['documentation'].update(user_manual_bytes=p.stat().st_size,user_manual_lines=len(p.read_text().splitlines()),user_manual_sha256=hashlib.sha256(p.read_bytes()).hexdigest())
status.write_text(json.dumps(out,indent=2)+'\n')
print('ISSUE39 COMMON-CORPUS PUBLICATION PASS',d['total_calls'])
