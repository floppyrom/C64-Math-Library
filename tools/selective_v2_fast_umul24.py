#!/usr/bin/env python3
"""Source-linked V2 24x24 fast unsigned producer, quarter-square carry-neutral.

The *actual historical assembly* (not a reimplementation of its arithmetic
rows) is extracted from v2_pareto_fast/resident/modules/pareto_umul24.a and
assembled at relocatable addresses. The public wrapper supplies X/Y inputs,
initializes 24 pointer ZP bytes and reifies Z0..Z5/C. No resident binary
copy, REU, compile-time profile, or installation-time initialization.

This is a candidate research emitter until two-placement CPU and native
VICE qualification completes. The 156-byte zero-ZP portable option remains.
"""
from __future__ import annotations
import hashlib
import re
from pathlib import Path
from mini6502 import Assembler

ROOT=Path(__file__).resolve().parents[1]
SOURCE="v2_pareto_fast/resident/modules/pareto_umul24.a"
ZP_BYTES=24
CODE_SLOT=512
TABLE_SLOT=512
TABLES=("sqr_lo","sqr_hi","neg_sqr_lo","neg_sqr_hi")
PUBLIC="FAST_UMUL24_V2_QS"
SIGNED_PUBLIC="FAST_SMUL24_V2_QS"
BIAS=0xCA

# Labels are direct aliases of the historical 24 contiguous ZP pointer bytes.
P_NAMES=tuple("%s_%d"%(family,i)
              for family in ("p_sqr_lo","p_sqr_hi","p_neg_lo","p_neg_hi")
              for i in range(3))


def layout(start):
    table_base=(start+CODE_SLOT+255)&~255
    addresses={"KERNEL_CODE":start}
    for j,name in enumerate(TABLES):
        addresses[name]=table_base+j*TABLE_SLOT
    return addresses,table_base+len(TABLES)*TABLE_SLOT


def planes():
    def q(i):
        return (i*i)//4+BIAS*(i&1)
    raw=[q(i) for i in range(511)]
    negative=[q(255-i) for i in range(511)]
    return (
        bytes(x&255 for x in raw),
        bytes((x>>8)&255 for x in raw),
        bytes((255-(x&255))&255 for x in negative),
        bytes((255-((x>>8)&255))&255 for x in negative),
    )


def native_core(root=ROOT):
    source=(root/SOURCE).read_text(encoding="utf-8")
    if (source.count("cg_code_start\n")!=1 or
        source.count("\ncg_code_end")!=1 or
        source.count("ODD  = $ca")!=1):
        raise ValueError("Historical biased source layout/offset changed")
    core=source.split("cg_code_start\n",1)[1].split("\ncg_code_end",1)[0]
    if core.count("umul24\n")!=1 or core.count("z0 !byte 0")!=1:
        raise ValueError("Historical 24-bit core label changed")
    # ACME's explicit +2 absolute width qualifier is unnecessary for a
    # fixed-address code label; mini6502's assembler derives absolute width.
    core=re.sub(r"\b([a-z]{3})\+2(?=\s)",r"\1",core)
    core=core.replace("z0 !byte 0","z0: !byte 0")
    return core



def signed_wrapper():
    """Shared V2 unsigned producer plus modulo-2^48 signed correction.

    No extra ZP or tables. The unsigned routine preserves public X24/Y24.
    Only Z[3:6] needs correction; both wrapper aliases use one source image.
    """
    return """FAST_SMUL24_V2_QS:
    jsr FAST_UMUL24_V2_QS
    lda INPUT_X+2
    bpl signed24_x_done
    sec
    lda OUTPUT_Z+3
    sbc INPUT_Y
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    sbc INPUT_Y+1
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    sbc INPUT_Y+2
    sta OUTPUT_Z+5
signed24_x_done:
    lda INPUT_Y+2
    bpl signed24_y_done
    sec
    lda OUTPUT_Z+3
    sbc INPUT_X
    sta OUTPUT_Z+3
    lda OUTPUT_Z+4
    sbc INPUT_X+1
    sta OUTPUT_Z+4
    lda OUTPUT_Z+5
    sbc INPUT_X+2
    sta OUTPUT_Z+5
signed24_y_done:
    clc
    rts
"""

