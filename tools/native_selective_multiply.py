#!/usr/bin/env python3
"""Native x64sc regression for selected compact UMUL8/UMUL16 PRGs.

This checks arithmetic, carry-clear, caller inputs and two placements,
not emulated VIC contention or native cycle timings.
"""
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

H = 0x2000
INPUT = 0x3000
OUTPUT = 0x3800
STRIDE = 0x80
N = 96


def operands():
    edge = [(0,0),(1,0),(0,1),(1,1),(0xffff,0xffff),
            (0xffff,1),(1,0xffff),(0x8000,2),(0x1234,0xabcd),
            (0xff00,0x0101),(0x0101,0xff00),(255,255)]
    randomizer = random.Random(0x16C64026)
    edge += [(randomizer.randrange(65536), randomizer.randrange(65536))
             for _ in range(N-len(edge))]
    return edge


def harness(entry, io):
    out = bytearray()
    def emit(*values):
        out.extend(values)
    def op(opcode, where):
        emit(opcode, where & 255, where >> 8)
    emit(0x78, 0xD8, 0xA9, 0x34, 0x85, 0x01, 0xA2, 0x00)
    loop = H+len(out)
    for slot, target in enumerate((io, io+1, io+4, io+5)):
        op(0xBD, INPUT+slot*STRIDE)
        op(0x8D, target)
    emit(0x8A,0x48)
    op(0x20, entry)
    # Snapshot result status before restoring the loop index.
    emit(0x08,0x68)
    op(0x8D,0xC030)
    emit(0x68,0xAA)
    for slot, src in enumerate((io+8,io+9,io+10,io+11,io,io+1,io+4,io+5,0xC030)):
        op(0xAD,src)
        op(0x9D,OUTPUT+slot*STRIDE)
    emit(0xE8,0xE0,N,0xF0,0x03)
    op(0x4C,loop)
    halt=H+len(out)
    op(0x4C,halt)
    assert len(out)<0x300
    return bytes(out),halt


def run_native(vice, prg_bytes, entry, code, io, tag, port, folder, bits=16):
    memory=bytearray(65536)
    memory[code:code+len(prg_bytes)-2]=prg_bytes[2:]
    stub,halt=harness(entry,io)
    memory[H:H+len(stub)]=stub
    tests=operands()
    for i,(x,y) in enumerate(tests):
        for col,byte in enumerate((x&255,x>>8,y&255,y>>8)):
            memory[INPUT+col*STRIDE+i]=byte
    prog=folder/(tag+".prg")
    dump=folder/(tag+".bin")
    prog.write_bytes(bytes((H&255,H>>8))+memory[H:0xC200])
    args=[vice,"-console","-silent","-sounddev","dummy","-warp",
          "-remotemonitor","-remotemonitoraddress","127.0.0.1:"+str(port),
          "-initbreak","reset"]
    with (folder/(tag+".log")).open("w") as log:
        proc=subprocess.Popen(args,cwd=folder,stdout=log,stderr=log)
        try:
            for _ in range(150):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.1)
                    break
                except (ConnectionRefusedError,TimeoutError):
                    time.sleep(.04)
            else:
                raise RuntimeError("Native VICE monitor timeout")
            sock.settimeout(.25)
            def command(line,needle):
                sock.sendall((line+"\n").encode())
                data=b""
                for _ in range(180):
                    try:
                        block=sock.recv(16384)
                        if not block:
                            break
                        data+=block
                        if needle.encode() in data and data.endswith(b") "):
                            break
                    except socket.timeout:
                        continue
                if needle.encode() not in data:
                    raise RuntimeError((line,data[-500:]))
            command('load "'+str(prog)+'" 0',"Loading")
            command("break "+format(halt,"04x"),"BREAK:")
            command("g "+format(H,"04x"),"Stop on  exec")
            command('bsave "'+str(dump)+'" 0 '+format(OUTPUT,"04x")+
                    " "+format(OUTPUT+9*STRIDE-1,"04x"),"Saving")
            sock.sendall(b"quit\n")
            sock.close()
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    data=dump.read_bytes()
    assert len(data)==9*STRIDE
    for i,(x,y) in enumerate(tests):
        value=sum(data[(j*STRIDE)+i]<<(8*j) for j in range(4))
        n=data[4*STRIDE+i]|(data[5*STRIDE+i]<<8)
        d=data[6*STRIDE+i]|(data[7*STRIDE+i]<<8)
        expected = x*y if bits == 16 else (x&255)*(y&255)
        if bits == "shr8":
            expected = (x*y) >> 8
            valid = (value & 0xffffff) == expected
        else:
            valid = value == expected if bits == 16 else (value & 0xffff) == expected
        processor_status = data[8*STRIDE+i]
        if not valid or (n,d)!=(x,y) or (processor_status & 1):
            raise AssertionError((tag,i,x,y,value,n,d,processor_status))
    return hashlib.sha256(data).hexdigest()


