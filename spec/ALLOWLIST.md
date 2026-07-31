# Public SDK allowlist (API v1)

**Status:** ✅ frozen (Phase 00) — P0–P3 is the v1 SDK surface  
**Auth:** `Authorization: Bearer <api_key>` (primary)  
**Not in SDK:** anything under Blocked; all `/subscription/admin/*`

Legend: **P0–P3** = v1 SDK release · **P4** = later · **ADV** = advanced (same app, ship after core convert)

**Official SDK languages (keep):** Python · TypeScript (covers JS) · PHP · Ruby · Java · C# · Go · Rust.  
**Never as SDKs:** SQL · HTML/CSS. **Deferred:** C++ · R · Kotlin · Swift.

Paths verified against local inventory 2026-07-30 (`design/audit/app/`). Prefer canonical `/api/v1/convert/{image|video|model}/` in docs; legacy aliases remain on server.

---

## P0 — Core convert

### fonts (`/api/v1/fonts/`)

| Method | Path | SDK |
|---|---|---|
| GET | `/api/v1/fonts/formats/` | P0 |
| GET | `/api/v1/fonts/formats/{input_format}/` | P0 |
| GET | `/api/v1/fonts/quota/` | P0 |
| GET | `/api/v1/fonts/health/` | P0 (optional in client) |
| GET | `/api/v1/fonts/routes/` | omit from SDK (debug) |
| POST | `/api/v1/fonts/upload/` | P0 |
| POST | `/api/v1/fonts/convert/` | P0 |
| POST | `/api/v1/fonts/validate/` | P0 |
| POST | `/api/v1/fonts/inspect/` | P0 |
| GET | `/api/v1/fonts/inspect/` | P0 |
| GET | `/api/v1/fonts/conversion/{conversion_id}/` | P0 |
| GET | `/api/v1/fonts/{conversion_id}/download/` | P0 |
| GET | `/api/v1/fonts/{conversion_id}/download/{filename}` | P0 |

### pdf_handler (`/api/v1/pdf_handler/`)

| Method | Path | SDK |
|---|---|---|
| GET | `/api/v1/pdf_handler/formats/` | P0 |
| GET | `/api/v1/pdf_handler/operations/` | P0 |
| POST | `/api/v1/pdf_handler/convert/` | P0 |
| POST | `/api/v1/pdf_handler/convert/json/` | P0 |
| POST | `/api/v1/pdf_handler/form-fields/` | P0 |
| POST | `/api/v1/pdf_handler/save/` | P0 |
| GET | `/api/v1/pdf_handler/history/` | P0 |
| GET | `/api/v1/pdf_handler/conversion/{conversion_id}/` | P0 |
| GET | `/api/v1/pdf_handler/{conversion_id}/download/` | P0 |
| GET | `/api/v1/pdf_handler/selftest/` | **omit** (internal) |
| GET/POST/DELETE | `/api/v1/pdf_handler/pipeline…` | ADV |
| * | `/api/v1/pdf_handler/scan…` | ADV |
| * | `/api/v1/pdf_handler/signing…` | ADV (fix non-UUID 500 before examples) |

### docs_core

| Method | Path | SDK |
|---|---|---|
| GET | `/api/v1/docs_core/credits/` | P0 |
| GET | `/api/v1/docs_core/conversion/{conversion_id}/` | P0 |
| GET | `/api/v1/docs_core/conversion/wait/{conversion_id}/` | P0 |
| POST | `/api/v1/docs_core/batch/collect/` | P0 |
| GET | `/api/v1/docs_core/batch/{batch_id}/download/` | P0 |
| POST | `/api/v1/docs_core/visibility/hide/` | P0 |
| GET | `/api/v1/docs_core/selftest/docs/` | **omit** |

### media_core

| Method | Path | SDK |
|---|---|---|
| GET | `/api/v1/media_core/health/` | P0 |
| GET | `/api/v1/media_core/credits/` | P0 |
| GET | `/api/v1/media_core/conversion/{conversion_id}/` | P0 |
| GET | `/api/v1/media_core/conversion/wait/{conversion_id}/` | P0 |
| GET | `/api/v1/media_core/files/{conversion_id}/download/` | P0 |
| POST | `/api/v1/media_core/batch/collect/` | P0 |
| GET | `/api/v1/media_core/batch/{batch_id}/download/` | P0 |
| POST | `/api/v1/media_core/visibility/hide/` | P0 |
| GET | `/api/v1/media_core/selftest/` | **omit** |

### image (canonical + legacy)

| Method | Path | SDK |
|---|---|---|
| POST | `/api/v1/convert/image/convert/` | P0 |
| GET | `/api/v1/convert/image/conversion/{conversion_id}/` | P0 |
| GET | `/api/v1/convert/image/formats/` | P0 |
| GET | `/api/v1/convert/image/operations/` | P0 |
| GET | `/api/v1/convert/image/history/` | P0 |
| POST | `/api/v1/image_converter/convert/` | P0 legacy alias |
| GET | `/api/v1/image_converter/conversion/{conversion_id}/` | P0 legacy |
| GET | `/api/v1/image_converter/formats/` | P0 legacy |
| GET | `/api/v1/image_converter/operations/` | P0 legacy |
| GET | `/api/v1/image_converter/history/` | P0 legacy |

### video

