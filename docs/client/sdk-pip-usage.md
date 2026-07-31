# INDOX Python SDK — pip Usage Guide

**Package:** `indox-client` v0.4.0
**PyPI name:** `indox-client`
**Requires:** Python ≥ 3.9, `requests ≥ 2.28`

---

## Installation

!!! warning "Not yet published"
    `indox-client` is not on PyPI yet, so `pip install indox-client` does **not** resolve.
    See the *Official SDKs* status page for the current state of every language; it is
    updated the day the package goes live.

    Until then, call the REST API directly — see the API reference. Everything below
    documents the client as it will ship, so you can evaluate the interface in advance;
    the authentication, resource, and error semantics it describes match the live API today.

---

## Authentication

Get your API key from `/dashboard/keys` in the web app.

**Option 1 — pass directly:**

```python
from indox_client import Indox

client = Indox(api_key="your-api-key")
```

**Option 2 — environment variable (recommended):**

```bash
export INDOX_API_KEY="your-api-key"      # Linux/macOS
$env:INDOX_API_KEY = "your-api-key"      # Windows PowerShell
```

```python
from indox_client import Indox

client = Indox()  # reads INDOX_API_KEY automatically
```

**Option 3 — custom base URL (self-hosted / dev):**

```python
client = Indox(
    api_key="your-api-key",
    base_url="https://indox.example.com",  # self-hosted; defaults to https://indox.org
    timeout=(5.0, 30.0),                   # (connect_timeout, read_timeout)
)
```

---

## Context Manager (recommended)

Always closes the HTTP session cleanly:

```python
with Indox(api_key="your-api-key") as client:
    result = client.fonts.convert_and_download(
        "./font.ttf",
        target_format="woff2",
        output_path="./font.woff2",
    )
```

---

## Fonts API — `client.fonts`

### 1. List all supported formats

```python
formats = client.fonts.formats.list()
print(formats)
# Returns: dict with engines and their input/output format mappings
```

### 2. Get outputs available for a specific input format

```python
outputs = client.fonts.formats.get("ttf")
print(outputs)
# Returns: available output formats and conversion engines for TTF input
```

### 3. Validate before converting (dry run)

```python
result = client.fonts.validate("./font.ttf", target_format="woff2")
if result["valid"]:
    print(f"Will use engine: {result['engine']}")
    print(f"Credits required: {result['credits']}")
```

### 4. Quick convert — upload + convert in one call

```python
job = client.fonts.convert_file("./font.ttf", target_format="woff2")
print(job["id"])      # conversion UUID
print(job["status"])  # "pending" / "completed" / "failed"
```

### 5. Poll for completion

```python
status = client.fonts.conversions.wait(
    job["id"],
    timeout=60.0,        # max seconds to wait (default: 60)
    poll_interval=0.5,   # seconds between checks (default: 0.5)
)
print(status["download_url"])
```

### 6. Download the converted file

```python
path = client.fonts.conversions.download(job["id"], "./output/font.woff2")
print(f"Saved to: {path}")
```

### 7. Full pipeline — one call does everything

```python
path = client.fonts.convert_and_download(
    "./font.ttf",
    target_format="woff2",
    output_path="./output/font.woff2",
    timeout=60.0,
    poll_interval=0.5,
)
print(f"Done: {path}")
```

### 8. Manual step-by-step (upload → convert → wait → download)

```python
# Step 1: upload
upload = client.fonts.upload("./font.ttf")
print(upload["s3_key"])      # S3 key for next step
print(upload["filename"])
print(upload["format"])
print(upload["size_bytes"])

# Step 2: start conversion
job = client.fonts.convert(
    upload["s3_key"],
    target_format="otf",
    filename=upload["filename"],   # optional
    external_token="my-ref-123",   # optional tracking token
)

# Step 3: check status manually
status = client.fonts.conversions.get(job["id"])
print(status["status"])  # "pending" | "completed" | "failed"

# Step 4: wait until done
client.fonts.conversions.wait(job["id"])

# Step 5: download
client.fonts.conversions.download(job["id"], "./output/font.otf")
```

