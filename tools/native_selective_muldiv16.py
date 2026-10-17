#!/usr/bin/env python3
"""Native x64sc full 32-bit multiply/divide with signed/unsigned Q and R."""
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

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker
from test_selective_muldiv16 import expected

H=0x2000
INPUT=0x3000
OUTPUT=0x3800
STRIDE=0x80
N=96

def operands():
    cases=[(0,0,0),(1,1,0),(1,1,1),(0xffff,0xffff,0xffff),
           (0x8000,0x8000,0xffff),(0xffff,0x8000,0x8000),
           (0x7fff,0x7fff,1),(0x8000,1,1),
           (0x8000,0xffff,0x7fff),(0xffff,0xffff,1),
           (0xffff,0xffff,0),(0,0xffff,0)]
    rng=random.Random(0x64164e)
    cases.extend((rng.randrange(65536),rng.randrange(65536),rng.randrange(65536))
                 for _ in range(N-len(cases)))
    return cases

def harness(entry,io):
    o=bytearray()
    def emit(*v):o.extend(v)
    def op(code,addr):emit(code,addr&255,addr>>8)
    emit(0x78,0xd8,0xa9,0x34,0x85,0x01,0xa2,0)
    loop=H+len(o)
    inp=[io,io+1,io+4,io+5,io+20,io+21]
    for col,where in enumerate(inp):
        op(0xbd,INPUT+col*STRIDE);op(0x8d,where)
    emit(0x8a,0x48);op(0x20,entry)
    emit(0x08,0x68);op(0x8d,0xc030)
    emit(0x68,0xaa)
    out=[io+i for i in range(24,28)]+[io+28,io+29]+inp+[0xc030]
    assert len(out)==13
    for col,where in enumerate(out):
        op(0xad,where);op(0x9d,OUTPUT+col*STRIDE)
    emit(0xe8,0xe0,N,0xf0,0x03);op(0x4c,loop)
    halt=H+len(o);op(0x4c,halt)
    assert len(o)<0x300
    return bytes(o),halt

def run_native(vice, prg, entry, code, io, signed, tag, port, folder):
    mem=bytearray(65536)
    mem[code:code+len(prg)-2]=prg[2:]
    stub,halt=harness(entry,io)
    mem[H:H+len(stub)]=stub
    cases=operands()
    for i,(x,y,d) in enumerate(cases):
        b=(*x.to_bytes(2,"little"),*y.to_bytes(2,"little"),*d.to_bytes(2,"little"))
        for col,byte in enumerate(b):
            mem[INPUT+col*STRIDE+i]=byte
    image=folder/(tag+".prg")
    result=folder/(tag+".bin")
    image.write_bytes(bytes((H&255,H>>8))+mem[H:0xc200])
    cmd=[vice,"-console","-silent","-sounddev","dummy","-warp",
         "-remotemonitor","-remotemonitoraddress","127.0.0.1:"+str(port),
         "-initbreak","reset"]
    with (folder/(tag+".log")).open("w") as log:
        proc=subprocess.Popen(cmd,cwd=folder,stdout=log,stderr=log)
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
                        part=sock.recv(16384)
                        if not part:break
                        data+=part
                        if needle.encode() in data and data.endswith(b") "):break
                    except socket.timeout:
                        continue
                if needle.encode() not in data:raise RuntimeError((line,data[-500:]))
            command('load "'+str(image)+'" 0',"Loading")
            command("break "+format(halt,"04x"),"BREAK:")
            command("g "+format(H,"04x"),"Stop on  exec")
            command('bsave "'+str(result)+'" 0 '+format(OUTPUT,"04x")+
                    " "+format(OUTPUT+13*STRIDE-1,"04x"),"Saving")
            sock.sendall(b"quit\n");sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
    data=result.read_bytes()
    assert len(data)==13*STRIDE
    for i,(x,y,d) in enumerate(cases):
        b=bytes(data[j*STRIDE+i] for j in range(13))
        q=int.from_bytes(b[:4],"little")
        r=int.from_bytes(b[4:6],"little")
        xo=int.from_bytes(b[6:8],"little")
        yo=int.from_bytes(b[8:10],"little")
        do=int.from_bytes(b[10:12],"little")
        c=b[12]&1
        eq,er,ec=expected(x,y,d,signed)
        if (q,r,c,xo,yo,do)!=(eq,er,ec,x,y,d):
            raise AssertionError((tag,i,x,y,d,q,r,c,eq,er,ec,xo,yo,do))
    return hashlib.sha256(data).hexdigest()

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():raise RuntimeError("VICE_WRAPPER must name native x64sc")
    index=math_builder.operation_index()
    count=0
    with tempfile.TemporaryDirectory(prefix="muldiv16_native_") as td:
        folder=Path(td)
        for map_i,(code,io) in enumerate(((0x8000,0xc000),(0x7123,0xc040))):
            plan=math_builder.create_plan(index,["UMULDIV16","SMULDIV16"],
                    objective="size",zp_budget=0,ram_budget=765)
            man=selective_linker.build(plan,folder,
                memory={"code_base":code,"math_io":io})
            assert man["resource_use"]["image_span_bytes"]==727
            assert man["resource_use"]["private_ram_scratch_bytes"]==6
            ep={o["api"]:int(o["entry"][1:],16) for o in man["operations"]}
            prg=(folder/"math_selective.prg").read_bytes()
            for k,name in enumerate(("UMULDIV16","SMULDIV16")):
                digest=run_native(vice,prg,ep["MATH_"+name],code,io,
                                  name.startswith("S"),
                                  name.lower()+"_%04x"%code,8480+map_i*2+k,folder)
                count+=N
                print("NATIVE",name,hex(code),N,"PASS",digest,flush=True)
    assert count==4*N
    print("NATIVE MULDIV16 2-MAP PASS",count)

if __name__=="__main__":
    main()
