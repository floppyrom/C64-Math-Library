#!/usr/bin/env python3
"""Check the assembly reduction against the certified model and mixed-call state."""
from pathlib import Path
import json
import random

from assemble_sources import parse_config
from benchmark_normalize_profile_parity import jobs, s16
from mini6502 import CPU
from normalize_model import normalized_reference
import validate_source_build as vsb

ROOT = Path(__file__).resolve().parents[1]


def design_for(profile):
    backend = 'exact' if profile in ('v3_reu_512k', 'v4_reu_16m') else 'log'
    filename = 'COMPONENT_TABLE_DESIGN.json' if backend == 'exact' else 'LOG_RATIO_TABLE_DESIGN.json'
    return backend, json.loads((ROOT / 'validation/normalize' / filename).read_text())


def check_vector(c, entry, io, x, y, design, backend):
    vsb.wr(c, io, x & 65535, 2)
    vsb.wr(c, io + 4, y & 65535, 2)
    before = bytes(c.mem[io:io + 8])
    c.call(entry)
    got = s16(*c.mem[io + 8:io + 10]), s16(*c.mem[io + 10:io + 12])
    assert got == normalized_reference(x, y, design, backend), (backend, x, y, got)
    assert c.c == int(x == y == 0), (backend, x, y, 'carry')
    assert bytes(c.mem[io:io + 8]) == before, (backend, x, y, 'input')


def reduction_cases():
    # Every normalized major/minor pair, both orientations and all signs. The
    # negative form exactly reverses the routine's one's-complement magnitude.
    for major in range(128, 256):
        for minor in range(major + 1):
            for x, y in ((major << 7, minor << 7), (minor << 7, major << 7)):
                for nx in (False, True):
                    for ny in (False, True):
                        yield (~x if nx else x), (~y if ny else y)
    # Exhaust all signed byte vectors, plus the +/-256 correction boundary.
    for x in range(-128, 128):
        for y in range(-128, 128):
            yield x, y
    for x in range(-257, 258):
        for y in (-257, -256, -255, -1, 0, 1, 255, 256, 257):
            yield x, y
            yield y, x


def main():
    out = {'status': 'PASS', 'reduced_plane': {}, 'mixed_calls': {}}
    for p in ('v1_balanced', 'v3_reu_512k'):
        c, entries, io, man, _ = vsb.load(p, jobs[p][0])
        backend, design = design_for(p)
        count = 0
        for x, y in reduction_cases():
            check_vector(c, entries['MATH_VEC2_NORMALIZE_Q8_8'], io, x, y, design, backend)
            count += 1
        out['reduced_plane'][p] = {'cases': count, 'errors': 0, 'prg_sha256': man['output_sha256']}
        print(p, 'reduced-plane and small-vector PASS', count, flush=True)

    for p, builds in jobs.items():
        backend, design = design_for(p)
        for kind, build in zip(('reference', 'alternate'), builds):
            c, entries, io, man, _ = vsb.load(p, build)
            cfg = parse_config(ROOT / man['config'])
            allowed = set(range(cfg['ZP_MAIN'] + 0x18, cfg['ZP_MAIN'] + 0x1c))
            rng = random.Random(0xC6415)
            count = 1000
            for i in range(count):
                # Changes the REU transport bank and uses shared volatile ZP.
                a, b = rng.randrange(256), rng.randrange(1, 256)
                vsb.wr(c, io, a, 1); vsb.wr(c, io + 4, b, 1)
                c.call(entries['MATH_UMUL8'])
                assert vsb.rd(c, io + 8, 2) == a * b
                vsb.wr(c, io + 0x10, a, 1); vsb.wr(c, io + 0x14, b, 1)
                c.call(entries['MATH_UDIV8'])
                assert (c.mem[io + 0x18], c.mem[io + 0x1c]) == divmod(a, b)
                before = bytes(c.mem[:256])
                c.a, c.x, c.y, c.c = a, b, i & 255, i & 1
                x, y = rng.randrange(-32768, 32768), rng.randrange(-32768, 32768)
                check_vector(c, entries['MATH_VEC2_NORMALIZE_Q8_8'], io, x, y, design, backend)
                assert all(c.mem[z] == before[z] for z in range(256) if z not in allowed)
                # Follow normalization with larger shared-ZP operations too.
                ux, uy = rng.randrange(1 << 32), rng.randrange(1 << 32)
                vsb.wr(c, io, ux, 4); vsb.wr(c, io + 4, uy, 4)
                c.call(entries['MATH_UMUL32_READY'])
                assert vsb.rd(c, io + 8, 8) == ux * uy
                sx, sy = rng.randrange(-32768, 32768), rng.randrange(-32768, 32768)
                vsb.wr(c, io, sx & 65535, 2); vsb.wr(c, io + 4, sy & 65535, 2)
                c.call(entries['MATH_SMUL16'])
                assert vsb.rd(c, io + 8, 4) == (sx * sy) & 0xffffffff
            cold = 0
            if backend == 'log':
                # No MATH_INIT or inherited ZP pointer state is needed by this
                # normalizer, including when extracted from the V2 profile.
                b = (build / p / man['output_prg']).read_bytes()
                start = int.from_bytes(b[:2], 'little')
                mem = bytearray([0xa5] * 65536)
                mem[start:start + len(b) - 2] = b[2:]
                c = CPU(mem)
                for _ in range(1000):
                    check_vector(c, entries['MATH_VEC2_NORMALIZE_Q8_8'], io,
                                 rng.randrange(-32768, 32768), rng.randrange(-32768, 32768), design, backend)
                    cold += 1
            out['mixed_calls'][p + '_' + kind] = {
                'normalize_calls': count, 'other_math_calls': count * 4,
                'cold_no_init_calls': cold, 'zp_bytes_allowed': 4,
                'errors': 0, 'prg_sha256': man['output_sha256']}
            print(p, kind, 'mixed-call/ZP/cold-load PASS', flush=True)
    (ROOT / 'validation/normalize/OPTIMIZED_VALIDATION.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
