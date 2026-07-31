# Python SDK

Package: `indox-client` 0.4.0.

!!! warning "Not yet published"
    `pip install indox-client` does **not** resolve yet — the package is not on PyPI. See the
    [SDK status table](index.md), which is updated the day it goes live.

## Until it ships — call the API directly

Create an API key under **Dashboard → API keys** and send it as a bearer token against
`https://indox.org`:

```python
import os
import requests

res = requests.get(
    "https://indox.org/api/v1/health/",
    headers={
        "Authorization": f"Bearer {os.environ['INDOX_API_KEY']}",
        "Accept": "application/json",
    },
    timeout=(5.0, 60.0),
)
res.raise_for_status()
```

The [API reference](../client/api-reference.md) documents every public endpoint.

## Usage guide

The guide below documents the client as it will ship, so you can evaluate the interface ahead
of release. Its installation step only works once the package is published; the authentication,
resource, and conversion sections describe the live API and are accurate today.

{% include-markdown "../client/sdk-pip-usage.md" heading-offset=1 %}
