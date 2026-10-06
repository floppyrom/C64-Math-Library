#!/usr/bin/env python3
from pathlib import Path
import json, random, shutil, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU, Assembler, REV, SIZE
from assemble_sources import build

PROFILE="v2_pareto_fast"; IO=0xC000; MASK32=(1<<32)-1

def parse_api(path):
    out={}
    for line in path.read_text().splitlines():
        if "=" not in line: continue
        k,v=[x.strip() for x in line.split("=",1)]
        if k.startswith("MATH_") and v.startswith("$"):
            try: out[k]=int(v[1:],16)
            except ValueError: pass
    return out

def load_prg(path):
    b=path.read_bytes(); lo=b[0]|(b[1]<<8)
    mem=bytearray(65536); mem[lo:lo+len(b)-2]=b[2:]
    return mem,lo,len(b)-2

def save_prg(mem,lo,n,path):
    path.write_bytes(bytes((lo&255,lo>>8))+bytes(mem[lo:lo+n]))

def patch_candidate(prg):
    mem,lo,n=load_prg(prg)

    # Rebuild the 116-byte MATH_INIT source image ($CC00 -> runtime $80-$F3)
    # without the leading 3-byte STY absolute. Relocate every ZP self-reference
    # that points inside the shifted image by -3, and preserve the fixed 116-byte
    # ownership contract with trailing BRKs.
    SRC=0xCC00
    old=bytes(mem[SRC:SRC+116])
    pc=0x80; off=0; ins=[]
    while pc<0xF4:
        oc=old[off]
        if oc not in REV: raise RuntimeError(f"bad core opcode {oc:02x} at {pc:02x}")
        op,mode=REV[oc]; sz=SIZE[mode]
        ins.append((pc,op,mode,bytearray(old[off:off+sz])))
        pc+=sz; off+=sz
    if pc!=0xF4 or off!=116: raise RuntimeError((pc,off))
    if ins[0][0]!=0x80 or ins[0][1]!="sty" or ins[0][2]!="abs":
        raise RuntimeError("unexpected SMUL16 core prologue")

    new=bytearray()
    for pc,op,mode,bs in ins[1:]:
        if mode in ("zp","zpx","zpy","indx","indy"):
            t=bs[1]
            if 0x83 <= t <= 0xF3:
                bs[1]=(t-3)&255
        elif mode in ("abs","absx","absy","ind"):
            t=bs[1]|(bs[2]<<8)
            if 0x0083 <= t <= 0x00F3:
                t-=3; bs[1]=t&255; bs[2]=t>>8
        new.extend(bs)
    if len(new)!=113: raise RuntimeError(f"new core size {len(new)}")
    new.extend(b"\x00"*3)
    mem[SRC:SRC+116]=new

    # The core's final low result bytes move $F2/$F3 -> $EF/$F0.
    if mem[0x211B:0x211D] != bytes((0xA5,0xF2)): raise RuntimeError("adapter z0 load drift")
    if mem[0x2120:0x2122] != bytes((0xA5,0xF3)): raise RuntimeError("adapter z1 load drift")
    mem[0x211C]=0xEF
    mem[0x2121]=0xF0

    # Reassemble the signed tail symbolically. Both X-negative paths re-read
    # stable public Y0 instead of the removed SMC byte.
    tail=r"""
.org $5a00
tail:
    bit $a7
    bmi xneg
    bit $b7
    bmi subx
    tax
    tya
    adc #$00
    rts
xneg:
    bit $b7
    bmi both
    bcc yready
    iny
yready:
    sec
    sbc $c004
    tax
    tya
    sbc $b7
    rts
subx:
    bcc xready
    iny
xready:
    sec
    sbc $99
    tax
    tya
    sbc $a7
    rts
both:
    bcc bready
    iny
bready:
    sec
    sbc $c004
    tax
    tya
    sbc $b7
    tay
    txa
    sec
    sbc $99
    tax
    tya
    sbc $a7
    rts
"""
    td,labels,const=Assembler().assemble(tail)
    end=max(td)+1
    for a,v in td.items(): mem[a]=v
    # Clear a small trailing area so stale old tail bytes can never be reached.
    for a in range(end,0x5A50): mem[a]=0

    save_prg(mem,lo,n,prg)
    return {"core_bytes":113,"reserved_core_bytes":116,"tail_bytes":end-0x5A00,
            "z0":0xEF,"z1":0xF0}