def main():
    vice=os.environ.get("VICE_WRAPPER")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must point to a working x64sc")
    index=math_builder.operation_index()
    total=0
    with tempfile.TemporaryDirectory(prefix="selective_umul16_native_") as tmp:
        folder=Path(tmp)
        for i,(code,io) in enumerate(((0x8000,0xC000),(0x7123,0xC040))):
            plan=math_builder.create_plan(
                index,["UMUL16"],zp_budget=0,ram_budget=146)
            man=selective_linker.build(
                plan,folder,memory={"code_base":code,"math_io":io})
            assert man["resource_use"]["image_span_bytes"]==108
            entry=int(man["operations"][0]["entry"][1:],16)
            image=(folder/"math_selective.prg").read_bytes()
            digest=run_native(vice,image,entry,code,io,
                              "umul16_%04x"%code,7480+i,folder)
            total+=N
            print("NATIVE UMUL16",hex(code),N,"PASS",digest,flush=True)
    # UMUL16_SHR8 is an independent zero-ZP reference with a 24-bit result.
    for i, (code, io) in enumerate(((0x8000, 0xC000), (0x7123, 0xC040))):
        plan = math_builder.create_plan(
            index, ["UMUL16_SHR8"], zp_budget=0, ram_budget=164)
        with tempfile.TemporaryDirectory(prefix="selective_umul16_shr8_native_") as temp:
            folder = Path(temp)
            man = selective_linker.build(
                plan, folder, memory={"code_base": code, "math_io": io})
            assert man["resource_use"]["image_span_bytes"] == 126
            entry = int(man["operations"][0]["entry"][1:], 16)
            image = (folder / "math_selective.prg").read_bytes()
            digest = run_native(vice, image, entry, code, io,
                                "umul16_shr8_%04x" % code, 7500+i, folder,
                                bits="shr8")
            total += N
            print("NATIVE UMUL16_SHR8", hex(code), N, "PASS", digest, flush=True)
    # Independent table-driven shifted product, genuine compiled PRG on x64sc.
    for i, (code, io) in enumerate(((0x8000, 0xC000), (0x7123, 0xC040))):
        plan = math_builder.create_plan(
            index, ["UMUL16_SHR8"], zp_budget=0, ram_budget=1314,
            pins={"UMUL16_SHR8":"link:quarter-square"})
        with tempfile.TemporaryDirectory(prefix="selective_umul16_shr8_qs_native_") as temp:
            folder = Path(temp)
            man = selective_linker.build(
                plan, folder, memory={"code_base":code,"math_io":io})
            assert man["resource_use"]["image_span_bytes"] == 1278
            entry = int(man["operations"][0]["entry"][1:],16)
            data = (folder/"math_selective.prg").read_bytes()
            digest = run_native(vice,data,entry,code,io,
                                "umul16_shr8_qs_%04x"%code,7520+i,folder,
                                bits="shr8")
            total += N
            print("NATIVE UMUL16_SHR8 QUARTER-SQUARE",hex(code),N,"PASS",digest,flush=True)
    # UMUL8 stores a 16-bit result; the two higher Z bytes are outside its
    # public output contract and intentionally not compared.
    for i,(code,io) in enumerate(((0x8000,0xC000),(0x7123,0xC040))):
        plan=math_builder.create_plan(
            index,["UMUL8"],zp_budget=0,ram_budget=95)
        with tempfile.TemporaryDirectory(prefix="selective_umul8_native_") as temp:
            folder=Path(temp)
            man=selective_linker.build(
                plan,folder,memory={"code_base":code,"math_io":io})
            assert man["resource_use"]["image_span_bytes"]==60
            entry=int(man["operations"][0]["entry"][1:],16)
            image=(folder/"math_selective.prg").read_bytes()
            digest=run_native(vice,image,entry,code,io,
                              "umul8_%04x"%code,7490+i,folder,bits=8)
            total+=N
            print("NATIVE UMUL8",hex(code),N,"PASS",digest,flush=True)
    assert total==768
    print("NATIVE SELECTIVE UMUL8/UMUL16/UMUL16_SHR8 PLUS QS PASS",total)


if __name__=="__main__":
    main()
