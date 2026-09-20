#!/usr/bin/env python3
"""Exhaustive dual-emulator and ACME certification of optional ATAN2 kernels.

Requires py65 (python3 -m pip install py65) and a built ACME executable.
This does not patch, regenerate, or overwrite any resident profile.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import tempfile

from benchmark import (Assembler, CPU, HERE, ROOT, KINDS, TABLE_BYTES, PUBLIC,
                       image, source)
from export_optimized import OPTIMIZED, export_source, table_blocks
from tables import exact_phase, phase_error, signed8


def digest(data):
    return hashlib.sha256(data).hexdigest()


class GuardedMemory(bytearray):
    """Reject even transient writes outside result and JSR return bytes."""
    armed = False
    allowed = frozenset()

    def __setitem__(self, address, value):
        if self.armed and address not in self.allowed:
            raise AssertionError(f'unexpected write to ${address:04X}')
        super().__setitem__(address, value)


def layout(kind, relocated=False):
    org = 0x88E9 if relocated else 0x8000
    asm = source(kind, org)
    replacements = {}
    if relocated:
        replacements = {'X0': 0xB000, 'Y0': 0xB004, 'Z0': 0xB008}
        replacements.update({name: 0xA000 + i * 256
                             for i, (name, _) in enumerate(table_blocks(kind))})
        # Only change symbol assignments, never instruction literals.
        lines = []
        for line in asm.splitlines():
            symbol = line.split('=', 1)[0].strip()
            if symbol in replacements and '=' in line:
                line = f'{symbol}=${replacements[symbol]:04X}'
            lines.append(line)
        asm = '\n'.join(lines) + '\n'
    code, _, constants = Assembler().assemble(asm)
    if not relocated:
        mem = image(kind, org)
    else:
        mem = bytearray(65536)
        for address, value in code.items():
            mem[address] = value
        mem[PUBLIC:PUBLIC + 3] = bytes((0x4C, org & 255, org >> 8))
        for name, data in table_blocks(kind):
            address = constants[name]
            mem[address:address + 256] = data
    return mem, code, constants, org, replacements


def certify(kind, initial_carry, reference, baseline, relocated=False):
    from py65.devices.mpu6502 import MPU

    mem, code, constants, org, replacements = layout(kind, relocated)
    x0, y0, z0 = (constants[s] for s in ('X0', 'Y0', 'Z0'))
    m1, m2 = GuardedMemory(mem), GuardedMemory(mem)
    for m in (m1, m2):
        m.allowed = frozenset((z0, 0x1FC, 0x1FD))
    cpu, independent = CPU(m1), MPU(memory=m2)
    cycles, errors = collections.Counter(), collections.Counter()
    outputs, cycle_vector = bytearray(), bytearray()
    baseline_differences = 0
    axis_failures = 0
    for rx in range(256):
        for ry in range(256):
            for m in (m1, m2):
                m.armed = False
                m[x0], m[y0], m[z0] = rx, ry, 0xA5
                m.armed = True
            cpu.c = initial_carry
            cpu.n, cpu.v, cpu.z, cpu.i = rx & 1, ry & 1, (rx ^ ry) & 1, ry & 1
            cpu.a, cpu.x, cpu.y = 0xA5, rx ^ 0x55, ry ^ 0xAA
            cyc = cpu.call(PUBLIC, max_steps=40)

            independent.a, independent.x, independent.y = 0x5A, ry, rx
            independent.p = (0x20 | initial_carry | ((rx & 1) << 7)
                             | ((ry & 1) << 6) | (((rx ^ ry) & 1) << 1)
                             | ((ry & 1) << 2))
            independent.sp = 0xFD
            independent.stPushWord(0xFEFF)
            independent.pc = PUBLIC
            before = independent.processorCycles
            for _ in range(40):
                independent.step()
                if independent.pc == 0xFF00:
                    break
            else:
                raise AssertionError('independent emulator step limit')
            other_cycles = independent.processorCycles - before
            got = cpu.mem[z0]
            assert got == independent.memory[z0] == cpu.a == independent.a, (kind, rx, ry)
            assert cyc == other_cycles, (kind, rx, ry, cyc, other_cycles)
            assert cpu.c == (independent.p & 1) == 0, (kind, rx, ry, 'carry')
            assert cpu.sp == independent.sp == 0xFD
            assert cpu.d == (independent.p & 8) == 0
            assert cpu.i == ((independent.p >> 2) & 1) == (ry & 1)
            assert m1[x0] == m2[x0] == rx and m1[y0] == m2[y0] == ry
            error = phase_error(got, reference[(rx << 8) | ry])
            assert error <= 1, (kind, rx, ry, error)
            if rx == 0 or ry == 0:
                axis_failures += int(error != 0)
            if baseline is not None:
                baseline_differences += int(got != baseline[(rx << 8) | ry])
            cycles[cyc] += 1
            errors[error] += 1
            outputs.append(got)
            cycle_vector.append(cyc)
    assert axis_failures == 0
    if kind != 'sum_small':
        assert baseline_differences == 0
    result = {
        'kernel': kind, 'layout': 'relocated_page_crossing' if relocated else 'reference',
        'origin': f'${org:04X}', 'initial_carry': initial_carry, 'cases': 65536,
        'code_bytes': len(code), 'table_bytes': TABLE_BYTES[kind],
        'occupied_bytes_excluding_public_jmp': len(code) + TABLE_BYTES[kind],
        'zp_bytes': 0, 'extra_stack_bytes': 0,
        'mean_cycles': sum(k * v for k, v in cycles.items()) / 65536,
        'min_cycles': min(cycles), 'max_cycles': max(cycles),
        'cycle_distribution': dict(sorted(cycles.items())),
        'max_phase_error_against_rounded_reference': max(errors),
        'error_distribution': dict(sorted(errors.items())),
        'changed_outputs_vs_shipped_compact': baseline_differences if baseline is not None else None,
        'outputs_sha256': digest(outputs), 'cycle_vector_sha256': digest(cycle_vector),
        'independent_result_and_cycle_mismatches': 0,
        'abi_failures': 0, 'unexpected_writes': 0, 'axis_failures': axis_failures,
        'status': 'PASS',
    }
    print(kind, result['layout'], 'C=' + str(initial_carry),
          f"{result['mean_cycles']:.6f}", 'PASS', flush=True)
    return result, outputs


def acme_check(kind, relocated, acme, temp):
    mem, code, constants, org, replacements = layout(kind, relocated)
    text = export_source(kind).replace('ATAN2_CODE = $8000', f'ATAN2_CODE = ${org:04X}')
    if relocated:
        lines = []
        for line in text.splitlines():
            symbol = line.split('=', 1)[0].strip()
            if symbol in replacements and '=' in line:
                line = f'{symbol}=${replacements[symbol]:04X}'
            lines.append(line)
        text = '\n'.join(lines) + '\n'
    src, out = temp / 'check.asm', temp / 'check.prg'
    src.write_text(text)
    subprocess.run([acme, '-f', 'cbm', '-o', str(out), str(src)],
                   check=True, capture_output=True, text=True)
    hi = max(constants[name] + len(data) for name, data in table_blocks(kind))
    expected = bytes((PUBLIC & 255, PUBLIC >> 8)) + bytes(mem[PUBLIC:hi])
    actual = out.read_bytes()
    assert actual == expected, (kind, relocated, 'ACME differs from bundled assembler')
    return {'kernel': kind, 'relocated': relocated, 'byte_identical': True,
            'prg_sha256': digest(actual), 'status': 'PASS'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acme', required=True)
    parser.add_argument('--out', type=Path,
                        default=ROOT / 'validation/ATAN2_OPTIMIZATION_VALIDATION.json')
    args = parser.parse_args()
    acme_version = subprocess.run([args.acme, '--version'], check=True, capture_output=True,
                                  text=True).stdout.strip()
    for kind in OPTIMIZED:
        path = HERE / 'standalone' / f'atan2_s8_s8_u8_{kind}.asm'
        assert path.read_text() == export_source(kind), f'stale export: {path}'
    reference = bytes(exact_phase(signed8(x), signed8(y))
                      for x in range(256) for y in range(256))
    checks = []
    result, baseline = certify('compact', 0, reference, None)
    checks.append(result)
    result, _ = certify('fast', 0, reference, baseline)
    checks.append(result)
    for kind in OPTIMIZED:
        for relocated in (False, True):
            for carry in (0, 1):
                result, _ = certify(kind, carry, reference, baseline, relocated)
                checks.append(result)
    with tempfile.TemporaryDirectory(prefix='atan2-acme-') as directory:
        acme_checks = [acme_check(kind, relocated, args.acme, Path(directory))
                       for kind in OPTIMIZED for relocated in (False, True)]
    sources = [HERE / f'atan2_{k}.asm' for k in KINDS]
    sources += [HERE / n for n in ('tables.py', 'benchmark.py', 'export_optimized.py',
                                   'validate_optimized.py')]
    sources += sorted((HERE / 'standalone').glob('*.asm'))
    report = {
        'status': 'PASS', 'date': '2026-09-20',
        'baseline_commit': '33ea1e80711dcc938f98f4dd4f64f0816c78d8dd',
        'scope': 'Optional standalone kernels; resident profiles are not modified.',
        'timing': ('CPU instruction cycles including public JMP and RTS; excluding caller JSR, '
                   'VIC DMA stalls and interrupts. D=0. Lookup tables page aligned.'),
        'independent_emulator': 'py65 ' + importlib.metadata.version('py65'),
        'acme_version': acme_version,
        'dual_emulator_input_cases': sum(c['cases'] for c in checks),
        'source_sha256': {str(p.relative_to(ROOT)): digest(p.read_bytes()) for p in sources},
        'checks': checks, 'acme_checks': acme_checks,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS ->', args.out)


if __name__ == '__main__':
    main()
