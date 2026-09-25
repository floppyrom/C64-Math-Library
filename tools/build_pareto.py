#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import argparse, csv, hashlib, itertools, json, math, shutil, sys, tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

from mini6502 import REV, SIZE
import assemble_sources as asm
import source_relocation as sr
import build_hybrid as hy

PROFILE = 'custom_pareto'
BASE_ZP_BYTES = 31
FULL_V2_ZP_BYTES = 221
# Native V2 resource islands at reference ZP_MAIN=$02.
PACKS = {
    'zero_zp_v5': {
        'extra_zp': 0,
        'extra_ram': hy.HYBRID_BYTES + 929,
        'requires_init': False,
        'description': 'Current V5 zero-extra-ZP division/modulo/COS/SINCOS imports, including direct-output signed division refresh',
        'savings': {
            'MATH_UDIV16': 22.782698, 'MATH_UDIV24': 21.055405,
            'MATH_UDIV32_16': 97.642282, 'MATH_UMOD8': 0.466003,
            'MATH_UMOD16': 22.782698, 'MATH_UMOD24': 21.055405,
            'MATH_UMOD32_16': 97.642282, 'MATH_COS8': 6.0,
            'MATH_SINCOS8': 8.0,
        },
    },
    'atan2_fast': {
        'extra_zp': 0,
        'extra_ram': hy.ATAN_EXTRA_TABLE_BYTES,
        'requires_init': False,
        'description': 'V2 sum-fast ATAN2 body using four V1-free table pages',
        'savings': {
            'MATH_ATAN2_8': 3.484375,
        },
    },
    'umul32_initialized': {
        'extra_zp': 0,
        'extra_ram': 627,
        'requires_init': True,
        'description': 'Retired compatibility catalog entry: V1 already carries the refreshed FAST31/V29 UMUL32/SMUL32 family, so importing the V2 copy has no useful fixed-profile gain',
        'savings': {},
        'retired': True,
    },
    'umul8_16': {
        # Historical pack name retained for CLI/config compatibility.  It now
        # carries only the V2 UMUL8 island; UMUL16 moved into the UMUL24
        # pack because the record UMUL16 reuses the first 17 bytes of UMUL24's
        # 24-byte pointer workspace.
        'extra_zp': 5,
        'extra_ram': 547,
        'requires_init': True,
        'description': 'V2 UMUL8 island; SMUL8 is already the refreshed direct-signed kernel in the V1 base (legacy pack name)',
        'savings': {
            'MATH_UMUL8': 12.000030,
        },
    },
    'umul24': {
        # $21-$38: twelve complete pointer pairs.  The record UMUL16 uses the
        # first 17 bytes ($21-$31), so no additional ZP is required for it.
        'extra_zp': 24,
        'extra_ram': 911,
        'requires_init': True,
        'description': 'Record 17-ZP UMUL16 + record 24-ZP UMUL24 + refreshed V2 FAST24 native-signed SMUL24 core; shared quarter-square tables',
        'savings': {
            'MATH_UMUL16': 32.000000, 'MATH_UMUL16_SHR8': 32.000000,
            'MATH_UMUL24': 44.000000, 'MATH_SMUL24': 41.750363,
        },
    },
    'smul16_exec': {
        'extra_zp': 116,
        'extra_ram': 176,
        'requires_init': True,
        'description': 'V2 native executable-ZP SMUL16 core ($80-$F3 by default); reuses V1 quarter-square tables',
        'savings': {
            'MATH_SMUL16': 171.545047, 'MATH_SMUL16_SHR8': 171.0,
        },
    },
}

AUX_DIFF_LO = 0x000
AUX_DIFF_HI = 0x100
AUX_UMUL8_CODE = 0x200
AUX_UMUL16_CODE = 0x240
# Preserve the certified V2 UMUL24 donor's low-byte/page geometry.
# The record core starts at $5649 and its ABI adapter at $34C0; keeping
# those low bytes avoids operand-dependent branch page-cross penalties.
AUX_UMUL24_CODE = 0x349
AUX_UMUL24_ADAPTER = 0x4C0
AUX_UMUL32_CODE = 0x500
AUX_UMUL32_ADAPTER = 0x620
AUX_SMUL_FINISH = 0x700
AUX_SMUL_IMAGE = 0x780
AUX_INIT = 0x800
# Private native-signed executable cores carried with packs that upgrade the matching signed path.
AUX_SMUL8_PRIVATE = 0x900
AUX_SMUL24_PRIVATE = 0xA00
AUX_SMUL32_PRIVATE = 0xC00
AUX_BYTES = 0x0E00


def hx(v: int, w: int = 4) -> str:
    return f'${v:0{w}X}'


