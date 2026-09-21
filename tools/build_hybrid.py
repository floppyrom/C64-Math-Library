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
HYBRID_BYTES = 0x1E00
DIV_SRC = (0x4200, 0x51FF)
UMOD8_SRC = (0x5200, 0x527F)
COS_SRC = (0xC766, 0xC770)
SINCOS_SRC = (0xC771, 0xC781)
COS_TABLE_SRC = (0x9500, 0x95FF)
ATAN_LOGX_SRC = (0x9600, 0x96FF)
ATAN_LOGY_SRC = (0x9700, 0x97FF)
ATAN_QPOS_SRC = (0x6E00, 0x6EFF)
ATAN_QNEG_SRC = (0x6F00, 0x6FFF)
ATAN_EXTRA_TABLE_BYTES = 4 * 256
SDIV24_PREFIX_SRC = (0x8100, 0x83F5)
SDIV24_CORE_SRC = (0x8400, 0x8849)
SDIV24_WRAPPER_SRC = (0x2550, 0x256E)
SDIV24_PRIVATE_TABLE_OFFSET = 0x1600
SDIV24_PREFIX_BYTES = SDIV24_PREFIX_SRC[1]-SDIV24_PREFIX_SRC[0]+1
SDIV24_CORE_BYTES = SDIV24_CORE_SRC[1]-SDIV24_CORE_SRC[0]+1

# V5 shared fast signed-division components. SDIV16 and SDIV32/16 use the
# same 1,104-byte private UDIV16 engine; V5 keeps one copy at HYBRID_CODE+$120C.
SDIV16_PREFIX_SRC=(0x7A00,0x7BD3)
SDIV16_CG_SRC=(0x7C0C,0x805B)
SDIV16_WRAPPER_SRC=(0x2520,0x254B)
SDIV32_CG_SRC=(0x890C,0x8D5B)
SDIV32_MX_SRC=(0x8E00,0x90E1)
SDIV32_PREFIX_SRC=(0x9200,0x92E8)
SDIV32_WRAPPER_SRC=(0x2590,0x25CF)
V2_REF_ZP_MAIN = 0x02
V2_REF_MATH_IO = 0xC000

PUBLIC_WRAPPERS = {
    'MATH_UDIV32_16': (0x31B0, 0x31EF),
    'MATH_UMOD8': (0x3200, 0x3210),
}

# Division-refresh direct source ranges in the current V2 donor image.
UDIV8_DIRECT_SRC = (0x4000, 0x41AD)
UDIV16_DIRECT_SRC = (0xB800, 0xBDC9)
SDIV16_DIRECT_PREFIX_SRC = (0x7A00, 0x7C2A)
SDIV16_DIRECT_CORE_SRC = (0x7C2B, 0x8177)
SDIV24_DIRECT_PREFIX_SRC = (0x8178, 0x82ED)
SDIV24_DIRECT_CORE_SRC = (0x82EE, 0x8878)

