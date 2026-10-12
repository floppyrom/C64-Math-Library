#!/usr/bin/env python3
"""Optional native x64sc correctness on two standalone UMOD16 direct-chain maps."""
from pathlib import Path
import tempfile,os,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"tools"))
from native_vice import check,VICE
from verify_umod16_direct_zerozp import MAPS,assemble
def main():
 assert os.environ.get("VICE_WRAPPER") and VICE.is_file(),"Set VICE_WRAPPER to x64sc launcher"
 with tempfile.TemporaryDirectory(prefix="umod16_direct_vice_") as folder:
  total=0
  for i,spec in enumerate(MAPS[:2]):
   name,code,table,adapter,buf,mean=spec
   if i:buf=0xc050 # avoid monitor-harness capture RAM $3800-$3A7F
   img,labels,mp=assemble((name,code,table,adapter,buf,mean))
   mem=bytearray(65536)
   for a,b in img.items():mem[a]=b
   row=check(mem,labels["FAST_UMOD16_DIRECT_PUBLIC"],16,mp,"umod16_direct_"+name,7850+i,Path(folder),True)
   assert row["cases"]==96
   total+=row["cases"]
   print("NATIVE VICE PASS",name,row["cases"],row["output_sha256"],flush=True)
  assert total==192
  print("NATIVE VICE UMOD16 DIRECT PASS 192 Q/R/C calls; no native timing claim")
if __name__=="__main__":main()