| Method | Path | SDK |
|---|---|---|
| POST | `/api/v1/convert/video/convert/` | P0 |
| GET | `/api/v1/convert/video/formats/` | P0 |
| POST | `/api/v1/video_converter/convert/` | P0 legacy |
| GET | `/api/v1/video_converter/formats/` | P0 legacy |

### model

| Method | Path | SDK |
|---|---|---|
| POST | `/api/v1/convert/model/convert/` | P0 |
| GET | `/api/v1/convert/model/conversion/{conversion_id}/` | P0 |
| GET | `/api/v1/convert/model/formats/` | P0 |
| GET | `/api/v1/convert/model/operations/` | P0 |
| POST | `/api/v1/model/convert/` | P0 legacy |
| GET | `/api/v1/model/conversion/{conversion_id}/` | P0 legacy |
| GET | `/api/v1/model/formats/` | P0 legacy |
| GET | `/api/v1/model/operations/` | P0 legacy |

### health

| Method | Path | SDK |
|---|---|---|
| GET | `/api/v1/health/` | P0 |

---

## P1 — Webhooks

| Method | Path | SDK |
|---|---|---|
| GET | `/api/v1/webhooks/` | P1 |
| POST | `/api/v1/webhooks/` | P1 |
| GET | `/api/v1/webhooks/{webhook_id}/` | P1 |
| PATCH | `/api/v1/webhooks/{webhook_id}/` | P1 |
| DELETE | `/api/v1/webhooks/{webhook_id}/` | P1 |
| GET | `/api/v1/webhooks/{webhook_id}/deliveries/` | P1 |
| POST | `/api/v1/webhooks/{webhook_id}/test/` | P1 |

---

## P2 — User (subset)

| Method | Path | SDK |
|---|---|---|
| POST | `/api/v1/user/auth/login/` | P2 |
| POST | `/api/v1/user/auth/logout/` | P2 |
| GET | `/api/v1/user/me/` | P2 |
| PATCH | `/api/v1/user/me/` | P2 |
| GET | `/api/v1/user/storage/files/` | P2 |
| POST | `/api/v1/user/storage/files/upload/` | P2 |
| POST | `/api/v1/user/storage/files/register/` | P2 |
| POST | `/api/v1/user/storage/files/download/` | P2 |
| POST | `/api/v1/user/storage/files/download/zip/` | P2 |
| POST | `/api/v1/user/storage/files/delete/` | P2 |
| GET | `/api/v1/user/usage/` | P2 |
| GET | `/api/v1/user/usage/summary/` | P2 |
| GET | `/api/v1/user/usage/trend/` | P2 |
| GET | `/api/v1/user/usage/recent-conversions/` | P2 |
| GET | `/api/v1/user/usage/conversions/{conversion_id}/` | P2 |
| GET | `/api/v1/user/shares/` | P2 |
| POST | `/api/v1/user/shares/` | P2 |
| DELETE | `/api/v1/user/shares/{link_id}/` | P2 |
| GET | `/api/v1/user/shares/public/{token}/` | P2 |
| POST | `/api/v1/user/shares/public/{token}/download/` | P2 |

Omit from v1 SDK: notification inbox, notification-settings, session revoke (revisit later).

---

## P3 — Billing (non-admin)

| Method | Path | SDK |
|---|---|---|
| GET | `/api/v1/subscription/credits/balance/` | P3 |
| POST | `/api/v1/subscription/credits/promo-code/` | P3 |
| GET | `/api/v1/subscription/pricing_plan/` | P3 |
| POST | `/api/v1/subscription/purchase_initiate/` | P3 |
| POST | `/api/v1/subscription/purchase_initiate/pay-as-you-go/` | P3 |
| GET | `/api/v1/subscription/purchase_initiate/callback/` | P3 |
| GET | `/api/v1/subscription/purchase_history/` | P3 |
| POST | `/api/v1/subscription/storage/initiate/` | P3 |
| GET | `/api/v1/subscription/storage/callback/` | P3 |
| POST | `/api/v1/subscription/tasks/task-completion/` | P3 |
| GET | `/api/v1/subscription/tasks/task-history/` | P3 |

**Blocked:** `/api/v1/subscription/admin/**`

---

## P4 — Cloud integrations (later)

| Prefix | Ops |
|---|---|
| `/api/v1/storage/{box\|dropbox\|google\|onedrive}/` | authorize, status, contents, disconnect |
| `/api/v1/{box\|dropbox\|google\|onedrive}_integration/` | same (legacy/parallel) |

---

## Blocked (never in public SDK)

| Area | Prefix / note |
|---|---|
| business | `/api/v1/business/**` |
| audit | `/api/v1/audit/**` |
| oidc | `/api/v1/oidc/**` |
| social_auth | `/api/v1/social/**` |
| notifications preview | `/api/v1/notifications/email-template/**` |
| subscription admin | `/api/v1/subscription/admin/**` |
| swagger / admin HTML | secret paths |
| selftest | `**/selftest**` as SDK methods |

---

## Counts (approx)

| Tier | Ops |
|---|---:|
| P0 (incl. legacy aliases, excl. omit/ADV) | ~70–80 |
| P1 | 7 |
| P2 | ~20 |
| P3 | 11 |
| **v1 SDK total** | **~90–110** |
| P4 | ~32 |
| Blocked | ~40+ |

Update this file when routes change; Phase 07 CI must fail on drift.