# Direct imported implementations; wider UMOD entries are stable aliases of the
# patched UDIV wrappers and therefore inherit the V2 kernels automatically.
IMPORTED_API = [
    'MATH_UDIV16', 'MATH_UDIV24', 'MATH_UDIV32_16',
    'MATH_UMOD8', 'MATH_UMOD16', 'MATH_UMOD24', 'MATH_UMOD32_16',
    'MATH_COS8', 'MATH_SINCOS8', 'MATH_ATAN2_8',
    'MATH_SDIV16', 'MATH_SMOD16', 'MATH_SDIV24', 'MATH_SMOD24',
    'MATH_SDIV16_SHL8',
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
    # Sum-fast ATAN2 consumes four pages deliberately empty in the V1 table layout.
    atan_maps = {
        ATAN_LOGX_SRC[0]: vals['REG_TABLE'] + 0x0D00,
        ATAN_LOGY_SRC[0]: vals['REG_TABLE'] + 0x0E00,
        ATAN_QPOS_SRC[0]: vals['REG_TABLE'] + 0x0F00,
        ATAN_QNEG_SRC[0]: vals['REG_TABLE'] + 0x1000,
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




def _v5_div16_zp(vals: dict[str,int], old:int) -> int:
    # SDIV16 donor map: signed $3E-$41 -> V5 +$0C..+$0F;
    # private UDIV16 $42-$49 -> shared +$10..+$17.
    if 0x3E <= old <= 0x41: return vals['ZP_MAIN']+0x0C+(old-0x3E)
    if 0x42 <= old <= 0x49: return vals['ZP_MAIN']+0x10+(old-0x42)
    raise RuntimeError(f'SDIV16 import unexpected ZP ${old:02X}')


def _v5_div32_zp(vals: dict[str,int], old:int) -> int:
    # SDIV32/16 donor map: signed $3E-$43, shared UDIV16 $44-$4B,
    # mixed-width scratch $4C-$4F. All remain inside the 31-byte V5 window.
    if 0x3E <= old <= 0x43: return vals['ZP_MAIN']+0x0A+(old-0x3E)
    if 0x44 <= old <= 0x4B: return vals['ZP_MAIN']+0x10+(old-0x44)
    if 0x4C <= old <= 0x4F: return vals['ZP_MAIN']+0x18+(old-0x4C)
    raise RuntimeError(f'SDIV32/16 import unexpected ZP ${old:02X}')


def _copy_fast_signed_component(dst:bytearray,src:bytearray,ss:int,se:int,ds:int,starts:set[int],
                                vals:dict[str,int],kind:str,dcg:int,dpre:int=0,dmx:int=0) -> None:
    dst[ds:ds+(se-ss+1)]=src[ss:se+1]
    for pc in sorted(x for x in starts if ss<=x<=se):
        oc=src[pc];op,mode=REV[oc];dp=ds+(pc-ss)
        if mode in ('zp','zpx','zpy','indx','indy'):
            old=src[pc+1]; new=_v5_div16_zp(vals,old) if kind=='s16' else _v5_div32_zp(vals,old)
            if not(vals['ZP_MAIN']<=new<=vals['ZP_MAIN']+0x1E): raise RuntimeError('V5 signed division ZP overflow')
            dst[dp+1]=new&255
        elif mode in ('abs','absx','absy','ind'):
            old=src[pc+1]|src[pc+2]<<8;new=old
            if kind=='s16':
                if SDIV16_PREFIX_SRC[0]<=old<=SDIV16_PREFIX_SRC[1]:new=dpre+(old-SDIV16_PREFIX_SRC[0])
                elif SDIV16_CG_SRC[0]<=old<=SDIV16_CG_SRC[1]:new=dcg+(old-SDIV16_CG_SRC[0])
            else:
                if SDIV32_CG_SRC[0]<=old<=SDIV32_CG_SRC[1]:new=dcg+(old-SDIV32_CG_SRC[0])
                elif SDIV32_MX_SRC[0]<=old<=SDIV32_MX_SRC[1]:new=dmx+(old-SDIV32_MX_SRC[0])
                elif SDIV32_PREFIX_SRC[0]<=old<=SDIV32_PREFIX_SRC[1]:new=dpre+(old-SDIV32_PREFIX_SRC[0])
            if V2_REF_MATH_IO<=old<=V2_REF_MATH_IO+0x1F:new=vals['MATH_IO']+(old-V2_REF_MATH_IO)
            dst[dp+1]=new&255;dst[dp+2]=(new>>8)&255


def apply_fast_signed16_32(dst:bytearray,src:bytearray,vals:dict[str,int],base_man:dict,entries:dict[str,int],hbase:int)->dict:
    # Preserve each donor component's low-byte phase to retain branch timing.
    dcg=hbase+0x120C                         # reference $B20C
    d16=vals['REG_KERNEL']+0x1200           # reference $5200
    dmx=vals['REG_KERNEL']+0x1A00           # reference $5A00
    d32=vals['REG_KERNEL']+0x1D00           # reference $5D00
    # Both signed routines derive from the same certified UDIV16 source. Their installed
    # donor bytes differ only because their ZP/absolute relocations differ, so V5 uses
    # the SDIV16 copy as the shared canonical private engine.
    t16=trace(src,entries['MATH_SDIV16']);t32=trace(src,entries['MATH_SDIV32_16'])
    # The two donor UDIV16 cores are byte-equivalent modulo relocation, but SDIV32/16
    # enters a few internal labels that SDIV16 never reaches. Relocate the union of
    # instruction starts before sharing the SDIV16 copy, otherwise those rare paths
    # retain donor absolute targets.
    shared_starts=set(t16)
    shared_starts.update(SDIV16_CG_SRC[0]+(pc-SDIV32_CG_SRC[0])
                         for pc in t32 if SDIV32_CG_SRC[0] <= pc <= SDIV32_CG_SRC[1])
    _copy_fast_signed_component(dst,src,*SDIV16_CG_SRC,dcg,shared_starts,vals,'s16',dcg,d16)
    _copy_fast_signed_component(dst,src,*SDIV16_PREFIX_SRC,d16,t16,vals,'s16',dcg,d16)
    _copy_fast_signed_component(dst,src,*SDIV32_MX_SRC,dmx,t32,vals,'s32',dcg,d32,dmx)
    _copy_fast_signed_component(dst,src,*SDIV32_PREFIX_SRC,d32,t32,vals,'s32',dcg,d32,dmx)
    # Replace the two stable-memory adapters in their existing V1 slots.
    w16=_jmp_target(dst,_public_addr(base_man,'MATH_SDIV16'))
    w32=_jmp_target(dst,_public_addr(base_man,'MATH_SDIV32_16'))
    _copy_fast_signed_component(dst,src,*SDIV16_WRAPPER_SRC,w16,t16,vals,'s16',dcg,d16)
    _copy_fast_signed_component(dst,src,*SDIV32_WRAPPER_SRC,w32,t32,vals,'s32',dcg,d32,dmx)
    return {'shared_udiv16_core':f'{hx(dcg)}-{hx(dcg+(SDIV16_CG_SRC[1]-SDIV16_CG_SRC[0]))}',
            'sdiv16_prefix':f'{hx(d16)}-{hx(d16+(SDIV16_PREFIX_SRC[1]-SDIV16_PREFIX_SRC[0]))}',
            'sdiv32_16_mixed':f'{hx(dmx)}-{hx(dmx+(SDIV32_MX_SRC[1]-SDIV32_MX_SRC[0]))}',
            'sdiv32_16_prefix':f'{hx(d32)}-{hx(d32+(SDIV32_PREFIX_SRC[1]-SDIV32_PREFIX_SRC[0]))}',
            'unique_code_bytes':(SDIV16_CG_SRC[1]-SDIV16_CG_SRC[0]+1)+(SDIV16_PREFIX_SRC[1]-SDIV16_PREFIX_SRC[0]+1)+(SDIV32_MX_SRC[1]-SDIV32_MX_SRC[0]+1)+(SDIV32_PREFIX_SRC[1]-SDIV32_PREFIX_SRC[0]+1),
            'max_transient_zp_bytes':18}


def _map_sdiv24_addr(target: int, vals: dict[str, int], sbase: int, cbase: int, wbase: int) -> int:
    if SDIV24_PREFIX_SRC[0] <= target <= SDIV24_PREFIX_SRC[1]:
        return sbase + (target - SDIV24_PREFIX_SRC[0])
    if SDIV24_CORE_SRC[0] <= target <= SDIV24_CORE_SRC[1]:
        return cbase + (target - SDIV24_CORE_SRC[0])
    if SDIV24_WRAPPER_SRC[0] <= target <= SDIV24_WRAPPER_SRC[1]:
        return wbase + (target - SDIV24_WRAPPER_SRC[0])
    if V2_REF_MATH_IO <= target <= V2_REF_MATH_IO + 0x1F:
        return vals['MATH_IO'] + (target - V2_REF_MATH_IO)
    return target


def _relocate_sdiv24_instruction(buf: bytearray, src_mem: bytearray, src_pc: int,
                                  dst_pc: int, vals: dict[str, int], sbase: int, cbase: int, wbase: int) -> None:
    oc=src_mem[src_pc]; op,mode=REV[oc]
    if mode in ('zp','zpx','zpy','indx','indy'):
        old=src_mem[src_pc+1]
        if not (0x3E <= old <= 0x4C):
            raise RuntimeError(f'SDIV24 import unexpected ZP ${old:02X} at ${src_pc:04X}')
        new=vals['ZP_MAIN'] + 0x0A + (old-0x3E)
        if not (vals['ZP_MAIN'] <= new <= vals['ZP_MAIN']+0x1E):
            raise RuntimeError(f'SDIV24 relocated ZP outside 31-byte window at ${src_pc:04X}: ${new:02X}')
        buf[dst_pc+1]=new&0xff
    elif mode in ('abs','absx','absy','ind'):
        old=src_mem[src_pc+1]|src_mem[src_pc+2]<<8
        new=_map_sdiv24_addr(old,vals,sbase,cbase,wbase)
        buf[dst_pc+1]=new&255;buf[dst_pc+2]=(new>>8)&255


def _copy_sdiv24_block(dst: bytearray, src: bytearray, ss: int, se: int, ds: int,
                        starts: set[int], vals: dict[str,int], sbase:int,cbase:int,wbase:int) -> None:
    dst[ds:ds+(se-ss+1)]=src[ss:se+1]
    for pc in sorted(x for x in starts if ss<=x<=se):
        _relocate_sdiv24_instruction(dst,src,pc,ds+(pc-ss),vals,sbase,cbase,wbase)


def apply_sdiv24_fast(dst: bytearray, src: bytearray, vals: dict[str,int],
                       base_man: dict, donor_entries: dict[str,int]) -> dict:
    # Repack the two source islands contiguously into a V1-free table window.
    sbase=vals['REG_TABLE']+SDIV24_PRIVATE_TABLE_OFFSET
    # Preserve the donor's page phase: prefix at +$1600, magnitude core at +$1900.
    # The deliberate gap costs no occupied bytes and avoids branch-page timing penalties.
    cbase=sbase+0x0300
    end=cbase+SDIV24_CORE_BYTES-1
    # Guard the V1-derived destination before assigning V5 ownership.
    if any(dst[sbase:end+1]):
        raise RuntimeError(f'V5 SDIV24 private destination {hx(sbase)}-{hx(end)} is not free')
    starts=trace(src,donor_entries['MATH_SDIV24'])
    # Reuse the old V1 adapter slot for the direct path's output-store helper.
    # Unlike the old donor, the public API now jumps straight into the signed prefix.
    dst_public=_public_addr(base_man,'MATH_SDIV24')
    dst_wrapper=_jmp_target(dst,dst_public)
    _copy_sdiv24_block(dst,src,*SDIV24_PREFIX_SRC,sbase,starts,vals,sbase,cbase,dst_wrapper)
    _copy_sdiv24_block(dst,src,*SDIV24_CORE_SRC,cbase,starts,vals,sbase,cbase,dst_wrapper)
    _copy_sdiv24_block(dst,src,*SDIV24_WRAPPER_SRC,dst_wrapper,starts,vals,sbase,cbase,dst_wrapper)
    dst[dst_public:dst_public+3]=bytes((0x4C,sbase&0xFF,(sbase>>8)&0xFF))
    return {'private_code':f'{hx(sbase)}-{hx(end)}','private_code_bytes':SDIV24_PREFIX_BYTES+SDIV24_CORE_BYTES,
            'output_helper':f'{hx(dst_wrapper)}-{hx(dst_wrapper+(SDIV24_WRAPPER_SRC[1]-SDIV24_WRAPPER_SRC[0]))}',
            'zp':f'{hx(vals["ZP_MAIN"]+0x0A,2)}-{hx(vals["ZP_MAIN"]+0x18,2)}','zp_bytes':15}


def apply_atan2_fast(dst_mem: bytearray, src_mem: bytearray,
                     vals: dict[str, int], base_man: dict,
                     donor_entries: dict[str, int], hbase: int) -> dict:
    """Transplant the certified V2 fast ATAN2 into a V1-layout image.

    The public ABI slot stays untouched.  The V2 body is relocated into the
    existing V1 ATAN2 private slot, and its four tables occupy V1 pages that
    are empty in the canonical layout.
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
    targets = [vals['REG_TABLE'] + offset for offset in (0x0D00, 0x0E00, 0x0F00, 0x1000)]
    for a in targets:
        if any(dst_mem[a:a + 256]):
            raise RuntimeError(f'ATAN2 fast destination page {hx(a)} is not free in V1 base')

    copy_relocated_block(dst_mem, src_mem, src_body, src_end, dst_body,
                         body_starts, vals, hbase)
    # Clear the now-dead remainder of the old compact body so private address
    # geometry stays pinned while the image remains easy to audit.
    dst_mem[dst_body + length:dst_isqrt] = bytes(dst_isqrt - (dst_body + length))
    for target, source in zip(targets, (ATAN_LOGX_SRC, ATAN_LOGY_SRC, ATAN_QPOS_SRC, ATAN_QNEG_SRC)):
        dst_mem[target:target + 256] = src_mem[source[0]:source[1] + 1]
    return {
        'body': f'{hx(dst_body)}-{hx(dst_body + length - 1)}',
        'body_bytes': length,
        'extra_table_bytes': ATAN_EXTRA_TABLE_BYTES,
        'extra_table_pages': [hx(a) for a in targets],
        'logx_page': hx(targets[0]),
        'logy_page': hx(targets[1]),
        'qpos_page': hx(targets[2]),
        'qneg_page': hx(targets[3]),
    }




def _copy_direct_component(dst: bytearray, src: bytearray, ss: int, se: int, ds: int,
                           starts: set[int], vals: dict[str,int],
                           internal_ranges: list[tuple[int,int,int]],
                           zp_map=None) -> None:
    """Relocate one direct-ABI donor component into V5.

    Relative branches remain byte-identical. Absolute references into one of
    internal_ranges are rebased, public MATH_IO references follow the selected
    V5 map, and optional ZP operands are remapped by zp_map.
    """
    dst[ds:ds+(se-ss+1)] = src[ss:se+1]
    for pc in sorted(x for x in starts if ss <= x <= se):
        oc=src[pc]; op,mode=REV[oc]; dp=ds+(pc-ss)
        if mode in ('zp','zpx','zpy','indx','indy'):
            old=src[pc+1]
            if zp_map is None:
                raise RuntimeError(f'unexpected ZP operand ${old:02X} at ${pc:04X}')
            new=zp_map(old)
            if not (vals['ZP_MAIN'] <= new <= vals['ZP_MAIN']+0x1E):
                raise RuntimeError(f'direct division relocated ZP outside V5 window at ${pc:04X}: ${new:02X}')
            dst[dp+1]=new&255
        elif mode in ('abs','absx','absy','ind'):
            old=src[pc+1] | (src[pc+2]<<8); new=old
            for rs,re,rd in internal_ranges:
                if rs <= old <= re:
                    new=rd+(old-rs); break
            if V2_REF_MATH_IO <= old <= V2_REF_MATH_IO+0x1F:
                new=vals['MATH_IO']+(old-V2_REF_MATH_IO)
            dst[dp+1]=new&255; dst[dp+2]=(new>>8)&255


def apply_udiv8_direct(dst: bytearray, src: bytearray, vals: dict[str,int],
                        base_man: dict, donor_entries: dict[str,int]) -> dict:
    db=vals['REG_KERNEL']
    starts=trace(src,donor_entries['MATH_UDIV8'])
    def zmap(old:int)->int:
        if old != 0x10: raise RuntimeError(f'UDIV8 direct unexpected ZP ${old:02X}')
        return vals['ZP_MAIN']+0x0E
    _copy_direct_component(dst,src,*UDIV8_DIRECT_SRC,db,starts,vals,
                           [(UDIV8_DIRECT_SRC[0],UDIV8_DIRECT_SRC[1],db)],zmap)
    entry=db+(0x4008-UDIV8_DIRECT_SRC[0])
    a=_public_addr(base_man,'MATH_UDIV8'); dst[a:a+3]=bytes((0x4C,entry&255,entry>>8))
    return {'private_code':f'{hx(db)}-{hx(db+(UDIV8_DIRECT_SRC[1]-UDIV8_DIRECT_SRC[0]))}',
            'zp':hx(vals['ZP_MAIN']+0x0E,2),'zp_bytes':1}


def apply_udiv16_direct(dst: bytearray, src: bytearray, vals: dict[str,int],
                         base_man: dict, donor_entries: dict[str,int], hbase:int) -> dict:
    # Put the 1,482-byte direct public-ABI UDIV16 engine in the high end of the
    # private hybrid region. It uses no ZP scratch.
    db=hbase+0x1800
    starts=trace(src,donor_entries['MATH_UDIV16'])
    _copy_direct_component(dst,src,*UDIV16_DIRECT_SRC,db,starts,vals,
                           [(UDIV16_DIRECT_SRC[0],UDIV16_DIRECT_SRC[1],db)])
    for name in ('MATH_UDIV16','MATH_UMOD16'):
        a=_public_addr(base_man,name); dst[a:a+3]=bytes((0x4C,db&255,db>>8))
    return {'private_code':f'{hx(db)}-{hx(db+(UDIV16_DIRECT_SRC[1]-UDIV16_DIRECT_SRC[0]))}',
            'private_code_bytes':UDIV16_DIRECT_SRC[1]-UDIV16_DIRECT_SRC[0]+1,'zp_bytes':0}


def apply_sdiv16_direct(dst: bytearray, src: bytearray, vals: dict[str,int],
                         base_man: dict, donor_entries: dict[str,int], hbase:int) -> dict:
    # Preserve the signed front-end page phase in a V1-free table page; place the
    # larger direct-output magnitude engine in private hybrid RAM.
    pbase=vals['REG_TABLE']+0x1400
    cbase=hbase+0x1200
    starts=trace(src,donor_entries['MATH_SDIV16'])
    def zmap(old:int)->int:
        if not (0x10 <= old <= 0x15): raise RuntimeError(f'SDIV16 direct unexpected ZP ${old:02X}')
        return vals['ZP_MAIN']+0x0E+(old-0x10)
    ranges=[(SDIV16_DIRECT_PREFIX_SRC[0],SDIV16_DIRECT_PREFIX_SRC[1],pbase),
            (SDIV16_DIRECT_CORE_SRC[0],SDIV16_DIRECT_CORE_SRC[1],cbase)]
    _copy_direct_component(dst,src,*SDIV16_DIRECT_PREFIX_SRC,pbase,starts,vals,ranges,zmap)
    _copy_direct_component(dst,src,*SDIV16_DIRECT_CORE_SRC,cbase,starts,vals,ranges,zmap)
    for name in ('MATH_SDIV16','MATH_SMOD16'):
        a=_public_addr(base_man,name); dst[a:a+3]=bytes((0x4C,pbase&255,pbase>>8))
    return {'prefix':f'{hx(pbase)}-{hx(pbase+(SDIV16_DIRECT_PREFIX_SRC[1]-SDIV16_DIRECT_PREFIX_SRC[0]))}',
            'private_core':f'{hx(cbase)}-{hx(cbase+(SDIV16_DIRECT_CORE_SRC[1]-SDIV16_DIRECT_CORE_SRC[0]))}',
            'zp':f'{hx(vals["ZP_MAIN"]+0x0E,2)}-{hx(vals["ZP_MAIN"]+0x13,2)}','zp_bytes':6}


def apply_sdiv24_direct(dst: bytearray, src: bytearray, vals: dict[str,int],
                         base_man: dict, donor_entries: dict[str,int]) -> dict:
    # The V1 table map has a 3.2 KiB free run here. Keep the donor low-byte phase
    # for both islands so branch page-cross behaviour is preserved exactly.
    pbase=vals['REG_TABLE']+0x1678
    cbase=vals['REG_TABLE']+0x19EE
    starts=trace(src,donor_entries['MATH_SDIV24'])
    def zmap(old:int)->int:
        if not (0x10 <= old <= 0x18): raise RuntimeError(f'SDIV24 direct unexpected ZP ${old:02X}')
        return vals['ZP_MAIN']+0x0E+(old-0x10)
    ranges=[(SDIV24_DIRECT_PREFIX_SRC[0],SDIV24_DIRECT_PREFIX_SRC[1],pbase),
            (SDIV24_DIRECT_CORE_SRC[0],SDIV24_DIRECT_CORE_SRC[1],cbase)]
    # Guard the selected V1-free destinations.
    for ds,se,ss in ((pbase,SDIV24_DIRECT_PREFIX_SRC[1],SDIV24_DIRECT_PREFIX_SRC[0]),
                     (cbase,SDIV24_DIRECT_CORE_SRC[1],SDIV24_DIRECT_CORE_SRC[0])):
        n=se-ss+1
        if any(dst[ds:ds+n]): raise RuntimeError(f'V5 direct SDIV24 destination {hx(ds)}-{hx(ds+n-1)} is not free')
    _copy_direct_component(dst,src,*SDIV24_DIRECT_PREFIX_SRC,pbase,starts,vals,ranges,zmap)
    _copy_direct_component(dst,src,*SDIV24_DIRECT_CORE_SRC,cbase,starts,vals,ranges,zmap)
    for name in ('MATH_SDIV24','MATH_SMOD24'):
        a=_public_addr(base_man,name); dst[a:a+3]=bytes((0x4C,pbase&255,pbase>>8))
    return {'prefix':f'{hx(pbase)}-{hx(pbase+(SDIV24_DIRECT_PREFIX_SRC[1]-SDIV24_DIRECT_PREFIX_SRC[0]))}',
            'private_core':f'{hx(cbase)}-{hx(cbase+(SDIV24_DIRECT_CORE_SRC[1]-SDIV24_DIRECT_CORE_SRC[0]))}',
            'zp':f'{hx(vals["ZP_MAIN"]+0x0E,2)}-{hx(vals["ZP_MAIN"]+0x16,2)}','zp_bytes':9}

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
    # V5 intentionally inherits the V1 normalization backend.  Publish a
    # profile-local standalone source, but require it to remain byte-identical
    # to the V1 canonical source so users can lift either copy safely.
    v1_norm = ROOT/'v1_balanced/resident/vector/native/vec2_normalize_q8_8.asm'
    v5_norm = ROOT/'v5_hybrid_lowzp/resident/vector/native/vec2_normalize_q8_8.asm'
    if v1_norm.read_bytes() != v5_norm.read_bytes():
        raise RuntimeError('V5 normalize native source drifted from inherited V1 backend')
    v5_tables = v5_norm.with_name('vec2_normalize_tables.asm')
    if v1_norm.with_name('vec2_normalize_tables.asm').read_bytes() != v5_tables.read_bytes():
        raise RuntimeError('V5 normalize tables drifted from inherited V1 backend')
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
        udiv8_detail = apply_udiv8_direct(dst, src, vals, v1man, entries)
        udiv16_detail = apply_udiv16_direct(dst, src, vals, v1man, entries, hbase)
        sdiv16_detail = apply_sdiv16_direct(dst, src, vals, v1man, entries, hbase)
        sdiv24_detail = apply_sdiv24_direct(dst, src, vals, v1man, entries)
        selected_trace: set[int] = set()
        for name in ('MATH_UDIV24', 'MATH_UDIV32_16', 'MATH_UMOD8'):
            selected_trace |= trace(src, entries[name])
        cos_trace = trace(src, entries['MATH_COS8'])
        sincos_trace = trace(src, entries['MATH_SINCOS8'])

        # Private code/data imports.
        copy_relocated_block(dst, src, DIV_SRC[0], DIV_SRC[1], hbase,
                             selected_trace, vals, hbase)
        copy_relocated_block(dst, src, UMOD8_SRC[0], UMOD8_SRC[1], hbase + 0x1000,
                             selected_trace, vals, hbase)
        # The current V2 UDIV24 is a direct-ABI JMP into the copied $4800 island.
        # Patch both quotient and modulo public entries to that relocated core.
        u24_target=hbase+(0x4816-DIV_SRC[0])
        for name in ('MATH_UDIV24','MATH_UMOD24'):
            a=_public_addr(v1man,name); dst[a:a+3]=bytes((0x4C,u24_target&255,u24_target>>8))
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
            'udiv8_direct': udiv8_detail,
            'udiv16_direct': udiv16_detail,
            'sdiv16_direct': sdiv16_detail,
            'sdiv24_direct': sdiv24_detail,
            'indirect_beneficiaries': [
                'MATH_UDIV16_SHL8',
                'MATH_URECIP16_Q16',
            ],
            'notes': [
                'All 46 stable API addresses and semantics remain V1-compatible.',
                'MATH_INIT remains optional exactly as in V1.',
                'The imported certified V2 kernels use only the existing V1 normal ZP window.',
                'Fast ATAN2, when enabled, adds no ZP and occupies four formerly empty V1 table pages (1024 bytes).',
                'V2 direct UDIV8 replaces the V1 256-class core in place; V2 direct UDIV16 is repacked into private hybrid RAM; UDIV24 uses the copied Repose direct core.',
                'V2 direct-output SDIV16 and SDIV24 are repacked into V1-free code/table windows and stay wholly inside the normal 31-byte ZP contract.',
                'SDIV32/16 remains the refreshed V1 low-ZP direct implementation in V5; UDIV32/16 retains the faster V2 hybrid import.',
                'HYBRID_CODE is private implementation storage and may be relocated at build time.',
                'Reference HYBRID_CODE=$A000 lives under BASIC ROM; RAM must be visible while executing imported routines.',
            ],
            'source_inputs': {
                'v1_source_sha256': hashlib.sha256((ROOT/'relocatable_source/v1_balanced/math_relocatable.asm').read_bytes()).hexdigest(),
                'v2_source_sha256': hashlib.sha256((ROOT/'relocatable_source/v2_pareto_fast/math_relocatable.asm').read_bytes()).hexdigest(),
                'normalize_native_sha256': hashlib.sha256(v5_norm.read_bytes()).hexdigest(),
                'normalize_tables_sha256': hashlib.sha256(v5_tables.read_bytes()).hexdigest(),
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
