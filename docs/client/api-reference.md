# API Reference

Base URL: `https://indox.org` — every path below is absolute from it and already carries its
`/api/v1/` prefix. Running your own instance? Substitute your host; the paths are identical.

## Authentication

```
Authorization: Bearer <api_key>
```

The `Auth` column in every table below says whether a request needs that header:

| Value | Meaning |
|---|---|
| **Bearer** | The endpoint returns `401`/`403` without a token. |
| **—** | The endpoint is reachable without a token. Anonymous requests are served within the [free quota](../limits.md); sending a token attributes the job to your account and applies your plan's limits instead. |

Browser clients authenticated by session cookie may send the cookie instead of the header — the
backend accepts either. See [Concepts](../concepts.md) for the full auth model.

## Async conversion flow

Conversions do not block. Every convert endpoint returns `202 { "conversion_id": ... }`; you then
poll the matching status endpoint for that media family and download when it reaches a terminal
state.

| Media family | Submit | Poll status | Download |
|---|---|---|---|
| Documents / PDF | `POST /api/v1/pdf_handler/convert/` | `GET /api/v1/docs_core/conversion/{conversion_id}/` | `GET /api/v1/pdf_handler/{conversion_id}/download/` |
| Fonts | `POST /api/v1/fonts/convert/` | `GET /api/v1/fonts/conversion/{conversion_id}/` | `GET /api/v1/fonts/{conversion_id}/download/` |
| Images / video / 3D | `POST /api/v1/convert/{image\|video\|model}/convert/` | `GET /api/v1/media_core/conversion/{conversion_id}/` | `GET /api/v1/media_core/files/{conversion_id}/download/` |

`GET /api/v1/docs_core/conversion/wait/{conversion_id}/` and
`GET /api/v1/media_core/conversion/wait/{conversion_id}/` long-poll instead of returning
immediately, if you would rather not implement a poll loop.

---

## Health

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/health/` | — | Health probe — DB, cache, storage, Celery broker |

## Documents

Document and PDF conversion. Job status, credits and batching for this family live under
`/api/v1/docs_core/` below.

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/pdf_handler/formats/` | — | Supported document types |
| `GET` | `/api/v1/pdf_handler/operations/` | — | Operations available for a from/to pair |
| `POST` | `/api/v1/pdf_handler/convert/` | — | Convert a document (multipart) |
| `POST` | `/api/v1/pdf_handler/convert/json/` | — | Convert a document (JSON body) |
| `POST` | `/api/v1/pdf_handler/form-fields/` | — | List the fillable form fields in a PDF |
| `POST` | `/api/v1/pdf_handler/save/` | — | Save an edited PDF and deliver it to a destination |
| `GET` | `/api/v1/pdf_handler/history/` | — | List conversion history |
| `GET` | `/api/v1/pdf_handler/conversion/{conversion_id}/` | — | Get conversion status |
| `GET` | `/api/v1/pdf_handler/{conversion_id}/download/` | — | Download the converted file |

### Document jobs — status, credits, batching

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/docs_core/conversion/{conversion_id}/` | — | Conversion info |
| `GET` | `/api/v1/docs_core/conversion/wait/{conversion_id}/` | — | Long-poll until the conversion settles |
| `POST` | `/api/v1/docs_core/batch/collect/` | — | Collect several conversions into one ZIP |
| `GET` | `/api/v1/docs_core/batch/{batch_id}/download/` | — | Download the batch ZIP |
| `GET` | `/api/v1/docs_core/credits/` | — | Remaining credits |
| `POST` | `/api/v1/docs_core/visibility/hide/` | — | Hide items from history |

### PDF pipelines

Saved, replayable sequences of PDF operations.

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/pdf_handler/pipeline/` | Bearer | List saved pipelines |
| `POST` | `/api/v1/pdf_handler/pipeline/` | Bearer | Create a saved pipeline |
| `GET` | `/api/v1/pdf_handler/pipeline/{pipeline_id}/` | Bearer | Get a saved pipeline |
| `DELETE` | `/api/v1/pdf_handler/pipeline/{pipeline_id}/` | Bearer | Delete a saved pipeline |
| `POST` | `/api/v1/pdf_handler/pipeline/{pipeline_id}/run/` | Bearer | Run a saved pipeline on a PDF |

### Phone scan

