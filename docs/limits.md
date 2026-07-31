# Limits

## Free tier (no auth)

| Resource | Limit |
|---|---|
| Conversions | **10 per IP per 30 days** |
| File size | **5 MB** per upload |
| Concurrent conversions | 1 |
| Output retention | 24 hours |

## Paid tier (authenticated)

| Resource | Limit |
|---|---|
| Conversions | Based on credit balance |
| File size | Plan-dependent (default 100 MB, enterprise up to 2 GB) |
| Concurrent conversions | Plan-dependent |
| Output retention | 30 days |

## Per-service notes

### Documents (`/api/v1/pdf_handler/`)
- Up to 500 pages per request (Pro tier+).
- PDF passwords stripped on conversion (you must provide the password if encrypted).

### Fonts (`/api/v1/fonts/`)
- 19 input formats, 19 output formats — 342 conversion routes.
- 1 credit per conversion regardless of engine.
- See [API → Fonts](api/fonts.md) for the format matrix.
