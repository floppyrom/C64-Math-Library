#!/usr/bin/env python3
"""Issue144 B/C source-and-evidence release seal, with no resident promotion."""
from __future__ import annotations
import hashlib,json,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/"tools"))
from stage_issue39_v1_3216_ool_release import reseal
from validate_unsigned_division import PROFILES
SRC_B="optional/issue144_pow2_mod32_16/mod32_16_pow2_remainder_only.asm"
SRC_C="optional/issue144_isqrt32_u16/low16_dispatch.asm"
SRC_S="optional/issue144_pow2_smod32_16/smod32_16_r_only.asm"
NATIVE="validation/review/ISSUE144_BC_SPECIALISTS_NATIVE_VICE.json"
DOC="docs/ISSUE144_BC_DOMAIN_SPECIALIST_PARETO_2026-10-15.md"
STAMP="2026-10-15 ISSUE144 B/C DOMAIN-QUALIFIED OPTIONAL SOURCES"
def data(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def main():
 release=data("RELEASE_STATUS.json")
 native=data(NATIVE)
 assert native["status"]=="PASS_NATIVE_VICE_BC_DOMAIN_SPECIALISTS"
 assert set(native["profiles"])==set(PROFILES)
 original={p:release["reference_prg_sha256"][p] for p in PROFILES}
 reference_reu=dict(release.get("reference_reu_sha256",{}))
 rows={}
 for profile in PROFILES:
  p=f"validation/review/ISSUE144_BC_DOMAIN_{profile}.json"
  x=data(p)
  assert x["status"]=="PASS_CPU_MODEL_DOMAIN_SCREEN_ONLY"
  assert x["profile"]==profile
  b=x["mod_pow2"];c=x["isqrt_low16"];signed=x["signed_mod_pow2"]
  assert signed["status"]=="PASS_SIGNED_POW2_RONLY_NOT_QUOTIENT"
  assert signed["source_sha256"]==sha(SRC_S)
  assert signed["saved"]["min_cycles"]>0
  assert b["status"]=="PASS_RONLY_POW2_CONTRACT"
  assert b["code_bytes"]==25 and b["specialist"]["mean_cycles"]==38
  assert b["public_alias_produces_quotient_but_specialist_does_not"]
  assert b["source_sha256"]==sha(SRC_B)
  assert c["status"]=="PASS_LOW16_AND_ALL_DOMAIN_GUARDED_CORRECTNESS"
  assert c["source_sha256"]==sha(SRC_C)
  assert c["workloads"]["low16"]["low16_only_savings"]["min_cycles"]>0
  assert c["workloads"]["full32"]["guard_savings"]["mean_cycles"]<0
  assert native["profiles"][profile]["mod_pow2"]["results_and_carry_equal"]
  assert native["profiles"][profile]["isqrt_low16"]["results_and_carry_equal"]
  assert native["profiles"][profile]["signed_mod_pow2"]["results_and_carry_equal"]
  path=f"{profile}/resident/math_{profile}_game_math.prg"
  assert sha(path)==original[profile],("resident changed",profile)
  rows[profile]={"smod_stock":signed["stock"]["mean_cycles"],
   "smod_fast":signed["specialist"]["mean_cycles"],
   "smod_gain":signed["saved"]["mean_cycles"],
   "mod_stock":b["stock"]["mean_cycles"],
   "mod_fast":b["specialist"]["mean_cycles"],
   "mod_gain":b["saved"]["mean_cycles"],
   "sqrt_stock":c["workloads"]["low16"]["timings"]["baseline"]["mean_cycles"],
   "sqrt_fast":c["workloads"]["low16"]["timings"]["low16_only"]["mean_cycles"],
   "sqrt_gain":c["workloads"]["low16"]["low16_only_savings"]["mean_cycles"],
   "sqrt_guard_full_regression":-c["workloads"]["full32"]["guard_savings"]["mean_cycles"],
   "sqrt_guard_mixed10_gain":c["workloads"]["mixed_10pct"]["guard_savings"]["mean_cycles"]}
 lines=[
  "# Issue #144 — B/C opt-in arithmetic Pareto source publication",
  "",
  "**Separate caller-selected domain specialists; not normal API replacements.**",
  "The regular V1–V5 PRGs, REUs, public symbol addresses, ZP and public",
  "PERFORMANCE leaderboard remain byte-for-byte unchanged.",
  "",
  "## B: 25-byte 32/16 unsigned remainder-only power-of-two producer",
  "",
  "Precondition: D16 nonzero and exactly a power of two (1..32768).",
  "N32 at $C010–$C013, D16 at $C014–$C015. Output R16 only",
  "at $C01C–$C01D, carry clear. Q32 at $C018–$C01B is",
  "**not computed**: this cannot be used as a drop-in replacement",
  "for existing MATH_UMOD32_16 which also returns Q32.",
  "No ZP, immutable tables, or init required; 25 bytes at caller-owned",
  "$0C00 (reassemble if occupied). X,Y,SP and inputs preserved.",
  "",
  "| Profile | Matched stock UMOD mean | R-only opt-in | Saved cycles |",
  "|---|---:|---:|---:|"]
 for p in PROFILES:
  a=rows[p];lines.append(f"| {p} | {a['mod_stock']:.3f} | {a['mod_fast']:.3f} | {a['mod_gain']:.3f} |")
 lines += [
  "",
  "Each profile: 16 legal power-of-two denominators, 160 random numerators",
  "per denominator plus structured edges: 2,752 paired CPU-model calls.",
  "All 13,760 matched model calls correct, including carry/input and",
  "preserved non-output quotient bytes. Native x64sc: 24 baseline plus",
  "24 optional calls/profile. These comparisons prove remainder/carry",
  "only, *not* quotient equivalence.",
  "",
  "## C: exact ISQRT32 low-word-domain selector",
  "",
  "Precondition: upper input word $C012,$C013 is zero, N32 <= $FFFF.",
  "The stock MATH_ISQRT16 is exact over this domain, so the separately",
  "placed three-byte JMP at $0C40 reuses it and returns exactly the",
  "same 16-bit root, input preservation and clear carry.",
  "Requires the resident original MATH_INIT and table data.",
  "",
  "| Profile | Stock 32-bit sqrt on low16 workload | Low16 specialist | Saved |",
  "|---|---:|---:|---:|"]
 for p in PROFILES:
  a=rows[p];lines.append(f"| {p} | {a['sqrt_stock']:.3f} | {a['sqrt_fast']:.3f} | {a['sqrt_gain']:.3f} |")

 lines += [
  "",
  "## B2: signed 32/16 remainder-only positive-power-of-two divisor",
  "",
  "Input N32 may be **any signed 32-bit value**, including negatives.",
  "D16 must be positive and exactly one bit set (1..16384).",
  "The 6510 kernel forms signed remainder correctly for truncation",
  "toward zero: if N is negative and the masked positive remainder",
  "is nonzero, subtract D to obtain the negative signed R16.",
  "Q32 is again untouched: NOT a drop-in signed modulo alias.",
  "It uses no normal ZP or lookup tables and preserves X, Y and SP.",
  "",
  "| Profile | Stock signed modulo | Signed R-only | Saved cycles |",
  "|---|---:|---:|---:|"]
 for p in PROFILES:
  a=rows[p]
  lines.append(f"| {p} | {a['smod_stock']:.3f} | {a['smod_fast']:.3f} | {a['smod_gain']:.3f} |")
 lines += [
  "",
  "15 nonzero positive powers of two x 165 operand vectors including",
  "negative edges and seeded random data: 2,475 model calls/profile,",
  "12,375 matched checks across all V1–V5, plus real native VICE",
  "baseline/specialist comparisons for signed-negative numerators.",
  "Source: "+SRC_S]
 lines += [
  "",
  "There is also an AUTO selector that checks upper input bytes. It is",
  "exact on arbitrary 32-bit inputs, but its branch tax slows full-width",
  "calls. **Not promoted as a default:** choose only after measuring",
  "application inputs. Mean paired full-width regression / 10% low16",
  "workload improvement (cycles, CPU model):",
  "",
  "| Profile | Full32 regression | Mixed 10% low16 gain |",
  "|---|---:|---:|"]
 for p in PROFILES:
  a=rows[p];lines.append(f"| {p} | {a['sqrt_guard_full_regression']:.3f} | {a['sqrt_guard_mixed10_gain']:.3f} |")
 lines += [
  "",
  "All five profiles pass deterministic common-input model tests",
  "and native x64sc arithmetic/carry comparisons (720 native calls",
  "total for three specialist families). The V4 sqrt native test",
  "loads the actual 16-MiB REU file. VICE native cycles, VIC-II",
  "bus effects and REU DMA time are **not** claimed.",
  "",
  "Source B: "+SRC_B,
  "Source C: "+SRC_C,
  "Model reproducer: tools/issue144_BC_domain_screen.py",
  "VICE reproducer: tools/native_issue144_BC_specialists.py",
  "Native evidence: "+NATIVE,
  "",
  "## Wider research that has NOT been promoted",
  "",
  "The existing 114-byte Issue39 power-of-two full-division helper",
  "produces complete Q32/R16. A new checked dispatcher can use that",
  "on power-of-two D and fall back to the ordinary alias for all",
  "other denominators, preserving divide-by-zero semantics. A separate",
  "same-input screen shows ~33.38 mean cycles gained when 10% of V2–V5",
  "divisors are powers of two, but ~28.39 mean cycles regressed when",
  "D16 is uniform. It is kept as source research, not a new normal API.",
  "Source: optional/issue144_guarded_pow2_divmod/guard.asm",
  "",
  "All specializers require independently verified caller-owned RAM;",
  "the example addresses are not reserved and can conflict with a",
  "loader, application screen, other opt-ins or interrupt hooks.",
  "No private OptiSearch source is published."
 ]
 (R/DOC).write_text("\n".join(lines)+"\n")
 status=release
 status["issue144_bc_domain_optins_2026_10_15"]={
  "status":"PASS_SOURCE_CPU_NATIVE_OPTIN_ONLY",
  "profiles":list(PROFILES),"pow2_mod_result_contract":"R16/C only, not quotient",
  "power_two_requirement":"D16 nonzero and exact power of two",
  "sqrt_domain":"N32 high word zero","native_vice_correctness":True,
  "native_cycles_measured":False,"v4_native_real_reu_image":True,
  "published_default_prgs_changed":False,"normal_zp_added":0,
  "documentation":DOC,"sources":[SRC_B,SRC_C,SRC_S],
  "model_prefix":"validation/review/ISSUE144_BC_DOMAIN_",
  "native_record":NATIVE,"paired_performance":rows}
 (R/"RELEASE_STATUS.json").write_text(json.dumps(status,indent=2)+"\n")
 note=STAMP+"\n- Source-only opt-in B/C specialists, no installed library change: unsigned and signed power-of-two 32/16 remainder-only (NOT quotient-producing); low16 ISQRT32 via existing ISQRT16; five-profile CPU/native proof including real V4 REU image. An all-input guard and quotient-complete pow2 selector remain research-only. Regular library binaries, ZP, public API and PERFORMANCE leaderboard unchanged. "+DOC+"\n\n"
 for fname in ("CHANGELOG.md","CSDB_CHANGELOG.txt"):
  f=R/fname
  if STAMP not in f.read_text():f.write_text(note+f.read_text())
 subprocess.run(["make","clean"],cwd=R,check=True)
 for _ in range(3):
  reseal()
  subprocess.run([sys.executable,"tools/package_audit.py"],cwd=R,check=True)
 assert all(sha(p+"/resident/math_"+p+"_game_math.prg")==original[p] for p in PROFILES)
 assert dict(data("RELEASE_STATUS.json").get("reference_reu_sha256",{}))==reference_reu
 print("ISSUE144 B/C SOURCE/CPU/NATIVE/DOCS/CHANGELOGS/SHA SEALED")
if __name__=="__main__":main()
