#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, shutil, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from mini6502 import REV, SIZE
import assemble_sources as asm
import source_relocation as sr

PROFILE = 'v5_hybrid_lowzp'
HYBRID_BYTES = 0x1200
DIV_SRC = (0x4200, 0x51FF)
UMOD8_SRC = (0x5200, 0x527F)
COS_SRC = (0xC766, 0xC770)
SINCOS_SRC = (0xC771, 0xC781)
COS_TABLE_SRC = (0x9500, 0x95FF)
ATAN_LOG_SRC = (0x9600, 0x96FF)
ATAN_Q0_SRC = (0x9700, 0x97FF)
ATAN_Q1_SRC = (0x6E00, 0x6EFF)
ATAN_Q2_SRC = (0x6F00, 0x6FFF)
ATAN_Q3_SRC = (0x9100, 0x91FF)
ATAN_EXTRA_TABLE_BYTES = 3 * 256
V2_REF_ZP_MAIN = 0x02
V2_REF_MATH_IO = 0xC000

PUBLIC_WRAPPERS = {
    'MATH_UDIV16': (0x3140, 0x316B),
    'MATH_UDIV24': (0x3170, 0x31AF),
    'MATH_UDIV32_16': (0x31B0, 0x31EF),
    'MATH_UMOD8': (0x3200, 0x3210),
}

# Direct imported implementations; wider UMOD entries are stable aliases of the
# patched UDIV wrappers and therefore inherit the V2 kernels automatically.
IMPORTED_API = [
    'MATH_UDIV16', 'MATH_UDIV24', 'MATH_UDIV32_16',
    'MATH_UMOD8', 'MATH_UMOD16', 'MATH_UMOD24', 'MATH_UMOD32_16',
    'MATH_COS8', 'MATH_SINCOS8', 'MATH_ATAN2_8',
]


def hx(v: int, width: int = 4) -> str:
    return f'${v:0{width}X}'


def load_prg(path: Path) -> tuple[bytearray, int, int]:
    b = path.read_bytes()
    lo = b[0] | (b[1] << 8)
    hi = lo + len(b) - 3
    mem = bytearray(65536)
    mem[lo:hi + 1] = b[2:]
    return mem, lo, hi


def write_prg(mem: bytearray, lo: int, hi: int, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes((lo & 0xFF, lo >> 8)) + bytes(mem[lo:hi + 1]))


def trace(mem: bytearray, start: int) -> set[int]:
    todo = [start]
    seen: set[int] = set()
    while todo:
        pc = todo.pop() & 0xFFFF
        if pc in seen:
            continue
        oc = mem[pc]
        if oc not in REV:
            raise RuntimeError(f'untraceable opcode {oc:02X} at {pc:04X}')
        seen.add(pc)
        op, mode = REV[oc]
        nxt = (pc + SIZE[mode]) & 0xFFFF
        if op in ('rts', 'rti', 'brk'):
            continue
        if mode == 'rel':
            d = mem[pc + 1]
            if d >= 128:
                d -= 256
            todo.extend((nxt, (nxt + d) & 0xFFFF))
            continue
        if op == 'jmp':
            if mode == 'abs':
                todo.append(mem[pc + 1] | (mem[pc + 2] << 8))
            else:
                raise RuntimeError(f'indirect JMP in imported trace at {pc:04X}')
            continue
        if op == 'jsr':
            todo.extend((mem[pc + 1] | (mem[pc + 2] << 8), nxt))
            continue
        todo.append(nxt)
    return seen