def load(prg,inc):
    mem,_,_=load_prg(prg); api=parse_api(inc)
    c=CPU(mem); c.d=0; c.call(api["MATH_INIT"],2_000_000)
    return c,api

def wr(m,a,v,n=2):
    for i in range(n): m[a+i]=(v>>(8*i))&255
def rd(m,a,n=4): return sum(m[a+i]<<(8*i) for i in range(n))
def si(v): return v-(1<<16) if v&0x8000 else v

def edges():
    s=1<<15; m=(1<<16)-1
    return list(dict.fromkeys([0,1,2,3,7,15,16,31,63,127,128,255,s-2,s-1,s,s+1,m-2,m-1,m]))

def canonical():
    e=edges(); pairs=[(x,y) for x in e for y in e]
    rng=random.Random(0x5A17_0000+1*0x100+16)
    pairs += [(rng.randrange(1<<16),rng.randrange(1<<16)) for _ in range(4096)]
    return pairs

def focus(kind,n=20000):
    rng=random.Random(0x516000+sum(map(ord,kind)))
    lo=lambda:rng.randrange(0,0x8000); hi=lambda:rng.randrange(0x8000,0x10000)
    fx,fy={"PP":(lo,lo),"PN":(lo,hi),"NP":(hi,lo),"NN":(hi,hi)}[kind]
    return [(fx(),fy()) for _ in range(n)]

def bench(cpu,entry,pairs,shr=False):
    total=0; mn=None; mx=None; errors=0; cs=[]
    for x,y in pairs:
        wr(cpu.mem,IO,x); wr(cpu.mem,IO+4,y)
        bx=bytes(cpu.mem[IO:IO+2]); by=bytes(cpu.mem[IO+4:IO+6])
        cy=cpu.call(entry,2_000_000)
        prod=(si(x)*si(y))&MASK32
        if shr:
            got=rd(cpu.mem,IO+8,3); exp=(prod>>8)&0xffffff
        else:
            got=rd(cpu.mem,IO+8,4); exp=prod
        if got!=exp or cpu.c!=0 or bytes(cpu.mem[IO:IO+2])!=bx or bytes(cpu.mem[IO+4:IO+6])!=by:
            errors+=1
            if errors<=8: print("ERROR",hex(x),hex(y),hex(got),hex(exp),"C",cpu.c)
        total+=cy; cs.append(cy); mn=cy if mn is None else min(mn,cy); mx=cy if mx is None else max(mx,cy)
    return {"cases":len(pairs),"errors":errors,"mean_cycles":total/len(pairs),"min_cycles":mn,"max_cycles":mx,"cycles":cs}

def compare(base,cand,entry,pairs,shr=False):
    b=bench(base[0],base[1][entry],pairs,shr)
    c=bench(cand[0],cand[1][entry],pairs,shr)
    ds=[y-x for x,y in zip(b["cycles"],c["cycles"])]
    b.pop("cycles"); c.pop("cycles")
    return {"baseline":b,"candidate":c,"delta_mean_cycles":sum(ds)/len(ds),"delta_min":min(ds),"delta_max":max(ds)}

def pair(tmp):
    return (load(ROOT/PROFILE/"resident"/f"math_{PROFILE}_game_math.prg",ROOT/PROFILE/"resident"/"math_api.inc"),
            load(tmp/f"math_{PROFILE}_source_built.prg",tmp/"math_api.inc"))

def main():
    tmp=Path(tempfile.mkdtemp(prefix="smul16-reloc-"))
    try:
        build(PROFILE,ROOT/"relocatable_source"/PROFILE/"math_config_reference.inc",tmp)
        candprg=tmp/f"math_{PROFILE}_source_built.prg"
        patch=patch_candidate(candprg)
        results={}
        b,c=pair(tmp); results["canonical"]=compare(b,c,"MATH_SMUL16",canonical())
        for k in ("PP","PN","NP","NN"):
            b,c=pair(tmp); results[k]=compare(b,c,"MATH_SMUL16",focus(k))
        b,c=pair(tmp); results["shr8"]=compare(b,c,"MATH_SMUL16_SHR8",canonical(),True)
        ok=all(v["candidate"]["errors"]==0 for v in results.values()) and results["canonical"]["delta_mean_cycles"]<0
        out={"status":"PASS" if ok else "FAIL","patch":patch,"results":results}
        print(json.dumps(out,indent=2))
        if not ok: raise SystemExit(1)
    finally:
        shutil.rmtree(tmp,ignore_errors=True)

if __name__=="__main__": main()