def unhx(v):
    if isinstance(v, str) and v.startswith('$'):
        return int(v[1:], 16)
    return int(v)


def load_prg(path: Path) -> tuple[bytearray, int, int]:
    b = path.read_bytes(); lo = b[0] | (b[1] << 8); hi = lo + len(b) - 3
    mem = bytearray(65536); mem[lo:hi+1] = b[2:]
    return mem, lo, hi


def write_prg(mem: bytearray, lo: int, hi: int, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes((lo & 255, lo >> 8)) + bytes(mem[lo:hi+1]))


def trace(mem: bytearray, start: int) -> set[int]:
    todo=[start]; seen=set()
    while todo:
        pc=todo.pop() & 0xffff
        if pc in seen: continue
        oc=mem[pc]
        if oc not in REV:
            raise RuntimeError(f'untraceable opcode {oc:02X} at {pc:04X}')
        seen.add(pc); op,mode=REV[oc]; nxt=(pc+SIZE[mode])&0xffff
        if op in ('rts','rti','brk'): continue
        if mode=='rel':
            d=mem[pc+1]; d=d-256 if d>=128 else d
            todo.extend((nxt,(nxt+d)&0xffff)); continue
        if op=='jmp':
            if mode=='abs': todo.append(mem[pc+1] | (mem[pc+2]<<8))
            continue
        if op=='jsr':
            todo.extend((mem[pc+1] | (mem[pc+2]<<8),nxt)); continue
        todo.append(nxt)
    return seen


def validate_custom_config(vals: dict, packs: set[str]):
    asm.validate_config('v1_balanced', vals)
    z0=vals['ZP_MAIN']; zbase=(z0,z0+0x1e)
    if zbase[1] > 0xff: raise ValueError('base V1 ZP window exceeds page zero')
    ranges=[('V1_ZP',*zbase)]
    if 'umul24' in packs: ranges.append(('UMUL24_ZP',z0+0x1f,z0+0x36))  # ref $21-$38
    if 'umul8_16' in packs: ranges.append(('UMUL8_16_ZP',z0+0x37,z0+0x3b)) # ref $39-$3D
    if 'smul16_exec' in packs:
        s=vals['ZP_SMUL']; ranges.append(('SMUL16_EXEC_ZP',s,s+0x73))
    for n,a,b in ranges:
        if a<2 or b>0xff: raise ValueError(f'{n} {hx(a,2)}-{hx(b,2)} is outside usable ZP')
    for i,(n,a,b) in enumerate(ranges):
        for n2,a2,b2 in ranges[i+1:]:
            if max(a,a2)<=min(b,b2): raise ValueError(f'ZP overlap: {n} with {n2}')
    aux=vals['PARETO_AUX']; ae=aux+AUX_BYTES-1
    if ae>0xffff or max(aux,0xd000)<=min(ae,0xdfff): raise ValueError('PARETO_AUX invalid/crosses I/O')
    claims=asm.validate_config('v1_balanced', vals)
    # PARETO_AUX is a private generated-code region; it must not collide with V1 claims.
    for name,start,end,space in claims:
        if space=='main' and max(aux,start)<=min(ae,end):
            raise ValueError(f'PARETO_AUX {hx(aux)}-{hx(ae)} collides with {name} {hx(start)}-{hx(end)}')
    if 'HYBRID_CODE' in vals:
        hb=vals['HYBRID_CODE']; he=hb+hy.HYBRID_BYTES-1
        if max(aux,hb)<=min(ae,he): raise ValueError('PARETO_AUX overlaps HYBRID_CODE')
    if 'zero_zp_v5' in packs:
        if 'HYBRID_CODE' not in vals: raise ValueError('zero_zp_v5 requires HYBRID_CODE')
        hy.validate_hybrid_region(vals, vals['HYBRID_CODE'])
    return ranges


def init_helper_length(packs: set[str]) -> int:
    """Exact generated MATH_INIT helper length for a selected pack set.

    Any pack that requires initialization also preserves V1's READY-entry setup by
    installing the six persistent UMUL32 pointer-high bytes. Optional pack-specific
    initialization is then appended.
    """
    if not any(PACKS[p]['requires_init'] for p in packs):
        return 0
    n = 18  # two LDA immediates + six STA zp + CLC/RTS
    if 'umul24' in packs:
        n += 32  # four table-page loads, three pointer-high stores each
    if 'umul8_16' in packs:
        n += 8   # two table-page loads + two pointer-high stores
    if 'smul16_exec' in packs:
        n += 10  # copy-loop setup/body for the 116-byte executable-ZP image
    return n


def exact_extra_ram_bytes(packs: set[str]) -> int:
    return sum(PACKS[p]['extra_ram'] for p in packs) + init_helper_length(packs)


