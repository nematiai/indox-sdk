# indox-client

Python SDK for the Indox API v1 — document, image, video, 3D-model and font conversion.

**Requires:** Python ≥ 3.9 · `requests ≥ 2.28`

## Install

```bash
pip install indox-client
```

## Authenticate

Create an API key in your Indox dashboard under **API Keys**. The value is shown once at
creation and starts with `ak_`.

Pass it directly, or set `INDOX_API_KEY` and let the client pick it up:

```bash
export INDOX_API_KEY='ak_your_key_here'
```

```python
from indox_client import Indox

with Indox() as client:                 # reads INDOX_API_KEY
    print(client.health.get())

with Indox(api_key="ak_...") as client:  # or pass it explicitly
    ...
```

The client defaults to `https://indox.org`. Point it elsewhere only if you run your own
instance — `Indox(base_url="https://api.example.com")`, or set `INDOX_BASE_URL`.

## Convert a file

Conversions are asynchronous: submit, poll, download.

```python
from indox_client import Indox

with Indox() as client:
    job = client.images.convert("photo.png", target_format="webp")
    done = client.images.wait(job["id"], timeout=120)
    client.media.download(job["id"], "photo.webp")
```

Fonts have a one-call helper that does all three steps:

```python
with Indox() as client:
    client.fonts.convert_and_download(
        "MyFont.ttf", target_format="woff2", output_path="MyFont.woff2"
    )
```

Before spending credits, you can check a conversion is supported:

```python
client.fonts.validate("MyFont.ttf", "woff2")
# {'valid': True, 'input': 'ttf', 'output': 'woff2', 'engine': 'fonttools', 'credits': 1}
```

## Discover what is supported

```python
client.images.formats()        # image formats and pairs
client.videos.formats()
client.models.formats()
client.pdf.formats()
client.fonts.formats.list()
client.fonts.formats.get("ttf")
```

## Resources

| Attribute | Covers |
|---|---|
| `client.health` | service health |
| `client.images` · `client.videos` · `client.models` | media conversion |
| `client.media` | media job status, downloads, batches, credits |
| `client.pdf` | document conversion, form fields, pipelines, phone scan, e-signing |
| `client.docs` | document job status, batches, credits |
| `client.fonts` | formats, quota, upload, convert, validate, inspect, download |
| `client.webhooks` | create, list, update, delete, deliveries, test |
| `client.user` | profile, storage, usage, share links |
| `client.billing` | credit balance, plans, purchases |

## Errors and timeouts

Failures raise typed exceptions from `indox_client._exceptions` — `AuthenticationError`,
`PermissionDeniedError`, `NotFoundError`, `BadRequestError`, `ConversionError`,
`APIConnectionError` — each carrying `status_code` and the parsed `response`.

```python
from indox_client import Indox
from indox_client._exceptions import BadRequestError

try:
    client.images.convert("photo.png", target_format="nope")
except BadRequestError as exc:
    print(exc.status_code, exc.response)
```

Requests use a 5 s connect / 60 s read timeout by default:
`Indox(timeout=(5.0, 120.0))` to change it.

## Links

- Documentation — <https://indox.org/docs/>
- Source, and SDKs for 7 other languages — <https://github.com/nematiai/indox-sdk>
