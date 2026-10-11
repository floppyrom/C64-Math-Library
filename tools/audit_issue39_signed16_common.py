#!/usr/bin/env python3
"""Issue39 signed 16/16 DIV/MOD five-profile identical-input screen.

Recomputes *actual public-entry* NMOS 6502 instruction cycles from the
shipped initialized resident on exactly identical numerator/divisor pairs.
Unlike validate_signed_division.py this intentionally never varies the
operand RNG seed by profile. This report does not promote code changes.
"""
from pathlib import Path
import csv, hashlib, json, random, sys
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from validate_signed_division import load_profile, div_expected, wr, rd, sgn, PROFILES
ROUTINES=('MATH_SDIV16','MATH_SMOD16')
N,D,Q,R=0xC010,0xC014,0xC018,0xC01C
J=ROOT/'validation/review/ISSUE39_SIGNED16_SAME_INPUT_AUDIT.json'
C=ROOT/'benchmarks/ISSUE39_SIGNED16_SAME_INPUT_AUDIT.csv'

def cases():
    rng=random.Random(0xC6391627)
    edges=[0,1,2,3,7,15,16,31,63,127,128,255,256,257,1023,4095,16384,32766,32767,32768,32769,65533,65534,65535]
    out=[(a,b) for a in edges for b in edges]
    out.extend((rng.randrange(65536),rng.randrange(65536)) for _ in range(2048))
    for d in [-32768,-16384,-1024,-257,-255,-17,-7,-2,-1,1,2,7,17,255,257,1024,16384,32767]:
        for q in [0,1,2,3,4,7,8,15,31,127]:
            for sign in (-1,1):
                for delta in (-1,0,1):
                    n=sign*(abs(d)*q+delta)
                    if -32768<=n<=32767:
                        out.append((n&65535,d&65535))
    for i in range(2048):
        d=rng.choice((-1,1))*rng.randint(1,32768)
        n=rng.randrange(-32768,32768)
        out.append((n&65535,d&65535))
    out.extend((rng.randrange(65536),0) for _ in range(128))
    return list(dict.fromkeys(out))

def group(n,d):
    n,d=sgn(n,16),sgn(d,16)
    if d==0:return 'divisor_zero'
    if n==0:return 'numerator_zero'
    q=abs(n)//abs(d)
    if q==0:return 'quotient_zero'
    if q==1:return 'quotient_one'
    if q<=7:return 'quotient_2_to_7'
    if q<=31:return 'quotient_8_to_31'
    return 'quotient_32_plus'

def main():
    pairs=cases()
    assert len(pairs)>4000
    blob=json.dumps(pairs,separators=(',',':')).encode()
    report={'status':'PASS','basis':'same-input public-entry 6502 instruction cycles, caller JSR excluded','cases_per_operation_per_profile':len(pairs),
            'same_cases_sha256':hashlib.sha256(blob).hexdigest(),
            'routines':{},'resident_sha256':{},'profiles':list(PROFILES),
            'total_calls':0}
    cpu={}; api={}
    for p in PROFILES:
        cpu[p],api[p]=load_profile(p)
        file=ROOT/p/'resident'/f'math_{p}_game_math.prg'
        report['resident_sha256'][p]=hashlib.sha256(file.read_bytes()).hexdigest()
    rows=[]
    for op in ROUTINES:
        rec={'profiles':{},'class_counts':{},'v2_minus_v1':{}}
        full={};cycles_by_class={p:defaultdict(list) for p in PROFILES}
        for p in PROFILES:full[p]=[]
        for n,d in pairs:
            exp=div_expected(n,16,d,16,16,16)
            cl=group(n,d)
            rec['class_counts'][cl]=rec['class_counts'].get(cl,0)+1
            for p in PROFILES:
                machine=cpu[p];m=machine.mem
                wr(m,N,n,2);wr(m,D,d,2)
                wr(m,Q,0xA95B,2);wr(m,R,0xE67C,2)
                cy=machine.call(api[p][op],4_000_000)
                got=(rd(m,Q,2),rd(m,R,2),machine.c)
                assert got==exp,(op,p,n,d,got,exp)
                assert (rd(m,N,2),rd(m,D,2))==(n,d),(op,p,n,d,'input mutated')
                full[p].append(cy)
                cycles_by_class[p][cl].append(cy)
                report['total_calls']+=1
        for p in PROFILES:
            vec=full[p]; record={
                'mean_cycles':sum(vec)/len(vec),'min_cycles':min(vec),'max_cycles':max(vec),
                'p95_cycles':sorted(vec)[int((len(vec)-1)*.95)],
                'cycle_vector_sha256':hashlib.sha256(json.dumps(vec,separators=(',',':')).encode()).hexdigest(),
                'class_mean_cycles':{cl:sum(vals)/len(vals) for cl,vals in cycles_by_class[p].items()}
            }
            rec['profiles'][p]=record
            for cl,mean in record['class_mean_cycles'].items():
                rows.append({'routine':op,'profile':p,'class':cl,'cases':len(cycles_by_class[p][cl]),
                             'mean_cycles':f'{mean:.6f}','resident_sha256':report['resident_sha256'][p],
                             'same_cases_sha256':report['same_cases_sha256']})
        differences=[b-a for a,b in zip(full['v1_balanced'],full['v2_pareto_fast'])]
        rec['v2_minus_v1']={'mean_cycles':sum(differences)/len(differences),'faster':sum(x<0 for x in differences),
                          'equal':sum(x==0 for x in differences),'slower':sum(x>0 for x in differences),
                          'max_v2_regression':max(differences),'max_v2_gain':-min(differences)}
        report['routines'][op]=rec
        print(op,'pairs',len(pairs),'means',*[f'{p}={rec["profiles"][p]["mean_cycles"]:.6f}' for p in PROFILES],
              'delta',rec['v2_minus_v1'],flush=True)
    J.parent.mkdir(parents=True,exist_ok=True);C.parent.mkdir(parents=True,exist_ok=True)
    J.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    with C.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)
    print('ISSUE39 SIGNED 16 COMMON INPUT AUDIT PASS',report['total_calls'],flush=True)

if __name__=='__main__':main()