def score_packs(packs: set[str], weights: dict[str,float]) -> float:
    s=0.0
    for p in packs:
        for routine,save in PACKS[p]['savings'].items():
            s += save * weights.get(routine, 1.0)
    return s


def select_packs(zp_budget: int, ram_budget: int | None, init_policy: str,
                 weights: dict[str,float]) -> dict:
    if zp_budget < BASE_ZP_BYTES:
        raise ValueError(f'ZP budget {zp_budget} is below the 31-byte V1 minimum')
    # Full V2 dominates the hybrid catalog once its complete 221-byte union fits.
    if zp_budget >= FULL_V2_ZP_BYTES and init_policy != 'optional' and (ram_budget is None or ram_budget >= 208):
        return {'mode':'v2_full','packs':[], 'zp_bytes':FULL_V2_ZP_BYTES,
                'extra_ram':208, 'score':math.inf, 'init_required':True}
    names=[n for n,v in PACKS.items() if not v.get('retired',False)]
    best=None
    for bits in itertools.product((0,1), repeat=len(names)):
        chosen={n for n,b in zip(names,bits) if b}
        if init_policy=='optional' and any(PACKS[p]['requires_init'] for p in chosen):
            continue
        zp=BASE_ZP_BYTES + sum(PACKS[p]['extra_zp'] for p in chosen)
        ram=exact_extra_ram_bytes(chosen)
        if zp>zp_budget: continue
        if ram_budget is not None and ram>ram_budget: continue
        sc=score_packs(chosen,weights)
        # Prefer higher score, then lower ZP, then lower exact private RAM, then more packs for deterministic tie-breaking.
        key=(sc,-zp,-ram,len(chosen))
        if best is None or key>best[0]:
            best=(key,chosen,zp,ram)
    if best is None: raise ValueError('no certified build fits the requested budgets/policy')
    _,chosen,zp,ram=best
    return {'mode':'hybrid','packs':sorted(chosen), 'zp_bytes':zp, 'extra_ram':ram,
            'score':score_packs(chosen,weights),
            'init_required':any(PACKS[p]['requires_init'] for p in chosen)}


def map_v2_abs(old: int, vals: dict, aux: int, pack: str|None=None) -> int:
    # Public I/O / configured stable regions.
    if 0xC000 <= old <= 0xC01F: return vals['MATH_IO'] + old-0xC000
    # V2->V1 table mappings; the data are byte-identical in the release.
    maps={
        0x6000: vals['REG_TABLE']+0x2400, 0x6200: vals['REG_TABLE']+0x2600,
        0x6400: vals['REG_TABLE']+0x2800, 0x6600: vals['REG_TABLE']+0x2A00,
        0x6800: vals['REG_TABLE']+0x2000, 0x6A00: vals['REG_TABLE']+0x2200,
        0x6C00: aux+AUX_DIFF_LO, 0x6D00: aux+AUX_DIFF_HI,
        0x7000: vals['REG_TABLE']+0x2C00, 0x7200: vals['REG_TABLE']+0x2E00,
        0x7400: vals['REG_TABLE']+0x3000, 0x7600: vals['REG_TABLE']+0x3200,
        # Native SMUL16 uses the same four quarter-square planes as V1 UMUL24.
        0x2800: vals['REG_TABLE']+0x2400, 0x2A00: vals['REG_TABLE']+0x2600,
        0x2C00: vals['REG_TABLE']+0x2800, 0x2E00: vals['REG_TABLE']+0x2A00,
    }
    for src,dst in maps.items():
        # 511-byte planes except the two 256-byte diff planes.
        ln=256 if src in (0x6C00,0x6D00) else 511
        if src <= old < src+ln: return dst+(old-src)
    # Pack code locations.
    if 0x5300 <= old <= 0x5322: return aux+AUX_UMUL8_CODE+(old-0x5300)
    if 0x53EC <= old <= 0x5457: return aux+AUX_UMUL16_CODE+(old-0x53EC)
    if 0x5649 <= old <= 0x575A: return aux+AUX_UMUL24_CODE+(old-0x5649)
    if 0x34C0 <= old <= 0x3505: return aux+AUX_UMUL24_ADAPTER+(old-0x34C0)
    if 0x5800 <= old <= 0x5912: return aux+AUX_UMUL32_CODE+(old-0x5800)
    if 0x3420 <= old <= 0x346A: return aux+AUX_UMUL32_ADAPTER+(old-0x3420)
    if 0x5A00 <= old <= 0x5A3B: return aux+AUX_SMUL_FINISH+(old-0x5A00)
    # Native-signed private executable cores in the refreshed V2 donor.
    if 0x2600 <= old <= 0x2622: return aux+AUX_SMUL8_PRIVATE+(old-0x2600)
    if 0xCD00 <= old <= 0xCED5: return aux+AUX_SMUL24_PRIVATE+(old-0xCD00)
    if 0x3800 <= old <= 0x3914: return aux+AUX_SMUL32_PRIVATE+(old-0x3800)
    # Signed producer wrappers live at the same REG_LOW-relative offsets in V1.
    if 0x2000 <= old <= 0x23FF: return vals['REG_LOW']+0x1000+(old-0x2000)
    return old