def render(start,io,zp,root=ROOT):
    if zp<2 or zp+ZP_BYTES>0x100:
        raise ValueError("Historical 24x24 fast producer needs 24 ZP bytes")
    if not (0x0200<=start and start+CODE_SLOT<=0x10000):
        raise ValueError("UMUL24 code origin outside legal RAM")
    if io<0 or io+16>0x10000:
        raise ValueError("UMUL24 public operand IO outside RAM")
    positions,end=layout(start)
    if end>0x10000:
        raise ValueError("UMUL24 code/table extent outside 64KB")

    const=["!cpu 6510","KERNEL_CODE = $%04X"%start,
           "INPUT_X = $%04X"%io,"INPUT_Y = $%04X"%(io+4),
           "OUTPUT_Z = $%04X"%(io+8)]
    const.extend("%s = $%04X"%(name,positions[name]) for name in TABLES)
    const.extend("%s = $%04X"%(name,zp+2*i)
                 for i,name in enumerate(P_NAMES))
    const.extend(["x0 = $%04X"%zp,"x1 = $%04X"%(zp+2),
                  "x2 = $%04X"%(zp+4)])
    # Original z1..4 reuse pointer-low scratch slots. No persistent setup.
    const.extend("z%d = $%04X"%(i,zp+12+2*i)
                 for i in range(1,5))
    # Seed the high bytes of every ZP pointer on *every* call. A table
    # therefore requires no MATH_INIT; its base is 256-byte aligned.
    wrapper=["* = KERNEL_CODE",PUBLIC+":",
             "    lda INPUT_X","    sta x0",
             "    lda INPUT_X+1","    sta x1",
             "    lda INPUT_X+2","    sta x2"]
    for family,tab in zip(
        ("p_sqr_lo","p_sqr_hi","p_neg_lo","p_neg_hi"),TABLES):
        wrapper.append("    lda #>%s"%tab)
        wrapper.extend("    sta %s_%d+1"%(family,i) for i in range(3))
    wrapper.extend([
        "    lda INPUT_Y+1", "    sta y1",
        "    lda INPUT_Y+2", "    sta y2",
        "    ldy INPUT_Y",
        "    ldx INPUT_X",
        "    lda INPUT_X+2",
        "    jsr umul24",
        "    sta OUTPUT_Z+5",
        "    lda z0","    sta OUTPUT_Z",
        "    lda z1","    sta OUTPUT_Z+1",
        "    lda z2","    sta OUTPUT_Z+2",
        "    lda z3","    sta OUTPUT_Z+3",
        "    lda z4","    sta OUTPUT_Z+4",
        "    clc","    rts",
    ])
    return "\n".join(const+wrapper)+"\n"+native_core(root)+"\n"+signed_wrapper()+"\n"


def assemble(start,io,zp,root=ROOT):
    positions,end=layout(start)
    code,labels,_=Assembler().assemble(render(start,io,zp,root))
    if labels.get(PUBLIC)!=start or "umul24" not in labels or SIGNED_PUBLIC not in labels:
        raise ValueError("UMUL24 public/native entries not source-linked")
    if not code or min(code)<start or max(code)>=start+CODE_SLOT:
        raise ValueError("UMUL24 wrapper+historical code exceeds 512 bytes")
    if not (start<labels["umul24"]<start+CODE_SLOT):
        raise ValueError("Historical V2 24-bit core relocated outside island")
    image={a:0xea for a in range(start,end)}
    image.update(code)
    for name,data in zip(TABLES,planes()):
        if len(data)!=511 or positions[name]&255:
            raise ValueError("Biased 511-entry page-spanning table geometry")
        for i,value in enumerate(data):
            image[positions[name]+i]=value
        image[positions[name]+511]=0
    segments=[{"name":"KERNEL_CODE","start":"$%04X"%start,
               "bytes":CODE_SLOT},
              {"name":"ALIGN_PADDING","start":"$%04X"%(start+CODE_SLOT),
               "bytes":positions[TABLES[0]]-(start+CODE_SLOT)}]
    segments.extend({"name":name,"start":"$%04X"%positions[name],
                     "bytes":TABLE_SLOT} for name in TABLES)
    return image,labels,segments,end


def provenance(root=ROOT):
    return hashlib.sha256((root/SOURCE).read_bytes()).hexdigest()


if __name__=="__main__":
    for start,io,zp in ((0x8000,0xc000,0x50),(0x7123,0xc040,0x70)):
        mem,labels,ranges,end=assemble(start,io,zp)
        print("HISTORICAL UMUL24 V2 SOURCE",hex(start),len(mem),
              "native-entry",hex(labels["umul24"]),
              "public-entry",hex(labels[PUBLIC]),"end",hex(end))
