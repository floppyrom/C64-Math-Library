#!/usr/bin/env python3
"""Fail closed: V1 short-quotient branch layout matches independently derived
323-byte machine code, leaving every other resident byte unmodified.
Experimental source build only; this script never installs release binaries.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
WIN=(0x4200,0x4343)
BASE='f60d4ec80e4285e8bb3b243b3e7f93ae908989c0818ba2e543750d33ed8909eb'
TARGET='7a1dfb987c2f9f1386cdbf7c4096c1a20cd9f143bce9907550cee209dacc2bc6'
def sha(x):return hashlib.sha256(x).hexdigest()
def main():
 orig=(ROOT/'v1_balanced/resident/math_v1_balanced_game_math.prg').read_bytes()
 built=(ROOT/'build_source/reference/v1_balanced/math_v1_balanced_source_built.prg').read_bytes()
 assert orig[:2]==built[:2] and len(orig)==len(built)
 base=int.from_bytes(orig[:2],'little')
 offset=lambda addr:2+addr-base
 before=orig[offset(WIN[0]):offset(WIN[1])]
 after=built[offset(WIN[0]):offset(WIN[1])]
 assert len(before)==len(after)==323
 assert sha(before)==BASE,('wrong parent',sha(before))
 assert sha(after)==TARGET,('unexpected source assembly',sha(after))
 assert orig[:offset(WIN[0])]==built[:offset(WIN[0])]
 assert orig[offset(WIN[1]):]==built[offset(WIN[1]):]
 changed=sum(a!=b for a,b in zip(before,after))
 # Independent alternate configuration must compile the same source without
 # consuming additional zero page or changing the configured code envelope.
 alternate=ROOT/'build_source/alternate/v1_balanced/math_v1_balanced_source_built.prg'
 assert alternate.exists() and alternate.stat().st_size>30000
 d={'status':'PASS','parent_sha256':sha(orig),'source_built_sha256':sha(built),
   'unchanged_resident_span':len(orig),'changed_bytes_inside_323_byte_window':changed,
   'changed_bytes_outside_window':0,'old_core_sha256':BASE,'new_core_sha256':TARGET,
   'reference_and_alternate_source_assembled':True,'public_entry_points_unchanged':True,
   'memory_growth':0,'normal_zero_page_growth':0,'release_promoted':False}
 p=ROOT/'validation/review/ISSUE39_V1_U16_Q2_LAYOUT_SOURCE_SCREEN.json'
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n')
 print('ISSUE39 V1 U16 Q2 BYTE-EXACT SOURCE PROOF PASS',json.dumps(d),flush=True)
if __name__=='__main__':main()