def map_v2_zp(old: int, vals: dict, smul: bool=False) -> int:
    if smul and 0x80 <= old <= 0xF3:
        return vals['ZP_SMUL'] + (old-0x80)
    # V2 ZP_MAIN reference base is $02; preserve offsets so pointer-pair geometry is exact.
    if 0x02 <= old <= 0x6A:
        return vals['ZP_MAIN'] + (old-0x02)
    return old


def relocate_instruction(dst: bytearray, src: bytearray, spc: int, dpc: int,
                         vals: dict, aux: int, smul: bool=False):
    oc=src[spc]; op,mode=REV[oc]
    if mode in ('zp','zpx','zpy','indx','indy'):
        old=src[spc+1]; new=map_v2_zp(old,vals,smul)
        if not 0<=new<=255: raise ValueError(f'ZP relocation overflow {old:02X}->{new:04X}')
        dst[dpc+1]=new
    elif mode in ('abs','absx','absy','ind'):
        old=src[spc+1] | (src[spc+2]<<8)
        # An absolute JSR/JMP into executable ZP needs SMUL-base relocation.
        if smul and 0x80 <= old <= 0xF3: new=vals['ZP_SMUL']+(old-0x80)
        else: new=map_v2_abs(old,vals,aux)
        dst[dpc+1]=new&255; dst[dpc+2]=(new>>8)&255


def copy_code_block(dst,src,ss,se,ds,starts,vals,aux,smul=False):
    dst[ds:ds+(se-ss+1)] = src[ss:se+1]
    for spc in sorted(p for p in starts if ss<=p<=se):
        relocate_instruction(dst,src,spc,ds+(spc-ss),vals,aux,smul)


def public_addr(man,name): return unhx(man['public_entries'][name])


def write_jmp(mem,at,target): mem[at:at+3]=bytes((0x4c,target&255,(target>>8)&255))


def emit_init(mem: bytearray, at: int, vals: dict, packs: set[str], aux: int):
    helper=aux+AUX_INIT; write_jmp(mem,at,helper)
    b=[]
    def lda_imm(v): b.extend((0xA9,v&255))
    def sta_zp(a): b.extend((0x85,a&255))
    # V1/V2 UMUL32 pointer highs, mapped to the V1 table planes.
    lda_imm((vals['REG_TABLE']+0x3000)>>8)
    for off in (0x01,0x05,0x09): sta_zp(vals['ZP_MAIN']+off)
    lda_imm((vals['REG_TABLE']+0x2E00)>>8)
    for off in (0x03,0x07,0x0B): sta_zp(vals['ZP_MAIN']+off)
    if 'umul24' in packs:
        # Record UMUL16/24 pointer layout.  Relative to V2's ZP_MAIN=$02:
        # SL -> $22,$2A,$32; NL -> $24,$2C,$34;
        # SH -> $26,$2E,$36; NH -> $28,$30,$38.
        for page,offs in [((vals['REG_TABLE']+0x2400)>>8,(0x20,0x28,0x30)),
                          ((vals['REG_TABLE']+0x2800)>>8,(0x22,0x2A,0x32)),
                          ((vals['REG_TABLE']+0x2600)>>8,(0x24,0x2C,0x34)),
                          ((vals['REG_TABLE']+0x2A00)>>8,(0x26,0x2E,0x36))]:
            lda_imm(page)
            for off in offs: sta_zp(vals['ZP_MAIN']+off)
    if 'umul8_16' in packs:
        lda_imm((vals['REG_TABLE']+0x2000)>>8); sta_zp(vals['ZP_MAIN']+0x38)
        lda_imm((vals['REG_TABLE']+0x2200)>>8); sta_zp(vals['ZP_MAIN']+0x3A)
    if 'smul16_exec' in packs:
        # LDX #$73 / loop LDA image,X ; STA ZP_SMUL,X ; DEX ; BPL loop
        b.extend((0xA2,0x73,0xBD,(aux+AUX_SMUL_IMAGE)&255,(aux+AUX_SMUL_IMAGE)>>8,
                  0x95,vals['ZP_SMUL']&255,0xCA,0x10,0xF8))
    b.extend((0x18,0x60))
    expected = init_helper_length(packs)
    if len(b) != expected:
        raise RuntimeError(f'generated init helper length {len(b)} != accounted length {expected}')
    if len(b) > AUX_BYTES-AUX_INIT:
        raise RuntimeError('generated init helper exceeds AUX allocation')
    mem[helper:helper+len(b)]=bytes(b)
    return helper,len(b)


