#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from source_relocation import config_values
from assemble_sources import validate_config

CASES=[]
def expect_fail(name,profile,mut):
 v=config_values(profile,False);mut(v)
 try: validate_config(profile,v)
 except Exception as e: CASES.append({'name':name,'profile':profile,'status':'PASS','rejected_with':str(e)});return
 raise AssertionError(f'{name}: invalid config was accepted')
def expect_pass(name,profile,v):
 validate_config(profile,v);CASES.append({'name':name,'profile':profile,'status':'PASS'})

for p in ('v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m'):
 expect_pass('reference config accepted',p,config_values(p,False))
 expect_pass('alternate config accepted',p,config_values(p,True))
expect_fail('page alignment enforced','v2_pareto_fast',lambda v:v.__setitem__('REG_GAME',v['REG_GAME']+1))
expect_fail('main-region collision rejected','v2_pareto_fast',lambda v:v.__setitem__('REG_TABLE',v['REG_KERNEL']))
expect_fail('ZP wrap rejected','v2_pareto_fast',lambda v:v.__setitem__('ZP_SMUL',0xF0))
expect_fail('ZP overlap rejected','v2_pareto_fast',lambda v:v.__setitem__('ZP_SMUL',0x60))
expect_fail('6510 processor port protected','v1_balanced',lambda v:v.__setitem__('ZP_MAIN',0x01))
expect_fail('V1 scratch/I-O collision rejected','v1_balanced',lambda v:v.__setitem__('MATH_IO',v['V1_SCRATCH']))
expect_fail('REU I/O page protected','v3_reu_512k',lambda v:v.__setitem__('MATH_IO',0xDF00))
expect_fail('V3 bank >7 rejected','v3_reu_512k',lambda v:v.__setitem__('REU_RECIP_HI_BANK',8))
expect_fail('V3 operational bank collision rejected','v3_reu_512k',lambda v:v.__setitem__('REU_RECIP_HI_BANK',5))
expect_fail('V3 duplicate stable bank rejected','v3_reu_512k',lambda v:v.__setitem__('REU_RECIP_HI_BANK',v['REU_RECIP_LO_BANK']))
expect_fail('V4 QS16 alignment enforced','v4_reu_16m',lambda v:v.__setitem__('REU_QS16_BASE_BANK',0x31))
expect_fail('V4 QS16/single-bank collision rejected','v4_reu_16m',lambda v:v.__setitem__('REU_QS16_BASE_BANK',0x20) or v.__setitem__('REU_UMUL8_LO_BANK',0x20))
expect_fail('V4 operational bank collision rejected','v4_reu_16m',lambda v:v.__setitem__('REU_ATAN2_BANK',4))
expect_fail('Turbo16 processor-port overlap rejected','v3_reu_512k',lambda v:v.__setitem__('TURBO16_ZP_BASE',0x01))
expect_fail('Turbo16 ZP wrap rejected','v3_reu_512k',lambda v:v.__setitem__('TURBO16_ZP_BASE',0x90))
expect_fail('Turbo32 processor-port overlap rejected','v3_reu_512k',lambda v:v.__setitem__('TURBO32_ZP_BASE',0x01))
expect_fail('Turbo32 ZP wrap rejected','v3_reu_512k',lambda v:v.__setitem__('TURBO32_ZP_BASE',0x7a))
expect_fail('V3 Turbo bank >7 rejected','v3_reu_512k',lambda v:v.__setitem__('REU_TURBO16_BANK',8))
expect_fail('V4 Turbo/QS16 bank collision rejected','v4_reu_16m',lambda v:v.__setitem__('REU_TURBO32_BANK',v['REU_QS16_BASE_BANK']))
out={'status':'PASS','tests':len(CASES),'cases':CASES}
(ROOT/'validation'/'CONFIG_VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS',len(CASES),'config validation cases')
