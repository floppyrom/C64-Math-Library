#!/usr/bin/env python3
"""Validate the public source/benchmark publication contract.

Rules:
  * every shipped profile standalone manifest row is indexed in routines/SOURCE_CATALOG.csv;
  * every catalog source and validation path exists;
  * every benchmark row has an existing public source;
  * source SHA-256 values match the published files;
  * canonical routine names follow the typed naming convention;
  * no benchmarked standalone alternative is source-less.
"""
from __future__ import annotations
import csv, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = [
    "v1_balanced", "v2_pareto_fast", "v3_reu_512k",
    "v4_reu_16m", "v5_hybrid_lowzp",
]

NAME_PATTERNS = [
    re.compile(r"^mul_[us]\d+_[us]\d+_[us]\d+(?:_(?:ready|shr\d+|turbo|turbo_begin|turbo_end|qs16|qs16_begin|qs16_end))?$"),
    re.compile(r"^div_[us]\d+_[us]\d+_[us]\d+(?:_\d+)?(?:_shl\d+)?$"),
    re.compile(r"^mod_[us]\d+_[us]\d+_[us]\d+$"),
    re.compile(r"^recip_[us]\d+_[us]\d+_q\d+$"),
    re.compile(r"^(?:sin|cos)_[us]\d+_[us]\d+$"),
    re.compile(r"^sincos_[us]\d+_[us]\d+_[us]\d+$"),
    re.compile(r"^atan2_[us]\d+_[us]\d+_[us]\d+$"),
    re.compile(r"^isqrt_[us]\d+_[us]\d+$"),
    re.compile(r"^dist_[us]\d+_[us]\d+_[us]\d+_(?:fast|accurate)$"),
    re.compile(r"^normalize_[us]\d+_[us]\d+_[us]\d+_[us]\d+_q\d+_\d+_to_q\d+_\d+$"),
]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_csv(path: Path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def valid_name(name: str) -> bool:
    return any(p.fullmatch(name) for p in NAME_PATTERNS)

def main() -> None:
    errors: list[str] = []
    catalog_path = ROOT / "routines/SOURCE_CATALOG.csv"
    public_path = ROOT / "benchmarks/PUBLIC_PROFILE_RESULTS.csv"
    standalone_path = ROOT / "benchmarks/STANDALONE_RESULTS.csv"
    best_path = ROOT / "benchmarks/BEST_PROFILE_RESULTS.csv"
    for p in (catalog_path, public_path, standalone_path, best_path):
        if not p.exists(): errors.append(f"missing required index: {p.relative_to(ROOT)}")
    if errors:
        raise SystemExit("\n".join(errors))

    catalog = read_csv(catalog_path)
    public = read_csv(public_path)
    standalone = read_csv(standalone_path)
    best = read_csv(best_path)

    cat_keys=set()
    for row in catalog:
        key=(row["scope"],row["profile"],row["legacy_api"],row["canonical_name"],row["variant"])
        if key in cat_keys: errors.append(f"duplicate catalog key: {key}")
        cat_keys.add(key)
        if not valid_name(row["canonical_name"]):
            errors.append(f"nonconforming canonical name: {row['canonical_name']}")
        src=ROOT/row["source_path"]
        if not src.is_file(): errors.append(f"missing source: {row['source_path']}")
        elif row.get("source_sha256") and digest(src)!=row["source_sha256"]:
            errors.append(f"source hash mismatch: {row['source_path']}")
        vp=row.get("validation_path","")
        if vp and not (ROOT/vp).is_file(): errors.append(f"missing validation/evidence: {vp}")

    # Every shipped standalone file must be in the catalog and public benchmark table.
    pub_keys={(r["profile"],r["routine"]):r for r in public}
    for profile in PROFILES:
        manifest=read_csv(ROOT/profile/"standalone/MANIFEST.csv")
        for m in manifest:
            key=("shipped-profile",profile,m["legacy_api"],m["canonical_name"],"")
            if key not in cat_keys:
                errors.append(f"manifest row absent from catalog: {profile} {m['legacy_api']}")
            if (profile,m["legacy_api"]) not in pub_keys:
                errors.append(f"manifest row absent from public benchmark table: {profile} {m['legacy_api']}")
            path=ROOT/profile/"standalone"/m["file"]
            if not path.is_file(): errors.append(f"manifest source absent: {path.relative_to(ROOT)}")

    # Public benchmark source contract.
    for r in public:
        src=ROOT/r["source_path"]
        if not src.is_file(): errors.append(f"public result source missing: {r['source_path']}")
        elif digest(src)!=r["source_sha256"]: errors.append(f"public result source hash mismatch: {r['source_path']}")
        if not valid_name(r["canonical_name"]): errors.append(f"public result name invalid: {r['canonical_name']}")

    # Fastest-shipped convenience index must be complete and truly minimal.
    by_name={}
    for r in public:
        try: cyc=float(r['mean_cycles'])
        except Exception: continue
        by_name.setdefault(r['canonical_name'],[]).append((cyc,r))
    best_names=set()
    for r in best:
        n=r['canonical_name'];best_names.add(n)
        if n not in by_name:
            errors.append(f"best-profile row has no public source row: {n}");continue
        target=min(c for c,_ in by_name[n])
        try: got=float(r['mean_cycles'])
        except Exception:
            errors.append(f"best-profile nonnumeric mean: {n}");continue
        if abs(got-target)>1e-9:
            errors.append(f"best-profile row is not fastest: {n} {got} != {target}")
        src=ROOT/r['source_path']
        if not src.is_file(): errors.append(f"best-profile source missing: {r['source_path']}")
        elif digest(src)!=r['source_sha256']: errors.append(f"best-profile source hash mismatch: {r['source_path']}")
    missing=set(by_name)-best_names
    if missing: errors.append(f"best-profile index missing canonical names: {sorted(missing)}")

    # Standalone benchmark source contract.
    alt_keys=set()
    for r in standalone:
        k=(r["canonical_name"],r["variant"])
        if k in alt_keys: errors.append(f"duplicate standalone result: {k}")
        alt_keys.add(k)
        src=ROOT/r["source_path"]
        if not src.is_file(): errors.append(f"standalone result source missing: {r['source_path']}")
        elif digest(src)!=r["source_sha256"]: errors.append(f"standalone source hash mismatch: {r['source_path']}")
        vp=ROOT/r["validation_path"]
        if not vp.is_file(): errors.append(f"standalone evidence missing: {r['validation_path']}")
        cat_key=("standalone-alternative","","",r["canonical_name"],r["variant"])
        if cat_key not in cat_keys: errors.append(f"standalone result absent from catalog: {k}")

    summary={
        "status":"PASS" if not errors else "FAIL",
        "catalog_rows":len(catalog),
        "shipped_profile_rows":sum(r["scope"]=="shipped-profile" for r in catalog),
        "standalone_alternative_rows":sum(r["scope"]=="standalone-alternative" for r in catalog),
        "public_profile_results":len(public),
        "standalone_results":len(standalone),
        "best_profile_results":len(best),
        "profiles":{p:len(read_csv(ROOT/p/"standalone/MANIFEST.csv")) for p in PROFILES},
        "errors":errors,
    }
    (ROOT/"validation/PUBLIC_SOURCE_CATALOG_AUDIT.json").write_text(json.dumps(summary,indent=2)+"\n")
    if errors:
        raise SystemExit("PUBLIC SOURCE CATALOG FAIL\n"+"\n".join(f"- {e}" for e in errors))
    print(f"PUBLIC SOURCE CATALOG PASS: {len(catalog)} sources/results indexed; {len(public)} shipped rows; {len(standalone)} standalone alternatives")

if __name__ == "__main__":
    main()
