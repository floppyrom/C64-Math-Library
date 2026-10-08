#!/usr/bin/env python3
"""Finalize the 2026-10-08 signed-core reuse publication after candidate images are installed.

This script updates human-facing performance/changelog/release metadata from the
canonical validation JSON and current source-build manifests. It does not build
or validate; the one-shot finalization workflow does that first.
"""
from __future__ import annotations
from pathlib import Path
import hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp']
TARGETS=['MATH_SDIV32_16','MATH_SDIV32_32','MATH_SMOD32_16','MATH_SMOD32_32','MATH_SDIV16_SHL8']

def sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def update_performance():
    sd=json.loads((ROOT/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
    txt=(ROOT/'PERFORMANCE.md').read_text()
    canon={}
    for line in txt.splitlines():
        m=re.match(r'^\| `(MATH_[A-Z0-9_]+)` \| `([^`]+)` \|',line)
        if m: canon[m.group(1)]=m.group(2)
    for name in TARGETS:
        vals=[sd['profiles'][p][name]['mean_cycles'] for p in PROFILES]
        newline='| `%s` | `%s` | %s |' % (
            name,canon[name],' | '.join(f'{v:.6f}' for v in vals))
        pat=rf'^\| `{re.escape(name)}` \|.*$'
        txt,n=re.subn(pat,newline,txt,flags=re.M)
        if n!=1: raise RuntimeError(f'PERFORMANCE row not unique: {name} ({n})')
    (ROOT/'PERFORMANCE.md').write_text(txt)

def prepend_once(path:Path,marker:str,block:str):
    txt=path.read_text()
    if marker in txt: return
    path.write_text(block.rstrip()+'\n\n'+txt)

def update_changelogs():
    marker='2026-10-08 SIGNED MAGNITUDE-CORE REUSE + LIFTABLE MULDIV16'
    block=f"""2026-10-08 SIGNED MAGNITUDE-CORE REUSE + LIFTABLE MULDIV16
- V2/V3/V4 SDIV16_SHL8 now bind signed magnitudes directly into the selected UDIV32/16 substrate; V5 keeps the same architecture with a post-OptiSearch positive-divisor shortcut.
- Final SDIV16_SHL8 means V1-V5: 846.155071 / 630.032715 / 630.265213 / 628.417884 / 628.885496 cycles.
- V2/V3/V4/V5 SDIV32/16 now use thin signed front ends around the qualified UDIV32/16 magnitude core. Final means: 724.392148 / 724.449509 / 721.003490 / 722.170774; V1 Balanced remains 955.051690.
- V2/V3/V4 SDIV32/32 now normalize/restore public operands around the profile-selected UDIV32/32 core: 420.452435 / 416.865672 / 418.153927 cycles. V1/V5 keep their Balanced private 32/32 paths.
- Signed-layout policy now permits only explicit audited magnitude-core sharing; all unlisted signed/unsigned executable overlap remains an error.
- Full signed DIV/MOD proof: 364,533 calls, zero errors; published signed-source and layout gates pass.
- OptiSearchV2 generic signed 32/32 is noncompetitive (~3480 cycles). Six local MOS6502 rewrite classes produced no legal selected-wrapper rewrite once explicit code-island origins were respected. Post-OptiSearch manual review retained the high-byte divisor shortcut only where placement allowed it.
- MULDIV16 now has canonical symbolic liftable sources under routines/muldiv16/, and the integrated sources include those same files. Exact per-profile standalone mirrors remain for byte-level auditing.
- Technical note: docs/SIGNED_CORE_REUSE_OPTIMIZATION_2026-10-08.md.
"""
    prepend_once(ROOT/'CHANGELOG.md',marker,block)
    csdb=f"""2026-10-08 SIGNED MAGNITUDE-CORE REUSE + LIFTABLE MULDIV16
- SDIV16_SHL8 V2/V3/V4/V5: 630.033 / 630.265 / 628.418 / 628.885 cycles (V1 Balanced 846.155).
- SDIV32/16 V2/V3/V4/V5: 724.392 / 724.450 / 721.003 / 722.171 cycles (V1 Balanced 955.052).
- SDIV32/32 V2/V3/V4: 420.452 / 416.866 / 418.154 cycles; V1/V5 keep Balanced private paths.
- Signed front ends now share certified unsigned magnitude substrates only through explicit validator exceptions.
- 364,533 signed DIV/MOD calls pass with zero errors; signed source/layout gates pass.
- OptiSearch local pass found no legal selected-wrapper rewrite after placement barriers; post-pass manual high-byte shortcut retained where safe.
- Clean symbolic MULDIV16 source modules are now published under routines/muldiv16/ and are used by the integrated build.
"""
    prepend_once(ROOT/'CSDB_CHANGELOG.txt',marker,csdb)

def update_release_status():
    p=ROOT/'RELEASE_STATUS.json'
    d=json.loads(p.read_text())
    d['date']='2026-10-08'
    # Current source-build hashes.
    alt={}
    for profile in PROFILES[:4]:
        m=json.loads((ROOT/'build_source/alternate'/profile/'source_build_manifest.json').read_text())
        alt[profile]=m['output_sha256']
    hm_alt=json.loads((ROOT/'build_hybrid/alternate/v5_hybrid_lowzp/source_build_manifest.json').read_text())
    alt['v5_hybrid_lowzp']=hm_alt['output_sha256']
    d['alternate_prg_sha256']=alt
    for profile in ('v3_reu_512k','v4_reu_16m'):
        m=json.loads((ROOT/'build_source/alternate'/profile/'source_build_manifest.json').read_text())
        ri=m.get('reu_image')
        if ri:
            q=ROOT/'build_source/alternate'/profile/ri['file']
            d.setdefault('alternate_reu_sha256',{})[profile]=sha(q)
    hm_ref=json.loads((ROOT/'build_hybrid/reference/v5_hybrid_lowzp/source_build_manifest.json').read_text())
    hv=d.setdefault('hybrid_v5',{})
    hv['reference_prg_sha256']=hm_ref['output_sha256']
    hv['alternate_prg_sha256']=hm_alt['output_sha256']
    hv['normal_zp_bytes']=31

    d['signed_core_reuse_2026_10_08']={
        'status':'PASS',
        'documentation':'docs/SIGNED_CORE_REUSE_OPTIMIZATION_2026-10-08.md',
        'signed_division_modulo_machine_calls':364533,
        'approved_shared_core_pairs':11,
        'normal_zp_bytes_v5':31,
        'optisearch_archive_sha256':'f5a6a9f0e8728186f91a95c1112a70488cf943fc99b2380c52272424e44455eb',
        'sdiv16_shl8_mean_cycles':{
            'v1_balanced':846.1550708833151,'v2_pareto_fast':630.0327153762269,
            'v3_reu_512k':630.2652126499455,'v4_reu_16m':628.4178844056706,
            'v5_hybrid_lowzp':628.8854961832061},
        'sdiv32_16_mean_cycles':{
            'v1_balanced':955.0516902944383,'v2_pareto_fast':724.3921483097056,
            'v3_reu_512k':724.4495092693566,'v4_reu_16m':721.0034896401309,
            'v5_hybrid_lowzp':722.170774263904},
        'sdiv32_32_mean_cycles':{
            'v1_balanced':566.8392884064526,'v2_pareto_fast':420.4524347957184,
            'v3_reu_512k':416.86567164179104,'v4_reu_16m':418.1539273330318,
            'v5_hybrid_lowzp':572.0058796924469},
        'liftable_muldiv16':'routines/muldiv16/README.md'
    }
    notes=d.get('notes',[])
    old='All shipped SMUL*/SDIV* public paths own signed-specific executable paths; corresponding unsigned executable engines are not entered.'
    new='Signed APIs own signed semantics; selected fast division paths may share certified unsigned magnitude substrates only through explicit signed-layout validator exceptions.'
    notes=[new if x==old else x for x in notes]
    if new not in notes: notes.insert(0,new)
    d['notes']=notes
    p.write_text(json.dumps(d,indent=2)+'\n')

def main():
    update_performance()
    update_changelogs()
    update_release_status()
    print('SIGNED CORE REUSE PUBLICATION METADATA UPDATED')

if __name__=='__main__':
    main()
