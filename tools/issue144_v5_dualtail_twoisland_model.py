#!/usr/bin/env python3
"""Issue144 B V5 31-ZP two-island dual-tail executable research (NOT default).

Use a temporary donor-source patch to build existing V5 hybrid; its unchanged
importer reaches an unmapped lowD $1C00. Instead of changing the public builder,
safely relocate the 16-stage tail into two verified zero-valued, symbol-relative
V5 resident gaps, with an explicit JMP across the eight-stage boundary.

All changes are restricted to a disposable generated PRG; the canonical V2
source, archived five reference PRGs, REUs, PERFORMANCE and OptiSearch remain
untouched. Source-only model qualification, not VICE/IRQ/NMI/bus validation.
"""
from __future__ import annotations
import hashlib,json,statistics,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import CPU,Assembler
from build_hybrid import build,trace,copy_relocated_block,map_abs
from assemble_sources import preprocess,parse_config
from issue144_u3216_inresident_fullabi_stage import variant,FILE
from issue144_u3216_dualtail_direct_dispatch_screen import vectors as unsigned_vectors
from issue144_dualtail_signed_public_regression import vectors as signed_vectors,exercise as signed_exercise
from validate_udiv32_16_integrated import one as unsigned_one
from validate_signed_division import div_expected
SLOTS=(0x0E4D,0x13AF)
CAP=(435,337)
OPS_U=("MATH_UDIV32_16","MATH_UMOD32_16")
OPS_S=("MATH_SDIV32_16","MATH_SMOD32_16")

def donor():
    vp=ROOT/"relocatable_source/v2_pareto_fast"
    original=preprocess(vp/"math_relocatable.asm",vp/"math_config_reference.inc")
    src=variant(original)
    mem,labels,_=Assembler().assemble(src)
    b=bytearray(65536)
    for a,v in mem.items():b[a]=v
    lo=labels["U3216_LOW_DIV"]
    mid=labels["U3216_LD_B8"]
    end=labels["U3216_LD_END"]
    assert (end-lo)==461 and (mid-lo+3, end-mid)==(234,230),(lo,mid,end)
    starts=trace(b,lo)
    assert all(s in starts for s in (lo,mid,labels["U3216_LOW_STUB"])),("label not executable")
    return b,labels,starts

def load(b):
    lo=int.from_bytes(b[:2],"little");mem=bytearray(65536)
    mem[lo:lo+len(b)-2]=b[2:]
    return mem,lo,lo+len(b)-2

def save(mem,lo,hi,path):
    return path.write_bytes(bytes((lo&255,lo>>8))+bytes(mem[lo:hi]))

