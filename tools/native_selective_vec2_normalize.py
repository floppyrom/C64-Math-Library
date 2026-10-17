#!/usr/bin/env python3
"""Native x64sc VEC2 normalized Q8.8 -> Q1.15 certified stock-source parity."""
from __future__ import annotations
import hashlib
import json
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
from normalize_model import normalized_reference

H=0x2000
INPUT=0x3000
OUTPUT=0x3800
STRIDE=0x80
N=96
DESIGN=json.loads((ROOT/"validation/normalize/LOG_RATIO_TABLE_DESIGN.json").read_text())

def vectors():
    edges=(-32768,-32767,-255,-2,-1,0,1,2,127,128,255,256,32767)
    v=[(x,y) for x in edges for y in (0,1,-1,32767,-32768)]
    rng=random.Random(0x16bece)
    v.extend((rng.randrange(-32768,32768),rng.randrange(-32768,32768))
             for _ in range(N-len(v)))
    return v

def harness(entry,io):
    out=bytearray()
    def emit(*b):out.extend(b)
    def op(code,addr):emit(code,addr&255,addr>>8)
    emit(0x78,0xd8,0xa9,0x34,0x85,0x01,0xa2,0)
    loop=H+len(out)
    inputs=[io,io+1,io+4,io+5]
    for col,addr in enumerate(inputs):
        op(0xbd,INPUT+col*STRIDE);op(0x8d,addr)
    emit(0x8a,0x48);op(0x20,entry)
    emit(0x08,0x68);op(0x8d,0xc030)
    emit(0x68,0xaa)
    fields=[io+8,io+9,io+10,io+11]+inputs+[0xc030]
    for col,addr in enumerate(fields):
        op(0xad,addr);op(0x9d,OUTPUT+col*STRIDE)
    emit(0xe8,0xe0,N,0xf0,0x03);op(0x4c,loop)
    halt=H+len(out);op(0x4c,halt)
    return bytes(out),halt

def run(vice,prg,entry,code,io,tag,port,folder):
    mem=bytearray(65536)
    mem[code:code+len(prg)-2]=prg[2:]
    stub,halt=harness(entry,io)
    mem[H:H+len(stub)]=stub
    pairs=vectors()
    for i,(x,y) in enumerate(pairs):
        b=(*(x&65535).to_bytes(2,"little"),*(y&65535).to_bytes(2,"little"))
        for col,by in enumerate(b):mem[INPUT+col*STRIDE+i]=by
    source=folder/(tag+".prg")
    out=folder/(tag+".bin")
    source.write_bytes(bytes((H&255,H>>8))+mem[H:0xc200])
    cmd=[vice,"-console","-silent","-sounddev","dummy","-warp",
         "-remotemonitor","-remotemonitoraddress","127.0.0.1:"+str(port),
         "-initbreak","reset"]
    with (folder/(tag+".log")).open("w") as log:
        process=subprocess.Popen(cmd,cwd=folder,stdout=log,stderr=log)
        try:
            for _ in range(150):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.1)
                    break
                except (ConnectionRefusedError,TimeoutError):
                    time.sleep(.04)
            else:raise RuntimeError("Native VICE monitor timeout")
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
                    except socket.timeout:continue
                if needle.encode() not in data:raise RuntimeError((line,data[-500:]))
            command('load "'+str(source)+'" 0',"Loading")
            command("break "+format(halt,"04x"),"BREAK:")
            command("g "+format(H,"04x"),"Stop on  exec")
            command('bsave "'+str(out)+'" 0 '+format(OUTPUT,"04x")+
                    " "+format(OUTPUT+9*STRIDE-1,"04x"),"Saving")
            sock.sendall(b"quit\n");sock.close()
        finally:
            process.terminate()
            try:process.wait(timeout=3)
            except subprocess.TimeoutExpired:process.kill()
    data=out.read_bytes()
    assert len(data)==9*STRIDE
    for i,(x,y) in enumerate(pairs):
        b=bytes(data[col*STRIDE+i] for col in range(9))
        got=(int.from_bytes(b[:2],"little",signed=True),
             int.from_bytes(b[2:4],"little",signed=True))
        original=(int.from_bytes(b[4:6],"little",signed=True),
                  int.from_bytes(b[6:8],"little",signed=True))
        carry=b[8]&1
        want=normalized_reference(x,y,DESIGN)
        if got!=want or original!=(x,y) or carry!=int(not(x or y)):
            raise AssertionError((tag,i,x,y,got,want,original,carry))
    return hashlib.sha256(data).hexdigest()

def main():
    vice=os.environ.get("VICE_WRAPPER","")
    if not Path(vice).is_file():raise RuntimeError("VICE_WRAPPER must name native x64sc")
    index=math_builder.operation_index()
    with tempfile.TemporaryDirectory(prefix="vec2_native_") as td:
        folder=Path(td)
        for i,(code,io,zp) in enumerate(((0x8000,0xc000,0x50),
                                         (0x7123,0xc040,0x72))):
            plan=math_builder.create_plan(index,["VEC2_NORMALIZE_Q8_8"],
                                          zp_budget=4,ram_budget=4000)
            man=selective_linker.build(plan,folder,
                memory={"code_base":code,"math_io":io,"zp_base":zp})
            assert man["resource_use"]["zero_page_bytes"]==4
            entry=int(man["operations"][0]["entry"][1:],16)
            prg=(folder/"math_selective.prg").read_bytes()
            digest=run(vice,prg,entry,code,io,"vec2_%04x"%code,
                       8620+i,folder)
            print("NATIVE VEC2",hex(code),N,"PASS",digest,flush=True)
    print("NATIVE VEC2 2-MAP PASS",2*N)

if __name__=="__main__":
    main()
