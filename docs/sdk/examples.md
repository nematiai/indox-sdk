# SDK Examples

Worked examples for the Python client, `indox-client`.

!!! warning "Not yet published"
    `pip install indox-client` does not resolve yet — see the
    [SDK status table](index.md). The snippets below are accurate against the live API and
    the shipping client; they run as soon as the package is available.

## Set up a client

```python
from indox_client import Indox

client = Indox(api_key="your-api-key")
```

`Indox()` with no arguments reads `INDOX_API_KEY` from the environment. The base URL defaults
to `https://indox.org`; `INDOX_BASE_URL` or the `base_url` argument overrides it for a
self-hosted deployment. Use it as a context manager to close the HTTP session cleanly:

```python
with Indox(timeout=(5.0, 60.0)) as client:   # (connect, read) seconds
    print(client.base_url)
    print(client.health.get()["status"])     # 'ok'
```

## Discover what a service can convert

```python
client.images.formats()           # raster + vector engines, inputs and outputs
client.videos.formats()
client.models.formats()           # 3D models
client.pdf.formats()
client.fonts.formats.list()
client.fonts.formats.get("ttf")   # only the outputs reachable from TTF
```

Each returns the live engine table, so you never have to hardcode a format list.

## Convert an image

Conversions are asynchronous: start the job, poll until it reaches a terminal status, then
download the result.

```python
job = client.images.convert("photo.png", data={"target_formats": "webp"})
# {'id': '8aa388e0-…', 'status': 'pending', 'service': 'image'}

final = client.images.wait(job["id"], timeout=120)
# {'status': 'completed', 'requested_formats': ['webp'],
#  'download_url': '/api/v1/media_core/files/…/download/', 'results': [...]}

client.media.download(job["id"], "photo.webp")   # returns a pathlib.Path
```

`client.models` follows the same pattern for 3D models, and `client.videos.convert()` starts a
video job. `client.docs` and `client.media` expose the shared status, batch, and credit
endpoints for document and media jobs.

## Convert a font

The font pipeline has a one-call form:

```python
path = client.fonts.convert_and_download(
    "MyFont.ttf",
    target_format="woff2",
    output_path="MyFont.woff2",
)
```

…and a step-by-step form when you want to inspect or validate first:

```python
client.fonts.inspect("MyFont.ttf")     # family, weight, glyph count, unicode ranges
client.fonts.validate("MyFont.ttf", target_format="woff2")
# {'valid': True, 'input': 'ttf', 'output': 'woff2', 'engine': 'fonttools', 'credits': 1}

upload = client.fonts.upload("MyFont.ttf")           # -> {'s3_key': …, 'format': 'ttf', …}
job = client.fonts.convert(upload["s3_key"], target_format="woff2")
client.fonts.conversions.wait(job["id"])
client.fonts.conversions.download(job["id"], "MyFont.woff2")
```

See the [Python SDK guide](python.md) for the full font reference.

## Check quota, credits, and history

```python
client.fonts.quota()               # free-tier request window
client.docs.credits()              # {'is_authenticated': True, 'remaining_credits': 10, …}
client.billing.credits_balance()
client.billing.pricing_plans()     # list of plans
client.user.me()
client.user.recent_conversions()
client.webhooks.list()
```

## Handle errors

Every HTTP failure raises a subclass of `APIStatusError` carrying `.status_code` and the
decoded `.response`:

```python
from indox_client import (
    APIConnectionError,
    BadRequestError,
    ConversionError,
    ConversionTimeoutError,
    PaymentRequiredError,
)

try:
    job = client.images.convert("photo.png", data={"target_formats": "webp"})
    final = client.images.wait(job["id"], timeout=120)
except BadRequestError as exc:
    print(exc.status_code, exc.response)   # 400 {'non_field_errors': [...]}
except PaymentRequiredError:
    print("out of credits")
except ConversionTimeoutError:
    print("still running past the timeout")
except ConversionError as exc:
    print("job failed:", exc.conversion_id)
except APIConnectionError:
    print("could not reach the API")
```

The full exception hierarchy is listed in the [Python SDK guide](python.md).