---

## Supported Font Formats

Query live from the API:

```python
client.fonts.formats.list()
```

Common formats: `ttf`, `otf`, `woff`, `woff2`, `eot`, `svg`

> Format strings are normalized automatically — case-insensitive, leading dots stripped.
> `"WOFF2"`, `".woff2"`, `"woff2"` all work.

---

## Error Handling

```python
from indox_client import (
    Indox,
    AuthenticationError,
    PaymentRequiredError,
    RateLimitError,
    ConversionError,
    ConversionTimeoutError,
    APIConnectionError,
    BadRequestError,
    NotFoundError,
    InternalServerError,
)

client = Indox(api_key="your-key")

try:
    path = client.fonts.convert_and_download(
        "./font.ttf",
        target_format="woff2",
        output_path="./font.woff2",
    )
except AuthenticationError:
    print("Invalid API key — check /dashboard/keys")
except PaymentRequiredError:
    print("Insufficient credits — upgrade plan")
except RateLimitError:
    print("Too many requests — slow down")
except ConversionError as e:
    print(f"Conversion failed: {e.message} (job: {e.conversion_id})")
except ConversionTimeoutError:
    print("Conversion took too long")
except BadRequestError as e:
    print(f"Bad input: {e.message}")
except NotFoundError:
    print("Conversion job not found")
except InternalServerError as e:
    print(f"Server error {e.status_code}: {e.message}")
except APIConnectionError:
    print("Could not reach the API")
```

### Exception Hierarchy

```
IndoxError
├── APIConnectionError          # network/connection failure
├── ConversionError             # conversion job failed  (.conversion_id)
├── ConversionTimeoutError      # polling timed out
└── APIStatusError              # HTTP error (.status_code, .response, .request_id)
    ├── BadRequestError         # 400
    ├── AuthenticationError     # 401
    ├── PaymentRequiredError    # 402 — out of credits
    ├── PermissionDeniedError   # 403
    ├── NotFoundError           # 404
    ├── RateLimitError          # 429
    └── InternalServerError     # 5xx
```

---

## Other resources

Fonts is documented in full above because its pipeline is the most involved. The client exposes
the rest of the public API the same way:

| Resource | Access | Covers |
|---|---|---|
| Health | `client.health` | service status probe |
| Images | `client.images` | raster/vector conversion, formats, operations, history |
| Videos | `client.videos` | video conversion, formats |
| 3D models | `client.models` | model conversion, formats, operations |
| PDF | `client.pdf` | conversion, form fields, pipelines, scan + signing sessions |
| Docs core | `client.docs` | conversion status, batch collect/download, credits |
| Media core | `client.media` | conversion status, download, batch, credits |
| Account | `client.user` | profile, files, shares, usage |
| Billing | `client.billing` | credit balance, pricing plans, purchases |
| Webhooks | `client.webhooks` | create, list, update, delete, test, deliveries |

Every conversion resource follows the same shape: start the job, poll `wait(conversion_id)`,
then download. The SDK examples page shows a worked image conversion end to end.

---

## API Endpoints Used (reference)

| Method | Endpoint |
|---|---|
| POST | `/api/v1/fonts/upload/` |
| POST | `/api/v1/fonts/convert/` |
| POST | `/api/v1/fonts/validate/` |
| POST | `/api/v1/fonts/inspect/` |
| GET | `/api/v1/fonts/inspect/` |
| GET | `/api/v1/fonts/quota/` |
| GET | `/api/v1/fonts/formats/` |
| GET | `/api/v1/fonts/formats/{input_format}/` |
| GET | `/api/v1/fonts/conversion/{id}/` |
| GET | `/api/v1/fonts/{id}/download/{filename}` |
