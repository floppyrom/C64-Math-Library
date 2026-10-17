#!/usr/bin/env python3
"""Relocate canonical V2 Pareto-Fast 32/16 native core behind public Q32/R16 ABI.

Source is read verbatim from the certified V2 donor. Only the two fixed code
origins and the twelve absolute ZP operand addresses are remapped. The donor
uses stable NMOS LAX/ANC opcodes; D must be clear. An explicit staging/output
adapter makes its timing incomparable with native-only publication records
until a full public-call matched-input benchmark has been passed.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
from mini6502 import Assembler

ROOT=Path(__file__).resolve().parents[1]
SOURCE="v2_pareto_fast/resident/modules/pareto_udiv32_16.a"
ZP_NAMES=("n0","n1","d0","d1","q0","q1","r0","r1",
          "ln0","ln1","lq0","lq1")
CG_SLOT=0x500-12
MX_SLOT=0x400
WRAPPER_OFFSET=0x900
MAX_WRAPPER=160
PUB_ENTRY="FAST_UDIV32_16_V2"

def layout(code):
    cg=code+12
    mx=code+0x500
    wrapper=code+WRAPPER_OFFSET
    if wrapper+MAX_WRAPPER>0x10000:
        raise ValueError("V2 size-fast 32/16 code islands exceed 64 KiB")
    return cg,mx,wrapper

def render(code,io,zp,root:Path=ROOT):
    if not (2<=zp<=0xf4):
        raise ValueError("V2 32/16 needs 12 reserved non-port zero-page bytes")
    if io+32>0x10000:
        raise ValueError("public IO exceeds 64 KiB")
    cg,mx,wrapper=layout(code)
    src=(root/SOURCE).read_text(encoding="utf-8")
    original="* = $0010\ncg_zp_start:\n"+''.join(
        "%s: !byte 0\n"%name for name in ZP_NAMES[:8])+"cg_zp_end:\n\n"
    low="*=$0018\nmx_zp_start:\n"+''.join(
        "%s: !byte 0\n"%name for name in ZP_NAMES[8:])+"mx_zp_end:\n\n"
    if src.count(original)!=1 or src.count(low)!=1:
        raise ValueError("Historical V2 ZP/ABI donor layout changed")
    # Labels point directly into 12 caller-selected ZP slots; the canonical
    # donor logic, including all branches and stable illegal NMOS opcodes,
    # remains otherwise byte-for-byte source identical.
    zp_main="cg_zp_start = TEMP_ZP\n"+''.join(
        "%s = TEMP_ZP+%d\n"%(name,i)
        for i,name in enumerate(ZP_NAMES[:8]))+"cg_zp_end = TEMP_ZP+8\n"
    zp_low="mx_zp_start = TEMP_ZP+8\n"+''.join(
        "%s = TEMP_ZP+%d\n"%(name,i+8)
        for i,name in enumerate(ZP_NAMES[8:]))+"mx_zp_end = TEMP_ZP+12\n"
    src=src.replace(original,zp_main).replace(low,zp_low)
    for old,new in (("* = $420c","* = KERNEL_CG"),
                    ("*=$4e00","* = KERNEL_MX")):
        if src.count(old)!=1:
            raise ValueError("Historical V2 code-island origin changed: "+old)
        src=src.replace(old,new)
    header=(f"TEMP_ZP = ${zp:02X}\nKERNEL_CG = ${cg:04X}\n"
            f"KERNEL_MX = ${mx:04X}\nKERNEL_WRAPPER = ${wrapper:04X}\n"
            f"INPUT_NUM = ${io+16:04X}\nINPUT_DIV = ${io+20:04X}\n"
            f"OUTPUT_QUOT = ${io+24:04X}\nOUTPUT_REM = ${io+28:04X}\n")
    before="* = KERNEL_WRAPPER\nFAST_UDIV32_16_V2:\nFAST_UMOD32_16_V2:\n"
    # Public inputs N0..3, D0..1 are staged into the original ABI layout
    # (native n0,n1 = high dividend word; ln0,ln1 = low).
    stage={
        "ln0":"INPUT_NUM","ln1":"INPUT_NUM+1",
        "n0":"INPUT_NUM+2","n1":"INPUT_NUM+3",
        "d0":"INPUT_DIV","d1":"INPUT_DIV+1"}
    for target,address in stage.items():
        before+="    lda "+address+"\n    sta "+target+"\n"
    before+="    jsr div_u32_16\n"
    for value,dest in (
        ("lq0","OUTPUT_QUOT"),("lq1","OUTPUT_QUOT+1"),
        ("q0","OUTPUT_QUOT+2"),("q1","OUTPUT_QUOT+3"),
        ("r0","OUTPUT_REM"),("r1","OUTPUT_REM+1")):
        before+="    lda "+value+"\n    sta "+dest+"\n"
    before+="    rts\n"
    return header+src+"\n"+before

def assemble(code,io,zp,root:Path=ROOT):
    cg,mx,wrapper=layout(code)
    memory,labels,_=Assembler().assemble(render(code,io,zp,root))
    sections={}
    for name,start,limit in (
        ("FAST16",cg,mx),
        ("TAIL16",mx,wrapper),
        ("PUBLIC",wrapper,wrapper+MAX_WRAPPER)):
        addresses=sorted(a for a in memory if start<=a<limit)
        if not addresses or addresses!=list(range(start,start+len(addresses))):
            raise ValueError("V2 32/16 non-contiguous "+name+" code island")
        sections[name]=(start,len(addresses))
    if min(memory)!=cg or max(memory)>=wrapper+MAX_WRAPPER:
        raise ValueError("V2 32/16 unexpected compiled code outside islands")
    if (sections["FAST16"][1]>CG_SLOT or
        sections["TAIL16"][1]>MX_SLOT or
        sections["PUBLIC"][1]>MAX_WRAPPER):
        raise ValueError("V2 32/16 historical code islands overflowed")
    if (labels.get(PUB_ENTRY)!=wrapper or
        labels.get("FAST_UMOD32_16_V2")!=wrapper):
        raise ValueError("V2 signed/unsigned public 32/16 export changed")
    return memory,labels,sections

def source_sha256(root:Path=ROOT):
    return hashlib.sha256((root/SOURCE).read_bytes()).hexdigest()

if __name__=="__main__":
    for code,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
        mem,labels,sections=assemble(code,io,zp)
        print("V2 SIZEFAST U3216",hex(code),sections,
              "public",hex(labels[PUB_ENTRY]),flush=True)
