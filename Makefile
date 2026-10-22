.DEFAULT_GOAL := builder-help

PYTHON ?= python3
ACME ?= acme

.PHONY: builder-help builder-list builder-setup builder builder-speed builder-frame builder-biased-qs-test builder-measure sources reference alternate validate public-index public-audit signed-layout signed-multiply turbo turbo-boundary isqrt config deterministic hybrid hybrid-validate pareto pareto-validate pareto-config pareto-stress builder-validate normalize seek audit acme clean package-audit all legacy-validate legacy-frozen-verify deterministic-current

# "all" is now the supported stock-C64 installer, not five historical
# resident distributions. Their reproducibility checks remain explicitly
# runnable via "make legacy-validate". No source or binary is removed.
all: builder

# Functional/current-source legacy regression for developers. Rebuilt V1-V4
# images are deterministic but include newer source-owned arithmetic modules;
# they are NOT claimed identical to the immutable historical resident PRGs.
legacy-validate: reference alternate validate signed-layout signed-multiply turbo turbo-boundary isqrt config deterministic-current hybrid-validate pareto-validate
	@echo "LEGACY CURRENT-SOURCE VALIDATION: PASS does not certify frozen PRG byte identity."
# Historical freeze check deliberately remains exact and FAILS on known V1-V4
# current-source-vs-frozen discrepancies (issue #398). Never silently relax it.
legacy-frozen-verify: reference alternate deterministic audit

# Sole supported new-project installer is operation-first. Override CONFIG and
# OUT to build another operation set. Historical residents are read-only
# reference/validation artifacts; REU service bundles remain separate.
CONFIG ?= examples/operation-first.json
OUT ?= build_selective

builder-help:
	@echo 'C64 Math Library: operation-first installer (sole new-project workflow)'
	@echo '  make builder                       # balanced: optimize resources, NOT fastest cycles'
	@echo '  make builder-speed                 # speed: compare same-corpus kernel cycles'
	@echo '  make builder-frame                 # source-qualified math-only frame objective'
	@echo '  make builder CONFIG=path/to.json    # build your own operation set'
	@echo '  make builder-measure                # measure exact assembled footprint'
	@echo '  make builder-list                   # show 56 public operations'
	@echo '  make builder-setup                  # guided setup, editable JSON plus tested PRG'
	@echo '  make all                            # stock C64 operation-first default build'
	@echo '  make legacy-validate                # current-source legacy regression (not frozen PRG identity)'\n\t@echo '  make legacy-frozen-verify           # strict frozen resident identity (known #398 failure)'

builder-setup:
	$(PYTHON) tools/configure_math.py

builder-list:
	$(PYTHON) tools/math_builder.py --list-linkable

builder-measure:
	$(PYTHON) tools/math_builder.py --config $(CONFIG) --measure

builder:
	$(PYTHON) tools/math_builder.py --config $(CONFIG) --out $(OUT)/selection_manifest.json --build

# This is deliberately an explicit, separate speed target. It never silently
# calls a resource-only installer when workload timing is unavailable. Supply
# a speed-qualified set of operations and per-operation calls in the config.
SPEED_CONFIG ?= examples/operation-first-speed.json

builder-speed:
	$(PYTHON) tools/math_builder.py --config $(SPEED_CONFIG) --objective speed --out $(OUT)/selection_manifest.json --build

# Strict opt-in whole linked-image synthetic frame objective.
FRAME_CONFIG ?= examples/operation-first-frame.json
# The default example has a deterministic, source-qualified report generator.
# User-supplied reports are never guessed, created or silently replaced.
FRAME_REPORT ?= $(OUT)/mixed3.json

builder-frame:
	@if [ ! -f "$(FRAME_REPORT)" ]; then \
		if [ "$(FRAME_REPORT)" = "$(OUT)/mixed3.json" ]; then \
			echo "Generating qualified default math-only frame evidence: $(FRAME_REPORT)"; \
			$(PYTHON) tools/mixed3_frame_parity.py --out "$(FRAME_REPORT)" || exit $?; \
		else \
			echo "No measured frame evidence at $(FRAME_REPORT); provide a verified report." >&2; \
			exit 2; \
		fi; \
	fi
	$(PYTHON) tools/math_builder.py --config $(FRAME_CONFIG) --objective frame --frame-report "$(FRAME_REPORT)" --out $(OUT)/selection_manifest.json --build

builder-biased-qs-test:
	$(PYTHON) -m unittest discover -s tools -p 'test_biased_quartersquare_offsets.py' -v


# Historical residents below are kept for source provenance, exact binary
# reproducibility and separate V3/V4 REU compatibility. They are NOT normal
# library installation commands; see README.md and docs/REU_COMPAT_EXPORT.md.
sources:
	$(PYTHON) tools/generate_sources.py

reference: sources
	$(PYTHON) tools/assemble_sources.py --profile all --config-kind reference

