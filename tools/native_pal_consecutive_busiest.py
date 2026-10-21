#!/usr/bin/env python3
"""24 consecutively scheduled PAL frame-8 bursts with native raster IRQ + SID writes.

Runs 24 repeats of the *same original 24-call busiest synthetic frame* in
ONE pinned x64sc process, not independent emulator startups. Raster-zero
barriers, a continuous 32-bit cascaded CIA timer and a live raster IRQ
produce cumulative PAL deadline and skipped-frame evidence. Every repeated
public-output/carry byte is checked in 6510 code, not just the last frame.

This is intentionally a synthetic frame-8 stress loop, NOT the diverse
24-frame application trace, a real SID player, sprites, REU or demo proof.
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

import frame_evidence_replay
import mixed_seven_d65536_frame as source
import native_installed_d65536_pal as installed
import native_pal_irq_sid_burst as irq
import native_pal_vic_cia_probe as cia

RUNS=24
FRAME=8
PLANS=installed.CHOICES
CODE=installed.CODE
MAIN=cia.HARNESS
HANDLER=irq.IRQ
SUB=0x8000
DATA=0x3c00
EXPECT=0x3d00
FRAME_COUNTER=0x3a02
ERROR_COUNTER=0x3a03
OUTPUT=cia.RESULT+6
PAL=cia.PAL_SLOTS
assert PAL==19656 and HANDLER==0x7e00 and MAIN==0x7000

def word(value):
    if type(value) is not int or not 0<=value<65536:
        raise ValueError("Unqualified 6510 absolute address")
    return bytes((value&255,value>>8))

def one_instruction_store(addr,value):
    return bytes((0xa9,value&255,0x8d))+word(addr)

def build_harness(entries, *, display):
    """Return exact linked math body, 24-frame caller and complete expected bytes."""
    if type(display) is not bool or set(entries)!=set(source.OPS):
        raise ValueError("Expected seven public installer exports and display boolean")
    base,_,expected,count=irq.irq_harness(
        entries,frame=FRAME,display=display,irq_enabled=True,raster_line=90)
    assert count==24 and len(expected)==48
    first=base.find(irq.SYNCH)
    start=base.find(irq.START,first)
    stop=base.rfind(bytes((0xa9,0,0x8d,0x0e,0xdc)))
    reset=irq.store(irq.IRQ_COUNT,0)+irq.store(irq.IRQ_AUX,0)
    if (first<0 or start<first or stop<start+10 or
            base[first:start][-len(reset):]!=reset or
            base[start:start+10]!=irq.START+bytes((0xa9,0x11,0x8d,0x0e,0xdc))):
        raise AssertionError("Original native raster/CIA/public-call harness moved")
    prefix=base[:first]
    barrier=base[first:start-len(reset)]
    math=base[start+10:stop]+b'\x60'  # identical 24 public loads/JSRs, then RTS
    if not math or SUB+len(math)>=0xc000:
        raise AssertionError("Busiest source call program would collide with I/O")
    b=bytearray(prefix)
    def emit(raw): b.extend(raw)
    for i,expect in enumerate(expected):
        emit(one_instruction_store(EXPECT+i,expect))
    emit(one_instruction_store(FRAME_COUNTER,0))
    emit(one_instruction_store(ERROR_COUNTER,0))
    loop_start=MAIN+len(b)
    emit(barrier)
    # Start the 32-bit CIA only on the first successfully synchronised frame.
    emit(bytes((0xad,))+word(FRAME_COUNTER))  # LDA frame count
    emit((0xd0,len(reset)+10))               # BNE skip reset and CIA start
    emit(reset)
    emit(base[start:start+10])               # CIA Timer B + A force-load and start
    emit(bytes((0x20,))+word(SUB))           # JSR same original 24-call body
    # Per-frame exact expected-output/carry check (48 actual bytes).
    emit((0xa2,0))                           # LDX #0
    verify_loop=MAIN+len(b)
    emit(bytes((0xbd,))+word(OUTPUT))        # LDA live RESULT+6,X
    emit(bytes((0xdd,))+word(EXPECT))        # CMP expected,X
    emit((0xf0,3))                           # BEQ +3
    emit(bytes((0xee,))+word(ERROR_COUNTER)) # INC error counter
    emit((0xe8,0xe0,len(expected)))          # INX; CPX #48
    next_pc=MAIN+len(b)+2
    back=verify_loop-next_pc
    if not -128<=back<=127:
        raise AssertionError("Output oracle loop branch range")
    emit((0xd0,back&255))                    # BNE verify_loop
    # Capture running (never reset/reloaded) cascaded 32-bit CIA timer at
    # completion of every PAL frame into 24 4-byte samples.
    emit(bytes((0xad,))+word(FRAME_COUNTER))
    emit((0x0a,0x0a,0xaa))                  # ASL; ASL; TAX (record offset 4*i)
    for i,reg in enumerate((0xdc04,0xdc05,0xdc06,0xdc07)):
        emit(bytes((0xad,))+word(reg))
        emit(bytes((0x9d,))+word(DATA+i))   # STA DATA+i,X
    emit(bytes((0xee,))+word(FRAME_COUNTER))
    emit(bytes((0xad,))+word(FRAME_COUNTER))
    emit((0xc9,RUNS))
    end_pc=MAIN+len(b)+2
    step=loop_start-end_pc
    if not -128<=step<=127:
        raise AssertionError("PAL raster barrier loop exceeds relative branch range")
    emit((0xd0,step&255))                    # BNE next raster period
    emit((0x78,))                           # SEI
    emit(one_instruction_store(0xd01a,0))  # mask VIC raster IRQ
    emit(one_instruction_store(0xdc0e,0))  # halt timers
    emit(one_instruction_store(0xdc0f,0))
    halt=MAIN+len(b)
    emit(bytes((0x4c,))+word(halt))
    if MAIN+len(b)>HANDLER:
        raise AssertionError("Main loop and real raster IRQ source collide")
    b.extend(b'\xea'*(HANDLER-(MAIN+len(b))))
    b.extend(irq.irq_handler())
    if MAIN+len(b)>SUB:
        raise AssertionError("IRQ handler and repeated public-call program collide")
    b.extend(b'\xea'*(SUB-(MAIN+len(b))))
    b.extend(math)
    if SUB+len(math)!=MAIN+len(b) or MAIN+len(b)>=0xc000:
        raise AssertionError("Repeated busy source escaped reserved PAL RAM")
    return bytes(b),halt,expected,{"body_start":SUB,"body_bytes":len(math),
                                   "main_loop":loop_start,"main_halt":halt,
                                   "raster_irq_handler":HANDLER}

def read_monitor(vice, image, entries, folder, tag, port, *, display):
    if not vice or not Path(vice).is_file() or image[:2]!=CODE.to_bytes(2,'little'):
        raise ValueError("Pinned native PAL x64sc and real source-linked PRG required")
    stub,halt,expected,geometry=build_harness(entries,display=display)
    if CODE+len(image)-2>=MAIN:
        raise AssertionError("Native installed math source overlaps PAL loop")
    image_ram=bytearray(65536)
    image_ram[CODE:CODE+len(image)-2]=image[2:]
    image_ram[MAIN:MAIN+len(stub)]=stub
    prg=folder/(tag+".prg")
    prg.write_bytes(CODE.to_bytes(2,'little')+image_ram[CODE:MAIN+len(stub)])
    outputs=folder/(tag+"-outputs.bin")
    counters=folder/(tag+"-timer.bin")
    state=folder/(tag+"-state.bin")
    args=[vice,"-console","-silent","-pal","-sounddev","dummy","-warp",
          "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
          "-initbreak","reset"]
    with (folder/(tag+".log")).open("w") as log:
        proc=subprocess.Popen(args,cwd=folder,stdout=log,stderr=log)
        try:
            for _ in range(200):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.1)
                    break
                except (OSError,TimeoutError):
                    time.sleep(.05)
            else:
                raise RuntimeError("Consecutive PAL probe remote monitor unavailable")
            sock.settimeout(.25)
            def cmd(line,marker):
                sock.sendall((line+"\n").encode())
                output=b''
                for _ in range(200):
                    try:
                        chunk=sock.recv(16384)
                        if not chunk: break
                        output+=chunk
                        if marker.encode() in output and output.endswith(b') '):
                            break
                    except socket.timeout:
                        continue
                if marker.encode() not in output:
                    raise RuntimeError("VICE PAL consecutive command failed "+str((line,output[-900:])))
            cmd('load "'+str(prg)+'" 0','Loading')
            cmd('break '+format(halt,'04x'),'BREAK:')
            cmd('g '+format(MAIN,'04x'),'Stop on  exec')
            cmd('bsave "'+str(outputs)+'" 0 '+format(OUTPUT,'04x')+' '+format(OUTPUT+47,'04x'),'Saving')
            cmd('bsave "'+str(counters)+'" 0 '+format(DATA,'04x')+' '+format(DATA+RUNS*4-1,'04x'),'Saving')
            cmd('bsave "'+str(state)+'" 0 3a00 3a03','Saving')
            sock.sendall(b'quit\n')
            sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
    actual=outputs.read_bytes()
    count_data=counters.read_bytes()
    summary=state.read_bytes()
    if actual!=expected or len(count_data)!=RUNS*4 or len(summary)!=4:
        raise AssertionError(("Native repeated math public-output/carry failure",tag,
                              actual.hex(),expected.hex(),len(count_data),len(summary)))
    irq_count,_,count,errors=summary
    if count!=RUNS or errors!=0:
        raise AssertionError(("Native repeated public oracle/frame count failed",
                              tag,count,errors,irq_count))
    if irq_count!=RUNS:
        raise AssertionError(("Consecutive PAL raster IRQ count not one/frame",tag,irq_count))
    elapsed=[cia.decode_elapsed(count_data[i*4:i*4+4]) for i in range(RUNS)]
    if any(a<=0 or a>=2_000_000 for a in elapsed) or any(
        elapsed[i]<=elapsed[i-1] for i in range(1,RUNS)):
        raise AssertionError("Continuous native CIA elapsed samples did not advance")
    records=[{
        "repeat_index":i,"cumulative_elapsed_slots":x,
        "nominal_deadline_slots":(i+1)*PAL,
        "deadline_margin_slots":(i+1)*PAL-x,
        "nominal_deadline_missed":x>(i+1)*PAL,
        "elapsed_since_prior_math_finish_slots":x-(elapsed[i-1] if i else 0),
    } for i,x in enumerate(elapsed)]
    return {
        "display_enabled":display,"source_linked_calls_per_frame":24,
        "total_public_calls":RUNS*24,
        "source_frame":FRAME,"raster_irq_count":irq_count,
        "frame_count":count,"public_output_error_count":errors,
        "public_output_sha256":hashlib.sha256(actual).hexdigest(),
        "source_frame_inputs_sha256":hashlib.sha256(
            json.dumps([x[-1] for x in cia.busiest_calls(FRAME)],
                       separators=(",",":")).encode()).hexdigest(),
        "qualified_prg_sha256":hashlib.sha256(image).hexdigest(),
        "peak_cumulative_deadline_lateness_slots":max(
            0,max(-r["deadline_margin_slots"] for r in records)),
        "nominal_deadline_misses":sum(r["nominal_deadline_missed"] for r in records),
        "last_completed_elapsed_slots":elapsed[-1],
        "geometry":geometry,"records":records,
    }

def run(vice):
    if not vice or not Path(vice).is_file():
        raise ValueError("Pinned x64sc r46284 is required")
    report=source.complete_report()
    if frame_evidence_replay.replay(report)!=report:
        raise AssertionError("Registered nine-plan source evidence drift")
    rows=[]
    with tempfile.TemporaryDirectory(prefix="continuous_pal_math_") as td:
        root=Path(td)
        for i,plan in enumerate(PLANS):
            folder=root/plan
            image,entries,proof=installed.build_one(plan,report,folder)
            for display in (False,True):
                tag=plan+"_display_"+str(int(display))
                row=read_monitor(
                    vice,image,entries,folder,tag,18800+i*4+int(display),
                    display=display)
                if row["qualified_prg_sha256"]!=proof["linked_prg_sha256"]:
                    raise AssertionError("Installed public source PRG SHA changed")
                row["plan"]=plan
                row["linked_ram_bytes"]=proof["linked_ram_bytes"]
                row["zero_page_bytes"]=proof["zero_page_bytes"]
                rows.append(row)
                print("CONSECUTIVE PAL BUSIEST",plan,display,
                      row["nominal_deadline_misses"],
                      row["last_completed_elapsed_slots"],flush=True)
    output_by_display={x["public_output_sha256"] for x in rows}
    inputs={x["source_frame_inputs_sha256"] for x in rows}
    if len(output_by_display)!=1 or len(inputs)!=1:
        raise AssertionError("Source plan/display changed public-call outputs or inputs")
    return {
        "schema":"native-pal-24-consecutive-frame8-stress-irq-sid-v1",
        "native_emulator":"pinned-x64sc-r46284",
        "source_linked_public_calls":24*RUNS*len(PLANS)*2,
        "consecutive_raster_zero_periods_tested":RUNS,
        "identical_busiest_math_trace_repeated_each_frame":True,
        "varied_original_24_frame_trace_measured":False,
        "full_sid_music_player_measured":False,
        "sprites_or_reu_dma_measured":False,
        "real_application_frame_certified":False,
        "pal_slots_per_frame":PAL,
        "plans":list(PLANS),"rows":rows,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    result=run(os.environ.get("VICE_WRAPPER",""))
    data=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(data,encoding="utf-8")
    else:
        print(data,end="")

if __name__=="__main__":
    main()
