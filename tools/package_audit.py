#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]

def repo_files(pattern='*'):
    return [p for p in ROOT.rglob(pattern) if p.is_file() and '.git' not in p.parts]

checks=[]
def ck(name,cond,detail=None):
    if not cond: raise AssertionError(f'{name}: {detail}')
    checks.append({'check':name,'status':'PASS','detail':detail})
ck('no_pregenerated_build_source',not (ROOT/'build_source').exists())
ck('no_pregenerated_build_hybrid',not (ROOT/'build_hybrid').exists() and not (ROOT/'build_hybrid_repeat').exists())
ck('no_pregenerated_build_pareto',not (ROOT/'build_pareto').exists())
ck('no_superseded_slow_isqrt_baseline',not (ROOT/'validation/baseline_reviewed_isqrt32').exists())
ck('prior_exhaustive_baseline_retained',(ROOT/'validation/baseline_prior_final/GAME_MATH_VALIDATION_FINAL.json').exists())
ck('csdb_changelog_named_correctly',(ROOT/'CSDB_CHANGELOG.txt').exists() and not (ROOT/'CARB_CHANGELOG.txt').exists())
ck('package_contents_documented',(ROOT/'docs/PACKAGE_CONTENTS.md').exists())
ck('pareto_builder_documented',(ROOT/'docs/PARETO_BUILDER.md').exists() and (ROOT/'relocatable_source/custom_pareto/README.md').exists())
ck('pareto_tools_shipped',all((ROOT/x).exists() for x in ('tools/build_pareto.py','tools/pareto_wizard.py','tools/validate_pareto.py','tools/test_pareto_config.py','tools/stress_pareto.py')))
ck('signed_taxonomy_documented',all((ROOT/x).exists() for x in ('docs/SIGNED_IMPLEMENTATIONS.md','docs/SIGNED_IMPLEMENTATION_REFERENCE.md','docs/SIGNED_IMPLEMENTATION_SELECTION.csv','docs/SIGNED_IMPLEMENTATION_VALIDATION.md','docs/PERFORMANCE_SIGNED_IMPLEMENTATIONS.csv')))
ck('signed_validation_tools_shipped',all((ROOT/x).exists() for x in ('tools/validate_signed_layout.py','tools/validate_signed_multiply.py','tools/validate_signed_division.py','tools/upgrade_native_signed.py','tools/publish_native_signed_sources.py','tools/validate_published_signed_sources.py')))
ck('signed_profile_trees',all((ROOT/p/'resident/signed/README.md').exists() for p in ('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')))
ck('normalize_native_sources_shipped',all((ROOT/p/'resident/vector/native/vec2_normalize_q8_8.asm').exists() and (ROOT/p/'resident/vector/native/README.md').exists() for p in ('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')))
signed_profiles=('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')
published_mul=('smul8_native.asm','smul16_native.asm','smul24_native.asm','smul32_native.asm','smul32_ready_native.asm','smul16_shr8_native.asm','smul32_shr16_native.asm')
published_div=('sdiv8_native.asm','sdiv16_native.asm','sdiv24_native.asm','sdiv32_16_native.asm','sdiv32_32_native.asm','sdiv16_shl8_native.asm')
ck('published_signed_sources_shipped',all((ROOT/p/'resident/signed/multiply/native'/f).exists() for p in signed_profiles for f in published_mul) and all((ROOT/p/'resident/signed/division/native'/f).exists() for p in signed_profiles for f in published_div))
ck('no_legacy_native_signed_tree',not any((ROOT/p/'resident/native_signed').exists() for p in ('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')))
ck('no_unsigned_derived_signed_tree',not any((ROOT/p/'resident/signed/multiply/unsigned_derived').exists() for p in ('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp')))
ck('turbo_plain_english_documented','Turbo modes in plain English' in (ROOT/'USER_MANUAL.md').read_text())
# Only intended deployable binaries are pre-shipped; generated build outputs are absent.
prgs=list(ROOT.glob('v*/resident/math_*_game_math.prg'))
reus=list(ROOT.glob('v*/reu/*.reu'))
ck('five_reference_prgs',len(prgs)==5,[str(p.relative_to(ROOT)) for p in prgs])
ck('two_reference_reu_images',len(reus)==2,[str(p.relative_to(ROOT)) for p in reus])
# No nested release/archive or transient clutter.
archives=[p for p in repo_files() if p.suffix.lower() in {'.zip','.7z','.tar','.gz','.bz2','.xz'}]
ck('no_nested_archives',not archives,[str(p.relative_to(ROOT)) for p in archives])
trans=[]
for p in repo_files():
    n=p.name
    if n in {'.DS_Store'} or p.suffix.lower() in {'.pyc','.swp','.tmp','.bak','.log'} or n.endswith('~') or '__pycache__' in p.parts:
        trans.append(p)
ck('no_cache_temp_backup_logs',not trans,[str(p.relative_to(ROOT)) for p in trans])
# Binary tables/labels in the profile trees must actually be referenced by shipped text/source.
texts=[]
for p in repo_files():
    if p.suffix.lower() in {'.asm','.a','.py','.md','.inc','.json','.csv','.txt'}:
        try: texts.append((p,p.read_text(errors='ignore')))
        except Exception: pass
orphans=[]
for p in repo_files('*.bin')+repo_files('*.labels'):
    if not any(p.name in t for q,t in texts if q!=p): orphans.append(p)
ck('no_unreferenced_bin_or_label_artifacts',not orphans,[str(p.relative_to(ROOT)) for p in orphans])
# Segment manifests must resolve to files actually present in the lean distribution.
import csv
manifest_bad=[]
for f in ROOT.glob('v*/resident/SEGMENTS*.csv'):
    profile=f.parents[1]
    for row in csv.DictReader(f.open()):
        v=row.get('file','')
        if not v or v=='integrated PRG': continue
        candidates=[f.parent/v, profile/v, f.parent/Path(v).name]
        if not any(q.exists() for q in candidates): manifest_bad.append((f,v))
ck('all_segment_manifest_paths_resolve',not manifest_bad,[(str(f.relative_to(ROOT)),v) for f,v in manifest_bad])
files=repo_files()
out={'status':'PASS','checks':checks,'summary':{'checks_passed':len(checks),'file_count_excluding_checksum':len([p for p in files if p.name!='SHA256SUMS.txt']),'uncompressed_bytes_excluding_checksum':sum(p.stat().st_size for p in files if p.name!='SHA256SUMS.txt'),'reference_prgs':5,'reference_reu_images':2}}
(ROOT/'validation/PACKAGE_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
print('PACKAGE AUDIT PASS',len(checks),'checks')
