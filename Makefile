PYTHON ?= python3

.PHONY: sources reference alternate validate turbo turbo-boundary isqrt config deterministic audit acme clean package-audit all

all: reference alternate validate turbo turbo-boundary isqrt config deterministic audit

sources:
	$(PYTHON) tools/generate_sources.py

reference: sources
	$(PYTHON) tools/assemble_sources.py --profile all --config-kind reference

alternate: sources
	$(PYTHON) tools/assemble_sources.py --profile all --config-kind alternate

validate: alternate
	$(PYTHON) tools/validate_source_build.py all --build build_source/alternate --out validation/source_relocation

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

audit:
	$(PYTHON) tools/release_audit.py

acme:
	$(PYTHON) tools/verify_with_acme.py --acme "$(ACME)" --kind all

clean:
	rm -rf build_source tools/__pycache__
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

package-audit: clean
	$(PYTHON) tools/package_audit.py
