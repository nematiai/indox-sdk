# Plan — API v1 official SDKs (6 languages)

**Status:** ⬜ planned  
**Created:** 2026-07-30  
**Source of truth for paths:** live `GET /api/v1/openapi.json` + DRF converter mounts (`config/urls/_converters.py`)  
**Audit evidence:** `design/audit/app/` (anon + auth smoke)

---

## 1. Problem

- Backend exposes ~**214** `/api/v1/` operations.
- Public Python SDK (`indox_client` / `indox-client`) implements **fonts only** (~11 useful ops).
- `Images` / `Videos` stubs raise `NotImplementedError`.
- No Node / PHP / Ruby / Java / .NET packages.
- Claiming “official PHP, Node.js, Python, Ruby, Java and .NET SDKs are available” is **false** until packages ship.

---

## 2. Goals

1. Freeze a **public allowlist** of endpoints API-key users may call via SDKs.
2. Make OpenAPI the single schema for that allowlist (including DRF convert routes).
3. Expand Python SDK to allowlist parity (P0–P3).
4. Generate/publish official SDKs: **Python, Node.js, PHP, Ruby, Java, .NET**.
5. Update public docs (`docs/`) only when each language is actually published.

Non-goals (this plan):

- Wrapping admin / OIDC provider / business / audit in SDKs.
- Building a separate shell CLI (optional later; not required for “SDK available”).
- Fixing unrelated API 5xx (tracked in audit; e.g. pdf_handler signing non-UUID) except where they block SDK acceptance tests.

---

## 3. Auth contract (all SDKs)

| Mechanism | Header / env | Audience |
|---|---|---|
| API key | `Authorization: Bearer ak_…` | Primary for SDKs |
| Env | `INDOX_API_KEY` (or language-idiomatic equiv) | Local / CI |
| Base URL | `INDOX_BASE_URL` default `https://indox.org` | Self-host / local |
| Optional | User `external_token` Bearer | Advanced (login flows); not required for P0 convert |

SDKs must never log keys or tokens.

---

## 4. Public surface tiers

### P0 — Core convert (must ship)

| App | Canonical prefix | Include |
|---|---|---|
| fonts | `/api/v1/fonts/` | convert, upload, validate, inspect, formats, quota, conversion status, download |
| pdf_handler | `/api/v1/pdf_handler/` | convert, convert/json, formats, operations, history, conversion status, download; **phase-2:** pipeline/scan/signing |
| docs_core | `/api/v1/docs_core/` | conversion get/wait, credits, batch collect/download, visibility hide |
| media_core | `/api/v1/media_core/` | conversion get/wait, credits, files download, batch, health (**exclude** selftest from public docs) |
| image | `/api/v1/convert/image/` (+ legacy `image_converter/`) | convert, status, formats, operations, history |
| video | `/api/v1/convert/video/` (+ legacy) | convert, formats |
| model | `/api/v1/convert/model/` (+ legacy) | convert, status, formats, operations |
| health | `/api/v1/health/` | GET |

Prefer documenting **canonical** `/api/v1/convert/{service}/` for image/video/model; keep legacy aliases working server-side.

### P1 — Webhooks

All `/api/v1/webhooks/` routes (list/create/get/patch/delete/deliveries/test).

### P2 — User (subset)

| Include | Exclude |
|---|---|
| `POST /user/auth/login/`, `logout/` | Session revoke-all (optional later) |
| `GET/PATCH /user/me/` | In-app notification inbox (product UI) |
| `/user/storage/files/*` | — |
| `/user/usage/*` | — |
| `/user/shares/*` | — |

API key CRUD stays dashboard-first until `/user/…/keys/` is mounted on the unified API again; document dashboard key creation until then.

### P3 — Billing (non-admin)

Include: credits balance, promo-code, pricing_plan, purchase_initiate (+ pay-as-you-go), purchase_history, storage initiate/callback, task-completion, task-history.  
**Exclude:** every `/api/v1/subscription/admin/*`.

### P4 — Integrations (later)

`/api/v1/storage/{provider}/…` and per-app `*_integration` authorize/status/contents/disconnect.

### Blocked from SDKs

`business`, `audit`, `oidc`, `social_auth`, admin billing, email-template preview, internal selftest as first-class SDK methods.

Exact METHOD+path table: [ALLOWLIST.md](./ALLOWLIST.md).

---

## 5. Phases

### Phase 00 — Freeze allowlist + auth contract

**Status:** ⬜  

- [ ] Approve P0–P3 as v1 SDK surface (this plan’s default).
- [ ] Mark P4 optional; blocked list explicit.
- [ ] Confirm API-key permission bits (`read`/`write`/…) map to allowlist methods.
- [ ] Keep `ALLOWLIST.md` in sync with OpenAPI tags/`x-indox-public: true` (or equivalent).

**Acceptance:** ALLOWLIST.md reviewed; no admin paths listed.

---

### Phase 01 — OpenAPI completeness

**Status:** ⬜  
**Depends on:** 00  

- [ ] Expose DRF image/video/model/media routes in the same OpenAPI document used by Swagger (`/api/v1/openapi.json`) **or** merge a second schema into a published `openapi-public.json`.
- [ ] Tag operations with stable `operationId`s (language-friendly).
- [ ] Add `x-indox-sdk-tier: p0|p1|p2|p3|internal` extension (or filter file generated from ALLOWLIST).
- [ ] Publish filtered `design/feature/sdk_api_v1/openapi-public.json` (or under `docs/`) for codegen.

