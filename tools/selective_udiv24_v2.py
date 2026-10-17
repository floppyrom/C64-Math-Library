#!/usr/bin/env python3
"""Relocate the exact canonical V2 UDIV24/UMOD24 source, including its fast chain.

The verified source is read unchanged and fingerprinted by the builder. This
adapter only rebinds public operands, the three private zero-page slots and
the code islands; it never copies executable bytes from a profile PRG.
V2 source uses NMOS LAX and ANC and one writable immediate tail-bias operand.
"""
from __future__ import annotations
from pathlib import Path
from mini6502 import Assembler

ROOT=Path(__file__).resolve().parents[1]
SOURCE="relocatable_source/v2_pareto_fast/udiv24_direct_repose.inc"
ENTRY="DU24F_div_u24"

def render(code: int, aux: int, io: int, zp: int, root: Path=ROOT) -> str:
    if not (0x10 <= zp <= 0xfd):
        raise ValueError("V2 U24 needs three zero-page bytes outside the 6510 port")
    src=(root/SOURCE).read_text(encoding="utf-8")
    # Remove historical pair of fixed-address public JMP trampolines.
    marker="* = REG_KERNEL+$0800\n"
    if src.count(marker)!=1: raise ValueError("canonical V2 initial island changed")
    src=src.split(marker,1)[1]
    # Original V2 register island is split at $10E1 relative to REG_KERNEL;
    # preserve logical labels while relocating the second code island.
    second="* = REG_KERNEL+$10E1"
    if src.count(second)!=1: raise ValueError("canonical V2 second island changed")
    src=src.replace(second,"* = KERNEL_AUX")
    if src.count("!byte $AF,<MATH_N+2,>MATH_N+2")!=1: raise ValueError("LAX source changed")
    src=src.replace("!byte $AF,<MATH_N+2,>MATH_N+2 ; LAX abs",
                    "lax MATH_N+2")
    if src.count("!byte $0b,$00")!=1: raise ValueError("ANC source changed")
    src=src.replace("!byte $0b,$00","anc #0")
    header=(f"!cpu 6510\nKERNEL_CODE = ${code:04X}\n"
            f"KERNEL_AUX = ${aux:04X}\n"
            f"MATH_N = ${io+16:04X}\nMATH_D = ${io+20:04X}\n"
            f"MATH_Q = ${io+24:04X}\nMATH_R = ${io+28:04X}\n"
            f"ZP_MAIN = ${zp-14:02X}\n"
            "* = KERNEL_CODE\n")
    return header+src

def assemble(code: int, aux: int, io: int, zp: int, root: Path=ROOT):
    machine,labels,_=Assembler().assemble(render(code,aux,io,zp,root))
    if ENTRY not in labels: raise ValueError("Missing canonical entry")
    region1=sorted(a for a in machine if code<=a<aux)
    region2=sorted(a for a in machine if a>=aux)
    if not region1 or not region2 or region1[0]!=code or region2[0]!=aux:
        raise ValueError("V2 U24 code islands not located where requested")
    if region1 != list(range(code,code+len(region1))):
        raise ValueError("V2 U24 main code island contains a hole")
    if region2 != list(range(aux,aux+len(region2))):
        raise ValueError("V2 U24 second code island contains a hole")
    return machine,labels,(len(region1),len(region2))

if __name__=="__main__":
    import sys
    mem,labels,sizes=assemble(0x7000,0x9000,0xc000,0x90)
    print("V2 U24 GENERATED SOURCE SIZES",sizes,
          "ENTRY",hex(labels[ENTRY]),"CODE",len(mem),flush=True)
