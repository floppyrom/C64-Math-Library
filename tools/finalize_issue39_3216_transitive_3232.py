#!/usr/bin/env python3
"""Publish exact transitive V1 32/32 cycle results after source V1 32/16 improvement.

Reads certified comparable corpus, never mixes profile-seeded cycle vectors
with identical-input rankings. Rebuilds two published human-readable rows and
the V5 baseline comparison. Does not touch resident arithmetic or REU images.
"""
from pathlib import Path
import csv,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from common_corpus_ranking import load_common
from stage_issue39_v1_3216_ool_release import reseal,sha
OPS=('MATH_UDIV32_32','MATH_UMOD32_32')
EXACT={'MATH_UDIV32_32':(335.7508244778307,275.01319164529133,2729),
       'MATH_UMOD32_32':(399.55718475073314,299.582991202346,1705)}
BASE='9af44deda4a1527a0ea5ecc09a48e1ec4927a45099f7b2e26ced0f618274c0a4'
def main():
    status=R/'RELEASE_STATUS.json';j=json.loads(status.read_text())
    assert j['reference_prg_sha256']['v1_balanced']==BASE
    common=load_common(R);assert common['total_calls']==136335
    means={}
    for op,(v1,v5,n) in EXACT.items():
        r=common['routines'][op];assert r['cases_per_profile']==n
        assert abs(r['metrics']['v1_balanced']['mean_cycles']-v1)<1e-10
        assert abs(r['metrics']['v5_hybrid_lowzp']['mean_cycles']-v5)<1e-10
        means[op]={'v1':v1,'v5':v5,'cases':n}
    root=R/'PERFORMANCE.md';lines=root.read_text().splitlines()
    for op,(v1,v5,_) in EXACT.items():
        row=[i for i,s in enumerate(lines) if s.startswith('| '+chr(96)+op+chr(96)+' |')]
        assert len(row)==1,op
        cells=lines[row[0]].split('|')
        cells[3]=f' {v1:.6f} '
        cells[7]=f' {v5:.6f} '
        lines[row[0]]='|'.join(cells)
    root.write_text('\n'.join(lines)+'\n')
    p=R/'v5_hybrid_lowzp/HYBRID_PERFORMANCE.csv'
    with p.open(newline='') as f:rows=list(csv.DictReader(f))
    for op,(v1,v5,_) in EXACT.items():
        hit=[z for z in rows if z['routine']==op];assert len(hit)==1
        hit[0].update(v1_mean_cycles=f'{v1:.6f}',v5_mean_cycles=f'{v5:.6f}',
          improvement_percent=f'{(v1-v5)*100/v1:.6f}',
          provenance='2026-10-13 source-installed V1 32/16 transitive public 32/32 identical-input benchmark')
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    title='2026-10-13 ISSUE39 V1 32/16 TRANSITIVE 32/32 PERFORMANCE PUBLICATION'
    note=(title+'\n'
       '- Source V1 32/16 hot-path relocation also accelerates 32/32 fallback for a bounded class.'
       ' Under exact current same-input corpus, V1 UDIV32_32 mean 335.825577 -> 335.750824'
       ' and UMOD32_32 399.676833 -> 399.557185. V5 donor remains unchanged.'
       ' Updated PERFORMANCE.md, V5 HYBRID_PERFORMANCE.csv and SHA-pinned bound checks,'
       ' no production binary change. Keep issue #39 OPEN.\n\n')
    for path in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
        f=R/path
        if title not in f.read_text():f.write_text(note+f.read_text())
    d=R/'docs/ISSUE39_V1_3216_OOL_ZERO_PRODUCTION_2026-10-13.md'
    desc='\n## Transitive 32/32 public-entry timing\n\n'
    if desc not in d.read_text():
        lines=[desc,
          'The 32/32 public frontends still call the V1 32/16 continuation in some'
          ' bounded cases. On the identical-input audit, V1 UDIV32_32 changes'
          ' from 335.825577 to **335.750824** cycles (2,729 inputs),'
          ' and V1 UMOD32_32 from 399.676833 to **399.557185** (1,705 inputs).'
          ' These gains are not claimed for V5, which retains the V2 donor.'
          ' The historical QONE/Q23 source validators are pinned to these'
          ' exact per-image means.\n']
        d.write_text(d.read_text().rstrip()+'\n'+''.join(lines))
    j['issue39_v1_3216_ool_transitive_3232_2026_10_13']={
        'status':'PASS_COMPARABLE_SAME_INPUT_PUBLISHED',
        'means':means,'native_vice_for_3232_not_newly_measured':True,
        'V1_resident_changed':False,'unsigned_campaign_complete':False}
    status.write_text(json.dumps(j,indent=2)+'\n')
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,str(R/'tools/package_audit.py')],cwd=R,check=True)
    print('ISSUE39 V1 32/16 TRANSITIVE 32/32 PERFORMANCE RELEASE TABLES PASS',flush=True)
if __name__=='__main__':main()
