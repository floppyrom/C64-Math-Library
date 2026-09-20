#!/usr/bin/env python3
"""Generate one auditable resource/performance table for every shipped profile routine.

Definitions:
- mean/min/max cycles are public-entry cycles including the routine's RTS and excluding caller JSR/input stores.
  The `cycle_basis` column identifies the evidence corpus/model; figures from different bases should not be
  over-interpreted below a cycle or two.
- reachable_code_bytes is the unique executable byte set statically reachable from the entry after MATH_INIT.
  It includes private callees and ZP-resident executable bytes. Shared code therefore appears on more than one
  row and rows MUST NOT be summed to obtain profile memory.
- zp_bytes/zp_ranges are concrete page-zero bytes executable/referenced by that routine's reachable code.
  For exclusive REU Turbo modes and V4 QS16, the advertised owned overlay range is reported instead.
- stack_page_reserved_bytes is persistent code/data reserved in $0100-$01FF. Ordinary transient JSR/PHA stack
  traffic is not counted. All shipped fixed/profile choices deliberately reserve 0 stack-page bytes.
- profile_prg_payload_span_bytes is the on-disk PRG payload span (load byte range), not a sum of per-routine code.
"""
from __future__ import annotations
from pathlib import Path
import csv,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU,REV,SIZE
from publish_standalone_sources import CANONICAL, PROFILE_EXTRAS
REV[0xBF]=('lax','absy'); REV[0xAF]=('lax','abs'); REV[0xA7]=('lax','zp')

PROFILES=['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m','v5_hybrid_lowzp']
PRG={p:next((ROOT/p/'resident').glob('*game_math.prg')) for p in PROFILES}
REU={'v3_reu_512k':ROOT/'v3_reu_512k/reu/c64_math_v3_512k_game_math.reu','v4_reu_16m':ROOT/'v4_reu_16m/reu/c64_math_v4_16m_game_math.reu'}
API_ROWS=list(csv.DictReader((ROOT/'docs/PUBLIC_API_COMPLETE.csv').open()))
API={r['entry']:int(r['address'][1:],16) for r in API_ROWS}


def load_profile(profile):
    b=PRG[profile].read_bytes(); load=b[0]|(b[1]<<8)
    mem=bytearray(65536); mem[load:load+len(b)-2]=b[2:]
    reu=bytearray(REU[profile].read_bytes()) if profile in REU else None
    cpu=CPU(mem,reu=reu); cpu.d=0; cpu.call(0x3280,2_000_000)
    return cpu.mem


def trace(mem,start):
    todo=[start]; seen=set(); code=set(); zp=set(); stack=set(); indirect=[]
    while todo:
        pc=todo.pop()
        if pc in seen: continue
        seen.add(pc); oc=mem[pc]
        if oc not in REV: raise RuntimeError(f'unsupported ${oc:02X} at ${pc:04X} tracing ${start:04X}')
        op,mode=REV[oc]; sz=SIZE[mode]
        for i in range(sz):
            a=(pc+i)&0xffff; code.add(a)
            if 2<=a<=0xff: zp.add(a)
            if 0x100<=a<=0x1ff: stack.add(a)
        if mode in ('zp','zpx','zpy'):
            zp.add(mem[(pc+1)&0xffff])
        elif mode in ('indx','indy'):
            q=mem[(pc+1)&0xffff]; zp.add(q); zp.add((q+1)&0xff)
        elif mode in ('abs','absx','absy'):
            a=mem[(pc+1)&0xffff]|(mem[(pc+2)&0xffff]<<8)
            if 2<=a<=0xff: zp.add(a)
        nxt=(pc+sz)&0xffff
        if mode=='rel':
            off=mem[(pc+1)&0xffff]; off=off-256 if off&128 else off; target=(nxt+off)&0xffff
            if pc in (0x4124,0x41AC): todo.append(target)
            else: todo += [nxt,target]
        elif op=='jmp':
            if mode=='abs': todo.append(mem[(pc+1)&0xffff]|(mem[(pc+2)&0xffff]<<8))
            else: indirect.append(pc)
        elif op=='jsr':
            todo += [nxt,mem[(pc+1)&0xffff]|(mem[(pc+2)&0xffff]<<8)]
        elif op in ('rts','rti','brk'): pass
        else: todo.append(nxt)
    if indirect: raise RuntimeError(f'indirect JMP(s) while tracing ${start:04X}: {indirect}')
    return code,zp,stack


