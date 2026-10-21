#!/usr/bin/env python3
"""Physical VICE proof of source-built QS16 table creation and guarded batches."""
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
import reu_qs16_standalone_package as q16

START=0x0800
SNAP=0x1a00
ZP=q16.ZP_MAIN+0x0e
ZP_LENGTH=16
EXAMPLES=((0x1234,0x5678),(0xffff,0xffff))


def harness(exports):
    values={name:int(a[1:],16) for name,a in exports.items()}
    seed=bytes((19+73*i)&255 for i in range(ZP_LENGTH))
    code=[
        "* = $0800","ENTRY:",
        "sei","cld","lda #$35","sta $01",
        "ldx #$00","SEED_LOOP:",
        "lda SEED_DATA,x","sta $%02x,x"%ZP,
        "inx","cpx #$%02x"%ZP_LENGTH,"bne SEED_LOOP",
        "jsr $%04x"%values["Q16_REU_INSTALL"],
        "php","pla","sta $1a00",
        "lda $%04x"%q16.READY,"sta $1a01",
        "bcc GO_BATCHES","jmp SNAPSHOT",
        "GO_BATCHES:",
    ]
    for batch,(x,y) in enumerate(EXAMPLES):
        for ofs in range(2):
            code.extend((
                "lda #$%02x"%((x>>(ofs*8))&255),
                "sta $%04x"%(q16.IO+ofs),
                "lda #$%02x"%((y>>(ofs*8))&255),
                "sta $%04x"%(q16.IO+4+ofs),
            ))
        code+= [
            "jsr $%04x"%values["Q16_REU_BEGIN"],
            "php","pla","sta $%04x"%(SNAP+2+3*batch),
            "jsr $%04x"%values["Q16_REU_CALL"],
            "php","pla","sta $%04x"%(SNAP+3+3*batch),
        ]
        for j in range(4):
            code.extend((
                "lda $%04x"%(q16.IO+8+j),
                "sta $%04x"%(SNAP+0x10+batch*4+j),
            ))
        code +=[
            "jsr $%04x"%values["Q16_REU_END"],
            "php","pla","sta $%04x"%(SNAP+4+3*batch),
        ]
    code +=[
        "SNAPSHOT:","ldx #$00","COPY_ZP:",
        "lda $%02x,x"%ZP,"sta $1a40,x",
        "inx","cpx #$%02x"%ZP_LENGTH,"bne COPY_ZP",
        "HALT:","jmp HALT",
        "SEED_DATA:",
        "!byte "+",".join("$%02x"%a for a in seed),
    ]
    memory,labels,_=Assembler().assemble("\n".join(code)+"\n")
    keys=sorted(memory)
    if keys!=list(range(START,START+len(keys))) or len(keys)>0x500:
        raise RuntimeError("Invalid native QS16 harness placement")
    return bytes(memory[k] for k in keys),labels["HALT"],seed


def command(sock,line,needle):
    sock.sendall((line+"\n").encode())
    data=b""
    for _ in range(300):
        try:
            part=sock.recv(16384)
            if not part:
                break
            data+=part
            if needle.encode() in data and data.endswith(b") "):
                return data
        except socket.timeout:
            continue
    raise RuntimeError(("VICE remote response",line,needle,data[-1500:]))


def native_case(exe,folder,name,installed_reu_kib,port):
    manifest,prg=q16.build()
    test,stop,seed=harness(manifest["public_exports"])
    ram=bytearray(q16.LIMIT-START)
    ram[:len(test)]=test
    ram[q16.BASE-START:q16.LIMIT-START]=prg[2:]
    image=folder/(name+".prg")
    dump=folder/(name+".dump")
    logfile=folder/(name+".log")
    image.write_bytes(bytes((START&255,START>>8))+ram)
    opts=(["-reu","-reusize",str(installed_reu_kib)]
          if installed_reu_kib else ["+reu"])
    args=[str(exe),"-console","-silent","-sounddev","dummy","-warp",
          *opts,"-remotemonitor",
          "-remotemonitoraddress",f"127.0.0.1:{port}",
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
                raise RuntimeError(("Native REU monitor unavailable",name,
                                    logfile.read_text()[-2000:]))
            sock.settimeout(.4)
            try:
                command(sock,'load "'+str(image)+'" 0',"Loading")
                command(sock,"break "+format(stop,"04x"),"BREAK:")
                command(sock,"g "+format(START,"04x"),"Stop on  exec")
                command(sock,'bsave "'+str(dump)+'" 0 1a00 1a4f',"Saving")
                sock.sendall(b"quit\n")
            finally:
                sock.close()
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
    if not dump.exists():
        raise AssertionError(("No native QS16 output",name,logfile.read_text()[-2000:]))
    result=dump.read_bytes()
    assert len(result)==0x50,(name,len(result))
    success=installed_reu_kib==16384
    if success:
        assert result[0]&1==0 and result[1]==1,(name,"install",result[:8])
        for i,(a,b) in enumerate(EXAMPLES):
            assert all(result[2+i*3+j]&1==0 for j in range(3)),(name,"batch",result[:8])
            got=int.from_bytes(result[0x10+i*4:0x14+i*4],"little")
            assert got==a*b,(name,a,b,got)
    else:
        assert result[0]&1 and result[1]==0,(name,"absent/aliased REU accepted",result[:8])
    assert result[0x40:0x40+ZP_LENGTH]==seed,(name,"caller ZP damaged")
    return {
        "test":name,"installed_capacity_kib":installed_reu_kib,
        "intended_capacity_kib":16384,
        "full_table_generated_by_reu_dma":success,
        "two_batches_passed":success,
        "hardware_or_alias_rejected":not success,
        "caller_zero_page_exactly_restored":True,
        "native_dma_cycle_timing_measured":False,
        "snapshot_sha256":hashlib.sha256(result).hexdigest(),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    exe=os.environ.get("VICE_WRAPPER")
    if not exe or not Path(exe).is_file():
        raise RuntimeError("Pinned VICE_WRAPPER x64sc required")
    cases=(("no_reu",0),("512k_reject",512),
           ("8m_mirror_reject",8192),("16m",16384))
    with tempfile.TemporaryDirectory(prefix="qs16_native_") as td:
        folder=Path(td)
        results=[native_case(exe,folder,name,kib,9850+i)
                 for i,(name,kib) in enumerate(cases)]
    report={
        "schema":"source-built-native-qs16-table-generator-preflight-v1",
        "status":"PASS_NATIVE_VICE_4_CASES",
        "native_reu_hardware_behaviour_tested":True,
        "qualified_under_live_irq_vic":False,
        "qualified_in_global_operation_first_allocator":False,
        "cases":results,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(report["status"],flush=True)

if __name__=="__main__":
    main()
