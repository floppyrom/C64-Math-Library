#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile
ROOT = Path(__file__).resolve().parents[1]
PROFILES = ['v1_balanced','v2_pareto_fast','v3_reu_512k','v4_reu_16m']

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run_build(out, kind):
    subprocess.run([sys.executable, str(ROOT/'tools/assemble_sources.py'), '--profile','all','--config-kind',kind,'--out',str(out)], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)

def main():
    subprocess.run([sys.executable, str(ROOT/'tools/generate_sources.py')], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    checks=[]
    with tempfile.TemporaryDirectory(prefix='c64math_det_a_') as a, tempfile.TemporaryDirectory(prefix='c64math_det_b_') as b:
        a=Path(a); b=Path(b)
        for kind in ('reference','alternate'):
            run_build(a,kind); run_build(b,kind)
            for p in PROFILES:
                pa=a/kind/p/f'math_{p}_source_built.prg'; pb=b/kind/p/f'math_{p}_source_built.prg'
                h=sha(pa); same=pa.read_bytes()==pb.read_bytes()
                ref_same=None
                if kind=='reference':
                    resident=ROOT/p/'resident'/f'math_{p}_game_math.prg'
                    ref_same=pa.read_bytes()==resident.read_bytes()
                reu_a=a/kind/p/f'c64_math_{p}_source_built.reu'; reu_b=b/kind/p/f'c64_math_{p}_source_built.reu'
                reu_hash=sha(reu_a) if reu_a.exists() else None
                reu_same=(reu_a.read_bytes()==reu_b.read_bytes()) if reu_a.exists() else None
                ref_reu_same=None
                if kind=='reference' and reu_a.exists():
                    refname='c64_math_v3_512k_game_math.reu' if p=='v3_reu_512k' else 'c64_math_v4_16m_game_math.reu'
                    bundled=ROOT/p/'reu'/refname
                    ref_reu_same=reu_a.read_bytes()==bundled.read_bytes()
                ok=same and (ref_same is not False) and (reu_same is not False) and (ref_reu_same is not False)
                checks.append({'kind':kind,'profile':p,'status':'PASS' if ok else 'FAIL','prg_sha256':h,'repeat_prg_identical':same,'reference_prg_identical':ref_same,'reu_sha256':reu_hash,'repeat_reu_identical':reu_same,'reference_reu_identical':ref_reu_same})
    status='PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL'
    out={'status':status,'statement':'Two clean source builds are byte-identical for every reference/alternate PRG and generated REU image; reference builds also reproduce the bundled fast-ISQRT32 resident PRG/REU artifacts exactly.','checks':checks}
    path=ROOT/'validation/source_relocation/DETERMINISTIC_REBUILD.json'; path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(out,indent=2)+'\n')
    print('DETERMINISTIC REBUILD',status,len(checks),'checks')
    if status!='PASS': raise SystemExit(1)
if __name__=='__main__': main()
