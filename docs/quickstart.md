# Quickstart

Convert your first file in 5 minutes.

## 1. Authentication

Free-tier conversions need **no credentials** — skip straight to step 2.

For authenticated (higher-quota) requests, send your Indox `external_token` as a Bearer header on every call:

```
Authorization: Bearer <external_token>
```

Tokens are issued by Google/Apple sign-in or OIDC — see [Auth](api/auth.md). The `Authorization` header is optional on free-tier requests.

## 2. Start a conversion

```bash
curl -X POST https://indox.org/api/v1/pdf_handler/convert/ \
  -H "Authorization: Bearer eyJ…" \
  -F "file=@report.docx" \
  -F "target_format=pdf"
```

Response (`202 Accepted`):

```json
{
  "conversion_id": "8f3c…",
  "status": "pending"
}
```

## 3. Poll status

```bash
curl https://indox.org/api/v1/pdf_handler/conversion/8f3c…/ \
  -H "Authorization: Bearer eyJ…"
```

Until `status` is `completed` (or `failed`).

## 4. Download

```bash
curl -L https://indox.org/api/v1/pdf_handler/8f3c…/download/ \
  -H "Authorization: Bearer eyJ…" \
  -o report.pdf
```

That's it. See [Concepts](concepts.md) for what each piece does, and [Limits](limits.md) for free-tier and paid quotas.