def fmt_ranges(vals):
    if not vals: return ''
    vals=sorted(vals); out=[]; s=p=vals[0]
    for v in vals[1:]:
        if v!=p+1:
            out.append((s,p)); s=v
        p=v
    out.append((s,p))
    return ';'.join(f'${a:02X}' if a==b else f'${a:02X}-${b:02X}' for a,b in out)


def add_cycle(cat,p,n,mean,minc='',maxc='',cases='',basis='',notes=''):
    cat.setdefault(p,{})[n]={'mean_cycles':float(mean),'min_cycles':minc,'max_cycles':maxc,'cases':cases,'cycle_basis':basis,'cycle_notes':notes}


def cycles_catalog():
    cat={p:{} for p in PROFILES}
    # Resident unsigned V1/V2 canonical data.
    for p in ['v1_balanced','v2_pareto_fast']:
        for r in csv.DictReader((ROOT/p/'PUBLIC_PERFORMANCE.csv').open()):
            n=r['operation'].upper()
            add_cycle(cat,p,n,r['avg_cycles'],r.get('min_cycles',''),r.get('max_cycles',''),r.get('cases',''),r.get('evidence','published canonical'),r.get('notes',''))
    # V3/V4 published resident transport/canonical means.
    for r in csv.DictReader((ROOT/'v3_reu_512k/PUBLIC_PERFORMANCE.csv').open()):
        add_cycle(cat,'v3_reu_512k','MATH_'+r['operation'].upper(),r['v3_reu_default_cycles'],basis=r['v3_evidence'])
    for r in csv.DictReader((ROOT/'v4_reu_16m/PUBLIC_PERFORMANCE.csv').open()):
        add_cycle(cat,'v4_reu_16m','MATH_'+r['operation'].upper(),r['v4_reu_16m_cycles'],basis=r['v4_evidence'])
    # Record-upgrade apples-to-apples measurements supersede UMUL16/24/32 old rows.
    up=json.loads((ROOT/'validation/umul_record_upgrade_current_benchmark.json').read_text())
    for p,rr in up.items():
        for n,v in rr.items(): add_cycle(cat,p,n,v['mean'],v['min'],v['max'],v['cases'],'2026-09-14 record-upgrade deterministic comparison corpus')
    # Fresh post-upgrade measurements for READY/fixed-point multiply entries.
    ch=json.loads((ROOT/'validation/record_upgrade_changed_entries_benchmark.json').read_text())
    for p,rr in ch['profiles'].items():
        for n,v in rr.items(): add_cycle(cat,p,n,v['mean_cycles'],v['min_cycles'],v['max_cycles'],v['cases'],'2026-09-14 post-upgrade deterministic comparison corpus')
    # Current native signed multiply evidence.
    sm=json.loads((ROOT/'validation/review/SIGNED_MULTIPLY_VALIDATION.json').read_text())
    for p,rr in sm['profiles'].items():
        for short,v in rr.items():
            n='MATH_'+short; add_cycle(cat,p,n,v['mean_cycles'],v['min_cycles'],v['max_cycles'],v['cases'],'current native-signed multiply validation',v.get('mode',''))
    # Current native signed divide/mod/fixed-point divide evidence.
    sd=json.loads((ROOT/'validation/review/SIGNED_DIVISION_VALIDATION.json').read_text())
    for p,rr in sd['profiles'].items():
        for n,v in rr.items(): add_cycle(cat,p,n,v['mean_cycles'],v['min_cycles'],v['max_cycles'],v['cases'],'current native-signed division validation',v.get('mode',''))
    # Current unsigned division/modulo/fixed-point/reciprocal evidence from the
    # 2026-09-20 family refresh.  This comes after the historic PUBLIC_PERFORMANCE
    # rows so current shipped direct-public paths are authoritative.
    ud=json.loads((ROOT/'validation/review/UNSIGNED_DIVISION_VALIDATION.json').read_text())
    for p,rr in ud['profiles'].items():
        for n,v in rr.items(): add_cycle(cat,p,n,v['mean_cycles'],v['min_cycles'],v['max_cycles'],v['cases'],'2026-09-20 unsigned division-family validation',v.get('mode',''))
    # Game math published measurements for unaffected entries.
    game={p:{} for p in PROFILES[:4]}
    for p in PROFILES[:4]:
        for r in csv.DictReader((ROOT/p/'PUBLIC_PERFORMANCE_GAME_MATH.csv').open()):
            name=r['routine']
            if name=='SMUL16_REPAIRED': continue
            game[p]['MATH_'+name]=r
            if 'MATH_'+name not in cat[p]:
                add_cycle(cat,p,'MATH_'+name,r['mean_cycles'],r['min_cycles'],r['max_cycles'],r['cases'],'current exhaustive/profile game-math benchmark',('alias '+r['alias_of']) if r.get('alias_of') else '')
    # Multiplication refresh: common deterministic public-entry corpus for all
    # entries whose implementation changed in the 2026-09-20 profile sweep.
    # This intentionally comes after the older game/record rows so the current
    # resident implementation is authoritative. Signed producer rows themselves
    # remain sourced from SIGNED_MULTIPLY_VALIDATION above.
    mr=json.loads((ROOT/'validation/multiply_refresh/MULTIPLY_REFRESH_BENCHMARK.json').read_text())
    for p,rr in mr['profiles'].items():
        for n,v in rr.items():
            add_cycle(cat,p,n,v['mean_cycles'],v['min_cycles'],v['max_cycles'],v['cases'],
                      '2026-09-20 multiply-refresh deterministic cross-profile corpus')

    # Q8.8 vector normalize profile-parity benchmark (107,396-vector deterministic corpus).
    norm=json.loads((ROOT/'validation/normalize/NORMALIZE_PROFILE_PARITY_107396.json').read_text())
    for row in norm['profiles']:
        v=row['reference']; add_cycle(cat,row['profile'],'MATH_VEC2_NORMALIZE_Q8_8',v['mean_cycles'],v['min_cycles'],v['max_cycles'],v['cases'],'2026-09-18 normalize profile-parity deterministic corpus','Q8.8 -> Q1.15; certified <=0.3621 deg / <=202 LSB')
    # V5 is V1 plus documented V2 imports; current signed/changed rows above override these inheritance rows.
    for n in API:
        if n in cat['v5_hybrid_lowzp']: continue
        donor='v1_balanced'
        if n in {'MATH_UDIV16','MATH_UDIV24','MATH_UDIV32_16','MATH_UMOD8','MATH_UMOD16','MATH_UMOD24','MATH_UMOD32_16','MATH_COS8','MATH_SINCOS8','MATH_ATAN2_8','MATH_UDIV16_SHL8','MATH_URECIP16_Q16'}:
            donor='v2_pareto_fast'
        if n in cat[donor]:
            v=dict(cat[donor][n]); v['cycle_basis']='V5 documented '+donor+' path; '+v['cycle_basis']; cat['v5_hybrid_lowzp'][n]=v
    # Sanity: all stable APIs have a cycle figure in every profile.
    missing=[(p,n) for p in PROFILES for n in API if n not in cat[p]]
    if missing: raise RuntimeError(f'missing cycle rows: {missing}')
    return cat


