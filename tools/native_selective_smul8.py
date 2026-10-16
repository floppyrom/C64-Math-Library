#!/usr/bin/env python3
"""Native x64sc signed 8x8 proof for 46-byte historical writable-SMC kernel."""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import random
import socket
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import math_builder
import selective_linker
import selective_smul8

H, INPUT, OUTPUT, STRIDE, N = 0x2000, 0x3000, 0x3800, 0x80, 96


def expected(x, y):
    value=selective_smul8.signed_reference(x,y)
    return value & 255, (value >> 8) & 255


def pairs():
    edges = (0,1,2,3,15,16,17,63,64,127,128,129,254,255)
    selected = [(a,b) for a in edges for b in (0,1,127,128,255)]
    rng = random.Random(0xD158C64)
    selected.extend((rng.randrange(256),rng.randrange(256))
                    for _ in range(N-len(selected)))
    assert len(selected) == N
    return selected


def harness(entry, io):
    b = bytearray()
    def emit(*v): b.extend(v)
    def absolute(opcode, addr): emit(opcode, addr & 255, addr >> 8)
    emit(0x78,0xd8,0xa9,0x34,0x85,0x01,0xa2,0x00)  # SEI CLD RAM map X=0
    loop = H + len(b)
    absolute(0xbd, INPUT)
    absolute(0x8d, io)
    absolute(0xbd, INPUT+STRIDE)
    absolute(0x8d, io+4)
    emit(0xa9,0xa5)
    absolute(0x8d, io+8)
    emit(0xa9,0x5a)
    absolute(0x8d, io+9)
    emit(0x8a,0x48)
    absolute(0x20, entry)
    emit(0x08,0x68)                        # PHP / PLA capture P before flags change
    absolute(0x8d, 0xc030)
    emit(0x68,0xaa)                        # restore index
    for src,dst in ((io+8,OUTPUT),(io+9,OUTPUT+STRIDE),
                    (0xc030,OUTPUT+2*STRIDE),(io,OUTPUT+3*STRIDE),
                    (io+4,OUTPUT+4*STRIDE)):
        absolute(0xad, src)
        absolute(0x9d, dst)
    emit(0xe8,0xe0,N,0xf0,0x03)
    absolute(0x4c,loop)
    stop = H + len(b)
    absolute(0x4c,stop)
    return bytes(b), stop


def verify(vice, image, entry, origin, io, tag, port, folder, api):
    memory = bytearray(65536)
    memory[origin:origin+len(image)-2] = image[2:]
    code, stop = harness(entry, io)
    assert len(code) < 0x300
    memory[H:H+len(code)] = code
    operands = pairs()
    for idx,(x,y) in enumerate(operands):
        memory[INPUT+idx] = x
        memory[INPUT+STRIDE+idx] = y
    prg=folder/(tag+".prg")
    dump=folder/(tag+".bin")
    prg.write_bytes(bytes((H&255,H>>8))+memory[H:0xc100])
    args=[vice,"-console","-silent","-sounddev","dummy","-warp",
          "-remotemonitor","-remotemonitoraddress","127.0.0.1:"+str(port),
          "-initbreak","reset"]
    with (folder/(tag+".log")).open("w") as out:
        proc=subprocess.Popen(args,cwd=folder,stdout=out,stderr=out)
        try:
            for _ in range(150):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.1)
                    break
                except (ConnectionRefusedError,TimeoutError):
                    time.sleep(.04)
            else:
                raise RuntimeError("x64sc remote monitor connection failed")
            sock.settimeout(.25)
            def monitor(command,marker):
                sock.sendall((command+"\n").encode())
                received=b""
                for _ in range(180):
                    try:
                        part=sock.recv(16384)
                        if not part:
                            break
                        received+=part
                        if marker.encode() in received and received.endswith(b") "):
                            break
                    except socket.timeout:
                        continue
                if marker.encode() not in received:
                    raise RuntimeError("VICE monitor failed: %r %r" %
                                       (command,received[-600:]))
            monitor('load "'+str(prg)+'" 0',"Loading")
            monitor("break "+format(stop,"04x"),"BREAK:")
            monitor("g "+format(H,"04x"),"Stop on  exec")
            monitor('bsave "'+str(dump)+'" 0 '+
                    format(OUTPUT,"04x")+" "+
                    format(OUTPUT+5*STRIDE-1,"04x"),"Saving")
            sock.sendall(b"quit\n")
            sock.close()
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    saved = dump.read_bytes()
    assert len(saved) == 5*STRIDE, len(saved)
    for i,(x,y) in enumerate(operands):
        value=saved[i]
        high=saved[STRIDE+i]
        p=saved[2*STRIDE+i]
        orig_x=saved[3*STRIDE+i]
        orig_y=saved[4*STRIDE+i]
        expect_low, expect_high=expected(x,y)
        assert (value,high,p&1,orig_x,orig_y)==(
            expect_low,expect_high,0,x,y), (tag,i,x,y,value,high,p,orig_x,orig_y)
    return hashlib.sha256(saved).hexdigest()


def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to working x64sc")
    index=math_builder.operation_index()
    with tempfile.TemporaryDirectory(prefix="selective_smul8_vice_") as directory:
        folder=Path(directory)
        for sequence,(origin,io) in enumerate(((0x8000,0xc000),
                                                (0x80d2,0xc040))):
            plan=math_builder.create_plan(
                index,["SMUL8"],zp_budget=0,ram_budget=2336,
                pins={"SMUL8":"link:v1-resident-smc"})
            result=selective_linker.build(
                plan,folder,memory={"code_base":origin,"math_io":io})
            assert result["resource_use"]["shared_table_bytes"]==2044
            entry=int(result["operations"][0]["entry"][1:],16)
            assert entry==origin
            image=(folder/"math_selective.prg").read_bytes()
            digest=verify(vice,image,entry,origin,io,
                          "smul8_%04x"%origin,7680+sequence,
                          folder,"SMUL8")
            print("NATIVE SMUL8 SMC",hex(origin),"PASS",N,digest,flush=True)
    print("NATIVE HISTORICAL SMUL8 PASS",2*N)


if __name__ == "__main__":
    main()
