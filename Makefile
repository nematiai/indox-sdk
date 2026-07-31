# indox-sdk — the 8 official API v1 clients, their codegen pipeline and gates.
# Config comes from .env (see .env.example); nothing is hardcoded here.
ROOT := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
PY = cd $(ROOT) && PYTHONPATH=$(ROOT) python3

.PHONY: help openapi gen gen-all drift packages smoke test ci
.DEFAULT_GOAL := help

help:          ## list targets
	@grep -hE '^[a-z0-9-]+:.*##' $(MAKEFILE_LIST) | sort | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

openapi:       ## rebuild spec/openapi-public.json from the live API
	$(PY) tools/build_openapi_public.py

gen:           ## codegen one client (SDK_LANG=typescript)
	@test -n "$(SDK_LANG)" || { echo "Usage: make gen SDK_LANG=typescript"; exit 1; }
	$(PY) tools/generate_sdk.py --lang $(SDK_LANG)

gen-all:       ## codegen every client
	$(PY) tools/generate_sdk.py --all

drift:         ## fail if the allowlist drifted from the live/DRF sources
	$(PY) tools/check_drift.py

packages:      ## assert every client tree is package-ready
	$(PY) tools/check_packages.py

smoke:         ## allowlist smoke via the Python client
	$(PY) tests/allowlist_smoke.py

test:          ## run the suite for all languages (SDK_LANG=… FAST=1)
	$(PY) -m tests.run_all $(if $(SDK_LANG),--lang $(SDK_LANG),) $(if $(filter 1,$(FAST)),--skip-python-allowlist,)

ci:            ## drift + package layout + multi-language tests
	$(PY) tools/ci_gates.py $(if $(filter 1,$(REBUILD)),--rebuild,)
