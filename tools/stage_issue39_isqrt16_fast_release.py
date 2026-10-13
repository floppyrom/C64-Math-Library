#!/usr/bin/env python3
"""Stage ISQRT16 in-place 294-byte seed replacement and inherited ISQRT32 wins.

Runs ONLY on disposable staging CI branch. Commit generated files separately
after all deterministic source, correctness, ABI, performance and publication
gates succeed. V4 native REU ISQRT16 is intentionally not changed.
"""
from __future__ import annotations
from pathlib import Path
import csv,hashlib,json,math,shutil,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assemble_sources as asm,build_hybrid
from validate_unsigned_division import PROFILES,load,wr,rd
from stage_issue39_v1_3216_ool_release import reseal

MODIFIED=('v1_balanced','v2_pareto_fast','v3_reu_512k','v5_hybrid_lowzp')
SOURCES=MODIFIED[:3]
V4='v4_reu_16m'
N=0xc010;Z=0xc008
S16=0x5E2D;S32=0x5E30
NOTE='2026-10-13 ISSUE39 INTEGER ROOTS SAME-ISLAND FAST SEED'
DOC='docs/ISSUE39_INTEGER_ROOTS_SOURCE_RELEASE_2026-10-13.md'
RESULT='validation/review/ISSUE39_ISQRT16_EXHAUSTIVE_2026-10-13.json'
EXTRA='validation/review/ISSUE39_ROOTS_SAME_INPUT_2026-10-13.json'

def h(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def prg(p):return ROOT/p/'resident'/('math_'+p+'_game_math.prg')
def run(*args):
    print('RUN',*map(str,args),flush=True)
    subprocess.run([str(x) for x in args],cwd=ROOT,check=True)
def py(name,*a):run(sys.executable,ROOT/'tools'/f'{name}.py',*a)
def build_one(p,kind,output):
    config=ROOT/'relocatable_source'/p/('math_config_'+kind+'.inc')
    return asm.build(p,config,output)
def build5(kind,output):
    config=ROOT/'relocatable_source/v5_hybrid_lowzp'/('math_config_'+kind+'.inc')
    return build_hybrid.build(config,output)
def get_prg(output,man):return Path(output)/man['output_prg']
def rows(path):
    with (ROOT/path).open(newline='') as f:return list(csv.DictReader(f))
def save_rows(path,items):
    with (ROOT/path).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(items[0]),lineterminator='\n')
        writer.writeheader();writer.writerows(items)

def root16_benchmark(profile):
    cpu,pub=load(profile);assert pub['MATH_ISQRT16']==S16
    sp=cpu.sp
    ticks=0;lo=10**10;hi=0
    for n in range(65536):
        wr(cpu.mem,N,n,2)
        wr(cpu.mem,Z,0x8AC7D4E9,4)
        cpu.d=0
        cy=cpu.call(S16,100000)
        got=rd(cpu.mem,Z,2)
        assert got==math.isqrt(n),(profile,hex(n),got,math.isqrt(n))
        assert rd(cpu.mem,N,2)==n and cpu.c==0 and cpu.sp==sp,(profile,n,'ABI')
        assert rd(cpu.mem,Z+2,2)==0x8AC7,(profile,n,'Z sentinel')
        ticks+=cy;lo=min(lo,cy);hi=max(hi,cy)
    return {'profile':profile,'cases':65536,'mean_cycles':ticks/65536,
      'min_cycles':lo,'max_cycles':hi,'errors':0,'resident_sha256':h(prg(profile))}

def splitmix64(x):
    MASK=(1<<64)-1
    x=(x+0x9E3779B97F4A7C15)&MASK;z=x
    z=(z^(z>>30))*0xBF58476D1CE4E5B9&MASK
    z=(z^(z>>27))*0x94D049BB133111EB&MASK
    return x,(z^(z>>31))&MASK
