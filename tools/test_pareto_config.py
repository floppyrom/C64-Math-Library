#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_pareto as bp
import assemble_sources as asm

REF=ROOT/'relocatable_source/custom_pareto/math_config_reference.inc'

def cfg_with(**changes):
    vals=asm.parse_config(REF)
    vals.update(changes)
    order=[]
    for line in REF.read_text().splitlines():
        if '=' in line and not line.lstrip().startswith(';'):
            k=line.split('=',1)[0].strip()
            if k in vals and k not in order: order.append(k)
    for k in vals:
        if k not in order: order.append(k)
    td=tempfile.TemporaryDirectory(prefix='pareto_cfg_')
    p=Path(td.name)/'math_config.inc'
    p.write_text('\n'.join(f'{k} = ${vals[k]:04X}' for k in order)+'\n')
    return td,p

def expect_fail(name,fn):
    try: fn()
    except Exception as e: return {'name':name,'status':'PASS','rejected_with':str(e)}
    raise AssertionError(f'{name}: invalid configuration was accepted')

def main():
    checks=[]
    # Selection boundary behavior.
    try:
        bp.select_packs(30,None,'auto',{})
        raise AssertionError('ZP<31 accepted')
    except ValueError as e: checks.append({'name':'reject_zp_below_v1_minimum','status':'PASS','detail':str(e)})
    s=bp.select_packs(31,0,'auto',{})
    assert s['packs']==[] and s['extra_ram']==0
    checks.append({'name':'31zp_zero_ram_selects_v1','status':'PASS'})
    target_packs={'atan2_fast','zero_zp_v5','umul32_initialized'}
    exact31=bp.exact_extra_ram_bytes(target_packs)
    s=bp.select_packs(31,exact31-1,'auto',{})
    assert set(s.get('packs',[])) != target_packs and s['extra_ram'] <= exact31-1
    checks.append({'name':f'exact_ram_budget_rejects_{exact31}_byte_choice_at_{exact31-1}','status':'PASS'})
    s=bp.select_packs(31,exact31,'auto',{})
    assert set(s['packs'])==target_packs and s['extra_ram']==exact31
    checks.append({'name':f'exact_ram_budget_accepts_{exact31}_byte_choice','status':'PASS'})
    # Valid reference/deep selections.
    vals=asm.parse_config(REF)
    bp.validate_custom_config(vals,set(bp.select_packs(31,None,'auto',{})['packs']))
    checks.append({'name':'reference_31_valid','status':'PASS'})
    bp.validate_custom_config(vals,set(bp.select_packs(176,None,'auto',{})['packs']))
    checks.append({'name':'reference_176_valid','status':'PASS'})
    # Bad private-region and ZP placements.
    td,p=cfg_with(PARETO_AUX=0xCF00)
    checks.append(expect_fail('reject_pareto_aux_cross_io',lambda: bp.validate_custom_config(asm.parse_config(p),{'umul8_16'})));td.cleanup()
    td,p=cfg_with(PARETO_AUX=0xA800)
    checks.append(expect_fail('reject_pareto_aux_hybrid_overlap',lambda: bp.validate_custom_config(asm.parse_config(p),{'zero_zp_v5','umul8_16'})));td.cleanup()
    td,p=cfg_with(PARETO_AUX=0x6000)
    checks.append(expect_fail('reject_pareto_aux_v1_region_collision',lambda: bp.validate_custom_config(asm.parse_config(p),{'umul8_16'})));td.cleanup()
    td,p=cfg_with(ZP_MAIN=0xE0)
    checks.append(expect_fail('reject_umul24_zp_overflow',lambda: bp.validate_custom_config(asm.parse_config(p),{'umul24'})));td.cleanup()
    td,p=cfg_with(ZP_SMUL=0x20)
    checks.append(expect_fail('reject_smul16_exec_zp_overlap',lambda: bp.validate_custom_config(asm.parse_config(p),{'smul16_exec'})));td.cleanup()
    td,p=cfg_with(PARETO_AUX=0xF800)
    checks.append(expect_fail('reject_pareto_aux_64k_overflow',lambda: bp.validate_custom_config(asm.parse_config(p),{'umul8_16'})));td.cleanup()
    out={'status':'PASS','tests':len(checks),'checks':checks}
    q=ROOT/'validation/pareto/PARETO_CONFIG_VALIDATION.json';q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(out,indent=2)+'\n')
    print('PARETO CONFIG PASS',len(checks),'checks')

if __name__=='__main__':main()
