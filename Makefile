PYTHON ?= python3

.PHONY: sources reference alternate validate signed-layout signed-multiply turbo turbo-boundary isqrt config deterministic hybrid hybrid-validate pareto pareto-validate pareto-config pareto-stress normalize audit acme clean package-audit all

all: reference alternate validate signed-layout signed-multiply turbo turbo-boundary isqrt config deterministic hybrid-validate pareto-validate audit

sources:
	$(PYTHON) tools/generate_sources.py

reference: sources
	$(PYTHON) tools/assemble_sources.py --profile all --config-kind reference

alternate: sources
	$(PYTHON) tools/assemble_sources.py --profile all --config-kind alternate

validate: alternate
	$(PYTHON) tools/validate_source_build.py all --build build_source/alternate --out validation/source_relocation

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

hybrid:
	$(PYTHON) tools/build_hybrid.py --config-kind reference
	$(PYTHON) tools/build_hybrid.py --config-kind alternate

hybrid-validate: hybrid
	$(PYTHON) tools/validate_hybrid.py
	$(PYTHON) tools/test_hybrid_config.py
	$(PYTHON) tools/verify_hybrid_deterministic.py

pareto:
	$(PYTHON) tools/build_pareto.py --zp-budget 60 --config-kind reference --name default_zp60

normalize: reference alternate hybrid
	$(PYTHON) tools/validate_normalize_native_sources.py
	$(PYTHON) tools/benchmark_normalize_profile_parity.py
	$(PYTHON) tools/certify_normalize_exact_ratio.py

pareto-config:
	$(PYTHON) tools/test_pareto_config.py

pareto-stress:
	$(PYTHON) tools/stress_pareto.py

pareto-validate:
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
