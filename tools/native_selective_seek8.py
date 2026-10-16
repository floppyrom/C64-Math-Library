#!/usr/bin/env python3
"""Native x64sc smoke of four exported SEEK8 entries at two RAM relocations."""
from __future__ import annotations
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
import math_builder
import selective_linker

H=0x2000
RESULT=0xc300
FAMILY=("MATH_SEEK8_INIT","MATH_SEEK8_STEP","MATH_SEEK8_STEP_INT","MATH_SEEK8_STEP1")


def harness(entries, io, state):
    buf=bytearray()
    def emit(*v): buf.extend(v)
    def absop(opcode,address):emit(opcode,address&255,address>>8)
    emit(0x78,0xd8,0xa9,0x34,0x85,0x01) # SEI, CLD, map RAM at $C000
    emit(0xa2,0x03) # select sprite slot 3
    for address,value in ((state+3,4),(state+11,4),(io,8),(io+4,4),
                          (io+16,0),(io+17,1)):
        emit(0xa9,value);absop(0x8d,address)
    absop(0x20,entries["MATH_SEEK8_INIT"])
    emit(0x08,0x68);absop(0x8d,RESULT+0) # INIT C should clear
    for step in ("MATH_SEEK8_STEP1",)*6:
        absop(0x20,entries[step])
    emit(0x08,0x68);absop(0x8d,RESULT+1) # STEP C should be set
    absop(0xad,state+3);absop(0x8d,RESULT+2)
    absop(0xad,state+11);absop(0x8d,RESULT+3)
    emit(0x8a);absop(0x8d,RESULT+4)
    absop(0xad,io);absop(0x8d,RESULT+5)
    absop(0xad,io+4);absop(0x8d,RESULT+6)
    absop(0xad,io+17);absop(0x8d,RESULT+7)
    halt=H+len(buf)
    absop(0x4c,halt)
    return bytes(buf),halt


def verify_native(vice,blob,entrymap,code,io,state,folder,port):
    memory=bytearray(65536)
    memory[code:code+len(blob)-2]=blob[2:]
    stub,halt=harness(entrymap,io,state)
    memory[H:H+len(stub)]=stub
    path=folder/("seek8_native_%04x.prg"%code)
    dest=folder/("seek8_native_%04x.bin"%code)
    path.write_bytes(bytes((0,0x20))+memory[H:0xc400])
    args=[vice,"-console","-silent","-sounddev","dummy","-warp",
          "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
          "-initbreak","reset"]
    with (folder/("seek8_native_%04x.log"%code)).open("w") as log:
        proc=subprocess.Popen(args,cwd=folder,stdout=log,stderr=log)
        try:
            for _ in range(150):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.1)
                    break
                except (ConnectionRefusedError,TimeoutError):
                    time.sleep(.04)
            else:
                raise RuntimeError("VICE monitor connection failed")
            sock.settimeout(.25)
            def command(line,word):
                sock.sendall((line+"\n").encode())
                data=b""
                for _ in range(180):
                    try:
                        chunk=sock.recv(16384)
                        if not chunk: break
                        data+=chunk
                        if word.encode() in data and data.endswith(b") "): break
                    except socket.timeout: continue
                if word.encode() not in data:
                    raise RuntimeError(f"VICE command {line}: {data[-500:]!r}")
            command(f'load "{path}" 0',"Loading")
            command(f"break {halt:04x}","BREAK:")
            command(f"g {H:04x}","Stop on  exec")
            command(f'bsave "{dest}" 0 {RESULT:04x} {RESULT+7:04x}',"Saving")
            sock.sendall(b"quit\n")
            sock.close()
        finally:
            proc.terminate()
            try: proc.wait(timeout=3)
            except subprocess.TimeoutExpired: proc.kill()
    result=dest.read_bytes()
    assert len(result)==8,(len(result),result)
    assert result[0]&1==0 and result[1]&1==1,result
    assert tuple(result[2:])==(8,4,3,8,4,1),result
    return result.hex()


def main():
    vice=os.environ.get("VICE_WRAPPER")
    if not vice or not Path(vice).is_file():
        raise RuntimeError("VICE_WRAPPER must name x64sc")
    index=math_builder.operation_index()
    with tempfile.TemporaryDirectory(prefix="native_seek8_") as d:
        folder=Path(d)
        for i,(code,io,sb) in enumerate(((0x8000,0xc000,0xc020),
                                         (0x7123,0xc100,0xc121))):
            plan=math_builder.create_plan(index,list(FAMILY),ram_budget=867,zp_budget=0)
            manifest=selective_linker.build(plan,folder,memory={
                "code_base":code,"math_io":io,"scratch_base":sb})
            names={item["api"]:int(item["entry"][1:],16)
                   for item in manifest["operations"]}
            state=int(manifest["memory_map"]["persistent_state"]["seek8"][1:],16)
            data=(folder/"math_selective.prg").read_bytes()
            digest=verify_native(vice,data,names,code,io,state,folder,7540+i)
            print(f"NATIVE SEEK8 {code:04x}: PASS {digest}",flush=True)
    print("NATIVE SEEK8 two relocations PASS",flush=True)


if __name__=="__main__":
    main()
