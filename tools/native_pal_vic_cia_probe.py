#!/usr/bin/env python3
"""EXPERIMENTAL native x64sc PAL VIC/CIA whole-burst clock-slot probe.

This runs the actual seven-API source-pinned installation, staged public
operands and source benchmark call order at a raster-synchronised PAL frame
start. Cascaded CIA1 timers measure elapsed PHI2 slots, including VIC steals.
It is a scoped synthetic frame *probe*, NOT a 50 Hz application, IRQ/SID or
REU proof, nor a time value from the offline Mini6502 simulator.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
from math import isqrt

import mixed_seven_frame_parity as seven
import mixed_seven_cross_pareto as crossed
import selective_speed_s3232 as signed
from native_seven_frame_installer import build_exact_frame_prg, CODE, IO, ZP

HARNESS = 0x7000
RESULT = 0x3b00
PAL_SLOTS = 312 * 63
FRAME = 0


def busiest_calls(frame=FRAME):
    if type(frame) is not int or not 0 <= frame < seven.FRAMES:
        raise ValueError('Unqualified synthetic frame number')
    return [row for row in seven.scenario() if row[0] == frame]


def expected_byte(api, x, y, n):
    if api == 'MATH_ISQRT16':
        return isqrt(n) & 0xff, 0
    if api in seven.OPS[:2]:
        return (x * y) & 0xff, 0
    if api in seven.OPS[3:5]:
        q, rem, carry = (x // y if y else 0, x % y if y else 0, int(y == 0))
    else:
        q, rem, carry = signed.reference(x, y)
    return (rem if api.endswith('MOD32_32') else q) & 0xff, carry


def harness(entries, *, frame=FRAME, display=True):
    """Generate authentic 6510 loads/JSRs and a 32-bit CIA A/B wall timer.

    The selected production linked image must end below $7000. Data reads
    are live results; no prefilled host-computed output is accepted.
    """
    if set(entries) != set(seven.OPS):
        raise ValueError('Missing selected public operation addresses')
    calls = busiest_calls(frame)
    if not calls or len(calls) > 64:
        raise AssertionError('Unqualified native burst length')
    b = bytearray()
    def emit(*values): b.extend(values)
    def absop(op, address):
        if not 0 <= address < 0x10000: raise ValueError('invalid absolute address')
        emit(op, address & 255, (address >> 8) & 255)
    def store_const(where, value):
        emit(0xa9, value & 255)  # LDA #imm
        absop(0x8d, where)     # STA abs

    emit(0x78, 0xd8)            # SEI; CLD, keep interrupts out of this probe
    emit(0xa9, 0x35, 0x85, 0x01)  # LDA #$35; STA $01: full RAM + VIC/CIA I/O
    store_const(0xd011, 0x1b if display else 0x0b)  # normal badlines or blank screen
    store_const(0xd016, 0x08)
    store_const(0xd018, 0x14)
    store_const(0xdc0d, 0x7f)  # mask CIA1 interrupts
    store_const(0xdd0d, 0x7f)  # mask CIA2 interrupts
    store_const(0xdc0e, 0x00)  # stop CIA1 Timer A
    store_const(0xdc0f, 0x00)  # stop CIA1 Timer B
    for addr in (0xdc04, 0xdc05, 0xdc06, 0xdc07):
        store_const(addr, 0xff)

    # Wait until 9th raster bit is high (lines 256..311), then until
    # it falls and $D012 reports line 0. Never mistake line 256 for 0.
    sync_high = HARNESS + len(b)
    absop(0x2c, 0xd011)       # BIT $D011
    emit(0x10, 0xfb)          # BPL -5
    assert HARNESS + len(b) - 5 == sync_high
    sync_low = HARNESS + len(b)
    absop(0x2c, 0xd011)       # BIT $D011
    emit(0x30, 0xfb)          # BMI -5
    absop(0xad, 0xd012)       # LDA $D012
    emit(0xd0, 0xf6)          # BNE -10
    assert HARNESS + len(b) - 10 == sync_low

    store_const(0xdc0f, 0x51)  # Timer B: force load, start, Timer A underflows
    store_const(0xdc0e, 0x11)  # Timer A: force load, start, PHI2

    expected = []
    for _, ordinal, api, x, y, n, a, rx, ry, carry, _ in calls:
        if api in seven.OPS[:3]:
            writes = [(IO+i, c) for i, c in enumerate(x.to_bytes(4, 'little')+y.to_bytes(4, 'little'))]
            writes += [(IO+16+i, c) for i, c in enumerate(n.to_bytes(2, 'little'))]
            where = IO+8
        else:
            writes = [(IO+16+i, c) for i, c in enumerate(x.to_bytes(4, 'little')+y.to_bytes(4, 'little'))]
            writes += [(IO+24+i, 0x55) for i in range(4)]
            writes += [(IO+28+i, 0x66) for i in range(4)]
            where = IO+28 if api.endswith('MOD32_32') else IO+24
        for addr, value in writes:
            store_const(addr, value)
        emit(0xa9, a, 0xa2, rx, 0xa0, ry, 0xd8, 0x38 if carry else 0x18)
        absop(0x20, entries[api])  # JSR exact public export
        # Record carry immediately, before any LDA affects zero/negative flags.
        emit(0x08, 0x68, 0x29, 0x01)  # PHP, PLA, AND #1
        absop(0x8d, RESULT+6+2*ordinal+1)
        absop(0xad, where)
        absop(0x8d, RESULT+6+2*ordinal)
        expected.extend(expected_byte(api, x, y, n))

    emit(0xa9, 0x00)          # LDA #0
    absop(0x8d, 0xdc0e)      # stop Timer A (wall clock end)
    absop(0x8d, 0xdc0f)      # stop Timer B
    for j, addr in enumerate((0xdc04, 0xdc05, 0xdc06, 0xdc07)):
        absop(0xad, addr)
        absop(0x8d, RESULT+j)
    absop(0xad, 0xd012)
    absop(0x8d, RESULT+4)
    absop(0xad, 0xd011)
    absop(0x8d, RESULT+5)
    halt = HARNESS + len(b)
    absop(0x4c, halt)
    if HARNESS+len(b)>0x8000:
        raise AssertionError('Machine-code PAL probe spilled beyond $8000')
    return bytes(b), halt, bytes(expected), len(calls)


def decode_elapsed(raw: bytes) -> int:
    if len(raw) < 4:
        raise ValueError('Truncated CIA counter dump')
    timer_a = int.from_bytes(raw[:2], 'little')
    timer_b = int.from_bytes(raw[2:4], 'little')
    # Timer B cascades, so a full 65536 PHI2 ticks are preserved in B.
    return (0xffff - timer_b) * 65536 + (0xffff - timer_a)


def run_one(vice: str, image: bytes, entries: dict, folder: Path, tag: str,
            port: int, *, display=True, frame=FRAME):
    if not (Path(vice).is_file() and image[:2] == CODE.to_bytes(2, 'little')):
        raise ValueError('Pinned native emulator and exact linked load address needed')
    if CODE+len(image)-2 >= HARNESS or IO != 0xc040 or ZP != 0x70:
        raise AssertionError('PRG/harness or linker memory map collision')
    stub, halt, expected, count = harness(entries, display=display, frame=frame)
    mem = bytearray(0x10000)
    mem[CODE:CODE+len(image)-2] = image[2:]
    mem[HARNESS:HARNESS+len(stub)] = stub
    prg = folder/(tag+'.prg')
    dumped = folder/(tag+'.bin')
    prg.write_bytes(bytes((CODE & 255, CODE >> 8)) + mem[CODE:HARNESS+len(stub)])
    args = [vice, '-console', '-silent', '-pal', '-sounddev', 'dummy', '-warp',
            '-remotemonitor', '-remotemonitoraddress', f'127.0.0.1:{port}',
            '-initbreak', 'reset']
    with (folder/(tag+'.log')).open('w') as log:
        proc = subprocess.Popen(args, cwd=folder, stdout=log, stderr=log)
        try:
            for _ in range(200):
                try:
                    sock = socket.create_connection(('127.0.0.1',port), timeout=.1)
                    break
                except (OSError, TimeoutError):
                    time.sleep(.05)
            else:
                raise RuntimeError('Native PAL probe remote monitor unavailable')
            sock.settimeout(.25)
            def command(line, marker):
                sock.sendall((line+'\n').encode())
                output = b''
                for _ in range(200):
                    try:
                        chunk = sock.recv(16384)
                        if not chunk: break
                        output += chunk
                        if marker.encode() in output and output.endswith(b') '):
                            break
                    except socket.timeout:
                        continue
                if marker.encode() not in output:
                    raise RuntimeError('VICE PAL probe monitor: %r %r' % (line, output[-800:]))
            command('load "'+str(prg)+'" 0','Loading')
            command('break '+format(halt,'04x'),'BREAK:')
            command('g '+format(HARNESS,'04x'),'Stop on  exec')
            end = RESULT+6+2*count-1
            command('bsave "'+str(dumped)+'" 0 '+format(RESULT,'04x')+' '+format(end,'04x'),'Saving')
            sock.sendall(b'quit\n')
            sock.close()
        finally:
            proc.terminate()
            try:proc.wait(timeout=3)
            except subprocess.TimeoutExpired:proc.kill()
    output = dumped.read_bytes()
    if len(output)!=6+2*count or output[6:]!=expected:
        raise AssertionError(('Native PAL public-call checksum/carry mismatch', tag, output[6:].hex(), expected.hex()))
    wall = decode_elapsed(output)
    if wall <= 0 or wall > 500000:
        raise AssertionError(('Impossible native CIA slot count',tag,wall,output[:4].hex()))
    return {
        'name': tag, 'native_vice_model': 'PAL', 'display_enabled': display,
        'measured_cia_phi2_slots': wall, 'nominal_pal_frame_slots': PAL_SLOTS,
        'nominal_headroom_after_whole_burst': PAL_SLOTS-wall,
        'source_linked_calls': count,
        'captured_outputs_sha256': hashlib.sha256(output[6:]).hexdigest(),
        'raw_cia_counter_hex': output[:4].hex(),
        'raster_at_stop': output[4], 'raster_high_bit_at_stop': (output[5]>>7)&1,
        'frame': frame, 'source_frame_inputs_sha256': hashlib.sha256(
            json.dumps([x[-1] for x in busiest_calls(frame)],separators=(',', ':')).encode()
        ).hexdigest(),
        'limited_probe_not_application_frame_qualification': True,
    }


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path)
    p.add_argument('--frame', type=int, default=FRAME)
    args = p.parse_args()
    vice = os.environ.get('VICE_WRAPPER','')
    if not vice or not Path(vice).is_file():
        p.error('Set VICE_WRAPPER to pinned installed x64sc r46284')
    report = crossed.complete_report()
    rows=[]
    with tempfile.TemporaryDirectory(prefix='pal_vic_cia_') as td:
        folder=Path(td)
        for i, (zp, label) in enumerate(((0,'compact'),(31,'speed'))):
            image, entries, proof = build_exact_frame_prg(
                report,folder/label,zp_budget=zp,frame_optimize='peak')
            for j, display in enumerate((False,True)):
                tag=f'{label}_display_{int(display)}'
                result=run_one(vice,image,entries,folder,tag,13710+i*2+j,
                               display=display,frame=args.frame)
                result['selected_choice']=proof['choice']
                result['qualified_prg_sha256']=proof['qualified_prg_sha256']
                result['source_report_basis']=report['basis']
                rows.append(result)
                print('NATIVE PAL CIA PROBE',tag,result['measured_cia_phi2_slots'],flush=True)
    for pair in (rows[:2], rows[2:]):
        if pair[0]['captured_outputs_sha256']!=pair[1]['captured_outputs_sha256']:
            raise AssertionError('Display control changed native public-call results')
        if pair[1]['measured_cia_phi2_slots'] <= pair[0]['measured_cia_phi2_slots']:
            raise AssertionError('VIC display did not increase native elapsed slots')
    result={
        'basis':'experimental-native-r46284-pal-vic-cia-seven-api-busy-burst',
        'prgs_qualified_by_existing_native_public_abi_oracle':True,
        'physical_native_pal_vic_cia_probe':True,
        'real_50hz_application_frame_certified':False,
        'reu_dma_sid_irq_measured':False,
        'frame':args.frame, 'runs':rows,
    }
    output=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding='utf-8')
    else:
        print(output,end='')


if __name__=='__main__':
    main()
