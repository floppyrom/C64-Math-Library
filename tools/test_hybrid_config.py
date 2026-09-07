#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import assemble_sources as asm
import build_hybrid as hy

base=asm.parse_config(ROOT/'relocatable_source/v5_hybrid_lowzp/math_config_reference.inc')
tests=[]
def ok(name,vals):
    hy.validate_hybrid_region(vals,vals['HYBRID_CODE']);tests.append({'name':name,'expected':'accept','status':'PASS'})
def bad(name,vals,needle=None):
    try:hy.validate_hybrid_region(vals,vals['HYBRID_CODE'])
    except Exception as e:
        if needle and needle.lower() not in str(e).lower():raise AssertionError((name,str(e),needle))
        tests.append({'name':name,'expected':'reject','status':'PASS','error':str(e)});return
    raise AssertionError(f'{name}: invalid config accepted')

ok('reference_map',dict(base))
alt=asm.parse_config(ROOT/'relocatable_source/v5_hybrid_lowzp/math_config_alternate.inc');ok('alternate_map',alt)
v=dict(base);v['HYBRID_CODE']=0xA001;bad('unaligned_hybrid_code',v,'page aligned')
v=dict(base);v['HYBRID_CODE']=0xF000;bad('hybrid_overflow',v,'exceeds')
v=dict(base);v['HYBRID_CODE']=0xD000;bad('io_overlap',v,'D000')
v=dict(base);v['HYBRID_CODE']=0x9000;bad('table_overlap',v,'collides')
v=dict(base);v['HYBRID_CODE']=0x3000;bad('api_overlap',v,'collides')
v=dict(base);v['HYBRID_CODE']=0x5E00;bad('kernel_overlap',v,'collides')
out={'status':'PASS','tests':len(tests),'cases':tests}
(ROOT/'validation/hybrid/HYBRID_CONFIG_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
print('HYBRID CONFIG PASS',len(tests),'cases')