**Acceptance:** Every P0–P3 path appears in the public schema; blocked paths absent.

**Blocker note:** Ninja schema today omits most DRF converter ops — must fix before multi-lang codegen.

---

### Phase 02 — Python SDK parity (`indox_client`)

**Status:** ⬜  
**Depends on:** 01 (can start P0 fonts/pdf against hand paths in parallel)  

- [ ] Implement resources: `fonts` (gap fill), `pdf`, `docs`, `media`, `images`, `videos`, `models`, `webhooks`, `user` (subset), `billing`/`subscription` (non-admin).
- [ ] Remove or implement `Images`/`Videos` stubs (no `NotImplementedError` on init).
- [ ] Helpers: `convert_and_download` / `wait` polling pattern reused across convert apps.
- [ ] Version bump (semver); changelog.
- [ ] Tests: unit + live optional (`LIVE_API_SMOKE` / existing `tests/test_indox_client_sdk.py` expanded).

**Acceptance:** Python client can exercise every P0–P3 allowlist path without raw `requests` in examples.

---

### Phase 03 — Codegen pipeline

**Status:** ⬜  
**Depends on:** 01  

- [ ] Choose generator (candidates: OpenAPI Generator, Stainless, Speakeasy, Kiota) — one pipeline for all langs.
- [ ] Repo layout proposal:
  - `sdk/python/` (or keep `indox_client/` as published tree)
  - `sdk/nodejs/`, `sdk/php/`, `sdk/ruby/`, `sdk/java/`, `sdk/dotnet/`
- [ ] CI job: schema → generate → compile/test smoke per language.
- [ ] Shared examples in `docs/sdk/` generated or verified from allowlist.

**Acceptance:** One command regenerates all six clients from `openapi-public.json`.

---

### Phase 04 — Node.js + PHP

**Status:** ⬜  
**Depends on:** 03, 02 patterns  

- [ ] Publish Node package to npm.
- [ ] Publish PHP package to Packagist.
- [ ] Auth + P0 convert + wait/download parity with Python.
- [ ] README + `docs/sdk/nodejs.md`, `docs/sdk/php.md`.

**Acceptance:** Install from registry; convert font + one image/pdf path works against staging/local.

---

### Phase 05 — Ruby + Java + .NET

**Status:** ⬜  
**Depends on:** 04  

- [ ] RubyGems, Maven Central (or GitHub Packages interim), NuGet.
- [ ] Same P0–P3 surface.
- [ ] Docs pages per language.

**Acceptance:** All three installable; CI smoke green.

---

### Phase 06 — Public docs marketing copy

**Status:** ⬜  
**Depends on:** each language’s publish  

Only then add (accurate) copy such as:

> For API v1, official PHP, Node.js, Python, Ruby, Java and .NET SDKs are available.

Until all six are published, docs must use a **status table** (Available / Planned), not a blanket claim.

- [ ] Update `docs/index.md`, `docs/sdk/`, `docs/client/`.
- [ ] Deep-link package registries.
- [ ] MkDocs nav entries.

**Acceptance:** No false “available” claims; status table matches registries.

---

### Phase 07 — Verification harness

**Status:** ⬜  
**Depends on:** 02+  

- [ ] Extend `common.testing.api_smoke` / allowlist fixture: “public SDK paths only”.
- [ ] Per-language smoke in CI (or weekly) with `api_audit_smoke` API key.
- [ ] Fail CI if OpenAPI public filter drifts from ALLOWLIST.md.

**Acceptance:** Drift detected automatically; pdf_handler known 5xx either fixed or excluded from signing paths in allowlist (signing optional P0.b).

---

## 6. Rollout order (recommended)

```text
Allowlist → OpenAPI public schema → Python parity
    → Codegen pipeline → Node + PHP → Ruby + Java + .NET → Docs claim
```

Do **not** announce six languages after Python-only fonts.

---

## 7. Risks

| Risk | Mitigation |
|---|---|
| OpenAPI missing DRF routes | Phase 01 gate; no codegen until green |
| Six hand-written SDKs drift | Mandatory codegen |
| Admin paths leak into SDK | ALLOWLIST + schema filter + CI |
| Claiming availability early | Phase 06 gated per language |
| pdf_handler signing 500 on bad UUID | Exclude from P0 or fix before SDK examples use signing |

---

## 8. Effort (rough)

| Phase | Effort |
|---|---|
| 00 Allowlist | 0.5 d |
| 01 OpenAPI | 2–4 d |
| 02 Python parity | 5–8 d |
| 03 Codegen pipeline | 3–5 d |
| 04 Node + PHP | 3–5 d (with codegen) |
| 05 Ruby + Java + .NET | 4–6 d |
| 06 Docs | 1 d |
| 07 Harness | 2 d |

---

## 9. Decide (product)

Default baked into this plan: **P0+P1+P2+P3**, six languages via codegen, docs claim only when true.

If product prefers smaller first ship: cut to **P0 only** for all six, then expand tiers — update ALLOWLIST.md and phase board accordingly.
