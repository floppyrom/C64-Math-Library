#!/usr/bin/env python3
from pathlib import Path
import argparse, json, random, re, sys, time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from mini6502 import CPU

PROFILES = ["v1_balanced", "v2_pareto_fast", "v3_reu_512k", "v4_reu_16m", "v5_hybrid_lowzp"]
REU = {
    "v3_reu_512k": ROOT / "v3_reu_512k/reu/c64_math_v3_512k_game_math.reu",
    "v4_reu_16m": ROOT / "v4_reu_16m/reu/c64_math_v4_16m_game_math.reu",
}
MASK = lambda bits: (1 << bits) - 1

def signed(v, bits):
    return v - (1 << bits) if v & (1 << (bits - 1)) else v

def wr(mem, addr, value, n):
    for i in range(n):
        mem[addr+i] = (value >> (8*i)) & 0xff

def rd(mem, addr, n):
    return sum(mem[addr+i] << (8*i) for i in range(n))

def parse_api(path):
    out = {}
    for line in path.read_text().splitlines():
        m = re.match(r"\s*(MATH_[A-Z0-9_]+)\s*=\s*\$([0-9A-Fa-f]+)", line)
        if m:
            out[m.group(1)] = int(m.group(2), 16)
    return out

def load_profile(profile):
    resident = ROOT / profile / "resident"
    prg = resident / f"math_{profile}_game_math.prg"
    b = prg.read_bytes(); load = b[0] | b[1] << 8
    mem = bytearray(65536); mem[load:load+len(b)-2] = b[2:]
    reu = bytearray(REU[profile].read_bytes()) if profile in REU else None
    cpu = CPU(mem, reu=reu); cpu.d = 0
    api = parse_api(resident / "math_api.inc")
    # All shipped profiles expose MATH_INIT at $3280 in the stable layout.
    cpu.call(0x3280, 2_000_000)
    return cpu, api

def edge_values(bits):
    m = MASK(bits); s = 1 << (bits-1)
    vals = [0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]
    return list(dict.fromkeys(v & m for v in vals))

def test_entry(cpu, entry, bits, pairs, ready=False):
    io = 0xC000; xaddr=io; yaddr=io+4; zaddr=io+8; n=bits//8
    errors = 0; mincy = None; maxcy = None; totalcy = 0
    for x,y in pairs:
        wr(cpu.mem,xaddr,x,n); wr(cpu.mem,yaddr,y,n)
        before_x=bytes(cpu.mem[xaddr:xaddr+n]); before_y=bytes(cpu.mem[yaddr:yaddr+n])
        cy=cpu.call(entry,2_000_000)
        exp=(signed(x,bits)*signed(y,bits)) & MASK(bits*2)
        got=rd(cpu.mem,zaddr,n*2)
        if got != exp or cpu.c != 0 or bytes(cpu.mem[xaddr:xaddr+n]) != before_x or bytes(cpu.mem[yaddr:yaddr+n]) != before_y:
            errors += 1
            if errors <= 3:
                print("ERROR",bits,hex(x),hex(y),hex(got),hex(exp),cpu.c)
        mincy=cy if mincy is None else min(mincy,cy); maxcy=cy if maxcy is None else max(maxcy,cy); totalcy += cy
    return {"cases":len(pairs),"errors":errors,"mean_cycles":totalcy/len(pairs),"min_cycles":mincy,"max_cycles":maxcy}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--profile', choices=PROFILES)
    args=ap.parse_args()
    run_profiles=[args.profile] if args.profile else PROFILES
    start=time.time(); results={}
    for profile in run_profiles:
        pi=PROFILES.index(profile)
        cpu,api=load_profile(profile); pres={}
        # Exhaustive signed 8x8 on each distinct resident SMUL8 family (V1, V2, V3).
        # V4 shares the V3 resident SMUL8 slice; V5 inherits the V1 signed path,
        # so those two receive a large structured/random regression instead.
        if profile in ('v1_balanced','v2_pareto_fast','v3_reu_512k'):
            pairs8=[(x,y) for x in range(256) for y in range(256)]
            smul8_mode='exhaustive'
        else:
            e8=edge_values(8); pairs8=[(x,y) for x in e8 for y in e8]
            rng8=random.Random(0x5800_0000 + pi)
            pairs8 += [(rng8.randrange(256),rng8.randrange(256)) for _ in range(8192)]
            smul8_mode='structured_random'
        pres['SMUL8']=test_entry(cpu,api['MATH_SMUL8'],8,pairs8)
        pres['SMUL8']['mode']=smul8_mode
        # Wider widths: dense signed edges + deterministic random corpus.
        for bits,name,count in [(16,'MATH_SMUL16',4096),(24,'MATH_SMUL24',2048),(32,'MATH_SMUL32',2048)]:
            e=edge_values(bits); pairs=[(x,y) for x in e for y in e]
            rng=random.Random(0x5A17_0000 + pi*0x100 + bits)
            pairs += [(rng.randrange(1<<bits),rng.randrange(1<<bits)) for _ in range(count)]
            pres[name[5:]]=test_entry(cpu,api[name],bits,pairs)
        # Initialized-state signed 32-bit entry.
        rng=random.Random(0x5320_0000+pi)
        ready_pairs=[(rng.randrange(1<<32),rng.randrange(1<<32)) for _ in range(1024)]
        pres['SMUL32_READY']=test_entry(cpu,api['MATH_SMUL32_READY'],32,ready_pairs,True)
        if any(v['errors'] for v in pres.values()):
            raise AssertionError((profile,pres))
        results[profile]=pres
        print(profile,"PASS",sum(v['cases'] for v in pres.values()),"signed multiply calls",flush=True)
    out={"status":"PASS","profiles":results,"summary":{"profiles":len(run_profiles),"machine_calls":sum(v['cases'] for p in results.values() for v in p.values()),"elapsed_seconds":round(time.time()-start,2)}}
    path=ROOT/'validation/review/SIGNED_MULTIPLY_VALIDATION.json'; path.write_text(json.dumps(out,indent=2)+'\n')
    print("SIGNED MULTIPLY PASS",out['summary']['machine_calls'],"calls")
if __name__=='__main__': main()
