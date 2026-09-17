#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib, json, math, random, shutil, sys, tempfile, time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from mini6502 import CPU
import source_relocation as sr
import validate_source_build as common
import build_pareto as bp

POINTS=[31,36,60,147,176,221]
MASK=lambda b:(1<<b)-1

def un(v): return int(v[1:],16) if isinstance(v,str) and v.startswith('$') else int(v)
def wr(c,a,v,n):
    for i in range(n): c.mem[a+i]=(v>>(8*i))&255
def rd(c,a,n): return sum(c.mem[a+i]<<(8*i) for i in range(n))

def build_point(z:int,kind:str,outname:str|None=None,**kw):
    sel=bp.select_packs(z,kw.get('ram_budget'),kw.get('init_policy','auto'),kw.get('weights',{}));sel['zp_budget_requested']=z
    cfg=ROOT/'relocatable_source/custom_pareto'/f'math_config_{kind}.inc'
    out=ROOT/'build_pareto'/(outname or f'cert_zp{z}_{kind}')
    if out.exists(): shutil.rmtree(out)
    if sel['mode']=='v2_full': man=bp.build_full_v2(cfg,out,sel)
    else: man=bp.build_hybrid_custom(cfg,out,sel)
    return out,man

def common_validate(out:Path):
    with tempfile.TemporaryDirectory(prefix='pareto_common_') as td:
        p=Path(td)/'custom_pareto'; shutil.copytree(out,p)
        return common.validate('custom_pareto',Path(td))

def load_custom(out:Path,do_init=True):
    m=json.loads((out/'selection_manifest.json').read_text()); b=(out/m['output_prg']).read_bytes(); ld=b[0]|b[1]<<8
    mem=bytearray(65536);mem[ld:ld+len(b)-2]=b[2:]; c=CPU(mem);c.d=0
    P={k:un(v) for k,v in m['public_entries'].items()}; I=un(m['public_io'].split('-')[0]); init=un(m['math_init'])
    if do_init:
        c.call(init,2_000_000); assert c.c==0
    return c,P,I,m

def load_v2():
    _,init=sr.load_reference('v2_pareto_fast'); c=CPU(bytearray(init));c.d=0
    return c,dict(sr.public_entries()),0xC000

def signed(v,b): return v-(1<<b) if v&(1<<(b-1)) else v

def parity_tests(out:Path,random_per=500):
    c,P,I,M=load_custom(out); v,P2,I2=load_v2(); rng=random.Random(0xC64F17)
    detail={}; total=0
    muls=[('MATH_UMUL8',8,False),('MATH_UMUL16',16,False),('MATH_UMUL24',24,False),('MATH_UMUL32',32,False),
          ('MATH_SMUL8',8,True),('MATH_SMUL16',16,True),('MATH_SMUL24',24,True),('MATH_SMUL32',32,True)]
    for name,bits,sgn in muls:
        n=bits//8
        for _ in range(random_per):
            x=rng.randrange(1<<bits);y=rng.randrange(1<<bits)
            wr(c,I,x,n);wr(c,I+4,y,n);cy=c.call(P[name],2_000_000);o=rd(c,I+8,2*n);cc=c.c
            wr(v,I2,x,n);wr(v,I2+4,y,n);cy2=v.call(P2[name],2_000_000);o2=rd(v,I2+8,2*n);cc2=v.c
            assert (cy,o,cc)==(cy2,o2,cc2),(name,x,y,cy,cy2,hex(o),hex(o2),cc,cc2)
        detail[name]={'cases':random_per,'cycle_vector_equal_to_v2':True};total+=random_per
    for name,nb,db in [('MATH_UDIV16',16,16),('MATH_UDIV24',24,24),('MATH_UDIV32_16',32,16)]:
        nn=nb//8;dn=db//8
        for _ in range(random_per):
            n=rng.randrange(1<<nb);d=rng.randrange(1<<db)
            wr(c,I+0x10,n,nn);wr(c,I+0x14,d,dn);cy=c.call(P[name],2_000_000);o=(rd(c,I+0x18,nn),rd(c,I+0x1c,dn),c.c)
            wr(v,I2+0x10,n,nn);wr(v,I2+0x14,d,dn);cy2=v.call(P2[name],2_000_000);o2=(rd(v,I2+0x18,nn),rd(v,I2+0x1c,dn),v.c)
            assert (cy,o)==(cy2,o2),(name,n,d,cy,cy2,o,o2)
        detail[name]={'cases':random_per,'cycle_vector_equal_to_v2':True};total+=random_per
    # UMOD8 full domain is retained from V5; sample cycle parity here, full correctness below.
    for _ in range(4096):
        n=rng.randrange(256);d=rng.randrange(256)
        wr(c,I+0x10,n,1);wr(c,I+0x14,d,1);cy=c.call(P['MATH_UMOD8'],10000);o=(c.mem[I+0x1c],c.c)
        wr(v,I2+0x10,n,1);wr(v,I2+0x14,d,1);cy2=v.call(P2['MATH_UMOD8'],10000);o2=(v.mem[I2+0x1c],v.c)
        assert (cy,o)==(cy2,o2)
    detail['MATH_UMOD8']={'cases':4096,'cycle_vector_equal_to_v2':True};total+=4096
    for name in ('MATH_COS8','MATH_SINCOS8'):
        for ph in range(256):
            c.mem[I]=ph;cy=c.call(P[name],10000);o=bytes(c.mem[I+8:I+10]);cc=c.c
            v.mem[I2]=ph;cy2=v.call(P2[name],10000);o2=bytes(v.mem[I2+8:I2+10]);cc2=v.c
            assert (cy,o,cc)==(cy2,o2,cc2),(name,ph,cy,cy2,o,o2)
        detail[name]={'cases':256,'cycle_vector_equal_to_v2':True,'full_phase_domain':True};total+=256
    # The deep standard point selects atan2_fast.  Exhaustively prove both the
    # donor cycle vector and the <=1 phase-unit public accuracy contract.
    atan_total=0; atan_min=10**9; atan_max=0; maxerr=0
    for rx in range(256):
        sx=rx if rx<128 else rx-256
        for ry in range(256):
            sy=ry if ry<128 else ry-256
            c.mem[I]=rx;c.mem[I+4]=ry;cy=c.call(P['MATH_ATAN2_8'],10000);o=c.mem[I+8];cc=c.c
            v.mem[I2]=rx;v.mem[I2+4]=ry;cy2=v.call(P2['MATH_ATAN2_8'],10000);o2=v.mem[I2+8];cc2=v.c
            exp=0 if sx==0 and sy==0 else round((math.atan2(sy,sx)%(2*math.pi))*128/math.pi)&255
            er=min((o-exp)&255,(exp-o)&255)
            assert (cy,o,cc)==(cy2,o2,cc2),('MATH_ATAN2_8',rx,ry,cy,cy2,o,o2,cc,cc2)
            assert er<=1,('MATH_ATAN2_8',rx,ry,o,exp,er)
            atan_total+=cy;atan_min=min(atan_min,cy);atan_max=max(atan_max,cy);maxerr=max(maxerr,er)
    detail['MATH_ATAN2_8']={'cases':65536,'cycle_vector_equal_to_v2':True,'exhaustive':True,'mean_cycles':atan_total/65536,'min_cycles':atan_min,'max_cycles':atan_max,'max_phase_error':maxerr};total+=65536
    return {'status':'PASS','cases':total,'routines':detail}

