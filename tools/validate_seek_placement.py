#!/usr/bin/env python3
"""Prove that the SEEK code/state islands are private to the seek kernels.

For every V1-V4 source build (reference and alternate maps) this runs
MATH_INIT, the complete common-API validation suite and (V3/V4) the Turbo16/32
lifecycle suite with a memory tracer
that also follows REU DMA transfers. Every byte read or written by an
instruction outside the seek code must lie outside the seek code, JMP slots
and object state. It also checks that the islands sit inside the profile's
claimed regions and do not overlap each other.

Run after `make reference alternate`. Writes validation/movement/SEEK_PLACEMENT.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import mini6502  # noqa: E402
from assemble_sources import parse_config, validate_config  # noqa: E402
import seek_kernel as K  # noqa: E402

PROFILES = ['v1_balanced', 'v2_pareto_fast', 'v3_reu_512k', 'v4_reu_16m']


def seek_ranges(profile, cfg):
    """Byte sets of the seek code (incl. JMP slots) and object state."""
    vals = parse_config(cfg)
    text = ''.join(f'{k} = ${v:04X}\n' for k, v in vals.items())
    text += (ROOT / profile / 'resident/movement/native/seek_dda.asm').read_text()
    mem, labels, const = mini6502.Assembler().assemble(text)
    code = set(mem)
    state = set(range(const['SEEK8_STATE'], const['SEEK8_STATE'] + K.S8_BYTES))
    state |= set(range(const['SEEK16_STATE'], const['SEEK16_STATE'] + K.S16_BYTES))
    scratch = set(range(const['SEEK_T'], const['SEEK_T'] + K.SCRATCH_BYTES))
    return code, state, scratch, const, vals


class Tracer:
    def __init__(self):
        self.code = set()
        self.touched = {}
        self.on = True

    def install(self):
        tr = self
        rd0, wr0, step0 = mini6502.CPU.rd, mini6502.CPU.wr, mini6502.CPU.step

        def rd(cpu, a):
            if tr.on and cpu._pc0 not in tr.code:
                tr.touched.setdefault(a & 0xFFFF, cpu._pc0)
            return rd0(cpu, a)

        def wr(cpu, a, v):
            a &= 0xFFFF
            if tr.on and cpu._pc0 not in tr.code:
                tr.touched.setdefault(a, cpu._pc0)
            if a == 0xDF01 and (v & 0x80) and cpu.reu is not None and (v & 3) in (1, 2):
                # REU -> C64 (or swap) DMA writes C64 RAM without going through wr().
                c64 = cpu.mem[0xDF02] | (cpu.mem[0xDF03] << 8)
                ln = cpu.mem[0xDF07] | (cpu.mem[0xDF08] << 8) or 65536
                fixed = bool(cpu.mem[0xDF0A] & 0x80)
                for j in range(1 if fixed else ln):
                    tr.touched.setdefault((c64 + j) & 0xFFFF, cpu._pc0)
            return wr0(cpu, a, v)

        def step(cpu):
            cpu._pc0 = cpu.pc
            return step0(cpu)

        mini6502.CPU.rd, mini6502.CPU.wr, mini6502.CPU.step = rd, wr, step
        mini6502.CPU._pc0 = 0


def main():
    tracer = Tracer()
    tracer.install()
    import validate_source_build as vsb  # after patching
    out = {'status': 'PASS', 'profiles': {}}
    for kind in ('reference', 'alternate'):
        for p in PROFILES:
            cfg = ROOT / 'relocatable_source' / p / f'math_config_{kind}.inc'
            code, state, scratch, const, vals = seek_ranges(p, cfg)
            claims = validate_config(p, vals)
            main_claims = [(s, e) for _, s, e, sp in claims if sp == 'main']
            outside = sorted(a for a in code | state if not any(s <= a <= e for s, e in main_claims))
            assert not outside, (p, kind, 'outside claimed regions', [hex(a) for a in outside[:8]])
            assert not code & state, (p, kind, 'code/state overlap')
            assert all((const[n] & 7) == 0 for n in ('SEEK8_STATE', 'SEEK16_STATE')), (p, kind, 'state alignment')
            tracer.code = code
            tracer.touched = {}
            build = ROOT / 'build_source' / kind
            vsb.validate(p, build)
            if p in ('v3_reu_512k', 'v4_reu_16m'):
                import validate_turbo_relocation as tur
                tur.validate_one(p, kind)  # Turbo16/32 BEGIN/CALL/END overlays
            hit = sorted(a for a in tracer.touched if a in code or a in state)
            assert not hit, (p, kind, 'foreign access', [(hex(a), hex(tracer.touched[a])) for a in hit[:8]])
            out['profiles'][f'{p}/{kind}'] = {
                'code_bytes_incl_jmp_slots': len(code), 'state_bytes': len(state),
                'scratch': f'${min(scratch):04X}-${max(scratch):04X}',
                'seek8_state': f"${const['SEEK8_STATE']:04X}", 'seek16_state': f"${const['SEEK16_STATE']:04X}",
                'foreign_accesses': 0,
            }
            print(p, kind, 'PASS', len(code), 'code', len(state), 'state')
    path = ROOT / 'validation/movement/SEEK_PLACEMENT.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1) + '\n')
    print('SEEK PLACEMENT PASS')


if __name__ == '__main__':
    main()