def map_abs(target: int, vals: dict[str, int], hbase: int) -> int:
    # Private V2 division block: old $4200-$51FF -> HYBRID_CODE+$0000-$0FFF.
    if DIV_SRC[0] <= target <= DIV_SRC[1]:
        return hbase + (target - DIV_SRC[0])
    # Private V2 UMOD8 block: old $5200-$527F -> HYBRID_CODE+$1000-$107F.
    if UMOD8_SRC[0] <= target <= UMOD8_SRC[1]:
        return hbase + 0x1000 + (target - UMOD8_SRC[0])
    # Public I/O follows the selected V1-style map.
    if V2_REF_MATH_IO <= target <= V2_REF_MATH_IO + 0x1F:
        return vals['MATH_IO'] + (target - V2_REF_MATH_IO)
    # V2 sine table is byte-identical to V1 and can be shared at the V1 table map.
    if 0x9400 <= target <= 0x94FF:
        return vals['REG_TABLE'] + 0x3400 + (target - 0x9400)
    # V2 cosine table differs from V1; retain a private copy.
    if COS_TABLE_SRC[0] <= target <= COS_TABLE_SRC[1]:
        return hbase + 0x1100 + (target - COS_TABLE_SRC[0])
    # Fast ATAN2 reuses V1's compact LOG/Q0 pages and consumes three pages
    # that are deliberately empty in the V1 table layout.  Q3 cannot stay at
    # donor $9100 because V1 owns that page; remap it to V1's free +$1000 page.
    atan_maps = {
        ATAN_LOG_SRC[0]: vals['REG_TABLE'] + 0x3600,
        ATAN_Q0_SRC[0]: vals['REG_TABLE'] + 0x3700,
        ATAN_Q1_SRC[0]: vals['REG_TABLE'] + 0x0E00,
        ATAN_Q2_SRC[0]: vals['REG_TABLE'] + 0x0F00,
        ATAN_Q3_SRC[0]: vals['REG_TABLE'] + 0x1000,
    }
    for src, dst in atan_maps.items():
        if src <= target <= src + 0xFF:
            return dst + (target - src)
    return target


def relocate_instruction(buf: bytearray, src_mem: bytearray, src_pc: int,
                         dst_pc: int, vals: dict[str, int], hbase: int) -> None:
    oc = src_mem[src_pc]
    op, mode = REV[oc]
    sz = SIZE[mode]
    # opcode and any untouched operand bytes were already copied; patch addresses.
    if mode in ('zp', 'zpx', 'zpy', 'indx', 'indy'):
        old = src_mem[src_pc + 1]
        # Imported certified kernels only use V2 main scratch within the V1 range.
        if not (0x02 <= old <= 0x20):
            raise RuntimeError(f'import would exceed V1 ZP footprint at {src_pc:04X}: ${old:02X}')
        new = vals['ZP_MAIN'] + (old - V2_REF_ZP_MAIN)
        if not (0x02 <= new <= 0xFF):
            raise RuntimeError(f'relocated ZP operand out of range at {src_pc:04X}: {new:04X}')
        buf[dst_pc + 1] = new & 0xFF
    elif mode in ('abs', 'absx', 'absy', 'ind'):
        old = src_mem[src_pc + 1] | (src_mem[src_pc + 2] << 8)
        new = map_abs(old, vals, hbase)
        buf[dst_pc + 1] = new & 0xFF
        buf[dst_pc + 2] = (new >> 8) & 0xFF
    # Relative branches remain byte-identical because every imported code block is
    # moved as a contiguous unit. Immediate constants are not addresses here.


def copy_relocated_block(dst_mem: bytearray, src_mem: bytearray,
                         src_start: int, src_end: int, dst_start: int,
                         code_starts: set[int], vals: dict[str, int], hbase: int) -> None:
    length = src_end - src_start + 1
    dst_mem[dst_start:dst_start + length] = src_mem[src_start:src_end + 1]
    for src_pc in sorted(p for p in code_starts if src_start <= p <= src_end):
        dst_pc = dst_start + (src_pc - src_start)
        relocate_instruction(dst_mem, src_mem, src_pc, dst_pc, vals, hbase)


def copy_relocated_wrapper(dst_mem: bytearray, src_mem: bytearray,
                           src_start: int, src_end: int, dst_start: int,
                           code_starts: set[int], vals: dict[str, int], hbase: int) -> None:
    copy_relocated_block(dst_mem, src_mem, src_start, src_end, dst_start,
                         code_starts, vals, hbase)