def exhaustive_umod8(out:Path):
    c,P,I,M=load_custom(out);count=0
    for n in range(256):
        for d in range(256):
            c.mem[I+0x10]=n;c.mem[I+0x14]=d;c.call(P['MATH_UMOD8'],10000);r=c.mem[I+0x1c]
            assert (c.c==1 and r==0) if d==0 else (c.c==0 and r==n%d)
            count+=1
    return count

def zp_guard(out:Path,iterations=3000):
    c,P,I,M=load_custom(out); ranges=[]
    for r in M.get('zp_ranges',[]): ranges.append((un(r['start']),un(r['end'])))
    outside=[x for x in range(256) if not any(a<=x<=b for a,b in ranges)]
    for x in outside: c.mem[x]=(x*109+41)&255
    snap=bytes(c.mem[x] for x in outside); rng=random.Random(0x5A5047)
    for i in range(iterations):
        mode=i%8
        if mode==0:
            x=rng.randrange(1<<16);y=rng.randrange(1<<16);wr(c,I,x,2);wr(c,I+4,y,2);c.call(P['MATH_UMUL16'],100000)
        elif mode==1:
            x=rng.randrange(1<<24);y=rng.randrange(1<<24);wr(c,I,x,3);wr(c,I+4,y,3);c.call(P['MATH_UMUL24'],200000)
        elif mode==2:
            x=rng.randrange(1<<32);y=rng.randrange(1<<32);wr(c,I,x,4);wr(c,I+4,y,4);c.call(P['MATH_UMUL32'],200000)
        elif mode==3:
            x=rng.randrange(1<<16);y=rng.randrange(1<<16);wr(c,I,x,2);wr(c,I+4,y,2);c.call(P['MATH_SMUL16'],200000)
        elif mode==4:
            n=rng.randrange(1<<32);d=rng.randrange(1<<16);wr(c,I+0x10,n,4);wr(c,I+0x14,d,2);c.call(P['MATH_UDIV32_16'],2_000_000)
        elif mode==5:
            c.mem[I]=rng.randrange(256);c.call(P['MATH_SINCOS8'],10000)
        elif mode==6:
            n=rng.randrange(1<<32);wr(c,I+0x10,n,4);c.call(P['MATH_ISQRT32'],100000)
        else:
            n=rng.randrange(256);d=rng.randrange(256);c.mem[I+0x10]=n;c.mem[I+0x14]=d;c.call(P['MATH_UMOD8'],10000)
    assert bytes(c.mem[x] for x in outside)==snap,'outside-ZP corruption'
    return {'reserved_ranges':M.get('zp_ranges',[]),'outside_bytes_unchanged':len(outside),'iterations':iterations}

