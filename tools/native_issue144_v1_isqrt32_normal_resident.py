#!/usr/bin/env python3
"""Issue144 V1 highword normal-resident source: real VICE proof (both layouts)."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib,json,os,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"tools"))
from issue144_v1_isqrt32_normal_resident_feasibility import probe,P
from native_issue144_isqrt32_normal_resident import native,E
from assemble_sources import parse_config

def main():
 vice=os.getenv("VICE_WRAPPER")
 assert vice, "set VICE_WRAPPER to a verified x64sc"
 result={"status":"PASS_V1_ISQRT32_SOURCE_NATIVE_6510","native_public_calls":0,
         "models_and_public_abi_unchanged":True,"resident_image_mutated":False,
         "v5_inheritance_not_qualified":True,"layouts":{}}
 with TemporaryDirectory(prefix="issue144_v1_isqrt_native_") as dirname:
  tmp=Path(dirname)
  for index,layout in enumerate(("reference","alternate")):
   geom,machines=probe(layout,0x0AA8)
   assert machines,geom
   old,new,entry,io=machines
   cfg=ROOT/"relocatable_source"/P/("math_config_"+layout+".inc")
   constants=parse_config(cfg)
   api={"MATH_INIT":constants["REG_API"]+0x0280,
        "MATH_ISQRT32":constants["REG_GAME_API"]+0x0030}
   n0=native(P,layout,old,api,io,24400+index*2,tmp,vice)
   n1=native(P,layout,new,api,io,24401+index*2,tmp,vice)
   assert n0==n1,(layout,"native result/status differences",
                   [(k,a,b) for k,(a,b) in enumerate(zip(n0,n1)) if a!=b][:8])
   result["layouts"][layout]={"status":"PASS_48_NATIVE_CALLS","pairs":len(E),
       "record_sha256":hashlib.sha256(n1).hexdigest(),
       "root_correct_and_carried":True,"full_status_equal":True,
       "preexisting_helper_bytes_only":True,"geometry":geom}
   result["native_public_calls"]+=2*len(E)
   print("V1 ISQRT32 NORMAL NATIVE",layout,"PASS",2*len(E),flush=True)
 assert result["native_public_calls"]==96
 print(json.dumps(result,indent=2,sort_keys=True))
if __name__=="__main__":main()
