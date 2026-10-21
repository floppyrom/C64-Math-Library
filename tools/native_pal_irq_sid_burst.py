#!/usr/bin/env python3
"""Experimental native PAL raster-IRQ + minimal SID register-write math probe.

Measures 24-call arithmetic bursts on actual installer-linked PRGs with one
real VIC-II raster IRQ and several SID writes in the handler. A matched
no-IRQ control uses an otherwise identical harness at the same raster
phase. This is NOT an actual SID music player, REU test or continuous
24-frame / 50 Hz game certificate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from unittest.mock import patch

import frame_evidence_replay
import mixed_seven_d65536_frame as model
import native_installed_d65536_pal as installed
import native_pal_vic_cia_probe as cia

BASE_HARNESS = cia.harness

IRQ = 0x7e00
IRQ_COUNT = 0x3a00
IRQ_AUX = 0x3a01
SYNCH = bytes((0x2c, 0x11, 0xd0, 0x10, 0xfb))  # BIT D011; BPL -5
START = bytes((0xa9, 0x51, 0x8d, 0x0f, 0xdc))  # CIA Timer B start
FRAME_SET = (0, 8, 16)
LINES = (90,)
PLANS = installed.CHOICES


def store(addr: int, value: int) -> bytes:
    if type(addr) is not int or type(value) is not int or not (0 <= addr < 65536):
        raise ValueError("Unqualified native IRQ source address")
    return bytes((0xa9, value & 255, 0x8d, addr & 255, addr >> 8))


def irq_handler():
    """6510 hardware IRQ, preserves A/X/Y/P; acknowledge VIC and touch SID."""
    return bytes((
        0x48, 0x8a, 0x48, 0x98, 0x48,     # PHA / TXA PHA / TYA PHA
        0xa9, 0x01, 0x8d, 0x19, 0xd0,     # LDA #1; STA $D019 (VIC IRQ ack)
        0xee, IRQ_COUNT & 255, IRQ_COUNT >> 8,  # INC IRQ_COUNTER
        0xad, IRQ_COUNT & 255, IRQ_COUNT >> 8,  # LDA counter
        0x8d, 0x00, 0xd4,               # STA SID voice-1 frequency low
        0xa9, 0x08, 0x8d, 0x01, 0xd4,   # SID voice-1 frequency high
        0xa9, 0x11, 0x8d, 0x04, 0xd4,   # SID voice-1 gate/control
        0xa9, 0x0f, 0x8d, 0x18, 0xd4,   # SID master volume
        0x68, 0xa8, 0x68, 0xaa, 0x68, 0x40,  # PLA TAY; PLA TAX; PLA; RTI
    ))


def irq_harness(entries, *, frame: int, display: bool,
                irq_enabled: bool, raster_line: int = 90):
    """Insert real raster-IRQ wiring, after original I/O setup/before sync.

    Counter reset is intentionally *after* the raster-0 barrier, so an
    interrupt incurred while the emulator booted cannot count as a
    math-workload IRQ. Timer writes and output collection remain those
    of the source-proven original seven-API harness.
    """
    if type(raster_line) is not int or not 0 < raster_line < 256:
        raise ValueError("Raster IRQ line must be a low-half PAL line")
    if type(irq_enabled) is not bool:
        raise ValueError("Explicit enable/disable IRQ control required")
    base, old_halt, expected, calls = BASE_HARNESS(
        entries, frame=frame, display=display)
    if base[:2] != b'\x78\xd8' or base[-3] != 0x4c:
        raise AssertionError("Underlying source-proven PAL harness drifted")
    first=base.find(SYNCH)
    start=base.find(START,first)
    if first < 0 or start < first or base.count(SYNCH) != 1 or base.count(START) != 1:
        raise AssertionError("Cannot identify source PAL frame start + timer setup")
    setup=(
        store(0xfffe,IRQ & 255)+store(0xffff,IRQ >> 8)+
        store(0xd012,raster_line)+store(0xd019,0x01)+
        store(0xd01a,0x01 if irq_enabled else 0x00)+
        bytes((0x58,))  # CLI: preserve original P across source public JSR
    )
    reset=store(IRQ_COUNT,0)+store(IRQ_AUX,0)
    b=bytearray(base[:first]+setup+base[first:start]+reset+base[start:])
    halt=old_halt+len(setup)+len(reset)
    if cia.HARNESS+len(b)-3 != halt:
        raise AssertionError("Source math burst epilogue moved unexpectedly")
    # Retain original CIA elapsed-slot snapshots, but return real IRQ count
    # in the two display-raster result bytes instead of original raster values.
    original=bytes((0xad,0x12,0xd0,0x8d,0x04,0x3b,
                    0xad,0x11,0xd0,0x8d,0x05,0x3b))
    new=bytes((0xad, IRQ_COUNT & 255, IRQ_COUNT >> 8,0x8d,0x04,0x3b,
               0xad, IRQ_AUX & 255, IRQ_AUX >> 8,0x8d,0x05,0x3b))
    if bytes(b[-15:-3])!=original:
        raise AssertionError("CIA/VIC source-probe epilogue no longer matches")
    b[-15:-3]=new
    b[-2:]=bytes((halt & 255,halt >> 8))
    if cia.HARNESS+len(b)>IRQ:
        raise AssertionError("IRQ handler overlaps busiest-frame caller code")
    b.extend(b'\xea'*(IRQ-cia.HARNESS-len(b)))
    b.extend(irq_handler())
    if cia.HARNESS+len(b)>=0x8000 or len(irq_handler())>128:
        raise AssertionError("Raster IRQ source escaped reserved harness region")
    return bytes(b),halt,expected,calls


def compare(rows, *, plans=PLANS, frames=FRAME_SET, lines=LINES):
    expected={(p,f,display,armed,l) for p in plans for f in frames
              for display in (False,True) for armed in (False,True)
              for l in lines}
    actual=[(x["plan"],x["frame"],x["display_enabled"],
             x["raster_irq_enabled"],x["raster_irq_line"]) for x in rows]
    if len(actual)!=len(expected) or set(actual)!=expected:
        raise ValueError("IRQ/SID PAL samples are missing, duplicated or mixed")
    totals={}
    for plan in plans:
        pairs=[]
        for f in frames:
            for display in (False,True):
                for line in lines:
                    off=next(x for x in rows if x["plan"]==plan and x["frame"]==f
                             and x["display_enabled"]==display and
                             x["raster_irq_line"]==line and not x["raster_irq_enabled"])
                    on=next(x for x in rows if x["plan"]==plan and x["frame"]==f
                            and x["display_enabled"]==display and
                            x["raster_irq_line"]==line and x["raster_irq_enabled"])
                    for field in ("qualified_prg_sha256",
                                  "captured_outputs_sha256",
                                  "source_frame_inputs_sha256",
                                  "source_linked_calls"):
                        if off[field]!=on[field]:
                            raise AssertionError("IRQ changed source/input/output evidence")
                    if (off["raster_irq_serviced"]!=0 or on["raster_irq_serviced"]!=1
                            or on["measured_cia_phi2_slots"] <=
                               off["measured_cia_phi2_slots"]):
                        raise AssertionError("IRQ not serviced exactly once within timed math burst")
                    pairs.append({
                        "frame":f,"display_enabled":display,"raster_irq_line":line,
                        "math_control_cia_slots":off["measured_cia_phi2_slots"],
                        "irq_plus_sid_cia_slots":on["measured_cia_phi2_slots"],
                        "irq_sid_delta_slots":on["measured_cia_phi2_slots"]-off["measured_cia_phi2_slots"],
                        "nominal_headroom_after_irq_sid":cia.PAL_SLOTS-on["measured_cia_phi2_slots"],
                        "output_sha256":on["captured_outputs_sha256"],
                    })
        totals[plan]={
            "samples":pairs,"worst_irq_plus_sid_slots":max(x["irq_plus_sid_cia_slots"] for x in pairs),
            "worst_irq_sid_added_slots":max(x["irq_sid_delta_slots"] for x in pairs),
            "nominal_deadline_misses":sum(x["nominal_headroom_after_irq_sid"]<0 for x in pairs),
        }
    for f in frames:
        for display in (False,True):
            for line in lines:
                digests={x["captured_outputs_sha256"] for x in rows
                         if x["frame"]==f and x["display_enabled"]==display
                         and x["raster_irq_line"]==line}
                if len(digests)!=1:
                    raise AssertionError("Selected source plans changed public output hashes")
    return totals


def run(vice: str, *, frames=FRAME_SET, lines=LINES, plans=PLANS):
    if not vice or not Path(vice).is_file():
        raise ValueError("Pinned native x64sc required")
    if frames!=FRAME_SET or lines!=LINES or plans!=PLANS:
        raise ValueError("Research evidence requires declared exact complete stress corpus")
    report=model.complete_report()
    if frame_evidence_replay.replay(report)!=report:
        raise AssertionError("Model source-proven nine-plan frame corpus changed")
    rows=[]
    with tempfile.TemporaryDirectory(prefix="raster_irq_sid_pal_") as temp:
        root=Path(temp)
        for i,plan in enumerate(plans):
            folder=root/plan
            image,entries,proof=installed.build_one(plan,report,folder)
            for frame in frames:
                for display in (False,True):
                    for armed in (False,True):
                        for line in lines:
                            tag=f"{plan}_f{frame:02d}_d{int(display)}_irq{int(armed)}_r{line}"
                            def run_harness(e, *, frame, display):
                                return irq_harness(e,frame=frame,display=display,
                                                   irq_enabled=armed,raster_line=line)
                            with patch.object(cia,"harness",side_effect=run_harness):
                                sample=cia.run_one(
                                    vice,image,entries,folder,tag,
                                    18300+i*100+frame*4+int(display)*2+int(armed),
                                    display=display,frame=frame)
                            sample["plan"]=plan
                            sample["qualified_prg_sha256"]=proof["linked_prg_sha256"]
                            sample["raster_irq_enabled"]=armed
                            sample["raster_irq_line"]=line
                            sample["raster_irq_serviced"]=sample["raster_at_stop"]
                            sample.pop("raster_at_stop")
                            sample.pop("raster_high_bit_at_stop")
                            rows.append(sample)
                            print("PAL IRQ SID",tag,sample["measured_cia_phi2_slots"],
                                  sample["raster_irq_serviced"],flush=True)
    summary=compare(rows,plans=plans,frames=frames,lines=lines)
    return {
        "schema":"experimental-pal-raster-irq-sid-synthetic-burst-v1",
        "real_native_vic_raster_irq_measured":True,
        "real_sid_register_writes_measured":True,
        "full_music_player_measured":False,
        "consecutive_50hz_frames_measured":False,
        "reu_dma_measured":False,
        "real_application_frame_certified":False,
        "nominal_pal_slots":cia.PAL_SLOTS,
        "raster_irq_line":list(lines),
        "frames":list(frames),
        "plans":list(plans),
        "native_runs":rows,
        "summary":summary,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path)
    a=p.parse_args()
    result=run(os.environ.get("VICE_WRAPPER",""))
    payload=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(payload,encoding="utf-8")
    else:
        print(payload,end="")


if __name__=="__main__":
    main()