def apply_umul8_16(dst, src, vals, man, aux, v2_entries):
    # Historical function/pack name retained for compatibility.  This island now
    # carries only UMUL8; record UMUL16 travels with UMUL24 because it
    # shares that pack's first 17 bytes of pointer workspace.
    dst[aux+AUX_DIFF_LO:aux+AUX_DIFF_LO+256]=src[0x6C00:0x6D00]
    dst[aux+AUX_DIFF_HI:aux+AUX_DIFF_HI+256]=src[0x6D00:0x6E00]
    starts=trace(src,v2_entries['MATH_UMUL8'])
    copy_code_block(dst,src,0x5300,0x5322,aux+AUX_UMUL8_CODE,starts,vals,aux)
    copy_code_block(dst,src,0x3000,0x3012,public_addr(man,'MATH_UMUL8'),starts,vals,aux)
    # MATH_SMUL8 is intentionally left on the V1 base: all fixed profiles now
    # share the same 67.992188-cycle direct signed-domain kernel.


def apply_umul24(dst,src,vals,man,aux,v2_entries):
    # Record UMUL16.  Its runtime core is $53EC-$5457; the following $5458-$5470
    # is the standalone candidate's init helper and is deliberately replaced by
    # the generated Pareto MATH_INIT helper.
    u16starts=trace(src,v2_entries['MATH_UMUL16'])
    copy_code_block(dst,src,0x53EC,0x5457,aux+AUX_UMUL16_CODE,u16starts,vals,aux)
    copy_code_block(dst,src,0x3020,0x3045,public_addr(man,'MATH_UMUL16'),u16starts,vals,aux)

    # Record UMUL24.  Likewise omit its dead standalone init tail $575B-$577B.
    starts=trace(src,v2_entries['MATH_UMUL24'])
    copy_code_block(dst,src,0x5649,0x575A,aux+AUX_UMUL24_CODE,starts,vals,aux)
    copy_code_block(dst,src,0x34C0,0x34FA,aux+AUX_UMUL24_ADAPTER,starts,vals,aux)
    write_jmp(dst,public_addr(man,'MATH_UMUL24'),aux+AUX_UMUL24_ADAPTER)
    # Refreshed FAST24 native-signed core. The current V2 implementation is a
    # single private island at $CD00-$CED5 plus a 3-byte public trampoline.
    # Copy the private island and point the stable custom-profile entry directly
    # at the relocated public implementation ($CE9B in the V2 reference map).
    sstarts=trace(src,v2_entries['MATH_SMUL24'])
    copy_code_block(dst,src,0xCD00,0xCED5,aux+AUX_SMUL24_PRIVATE,sstarts,vals,aux)
    write_jmp(dst,public_addr(man,'MATH_SMUL24'),aux+AUX_SMUL24_PRIVATE+(0xCE9B-0xCD00))


def apply_umul32(dst,src,vals,man,aux,v2_entries):
    starts=trace(src,v2_entries['MATH_UMUL32'])
    copy_code_block(dst,src,0x5800,0x5912,aux+AUX_UMUL32_CODE,starts,vals,aux)
    copy_code_block(dst,src,0x3420,0x346A,aux+AUX_UMUL32_ADAPTER,starts,vals,aux)
    for n in ('MATH_UMUL32','MATH_UMUL32_READY'):
        write_jmp(dst,public_addr(man,n),aux+AUX_UMUL32_ADAPTER)
    sstarts=trace(src,v2_entries['MATH_SMUL32'])
    copy_code_block(dst,src,0x3800,0x3914,aux+AUX_SMUL32_PRIVATE,sstarts,vals,aux)
    copy_code_block(dst,src,0x2300,0x23A1,vals['REG_LOW']+0x1300,sstarts,vals,aux)
    for n in ('MATH_SMUL32','MATH_SMUL32_READY'):
        write_jmp(dst,public_addr(man,n),vals['REG_LOW']+0x1300)


