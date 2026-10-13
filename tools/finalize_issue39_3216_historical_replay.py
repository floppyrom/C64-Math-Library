#!/usr/bin/env python3
"""Release-seal exact historical replay adaptations following PR100 source promotion."""
from pathlib import Path
import json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from stage_issue39_v1_3216_ool_release import reseal,sha,DOC
V1='9af44deda4a1527a0ea5ecc09a48e1ec4927a45099f7b2e26ced0f618274c0a4'
V2='c3c0898bc61a9836e7f58d1b51088ccc644613bf68d9e4199aa1243c4f164c84'
V5='0662a9644ee4ebb6df7a06f9c77a40ffb5308b69ecd5e6bc9c7d6250b5bd5750'
def main():
    s=ROOT/'RELEASE_STATUS.json'
    state=json.loads(s.read_text())
    assert state['reference_prg_sha256']['v1_balanced']==V1
    assert state['reference_prg_sha256']['v2_pareto_fast']==V2
    assert state['reference_prg_sha256']['v5_hybrid_lowzp']==V5
    assert state['issue39_v1_3216_ool_zero_source_production_2026_10_13']['native_vice_source_built_calls']==384
    marker='2026-10-13 ISSUE39 HISTORICAL DIV/MOD REPLAY PINNING AFTER V1 32/16 SOURCE PROMOTION'
    text=(
        marker+'\n'
        '- Recovered exact prior PR99 V1 resident bytes from SHA-pinned current V1 by reversing ONLY'
        ' the new 7-byte cold handler, 111-byte 32/16 continuation displacement and unroll return JMP;'
        ' verify reverse SHA equals immutable prior main before playing historical PR78/PR81 24/8 proofs.\n'
        '- Updated V2 UMOD8 history against exact SHA-pinned current V2, restoring only the 104 changed'
        ' wrapper/helper bytes for the original exhaustive 65536-case paired A/B. V5 unchanged-source'
        ' check short-circuits before invoking historical PR71 inverse. Historical tests and general'
        ' profile correctness remain independent; issue #39 OPEN. '+DOC+'\n\n'
    )
    for p in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
        f=ROOT/p
        if marker not in f.read_text():f.write_text(text+f.read_text())
    p=ROOT/DOC
    data=p.read_text()
    heading='\n## Historical proof compatibility after source promotion\n'
    if heading not in data:
        data+=(heading+
          'Older 24/8 and UMOD8 replay scripts previously assumed only archived resident SHA values.'
          ' The V1 24/8 replay now reverses the **exact known** V1 32/16 transformation and asserts'
          ' the recovered pre-PR100 SHA before running its original comparisons. The V2 UMOD8'
          ' replay uses the SHA-pinned current V2 resident, reverses only the original 104-byte'
          ' UMOD8 guard, and requires all other bytes to match. The V5 unchanged-source'
          ' comparison short-circuits, avoiding unnecessary historical PR71 inversion.'
          ' These changes do not modify production arithmetic or relax arbitrary-hash checks.\n')
        p.write_text(data)
    state['issue39_v1_3216_historical_replay_2026_10_13']={
        'status':'PASS_SHA_PINNED_HISTORICAL_REPLAY',
        'V1_current_sha256':V1,'V2_current_sha256':V2,'V5_current_sha256':V5,
        'previous_V1_sha256':'2567dccbc4e01f3d606e80126c8150c58e4f30b8b726ff38e116c6aaec644178',
        'inverse_strict':True,'production_arithmetic_changed':False,
        'issue39_unsigned_family_complete':False}
    s.write_text(json.dumps(state,indent=2)+'\n')
    for _ in range(2):
        reseal()
        subprocess.run([sys.executable,str(ROOT/'tools/package_audit.py')],cwd=ROOT,check=True)
    reseal()
    subprocess.run([sys.executable,str(ROOT/'tools/package_audit.py')],cwd=ROOT,check=True)
    print('ISSUE39 PR100 HISTORICAL REPLAY AND RELEASE PACKAGE SEALED',flush=True)
if __name__=='__main__':main()