def compiler(layout,tmp):
    profile="v5_hybrid_lowzp"
    cfg=ROOT/"relocatable_source"/profile/("math_config_"+layout+".inc")
    vals=parse_config(cfg)
    original_bytes=FILE.read_bytes()
    old_sha=hashlib.sha256(original_bytes).hexdigest()
    stock=tmp/layout/"stock"/profile
    stock.mkdir(parents=True,exist_ok=True)
    stockman=build(cfg,stock)
    oldpath=stock/stockman["output_prg"]
    oldraw=oldpath.read_bytes()
    try:
        FILE.write_text(variant(original_bytes.decode()))
        opt=tmp/layout/"candidate"/profile
        opt.mkdir(parents=True,exist_ok=True)
        man=build(cfg,opt)
        path=opt/man["output_prg"]
        img=path.read_bytes()
    finally:
        FILE.write_bytes(original_bytes)
    assert hashlib.sha256(FILE.read_bytes()).hexdigest()==old_sha
    mem,lo,hi=load(img)
    src,labels,starts=donor()
    hbase=int(man["hybrid_code"].split("-")[0].lstrip("$"),16)
    p0=vals["REG_LOW"]+SLOTS[0]
    p1=vals["REG_LOW"]+SLOTS[1]
    n0=234;n1=230
    assert mem[p0:p0+n0]==bytes(n0),(layout,"1st island occupied")
    assert mem[p1:p1+n1]==bytes(n1),(layout,"2nd island occupied")
    # Copy the exact NMOS instructions and fix their absolute/ZP operands
    # using the same map_abs + relocation machinery as the actual V5 linker.
    start=labels["U3216_LOW_DIV"]
    mid=labels["U3216_LD_B8"]
    end=labels["U3216_LD_END"]
    copy_relocated_block(mem,src,start,mid-1,p0,starts,vals,hbase)
    copy_relocated_block(mem,src,mid,end-1,p1,starts,vals,hbase)
    # Append one inter-island jump after the first 8-step block.
    x=p0+(mid-start)
    mem[x:x+3]=bytes((0x4C,p1&255,p1>>8))
    # The as-built importer has copied the V2 U3216_LOW_STUB JMP, but
    # the stock V5 linker does not relocate its source $1C00 target.
    stub=map_abs(labels["U3216_LOW_STUB"],vals,hbase)
    assert mem[stub]==0x4C,(layout,"unexpected source-only importer opcode",hex(stub),hex(mem[stub]))
    dangling=mem[stub+1]|(mem[stub+2]<<8)
    assert dangling==labels["U3216_LOW_DIV"],(layout,"unexpected branch target",hex(dangling))
    mem[stub+1:stub+3]=bytes((p0&255,p0>>8))
    assert mem[p0:p0+n0] and mem[p1:p1+n1]
    save(mem,lo,hi,path)
    man["output_sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
    (opt/"source_build_manifest.json").write_text(json.dumps(man,indent=2)+"\n")
    api={k:int(v[1:],16) if isinstance(v,str) and v.startswith("$") else int(v)
         for k,v in man["public_entries"].items()}
    return load(oldraw)[0],mem,api,vals,man,opt,((p0,p0+n0),(p1,p1+n1))

def init(mem,api):
    c=CPU(bytearray(mem));c.d=0
    assert c.call(api["MATH_INIT"],2000000)>0 and c.c==0
    return c

def stats(s):
    t=sorted(s)
    return {"cases":len(s),"mean_saved":statistics.mean(s),
            "min_saved":t[0],"p05_saved":t[int(.05*(len(s)-1))],
            "p95_saved":t[int(.95*(len(s)-1))],"max_saved":t[-1],
            "slower":sum(x<0 for x in s)}

def main():
    from validate_source_build import validate
    report={"status":"PASS_RESEARCH_V5_SPLIT_LOWTAIL_SOURCE_MODEL",
            "research_only":True,"default_v5_builder_modified":False,
            "reference_PRGs_REUs_modified":False,"normal_zp_added":0,
            "caller_ram_added":0,"native_vice_qualified":False,
            "source_donor_restored":False,"layouts":{}}
    src,labels,starts=donor()
    U=unsigned_vectors()
    S=signed_vectors()
    with tempfile.TemporaryDirectory(prefix="issue144_v5_dualtail_split_") as temp:
        tmp=Path(temp)
        for layout in ("reference","alternate"):
            before,after,api,vals,man,folder,spans=compiler(layout,tmp)
            a=init(before,api)
            b=init(after,api)
            stored=[bytes(b.mem[x:y]) for x,y in spans]
            assert stored==[bytes(after[x:y]) for x,y in spans],(layout,"init overwrote resident")
            result={}
            for op in (*OPS_U,*OPS_S):
                seq=U if op in OPS_U else S
                diff=[]
                for i,(_,n,d) in enumerate(seq):
                    if op in OPS_U:
                        old,good0,z0,want=unsigned_one(a,api[op],n,d,vals["MATH_IO"])
                        new,good1,z1,_=unsigned_one(b,api[op],n,d,vals["MATH_IO"])
                        assert good0 and good1 and z0==z1==want,(
                            layout,op,i,hex(n),hex(d),z0,z1,want)
                    else:
                        old,z0,f0,acc0,x0,y0=signed_exercise(a,api[op],vals["MATH_IO"],n,d)
                        new,z1,f1,acc1,x1,y1=signed_exercise(b,api[op],vals["MATH_IO"],n,d)
                        want=div_expected(n,32,d,16,32,16)
                        assert z0==z1==want,(layout,op,i,hex(n),hex(d),z0,z1,want)
                        assert (f0,acc0,x0,y0)==(f1,acc1,x1,y1),(layout,op,i,"volatile")
                    diff.append(old-new)
                    if i%41==0:
                        assert stored==[bytes(b.mem[x:y]) for x,y in spans],(
                            layout,op,i,"runtime overwrite of V5 code")
                result[op]=stats(diff)
            check=validate("v5_hybrid_lowzp",tmp/layout/"candidate")
            assert check["public_entries_executed"]==56
            assert check["machine_calls"]==21678
            assert man["normal_zp_bytes"]==31
            report["layouts"][layout]={"entries":56,"public_calls":check["machine_calls"],
                 "resident_spans":[[hex(a),hex(b-1)] for a,b in spans],
                 "assembled_tail_bytes":464,"ordinary_zp":31,
                 "public_pair_benchmark":result}
            print("V5 8+8 SPLIT TAIL MODEL",layout,"PASS",sum(v["cases"] for v in result.values()),flush=True)
    report["source_donor_restored"]=True
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__=="__main__":main()