def apply_smul16(dst,src_raw,src_init,vals,man,aux,v2_entries):
    # Low public adapter.
    starts=trace(src_init,v2_entries['MATH_SMUL16'])
    copy_code_block(dst,src_raw,0x2100,0x2126,vals['REG_LOW']+0x1100,starts,vals,aux,smul=True)
    write_jmp(dst,public_addr(man,'MATH_SMUL16'),vals['REG_LOW']+0x1100)
    # Shared finish routine.
    copy_code_block(dst,src_raw,0x5A00,0x5A3B,aux+AUX_SMUL_FINISH,starts,vals,aux,smul=True)
    # Start from the source image and relocate instructions according to the initialized executable-ZP trace.
    image=bytearray(src_raw[0xCC00:0xCC74]); dst[aux+AUX_SMUL_IMAGE:aux+AUX_SMUL_IMAGE+0x74]=image
    zstarts=trace(src_init,0x80)
    for spc in sorted(p for p in zstarts if 0x80<=p<=0xF3):
        dpc=aux+AUX_SMUL_IMAGE+(spc-0x80)
        relocate_instruction(dst,src_init,spc,dpc,vals,aux,smul=True)


def private_ram_ranges(vals: dict, packs: set[str], aux: int, init_len: int | None):
    """Return exact extra main-RAM regions owned by the generated hybrid.

    --ram-budget is enforced against the exact selected private payload, including
    the exact emitted initialization helper length. The manifest also reports each
    owned range separately so applications can place/bank those regions deliberately.
    """
    rr=[]
    def add(name,start,end):
        rr.append({'name':name,'start':hx(start),'end':hx(end),'bytes':end-start+1})
    if 'atan2_fast' in packs:
        add('ATAN2_LOGX_TABLE', vals['REG_TABLE']+0x0D00, vals['REG_TABLE']+0x0DFF)
        add('ATAN2_LOGY_TABLE', vals['REG_TABLE']+0x0E00, vals['REG_TABLE']+0x0EFF)
        add('ATAN2_QPOS_TABLE', vals['REG_TABLE']+0x0F00, vals['REG_TABLE']+0x0FFF)
        add('ATAN2_QNEG_TABLE', vals['REG_TABLE']+0x1000, vals['REG_TABLE']+0x10FF)
    if 'zero_zp_v5' in packs:
        add('V5_HYBRID_CODE', vals['HYBRID_CODE'], vals['HYBRID_CODE']+hy.HYBRID_BYTES-1)
        add('V5_SDIV16_PREFIX', vals['REG_TABLE']+0x1400, vals['REG_TABLE']+0x162A)
        add('V5_SDIV24_PREFIX', vals['REG_TABLE']+0x1678, vals['REG_TABLE']+0x17ED)
    if 'umul8_16' in packs:
        add('PARETO_DIFF_LO', aux+AUX_DIFF_LO, aux+AUX_DIFF_LO+0xff)
        add('PARETO_DIFF_HI', aux+AUX_DIFF_HI, aux+AUX_DIFF_HI+0xff)
        add('PARETO_UMUL8_CODE', aux+AUX_UMUL8_CODE, aux+AUX_UMUL8_CODE+0x22)
    if 'umul24' in packs:
        add('PARETO_UMUL16_CODE', aux+AUX_UMUL16_CODE, aux+AUX_UMUL16_CODE+0x6b)
        add('PARETO_UMUL24_CODE', aux+AUX_UMUL24_CODE, aux+AUX_UMUL24_CODE+0x111)
        add('PARETO_UMUL24_ADAPTER', aux+AUX_UMUL24_ADAPTER, aux+AUX_UMUL24_ADAPTER+0x3a)
        add('PARETO_SMUL24_PRIVATE', aux+AUX_SMUL24_PRIVATE, aux+AUX_SMUL24_PRIVATE+0x1d5)
    if 'umul32_initialized' in packs:
        add('PARETO_UMUL32_CODE', aux+AUX_UMUL32_CODE, aux+AUX_UMUL32_CODE+0x112)
        add('PARETO_UMUL32_ADAPTER', aux+AUX_UMUL32_ADAPTER, aux+AUX_UMUL32_ADAPTER+0x4a)
        add('PARETO_SMUL32_PRIVATE', aux+AUX_SMUL32_PRIVATE, aux+AUX_SMUL32_PRIVATE+0x114)
    if 'smul16_exec' in packs:
        add('PARETO_SMUL16_FINISH', aux+AUX_SMUL_FINISH, aux+AUX_SMUL_FINISH+0x3b)
        add('PARETO_SMUL16_IMAGE', aux+AUX_SMUL_IMAGE, aux+AUX_SMUL_IMAGE+0x73)
    if init_len:
        add('PARETO_INIT_HELPER', aux+AUX_INIT, aux+AUX_INIT+init_len-1)
    return rr


