#!/usr/bin/env python3
"""Stage independently verified V4 REU ISQRT32 exact 6-cycle peephole.

Optional reversible source only: never edit normal V4 PRG/REU images.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'tools'))
from stage_issue39_v1_3216_ool_release import reseal
from validate_unsigned_division import PROFILES
SRC='optional/issue144_v4_reu_isqrt_rotate6/v4_reu_16m.asm'
MODEL='validation/review/ISSUE144_V4_REU_ISQRT32_ROTATE6_MODEL.json'
VICE='validation/review/ISSUE144_V4_REU_ISQRT32_ROTATE6_NATIVE_VICE.json'
DOC='docs/ISSUE144_V4_REU_ISQRT32_ROTATE6_PARETO_2026-10-15.md'
STAMP='2026-10-15 ISSUE144 V4 REU ISQRT32 INPLACE ROTATE6 PARETO'
def read(path):return json.loads((R/path).read_text())
def sha(path):return hashlib.sha256((R/path).read_bytes()).hexdigest()
def main():
    model=read(MODEL);vice=read(VICE);release=read('RELEASE_STATUS.json')
    assert model['status']=='PASS_CPU_MODEL_V4_REU_ISQRT32_NO_EXTRA_RESOURCES'
    assert vice['status']=='PASS_REAL_NATIVE_VICE_V4_REU_ISQRT32_ROTATE6'
    assert model['canonical_corpus']==4130 and model['gain_cycles_on_every_input']==6
    assert vice['original_and_candidate_calls']==48
    assert vice['original_and_candidate_output_and_STATUS_BYTES_EQUAL']
    assert vice['real_16MiB_REU_image_loaded']
    assert model['enable_cycles']==66 and model['disable_cycles']==56
    assert model['source_installer_bytes']==88
    assert model['net_executable_bytes_growth']==0
    assert model['source_sha256']==sha(SRC)
    assert model['patch']==[
        {'address':'0xc90b','original':'0a'*6,'candidate':'4a6a6a9001ea'},
        {'address':'0xc924','original':'0a'*6,'candidate':'4a6a6a9001ea'},
    ]
    before=dict(release['reference_prg_sha256']);before_reu=dict(release.get('reference_reu_sha256',{}))
    assert set(before)==set(PROFILES)
    for p in PROFILES:
        assert sha(p+'/resident/math_'+p+'_game_math.prg')==before[p]
    doc=[
        '# Issue #144 C — V4 16-MiB REU ISQRT32 exact in-place rotate-six optimization',
        '',
        '**Full unsigned 32-bit radicand domain; original REU mapping and lookup data preserved.**',
        '',
        'V4 differs from non-REU ISQRT32 (PR #155): its $C8FC REU producer',
        'computes a REU address and performs a four-byte DMA before radix-4',
        'refinement. Two source-backed runs of **six ASL A instructions**',
        'at $C90B and $C924 follow `AND #$03` and compute `x << 6`.',
        'For x in 0..3, the exact six-byte in-place substitution is:',
        '',
        '```asm',
        'lsr a',
        'ror a',
        'ror a',
        'bcc +1   ; skip one-byte NOP, carry provably clear',
        'nop',
        '```',
        '',
        'This emits identical A/N/Z/C/V outputs and does not change X/Y.',
        'The branch is taken for all x in 0..3, producing the same address.',
        'Each substituted site executes in **9 rather than 12 cycles**;',
        'two sites yield a constant **6 CPU-model cycles saved/call**.',
        'Source opcode bytes are `4A 6A 6A 90 01 EA`, unchanged six-byte',
        'footprint per site, no extra production code/ZP/data/REU payload.',
        '',
        '## Public-call CPU-model performance on canonical identical inputs',
        '',
        '| Profile | Original mean | In-place optimized mean | Saved | Inputs |',
        '|---|---:|---:|---:|---:|',
        '| V4 16-MiB REU | %.6f | %.6f | 6.000000 | 4,130 |' %
        (model['before']['mean'],model['after']['mean']),
        '',
        'All 4,130 baseline/candidate comparisons pass exact root and',
        'unchanged four input bytes, C, X/Y, N/Z/V/D and SP; ordinary',
        'ISQRT16 calls were interleaved every 199 cases. Minimum and',
        'maximum paired saving are also exactly six cycles. The actual',
        'CPU model loads the original 16-MiB REU reference image.',
        'Native real x64sc loads the same 16-MiB REU image and compares',
        '**24 baseline plus 24 candidate executions**, identical roots',
        'and full PHP status bytes. Native/VIC-II/REU DMA wall time is',
        '**not measured or claimed to improve by exactly six cycles**.',
        '',
        '## Optional use and resource contract',
        '',
        'Use the per-profile 6510 BEGIN/END source under `optional`.',
        'Its example caller-owned $0D00 installer occupies 88 bytes;',
        'CPU-model entry costs **66 cycles BEGIN**, **56 END**, excluding',
        'any real caller JSR. If called as subroutines, setup/teardown',
        'with two JSRs costs ~134 cycles, so **23 or more calls**',
        'amortize the runtime patch. A custom builder may apply the same',
        'twelve byte substitutions at build-time with zero runtime',
        'setup cost, but must qualify the complete resident image.',
        'This source-only release does NOT modify the shipped resident.',
        '',
        'Require the exact V4 resident image, original 12 ASL bytes',
        'verified, writable RAM at $C90B/$C924, normal MATH_INIT,',
        'existing REU image and exclusive install/restore. Do NOT',
        'run any IRQ/NMI or concurrent math while patching executable',
        'code: 12 byte changes are not atomic. Check $0D00–$0D57',
        'really belongs to the application before loading installers.',
        'Original public entry $5E30 and normal resource budgets unchanged.',
        '',
        'Assembly: '+SRC,
        'Canonical CPU and restoration reproducer: tools/issue144_v4_reu_rotate6_peephole.py',
        'Native real x64sc/16-MiB REU reproducer: tools/native_issue144_v4_reu_rotate6.py',
        'Model proof: '+MODEL,
        'Native proof: '+VICE,
        'No private OptiSearch source is included.',
    ]
    (R/DOC).parent.mkdir(parents=True,exist_ok=True)
    (R/DOC).write_text('\n'.join(doc)+'\n')
    (R/'optional/issue144_v4_reu_isqrt_rotate6/README.md').write_text(
        '# V4 16MiB REU ISQRT32 rotate6 in-place optional optimization\n\n'
        'See ../../'+DOC+'. Not installed into normal PRGs.\n')
    release['issue144_v4_reu_isqrt32_rotate6_2026_10_15']={
        'status':'PASS_CANONICAL_CPU_AND_NATIVE_REAL_REU_SOURCE_OPTIN_ONLY',
        'profile':'v4_reu_16m','all_unsigned_32bit_inputs_supported':True,
        'canonical_paired_inputs':4130,'CPU_saved_cycles_every_case':6,
        'model_baseline':model['before']['mean'],'model_candidate':model['after']['mean'],
        'native_original_candidate_calls':48,'real_16MiB_REU_image_loaded':True,
        'normal_code_growth':0,'normal_ZP_growth':0,'normal_REU_data_growth':0,
        'optional_installer_bytes':88,'begin_cycles':66,'end_cycles':56,
        'normal_PRGs_and_REUs_unchanged':True,'native_cycles_measured':False,
        'source':SRC,'documentation':DOC,'model_evidence':MODEL,'native_evidence':VICE,
    }
    (R/'RELEASE_STATUS.json').write_text(json.dumps(release,indent=2)+'\n')
    note=(STAMP+'\n- Source-only V4 REU ISQRT32 all-input 12-byte in-place peephole: '
      'two 6x ASL groups -> LSR/ROR/ROR/BCC+1/NOP, exact public output/flags, '
      '6 CPU-model cycles saved on all 4,130 canonical inputs (917.317433 -> '
      '911.317433), 48 real native x64sc REU-16MiB baseline/candidate calls PASS. '
      'Optional reversible 88-byte BEGIN/END assembly, no extra normal ZP/code/data; '
      'normal resident PRG/REU and ordinary PERFORMANCE remain unchanged. '+DOC+'\n\n')
    for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
        file=R/name
        if STAMP not in file.read_text():file.write_text(note+file.read_text())
    subprocess.run(['make','clean'],cwd=R,check=True)
    for _ in range(3):
        reseal()
        subprocess.run([sys.executable,'tools/package_audit.py'],cwd=R,check=True)
    assert all(sha(p+'/resident/math_'+p+'_game_math.prg')==digest for p,digest in before.items())
    assert read('RELEASE_STATUS.json').get('reference_reu_sha256',{})==before_reu
    print('ISSUE144 V4 REU ISQRT32 ROTATE6 MODEL/NATIVE/ABI/SHA SEALED')
if __name__=='__main__':main()
