#!/usr/bin/env python3
from pathlib import Path
import argparse, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from mini6502 import Assembler, REV, SIZE

def load_prg(path):
    b=Path(path).read_bytes(); lo=b[0]|(b[1]<<8)
    mem=bytearray(65536); mem[lo:lo+len(b)-2]=b[2:]
    return mem,lo,len(b)-2

def save_prg(mem,lo,n,path):
    Path(path).write_bytes(bytes((lo&255,lo>>8))+bytes(mem[lo:lo+n]))

def patch(path):
    path=Path(path); mem,lo,n=load_prg(path)
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
            if 0x83<=t<=0xF3: bs[1]=(t-3)&255
        elif mode in ("abs","absx","absy","ind"):
            t=bs[1]|(bs[2]<<8)
            if 0x0083<=t<=0x00F3:
                t-=3; bs[1]=t&255; bs[2]=t>>8
        new.extend(bs)
    if len(new)!=113: raise RuntimeError(f"new core size {len(new)}")
    new.extend(b"\x00"*3)
    mem[SRC:SRC+116]=new

    for pc,oldv,newv in ((0x2104,0x99,0x96),(0x2109,0xA7,0xA4),(0x210E,0xB7,0xB4)):
        if mem[pc]!=oldv: raise RuntimeError(f"adapter SMC drift at {pc:04x}: {mem[pc]:02x}")
        mem[pc]=newv
    if mem[0x211B:0x211D]!=bytes((0xA5,0xF2)): raise RuntimeError("adapter z0 load drift")
    if mem[0x2120:0x2122]!=bytes((0xA5,0xF3)): raise RuntimeError("adapter z1 load drift")
    mem[0x211C]=0xEF; mem[0x2121]=0xF0

    tail=r"""
.org $5a00
tail:
    bit $a4
    bmi xneg
    bit $b4
    bmi subx
    tax
    tya
    adc #$00
    rts
xneg:
    bit $b4
    bmi both
    bcc yready
    iny
yready:
    sec
    sbc $c004
    tax
    tya
    sbc $b4
    rts
subx:
    bcc xready
    iny
xready:
    sec
    sbc $96
    tax
    tya
    sbc $a4
    rts
both:
    bcc bready
    iny
bready:
    sec
    sbc $c004
    tax
    tya
    sbc $b4
    tay
    txa
    sec
    sbc $96
    tax
    tya
    sbc $a4
    rts
"""
    td,labels,const=Assembler().assemble(tail)
    for a,v in td.items(): mem[a]=v
    end=max(td)+1
    if end!=0x5A3D: raise RuntimeError(f"unexpected tail end {end:04x}")
    save_prg(mem,lo,n,path)
    return {"path":str(path),"core_used":113,"core_reserved":116,"tail_bytes":61}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("prg",nargs="+",type=Path)
    args=ap.parse_args()
    for p in args.prg: print(patch(p))

if __name__=="__main__": main()
