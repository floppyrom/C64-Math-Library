#!/usr/bin/env python3
"""Experimental 24 different PAL frames: actual SID note sequencing and VIC screen rendering.

Replay the original 150 public calls in their original 24-frame order, with
the source-linked installed PRG, a raster IRQ running a small three-voice SID
sequencer, and a 64-character/16-colour-cell per-frame renderer. A continuous
32-bit CIA timer measures deadline margins in one pinned x64sc PAL session.

This is a small genuine music+render workload, not playback of an external
SID file, a full demo/game, a sprite multiplexer or REU DMA qualification.
Native timing must not be claimed until the pinned workflow passes.
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
import mixed_seven_d65536_frame as source
import mixed_seven_frame_parity as seven
import native_installed_d65536_pal as installed
import native_pal_consecutive_busiest as repeated
import native_pal_irq_sid_burst as irq
import native_pal_vic_cia_probe as cia

RUNS=seven.FRAMES
PLANS=installed.CHOICES
MAIN=repeated.MAIN
HANDLER=repeated.HANDLER
SUB=repeated.SUB
RENDER=0x7f00
EXPECT=0x7900
PAL=repeated.PAL
OUTPUT=repeated.OUTPUT
FRAMES_ADDR=repeated.FRAME_COUNTER
ERRORS_ADDR=repeated.ERROR_COUNTER
DATA=repeated.DATA
assert RUNS==24 and seven.CALLS==150 and PAL==19656



def varied_irq_events(serviced, completed=RUNS):
    """Final light frame may finish before its line-90 IRQ has occurred.

    Unlike a repeated heavy frame-8 loop, a varied 3-call frame often
    completes *before* line 90. For 24 raster-zero-scheduled jobs, the
    first 23 line-90 interrupts must have occurred; the last interrupt
    need not have occurred when the final CIA snapshot is taken.
    Report all observed IRQs, never synthesize the missing final event.
    """
    if (type(serviced) is not int or type(completed) is not int
            or completed!=RUNS or not completed-1<=serviced<255):
        raise ValueError("Unqualified varied-frame real raster IRQ count")
    return max(0,serviced-completed)


def word(a):
    return repeated.word(a)


def store(addr, value):
    return repeated.one_instruction_store(addr,value)


def sequencer_irq():
    """Hardware IRQ; update three audible SID voices from 8-step note tables.

    Each note lasts four PAL ticks. The frequency tables use the PAL SID
    oscillator clock (~985248 Hz) and equal-tempered MIDI note numbers.
    A/X/Y are preserved and VIC raster IRQ is acknowledged before playback.
    """
    b=bytearray((
        0x48,0x8a,0x48,0x98,0x48,                 # save A/X/Y
        0xa9,0x01,0x8d,0x19,0xd0,                 # acknowledge VIC IRQ
        0xee,irq.IRQ_COUNT&255,irq.IRQ_COUNT>>8, # actual IRQ count
        0xad,irq.IRQ_COUNT&255,irq.IRQ_COUNT>>8, # LDA tick
        0x4a,0x4a,0x29,0x07,0xaa,               # tick/4 modulo 8
    ))
    patch_positions=[]
    notes=(
        (60,64,67,72,67,64,62,67),  # melody
        (55,59,62,67,62,59,57,62),  # harmony
        (48,48,53,53,55,55,48,48),  # bass
    )
    for voice in range(3):
        for byte_idx in (0,1):
            b.append(0xbd)                       # LDA note_table,X
            patch_positions.append(len(b))
            b.extend((0,0))
            b.append(0x8d)                       # STA SID frequency register
            b.extend(word(0xd400+voice*7+byte_idx))
    b.extend((0x68,0xa8,0x68,0xaa,0x68,0x40))   # restore Y/X/A; RTI
    for voice,melody in enumerate(notes):
        freqs=[round(440*(2**((note-69)/12))*2**24/985248) for note in melody]
        for part in (0,1):
            address=HANDLER+len(b)
            index=patch_positions[2*voice+part]
            b[index:index+2]=word(address)
            b.extend((freq>>(8*part))&255 for freq in freqs)
    if len(b)>RENDER-HANDLER:
        raise AssertionError("SID player overlaps renderer")
    return bytes(b)


def renderer():
    """Draw four 16-character animated screen rows plus their colour cells."""
    b=bytearray((0xa2,15))      # LDX #15
    loop=RENDER+len(b)
    b.extend((0x8a,0x4d))       # TXA; EOR frame counter
    b.extend(word(FRAMES_ADDR))
    for addr in (0x0400,0x0428,0x0450,0x0478):
        b.append(0x9d)          # STA screen row,X
        b.extend(word(addr))
    b.extend((0x29,0x0f,0x9d)) # AND #$0f; STA colour RAM,X
    b.extend(word(0xd800))
    b.append(0xca)              # DEX
    delta=loop-(RENDER+len(b)+2)
    if not -128<=delta<=127:
        raise AssertionError("Renderer loop branch range")
    b.extend((0x10,delta&255))  # BPL loop
    b.extend((0xee,irq.IRQ_AUX&255,irq.IRQ_AUX>>8,0x60)) # count renderer jobs; RTS
    if len(b)>SUB-RENDER:
        raise AssertionError("Renderer overlaps arithmetic source")
    return bytes(b)


def extract_frame(entries, frame, display):
    """Extract verbatim operand staging / public JSR / result collection bytes."""
    base,_,expected,count=irq.irq_harness(
        entries,frame=frame,display=display,irq_enabled=True,raster_line=90)
    first=base.find(irq.SYNCH)
    start=base.find(irq.START,first)
    stop=base.rfind(bytes((0xa9,0,0x8d,0x0e,0xdc)))
    reset=irq.store(irq.IRQ_COUNT,0)+irq.store(irq.IRQ_AUX,0)
    if (first<0 or start<first or stop<start+10 or
            base[first:start][-len(reset):]!=reset or
            base[start:start+10]!=irq.START+bytes((0xa9,0x11,0x8d,0x0e,0xdc))):
        raise AssertionError("Source-linked IRQ/CIA arithmetic frame source drift")
    expected_calls=len(cia.busiest_calls(frame))
    if count!=expected_calls or len(expected)!=2*count:
        raise AssertionError("Varied frame call count or source oracle drift")
    return (base[:first],base[first:start-len(reset)],
            base[start:start+10],base[start+10:stop]+b'\x60',expected,count)


def build_harness(entries, *, display, reserve_cpu_cycles=0):
    """Return authentic varied calls, without adding synthetic NOP workload."""
    if type(reserve_cpu_cycles) is not int or reserve_cpu_cycles != 0:
        raise ValueError("Real SID/renderer harness rejects injected NOP reserve")
    if type(display) is not bool or set(entries)!=set(source.OPS):
        raise ValueError("Seven public exports and explicit VIC display choice required")
    frames=[extract_frame(entries,n,display) for n in range(RUNS)]
    if sum(frame[5] for frame in frames)!=seven.CALLS:
        raise AssertionError("Expected exactly 150 original public calls")
    prefix,barrier,start=frames[0][:3]
    if any(f[:3]!=(prefix,barrier,start) for f in frames):
        raise AssertionError("PAL IRQ setup or timer differs across original frames")

    bodies=bytearray()
    addresses=[]
    final_live=bytearray(48)
    all_expected=bytearray()
    expected_offsets=[]
    sizes=[]
    body_hashes=[]
    for _,_,_,body,expected,count in frames:
        addresses.append(SUB+len(bodies))
        bodies.extend(body)
        sizes.append(count)
        body_hashes.append(hashlib.sha256(body).hexdigest())
        expected_offsets.append(len(all_expected))
        all_expected.extend(expected)
        final_live[:len(expected)]=expected
    if SUB+len(bodies)>=0xc000 or EXPECT+len(all_expected)>=HANDLER:
        raise AssertionError("Varied source exceeds safe screen/IRQ/I/O RAM map")
    if len(all_expected)!=2*seven.CALLS:
        raise AssertionError("Original output/carry oracle has wrong total length")

    b=bytearray(prefix)
    def emit(raw): b.extend(raw)
    # Real SID synthesis configuration: master volume, three independent
    # gated oscillators and ADSR envelopes (the IRQ changes pitched notes).
    for addr,value in (
        (0xd418,0x0c),
        (0xd405,0x09),(0xd406,0xe8),(0xd404,0x11),
        (0xd40c,0x08),(0xd40d,0xd8),(0xd40b,0x21),
        (0xd410,0x00),(0xd411,0x08),
        (0xd413,0x08),(0xd414,0xe8),(0xd412,0x41)):
        emit(store(addr,value))
    emit(store(FRAMES_ADDR,0))
    emit(store(ERRORS_ADDR,0))
    for frame,(address,offset,count) in enumerate(zip(addresses,expected_offsets,sizes)):
        emit(barrier)
        if frame==0:
            emit(irq.store(irq.IRQ_COUNT,0)+irq.store(irq.IRQ_AUX,0))
            emit(start)                         # start CIA only once
        emit(bytes((0x20,))+word(address))       # JSR original source frame
        emit((0xa2,0))                          # compare live original results
        verify=MAIN+len(b)
        emit(bytes((0xbd,))+word(OUTPUT))        # LDA result/carry,X
        emit(bytes((0xdd,))+word(EXPECT+offset)) # CMP oracle[offset],X
        emit((0xf0,3))                          # BEQ past INC errors
        emit(bytes((0xee,))+word(ERRORS_ADDR))
        emit((0xe8,0xe0,2*count))                # INX; CPX #actual bytes
        rel=verify-(MAIN+len(b)+2)
        if not -128<=rel<=127:
            raise AssertionError("Output compare loop branch too long")
        emit((0xd0,rel&255))
        emit(bytes((0x20,))+word(RENDER))        # real VIC screen/colour writes
        emit(bytes((0xad,))+word(FRAMES_ADDR))
        emit((0x0a,0x0a,0xaa))                   # index CIA sample [frame*4]
        for i,reg in enumerate((0xdc04,0xdc05,0xdc06,0xdc07)):
            emit(bytes((0xad,))+word(reg))
            emit(bytes((0x9d,))+word(DATA+i))
        emit(bytes((0xee,))+word(FRAMES_ADDR))
    # Fail closed if any of the 24 real renderer calls was lost.
    emit(bytes((0xad,))+word(irq.IRQ_AUX))
    emit((0xc9,RUNS,0xf0,3))
    emit(bytes((0xee,))+word(ERRORS_ADDR))
    emit((0x78,))
    emit(store(0xd01a,0))
    emit(store(0xdc0e,0))
    emit(store(0xdc0f,0))
    halt=MAIN+len(b)
    emit(bytes((0x4c,))+word(halt))
    if MAIN+len(b)>EXPECT:
        raise AssertionError("Frame scheduler collides with source oracle table")
    b.extend(b'\xea'*(EXPECT-(MAIN+len(b))))
    b.extend(all_expected)
    if MAIN+len(b)>HANDLER:
        raise AssertionError("Oracle table overlaps raster IRQ")
    b.extend(b'\xea'*(HANDLER-(MAIN+len(b))))
    music=sequencer_irq()
    b.extend(music)
    b.extend(b'\xea'*(RENDER-(MAIN+len(b))))
    drawing=renderer()
    b.extend(drawing)
    b.extend(b'\xea'*(SUB-(MAIN+len(b))))
    b.extend(bodies)
    if MAIN+len(b)!=SUB+len(bodies):
        raise AssertionError("Original source bytes moved during build")
    return bytes(b),halt,bytes(final_live),{
        "source_frames":RUNS,"source_public_calls":seven.CALLS,
        "calls_by_frame":sizes,"body_addresses":addresses,
        "body_sha256_by_frame":body_hashes,
        "oracle_table_address":EXPECT,
        "oracle_sha256":hashlib.sha256(all_expected).hexdigest(),
        "sid_irq_bytes":len(music),"renderer_bytes":len(drawing),
        "source_body_bytes":len(bodies),"raster_irq_handler":HANDLER,
        "sid_player_mode":"three-voice-eight-note-4tick-original-sequencer",
        "rendered_character_cells_per_frame":64,
        "rendered_color_cells_per_frame":16,
    }


def run(vice):
    if not vice or not Path(vice).is_file():
        raise ValueError("Pinned x64sc r46284 executable required")
    evidence=source.complete_report()
    if frame_evidence_replay.replay(evidence)!=evidence:
        raise AssertionError("Nine-plan source evidence replay failed")
    source_digest=hashlib.sha256(json.dumps(
        [call[-1] for call in seven.scenario()],separators=(",",":")
    ).encode()).hexdigest()
    rows=[]
    with tempfile.TemporaryDirectory(prefix="pal_varied_sid_render_") as td:
        root=Path(td)
        for i,plan in enumerate(PLANS):
            directory=root/plan
            image,entries,proof=installed.build_one(plan,evidence,directory)
            for screen in (False,True):
                # Reuse the independently exercised native one-process remote
                # monitor and continuous CIA oracle, but replace its harness.
                with (patch.object(repeated,"build_harness",build_harness),
                      patch.object(repeated,"extra_irq_events",varied_irq_events)):
                    row=repeated.read_monitor(
                        vice,image,entries,directory,
                        plan+"_screen_"+str(int(screen)),19400+i*4+int(screen),
                        display=screen)
                if row["qualified_prg_sha256"]!=proof["linked_prg_sha256"]:
                    raise AssertionError("Verified installed PRG changed")
                row.update(
                    plan=plan,source_frame="original-varied-0-through-23",
                    source_frame_inputs_sha256=source_digest,
                    source_linked_calls_per_frame=None,
                    total_public_calls=seven.CALLS,
                    final_frame_can_finish_before_line90_irq=True,
                    raster_irqs_observed_at_final_math_completion=row["raster_irq_count"],
                    linked_ram_bytes=proof["linked_ram_bytes"],
                    zero_page_bytes=proof["zero_page_bytes"],
                )
                rows.append(row)
                print("PAL ORIGINAL TRACE SID RENDER",plan,screen,
                      row["nominal_deadline_misses"],
                      row["peak_cumulative_deadline_lateness_slots"],
                      flush=True)
    for field in ("source_frame_inputs_sha256","public_output_sha256"):
        if len({row[field] for row in rows})!=1:
            raise AssertionError("Matched source and public outputs differ")
    return {
        "schema":"native-pal-varied-24frame-sid-render-experiment-v1",
        "native_emulator":"pinned-x64sc-r46284",
        "source_original_24_frames":True,
        "source_original_public_calls_per_run":seven.CALLS,
        "one_consecutive_pal_session_per_plan_and_display":True,
        "real_three_voice_sid_note_sequencer":True,
        "real_vic_screen_characters_and_color_ram_written":True,
        "external_sid_tune_or_full_game_tested":False,
        "sprites_or_reu_dma_tested":False,
        "full_50hz_application_certified":False,
        "pal_slots_per_frame":PAL,
        "plans":list(PLANS),"rows":rows,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    data=json.dumps(run(os.environ.get("VICE_WRAPPER","")),indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(data,encoding="utf-8")
    else:
        print(data,end="")


if __name__=="__main__":
    main()