alternate: sources
	$(PYTHON) tools/assemble_sources.py --profile all --config-kind alternate

validate: alternate
	$(PYTHON) tools/validate_source_build.py all --build build_source/alternate --out validation/source_relocation

public-index:
	$(PYTHON) tools/generate_public_indexes.py

public-audit: public-index
	$(PYTHON) tools/validate_public_catalog.py
	$(PYTHON) tools/validate_standalone_sources.py

signed-layout:
	$(PYTHON) tools/validate_signed_layout.py

signed-multiply:
	$(PYTHON) tools/validate_signed_multiply.py

turbo: reference alternate
	$(PYTHON) tools/validate_turbo_relocation.py

turbo-boundary: sources
	$(PYTHON) tools/validate_turbo_boundary_sweep.py

isqrt:
	$(PYTHON) tools/validate_isqrt32_fast.py
	$(PYTHON) tools/benchmark_isqrt32_fast.py

config:
	$(PYTHON) tools/test_config_validation.py

deterministic: reference alternate
	$(PYTHON) tools/verify_deterministic_rebuild.py

deterministic-current: reference alternate
	$(PYTHON) tools/verify_deterministic_rebuild.py --current-repeatability

hybrid:
	$(PYTHON) tools/build_hybrid.py --config-kind reference
	$(PYTHON) tools/build_hybrid.py --config-kind alternate

hybrid-validate: reference hybrid
	$(PYTHON) tools/validate_hybrid.py
	$(PYTHON) tools/test_hybrid_config.py
	$(PYTHON) tools/verify_hybrid_deterministic.py

pareto:
	$(PYTHON) tools/build_pareto.py --zp-budget 60 --config-kind reference --name default_zp60

normalize: reference alternate hybrid
	$(PYTHON) tools/generate_normalize_tables.py --check
	$(PYTHON) tools/validate_normalize_native_sources.py
	$(PYTHON) tools/benchmark_normalize_profile_parity.py
	$(PYTHON) tools/validate_normalize_optimized.py
	$(PYTHON) tools/certify_normalize_exact_ratio.py

seek: reference alternate hybrid
	$(PYTHON) tools/generate_seek_sources.py --check
	$(PYTHON) tools/test_mini6502_illegal.py
	$(PYTHON) tools/validate_seek_placement.py
	$(PYTHON) tools/benchmark_seek_profiles.py

pareto-config:
	$(PYTHON) tools/test_pareto_config.py

pareto-stress:
	$(PYTHON) tools/stress_pareto.py

