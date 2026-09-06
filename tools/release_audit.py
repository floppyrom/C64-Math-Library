#!/usr/bin/env python3
from pathlib import Path
import csv, json, hashlib, py_compile, re
ROOT=Path(__file__).resolve().parents[1]
PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m']
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
def ck(name,cond,detail=None):
    if not cond: raise AssertionError(f'{name}: {detail}')
    checks.append({'check':name,'status':'PASS','detail':detail})

# Tool syntax.
for p in sorted((ROOT/'tools').glob('*.py')): py_compile.compile(str(p),doraise=True)
ck('python_tools_compile',True,f'{len(list((ROOT/"tools").glob("*.py")))} files')

# Stable API manifest.
rows=list(csv.DictReader((ROOT/'docs/PUBLIC_API_COMPLETE.csv').open()))
names=[r['entry'] for r in rows]
ck('public_api_count',len(rows)==45,len(rows));ck('public_api_unique',len(set(names))==45)
game=rows[26:]
ck('game_api_slots',len(game)==19 and all(int(r['address'][1:],16)==0x5e00+i*3 for i,r in enumerate(game)),[r['address'] for r in game])
turbo_rows=list(csv.DictReader((ROOT/'docs/TURBO_API.csv').open()))
turbo_names=[r['entry'] for r in turbo_rows]
ck('turbo_api_count',len(turbo_rows)==6,len(turbo_rows));ck('turbo_api_unique',len(set(turbo_names))==6)
ck('turbo_api_profiles',all(r['profiles']=='V3/V4' for r in turbo_rows))

# Build and validation evidence.
source_val=json.loads((ROOT/'validation/source_relocation/ALTERNATE_MAP_VALIDATION.json').read_text())
ck('alternate_validation_status',source_val['status']=='PASS')
ck('alternate_all_profiles',len(source_val['profiles'])==4)
ck('alternate_entries_180',sum(x['public_entries_executed'] for x in source_val['profiles'])==180)
ck('alternate_calls_16688',sum(x['machine_calls'] for x in source_val['profiles'])==16688)
for x in source_val['profiles']:
    ck(f'{x["profile"]}_45_entries',x['public_entries_executed']==45)
    ck(f'{x["profile"]}_all_named_entries_hit',set(x['entry_hits'])==set(names))

det=json.loads((ROOT/'validation/source_relocation/DETERMINISTIC_REBUILD.json').read_text())
ck('deterministic_rebuild',det['status']=='PASS' and len(det['checks'])==8)
for x in det['checks']:
    ck(f'deterministic_{x["kind"]}_{x["profile"]}',x['repeat_prg_identical'] is True and (x['repeat_reu_identical'] in (True,None)))
    current=json.loads((ROOT/'build_source'/x['kind']/x['profile']/'source_build_manifest.json').read_text())
    ck(f'deterministic_hash_current_{x["kind"]}_{x["profile"]}',x['prg_sha256']==current['output_sha256'])
    if x['kind']=='reference':
        ck(f'reference_exact_{x["profile"]}',x['reference_prg_identical'] is True)
        if x['profile'] in ('v3_reu_512k','v4_reu_16m'):
            ck(f'reference_reu_exact_{x["profile"]}',x.get('reference_reu_identical') is True)

acme=json.loads((ROOT/'validation/acme/ACME_SOURCE_BUILD_VALIDATION.json').read_text())
ck('acme_validation',acme['status']=='PASS' and len(acme['checks'])==8 and len(acme.get('overlay_checks',[]))==8 and len(acme.get('overlay_boundary_checks',[]))==4,acme['assembler'])
for x in acme['checks']:
    ck(f'acme_{x["map"]}_{x["profile"]}',x['byte_identical'] is True and (x['reference_prg_identical'] is True if x['map']=='reference' else True))
    current=json.loads((ROOT/'build_source'/x['map']/x['profile']/'source_build_manifest.json').read_text())
    ck(f'acme_hash_current_{x["map"]}_{x["profile"]}',x['acme_sha256']==current['output_sha256'])
for x in acme.get('overlay_checks',[]):
    ck(f'acme_overlay_{x["map"]}_{x["profile"]}_{x["overlay"]}',x['byte_identical'] is True and x['status']=='PASS')
    if x['map']=='reference': ck(f'acme_reference_overlay_exact_{x["profile"]}_{x["overlay"]}',x.get('reference_overlay_identical') is True)
for x in acme.get('overlay_boundary_checks',[]):
    ck(f'acme_boundary_{x["overlay"]}_{x["zp_base"]}',x['status']=='PASS' and x['byte_identical'] is True)

