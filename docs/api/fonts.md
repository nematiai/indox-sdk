# Font Conversion API

Base path: `/api/v1/fonts/`

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/upload/` | Upload font file → returns `s3_key` |
| `POST` | `/convert/` | Convert from `s3_key` → `202 { id, status }` |
| `GET`  | `/conversion/{id}/` | Poll conversion status |
| `GET`  | `/{id}/download/` | Redirect to presigned URL |
| `POST` | `/validate/` | Check if conversion is supported without executing |

## Supported formats

**19 formats, 342 routes**, served by 2 engines:

| Engine | Inputs | Outputs |
|---|---|---|
| `fonttools` (fast) | ttf, otf, woff, woff2 | ttf, otf, woff, woff2 |
| `fontforge` (full) | + eot, svg, pfa, pfb, ufo, dfont, ttc, bdf, pt3, t42, cff, sfd, fon, fnt, otb | same set |

`fonttools` is tried first when the route is supported; falls back to `fontforge` for anything else.

## Limits

- Free: 10 conversions / IP / 30 days, 5 MB max input.
- Paid: 1 credit per conversion, plan-dependent size cap.

## Worked example

```bash
# 1. Upload
curl -X POST https://indox.org/api/v1/fonts/upload/ \
  -H "Authorization: Bearer eyJ…" \
  -F "file=@MyFont.ttf"
# → {"s3_key": "production/input/2026/05/11/ttf/...", ...}

# 2. Convert
curl -X POST https://indox.org/api/v1/fonts/convert/ \
  -H "Authorization: Bearer eyJ…" \
  -H "Content-Type: application/json" \
  -d '{"s3_key":"production/input/2026/05/11/ttf/...","target_format":"woff2"}'
# → {"id":"<uuid>","status":"pending", ...}

# 3. Poll, 4. Download
```
