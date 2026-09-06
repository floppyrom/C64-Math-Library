#!/usr/bin/env python3
from pathlib import Path
import json
from source_relocation import ROOT,PROFILES,generate_source,write_config
out=[]
for p in PROFILES:
 d=ROOT/'relocatable_source'/p;d.mkdir(parents=True,exist_ok=True)
 src=d/'math_relocatable.asm';r=generate_source(p,src)
 write_config(p,d/'math_config.inc',False);write_config(p,d/'math_config_reference.inc',False);write_config(p,d/'math_config_alternate.inc',True)
 out.append(r);print(p,'SOURCE',r['reachable_instructions'])
(ROOT/'relocatable_source/SOURCE_GENERATION.json').write_text(json.dumps({'status':'PASS','profiles':out},indent=2)+'\n')
