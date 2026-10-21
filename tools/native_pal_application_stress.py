#!/usr/bin/env python3
"""Issue #367: graduated real SID-register/player and VIC renderer PAL load.

Each candidate executes the untouched 150 public calls in the original varied
24-frame order, with a real line-90 IRQ and a deliberately more demanding
three-voice score player. The 4/8/12/16-row renderer writes visible text and
colour RAM on each scheduled frame. A CPU-side end-of-run oracle verifies all
12 player register shadows and selected live screen/colour cells.

The player is an original deterministic scored synthesizer, NOT an imported
SID binary / production game player. This is an empirical admission test:
a frame miss is published as a miss, never treated as success.
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
import native_pal_consecutive_application as previous
import native_pal_irq_sid_burst as irq

HANDLER=previous.HANDLER
RENDER=previous.RENDER
MAIN=previous.MAIN
VERIFY=0x7a40
HALT=0x7b80
PLAYER_SHADOW=0x3e20
COLOR_EXPECT=0x3e30   # non-ZP safe scratch; CPU colour RAM is only 4 bits
LEVELS=(4,8,12,16)
RUNS=previous.RUNS
assert HANDLER==0x7e00 and RENDER==0x7f00 and RUNS==24


def word(address):
    return repeated.word(address)


def note_freq(midi_note):
    return round(440.0 * 2**((midi_note-69)/12) * (2**24) / 985248)


def make_player():
    """Encode a table-driven SID register-writing IRQ and its reference tables.

    Every SID write is immediately mirrored to RAM so native execution can
    verify actual tick-dependent register *inputs*. No SID readback/audio
    verification is claimed (SID registers are largely write-only).
    """
    melody=((60,64,67,72,69,67,62,64),
            (55,59,62,67,64,62,57,59),
            (48,48,53,53,55,55,50,50))
    tables=[]
    for voice,notes in enumerate(melody):
        frequencies=[note_freq(n) for n in notes]
        tables.extend((
            (0xd400+voice*7,tuple(f&255 for f in frequencies)),
            (0xd401+voice*7,tuple((f>>8)&255 for f in frequencies)),
            (0xd404+voice*7,tuple(
                (0x11 if ((i+voice)&1)==0 else 0x21)
                for i in range(8))),
        ))
    tables.extend((
        (0xd416,(0x30,0x38,0x50,0x60,0x80,0x68,0x48,0x40)),
        (0xd417,(0x12,0x22,0x32,0x42,0x72,0x52,0x22,0x12)),
        (0xd418,(0x1c,0x1d,0x1f,0x1e,0x1c,0x1a,0x1e,0x1f)),
    ))
    if len(tables)!=12:
        raise AssertionError("SID player requires twelve distinct register streams")
    b=bytearray((
        0x48,0x8a,0x48,0x98,0x48,       # save A/X/Y
        0xa9,0x01,0x8d,0x19,0xd0,       # acknowledge actual VIC IRQ
        0xee,0x00,0x3a,                # INC actual IRQ counter
        0xad,0x00,0x3a,0x29,0x07,0xaa, # table index = counter & 7
    ))
    offsets=[]
    for i,(sid,values) in enumerate(tables):
        b.append(0xbd)
        offsets.append(len(b))
        b.extend((0,0))                # LDA table_i,X, relocated below
        b.extend((0x8d,)+tuple(word(sid)))
        b.extend((0x8d,)+tuple(word(PLAYER_SHADOW+i)))
    b.extend((0x68,0xa8,0x68,0xaa,0x68,0x40))
    refs=[]
    for i,(sid,values) in enumerate(tables):
        address=HANDLER+len(b)
        b[offsets[i]:offsets[i]+2]=word(address)
        b.extend(values)
        refs.append({"sid_register":sid,"shadow_address":PLAYER_SHADOW+i,
                     "table_address":address,"values":values})
    if HANDLER+len(b)>RENDER:
        raise AssertionError("Table-driven SID player exceeds $7E00-$7EFF")
    return bytes(b),tuple(refs)


PLAYER,STREAMS=make_player()


def render_rows(rows):
    if type(rows) is not int or rows not in LEVELS:
        raise ValueError("Render rows require a registered 4/8/12/16 load")
    b=bytearray((0xa2,0x0f))             # LDX #15
    loop=RENDER+len(b)
    b.extend((0x8a,0x4d)+tuple(word(previous.FRAMES_ADDR))) # TXA; EOR frame
    for row in range(rows):
        b.extend((0x9d,)+tuple(word(0x0400+row*40)))       # STA screen cell,X
    b.extend((0x29,0x0f))
    for row in range(0,rows,2):
        b.extend((0x9d,)+tuple(word(0xd800+row*40)))       # STA colour cell,X
    b.append(0xca)                                          # DEX
    rel=loop-(RENDER+len(b)+2)
    if not -128<=rel<=127:
        raise AssertionError("Renderer branch escaped local code")
    b.extend((0x10,rel&255))                               # BPL
    b.extend((0xee,0x01,0x3a,0x60))                        # INC jobs; RTS
    if RENDER+len(b)>previous.SUB:
        raise AssertionError("Renderer code overlaps preserved math trace")
    return bytes(b)


def add_readback(rom, old_halt, rows):
    """Patch the old halt JMP into an end-only 6510 RAM oracle.

    The source arithmetic, original per-frame Q/R/C oracle, raster timing
    and visible renderer stay identical. Verification occurs AFTER SEI /
    CIA stop, so no concurrent music IRQ can race the final shadow reads.
    """
    data=bytearray(rom)
    old_offset=old_halt-MAIN
    if data[old_offset:old_offset+3]!=bytes((0x4c,))+word(old_halt):
        raise AssertionError("Original exit JMP changed; cannot add oracle")
    if data[VERIFY-MAIN:VERIFY-MAIN+16]!=b'\xea'*16:
        raise AssertionError("SID oracle collides with original source bytes")
    b=bytearray((0xad,0x00,0x3a,0x29,0x07,0xaa)) # IRQ count &7 -> X
    def check_accumulator_against(address):
        b.extend((0xcd,)+tuple(word(address)))  # CMP abs
        b.extend((0xf0,0x03,0xee)+tuple(word(previous.ERRORS_ADDR)))
    for item in STREAMS:
        b.extend((0xbd,)+tuple(word(item["table_address"]))) # expected table
        check_accumulator_against(item["shadow_address"])
    # The scheduler increments FRAME_COUNTER after rendering frame 23.
    # Readback runs after all 24 jobs: compare the rendered pattern against
    # FRAME_COUNTER-1, not the advanced counter (24).  This correction is
    # essential; otherwise six legitimate screen/colour checks fail.
    for addr,mask in ((0x0400,0),(0x040f,15),
                      (0x0400+40*(rows-1)+15,15)):
        b.extend((0xad,)+tuple(word(previous.FRAMES_ADDR)))
        b.extend((0x38,0xe9,0x01))           # SEC; SBC #1 (last drawn frame)
        if mask: b.extend((0x49,mask))
        check_accumulator_against(addr)
    for addr,mask in ((0xd800,0),(0xd80f,15),
                      (0xd800+40*((rows-1)//2*2)+15,15)):
        b.extend((0xad,)+tuple(word(previous.FRAMES_ADDR)))
        b.extend((0x38,0xe9,0x01))           # SEC; SBC #1 (last drawn frame)
        if mask: b.extend((0x49,mask))
        b.extend((0x29,0x0f))                 # expected 4-bit colour
        b.extend((0x8d,)+tuple(word(COLOR_EXPECT))) # save expected nibble
        b.extend((0xad,)+tuple(word(addr)))    # read actual colour RAM
        b.extend((0x29,0x0f))                 # high nibble is undefined!
        check_accumulator_against(COLOR_EXPECT)
    b.extend((0x4c,)+tuple(word(HALT)))
    if VERIFY+len(b)>=HALT:
        raise AssertionError("End-only player/renderer oracle exceeds reserved RAM")
    data[old_offset:old_offset+3]=bytes((0x4c,))+word(VERIFY)
    data[VERIFY-MAIN:VERIFY-MAIN+len(b)]=b
    data[HALT-MAIN:HALT-MAIN+3]=bytes((0x4c,))+word(HALT)
    return bytes(data),len(b)


def build_harness(entries, *, display, reserve_cpu_cycles=0, rows=4):
    if type(reserve_cpu_cycles) is not int or reserve_cpu_cycles!=0:
        raise ValueError("No NOP workload may be injected into real music/renderer")
    if type(rows) is not int or rows not in LEVELS:
        raise ValueError("Unqualified renderer row load")
    with (patch.object(previous,"sequencer_irq",lambda:PLAYER),
          patch.object(previous,"renderer",lambda:render_rows(rows))):
        code,old_halt,expected,geometry=previous.build_harness(
            entries,display=display,reserve_cpu_cycles=0)
    instrumented,readback_bytes=add_readback(code,old_halt,rows)
    meta=dict(geometry)
    meta.update({
        "player_mode":"table-driven-12-stream-3voice-sid-irq",
        "sid_register_stores_per_irq":len(STREAMS),
        "sid_shadow_cells_verified_at_exit":len(STREAMS),
        "screen_rows_per_frame":rows,
        "rendered_character_cells_per_frame":rows*16,
        "rendered_color_cells_per_frame":((rows+1)//2)*16,
        "native_readback_oracle_bytes":readback_bytes,
        "original_halt":old_halt,
        "main_halt":HALT,
        "player_sha256":hashlib.sha256(PLAYER).hexdigest(),
        "renderer_sha256":hashlib.sha256(render_rows(rows)).hexdigest(),
    })
    return instrumented,HALT,expected,meta


def run(vice, levels=LEVELS):
    if not vice or not Path(vice).is_file():
        raise ValueError("Pinned x64sc r46284 executable required")
    if (not levels or tuple(levels)!=tuple(sorted(set(levels)))
            or any(type(v) is not int or v not in LEVELS for v in levels)):
        raise ValueError("Renderer loads must be sorted unique members of 4/8/12/16")
    evidence=source.complete_report()
    if frame_evidence_replay.replay(evidence)!=evidence:
        raise AssertionError("Nine-plan source evidence failed source replay")
    input_sha=hashlib.sha256(json.dumps(
        [call[-1] for call in seven.scenario()],
        separators=(",",":")).encode()).hexdigest()
    records=[]
    with tempfile.TemporaryDirectory(prefix="native_pal_realwork_") as td:
        root=Path(td)
        for plan_index,plan in enumerate(installed.CHOICES):
            folder=root/plan
            image,exports,proof=installed.build_one(plan,evidence,folder)
            for rows in levels:
                for screen in (False,True):
                    def this_harness(entries, *, display, reserve_cpu_cycles=0):
                        return build_harness(
                            entries,display=display,
                            reserve_cpu_cycles=reserve_cpu_cycles,rows=rows)
                    tag=f"{plan}_rows{rows:02d}_screen{int(screen)}"
                    with (patch.object(repeated,"build_harness",this_harness),
                          patch.object(repeated,"extra_irq_events",
                                       previous.varied_irq_events)):
                        row=repeated.read_monitor(
                            vice,image,exports,folder,tag,
                            19500+plan_index*100+rows*2+int(screen),
                            display=screen)
                    if row["qualified_prg_sha256"]!=proof["linked_prg_sha256"]:
                        raise AssertionError("Math installer image SHA changed")
                    row.update(plan=plan,renderer_rows=rows,
                               original_public_calls=seven.CALLS,
                               source_frame_inputs_sha256=input_sha,
                               linked_ram_bytes=proof["linked_ram_bytes"],
                               zero_page_bytes=proof["zero_page_bytes"],
                               player_and_screen_oracle_errors=row["public_output_error_count"],
                               strict_frame_deadlines_met=row["nominal_deadline_misses"]==0,
                               worst_cumulative_margin_slots=min(
                                   r["deadline_margin_slots"] for r in row["records"]))
                    records.append(row)
                    print("PAL SID RENDER STRESS",plan,rows,screen,
                          "misses",row["nominal_deadline_misses"],
                          "minmargin",row["worst_cumulative_margin_slots"],
                          flush=True)
    if len({r["source_frame_inputs_sha256"] for r in records})!=1 or len({
            r["public_output_sha256"] for r in records})!=1:
        raise AssertionError("Source trace or public output changed across plans")
    summaries=[]
    for plan in installed.CHOICES:
        for screen in (False,True):
            rows=[r for r in records if r["plan"]==plan and
                  r["display_enabled"]==screen]
            summaries.append({
                "plan":plan,"display_enabled":screen,
                "highest_tested_passing_renderer_rows":max(
                    (r["renderer_rows"] for r in rows if
                     r["strict_frame_deadlines_met"]),default=None),
                "first_tested_failing_renderer_rows":next((
                    r["renderer_rows"] for r in rows if
                    not r["strict_frame_deadlines_met"]),None),
                "levels":[{"rows":r["renderer_rows"],
                           "deadline_misses":r["nominal_deadline_misses"],
                           "worst_margin_slots":r["worst_cumulative_margin_slots"],
                           "irqs":r["raster_irq_count"]} for r in rows],
            })
    return {
        "schema":"native-pal-original-trace-sid-render-graded-load-v1",
        "native_emulator":"pinned-x64sc-r46284",
        "original_source_public_calls_per_run":seven.CALLS,
        "varied_original_24_frame_trace_preserved":True,
        "real_sid_register_stores_per_irq":len(STREAMS),
        "sid_shadow_native_oracle":True,
        "renderer_screen_and_colour_native_oracle":True,
        "external_sid_song_or_complete_effect_certified":False,
        "sprite_or_reu_dma_tested":False,
        "nominal_pal_slots_per_frame":previous.PAL,
        "levels":list(levels),
        "summaries":summaries,
        "runs":records,
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows",default="4,8,12,16")
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    try:
        levels=tuple(int(x) for x in args.rows.split(","))
    except ValueError:
        parser.error("Rows must be comma-separated registered integer choices")
    try:
        report=run(os.environ.get("VICE_WRAPPER",""),levels)
    except ValueError as exc:
        parser.error(str(exc))
    content=json.dumps(report,indent=2,sort_keys=True)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(content,encoding="utf-8")
    else:
        print(content,end="")


if __name__=="__main__":
    main()
