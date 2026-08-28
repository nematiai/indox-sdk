# indox-sdk — the 8 official API v1 clients, their codegen pipeline and gates.
# Config comes from .env at the repo root — internal, git-ignored, not published.
ROOT := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
PY = cd $(ROOT) && PYTHONPATH=$(ROOT) python3

PY_DIR = $(ROOT)/languages/python
# Build/publish tooling lives in a repo-local venv (git-ignored) — self-contained,
# nothing installed system-wide. Only `gen`/`gen-all` need Docker, because
# openapi-generator is only distributed as an image.
VENV = $(PY_DIR)/.venv
VPY  = $(VENV)/bin/python
STAMP = $(VENV)/.build-deps

.PHONY: help openapi openapi-drf gen gen-all drift packages smoke convert-inventory convert-test test test-all test-clean ci version bump build dist-check publish release
.DEFAULT_GOAL := help

# The convert/media routes are DRF, not ninja, so they are absent from
# /api/v1/openapi.json and reach the spec only through this dump. It is a
# git-ignored local file — it exposes internal routes, so it is never published;
# this target is the only way to refresh it, and 30 of the 114 allowlist ops are
# gated against it.
INDOX_CONTAINER ?= indox-django

help:          ## list targets
	@grep -hE '^[a-z0-9-]+:.*##' $(MAKEFILE_LIST) | sort | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

openapi-drf:   ## re-dump spec/openapi-drf.json from the running backend container
	@docker exec -w /app/indox $(INDOX_CONTAINER) python manage.py spectacular \
	   --format openapi-json > $(ROOT)/spec/openapi-drf.json.tmp
	@python3 -c "import json,sys; json.load(open('$(ROOT)/spec/openapi-drf.json.tmp'))" \
	   || { rm -f $(ROOT)/spec/openapi-drf.json.tmp; echo "spectacular produced invalid JSON"; exit 1; }
	@mv $(ROOT)/spec/openapi-drf.json.tmp $(ROOT)/spec/openapi-drf.json
	@echo "refreshed spec/openapi-drf.json from $(INDOX_CONTAINER)"

openapi: openapi-drf  ## rebuild spec/openapi-public.json from the live API + a fresh DRF dump
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

convert-inventory: ## list/assert all live convert formats + routes (fonts/pdf/image/video/model)
	$(PY) -m tests.test_convert_inventory

convert-test:  ## convert every colab/*/samples file to every valid output (CONVERT_MAX_JOBS=N to cap)
	$(PY) -m tests.test_convert_samples

test:          ## run the suite for all languages (SDK_LANG=… FAST=1)
	$(PY) -m tests.run_all $(if $(SDK_LANG),--lang $(SDK_LANG),) $(if $(filter 1,$(FAST)),--skip-python-allowlist,)

test-all:      ## run every language, using Docker for missing toolchains (CLEAN=1 to drop each image after use)
	SDK_DOCKER=1 $(if $(filter 1,$(CLEAN)),SDK_DOCKER_CLEAN=1,) $(MAKE) test

test-clean:    ## report which toolchain images are on this host (removes nothing — see its output)
	$(PY) -m tests.run_all --clean-images

ci:            ## drift + package layout + multi-language tests
	$(PY) tools/ci_gates.py $(if $(filter 1,$(REBUILD)),--rebuild,)

# ── Python release ────────────────────────────────────────────────────────────
# A PyPI version can never be reused, so `publish` runs the guards first and
# refuses on an already-published version or a dirty tree. The token comes from
# the environment (PYPI_TOKEN) — never a literal, never echoed.

version:       ## print the version the next build will carry
	@$(PY) tools/release.py --print-version

bump:          ## set the version (SDK_VERSION=0.4.1)
	@test -n "$(SDK_VERSION)" || { echo "Usage: make bump SDK_VERSION=0.4.1"; exit 1; }
	@$(PY) tools/release.py --set-version $(SDK_VERSION)

# Stamped on the pip install, not on the directory: a venv that exists but is
# missing build/twine must still re-provision, or `make publish` dies mid-release.
$(STAMP): ## create the repo-local build venv
	python3 -m venv --clear $(VENV)
	$(VPY) -m pip install -q --upgrade pip build twine
	touch $(STAMP)

build: $(STAMP)  ## build sdist + wheel
	rm -rf $(PY_DIR)/dist $(PY_DIR)/build $(PY_DIR)/*.egg-info
	cp $(ROOT)/LICENSE $(PY_DIR)/LICENSE
	cd $(PY_DIR) && $(VPY) -m build
	@ls -1 $(PY_DIR)/dist

dist-check: $(STAMP)  ## twine check + install the wheel into a throwaway venv and import it
	cd $(PY_DIR) && $(VPY) -m twine check dist/*
	rm -rf $(PY_DIR)/.venv-verify && python3 -m venv $(PY_DIR)/.venv-verify
	$(PY_DIR)/.venv-verify/bin/pip install -q $(PY_DIR)/dist/*.whl
	$(PY_DIR)/.venv-verify/bin/python -c "from indox_client import Indox, __version__; \
	  print('import OK', __version__, Indox(api_key='x').base_url)"
	rm -rf $(PY_DIR)/.venv-verify

publish: $(STAMP)  ## upload to PyPI (token from env or .env; TESTPYPI=1 to rehearse)
	@tok=$${PYPI_TOKEN:-$$(sed -n 's/^PYPI_TOKEN=//p' $(ROOT)/.env 2>/dev/null | tail -1)}; \
	 test -n "$$tok" || { echo "No PYPI_TOKEN in the environment or $(ROOT)/.env"; exit 1; }
	@$(PY) tools/release.py --guard
	$(MAKE) build dist-check
	@tok=$${PYPI_TOKEN:-$$(sed -n 's/^PYPI_TOKEN=//p' $(ROOT)/.env 2>/dev/null | tail -1)}; \
	 cd $(PY_DIR) && TWINE_USERNAME=__token__ TWINE_PASSWORD="$$tok" $(VPY) -m twine upload \
	   $(if $(filter 1,$(TESTPYPI)),--repository-url https://test.pypi.org/legacy/,) dist/*

release:       ## +1 the version, then build → check → publish → tag → push
	@$(PY) tools/release.py --bump-patch
	@v=$$($(PY) tools/release.py --print-version); \
	 git -C $(ROOT) add languages/python/indox_client/_version.py && \
	 git -C $(ROOT) commit -q -m "release: indox-client $$v" && echo "committed release: indox-client $$v"
	$(MAKE) publish
	@v=$$($(PY) tools/release.py --print-version); \
	 git -C $(ROOT) tag -a "python-v$$v" -m "indox-client $$v" && \
	 git -C $(ROOT) push -q origin production "python-v$$v" && echo "pushed production + python-v$$v"