def build_hybrid_custom(config: Path, outdir: Path, selection: dict) -> dict:
    packs=set(selection['packs']); vals=asm.parse_config(config); ranges=validate_custom_config(vals,packs)
    aux=vals['PARETO_AUX']; outdir.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='c64_math_pareto_') as td:
        td=Path(td)
        if 'zero_zp_v5' in packs:
            bdir=td/'base_hybrid'; base_man=hy.build(config,bdir,include_atan2_fast=('atan2_fast' in packs)); base_prg=bdir/base_man['output_prg']
        else:
            bdir=td/'base_v1'; base_man=asm.build('v1_balanced',config,bdir); base_prg=bdir/base_man['output_prg']
        dst,lo,hi=load_prg(base_prg)
        # Fresh source-built V2 donor at reference map.
        v2dir=td/'v2'; v2cfg=ROOT/'relocatable_source/v2_pareto_fast/math_config_reference.inc'
        v2man=asm.build('v2_pareto_fast',v2cfg,v2dir); src_raw,_,_=load_prg(v2dir/v2man['output_prg'])
        _,src_init=sr.load_reference('v2_pareto_fast'); src_init=bytearray(src_init)
        entries=dict(sr.public_entries())
        if 'atan2_fast' in packs and 'zero_zp_v5' not in packs:
            hy.apply_atan2_fast(dst,src_raw,vals,base_man,entries,vals.get('HYBRID_CODE',0))
        if 'umul8_16' in packs: apply_umul8_16(dst,src_raw,vals,base_man,aux,entries)
        if 'umul24' in packs: apply_umul24(dst,src_raw,vals,base_man,aux,entries)
        if 'umul32_initialized' in packs: apply_umul32(dst,src_raw,vals,base_man,aux,entries)
        if 'smul16_exec' in packs: apply_smul16(dst,src_raw,src_init,vals,base_man,aux,entries)
        init_required=selection['init_required']
        if init_required:
            init_at=unhx(base_man['math_init']); helper,init_len=emit_init(dst,init_at,vals,packs,aux)
        else: helper=init_len=None
        # Preserve the base PRG span. Private Pareto payload is placed in configurable RAM;
        # the reference map uses RAM under BASIC ROM.
        hi=max(hi, vals['HYBRID_CODE']+hy.HYBRID_BYTES-1 if 'zero_zp_v5' in packs else hi, aux+AUX_BYTES-1 if (packs-{'zero_zp_v5','atan2_fast'}) else hi)
        if packs-{'zero_zp_v5','atan2_fast'}: lo=min(lo,aux)
        prg=outdir/'math_custom_pareto_game_math.prg'; write_prg(dst,lo,hi,prg)
        # Caller include from base map + generated metadata.
        inc=(bdir/'math_api.inc').read_text().rstrip()+'\n\n; Generated Pareto profile metadata\n'
        inc += f'MATH_PROFILE_ZP_BYTES = {selection["zp_bytes"]}\n'
        inc += f'MATH_PROFILE_INIT_REQUIRED = {1 if init_required else 0}\n'
        inc += f'PARETO_AUX_BASE = {hx(aux)}\n'
        (outdir/'math_api.inc').write_text(inc)
        ram_ranges=private_ram_ranges(vals,packs,aux,init_len)
        exact_private=sum(r['bytes'] for r in ram_ranges)
        manifest={
            'profile':PROFILE,'mode':'hybrid','status':'BUILT_FROM_CERTIFIED_V1_V2_PACKS',
            'config':str(config.relative_to(ROOT)) if config.is_relative_to(ROOT) else str(config),
            'output_prg':prg.name,'output_load':hx(lo),'output_end':hx(hi),
            'output_sha256':hashlib.sha256(prg.read_bytes()).hexdigest(),
            'public_entries':base_man['public_entries'],'math_init':base_man['math_init'],
            'public_io':base_man['public_io'],'selected_packs':sorted(packs),
            'zp_budget_requested':selection.get('zp_budget_requested'),
            'zp_bytes_reserved':selection['zp_bytes'],'zp_ranges':[{'name':n,'start':hx(a,2),'end':hx(b,2),'bytes':b-a+1} for n,a,b in ranges],
            'extra_main_ram_bytes':exact_private,
            'extra_main_ram_payload_bytes':exact_private,
            'private_main_ram_owned_bytes':exact_private,
            'private_main_ram_ranges':ram_ranges,
            'math_init_required':init_required,'init_helper':hx(helper) if helper is not None else None,
            'selection_score':selection['score'],
            'pack_details':{p:PACKS[p] for p in sorted(packs)},
            'notes':[
                'Selection occurs at build time; there is no runtime dispatcher.',
                'Only certified dependency-compatible packs are considered.',
                'All callers retain the common 54-entry ABI.',
                'If math_init_required is true, call MATH_INIT once before any math routine.',
                'The RAM budget is enforced against the exact selected private payload; it is not a requirement for one contiguous block. Inspect private_main_ram_ranges for placement/ownership.',
            ],
        }
        (outdir/'selection_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        (outdir/'source_build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        return manifest


def build_full_v2(config:Path,outdir:Path,selection:dict)->dict:
    outdir.mkdir(parents=True,exist_ok=True); man=asm.build('v2_pareto_fast',config,outdir)
    # Normalize output naming for custom builder users while preserving bytes.
    src=outdir/man['output_prg']; prg=outdir/'math_custom_pareto_game_math.prg'; shutil.copy2(src,prg)
    inc=(outdir/'math_api.inc').read_text().rstrip()+f'\n\n; Generated Pareto profile metadata\nMATH_PROFILE_ZP_BYTES = {FULL_V2_ZP_BYTES}\nMATH_PROFILE_INIT_REQUIRED = 1\n'
    (outdir/'math_api.inc').write_text(inc)
    manifest={
        'profile':PROFILE,'mode':'v2_full','status':'FULL_V2_SELECTED_BY_BUDGET',
        'config':str(config.relative_to(ROOT)) if config.is_relative_to(ROOT) else str(config),
        'output_prg':prg.name,'output_sha256':hashlib.sha256(prg.read_bytes()).hexdigest(),
        'public_entries':man['public_entries'],'math_init':man['math_init'],'public_io':man['public_io'],
        'selected_packs':['v2_full'],'zp_budget_requested':selection.get('zp_budget_requested'),
        'zp_bytes_reserved':FULL_V2_ZP_BYTES,'extra_main_ram_bytes':selection['extra_ram'],
        'extra_main_ram_payload_bytes':selection['extra_ram'],'math_init_required':True,
        'selection_score':'dominates_hybrid_catalog_at_full_v2_budget',
        'notes':['The requested ZP budget fits the complete V2 implementation under the selected map; V2 dominates the current certified stock-C64 hybrid catalog.','The 208-byte RAM figure is the resident payload increase versus the V1 reference profile, not a separately allocated scratch block.'],
    }
    (outdir/'selection_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (outdir/'source_build_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def parse_weights(items:list[str], path:Path|None)->dict[str,float]:
    w={}
    if path:
        obj=json.loads(path.read_text()); w.update({str(k).upper():float(v) for k,v in obj.items()})
    for item in items:
        if '=' not in item: raise ValueError('--weight must be NAME=NUMBER')
        k,v=item.split('=',1); k=k.upper(); k=k if k.startswith('MATH_') else 'MATH_'+k
        w[k]=float(v)
    return w


def main():
    ap=argparse.ArgumentParser(description='Build the fastest certified stock-C64 math profile fitting a ZP budget.')
    ap.add_argument('--zp-budget',type=int,required=True,help='total zero-page bytes available to the math library (minimum 31)')
    ap.add_argument('--ram-budget',type=int,default=None,help='optional exact extra private/resident payload budget in bytes relative to V1')
    ap.add_argument('--init-policy',choices=['auto','optional'],default='auto',help='optional forbids packs that require one-time MATH_INIT')
    ap.add_argument('--weight',action='append',default=[],help='routine frequency/importance hint, e.g. --weight MATH_SMUL16=20')
    ap.add_argument('--weights-json',type=Path)
    ap.add_argument('--config-kind',choices=['reference','alternate'],default='reference')
    ap.add_argument('--config',type=Path)
    ap.add_argument('--out',type=Path,default=ROOT/'build_pareto')
    ap.add_argument('--name',default=None,help='output build directory name')
    args=ap.parse_args()
    weights=parse_weights(args.weight,args.weights_json)
    sel=select_packs(args.zp_budget,args.ram_budget,args.init_policy,weights); sel['zp_budget_requested']=args.zp_budget
    cfg=args.config or ROOT/'relocatable_source'/PROFILE/f'math_config_{args.config_kind}.inc'
    name=args.name or f'zp{args.zp_budget}_{args.config_kind}'
    out=args.out/name
    if sel['mode']=='v2_full': man=build_full_v2(cfg,out,sel)
    else: man=build_hybrid_custom(cfg,out,sel)
    print(json.dumps({'status':'BUILT','directory':str(out),'mode':man['mode'],'selected_packs':man['selected_packs'],'zp_bytes':man['zp_bytes_reserved'],'init_required':man['math_init_required'],'extra_ram_payload_bytes':man.get('extra_main_ram_payload_bytes',man.get('extra_main_ram_bytes')),'sha256':man['output_sha256']},indent=2))

if __name__=='__main__': main()
