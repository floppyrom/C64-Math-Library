#!/usr/bin/env python3
"""The original V3 signed24 Q/R producer, independently relocated and paired."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mini6502 import CPU, Assembler
import math_builder
import selective_linker as linker
from test_selective_sdiv24 import reference
from test_selective_sdiv24_qzero import corpus

OPS = ("SDIV24", "SMOD24")
V3 = "link:v3-signed-magnitude"
PORTABLE = "link:portable-zerozp"


def load(td, variant, code, io, zp):
    plan=math_builder.create_plan(math_builder.operation_index(), list(OPS),
        objective="size",zp_budget=9,ram_budget=2500,
        pins={op:variant for op in OPS})
    folder=Path(td)/(variant.split(":")[-1])
    if variant==V3:
        mod=linker.MODULES["MATH_SDIV24"][V3]
        localmap={"KERNEL_CODE":code,"INPUT_NUM":io+16,"INPUT_DIV":io+20,
                  "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28,"TEMP_ZP":zp}
        candidate, checklabels, _=Assembler().assemble(
            linker.relocate_source(mod,localmap,linker.ROOT))
        assert len(candidate)==1897 and set(candidate)==set(
            range(code,code+1897)), (
                "V3 compact source layout",len(candidate),
                hex(min(candidate)),hex(max(candidate)),
                [hex(v) for v in sorted(set(range(code,code+1897))-set(candidate))[:12]],
                [hex(v) for v in sorted(set(candidate)-set(range(code,code+1897)))[:12]])
    report=linker.build(plan,folder,memory={
        "code_base":code,"math_io":io,"zp_base":zp,"scratch_base":io+0x40})
    entries={x["api"]:int(x["entry"][1:],16) for x in report["operations"]}
    image=(folder/"math_selective.prg").read_bytes()
    assert int.from_bytes(image[:2],"little")==code
    mem=bytearray(65536)
    mem[code:code+len(image)-2]=image[2:]
    cpu=CPU(mem)
    labels={}
    if variant==V3:
        mod=linker.MODULES["MATH_SDIV24"][V3]
        locations={"KERNEL_CODE":code,"INPUT_NUM":io+16,"INPUT_DIV":io+20,
                   "OUTPUT_QUOT":io+24,"OUTPUT_REM":io+28,"TEMP_ZP":zp}
        sparse, labels, _=Assembler().assemble(
            linker.relocate_source(mod,locations,linker.ROOT))
        assert len(sparse)==1897
        assert all(mem[address]==byte for address,byte in sparse.items())
    return cpu,entries,report,len(image)-2,labels


def call(cpu,entry,io,n,d,flag):
    mem=cpu.mem
    b_n=n.to_bytes(3,"little")+bytes([0x5a])
    b_d=d.to_bytes(3,"little")+bytes([0xa5])
    mem[io+16:io+20]=b_n
    mem[io+20:io+24]=b_d
    mem[io+24:io+28]=bytes([0xcc,0xcc,0xcc,0x39])
    mem[io+28:io+32]=bytes([0xdd,0xdd,0xdd,0x59])
    cpu.d=0;cpu.c=flag
    cpu.a=(n^d)&255;cpu.x=(n>>8)&255;cpu.y=(d>>8)&255
    sp=cpu.sp
    cycles=cpu.call(entry,100000)
    got=(int.from_bytes(mem[io+24:io+27],"little"),
         int.from_bytes(mem[io+28:io+31],"little"),cpu.c)
    if got!=reference(n,d):
        raise AssertionError((hex(entry),hex(n),hex(d),got,reference(n,d)))
    if bytes(mem[io+16:io+20])!=b_n or bytes(mem[io+20:io+24])!=b_d:
        raise AssertionError("Historical source modified public numerator/divisor")
    if mem[io+27]!=0x39 or mem[io+31]!=0x59 or cpu.sp!=sp:
        raise AssertionError("High public result sentinel or stack changed")
    return cycles


class Signed24V3TransplantTests(unittest.TestCase):
    def test_v3_donor_shared_image_public_abi_and_relocation(self):
        for code,io,zp in ((0x8000,0xc000,0x40),(0x7123,0xc040,0x60)):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as d:
                cpu,entry,man,size,labels=load(d,V3,code,io,zp)
                orig,oldent,oldman,oldsize,_=load(d,PORTABLE,code,io,zp)
                self.assertEqual((size,oldsize),(1897,325))
                self.assertEqual(man["resource_use"]["zero_page_bytes"],9)
                self.assertEqual(man["resource_use"]["private_ram_scratch_bytes"],0)
                self.assertEqual(len(man["link_order"]),1)
                self.assertEqual(entry["MATH_SDIV24"],code)
                self.assertEqual(entry["MATH_SMOD24"],code+3)
                self.assertTrue(
                    {"L5A40", "L83E2", "L8801_ADC_IMMEDIATE",
                     "FAST_SDIV24_V3", "FAST_SMOD24_V3"} <= set(labels))
                smc=labels["L8801_ADC_IMMEDIATE"]+1
                assert code<=smc<code+size
                donor_before=bytes(cpu.mem[code:code+size])
                results=[]
                for i,(n,divisor) in enumerate(corpus()):
                    operation="MATH_SDIV24" if i&1 else "MATH_SMOD24"
                    donor_cycles=call(cpu,entry[operation],io,n,divisor,i&1)
                    portable_cycles=call(orig,oldent[operation],io,n,divisor,i&1)
                    results.append((portable_cycles,donor_cycles))
                modified={code+i for i,(a,b) in enumerate(zip(donor_before,cpu.mem[code:code+size])) if a!=b}
                self.assertLessEqual(modified,{smc},
                    "Only the original ADC immediate byte is permitted to self-modify")
                total=len(results)
                paired={"placement":"$%04X/$%04X"%(code,io),"cases":total,
                        "donor_bytes":size,"compact_bytes":oldsize,
                        "mean_donor":round(sum(b for a,b in results)/total,3),
                        "mean_portable":round(sum(a for a,b in results)/total,3),
                        "min_donor":min(b for a,b in results),
                        "max_donor":max(b for a,b in results),
                        "saved_cycles":sum(a-b for a,b in results),
                        "worst_regression":max(b-a for a,b in results)}
                print("V3_SIGNED24_PAIRED",json.dumps(paired,sort_keys=True),flush=True)

if __name__=="__main__":
    unittest.main()
