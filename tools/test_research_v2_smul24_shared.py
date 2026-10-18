#!/usr/bin/env python3
"""Prove signed UMUL24 composition uses one $CA-biased source/table image."""
from __future__ import annotations
import random
import unittest
from mini6502 import CPU
import selective_v2_fast_umul24 as emitter

EDGES=(0,1,2,3,127,255,256,0x7fffff,0x800000,0x800001,
       0xfffffe,0xffffff)
MASK48=(1<<48)-1


def corpus():
    pairs=[(x,y) for x in EDGES for y in EDGES]
    r=random.Random(0x5A2424)
    pairs.extend((r.getrandbits(24),r.getrandbits(24))
                 for _ in range(512-len(pairs)))
    return pairs


def signed(x):
    return x-(1<<24) if x&0x800000 else x


class SharedBiasedSigned24(unittest.TestCase):
    def test_signed_correction_and_unsigned_interleaving_two_origins(self):
        for code,io,zp in ((0x8000,0xc000,0x50),
                           (0x7123,0xc040,0x70)):
            with self.subTest(code=code):
                image,labels,ranges,end=emitter.assemble(code,io,zp)
                self.assertIn(emitter.SIGNED_PUBLIC,labels)
                self.assertEqual(labels[emitter.PUBLIC],code)
                self.assertTrue(code<labels[emitter.SIGNED_PUBLIC]<code+512)
                self.assertEqual(sum(s["name"] in emitter.TABLES for s in ranges),4)
                mem=bytearray(65536)
                for at,value in image.items():
                    mem[at]=value
                cpu=CPU(mem)
                sp=cpu.sp
                ticks_signed=[]
                for i,(x,y) in enumerate(corpus()):
                    xb=x.to_bytes(3,"little")
                    yb=y.to_bytes(3,"little")
                    for signed_case in (False,True):
                        mem[io:io+4]=xb+bytes([0x6a])
                        mem[io+4:io+8]=yb+bytes([0xa5])
                        mem[io+8:io+16]=bytes([0xcc]*6+[0x49,0x59])
                        cpu.a=(x^i)&255
                        cpu.x=(y>>8)&255
                        cpu.y=(i*19)&255
                        cpu.c=i&1
                        cpu.d=0
                        cycles=cpu.call(labels[
                            emitter.SIGNED_PUBLIC if signed_case else emitter.PUBLIC],
                            100000)
                        a=signed(x) if signed_case else x
                        b=signed(y) if signed_case else y
                        self.assertEqual(
                            int.from_bytes(mem[io+8:io+14],"little"),
                            (a*b)&MASK48,
                            (code,i,x,y,signed_case))
                        self.assertEqual(cpu.c,0)
                        self.assertEqual(cpu.sp,sp)
                        self.assertEqual(bytes(mem[io:io+4]),xb+bytes([0x6a]))
                        self.assertEqual(bytes(mem[io+4:io+8]),yb+bytes([0xa5]))
                        self.assertEqual(bytes(mem[io+14:io+16]),
                                         bytes([0x49,0x59]))
                        if signed_case:
                            ticks_signed.append(cycles)
                print("SHARED V2 BIASED SMUL24",hex(code),
                      "cases",len(ticks_signed),
                      "signed_mean",round(sum(ticks_signed)/len(ticks_signed),3),
                      "signed_max",max(ticks_signed),
                      "signed_entry",hex(labels[emitter.SIGNED_PUBLIC]),
                      flush=True)

if __name__=="__main__":
    unittest.main()
