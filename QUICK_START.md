# Quick start

Requirements: Python 3. The repository includes its own deterministic 6502 source assembler/validator; no external assembler is required. ACME 0.97 is an optional independent cross-check.

The distribution is intentionally lean: `build_source/` is **generated on demand** and is not pre-populated in the ZIP. This avoids shipping duplicate PRGs and duplicate 512 KiB/16 MiB REU images.

```sh
# Re-generate canonical symbolic sources/config templates
python3 tools/generate_sources.py

# Build reference and deliberately different maps from source
python3 tools/assemble_sources.py --profile all --config-kind reference
python3 tools/assemble_sources.py --profile all --config-kind alternate

# Execute all 45 stable public entries in every alternate-map profile
python3 tools/validate_source_build.py all --build build_source/alternate --out validation/source_relocation

# Validate relocatable Turbo16/Turbo32 overlays on V3/V4
python3 tools/validate_turbo_relocation.py

# Validate fast exact ISQRT32
python3 tools/validate_isqrt32_fast.py

# Validate accepted/rejected memory and REU configurations
python3 tools/test_config_validation.py

# Audit the clean distribution contents (also removes generated build_source/)
make package-audit
```

For a custom map, copy a profile's `math_config_reference.inc` to `math_config.inc`, edit the symbols, then run `tools/assemble_sources.py --profile <profile> --config <path> --out <output-dir>`. Configuration validation rejects unsafe mappings before assembly.

V2–V4 require `MATH_INIT` once before normal calls. V3/V4 also require the **matching generated REU image**. If Turbo modes are used, do not call normal/game math between Turbo `BEGIN` and `END`; the overlay owns its configured ZP range during that lifecycle.

## Optional ACME verification

```sh
python3 tools/verify_with_acme.py --acme /path/to/acme --kind all
```

The verifier requires byte identity for all eight resident PRGs and, on V3/V4, independently assembles both Turbo overlay sources for reference and alternate maps and requires byte identity with the bundled assembler.