builder-validate:
	$(PYTHON) -m compileall -q tools/math_builder.py tools/selective_linker.py tools/selective_atan2.py tools/test_math_builder.py tools/test_selective_linker.py tools/test_selective_atan2.py tools/test_selective_multiply.py tools/test_selective_umul16_shr8.py tools/test_selective_fast_umul16_shr8.py tools/test_selective_speed_umul16_shr8.py tools/selective_speed_umul16_shr8.py tools/test_selective_umul8.py tools/selective_isqrt16.py tools/selective_seek8.py tools/selective_seek16.py tools/test_selective_seek8.py tools/native_selective_seek8.py tools/test_selective_seek16.py tools/native_selective_seek16.py tools/test_selective_u3216.py tools/test_selective_udiv16_shl8.py tools/native_selective_udiv16_shl8.py tools/test_selective_urecip16_q16.py tools/native_selective_urecip16_q16.py tools/test_selective_umul24.py tools/native_selective_umul24.py tools/test_selective_smul16.py tools/native_selective_smul16.py tools/test_selective_smul16_shr8.py tools/native_selective_smul16_shr8.py tools/test_selective_smul24.py tools/native_selective_smul24.py tools/test_selective_umul32.py tools/native_selective_umul32.py tools/test_selective_sdiv16.py tools/native_selective_sdiv16.py tools/test_selective_sdiv16_shl8.py tools/native_selective_sdiv16_shl8.py tools/test_selective_sdiv24.py tools/native_selective_sdiv24.py tools/test_selective_sdiv32_16.py tools/native_selective_sdiv32_16.py tools/test_selective_sdiv32_32.py tools/native_selective_sdiv32_32.py tools/test_selective_umul32_shr16.py tools/native_selective_umul32_shr16.py tools/test_selective_smul32.py tools/native_selective_smul32.py tools/native_selective_u3216.py tools/test_selective_u24.py tools/native_selective_u24.py tools/test_selective_udiv24_v2.py tools/selective_udiv24_v2.py tools/test_selective_u3216_accum.py tools/test_selective_isqrt16.py tools/native_selective_isqrt16.py tools/test_selective_isqrt32.py tools/native_selective_isqrt32.py tools/test_selective_isqrt32_v2.py tools/native_selective_isqrt32_v2.py tools/test_selective_speed_isqrt32.py tools/selective_speed_isqrt32.py tools/test_selective_dist8.py tools/native_selective_dist8.py tools/test_selective_udiv8.py tools/native_selective_udiv8.py tools/test_selective_udiv8_v2v5.py tools/native_selective_udiv8_v2v5.py tools/selective_speed_udiv8.py tools/test_selective_speed_udiv8.py tools/test_selective_sdiv8.py tools/native_selective_sdiv8.py tools/selective_smul8.py tools/test_selective_smul8.py tools/native_selective_smul8.py tools/test_selective_umod8.py tools/native_selective_umod8.py tools/test_selective_umod8_variants.py tools/test_selective_umod8_speed.py tools/selective_speed_umod8.py tools/test_selective_speed_umod8.py tools/native_selective_umod8_variants.py tools/selective_trig8.py tools/test_selective_trig8.py tools/native_selective_trig8.py tools/selective_dist8_accurate.py tools/test_selective_dist8_accurate.py tools/native_selective_dist8_accurate.py tools/native_selective_linker.py tools/native_selective_atan2.py tools/native_selective_multiply.py routines/atan2/tables.py tools/mini6502.py routines/standalone_lab/portable/native_vice.py
	$(PYTHON) tools/test_math_builder.py
	$(PYTHON) tools/test_selective_linker.py
	$(PYTHON) tools/test_selective_atan2.py
	$(PYTHON) tools/test_selective_multiply.py
	$(PYTHON) tools/test_selective_umul16_shr8.py
	$(PYTHON) tools/test_selective_umul8.py
	$(PYTHON) tools/test_selective_fast_umul8.py
	$(PYTHON) tools/test_selective_umul8_v1.py
	$(PYTHON) tools/test_selective_fast_umul16.py
	$(PYTHON) tools/test_selective_fast_umul16_shr8.py
	$(PYTHON) tools/test_selective_speed_umul16_shr8.py
	$(PYTHON) tools/test_selective_speed_umul16.py
	$(PYTHON) tools/test_selective_speed_udiv8.py
	$(PYTHON) tools/test_selective_speed.py
	$(PYTHON) tools/test_selective_isqrt16.py
	$(PYTHON) tools/test_selective_isqrt32.py
	$(PYTHON) tools/test_selective_isqrt32_v2.py
	$(PYTHON) tools/test_selective_speed_isqrt32.py
	$(PYTHON) tools/test_selective_seek8.py
	$(PYTHON) tools/test_selective_seek16.py
	$(PYTHON) tools/test_selective_u3216.py
	$(PYTHON) tools/test_selective_udiv16_shl8.py
	$(PYTHON) tools/test_selective_urecip16_q16.py
	$(PYTHON) tools/test_selective_umul24.py
	$(PYTHON) tools/test_selective_smul16.py
	$(PYTHON) tools/test_selective_smul16_shr8.py
	$(PYTHON) tools/test_selective_smul24.py
	$(PYTHON) tools/test_selective_umul32.py
	$(PYTHON) tools/test_selective_sdiv16.py
	$(PYTHON) tools/test_selective_sdiv16_shl8.py
	$(PYTHON) tools/test_selective_sdiv24.py
	$(PYTHON) tools/test_selective_sdiv32_16.py
	$(PYTHON) tools/test_selective_sdiv32_32.py
	$(PYTHON) tools/test_selective_umul32_shr16.py
	$(PYTHON) tools/test_selective_smul32.py
	$(PYTHON) tools/test_selective_u24.py
	$(PYTHON) tools/test_selective_udiv24_v2.py
	$(PYTHON) tools/test_selective_u3216_accum.py
	$(PYTHON) tools/test_selective_dist8.py
	$(PYTHON) tools/test_selective_udiv8.py
	$(PYTHON) tools/test_selective_udiv8_v2v5.py
	$(PYTHON) tools/test_selective_sdiv8.py
	$(PYTHON) tools/test_selective_smul8.py
	$(PYTHON) tools/test_selective_umod8.py
	$(PYTHON) tools/test_selective_umod8_variants.py
	$(PYTHON) tools/test_selective_umod8_speed.py
	$(PYTHON) tools/test_selective_speed_umod8.py
	$(PYTHON) tools/test_selective_trig8.py
	$(PYTHON) tools/test_selective_dist8_accurate.py

pareto-validate: reference hybrid
	$(PYTHON) tools/validate_pareto.py
	$(PYTHON) tools/test_pareto_config.py
	$(PYTHON) tools/stress_pareto.py

audit:
	$(PYTHON) tools/release_audit.py

acme:
	$(PYTHON) tools/verify_with_acme.py --acme "$(ACME)" --kind all

clean:
	rm -rf build_source build_hybrid build_hybrid_repeat build_pareto tools/__pycache__
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

package-audit: clean
	$(PYTHON) tools/package_audit.py