def declared_zp(profile):
    txt=(ROOT/profile/'resident/math_api.inc').read_text()
    m=re.search(r'MATH_ZP_BYTES\s*=\s*(\d+|\$[0-9A-Fa-f]+)',txt)
    if not m: return 31 if profile=='v5_hybrid_lowzp' else ''
    return int(m.group(1)[1:],16) if m.group(1).startswith('$') else int(m.group(1))


def provenance(profile,n):
    if n=='MATH_ATAN2_8':
        if profile=='v1_balanced':
            return 'compact_opt signed-log kernel; two table pages; exact parity with prior compact outputs'
        if profile in ('v2_pareto_fast','v3_reu_512k'):
            return 'sum_fast carry-clearing signed-log kernel; four table pages; exact parity with prior fast outputs'
        if profile=='v4_reu_16m':
            return 'exact signed-byte phase plane in REU bank 8'
        return 'V2 sum_fast kernel imported into V5 with four private table pages'
    if n=='MATH_UMUL8':
        return 'profile-selected existing UMUL8 path; refreshed ZP record candidate rejected by profile resource contract'
    if n=='MATH_UMUL16':
        return '17-ZP qualified record-derived fused quarter-square resident kernel (retained after refresh sweep)'
    if n=='MATH_UMUL24':
        if profile in ('v1_balanced','v5_hybrid_lowzp'):
            return 'FAST24 private 24-ZP carry producer with stable public adapter'
        return '24-ZP reverse_24zp_carry certified resident kernel (retained; refresh candidate did not win)'
    if n in ('MATH_UMUL32','MATH_UMUL32_READY'):
        return 'FAST31/V29-derived private q0 unsigned producer; mixed-call-safe public binder'
    if n=='MATH_UMUL32_SHR16':
        return 'FAST31/V29-derived UMUL32 producer plus existing SHR16 extraction'
    if n=='MATH_SMUL8':
        return 'direct signed-domain quarter-square kernel with private signed-sum planes'
    if n=='MATH_SMUL16':
        if profile in ('v1_balanced','v5_hybrid_lowzp'):
            return 'FAST17 native signed composition with private 17-ZP magnitude core'
        return '116-ZP practical native signed quarter-square kernel (retained after FAST17 comparison)'
    if n=='MATH_SMUL16_SHR8':
        return ('FAST17 SMUL16 plus SHR8 extraction' if profile in ('v1_balanced','v5_hybrid_lowzp')
                else '116-ZP practical native SMUL16 plus SHR8 extraction')
    if n=='MATH_SMUL24':
        return 'FAST24 four-quadrant native signed composition; immutable quarter-square tables shared'
    if n in ('MATH_SMUL32','MATH_SMUL32_READY'):
        return 'FAST31/V29 native signed quadrant composition; mixed-call-safe public path'
    if n=='MATH_SMUL32_SHR16':
        return 'FAST31/V29 SMUL32 producer plus existing SHR16 extraction'
    if n in ('MATH_UDIV8','MATH_UMOD8'):
        if profile in ('v3_reu_512k','v4_reu_16m') and n=='MATH_UMOD8':
            return 'REU direct remainder plane retained; direct-public UDIV8 selected separately'
        return 'direct-public 8-bit divider; quotient/remainder produced in stable I/O without marshalling'
    if n in ('MATH_UDIV16','MATH_UMOD16'):
        return ('balanced direct-public 16-bit divider' if profile=='v1_balanced' else
                'fast direct-public 16-bit divider; V5 repacked into hybrid private RAM' if profile=='v5_hybrid_lowzp' else
                'fast direct-public 16-bit divider')
    if n in ('MATH_UDIV24','MATH_UMOD24'):
        return ('balanced direct-public 24-bit divider' if profile=='v1_balanced' else
                'Repose q0-counter/direct-public UDIV24; V5 repacked hybrid copy' if profile=='v5_hybrid_lowzp' else
                'Repose q0-counter/direct-public UDIV24')
    if n in ('MATH_UDIV32_32','MATH_UMOD32_32'):
        return 'native tiered 32/32 divider with early q=0 gate'
    if n=='MATH_UDIV32_16' or n=='MATH_UMOD32_16':
        return ('V2 certified 32/16 divider imported into V5 hybrid private RAM' if profile=='v5_hybrid_lowzp' else
                'profile-selected native 32/16 divider')
    if n=='MATH_UDIV16_SHL8':
        return 'fixed-point adapter into selected unsigned 32/16 divider'
    if n=='MATH_URECIP16_Q16':
        return 'exact reciprocal ladder with selected profile division fallback'
    if n in ('MATH_SDIV8','MATH_SMOD8'):
        return 'direct-output native signed 8-bit divider; executable-disjoint from UDIV8'
    if n in ('MATH_SDIV16','MATH_SMOD16'):
        return ('balanced direct-output native signed 16-bit divider' if profile=='v1_balanced' else
                'fast direct-output native signed 16-bit divider; V5 repacked under 31-ZP contract' if profile=='v5_hybrid_lowzp' else
                'fast direct-output native signed 16-bit divider')
    if n in ('MATH_SDIV24','MATH_SMOD24'):
        if profile in ('v3_reu_512k','v4_reu_16m'):
            return 'Repose-derived direct-output native signed 24-bit divider with private magnitude engine'
        if profile=='v5_hybrid_lowzp':
            return 'fast direct-output native signed 24-bit divider repacked under V5 31-ZP contract'
        return ('balanced direct-output native signed 24-bit divider' if profile=='v1_balanced' else 'fast direct-output native signed 24-bit divider')
    if n in ('MATH_SDIV32_16','MATH_SMOD32_16'):
        return ('refreshed low-ZP native signed 32/16 divider retained in V5' if profile=='v5_hybrid_lowzp' else 'direct-output native signed 32/16 divider')
    if n in ('MATH_SDIV32_32','MATH_SMOD32_32'):
        return 'native signed 32/32 magnitude path with redundant zero-test removed'
    if n=='MATH_SDIV16_SHL8':
        return 'fixed-point adapter into selected native signed 32/16 divider'
    if profile=='v5_hybrid_lowzp' and n in {'MATH_UDIV16','MATH_UDIV24','MATH_UDIV32_16','MATH_UMOD8','MATH_UMOD16','MATH_UMOD24','MATH_UMOD32_16','MATH_COS8','MATH_SINCOS8','MATH_ATAN2_8'}:
        return 'V2 certified kernel imported into V5 hybrid private RAM'
    return 'profile-selected resident implementation'