def official32():
    x=0x5A7E3200
    vals=[]
    for i in range(4096):
        x,a=splitmix64(x);x,b=splitmix64(x)
        vals.append(a&0xffffffff)
    vals+= [0,1,2,3,7,15,16,31,127,128,255,256,257,0x7fff,0x8000,
      0xffff,0x10000,0x10001,0x7fffff,0x800000,0xffffff,0x1000000,
      0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
    vals+=[n*n&0xffffffff for n in [0,1,2,3,255,256,257,65535]]
    assert len(vals)==4130
    return vals
def root32_benchmark(profile):
    cpu,pub=load(profile);assert pub['MATH_ISQRT32']==S32
    sp=cpu.sp
    ticks=0;lo=10**10;hi=0
    for n in official32():
        wr(cpu.mem,N,n,4)
        wr(cpu.mem,Z,0x8AC7D4E9,4)
        cpu.d=0
        cy=cpu.call(S32,2000000)
        assert rd(cpu.mem,Z,2)==math.isqrt(n),(profile,hex(n),'ISQRT32')
        assert rd(cpu.mem,N,4)==n and cpu.c==0 and cpu.sp==sp,(profile,hex(n),'ABI')
        assert rd(cpu.mem,Z+2,2)==0x8AC7,(profile,'sentinel')
        ticks+=cy;lo=min(lo,cy);hi=max(hi,cy)
    return {'profile':profile,'cases':4130,'mean_cycles':ticks/4130,
      'min_cycles':lo,'max_cycles':hi,'errors':0,'resident_sha256':h(prg(profile))}

def main():
    statuspath=ROOT/'RELEASE_STATUS.json'
    st=json.loads(statuspath.read_text());old=st['reference_prg_sha256']
    assert {p:h(prg(p)) for p in PROFILES}==old,'begin from exact merged main'
    oldroot16={};oldroot32={}
    for p in PROFILES:
        rs=rows(p+'/PUBLIC_PERFORMANCE_GAME_MATH.csv')
        oldroot16[p]=float(next(x['mean_cycles'] for x in rs if x['routine']=='ISQRT16'))
        oldroot32[p]=float(next(x['mean_cycles'] for x in rs if x['routine']=='ISQRT32'))
    before={p:prg(p).stat().st_size for p in PROFILES}
    with tempfile.TemporaryDirectory(prefix='issue39_root16_staging_') as td:
        t=Path(td); paths={}
        for p in SOURCES:
            folder=t/'root_build'/p
            man=build_one(p,'reference',folder)
            paths[p]=get_prg(folder,man)
        folder=t/'root_build'/'v5_hybrid_lowzp'
        man=build5('reference',folder)
        paths['v5_hybrid_lowzp']=get_prg(folder,man)
        for p in MODIFIED:
            assert paths[p].stat().st_size==before[p],(p,'resident PRG growth')
            assert h(paths[p])!=old[p],(p,'optimized image unchanged')
            shutil.copyfile(paths[p],prg(p))
        assert h(prg(V4))==old[V4]
        py('generate_sources')
        new={p:h(prg(p)) for p in PROFILES}
        alt={}
        for kind in ('reference','alternate'):
            for p in (*SOURCES,V4):
                folder=t/'rebuild'/kind/p
                man=build_one(p,kind,folder)
                actual=get_prg(folder,man)
                if kind=='reference':assert h(actual)==new[p],(p,'regen drift')
                else:alt[p]=h(actual)
            folder=t/'rebuild'/kind/'v5_hybrid_lowzp'
            man=build5(kind,folder)
            actual=get_prg(folder,man)
            if kind=='reference':assert h(actual)==new['v5_hybrid_lowzp'],'V5 regen drift'
            else:alt['v5_hybrid_lowzp']=h(actual)
        print('ROOT SOURCE-REGEN REFERENCE/ALTERNATE ALL PROFILES PASS',new,flush=True)
    assert all(prg(p).stat().st_size==before[p] for p in PROFILES)
    assert new[V4]==old[V4]

    # Native machine-code model, full 16-bit domain including every perfect
    # square and boundary, with identical input ownership and preserved stack.
    result={'status':'PASS_SOURCE_STAGED_NATIVE_VICE_PENDING',
      'expected_exact_domain':65536,
      'profiles':{},'source_owned_code_plus_seed_bytes':294,
      'additional_zero_page_bytes':0,'resident_size_growth':0,
      'native_vice_calls':0,'unchanged_V4':True}
    for p in MODIFIED:
        v=root16_benchmark(p)
        result['profiles'][p]=v
        rs=rows(p+'/PUBLIC_PERFORMANCE_GAME_MATH.csv')
        item=next(x for x in rs if x['routine']=='ISQRT16')
        item.update(cases='65536',mean_cycles=str(v['mean_cycles']),
                    min_cycles=str(v['min_cycles']),max_cycles=str(v['max_cycles']))
        save_rows(p+'/PUBLIC_PERFORMANCE_GAME_MATH.csv',rs)
        print(p,'EXHAUSTIVE ROOT16',v['mean_cycles'],v['min_cycles'],v['max_cycles'],flush=True)
    # V4's exact REU lookup remains published with its original proof.
    row=ROOT/RESULT
    row.parent.mkdir(parents=True,exist_ok=True)
    row.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    py('validate_isqrt32_fast')
    py('benchmark_isqrt32_fast')
    v5_32=root32_benchmark('v5_hybrid_lowzp')
    rs=rows('v5_hybrid_lowzp/PUBLIC_PERFORMANCE_GAME_MATH.csv')
    item=next(x for x in rs if x['routine']=='ISQRT32')
    item.update(cases='4130',mean_cycles=str(v5_32['mean_cycles']),
                min_cycles=str(v5_32['min_cycles']),max_cycles=str(v5_32['max_cycles']))
    save_rows('v5_hybrid_lowzp/PUBLIC_PERFORMANCE_GAME_MATH.csv',rs)
    root32=json.loads((ROOT/'validation/review/ISQRT32_FAST_PERFORMANCE_4130.json').read_text())
    r32={x['profile']:x for x in root32['profiles']}
    r32['v5_hybrid_lowzp']=v5_32
    assert h(prg(V4))==old[V4]
    details={'status':'PASS_SOURCE_STAGED_NATIVE_PENDING','ISQRT16':result['profiles'],
       'ISQRT32':r32,'previous16':oldroot16,'previous32':oldroot32,
       'reference_sha256':new,'alternate_sha256':alt,
       'V4_isqrt16_still_REU':True,'V4_binary_unchanged':True}
    (ROOT/EXTRA).write_text(json.dumps(details,indent=2,sort_keys=True)+'\n')

    perf=ROOT/'PERFORMANCE.md'
    lines=perf.read_text().splitlines()
    for routine,key in [('MATH_ISQRT16','ISQRT16'),('MATH_ISQRT32','ISQRT32')]:
        matches=[i for i,line in enumerate(lines) if line.startswith('| '+chr(96)+routine+chr(96)+' |')]
        assert len(matches)==1,(routine,'PERFORMANCE row layout changed')
        cells=lines[matches[0]].split('|')
        for j,p in enumerate(PROFILES): 
            x=(result['profiles'][p] if p in MODIFIED else
               {'mean_cycles':oldroot16[p]}) if key=='ISQRT16' else r32[p]
            cells[3+j]=' '+format(float(x['mean_cycles']),'.6f')+' '
        lines[matches[0]]='|'.join(cells)
    perf.write_text('\n'.join(lines)+'\n')

    py('publish_standalone_sources')
    py('generate_consolidated_routine_table')
    py('generate_public_indexes')
    py('validate_public_catalog')
    py('validate_standalone_sources')
    py('verify_deterministic_rebuild')
    # All existing signed/unsigned families are retained verbatim in PRG, but
    # reverify them through canonical deterministic public API validators.
    py('validate_unsigned_division')
    py('validate_signed_division')

    text=('# Issue39 — integer square roots source integration (release stage)\n\n'
      '13 October 2026. Production staging, native VICE and PR/main CI not yet qualified.\n\n'
      'A manually implemented exact ISQRT16 upper-bound table seeds the root '
      'from the radicand high byte, then compares candidate-square bytes '
      'against the existing two resident square planes and decreases the '
      'candidate until the floor root is exact. The 294-byte executable + '
      '256-byte seed table occupies the original 304-byte V2/V3 root-search '
      'island (V1 had 329 bytes), replacing code rather than growing the '
      'resident. No extra normal ZP or additional RAM table pages.\n\n'
      'V1, V2, V3 and V5 apply this improvement. V4 retains its faster '
      'exact 54-cycle REU ISQRT16 service and its released PRG/REU images. '
      'ISQRT32 inherits a high-byte seed improvement for V1/V2/V3/V5; '
      'all four root32 implementations still compute exact floor(sqrt(N)).\n\n'
      '| Profile | ISQRT16 before | ISQRT16 new | ISQRT32 before | ISQRT32 new |\n'
      '|---|---:|---:|---:|---:|\n'+
      ''.join('| '+p+' | '+format(oldroot16[p],'.6f')+' | '
        +format((result['profiles'][p]['mean_cycles'] if p in MODIFIED else oldroot16[p]),'.6f')
        +' | '+format(oldroot32[p],'.6f')+' | '+format(r32[p]['mean_cycles'],'.6f')+' |\n'
        for p in PROFILES)+
      '\nISQRT16 timing is an actual exhaustive 65,536-case public-entry'
      ' 6502 instruction count on each optimized profile. ISQRT32 uses'
      ' the existing exact same 4,130-case corpus. These are not cycle-exact'
      ' native hardware or REU bus-time measurements.\n\n'
      'V1/V2/V3/V5 source reference/alternate regeneration passed.'
      ' V4 untouched. Stable public ABI, input ownership, stack and'
      ' carry preserved. OptiSearch source remains private and is NOT'
      ' included or transcribed into this repository.\n\n'
      '**Pending before release:** native VICE on installed source-built'
      ' resident images, independent PR tests, post-merge main CI.'
      ' Issue #39 remains OPEN; unrelated unsigned closure also remains'
      ' unchecked until documented.\n')
    (ROOT/DOC).write_text(text)
    note=(NOTE+'\n'
      '- ISQRT16 exact floor-root public source upgrade on V1/V2/V3/V5: '
      '294 bytes total replacement of existing ISQRT16 code island, '
      'includes 256-byte upper seed table and reuses $9800/$9900 squares. '
      'No PRG length/ZP changes. V4 REU root unchanged.\n'
      '- Rebenchmarked all 65536 ISQRT16 operands and 4130 common ISQRT32 '
      'operands, with exact source reference/alternate and V5 hybrid '
      'regeneration, standalone/public catalog and all-family ABI checks. '
      'Native VICE pending. Issue #39 remains OPEN. '+DOC+'\n\n')
    for name in ('CHANGELOG.md','CSDB_CHANGELOG.txt'):
        path=ROOT/name
        if NOTE not in path.read_text():path.write_text(note+path.read_text())
    for name in ('README.md','USER_MANUAL.md'):
        path=ROOT/name
        link='\n- Root optimization release-stage evidence: '+DOC+' (native VICE and independent PR/main CI pending).\n'
        if link not in path.read_text():path.write_text(path.read_text().rstrip()+'\n'+link)
    st['reference_prg_sha256']=new
    st['alternate_prg_sha256']=alt
    st['issue39_integer_roots_source_release_2026_10_13']={
      'status':'PASS_STAGED_NATIVE_VICE_PENDING',
      'root16_exact_domain_per_optimized_profile':65536,
      'isqrt32_same_input_cases_per_profile':4130,
      'optimized_profiles':list(MODIFIED),'v4_PRG_unchanged':True,
      'normal_ZP_growth':0,'resident_size_growth':0,
      'reference_sha256':new,'alternate_sha256':alt,
      'native_vice_calls':0,'document':DOC,'proof':EXTRA,
      'issue39_complete':False}
    if isinstance(st.get('documentation'),dict):
        p=ROOT/'USER_MANUAL.md'
        st['documentation'].update(user_manual_bytes=p.stat().st_size,
          user_manual_lines=len(p.read_text().splitlines()),user_manual_sha256=h(p))
    statuspath.write_text(json.dumps(st,indent=2)+'\n')
    run('make','clean')
    for _ in range(3):
        reseal()
        py('package_audit')
    print('ISQRT16/32 SOURCE-INTEGRATED STAGING COMPLETE; NATIVE VICE STILL REQUIRED',flush=True)
if __name__=='__main__':main()