Pair a phone to a desktop session, capture pages, assemble them into a PDF.

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/pdf_handler/scan/sessions/` | Bearer | Open a phone-scan session |
| `GET` | `/api/v1/pdf_handler/scan/sessions/{session_id}/` | Bearer | Poll a phone-scan session |
| `POST` | `/api/v1/pdf_handler/scan/sessions/{session_id}/finalize/` | Bearer | Queue assembly of the captured pages into a PDF |
| `GET` | `/api/v1/pdf_handler/scan/pair/` | Bearer | Phone: read a paired scan session |
| `POST` | `/api/v1/pdf_handler/scan/pair/pages/` | — | Phone: upload a captured page |
| `DELETE` | `/api/v1/pdf_handler/scan/pair/pages/{page_id}/` | Bearer | Phone: discard a captured page |

### E-signing

The session owner authenticates; each participant acts through a per-recipient `{token}`, so the
participant routes take no bearer token.

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/pdf_handler/signing/sessions/` | Bearer | Create a multi-party signing session |
| `GET` | `/api/v1/pdf_handler/signing/sessions/{session_id}/` | Bearer | Get a signing session |
| `GET` | `/api/v1/pdf_handler/signing/sign/{token}/` | — | Participant: view a document to sign |
| `POST` | `/api/v1/pdf_handler/signing/sign/{token}/` | — | Participant: sign |
| `POST` | `/api/v1/pdf_handler/signing/sign/{token}/decline/` | — | Participant: decline |

## Fonts

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/fonts/formats/` | — | List font formats |
| `GET` | `/api/v1/fonts/formats/{input_format}/` | — | Output formats available for an input format |
| `POST` | `/api/v1/fonts/upload/` | — | Upload a font to object storage |
| `POST` | `/api/v1/fonts/convert/` | — | Convert an uploaded font by key |
| `POST` | `/api/v1/fonts/validate/` | — | Validate a conversion before running it |
| `POST` | `/api/v1/fonts/inspect/` | — | Inspect an uploaded font file |
| `GET` | `/api/v1/fonts/inspect/` | — | Inspect a stored font by key |
| `GET` | `/api/v1/fonts/conversion/{conversion_id}/` | — | Get font conversion info |
| `GET` | `/api/v1/fonts/{conversion_id}/download/` | — | Download the converted font |
| `GET` | `/api/v1/fonts/{conversion_id}/download/{filename}` | — | Download the converted font under a chosen filename |
| `GET` | `/api/v1/fonts/quota/` | — | Remaining font quota |
| `GET` | `/api/v1/fonts/health/` | — | Font service health |

## Images, video and 3D models

Three media families share one path shape. Job status, downloads and credits for all three go
through `/api/v1/media_core/` below.

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/convert/image/formats/` | — | List image formats |
| `GET` | `/api/v1/convert/image/operations/` | — | List image operations |
| `POST` | `/api/v1/convert/image/convert/` | — | Convert an image |
| `GET` | `/api/v1/convert/image/conversion/{conversion_id}/` | — | Retrieve image conversion info |
| `GET` | `/api/v1/convert/image/history/` | Bearer | List image conversion history |
| `GET` | `/api/v1/convert/video/formats/` | — | List video formats |
| `POST` | `/api/v1/convert/video/convert/` | — | Convert a video |
| `GET` | `/api/v1/convert/model/formats/` | — | List 3D model formats |
| `GET` | `/api/v1/convert/model/operations/` | — | List 3D model operations |
| `POST` | `/api/v1/convert/model/convert/` | — | Convert a 3D model |
| `GET` | `/api/v1/convert/model/conversion/{conversion_id}/` | — | Retrieve 3D model conversion info |

Video conversions have no dedicated status route — poll
`GET /api/v1/media_core/conversion/{conversion_id}/`.

### Media jobs — status, downloads, credits

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/media_core/conversion/{conversion_id}/` | — | Unified download link for a media conversion |
| `GET` | `/api/v1/media_core/conversion/wait/{conversion_id}/` | — | Long-poll until the conversion or batch settles |
| `GET` | `/api/v1/media_core/files/{conversion_id}/download/` | — | Download the converted media file |
| `POST` | `/api/v1/media_core/batch/collect/` | Bearer | Collect several items into one ZIP |
| `GET` | `/api/v1/media_core/batch/{batch_id}/download/` | — | Download the batch ZIP |
| `GET` | `/api/v1/media_core/credits/` | — | Remaining credits |
| `POST` | `/api/v1/media_core/visibility/hide/` | — | Hide items from history |
| `GET` | `/api/v1/media_core/health/` | — | Media service health |

## User

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/api/v1/user/auth/login/` | — | Log in with username/email + password, Google OAuth or Apple Sign-In |
| `POST` | `/api/v1/user/auth/logout/` | — | Log out |
| `GET` | `/api/v1/user/me/` | Bearer | Current user profile |
| `PATCH` | `/api/v1/user/me/` | Bearer | Update the current user profile |
| `GET` | `/api/v1/user/usage/` | Bearer | Assigned pricing plans |
| `GET` | `/api/v1/user/usage/summary/` | Bearer | Usage summary |
| `GET` | `/api/v1/user/usage/trend/` | Bearer | Conversion trend over time |
| `GET` | `/api/v1/user/usage/recent-conversions/` | Bearer | Recent conversions |
| `GET` | `/api/v1/user/usage/conversions/{conversion_id}/` | Bearer | Detailed conversion record |

