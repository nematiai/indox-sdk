# indox-client

Python SDK for Indox **API v1** (`/api/v1/…`).

**Version:** 0.4.0  
**Requires:** Python ≥ 3.9, `requests ≥ 2.28`

## Install (macOS)

From the monorepo (dev):

```bash
cd /path/to/indox
python3 -m venv .venv
source .venv/bin/activate
pip install -e .   # if package root is configured
# or:
pip install requests
export PYTHONPATH="/path/to/indox:$PYTHONPATH"
```

## Create an API key

### Option A — Dashboard

1. Open the app (local: `http://localhost:41002` or your host LAN IP).
2. Sign in → **Dashboard → API Keys** (or `/dashboard/keys`).
3. Create a key → copy the `ak_…` value once (shown only at creation).

### Option B — Local Docker (dev)

On the machine running the stack:

```bash
docker compose --env-file .env -f docker/local/compose.yml exec -T django \
  python manage.py shell -c "
from django.contrib.auth import get_user_model
from apps.user.models import UserProfile
from apps.user.api_keys import APIKey
u = get_user_model().objects.get(username='YOUR_USERNAME')
APIKey.objects.filter(user=u, name='macos-sdk').update(is_active=False)
raw, k = APIKey.create_api_key(u, 'macos-sdk', ['read','write','admin'], expires_in_days=30)
print(raw)
"
```

## Convert from macOS

Point `INDOX_BASE_URL` at a host the Mac can reach:

| Where API runs | Base URL |
|---|---|
| Same Mac (local docker) | `http://localhost:41000` (API) or via nginx `http://localhost:41002` if proxied |
| Linux box on LAN | `http://<linux-lan-ip>:41000` |

```bash
export INDOX_API_KEY='ak_xxxxxxxx'
export INDOX_BASE_URL='http://YOUR_HOST:41000'   # or https://indox.org

python3 <<'PY'
from indox_client import Indox

with Indox() as client:  # reads INDOX_API_KEY / INDOX_BASE_URL
    print(client.health.get())
    print(client.fonts.formats.list())
    # Font convert + download
    out = client.fonts.convert_and_download(
        "./MyFont.ttf",
        target_format="woff2",
        output_path="./MyFont.woff2",
    )
    print("saved", out)
PY
```

PDF example:

```python
from indox_client import Indox

with Indox(api_key="ak_…", base_url="http://HOST:41000") as client:
    job = client.pdf.convert("./input.pdf", target_format="docx")
    cid = job["id"]  # or job["conversion_id"]
    client.pdf.wait(cid)
    client.pdf.download(cid, "./out.docx")
```

## Resources (v1 P0–P3 + PDF ADV)

| Attribute | Coverage |
|---|---|
| `client.health` | GET health |
| `client.fonts` | formats, quota, health, upload/convert/validate/inspect, wait/download |
| `client.pdf` | convert, formats, ops, history, download + pipeline/scan/signing |
| `client.docs` | credits, conversion, batch, hide |
| `client.media` | health, credits, conversion, download, batch |
| `client.images` | `/api/v1/convert/image/` |
| `client.videos` | `/api/v1/convert/video/` |
| `client.models` | `/api/v1/convert/model/` |
| `client.webhooks` | CRUD + deliveries + test |
| `client.user` | me, storage, usage, shares, login/logout |
| `client.billing` | credits, plans, purchase, tasks (no admin) |

## Live allowlist smoke

```bash
PYTHONPATH=. INDOX_BASE_URL=http://localhost:41000 INDOX_API_KEY=ak_… \
  python backend/tests/test_indox_client_sdk_v1.py
```

## Auth

`Authorization: Bearer <api_key>` — set via `api_key=` or `INDOX_API_KEY`.