def selection_tests():
    cases=[]
    def ck(z,expect,**kw):
        s=bp.select_packs(z,kw.get('ram'),kw.get('init','auto'),kw.get('weights',{})); got=set(s.get('packs',[])) if s['mode']=='hybrid' else {'v2_full'}
        assert got==set(expect),(z,got,expect,s);cases.append({'zp_budget':z,'expected':expect,'result':s})
    ck(31,['atan2_fast','umul32_initialized','zero_zp_v5'])
    ck(36,['atan2_fast','umul32_initialized','umul8_16','zero_zp_v5'])
    ck(60,['atan2_fast','umul24','umul32_initialized','umul8_16','zero_zp_v5'])
    ck(147,['atan2_fast','smul16_exec','umul32_initialized','zero_zp_v5'])
    ck(176,['atan2_fast','smul16_exec','umul24','umul32_initialized','umul8_16','zero_zp_v5'])
    ck(221,['v2_full'])
    ck(31,[],ram=0)
    ck(31,['atan2_fast','zero_zp_v5'],init='optional')
    # Workload hint must change the 55-byte choice from UMUL8/16 to UMUL24.
    w={'MATH_UMUL24':100,'MATH_UMUL8':0,'MATH_UMUL16':0,'MATH_SMUL8':0,'MATH_UMUL16_SHR8':0}
    ck(55,['atan2_fast','umul24','umul32_initialized','zero_zp_v5'],weights=w)
    return cases

def deterministic(points=(31,176,221)):
    out=[]
    for kind in ('reference','alternate'):
        for z in points:
            a,ma=build_point(z,kind,f'det_a_{kind}_{z}'); b,mb=build_point(z,kind,f'det_b_{kind}_{z}')
            ha=hashlib.sha256((a/ma['output_prg']).read_bytes()).hexdigest();hb=hashlib.sha256((b/mb['output_prg']).read_bytes()).hexdigest()
            assert ha==hb,(kind,z,ha,hb);out.append({'map':kind,'zp_budget':z,'sha256':ha,'identical':True})
    return out

def main():
    t=time.time(); result={'status':'PASS','standard_points':{},'selection_tests':selection_tests()}
    # Build and common-validate standard Pareto points on both maps.
    total_calls=0
    for kind in ('reference','alternate'):
        result['standard_points'][kind]={}
        for z in POINTS:
            out,man=build_point(z,kind); r=common_validate(out);total_calls+=r['machine_calls']; print('matrix',kind,z,'PASS',r['machine_calls'],flush=True)
            result['standard_points'][kind][str(z)]={'selected_packs':man['selected_packs'],'zp_bytes':man['zp_bytes_reserved'],'extra_private_ram_bytes':man.get('extra_main_ram_bytes'),'init_required':man['math_init_required'],'common_api':{'entries':r['public_entries_executed'],'calls':r['machine_calls']},'sha256':man['output_sha256']}
    # Deep parity/stress uses the all-certified-pack 176-byte reference build.
    deep=ROOT/'build_pareto/cert_zp176_reference'
    result['direct_v2_cycle_parity']=parity_tests(deep)
    result['umod8_exhaustive_cases']=exhaustive_umod8(deep)
    result['zp_confinement']=zp_guard(deep)
    # Pure V1 and optional-init endpoints should be byte-identical to their canonical bases.
    pure,pm=build_point(31,'reference','cert_pure_v1',ram_budget=0)
    v1raw=ROOT/'v1_balanced/resident/math_v1_balanced_game_math.prg'
    result['pure_v1_identity']=hashlib.sha256((pure/pm['output_prg']).read_bytes()).hexdigest()==hashlib.sha256(v1raw.read_bytes()).hexdigest()
    assert result['pure_v1_identity']
    opt_sel=bp.select_packs(31,None,'optional',{});opt_sel['zp_budget_requested']=31
    opt=ROOT/'build_pareto/cert_optional31';
    if opt.exists():shutil.rmtree(opt)
    om=bp.build_hybrid_custom(ROOT/'relocatable_source/custom_pareto/math_config_reference.inc',opt,opt_sel)
    v5raw=ROOT/'v5_hybrid_lowzp/resident/math_v5_hybrid_lowzp_game_math.prg'
    result['optional31_v5_identity']=hashlib.sha256((opt/om['output_prg']).read_bytes()).hexdigest()==hashlib.sha256(v5raw.read_bytes()).hexdigest()
    assert result['optional31_v5_identity']
    result['deterministic_rebuilds']=deterministic(points=(31,176))
    result['common_api_machine_calls']=total_calls
    result['elapsed_seconds']=round(time.time()-t,3)
    p=ROOT/'validation/pareto/PARETO_SELECTOR_VALIDATION.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
    print('PARETO SELECTOR PASS',json.dumps({'standard_builds':len(POINTS)*2,'common_api_calls':total_calls,'direct_parity_cases':result['direct_v2_cycle_parity']['cases'],'umod8':result['umod8_exhaustive_cases'],'elapsed_seconds':result['elapsed_seconds']}))

if __name__=='__main__': main()
