# indox Developer Documentation

Welcome. This is the public documentation for the **indox** file-conversion platform.

If you are an external developer integrating with indox, you are in the right place. If you are an internal contributor looking for plans, decisions, or dashboards — see `design/` in the repository (not published here).

## What is indox

indox converts files — documents, images, audio, video, fonts — through a uniform REST API, spanning **6,022 conversions** across the platform.
<!-- 6,022 = mergedJsonData source of truth: frontend/src/lib/mergedJsonData.ts (image + video + docs + font pairs). Update this number if that dataset changes. -->

Conversions are asynchronous:

1. `POST /<service>/api/v1/convert/` → `202 { conversion_id }`
2. Poll `GET /conversion/{id}/` → terminal state
3. `GET /{id}/download/` → presigned URL

## Services

| Service | Base path | Formats |
|---|---|---|
| Documents | `/api/v1/pdf_handler/` | PDF, DOCX, ODT, RTF, HTML, MD, EPUB, … |
| Fonts | `/api/v1/fonts/` | TTF, OTF, WOFF, WOFF2, and 15 more |
| Billing | `/api/v1/subscription/` | plans, usage, credits |
| Auth | `/api/v1/user/` | profile, sessions, OIDC, social |

## Getting started

- [Quickstart](quickstart.md) — your first conversion in 5 minutes
- [Concepts](concepts.md) — auth, conversions, polling, credits
- [Limits](limits.md) — free quota, paid tiers, file size caps
- [Errors](errors.md) — error codes and what they mean

## Reference

- [API Reference](api/overview.md) — endpoint-by-endpoint
- [Official SDKs](sdk/index.md) — availability per language (none published yet — call the API directly)
- [Integrations](integrations/box.md) — Box, Dropbox, Google Drive, OneDrive
- [Client guides](client/README.md) — apps overview, architecture, dev setup