## Storage

Files the account owns — uploads and conversion outputs alike.

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/user/storage/files/` | Bearer | List user-managed files |
| `POST` | `/api/v1/user/storage/files/upload/` | Bearer | Upload a new file to the account's storage |
| `POST` | `/api/v1/user/storage/files/register/` | Bearer | Register an existing object as a user-managed file |
| `POST` | `/api/v1/user/storage/files/download/` | Bearer | Generate download URLs for stored files |
| `POST` | `/api/v1/user/storage/files/download/zip/` | Bearer | Download stored files as a ZIP archive |
| `POST` | `/api/v1/user/storage/files/delete/` | Bearer | Delete stored files and reclaim storage |

## Shares

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/user/shares/` | Bearer | List the caller's share links |
| `POST` | `/api/v1/user/shares/` | Bearer | Create a share link for a file the caller owns |
| `DELETE` | `/api/v1/user/shares/{link_id}/` | Bearer | Revoke a share link |
| `GET` | `/api/v1/user/shares/public/{token}/` | — | Public share metadata — never returns the file itself |
| `POST` | `/api/v1/user/shares/public/{token}/download/` | — | Redeem a share link for a download URL |

## Billing

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/subscription/pricing_plan/` | — | Structured pricing plans |
| `GET` | `/api/v1/subscription/credits/balance/` | Bearer | Credit balance |
| `POST` | `/api/v1/subscription/credits/promo-code/` | Bearer | Redeem a promo code for credits |
| `GET` | `/api/v1/subscription/purchase_history/` | Bearer | Purchase history |
| `POST` | `/api/v1/subscription/purchase_initiate/` | Bearer | Start a subscription purchase |
| `POST` | `/api/v1/subscription/purchase_initiate/pay-as-you-go/` | Bearer | Start a pay-as-you-go purchase |
| `GET` | `/api/v1/subscription/purchase_initiate/callback/` | — | Stripe checkout return callback |
| `POST` | `/api/v1/subscription/storage/initiate/` | Bearer | Start a Stripe checkout for storage add-ons |
| `GET` | `/api/v1/subscription/storage/callback/` | — | Stripe storage checkout return callback |
| `POST` | `/api/v1/subscription/tasks/task-completion/` | Bearer | Report task completion and deduct credits |
| `GET` | `/api/v1/subscription/tasks/task-history/` | Bearer | Recent task completion history |

The two `callback/` routes are Stripe redirect targets, not endpoints you call directly.

## Webhooks

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/webhooks/` | Bearer | List the account's webhooks |
| `POST` | `/api/v1/webhooks/` | Bearer | Create a webhook — the raw secret is returned exactly once |
| `GET` | `/api/v1/webhooks/{webhook_id}/` | Bearer | Get one webhook |
| `PATCH` | `/api/v1/webhooks/{webhook_id}/` | Bearer | Update url / events / is_active / description |
| `DELETE` | `/api/v1/webhooks/{webhook_id}/` | Bearer | Delete a webhook and its delivery history |
| `GET` | `/api/v1/webhooks/{webhook_id}/deliveries/` | Bearer | Recent delivery attempts, newest first |
| `POST` | `/api/v1/webhooks/{webhook_id}/test/` | Bearer | Enqueue a test delivery |

---

## Notes

- **Send the trailing slash.** Every path above ends in `/` except
  `/api/v1/fonts/{conversion_id}/download/{filename}`. Omitting it makes a `GET` cost an extra
  `301` round trip, and a `POST` without the slash fails — send the exact path.
- **Legacy aliases.** The image, video and 3D routes are also served under `/api/v1/image_converter/`,
  `/api/v1/video_converter/` and `/api/v1/model/`. Those are legacy prefixes kept for older clients —
  use the `/api/v1/convert/{image|video|model}/` forms above in new code.
- **Not listed here:** internal, admin and self-test routes are outside the public surface and are
  not part of the API contract. This page covers the 101 public operations only.
- **Machine-readable schema.** The same surface is published as OpenAPI at
  `/api/v1/openapi.json` on any running instance; the [official SDKs](../sdk/index.md) are generated
  from it.