cfg=json.loads((ROOT/'validation/CONFIG_VALIDATION.json').read_text())
ck('config_validation',cfg['status']=='PASS' and cfg['tests']==27,cfg['tests'])

turbo=json.loads((ROOT/'validation/turbo_relocation/TURBO_RELOCATION_VALIDATION.json').read_text())
ck('turbo_validation_status',turbo['status']=='PASS')
ck('turbo_product_calls_17164',turbo['total_product_calls']==17164,turbo['total_product_calls'])
ck('turbo_lifecycle_calls_32',turbo.get('total_lifecycle_calls')==32,turbo.get('total_lifecycle_calls'))
ck('turbo_api_calls_17196',turbo.get('total_turbo_api_calls')==17196,turbo.get('total_turbo_api_calls'))
for p in ['v3_reu_512k','v4_reu_16m']:
    r=turbo['profiles'][p]['reference']; a=turbo['profiles'][p]['alternate']
    for mode in ['turbo16','turbo32']:
        rr=r[mode]; aa=a[mode]
        ck(f'{p}_{mode}_cases',rr['cases']==aa['cases'] and rr['cases'] in (2098,2193))
        ck(f'{p}_{mode}_relocated',rr['zp_base']!=aa['zp_base'] and rr['reu_bank']!=aa['reu_bank'])
        ck(f'{p}_{mode}_zero_cycle_penalty',rr['cycle_vector_sha256']==aa['cycle_vector_sha256'] and rr['begin_cycles']==aa['begin_cycles'] and rr['end_cycles']==aa['end_cycles'])

boundary=json.loads((ROOT/'validation/turbo_relocation/TURBO_BOUNDARY_SWEEP.json').read_text())
ck('turbo_boundary_status',boundary['status']=='PASS')
ck('turbo_boundary_products_3556',boundary['total_product_calls']==3556,boundary['total_product_calls'])
for p in ('v3_reu_512k','v4_reu_16m'):
    lo=boundary['profiles'][p]['minimum_origins'];hi=boundary['profiles'][p]['maximum_origins']
    ck(f'{p}_turbo16_origin_bounds',lo['turbo16']['zp_base']=='$02' and hi['turbo16']['zp_base']=='$8F')
    ck(f'{p}_turbo32_origin_bounds',lo['turbo32']['zp_base']=='$02' and hi['turbo32']['zp_base']=='$0F')
    for t in ('turbo16','turbo32'):
        ck(f'{p}_{t}_boundary_cycle_identity',lo[t]['cycle_vector_sha256']==hi[t]['cycle_vector_sha256'])

sq=json.loads((ROOT/'validation/review/ISQRT32_FAST_VALIDATION.json').read_text())
ck('isqrt32_validation',sq['status']=='PASS' and all(x['status']=='PASS' and x['cases']==5097 for x in sq['profiles']))
delta=json.loads((ROOT/'validation/review/ISQRT32_FAST_DELTA_AUDIT.json').read_text())
ck('binary_delta_confined',delta['status']=='PASS' and all(x['outside_allowed_ranges']==0 for x in delta['profiles']))

# Performance rows match current comparable corpus.
sp=json.loads((ROOT/'validation/review/ISQRT32_FAST_PERFORMANCE_4130.json').read_text());want={x['profile']:x for x in sp['profiles']}
prows=list(csv.DictReader((ROOT/'docs/PERFORMANCE_GAME_MATH_FINAL.csv').open()))
for p in PROFILES:
    r=next(x for x in prows if x['profile']==p and x['routine']=='ISQRT32');w=want[p]
    ck(f'isqrt32_perf_{p}',int(r['cases'])==w['cases'] and abs(float(r['mean_cycles'])-w['mean_cycles'])<1e-12 and int(r['min_cycles'])==w['min_cycles'] and int(r['max_cycles'])==w['max_cycles'])

