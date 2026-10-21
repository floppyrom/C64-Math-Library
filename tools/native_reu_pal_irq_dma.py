#!/usr/bin/env python3
"""Experimental physical REU native PAL CIA wall-clock + VIC/IRQ/SID probe.

Full operation-first two-PRG installation, repeated guarded Turbo16 calls,
then intact stock UMUL16 fallback. Matched VIC screen enabled/disabled and
raster IRQ enabled/disabled controls. The IRQ writes real SID registers and
is deliberately zero-page neutral. This is a bounded stress probe, NOT a
live music player, 50Hz scheduler guarantee, or real-hardware certificate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import tempfile
import time

import configure_math as setup
import math_builder as builder
from mini6502 import Assembler
from reu_turbo16_standalone_package import BASE, LIMIT, IO, ZP, STATE

HARNESS = 0x0800
IRQ = 0x1000
NMI_GUARD = 0x1100
SNAP = 0x1a00
COUNT = 24
A, B = 0x1234, 0x5678
STOCK_A, STOCK_B = 0x2345, 0x1321
PAL_SLOTS = 312*63


def assemble(exports, stock_entry, stock_io, *, display, irq):
    addr = {n:int(v[1:],16) for n,v in exports.items()}
    seed = bytes((i*73+19)&255 for i in range(122))
    if stock_io != 0xc040:
        raise ValueError("This reference timing probe expects source-linked stock IO $C040")
    code = [
        "* = $0800",
        "PAL_INIT:",
        "sei","cld","lda #$35","sta $01",
        "lda #$7f","sta $dc0d","sta $dd0d",
        "lda #$00","sta $dc0e","sta $dc0f","sta $d01a",
        "lda #$%02x"%(0x1b if display else 0x0b),"sta $d011",
        "lda #$08","sta $d016","lda #$14","sta $d018",
        "ldx #$00",
        "PAL_SEED_ZP:",
        "lda PAL_SEED,x","sta $3e,x","inx","cpx #$7a","bne PAL_SEED_ZP",
        "jsr $%04x"%addr["T16_REU_INSTALL"],
        "php","pla","sta $%04x"%(SNAP+0),
        "lda $%04x"%(STATE+1),"sta $%04x"%(SNAP+1),
        "bcc PAL_INSTALLED","jmp PAL_HALT",
        "PAL_INSTALLED:",
        "lda #$%02x"%(IRQ&255),"sta $fffe",
        "lda #$%02x"%(IRQ>>8),"sta $ffff",
        "lda #$%02x"%(NMI_GUARD&255),"sta $fffa",
        "lda #$%02x"%(NMI_GUARD>>8),"sta $fffb",
        "lda #$73","sta $%04x"%(SNAP+0x31),
        # Early diagnostic NMI covers armed IRQ *and raster sync*, not
        # merely the math batch. Max one normal PAL frame to sync.
        "lda #$7f","sta $dd0d",
        "lda #$60","sta $dd04",
        "lda #$ea","sta $dd05",
        "lda #$81","sta $dd0d",
        "lda #$11","sta $dd0e",
        "lda #$17","sta $d012",
        "lda #$01","sta $d019",
        "lda #$%02x"%(1 if irq else 0),"sta $d01a",
        "lda $dc0d","lda $dd0d",
        "PAL_SYNC_HI:","bit $d011","bpl PAL_SYNC_HI",
        "PAL_SYNC_LO:","bit $d011","bmi PAL_SYNC_LO",
        "lda #$74","sta $%04x"%(SNAP+0x31),
        "lda #$00","sta $%04x"%(SNAP+6),"sta $%04x"%(SNAP+7),
        "cli",
        "lda #$ff","sta $dc04","sta $dc05","sta $dc06","sta $dc07"
    ]
    for shift,i in ((0,0),(8,1)):
        code += [
            "lda #$%02x"%((A>>shift)&255),"sta $%04x"%(IO+i),
            "lda #$%02x"%((B>>shift)&255),"sta $%04x"%(IO+4+i),
        ]
    code += [
        "lda #$%02x"%COUNT,"sta $%04x"%(SNAP+0x30),
        # Diagnostic fail-closed CIA2 NMI after 18,000 PHI2 clocks.
        # A normal measured batch ends in ~6,000-7,000 clocks, before it.
        "lda #$50","sta $dd04",
        "lda #$46","sta $dd05",
        "lda #$81","sta $dd0d",
        "lda #$11","sta $dd0e",
        "lda #$51","sta $dc0f",
        "lda #$11","sta $dc0e",
        "lda #$b0","sta $%04x"%(SNAP+0x31),
        "jsr $%04x"%addr["T16_REU_BEGIN"],
        "lda #$b1","sta $%04x"%(SNAP+0x31),
        "php","pla","sta $%04x"%(SNAP+2),
        "PAL_REPEAT:",
        "lda #$b2","sta $%04x"%(SNAP+0x31),
        "jsr $%04x"%addr["T16_REU_CALL"],
        "dec $%04x"%(SNAP+0x30),
        "bne PAL_REPEAT",
        "php","pla","sta $%04x"%(SNAP+3)
    ]
    for i in range(4):
        code += ["lda $%04x"%(IO+8+i),"sta $%04x"%(SNAP+0x10+i)]
    code += [
        "lda #$b3","sta $%04x"%(SNAP+0x31),
        "jsr $%04x"%addr["T16_REU_END"],
        "php","pla","sta $%04x"%(SNAP+4),
        "lda #$00","sta $dd0e","sta $dc0e","sta $dc0f",
        "lda #$7f","sta $dd0d",
    ]
    for j,p in enumerate((0xdc04,0xdc05,0xdc06,0xdc07)):
        code += ["lda $%04x"%p,"sta $%04x"%(SNAP+8+j)]
    code += [
        "sei","lda #$00","sta $d01a",
        "lda #$01","sta $d019",
    ]
    for shift,i in ((0,0),(8,1)):
        code += [
            "lda #$%02x"%((STOCK_A>>shift)&255),"sta $%04x"%(stock_io+i),
            "lda #$%02x"%((STOCK_B>>shift)&255),"sta $%04x"%(stock_io+4+i)
        ]
    code += ["jsr $%04x"%stock_entry,
             "php","pla","sta $%04x"%(SNAP+5)]
    for i in range(4):
        code += ["lda $%04x"%(stock_io+8+i),"sta $%04x"%(SNAP+0x20+i)]
    code += [
        "ldx #$00",
        "PAL_COPY_ZP:",
        "lda $3e,x","sta $1a40,x",
        "inx","cpx #$7a","bne PAL_COPY_ZP",
        "PAL_HALT:",
        "jmp PAL_HALT",
        "PAL_SEED:",
        "!byte "+",".join("$%02x"%v for v in seed),
        "* = $1000",
        "PAL_IRQ:",
        "pha","txa","pha","tya","pha",
        "lda #$01","sta $d019",
        "inc $%04x"%(SNAP+6),
        # Diagnostic-only watchdog: repeated unacknowledged VIC IRQs
        # must produce a snapshot instead of hanging the CI monitor.
        "lda $%04x"%(SNAP+6),
        "cmp #$05","bne PAL_IRQ_NORMAL",
        "lda #$ee","sta $%04x"%(SNAP+7),
        "ldx #$fd","txs","jmp PAL_HALT",
        "PAL_IRQ_NORMAL:",
        "lda $%04x"%(SNAP+6),"sta $d400",
        "lda #$11","sta $d404",
        "lda #$0f","sta $d418",
        "pla","tay","pla","tax","pla","rti",
        "* = $1100",
        "PAL_NMI_GUARD:",
        # A timer NMI only means the test failed to reach END in time.
        # It is not permitted to turn a hung REU/IRQ run into a pass.
        "lda $dd0d",
        "lda #$dd","sta $%04x"%(SNAP+7),
        "ldx #$fd","txs","jmp PAL_HALT",
    ]
    memory,symbols,_=Assembler().assemble("\n".join(code)+"\n")
    if symbols["PAL_HALT"]>=IRQ or any(
        p not in range(HARNESS,IRQ) and
        p not in range(IRQ,IRQ+0x100) and
        p not in range(NMI_GUARD,NMI_GUARD+0x100)
        for p in memory):
        raise AssertionError("Native PAL probe escaped segregated CPU/IRQ allocations")
    if symbols["PAL_HALT"]-HARNESS>0x600 or IRQ not in memory or NMI_GUARD not in memory:
        raise AssertionError("Native PAL program too large or missing handler")
    return memory,symbols["PAL_HALT"],seed


def elapsed(raw):
    return (0xffff-int.from_bytes(raw[2:4],"little"))*65536+(
        0xffff-int.from_bytes(raw[0:2],"little"))


def monitor(sock, line, needle):
    sock.sendall((line+"\n").encode())
    data=b""
    for _ in range(180):
        try:
            block=sock.recv(16384)
            if not block:break
            data+=block
            if needle.encode() in data and data.endswith(b") "):
                return data
        except socket.timeout:
            continue
    raise RuntimeError(("Native PAL REU VICE monitor failed",line,data[-1200:]))


def native_case(exe, work, tag, tier, bank, display, irq, port, *, trace_irq=False,
                monitor_start="register-go"):
    work.mkdir()
    conf={
        "target":"c64","operations":["UMUL16"],"objective":"size",
        "constraints":{"max_zp_bytes":200,"max_ram_bytes":25000},
        "hardware":{"reu":{"turbo16":{
            "capacity_kib":tier,"bank":bank,"reserved_banks":[]}}},
    }
    stock=setup.build_checked(conf,builder.operation_index(),work)
    report=json.loads((work/"math_project_manifest.json").read_text())
    reuman=json.loads((work/"turbo16_reu_manifest.json").read_text())
    m=re.search(r"^MATH_UMUL16\s*=\s*\$([0-9a-fA-F]+)\s*$",
                (work/"math_api.inc").read_text(),re.M)
    if not m or not report["physical_memory_bound_by_stock_linker"]:
        raise AssertionError("Missing stock ABI or global resource ownership")
    stock_io=int(stock["memory_map"]["math_io_start"][1:],16)
    stub,stop,seed=assemble(reuman["public_exports"],int(m.group(1),16),
                            stock_io,display=display,irq=irq)
    stock_prg=(work/"math_selective.prg").read_bytes()
    reu_prg=(work/"turbo16_reu.prg").read_bytes()
    base=int.from_bytes(stock_prg[:2],"little")
    end=base+len(stock_prg)-2
    if not LIMIT<=base<end<=0xd000:
        raise AssertionError("Physical source-linked stock placement violates REU footprint")
    machine=bytearray(end-HARNESS)
    machine[BASE-HARNESS:LIMIT-HARNESS]=reu_prg[2:]
    machine[base-HARNESS:end-HARNESS]=stock_prg[2:]
    for k,v in stub.items():machine[k-HARNESS]=v
    image=work/(tag+".prg")
    dumped=work/(tag+".dump")
    logfile=work/(tag+".log")
    image.write_bytes(bytes((HARNESS&255,HARNESS>>8))+machine)
    cmd=[str(exe),"-console","-silent","-pal","-sounddev","dummy","-warp",
         "-reu","-reusize",str(tier),
         "-remotemonitor","-remotemonitoraddress",f"127.0.0.1:{port}",
         "-initbreak","reset"]
    with logfile.open("w") as log:
        proc=subprocess.Popen(cmd,cwd=work,stdout=log,stderr=log)
        try:
            sock=None
            for _ in range(240):
                try:
                    sock=socket.create_connection(("127.0.0.1",port),timeout=.25)
                    break
                except (TimeoutError,ConnectionRefusedError):
                    time.sleep(.075)
            if sock is None:
                raise RuntimeError("Native PAL REU VICE remote monitor unavailable")
            sock.settimeout(.35)
            try:
                try:
                    monitor(sock,'load "'+str(image)+'" 0',"Loading")
                    monitor(sock,"break "+format(stop,"04x"),"BREAK:")
                    if trace_irq:
                        monitor(sock,"break "+format(IRQ,"04x"),"BREAK:")
                    if monitor_start == "register-go":
                        # Avoid address-bearing 'g xxxx', which has documented
                        # monitor/interrupt timing hazards in older VICE builds.
                        monitor(sock,"r pc="+format(HARNESS,"04x"),"")
                        regs=monitor(sock,"r","")
                        if format(HARNESS,"04x").encode() not in regs.lower():
                            raise RuntimeError(("VICE register-go PC readback mismatch",
                                                regs[-1000:]))
                        hit=monitor(sock,"g","Stop on  exec")
                    elif monitor_start == "goto":
                        hit=monitor(sock,"g "+format(HARNESS,"04x"),"Stop on  exec")
                    else:
                        raise AssertionError("Unqualified remote monitor start mode")
                    if trace_irq:
                        monitor(sock,'bsave "'+str(dumped)+'" 0 1a00 1ab9',"Saving")
                        snap=dumped.read_bytes()
                        if snap[7]==0xdd:
                            raise AssertionError(("NMI watchdog fired before IRQ breakpoint",
                                                  "last_stage",snap[0x31],
                                                  "irq_count",snap[6]))
                        print("TRACE_NATIVE_IRQ_BREAKPOINT",tag,
                              hit[-1000:].decode(errors="replace"),flush=True)
                        sock.sendall(b"quit\n")
                        return {"case":tag,"status":"IRQ_ENTRY_MONITOR_TRACE_ONLY",
                                "trace_monitor_output":hit[-1000:].decode(errors="replace"),
                                "stage_marker":snap[0x31],
                                "full_batch_qualified":False}
                    monitor(sock,'bsave "'+str(dumped)+'" 0 1a00 1ab9',"Saving")
                    sock.sendall(b"quit\n")
                except Exception as exc:
                    log.flush()
                    reason={
                        "case":tag,
                        "monitor_start":monitor_start,
                        "original_monitor_failure":str(exc),
                        "vice_process_returncode":proc.poll(),
                        "vice_log_tail":logfile.read_text(errors="replace")[-7500:],
                        "image_bytes":len(machine),
                        "irq_vector":format(IRQ,"04x"),
                        "stop_address":format(stop,"04x"),
                        "source_prg_stock":report["stock_prg_sha256"],
                        "source_prg_reu":report["reu_prg_sha256"],
                    }
                    raise RuntimeError("Native REU PAL monitor diagnostic: "+
                                       json.dumps(reason,sort_keys=True)) from exc
            finally:sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
    if not dumped.is_file():
        raise AssertionError((tag,"missing VICE dump",logfile.read_text(errors="replace")[-1500:]))
    snapshot=dumped.read_bytes()
    if len(snapshot)!=0xba:
        raise AssertionError((tag,"snapshot wrong size",len(snapshot)))
    if snapshot[7]==0xdd:
        raise AssertionError((tag,"CIA2 NMI fail-closed: bounded physical REU IRQ batch failed",
                              "calls_remaining",snapshot[0x30],
                              "last_math_stage",snapshot[0x31],
                              "irq_entries",snapshot[6],"flags",snapshot[:12].hex()))
    if snapshot[7]==0xee:
        raise AssertionError((tag,"VIC IRQ watchdog: at least five IRQ entries before normal return",
                              "irq_entries",snapshot[6],"flags",snapshot[:12].hex()))
    if snapshot[0]&1 or snapshot[1]!=1 or any(snapshot[i]&1 for i in (2,3,4,5)):
        raise AssertionError((tag,"REU or stock API returned failure flags",snapshot[:12].hex()))
    reu_product=int.from_bytes(snapshot[0x10:0x14],"little")
    stock_product=int.from_bytes(snapshot[0x20:0x24],"little")
    if reu_product!=A*B or stock_product!=STOCK_A*STOCK_B:
        raise AssertionError((tag,"source-built math mismatch",reu_product,stock_product))
    if snapshot[0x40:0x40+122]!=seed:
        raise AssertionError((tag,"IRQ or overlay mutated reserved caller ZP"))
    serviced=snapshot[6]
    if (irq and serviced<1) or (not irq and serviced!=0):
        raise AssertionError((tag,"raster interrupt was not correctly serviced",serviced))
    slots=elapsed(snapshot[8:12])
    if not 0<slots<500000:
        raise AssertionError((tag,"invalid native CIA elapsed PHI2 slots",slots))
    return {
        "case":tag,"tier_kib":tier,"bank":bank,
        "display_enabled":display,"raster_irq_enabled":irq,
        "raster_interrupts_serviced":serviced,
        "native_cia_phi2_slots":slots,
        "nominal_pal_frame_slots":PAL_SLOTS,
        "math_calls_per_guarded_batch":COUNT,
        "caller_zero_page_restored":True,
        "sid_register_writes_in_irq":bool(irq),
        "stock_fallback_still_correct":True,
        "source_stock_prg_sha256":report["stock_prg_sha256"],
        "source_reu_prg_sha256":report["reu_prg_sha256"],
        "native_snapshot_sha256":hashlib.sha256(snapshot).hexdigest(),
    }


def summarize(rows):
    combos={(r["tier_kib"],r["display_enabled"],r["raster_irq_enabled"]):r for r in rows}
    if len(combos)!=8:
        raise AssertionError("Incomplete paired PAL physical REU matrix")
    summary={}
    for tier in (512,16384):
        result={}
        for display in (False,True):
            off=combos[tier,display,False]
            on=combos[tier,display,True]
            for key in ("source_stock_prg_sha256","source_reu_prg_sha256"):
                if off[key]!=on[key]:
                    raise AssertionError("Matched PAL run used distinct source images")
            if on["native_cia_phi2_slots"] <= off["native_cia_phi2_slots"]:
                raise AssertionError(("IRQ/SID handler not visible in physical elapsed slot count",tier,display))
            result["display_on" if display else "display_off"]={
                "no_irq_phi2_slots":off["native_cia_phi2_slots"],
                "irq_sid_phi2_slots":on["native_cia_phi2_slots"],
                "irq_sid_delta":on["native_cia_phi2_slots"]-off["native_cia_phi2_slots"],
                "interrupts_serviced":on["raster_interrupts_serviced"],
            }
        summary[str(tier)]=result
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--monitor-start",choices=("register-go","goto"),
                   default="register-go",
                   help="Set PC with 'r pc=' then plain 'g' (default); legacy 'g xxxx' control")
    p.add_argument("--diagnostic-16m-bank",type=int,choices=(4,200),
                   default=200,
                   help="Diagnose high-bank address vs 16MiB device; restricted to --only-case")
    p.add_argument("--trace-irq-entry",action="store_true",
                   help="Stop at first real IRQ handler entry; diagnostic only")
    p.add_argument("--only-case",choices=(
        "reu_512_display0_irq0","reu_512_display0_irq1",
        "reu_512_display1_irq0","reu_512_display1_irq1",
        "reu_16384_display0_irq0","reu_16384_display0_irq1",
        "reu_16384_display1_irq0","reu_16384_display1_irq1"),
        help="Diagnostic single hardware case; does not provide qualification")
    args=p.parse_args()
    if args.trace_irq_entry and args.only_case is None:
        p.error("--trace-irq-entry requires --only-case")
    if args.diagnostic_16m_bank != 200 and (
            not args.only_case or not args.only_case.startswith("reu_16384")):
        p.error("Alternate 16MiB bank is diagnostic only and needs 16MiB --only-case")
    exe=os.environ.get("VICE_WRAPPER")
    if not exe or not Path(exe).is_file():
        raise RuntimeError("Pinned VICE x64sc required for native PAL REU timing")
    rows=[]
    with tempfile.TemporaryDirectory(prefix="reu_pal_irq_dma_") as td:
        root=Path(td)
        index=0
        for tier,bank in ((512,4),(16384,args.diagnostic_16m_bank)):
            for display in (False,True):
                for armed in (False,True):
                    tag=f"reu_{tier}_display{int(display)}_irq{int(armed)}"
                    if args.only_case is not None and tag!=args.only_case:
                        index+=1
                        continue
                    try:
                        row=native_case(exe,root/tag,tag,tier,bank,display,armed,9910+index,
                                        trace_irq=args.trace_irq_entry,
                                        monitor_start=args.monitor_start)
                    except Exception as error:
                        args.out.parent.mkdir(parents=True,exist_ok=True)
                        args.out.write_text(json.dumps({
                            "status":"FAIL_NATIVE_PAL_REU_GATE_NO_CERTIFICATION",
                            "failed_case":tag,
                            "error":str(error),
                            "completed_case_results":rows,
                            "no_claim_of_16m_irq_safety":True,
                        },indent=2,sort_keys=True)+"\n")
                        raise
                    rows.append(row)
                    args.out.parent.mkdir(parents=True,exist_ok=True)
                    args.out.write_text(json.dumps({
                        "status":"PARTIAL_RESULTS_NOT_QUALIFIED",
                        "completed_case_results":rows,
                        "total_qualified_cases":0,
                    },indent=2,sort_keys=True)+"\n")
                    index+=1
                    if args.trace_irq_entry:
                        print(tag,"IRQ entry breakpoint hit; trace-only, no batch certification",
                              flush=True)
                    else:
                        print(tag,row["native_cia_phi2_slots"],
                              "irq",row["raster_interrupts_serviced"],flush=True)
    report={
        "schema":"source-linked-native-pal-reu-vic-irq-cia-bounded-probe-v1",
        "status":("DIAGNOSTIC_IRQ_ENTRY_NOT_QUALIFIED" if args.trace_irq_entry
                  else "DIAGNOSTIC_SINGLE_CASE_NOT_QUALIFIED" if args.only_case is not None
                  else "PASS_NATIVE_PAL_REU_IRQ_SID_CIA_BOUNDED_PROBE"),
        "monitor_launch_mode":args.monitor_start,
        "diagnostic_bank_override":args.diagnostic_16m_bank != 200,
        "real_vice_reu_dma_timing_included":True,
        "real_vic_screen_contention_included":True,
        "real_irq_and_sid_register_writes_included":True,
        "full_sid_music_player":False,
        "long_run_50hz_application_certified":False,
        "real_hardware_electrical_timing_certified":False,
        "active_irq_touching_overlay_zp_permitted":False,
        "results":rows,"summary":(summarize(rows) if args.only_case is None else None),
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(report["status"],flush=True)


if __name__=="__main__":
    main()
