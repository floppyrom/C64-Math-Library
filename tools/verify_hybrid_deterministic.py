#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,shutil,tempfile,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_hybrid as hy
checks=[]
for kind in ('reference','alternate'):
    cfg=ROOT/'relocatable_source/v5_hybrid_lowzp'/f'math_config_{kind}.inc'
    canonical=ROOT/'build_hybrid'/kind/'v5_hybrid_lowzp'/'math_v5_hybrid_lowzp_game_math.prg'
    if not canonical.exists(): hy.build(cfg,ROOT/'build_hybrid'/kind/'v5_hybrid_lowzp')
    with tempfile.TemporaryDirectory(prefix='hybrid_repeat_') as td:
        out=Path(td)/'v5_hybrid_lowzp';m=hy.build(cfg,out);repeat=out/m['output_prg']
        same=canonical.read_bytes()==repeat.read_bytes();assert same,(kind,'non-deterministic')
        checks.append({'kind':kind,'byte_identical':True,'sha256':hashlib.sha256(canonical.read_bytes()).hexdigest()})
out={'status':'PASS','checks':checks}
p=ROOT/'validation/hybrid/HYBRID_DETERMINISTIC_REBUILD.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2)+'\n')
print('HYBRID DETERMINISTIC PASS',len(checks),'maps')
