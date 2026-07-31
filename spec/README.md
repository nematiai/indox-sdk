# API v1 — Official SDKs (multi-language)

**Status:** 🟨 package-ready + tests green (registry publish pending approval)  
**Owner:** backend + docs (public)  
**Depends on:** OpenAPI public filter (`openapi-public.json`); frozen allowlist  
**Related:** `indox_client/` (Python), `sdk/`, `sdk/tests/`, `docs/sdk/`

## Goal

Ship **official API v1 SDKs** for:

| Language | Package (proposed) | Status today |
|---|---|---|
| Python | `indox-client` **0.4.0** | ✅ P0–P3 + PDF ADV; allowlist smoke green |
| TypeScript | `@indox/sdk` (covers JavaScript) | ✅ package-ready + `sdk/tests` |
| PHP | `indox/indox` (Packagist) | ✅ package-ready + `sdk/tests` |
| Ruby | `indox` (RubyGems) | ✅ package-ready + `sdk/tests` |
| Java | `org.indox:indox-sdk` (Maven) | ✅ package-ready + `sdk/tests` |
| C# | `Indox.Sdk` (NuGet) | ✅ package-ready + `sdk/tests` |
| Go | `github.com/nematiai/indox-go` | ✅ package-ready + `sdk/tests` |
| Rust | `indox` / `indox-sdk` (crates.io) | ✅ package-ready + `sdk/tests` |

**Removed from SDK program:** SQL, HTML/CSS (not HTTP clients). **Deferred:** C++, R, Kotlin, Swift.

**Marketing rule:** do **not** claim “official SDKs are available” until that package is published and covers the frozen public allowlist (P0 minimum).

## Phase board

| Phase | Title | Status |
|---|---|---|
| 00 | Freeze public allowlist + auth contract | ✅ |
| 01 | OpenAPI: public filter + DRF spectacular merge | ✅ synth ops **0** |
| 02 | Python SDK → P0–P3 parity | ✅ 0.4.0 |
| 03 | Codegen pipeline | ✅ `make sdk-gen` |
| 04–05 | TS → PHP → Ruby → Java → C# → Go → Rust | ✅ package-ready (publish pending) |
| 06 | Public docs status table | ✅ `docs/sdk/index.md` |
| 07 | Live smoke + CI + multi-lang tests | ✅ `make sdk-ci` / `sdk-test` |

## How to build / test

```bash
make sdk-openapi          # dump DRF + rebuild openapi-public.json
make sdk-gen LANG=typescript
make sdk-ci               # drift + packages + fast multi-lang tests
make sdk-test             # all langs (+ full Python allowlist)
make sdk-test FAST=1      # skip 79-probe Python allowlist
make sdk-test LANG=go
```

Files: [ALLOWLIST.md](./ALLOWLIST.md) · [openapi-public.json](./openapi-public.json) · [openapi-drf.json](./openapi-drf.json) · [PLAN.md](./PLAN.md)
