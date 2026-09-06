#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,random,re,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
from assemble_sources import build,validate_config
from source_relocation import config_values,hx,REU_BANK_KEYS

PROFILES=('v3_reu_512k','v4_reu_16m')

def write_cfg(path,v):
    keys=['REG_LOW','REG_API','REG_KERNEL','REG_GAME_API','REG_TABLE','REG_GAME','MATH_IO','REU_SCRATCH','V1_SCRATCH','ZP_MAIN','ZP_SMUL','TURBO16_ZP_BASE','TURBO32_ZP_BASE']+list(REU_BANK_KEYS)
    path.write_text('\n'.join(f'{k} = {hx(v[k],2 if (k.startswith("ZP_") or k.startswith("TURBO") or k.startswith("REU_")) else 4)}' for k in keys)+'\n')

def load_prg(path):
    b=Path(path).read_bytes();load=b[0]|b[1]<<8;mem=bytearray(65536);mem[load:load+len(b)-2]=b[2:];return mem

def parse_inc(path):
    out={}
    for raw in Path(path).read_text().splitlines():
        m=re.fullmatch(r'\s*([A-Z][A-Z0-9_]*)\s*=\s*\$([0-9A-Fa-f]+)\s*',raw.split(';',1)[0])
        if m:out[m.group(1)]=int(m.group(2),16)
    return out

def put(mem,a,v,n):
    for i in range(n):mem[a+i]=(v>>(8*i))&255

def get(mem,a,n):return sum(mem[a+i]<<(8*i) for i in range(n))

def corpus(bits):
    mask=(1<<bits)-1; edge=[0,1,2,3,0x7f,0x80,0xff,0x100,0x7fff,0x8000,0xffff]
    if bits==32:edge += [0x10000,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
    edge=[x&mask for x in edge]
    out=[(x,y) for x in edge for y in edge]
    rng=random.Random(0xC64B0000+bits)
    out += [(rng.getrandbits(bits),rng.getrandbits(bits)) for _ in range(256)]
    return out

def validate_build(profile,label,v,bdir):
    inc=parse_inc(bdir/'math_api.inc');mem=load_prg(bdir/f'math_{profile}_source_built.prg');reu=bytearray((bdir/f'c64_math_{profile}_source_built.reu').read_bytes())
    cpu=CPU(mem,reu=reu);cpu.d=0;cpu.call(inc['MATH_INIT'],2_000_000)
    mx,my,mz=inc['MATH_X'],inc['MATH_Y'],inc['MATH_Z']; modes={}
    for bits,prefix,zplen in ((16,'MATH_REU_UMUL16',113),(32,'MATH_REU_UMUL32',241)):
        base=v[f'TURBO{bits}_ZP_BASE']; before=bytes(((i*37+bits+5)&255) for i in range(zplen));cpu.mem[base:base+zplen]=before
        begin,call,end=inc[prefix+'_BEGIN'],inc[prefix],inc[prefix+'_END'];cb=cpu.call(begin,2_000_000);installed=bytes(cpu.mem[base:base+zplen]);
        if installed==before:raise AssertionError(f'{profile}/{label}/T{bits}: overlay not installed')
        cyc=[]
        for x,y in corpus(bits):
            put(cpu.mem,mx,x,bits//8);put(cpu.mem,my,y,bits//8);cyc.append(cpu.call(call,2_000_000));got=get(cpu.mem,mz,bits//4);want=x*y
            if got!=want:raise AssertionError(f'{profile}/{label}/T{bits}: {x:#x}*{y:#x} -> {got:#x} != {want:#x}')
        ce=cpu.call(end,2_000_000)
        if bytes(cpu.mem[base:base+zplen])!=before:raise AssertionError(f'{profile}/{label}/T{bits}: END restore')
        modes[f'turbo{bits}']={'cases':len(corpus(bits)),'zp_base':f'${base:02X}','zp_end':f'${base+zplen-1:02X}','reu_bank':f'${v[f"REU_TURBO{bits}_BANK"]:02X}','begin_cycles':cb,'end_cycles':ce,'mean_cycles':sum(cyc)/len(cyc),'min_cycles':min(cyc),'max_cycles':max(cyc),'cycle_vector_sha256':hashlib.sha256(','.join(map(str,cyc)).encode()).hexdigest(),'overlay_sha256':hashlib.sha256(installed).hexdigest()}
    return modes

def maps(profile):
    lo=config_values(profile,True);lo['TURBO16_ZP_BASE']=0x02;lo['TURBO32_ZP_BASE']=0x02
    hi=config_values(profile,False);hi['TURBO16_ZP_BASE']=0x8f;hi['TURBO32_ZP_BASE']=0x0f
    if profile=='v3_reu_512k':
        hi.update(REU_UMUL8_LO_BANK=0,REU_UMUL8_HI_BANK=1,REU_UDIV8_Q_BANK=2,REU_UDIV8_R_BANK=3,REU_RECIP_LO_BANK=4,REU_RECIP_HI_BANK=5,REU_TURBO16_BANK=6,REU_TURBO32_BANK=7)
    else:
        hi.update(REU_TURBO16_BANK=0xfe,REU_TURBO32_BANK=0xff)
    return [('minimum_origins',lo),('maximum_origins',hi)]

def main():
    out={'status':'PASS','profiles':{},'statement':'Representative edge proof: both Turbo ZP origins execute at their minimum and maximum legal bases; V3 also exercises Turbo banks 6/7 and V4 exercises banks $FE/$FF.'}
    with tempfile.TemporaryDirectory(prefix='c64math-turbo-boundary-') as td0:
        td=Path(td0)
        for p in PROFILES:
            out['profiles'][p]={}
            for label,v in maps(p):
                validate_config(p,v);cfg=td/f'{p}_{label}.inc';write_cfg(cfg,v);bdir=td/p/label;build(p,cfg,bdir);r=validate_build(p,label,v,bdir);out['profiles'][p][label]=r;print(p,label,'PASS',r['turbo16']['zp_base'],r['turbo32']['zp_base'],r['turbo16']['reu_bank'],r['turbo32']['reu_bank'])
            # Origin changes are zero-cost on identical per-mode corpus.
            a=out['profiles'][p]['minimum_origins'];b=out['profiles'][p]['maximum_origins']
            for t in ('turbo16','turbo32'):
                if a[t]['cycle_vector_sha256']!=b[t]['cycle_vector_sha256'] or a[t]['begin_cycles']!=b[t]['begin_cycles'] or a[t]['end_cycles']!=b[t]['end_cycles']:
                    raise AssertionError(f'{p}/{t}: boundary origin changed cycle vector')
    out['total_product_calls']=sum(x['cases'] for p in out['profiles'].values() for m in p.values() for x in m.values())
    path=ROOT/'validation/turbo_relocation/TURBO_BOUNDARY_SWEEP.json';path.write_text(json.dumps(out,indent=2)+'\n');print('TURBO BOUNDARY SWEEP PASS',out['total_product_calls'],'products')
if __name__=='__main__':main()
