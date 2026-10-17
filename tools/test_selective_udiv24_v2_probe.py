#!/usr/bin/env python3
"""Same-input canonical V2 UDIV24/UMOD24 standalone portability proof."""
from __future__ import annotations
import random
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import selective_udiv24_v2 as src
from mini6502 import CPU

def cases():
    edges=(0,1,2,3,7,15,127,255,256,257,65535,65536,65537,
           0x7fffff,0x800000,0xfffffe,0xffffff)
    rng=random.Random(0x241017)
    pairs=[(n,d) for n in edges for d in edges]
    pairs += [(rng.getrandbits(24),rng.getrandbits(24)) for _ in range(550)]
    pairs += [(rng.getrandbits(24),0) for _ in range(35)]
    pairs += [(rng.getrandbits(24),rng.randrange(1,256)) for _ in range(125)]
    return pairs

def main():
    for base,aux,io,zp in ((0x7000,0x9000,0xc000,0x90),
                           (0x7123,0x9300,0xc040,0xb0)):
        machine,labels,sizes=src.assemble(base,aux,io,zp)
        print("V2 SOURCE SIZES",sizes,"ENTRY",hex(labels[src.ENTRY]),
              "CODE TOTAL",sum(sizes),flush=True)
        cpu=CPU(bytearray(65536))
        for addr,value in machine.items(): cpu.mem[addr]=value
        before=bytes(cpu.mem[base:base+sizes[0]])+bytes(cpu.mem[aux:aux+sizes[1]])
        total=0
        sp=cpu.sp
        for n,d in cases():
            cpu.mem[io+16:io+20]=n.to_bytes(3,"little")+b"\x6a"
            cpu.mem[io+20:io+24]=d.to_bytes(3,"little")+b"\xa9"
            cpu.mem[io+24:io+28]=b"\x55"*4
            cpu.mem[io+28:io+32]=b"\x66"*4
            cpu.d=0
            cycles=cpu.call(labels[src.ENTRY],40000)
            q=int.from_bytes(cpu.mem[io+24:io+27],"little")
            r=int.from_bytes(cpu.mem[io+28:io+31],"little")
            expect=(n//d if d else 0,n%d if d else 0,int(d==0))
            if (q,r,cpu.c)!=expect:
                raise AssertionError((hex(base),hex(n),hex(d),(q,r,cpu.c),expect))
            assert cpu.mem[io+16:io+20]==n.to_bytes(3,"little")+b"\x6a"
            assert cpu.mem[io+20:io+24]==d.to_bytes(3,"little")+b"\xa9"
            assert cpu.mem[io+27]==0x55 and cpu.mem[io+31]==0x66
            assert cpu.sp==sp
            total+=cycles
        # The writable bias byte can legitimately return to its original value
        # after the final test; checking only the final image is not evidence
        # about whether self-modifying code ran. Record the source SMC contract
        # and validate each arithmetic call instead.
        assert "sta DU24F_tail_bias+1" in src.render(base,aux,io,zp)
        print("V2 UDIV24 SOURCE PASS",len(cases()),"sum cycles",total,
              "mean cycles",total/len(cases()),flush=True)

if __name__=="__main__":main()
