#!/usr/bin/env python3
"""Paired, exact-operand CPU-model validation of 32/16 unrolled zero-ZP producer."""
from __future__ import annotations

from pathlib import Path
import re
import unittest

from mini6502 import Assembler,CPU,load_sparse
from selective_speed_u3216 import corpus,COUNT

ROOT=Path(__file__).resolve().parents[1]
SOURCE="routines/divide/u32_by_u16_accum_unrolled_selective.asm"
BASE="routines/divide/u32_by_u16_accum_selective.asm"

def assemble(source_path,code,io,scratch):
    s=(ROOT/source_path).read_text(encoding="utf-8")
    bindings={
        "KERNEL_CODE":code,"INPUT_NUM":io+16,"INPUT_DIV":io+20,
        "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28,"TEMP_RAM":scratch}
    for name,addr in bindings.items():
        s,count=re.subn(r"(?m)^"+re.escape(name)+r"\s*=\s*\$[0-9A-Fa-f]+\s*$",
                       name+" = $%04X"%addr,s)
        if count!=1:
            raise ValueError("Missing source binding "+name)
    mem,labels,_=Assembler().assemble(s)
    if set(mem)!=set(range(code,code+len(mem))):
        raise ValueError("Noncontiguous divider code image")
    a=labels["FAST_UDIV32_16_ACCUM"]
    b=labels["FAST_UMOD32_16_ACCUM"]
    if a!=code or b!=a:
        raise ValueError("Missing shared Q/R entry")
    return mem,a

def benchmark(image,entry,io,pairs):
    cpu=CPU(load_sparse(image))
    original=dict(image)
    sp=cpu.sp
    total=0
    for i,(n,d) in enumerate(pairs):
        for mode in range(2):
            cpu.mem[io+16:io+20]=n.to_bytes(4,"little")
            cpu.mem[io+20:io+22]=d.to_bytes(2,"little")
            cpu.mem[io+24:io+28]=b"\x55"*4
            cpu.mem[io+28:io+32]=b"\x66\x66\x69\xab"
            cpu.d=0;cpu.c=(i^mode^n^d)&1
            total+=cpu.call(entry,16000)
            got=(int.from_bytes(cpu.mem[io+24:io+28],"little"),
                 int.from_bytes(cpu.mem[io+28:io+30],"little"),cpu.c)
            expect=(n//d if d else 0,n%d if d else 0,int(d==0))
            if (got!=expect or cpu.sp!=sp or
                cpu.mem[io+16:io+20]!=n.to_bytes(4,"little") or
                cpu.mem[io+20:io+22]!=d.to_bytes(2,"little") or
                cpu.mem[io+30:io+32]!=b"\x69\xab"):
                raise AssertionError((hex(n),hex(d),got,expect))
    if any(cpu.mem[k]!=v for k,v in original.items()):
        raise AssertionError("Non-SMC divider code mutated")
    return total/(2*len(pairs))

class UnrolledU3216SourceTests(unittest.TestCase):
    def test_public_quotient_remainder_same_corpus_two_relocations(self):
        pairs=corpus()
        self.assertEqual(len(pairs),COUNT)
        for code,io,scratch in ((0x8000,0xc000,0xc020),
                                (0x7123,0xc040,0xc080)):
            with self.subTest(code=code):
                old,base_entry=assemble(BASE,code,io,scratch)
                new,fast_entry=assemble(SOURCE,code,io,scratch)
                self.assertEqual(len(old),131)
                self.assertGreater(len(new),len(old))
                self.assertLess(len(new),2800)
                prior=benchmark(old,base_entry,io,pairs)
                candidate=benchmark(new,fast_entry,io,pairs)
                self.assertLess(candidate,prior)
                print("UNROLLED U3216",hex(code),
                      "size",len(new),"prior",prior,
                      "candidate",candidate,"saving",prior-candidate,
                      "speedup",prior/candidate,flush=True)

if __name__=="__main__":
    unittest.main()
