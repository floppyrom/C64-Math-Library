# Issue #144 V4 REU ISQRT32 — fast-four refinement (research only)

**15 October 2026.** This independently authored, opt-in NMOS 6510 source is NOT installed into the normal V4 resident, and neither production `PERFORMANCE.md` nor the five PRGs/two REU payloads is changed. The general optimization campaign stays open.

## Algorithm
The existing 16 MiB V4 REU image supplies a 4 MiB prefix table: a mathematically exact root and residual after the first 20 radicand bits, with partial root ≤1023. The next **four** radix-4 steps have two-byte residual and trial, so the third-byte shifts, compare and subtract are redundant. Replace these stages with `IS32P_REFINE_FAST` and retain original `IS32P_REFINE` for the **final two** steps, where a 17th bit can be live. No new normal zero-page allocation and no REU table changes. Ordinary `MATH_ISQRT32` accepts any unsigned N32 and returns floor(sqrt(N)) and carry clear.

## Paired proof (original versus opt-in)
- Source-assembled reference and alternate V4 layouts both built successfully. V4 REU DMA uses the **existing current-main `$91` immediate** command in both; this is not a new production DMA fix. An obsolete staging ZIP had `$81` and was discarded as a production baseline (see the correction closing #166).
- Public entry after `MATH_INIT`, same deterministic **8,619 unrestricted radicands** and actual 16 MiB REU lookup data in the public CPU model: correct root, carry, N preservation, A/X/Y, N/Z, stack and tracked scratch. Paired means: baseline **918.542406** vs candidate **807.352361** model cycles: **111.190045 saved**, median 111, p95 saving 129, minimum saving 93, **zero slower**. Corpus SHA256 `12792bbb3d4738896be4d33123675ab915e01eec875f7a54ca284e51e1a6ea1c`.
- **Volatile overflow flag V differs on 195/8619 modeled calls**. It is not a documented hard-output contract; applications relying on the old incidental V value cannot substitute this source. The 24 native paired vector samples had no V differences.
- Headless **VICE 3.13.2, real 16 MiB V4 REU**, native baseline 24 calls + candidate 24 calls: all arithmetic roots and public carry correct, including extrema, $7FFF and $FFFFFFFF. Native CPU/VIC/REU DMA cycle timing **not measured**.
- Tests were performed on a source-built V4 reference-equivalent module with the `$91` command matching current main. This is research proof, not a current-main production regression result.

## Reuse / qualification
The separately available `optional/issue144_v4_reu_isqrt_fast4/v4_reu_16m.asm` replaces `relocatable_source/v4_reu_16m/isqrt32_reu_prefix.asm` **only in a disposable local custom V4 source build**. Build both `--config-kind reference` and `alternate`; verify source/executable placements, native end-to-end tests on the **current** shipped V4 resident and physical REU/VIC DMA before considering normal-profile promotion. This source cannot simply be JSR'd as a separately linked self-contained object. The remainder of #144 stays open.

**No private OptiSearch generator, source, files or candidate archive is redistributed.**

## Independently rerunnable proof (not merely an evidence ledger)

Run `python3 tools/issue144_v4_isqrt_fast4_source_native_qualify.py` to build both reference and alternate layouts from temporary source copies, then compare 2,109 additional unrestricted public-entry pairs against `math.isqrt` using the actual 16MiB REU data in mini6502. To also execute 48 real x64sc hardware-emulation calls, set `VICE_WRAPPER` to a working headless x64sc binary or wrapper. The dedicated `.github/workflows/issue144-v4-isqrt-fast4.yml` installs a SHA256-pinned VICE package and reruns this combined gate in CI. All production source and binary files are left untouched.