def main():
    cyc=cycles_catalog(); rows=[]; summaries=[]
    mems={p:load_profile(p) for p in PROFILES}
    api_meta={r['entry']:r for r in API_ROWS}
    for p in PROFILES:
        zp_union=set(); stack_union=set(); code_union=set()
        for n,a in API.items():
            code,zp,stack=trace(mems[p],a); code_union|=code; zp_union|=zp; stack_union|=stack
            c=cyc[p][n]; meta=api_meta[n]
            rows.append({
                'profile':p,'routine':n,'canonical_name':meta.get('canonical_name',''),'api_class':'stable','signedness':meta['signedness'],'operation':meta['operation'],'width':meta['width'],
                'mean_cycles':f"{c['mean_cycles']:.6f}",'min_cycles':c['min_cycles'],'max_cycles':c['max_cycles'],'cases':c['cases'],'cycle_basis':c['cycle_basis'],
                'reachable_code_bytes':len(code),'zp_bytes':len(zp),'zp_ranges':fmt_ranges(zp),'stack_page_reserved_bytes':len(stack),
                'profile_prg_payload_span_bytes':PRG[p].stat().st_size-2,'profile_reu_image_bytes':REU[p].stat().st_size if p in REU else 0,
                'profile_declared_shared_zp_bytes':declared_zp(p),'implementation':provenance(p,n),'notes':c.get('cycle_notes','')})
        summaries.append({'profile':p,'stable_api_entries':len(API),'prg_payload_span_bytes':PRG[p].stat().st_size-2,'reu_image_bytes':REU[p].stat().st_size if p in REU else 0,
                          'declared_shared_zp_bytes':declared_zp(p),'stable_api_zp_union_touched_bytes':len(zp_union),'stable_api_zp_union_ranges':fmt_ranges(zp_union),
                          'stable_api_stack_page_reserved_union_bytes':len(stack_union),'stable_api_reachable_code_union_bytes':len(code_union)})
    # REU Turbo lifecycle surface, using validated reference timings and advertised exclusive overlay ownership.
    tv=json.loads((ROOT/'validation/turbo_relocation/TURBO_RELOCATION_VALIDATION.json').read_text())
    taddr={'MATH_REU_UMUL16_BEGIN':0x3800,'MATH_REU_UMUL16':0x3840,'MATH_REU_UMUL16_END':0x3880,'MATH_REU_UMUL32_BEGIN':0x38c0,'MATH_REU_UMUL32':0x3900,'MATH_REU_UMUL32_END':0x3960}
    for p in ['v3_reu_512k','v4_reu_16m']:
        for bits,owned in [(16,113),(32,135)]:
            d=tv['profiles'][p]['reference'][f'turbo{bits}']
            entries=[(f'MATH_REU_UMUL{bits}_BEGIN',d['begin_cycles'],d['begin_cycles'],d['begin_cycles'],1),
                     (f'MATH_REU_UMUL{bits}',d['call_mean_cycles'],d['call_min_cycles'],d['call_max_cycles'],d['cases']),
                     (f'MATH_REU_UMUL{bits}_END',d['end_cycles'],d['end_cycles'],d['end_cycles'],1)]
            base=int(d['zp_base'][1:],16); zps=set(range(base,base+owned))
            for n,mean,mn,mx,cases in entries:
                code,_,stack=trace(mems[p],taddr[n])
                rows.append({'profile':p,'routine':n,'canonical_name':PROFILE_EXTRAS[p][n],'api_class':'reu_turbo','signedness':'unsigned','operation':f'turbo multiply {bits}','width':str(bits),
                  'mean_cycles':f'{float(mean):.6f}','min_cycles':mn,'max_cycles':mx,'cases':cases,'cycle_basis':'Turbo relocation canonical reference corpus',
                  'reachable_code_bytes':len(code),'zp_bytes':owned,'zp_ranges':fmt_ranges(zps),'stack_page_reserved_bytes':len(stack),
                  'profile_prg_payload_span_bytes':PRG[p].stat().st_size-2,'profile_reu_image_bytes':REU[p].stat().st_size,
                  'profile_declared_shared_zp_bytes':declared_zp(p),'implementation':('113-ZP Turbo16 overlay' if bits==16 else '135-ZP stack-free ram135 Turbo32 record compromise'),
                  'notes':'exclusive overlay mode; ZP ownership is mode allocation, not static wrapper touch set'})
    # V4 16MiB QS16 optional surface.
    qaddr={'MATH_REU_QS16_BEGIN':0x3a80,'MATH_REU_QS16':0x3a8b,'MATH_REU_QS16_END':0x3b5c}
    qcycles={'MATH_REU_QS16_BEGIN':(18,18,18,1),'MATH_REU_QS16':(281.541031,279,293,65536),'MATH_REU_QS16_END':(18,18,18,1)}
    qzp=set(range(0x10,0x20));p='v4_reu_16m'
    for n,a in qaddr.items():
        code,_,stack=trace(mems[p],a);mean,mn,mx,cases=qcycles[n]
        rows.append({'profile':p,'routine':n,'canonical_name':PROFILE_EXTRAS[p][n],'api_class':'reu_qs16','signedness':'unsigned','operation':'V4 QS16 multiply mode','width':'16',
          'mean_cycles':f'{float(mean):.6f}','min_cycles':mn,'max_cycles':mx,'cases':cases,'cycle_basis':'V4 QS16 source/exact timing classes',
          'reachable_code_bytes':len(code),'zp_bytes':16,'zp_ranges':fmt_ranges(qzp),'stack_page_reserved_bytes':len(stack),
          'profile_prg_payload_span_bytes':PRG[p].stat().st_size-2,'profile_reu_image_bytes':REU[p].stat().st_size,
          'profile_declared_shared_zp_bytes':declared_zp(p),'implementation':'V4 16MiB QS16 mode','notes':'exclusive QS16 mode ZP ownership'})
    # No shipped routine may reserve hardware stack page under this release policy.
    bad=[(r['profile'],r['routine'],r['stack_page_reserved_bytes']) for r in rows if int(r['stack_page_reserved_bytes'])]
    if bad: raise RuntimeError(f'unexpected hardware-stack-page reservation: {bad}')
    if len(rows)!=(len(API)*len(PROFILES)+15): raise RuntimeError(f'expected {len(API)*len(PROFILES)+15} consolidated rows, got {len(rows)}')
    fields=list(rows[0])
    outcsv=ROOT/'docs/CONSOLIDATED_ROUTINE_TABLE.csv'
    with outcsv.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
    # Machine-readable evidence.
    (ROOT/'validation/CONSOLIDATED_ROUTINE_TABLE.json').write_text(json.dumps({'status':'PASS','definitions':{
      'cycles':'public entry including RTS; excludes caller JSR and input stores; see per-row cycle_basis',
      'reachable_code_bytes':'unique executable bytes statically reachable after MATH_INIT; shared code can appear on multiple rows; do not sum rows',
      'zp_bytes':'unique concrete ZP bytes executable/referenced; exclusive mode rows report owned overlay allocation',
      'stack_page_reserved_bytes':'persistent code/data reserved in $0100-$01FF; transient call/PHA traffic excluded',
      'profile_prg_payload_span_bytes':'PRG payload span, not a sum of per-routine memory'},'profile_summary':summaries,'rows':rows},indent=2)+'\n')
    # Human-readable table, one profile section each.
    md=[]
    md += ['# Consolidated routine performance and memory table','',
      'Generated from the shipped reference images by `tools/generate_consolidated_routine_table.py`. This is the single cross-profile index for cycles and resource use. Canonical typed names follow `docs/NAMING_STANDARD.md`; legacy `MATH_*` symbols remain ABI-stable.','',
      '**Memory accounting.** `Code B` is the unique executable byte set statically reachable from that entry after `MATH_INIT`; shared callees therefore appear on multiple rows and **must not be summed**. `ZP B` is the concrete page-zero set executable/referenced by the path; Turbo/QS16 rows instead report their exclusive owned overlay. `Stack B` is persistent hardware-stack-page (`$0100-$01FF`) reservation. It is **0 for every shipped choice**; ordinary transient JSR/PHA return/data stack traffic is intentionally not counted. The absolute 606.337632-cycle UMUL32 record is therefore not a shipped fixed-profile kernel because it reserves stack-page space.','',
      '**Cycle accounting.** Mean cycles include the public routine through RTS and exclude the caller JSR/input stores. The `Basis` column identifies the validation corpus/model; specialized exact/canonical source files remain authoritative for their own corpora.','',
      '## Profile-level memory contracts','',
      '| Profile | PRG payload span B | REU image B | Declared shared ZP B | Stable API ZP union touched B | Stack-page reserved B |',
      '|---|---:|---:|---:|---:|---:|']
    for s in summaries:
        md.append(f"| `{s['profile']}` | {s['prg_payload_span_bytes']} | {s['reu_image_bytes']} | {s['declared_shared_zp_bytes']} | {s['stable_api_zp_union_touched_bytes']} | {s['stable_api_stack_page_reserved_union_bytes']} |")
    for p in PROFILES:
        md += ['',f'## {p}','', '| Routine | Canonical | Mean cycles | Min | Max | Code B | ZP B | ZP range(s) | Stack B | Implementation | Basis |','|---|---|---:|---:|---:|---:|---:|---|---:|---|---|']
        for r in [x for x in rows if x['profile']==p]:
            basis=r['cycle_basis'].replace('|','/')
            impl=r['implementation'].replace('|','/')
            md.append(f"| `{r['routine']}` | `{r.get('canonical_name','')}` | {r['mean_cycles']} | {r['min_cycles']} | {r['max_cycles']} | {r['reachable_code_bytes']} | {r['zp_bytes']} | {r['zp_ranges'] or '—'} | {r['stack_page_reserved_bytes']} | {impl} | {basis} |")
    md += ['', '## Interpretation notes','',
      '- V1/V5 keep the 31-byte resident ZP contract. Their upgraded UMUL16/UMUL24 reuse that window and preserve `UMUL32_READY` state.','- V2-V4 use larger profile-selected ZP regions for some native signed/division kernels; per-routine ZP rows show the actual touched/owned set.','- V3/V4 Turbo16 owns 113 ZP bytes while active. Turbo32 now owns 135 ZP bytes (stack-free `ram135` compromise), down from the old 241-byte overlay.','- V4 QS16 owns `$10-$1F` (16 ZP bytes) while active.','- The PRG payload span includes address gaps in the load image and is not “occupied code bytes”. Use `SEGMENTS.csv` for physical segment placement and this table for per-entry reachable executable size.','']
    (ROOT/'docs/CONSOLIDATED_ROUTINE_TABLE.md').write_text('\n'.join(md))
    print('PASS',len(rows),'rows ->',outcsv)

if __name__=='__main__': main()
