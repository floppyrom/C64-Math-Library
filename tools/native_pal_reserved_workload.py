#!/usr/bin/env python3
"""Fail-closed headroom selection from authentic *installed* PAL burst evidence.

Only three 24-frame installer source plans verified in #361 are supported.
Reservations are hypothetical additional slots, not actual IRQ/SID/REU
measurements and not certification of continuous 50 Hz playback.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PAL = 19656
EXPECTED_BASIS = 'seven-api-registered-d65536-nine-source-linked-frame-choices-v1'
EXPECTED_SCHEMA = 'installed-d65536-three-plan-independent-pal-cia-v1'
LABELS = ('fast31-stock-v2', 'fast31-u65536-s65536', 'fast31-uv2-s65536')
OPS = ('MATH_UMUL32', 'MATH_SMUL32', 'MATH_ISQRT16', 'MATH_UDIV32_32',
       'MATH_UMOD32_32', 'MATH_SDIV32_32', 'MATH_SMOD32_32')


def verified_plans(report: dict) -> list[dict]:
    if not isinstance(report, dict) or any((
        report.get('schema') != EXPECTED_SCHEMA,
        report.get('source_report_basis') != EXPECTED_BASIS,
        report.get('native_emulator') != 'pinned-x64sc-r46284',
        report.get('nominal_pal_slots') != PAL,
        report.get('native_public_calls_per_display') != 450,
        report.get('consecutive_50hz_frames_measured') is not False,
        report.get('real_application_frame_certified') is not False,
        report.get('sid_irq_reu_application_work_measured') is not False,
    )):
        raise ValueError('Not the scoped source-installed, independent PAL burst evidence')
    by_plan = report.get('by_plan')
    sources = report.get('sources')
    if (not isinstance(by_plan, dict) or set(by_plan) != set(LABELS)
            or not isinstance(sources, list) or len(sources) != len(LABELS)
            or any(not isinstance(s, dict) for s in sources)):
        raise ValueError('Incomplete or unfamiliar three-plan source evidence')
    source_by_label = {row.get('label'): row for row in sources}
    if set(source_by_label) != set(LABELS):
        raise ValueError('Missing or duplicated source-linked PRG label')

    parsed = []
    reference_outputs = {}
    reference_calls = {}
    for label in LABELS:
        record = by_plan[label]
        source = source_by_label[label]
        frames = record.get('per_frame')
        if (not isinstance(frames, list) or len(frames) != 24
                or [row.get('frame') for row in frames] != list(range(24))
                or record.get('prg_sha256') != source.get('linked_prg_sha256')
                or not isinstance(source.get('linked_prg_sha256'), str)
                or len(source['linked_prg_sha256']) != 64
                or set(source.get('variants', {})) != set(OPS)):
            raise ValueError('Native samples do not match source-installed PRG or 24-frame trace')
        ram, zp = source.get('linked_ram_bytes'), source.get('zero_page_bytes')
        if not all(type(x) is int and x >= 0 for x in (ram, zp)):
            raise ValueError('Invalid linked RAM/ZP resource measurement')
        peak = 0
        peak_frame = None
        misses = 0
        total = 0
        calls = 0
        for row in frames:
            on, off = row.get('display_on_slots'), row.get('display_off_slots')
            n = row.get('source_linked_calls')
            if (not all(type(x) is int and x > 0 for x in (on, off, n))
                    or on < off
                    or row.get('visible_vic_overhead_slots') != on - off
                    or row.get('nominal_frame_headroom_slots') != PAL - on
                    or not isinstance(row.get('output_sha256'), str)
                    or len(row['output_sha256']) != 64):
                raise ValueError('Forged or incomplete real native CIA/frame/output fields')
            frame = row['frame']
            if frame in reference_outputs and reference_outputs[frame] != row['output_sha256']:
                raise ValueError('Public outputs differed across installed source plans')
            if frame in reference_calls and reference_calls[frame] != n:
                raise ValueError('Unmatched arithmetic public call schedule')
            reference_outputs[frame] = row['output_sha256']
            reference_calls[frame] = n
            calls += n
            total += on
            if on > peak:
                peak, peak_frame = on, frame
            misses += on > PAL
        if (calls != 150 or record.get('total_public_calls_per_display') != 150
                or record.get('peak_visible_slots') != peak
                or record.get('peak_frame_index') != peak_frame
                or record.get('worst_nominal_headroom_slots') != PAL - peak
                or record.get('nominal_deadline_overruns') != misses):
            raise ValueError('Reported native peak, deadline, or public-call count is inconsistent')
        parsed.append({'plan': label, 'native_peak_slots': peak,
                       'peak_frame': peak_frame, 'linked_ram_bytes': ram,
                       'zero_page_bytes': zp, 'native_24_burst_total_slots': total,
                       'prg_sha256': source['linked_prg_sha256']})
    if len({row['prg_sha256'] for row in parsed}) != 3:
        raise ValueError('Comparisons must use distinct installer source PRGs')
    return parsed


def select(report, *, reserve_nonmath_slots: int, max_ram: int, max_zp: int,
           require_headroom: bool = False):
    if not all(type(x) is int and x >= 0 for x in
               (reserve_nonmath_slots, max_ram, max_zp)):
        raise ValueError('All budget amounts must be nonnegative integers')
    measured = verified_plans(report)
    rows = []
    for plan in measured:
        remaining = PAL - reserve_nonmath_slots - plan['native_peak_slots']
        eligible = (remaining >= 0 and plan['linked_ram_bytes'] <= max_ram
                    and plan['zero_page_bytes'] <= max_zp)
        rows.append({**plan, 'reserved_nonmath_slots': reserve_nonmath_slots,
                     'estimated_remaining_slots_after_reservation': remaining,
                     'within_resource_and_nominal_slot_budget': eligible})
    possible = [r for r in rows if r['within_resource_and_nominal_slot_budget']]
    possible.sort(key=lambda p:(p['native_peak_slots'],p['linked_ram_bytes'],
                                p['zero_page_bytes'],p['native_24_burst_total_slots'],p['plan']))
    if require_headroom and not possible:
        raise ValueError('No measured source plan fits both resources and hypothetical reservation')
    return {
        'schema': 'native-installed-three-plan-hypothetical-headroom-budget-v1',
        'selected_plan': possible[0]['plan'] if possible else None,
        'source_report_basis': report['source_report_basis'],
        'reservation_is_hypothetical_not_physically_measured': True,
        'continuous_50hz_application_certified': False,
        'irq_sid_reu_application_work_measured': False,
        'nominal_pal_slots': PAL,
        'reserve_nonmath_slots': reserve_nonmath_slots,
        'max_linked_ram_bytes': max_ram,
        'max_zero_page_bytes': max_zp,
        'measured_plan_count': len(measured),
        'eligible_plan_count': len(possible),
        'plans': rows,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--native-report', type=Path, required=True)
    p.add_argument('--reserve-nonmath-slots', type=int, default=0)
    p.add_argument('--max-ram', type=int, default=65535)
    p.add_argument('--max-zp', type=int, default=255)
    p.add_argument('--require-headroom', action='store_true')
    p.add_argument('--out', type=Path)
    a = p.parse_args()
    try:
        evidence=json.loads(a.native_report.read_text(encoding='utf-8'))
        result=select(evidence,reserve_nonmath_slots=a.reserve_nonmath_slots,
                      max_ram=a.max_ram,max_zp=a.max_zp,
                      require_headroom=a.require_headroom)
    except (ValueError, OSError, json.JSONDecodeError) as err:
        p.error(str(err))
    payload=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True)
        a.out.write_text(payload,encoding='utf-8')
    else:
        print(payload,end='')


if __name__ == '__main__':
    main()
