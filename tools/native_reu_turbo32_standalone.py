#!/usr/bin/env python3
"""Exercise a standalone *source-built*, self-uploading Turbo32 PRG in VICE.

Checks physical DMA presence/absence and 512KiB high-bank alias rejection.
Does not establish IRQ/VIC contention safety or DMA cycle performance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time

from mini6502 import Assembler
from reu_turbo32_standalone_package import BASE, LIMIT, ZP, IO, STATE, build

SNAP=0x1a00
START=0x0800
EXAMPLES=((0x12345678,0x98765432),(0xffffffff,0xffffffff))


def compile_harness(exports,stock_entry=None,stock_io=None):
    addr={k:int(v[1:],16) for k,v in exports.items()}
    seed=bytes((i*73+19)&255 for i in range(135))
    code=[
        "* = $0800",
        "NATIVE_START:",
        "sei", "cld", "lda #$35", "sta $01",
        "ldx #$00",
        "NATIVE_INIT_ZP:",
        "lda NATIVE_SEED,x", "sta $0a,x",
        "inx", "cpx #$87", "bne NATIVE_INIT_ZP",
        "jsr $%04x" % addr["T32_REU_INSTALL"],
        "php", "pla", "sta $1a00",
        "lda $%04x" % (STATE+1), "sta $1a01",
        "bcc NATIVE_START_MATH",
        "jmp NATIVE_STOCK" if stock_entry is not None else "jmp NATIVE_SNAPSHOT",
        "NATIVE_START_MATH:"
    ]
    for batch,(x,y) in enumerate(EXAMPLES):
        for shift,index in ((0,0),(8,1),(16,2),(24,3)):
            code += ["lda #$%02x" % (x>>shift&255),
                     "sta $%04x" % (IO+index),
                     "lda #$%02x" % (y>>shift&255),
                     "sta $%04x" % (IO+4+index)]
        code += [
            "jsr $%04x" % addr["T32_REU_BEGIN"],
            "php", "pla", "sta $%04x" % (SNAP+2+batch*3),
            "jsr $%04x" % addr["T32_REU_CALL"],
            "php", "pla", "sta $%04x" % (SNAP+3+batch*3)
        ]
        for i in range(8):
            code += ["lda $%04x" % (IO+8+i),
                     "sta $%04x" % (SNAP+0x10+batch*8+i)]
        code += ["jsr $%04x" % addr["T32_REU_END"],
                 "php", "pla", "sta $%04x" % (SNAP+4+batch*3)]
    if stock_entry is not None:
        if stock_io is None:
            raise AssertionError("Stock public math IO must be explicitly provided")
        x,y=0x2345,0x1321
        code += ["NATIVE_STOCK:"]
        for shift,index in ((0,0),(8,1),(16,2),(24,3)):
            code += ["lda #$%02x" % (x>>shift&255),
                     "sta $%04x" % (stock_io+index),
                     "lda #$%02x" % (y>>shift&255),
                     "sta $%04x" % (stock_io+4+index)]
        code += ["jsr $%04x" % stock_entry,
                 "php","pla","sta $%04x" % (SNAP+0x0A)]
        for j in range(4):
            code += ["lda $%04x" % (stock_io+8+j),
                     "sta $%04x" % (SNAP+0x20+j)]
    code += [
        "NATIVE_SNAPSHOT:",
        "ldx #$00",
        "NATIVE_COPY:",
        "lda $0a,x",
        "sta $1a40,x",
        "inx", "cpx #$87", "bne NATIVE_COPY",
        "NATIVE_STOP:",
        "jmp NATIVE_STOP",
        "NATIVE_SEED:",
        "!byte " + ",".join("$%02x" % x for x in seed)
    ]
    memory,labels,_=Assembler().assemble("\n".join(code)+"\n")
    keys=sorted(memory)
    if keys!=list(range(START,START+len(keys))) or len(keys)>0x500:
        raise AssertionError("Native monitor harness overlap / noncontiguous")
    return bytes(memory[k] for k in keys),labels["NATIVE_STOP"],seed


def command(sock,line,needle):
    sock.sendall((line+"\n").encode())
    data=b""
    for _ in range(180):
        try:
            part=sock.recv(16384)
            if not part:break
            data+=part
            if needle.encode() in data and data.endswith(b") "):
                return data
        except socket.timeout:
            continue
    raise RuntimeError(("VICE remote response",line,needle,data[-1100:]))


def native_case(exe, folder, label, reu_kib, packed_kib, bank, port,
                *, stock_prg=None, stock_entry=None, stock_io=None):
    manifest,prg=build(packed_kib,bank)
    harness,stop,seed=compile_harness(manifest["public_exports"],stock_entry,stock_io)
    if (stock_prg is None) != (stock_entry is None):
        raise AssertionError("Stock PRG and its actual exported entry must be supplied together")
    stock_load = int.from_bytes(stock_prg[:2],"little") if stock_prg is not None else 0
    stock_end = stock_load+len(stock_prg)-2 if stock_prg is not None else LIMIT
    if stock_prg is not None and (stock_load<LIMIT or stock_end>0xD000):
        raise AssertionError("Stock loader image overlaps REU or I/O")
    memory=bytearray(max(LIMIT,stock_end)-START)
    offset=BASE-START
    memory[offset:offset+len(prg)-2]=prg[2:]
    memory[:len(harness)]=harness
    if stock_prg is not None:
        memory[stock_load-START:stock_end-START]=stock_prg[2:]
    image=folder/(label+".prg")
    dump=folder/(label+".dump")
    logfile=folder/(label+".log")
    image.write_bytes(bytes((START & 255,START >> 8))+memory)
    flags=["-reu","-reusize",str(reu_kib)] if reu_kib else ["+reu"]
    args=[str(exe),"-console","-silent","-sounddev","dummy","-warp",
          *flags,"-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
          "-initbreak","reset"]
    with logfile.open("w") as log:
        proc=subprocess.Popen(args,cwd=folder,stdout=log,stderr=log)
        try:
            sock=None
            for _ in range(240):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.25)
                    break
                except (ConnectionRefusedError,TimeoutError):
                    time.sleep(.075)
            if sock is None:
                raise RuntimeError(("Native REU monitor unavailable",label,logfile.read_text()[-1600:]))
            sock.settimeout(.35)
            try:
                command(sock,'load "'+str(image)+'" 0',"Loading")
                command(sock,"break "+format(stop,"04x"),"BREAK:")
                command(sock,"g "+format(START,"04x"),"Stop on  exec")
                command(sock,'bsave "'+str(dump)+'" 0 1a00 1ac6',"Saving")
                sock.sendall(b"quit\n")
            finally:
                sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
    if not dump.exists():
        raise AssertionError(("Missing native REU dump",label,logfile.read_text()[-1500:]))
    result=dump.read_bytes()
    assert len(result)==0xc7,(label,len(result))
    expect_success=(reu_kib==packed_kib)
    if expect_success:
        assert result[0]&1==0 and result[1]==1,(label,"hardware probe",result[:8])
        for i,(x,y) in enumerate(EXAMPLES):
            assert all(result[2+i*3+j]&1==0 for j in range(3)),(label,"lifecycle",result[:9])
            got=int.from_bytes(result[0x10+i*8:0x18+i*8],"little")
            assert got==x*y,(label,i,got,x*y)
    else:
        assert result[0]&1 and result[1]==0,(label,"absent or aliased REU was accepted",result[:8])
    assert result[0x40:0x40+135]==seed,(label,"caller ZP was corrupted")
    if stock_prg is not None:
        product=int.from_bytes(result[0x20:0x24],"little")
        assert product==0x2345*0x1321,(label,"stock fallback/coexistence failed",product)
        assert result[0x0A]&1==0,(label,"stock UMUL16 returned carry",result[0x0A])
    return {
        "test":label,"vice_native_dma_registers_exercised":True,
        "actual_vice_reu_kib":reu_kib,"package_declared_reu_kib":packed_kib,
        "installed_bank":bank,"rejected_safely":not expect_success,
        "two_batches_passed":expect_success,
        "caller_zp_exact_restoration":True,
        "stock_fallback_correct_with_or_without_reu":stock_prg is not None,
        "output_sha256":hashlib.sha256(result).hexdigest(),
        "native_dma_cycle_timing_measured":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    exe=os.environ.get("VICE_WRAPPER")
    if not exe or not Path(exe).is_file():
        raise RuntimeError("Native pinned VICE_WRAPPER x64sc required")
    cases=(( "no_reu",0,512,4),
           ( "512k",512,512,4),
           ( "16m",16384,16384,200),
           ( "512k_alias_reject_16m",512,16384,200),
           ( "1m_alias_reject_16m",1024,16384,200),
           ( "8m_alias_reject_16m",8192,16384,200))
    with tempfile.TemporaryDirectory(prefix="turbo32_native_reu_") as temp:
        folder=Path(temp)
        rows=[native_case(exe,folder,name,installed,declared,bank,9550+i)
              for i,(name,installed,declared,bank) in enumerate(cases)]
    result={
        "schema":"native-source-built-turbo32-reu-dma-preflight-v1",
        "status":"PASS_NATIVE_VICE_6_DMA_CASES",
        "native_vice_hardware_behaviour_tested":True,
        "native_cycle_timing_measured":False,
        "irq_vic_coexistence_qualified":False,
        "operation_first_global_linker_integration_complete":False,
        "cases":rows,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["status"],flush=True)

if __name__=="__main__":
    main()