def _jmp_target(mem: bytearray, at: int) -> int:
    if mem[at] != 0x4C:
        raise RuntimeError(f'expected JMP at public entry {hx(at)}')
    return mem[at + 1] | (mem[at + 2] << 8)


def apply_atan2_fast(dst_mem: bytearray, src_mem: bytearray,
                     vals: dict[str, int], base_man: dict,
                     donor_entries: dict[str, int], hbase: int) -> dict:
    """Transplant the certified V2 fast ATAN2 into a V1-layout image.

    The public ABI slot stays untouched.  The V2 body is relocated into the
    existing V1 ATAN2 private slot, LOG/Q0 reuse V1's two compact pages, and
    Q1/Q2/Q3 occupy three V1 pages that are empty in the canonical layout.
    """
    base_pub = _public_addr(base_man, 'MATH_ATAN2_8')
    base_isqrt_pub = _public_addr(base_man, 'MATH_ISQRT16')
    donor_pub = donor_entries['MATH_ATAN2_8']
    donor_isqrt_pub = donor_entries['MATH_ISQRT16']
    dst_body = _jmp_target(dst_mem, base_pub)
    dst_isqrt = _jmp_target(dst_mem, base_isqrt_pub)
    src_body = _jmp_target(src_mem, donor_pub)
    src_isqrt = _jmp_target(src_mem, donor_isqrt_pub)
    starts = trace(src_mem, donor_pub)
    body_starts = {pc for pc in starts if src_body <= pc < src_isqrt}
    if not body_starts:
        raise RuntimeError('fast ATAN2 donor body trace is empty')
    src_end = max(pc + SIZE[REV[src_mem[pc]][1]] - 1 for pc in body_starts)
    length = src_end - src_body + 1
    if dst_body + length > dst_isqrt:
        raise RuntimeError('fast ATAN2 body does not fit stable V1 ATAN2 slot')

    # The destination pages must be unused in the V1 layout before ownership is
    # assigned to fast ATAN2.  This guard catches future table-layout changes.
    targets = [vals['REG_TABLE'] + 0x0E00, vals['REG_TABLE'] + 0x0F00, vals['REG_TABLE'] + 0x1000]
    for a in targets:
        if any(dst_mem[a:a + 256]):
            raise RuntimeError(f'ATAN2 fast destination page {hx(a)} is not free in V1 base')

    copy_relocated_block(dst_mem, src_mem, src_body, src_end, dst_body,
                         body_starts, vals, hbase)
    # Clear the now-dead remainder of the old compact body so private address
    # geometry stays pinned while the image remains easy to audit.
    dst_mem[dst_body + length:dst_isqrt] = bytes(dst_isqrt - (dst_body + length))
    dst_mem[targets[0]:targets[0] + 256] = src_mem[ATAN_Q1_SRC[0]:ATAN_Q1_SRC[1] + 1]
    dst_mem[targets[1]:targets[1] + 256] = src_mem[ATAN_Q2_SRC[0]:ATAN_Q2_SRC[1] + 1]
    dst_mem[targets[2]:targets[2] + 256] = src_mem[ATAN_Q3_SRC[0]:ATAN_Q3_SRC[1] + 1]
    return {
        'body': f'{hx(dst_body)}-{hx(dst_body + length - 1)}',
        'body_bytes': length,
        'extra_table_bytes': ATAN_EXTRA_TABLE_BYTES,
        'extra_table_pages': [hx(a) for a in targets],
        'log_page': hx(vals['REG_TABLE'] + 0x3600),
        'q0_page': hx(vals['REG_TABLE'] + 0x3700),
    }