# Per-profile generated API includes and reference binaries.
for p in PROFILES:
    man=json.loads((ROOT/'build_source/reference'/p/'source_build_manifest.json').read_text())
    ck(f'{p}_manifest_45',set(man['public_entries'])==set(names) and len(man['public_entries'])==45)
    if p in ('v3_reu_512k','v4_reu_16m'):
        inc=(ROOT/'build_source/reference'/p/'math_api.inc').read_text()
        ck(f'{p}_generated_turbo_api',all(re.search(rf'^\s*{re.escape(n)}\s*=',inc,re.M) for n in turbo_names))
        ck(f'{p}_generated_turbo_config',all(k in inc for k in ('TURBO16_ZP_BASE','TURBO32_ZP_BASE','REU_TURBO16_BANK','REU_TURBO32_BANK')))
    resident=ROOT/p/'resident'/f'math_{p}_game_math.prg';built=ROOT/'build_source/reference'/p/man['output_prg']
    ck(f'{p}_reference_prg_exact',built.read_bytes()==resident.read_bytes(),sha(resident))
    if p in ('v3_reu_512k','v4_reu_16m'):
        ref_reu=ROOT/p/'reu'/('c64_math_v3_512k_game_math.reu' if p=='v3_reu_512k' else 'c64_math_v4_16m_game_math.reu')
        built_reu=ROOT/'build_source/reference'/p/man['reu_image']['file']
        ck(f'{p}_reference_reu_exact',built_reu.read_bytes()==ref_reu.read_bytes(),sha(ref_reu))

# Canonical sources must expose every map symbol and use symbolic public API.
required=['REG_LOW','REG_API','REG_KERNEL','REG_GAME_API','REG_TABLE','REG_GAME','MATH_IO','REU_SCRATCH','V1_SCRATCH','ZP_MAIN','ZP_SMUL','TURBO16_ZP_BASE','TURBO32_ZP_BASE']
for p in PROFILES:
    src=(ROOT/'relocatable_source'/p/'math_relocatable.asm').read_text()
    cfgtext=(ROOT/'relocatable_source'/p/'math_config_reference.inc').read_text()
    ck(f'{p}_config_symbols',all(re.search(rf'^\s*{re.escape(k)}\s*=',cfgtext,re.M) for k in required))
    ck(f'{p}_source_uses_config',all(k in src for k in ['REG_API','REG_GAME_API','MATH_IO','ZP_MAIN']))
    if p in ('v3_reu_512k','v4_reu_16m'):
        ck(f'{p}_turbo_config_symbols',all(re.search(rf'^\s*{k}\s*=',cfgtext,re.M) for k in ('TURBO16_ZP_BASE','TURBO32_ZP_BASE','REU_TURBO16_BANK','REU_TURBO32_BANK')))
        ck(f'{p}_source_uses_turbo_config',all(k in src for k in ('TURBO16_ZP_BASE','TURBO32_ZP_BASE','REU_TURBO16_BANK','REU_TURBO32_BANK')))

# Documentation/release hygiene.
needed=['README.md','QUICK_START.md','CHANGELOG.md','CSDB_CHANGELOG.txt','docs/SOURCE_RELOCATION.md','docs/TURBO_RELOCATION.md','docs/TURBO_API.csv','validation/REVIEWED_RELEASE_VALIDATION.md']
ck('required_docs',all((ROOT/x).exists() for x in needed),needed)
manual=(ROOT/'USER_MANUAL.md').read_text()
ck('turbo_plain_english_manual','Turbo modes in plain English' in manual and 'zero-page workbench' in manual and 'REU DMA' in manual)
ck('package_contents_doc',(ROOT/'docs/PACKAGE_CONTENTS.md').exists())
ck('no_interrupted_full_reference_logs',not (ROOT/'validation/full_reference').exists())
ck('no_superseded_binary_relocation_evidence',not (ROOT/'validation/relocation').exists())
third=(ROOT/'docs/THIRD_PARTY_NOTICES_GAME_MATH.md').read_text()
ck('isqrt32_notice_current','independently derived exact hybrid' in third and 'eight remaining restoring base-4 refinement steps' in third and 'CC BY-NC-SA' not in third)
for p in PROFILES:
    src=(ROOT/p/'resident/game_math_extension.asm').read_text()
    ck(f'{p}_active_source_comment_current','ISQRT16 seeding plus eight restoring base-4 refinement steps' in src and 'fast recurrence below' not in src)

v4=(ROOT/'v4_reu_16m/resident/math_v4_reu_16m_game_math.prg').read_bytes();ld=v4[0]|v4[1]<<8
def vb(a): return v4[2+a-ld]
ck('v4_isqrt32_square_planes',all(vb(0x9800+x)==((x*x)&255) and vb(0x9900+x)==(((x*x)>>8)&255) for x in range(256)))

out={'status':'PASS','checks':checks,'summary':{'checks_passed':len(checks),'public_entries':45,'alternate_entry_executions':180,'alternate_machine_calls':16688,'config_cases':27,'turbo_product_calls':17164,'turbo_lifecycle_calls':32,'turbo_api_calls':17196,'turbo_boundary_product_calls':3556,'reu_profiles_turbo_entries':6,'isqrt32_cases_per_profile':5097}}
(ROOT/'validation/RELEASE_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
print('RELEASE AUDIT PASS',len(checks),'checks')
