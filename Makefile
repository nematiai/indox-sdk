# indox-sdk — the 8 official API v1 clients, their codegen pipeline and gates.
# Config comes from .env (see .env.example); nothing is hardcoded here.
ROOT := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))
PY = cd $(ROOT) && PYTHONPATH=$(ROOT) python3

PY_DIR = $(ROOT)/languages/python
# Builds and uploads run in an ephemeral container — nothing is installed on the host.
PY_IMAGE = python:3.12-slim
IN_PY = docker run --rm -u $$(id -u):$$(id -g) -v $(PY_DIR):/w -w /w -e HOME=/tmp \
          -e PATH=/tmp/.local/bin:/usr/local/bin:/usr/bin:/bin $(PY_IMAGE)

.PHONY: help openapi gen gen-all drift packages smoke test ci version bump build dist-check publish release
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

# ── Python release ────────────────────────────────────────────────────────────
# A PyPI version can never be reused, so `publish` runs the guards first and
# refuses on an already-published version or a dirty tree. The token comes from
# the environment (PYPI_TOKEN) — never a literal, never echoed.

version:       ## print the version the next build will carry
	@$(PY) tools/release.py --print-version

bump:          ## set the version (SDK_VERSION=0.4.1)
	@test -n "$(SDK_VERSION)" || { echo "Usage: make bump SDK_VERSION=0.4.1"; exit 1; }
	@$(PY) tools/release.py --set-version $(SDK_VERSION)

build:         ## build sdist + wheel in a container
	rm -rf $(PY_DIR)/dist $(PY_DIR)/build $(PY_DIR)/*.egg-info
	$(IN_PY) sh -c "pip install -q --user build && python -m build"
	@ls -1 $(PY_DIR)/dist

dist-check:    ## twine check + install the wheel clean and import it
	$(IN_PY) sh -c "pip install -q --user twine && python -m twine check dist/*"
	docker run --rm -v $(PY_DIR)/dist:/d $(PY_IMAGE) sh -c \
	  "pip install -q /d/*.whl && python -c 'from indox_client import Indox, __version__; \
	   print(\"import OK\", __version__, Indox(api_key=\"x\").base_url)'"

publish:       ## upload to PyPI (PYPI_TOKEN=… ; TESTPYPI=1 for test.pypi.org)
	@test -n "$$PYPI_TOKEN" || { echo "Set PYPI_TOKEN (export it; do not paste it into a file)"; exit 1; }
	@$(PY) tools/release.py --guard
	$(MAKE) build dist-check
	$(IN_PY) sh -c "pip install -q --user twine && python -m twine upload \
	  $(if $(filter 1,$(TESTPYPI)),--repository-url https://test.pypi.org/legacy/,) \
	  -u __token__ -p '$$PYPI_TOKEN' dist/*"

release:       ## guard → build → check → publish → tag → push (PYPI_TOKEN=…)
	$(MAKE) publish
	git -C $(ROOT) tag -a "python-v$$($(PY) tools/release.py --print-version)" \
	  -m "indox-client $$($(PY) tools/release.py --print-version)"
	git -C $(ROOT) push origin "python-v$$($(PY) tools/release.py --print-version)"