def validate_hybrid_region(vals: dict[str, int], hbase: int) -> None:
    if hbase & 0xFF:
        raise ValueError('HYBRID_CODE must be page aligned')
    hend = hbase + HYBRID_BYTES - 1
    if hend > 0xFFFF:
        raise ValueError('HYBRID_CODE region exceeds 64 KiB address space')
    if max(hbase, 0xD000) <= min(hend, 0xDFFF):
        raise ValueError('HYBRID_CODE must not overlap $D000-$DFFF C64 I/O/ROM window')
    # Reuse the existing V1 configuration validator, then make sure the private
    # hybrid region does not collide with any V1 resident/public workspace claim.
    claims = asm.validate_config('v1_balanced', vals)
    for name, start, end, space in claims:
        if space != 'main':
            continue
        if max(hbase, start) <= min(hend, end):
            raise ValueError(
                f'HYBRID_CODE {hx(hbase)}-{hx(hend)} collides with '
                f'{name} {hx(start)}-{hx(end)}'
            )


def _public_addr(man: dict, name: str) -> int:
    v = man['public_entries'][name]
    return int(v[1:], 16) if isinstance(v, str) and v.startswith('$') else int(v)


def build(config: Path, outdir: Path, include_atan2_fast: bool = True) -> dict:
    vals = asm.parse_config(config)
    if 'HYBRID_CODE' not in vals:
        raise ValueError('hybrid config is missing HYBRID_CODE')
    hbase = vals['HYBRID_CODE']
    validate_hybrid_region(vals, hbase)

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='c64_math_hybrid_') as td:
        tmp = Path(td)
        # Base profile is built from canonical V1 source using the hybrid map.
        v1out = tmp / 'v1'
        v1man = asm.build('v1_balanced', config, v1out)
        v1prg = v1out / v1man['output_prg']
        dst, lo, hi = load_prg(v1prg)

        # Donor is rebuilt from canonical V2 source at its reference map, so the
        # hybrid does not depend on opaque prebuilt donor machine code.
        v2out = tmp / 'v2'
        v2cfg = ROOT / 'relocatable_source' / 'v2_pareto_fast' / 'math_config_reference.inc'
        v2man = asm.build('v2_pareto_fast', v2cfg, v2out)
        v2prg = v2out / v2man['output_prg']
        src, _, _ = load_prg(v2prg)

        # Build exact reachability sets from the rebuilt V2 donor image.
        entries = dict(sr.public_entries())
        atan2_detail = apply_atan2_fast(dst, src, vals, v1man, entries, hbase) if include_atan2_fast else None
        selected_trace: set[int] = set()
        for name in ('MATH_UDIV16', 'MATH_UDIV24', 'MATH_UDIV32_16', 'MATH_UMOD8'):
            selected_trace |= trace(src, entries[name])
        cos_trace = trace(src, entries['MATH_COS8'])
        sincos_trace = trace(src, entries['MATH_SINCOS8'])

        # Private code/data imports.
        copy_relocated_block(dst, src, DIV_SRC[0], DIV_SRC[1], hbase,
                             selected_trace, vals, hbase)
        copy_relocated_block(dst, src, UMOD8_SRC[0], UMOD8_SRC[1], hbase + 0x1000,
                             selected_trace, vals, hbase)
        copy_relocated_block(dst, src, COS_SRC[0], COS_SRC[1], hbase + 0x1080,
                             cos_trace, vals, hbase)
        copy_relocated_block(dst, src, SINCOS_SRC[0], SINCOS_SRC[1], hbase + 0x1090,
                             sincos_trace, vals, hbase)
        dst[hbase + 0x1100:hbase + 0x1200] = src[COS_TABLE_SRC[0]:COS_TABLE_SRC[1] + 1]

        # Replace only the certified public wrapper bodies. Because the wrappers
        # remain at their stable API addresses, imported direct-call timing is
        # cycle-identical to V2 (no dispatcher/JMP tax).
        for name, (ss, se) in PUBLIC_WRAPPERS.items():
            api_starts = {p for p in trace(src, entries[name]) if 0x3000 <= p <= 0x3FFF}
            dst_addr = _public_addr(v1man, name)
            copy_relocated_wrapper(dst, src, ss, se, dst_addr, api_starts, vals, hbase)

        # V2 COS/SINCOS public ABI slots are JMP stubs. Redirect the V1 slots to
        # the private V2 implementations. SIN8 stays V1 because its timing is equal.
        for name, target in [('MATH_COS8', hbase + 0x1080),
                             ('MATH_SINCOS8', hbase + 0x1090)]:
            a = _public_addr(v1man, name)
            dst[a:a + 3] = bytes((0x4C, target & 0xFF, target >> 8))

        new_hi = max(hi, hbase + HYBRID_BYTES - 1)
        prg = outdir / 'math_v5_hybrid_lowzp_game_math.prg'
        write_prg(dst, lo, new_hi, prg)

        # Reuse the stable 46-entry caller include generated from the same map.
        inc_src = v1out / 'math_api.inc'
        inc = outdir / 'math_api.inc'
        inc_text = inc_src.read_text().rstrip() + '\n'
        inc_text += f'\n; Hybrid profile metadata (not additional API entries)\nHYBRID_CODE_BASE         = {hx(hbase)}\nHYBRID_CODE_END          = {hx(hbase + HYBRID_BYTES - 1)}\n'
        inc.write_text(inc_text)

        manifest = {
            'profile': PROFILE,
            'status': 'BUILT_FROM_V1_V2_SOURCE',
            'base_profile': 'v1_balanced',
            'donor_profile': 'v2_pareto_fast',
            'config': str(config.relative_to(ROOT)) if config.is_relative_to(ROOT) else str(config),
            'output_prg': prg.name,
            'output_load': hx(lo),
            'output_end': hx(new_hi),
            'output_sha256': hashlib.sha256(prg.read_bytes()).hexdigest(),
            'public_entries': v1man['public_entries'],
            'math_init': v1man['math_init'],
            'public_io': v1man['public_io'],
            'normal_zp': f'{hx(vals["ZP_MAIN"],2)}-{hx(vals["ZP_MAIN"]+0x1E,2)}',
            'normal_zp_bytes': 31,
            'hybrid_code': f'{hx(hbase)}-{hx(hbase + HYBRID_BYTES - 1)}',
            'hybrid_code_bytes': HYBRID_BYTES,
            'imported_api_entries': [n for n in IMPORTED_API if include_atan2_fast or n != 'MATH_ATAN2_8'],
            'atan2_fast_enabled': include_atan2_fast,
            'atan2_fast': atan2_detail,
            'indirect_beneficiaries': [
                'MATH_UDIV16_SHL8',
                'MATH_URECIP16_Q16',
            ],
            'notes': [
                'All 46 stable API addresses and semantics remain V1-compatible.',
                'MATH_INIT remains optional exactly as in V1.',
                'The imported certified V2 kernels use only the existing V1 normal ZP window.',
                'Fast ATAN2, when enabled, adds no ZP and occupies three formerly empty V1 table pages (768 bytes).',
                'HYBRID_CODE is private implementation storage and may be relocated at build time.',
                'Reference HYBRID_CODE=$A000 lives under BASIC ROM; RAM must be visible while executing imported routines.',
            ],
            'source_inputs': {
                'v1_source_sha256': hashlib.sha256((ROOT/'relocatable_source/v1_balanced/math_relocatable.asm').read_bytes()).hexdigest(),
                'v2_source_sha256': hashlib.sha256((ROOT/'relocatable_source/v2_pareto_fast/math_relocatable.asm').read_bytes()).hexdigest(),
                'builder_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            },
        }
        (outdir / 'source_build_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description='Build the certified V1/V2 low-ZP hybrid C64 Math Library profile.')
    ap.add_argument('--config-kind', choices=['reference', 'alternate'], default='reference')
    ap.add_argument('--config', type=Path)
    ap.add_argument('--out', type=Path, default=ROOT / 'build_hybrid')
    args = ap.parse_args()
    cfg = args.config or ROOT / 'relocatable_source' / PROFILE / f'math_config_{args.config_kind}.inc'
    out = args.out / args.config_kind / PROFILE
    man = build(cfg, out)
    print(PROFILE, args.config_kind, 'BUILT', man['output_sha256'])


if __name__ == '__main__':
    main()
