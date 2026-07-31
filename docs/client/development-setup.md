# Development Setup

This page is for running **your own indox instance** from the source repository. If you only want
to call the hosted API at `indox.org`, you do not need any of this — start at
[Quickstart](../quickstart.md).

The whole stack runs in Docker. There is no supported host-Python path: the backend image carries
the LibreOffice and fontconfig toolchains that conversions depend on, and PDF operations are
delegated to a Stirling PDF sidecar container — so a bare `pip install` will not produce a working
instance.

## Prerequisites

- Docker Engine with **Compose v2** (`docker compose`, not `docker-compose`)
- `git`
- A Linux or macOS host. On Windows use WSL2 — the commands below are bash.

## Configuration

All configuration comes from a single `.env` file at the repository root. The repo ships **no**
`.env.example` — it is deliberately not tracked, so create the file yourself.

Every compose command must pass `--env-file .env` explicitly. Compose resolves variables relative
to the *project directory* (`docker/local/`), which has no `.env` of its own; omit the flag and the
published ports silently become random ephemeral ones.

### Minimum to boot

| Variable | Used for |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret. `SECRET_KEY` is accepted as a fallback name. |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Database. `POSTGRES_HOST` is set to `indox-db` by compose. |
| `REDIS_URL` | Celery broker and cache. |
| `API_PORT` | Host port for the Django container (`41000` in the shipped setup). |
| `HTTP_PORT` | Host port for the nginx proxy (`41002`). |
| `STIRLING_VERSION` / `STIRLING_ENABLE_LOGIN` | Pins the Stirling PDF sidecar image. |
| `SUPERUSER_USERNAME` / `SUPERUSER_EMAIL` / `SUPERUSER_PASSWORD` | Read by compose when you create the first admin user. |

### Object storage

Conversion inputs and outputs live in S3-compatible object storage (Cloudflare R2). Without these,
uploads and downloads will not work:

| Variable | Used for |
|---|---|
| `R2_ENDPOINT` | S3 endpoint URL. |
| `R2_ACCESS_KEY_ID` / `R2_SECRET_ACCESS_KEY` | Credentials. |
| `R2_BUCKET` | Bucket name. |
| `R2_REGION` | Defaults to `auto`. |
| `R2_CUSTOM_DOMAIN` | Optional public domain for served objects. |

### Optional integrations

Each of these is only needed if you enable the corresponding feature:

| Variable | Feature |
|---|---|
| `STRIPE_SECRET_KEY` · `STRIPE_PUBLIC_KEY` · `STRIPE_WEBHOOK_SECRET` | Billing |
| `GOOGLE_OAUTH2_CLIENT_ID` · `GOOGLE_OAUTH2_CLIENT_SECRET` | Google sign-in and Drive |
| `APPLE_CLIENT_ID` · `APPLE_TEAM_ID` · `APPLE_KEY_ID` · `APPLE_PRIVATE_KEY` | Apple Sign-In |
| `EMAIL_SMTP` · `EMAIL_PORT` · `EMAIL_HOST_USER` · `EMAIL_HOST_PASSWORD` · `MAIL_FROM` | Transactional email |
| `SECRET_ADMIN_URL` | Path the Django admin is mounted at — the admin is **not** at `/admin/` |
| `TOKEN_ENCRYPTION_KEY` | Encrypts stored third-party OAuth tokens |

Settings live in `backend/config/settings/` — `base.py` plus one module per concern under
`modules/`. Read those for the full set and the defaults.

## Run the stack

```bash
docker compose --env-file .env -f docker/local/compose.yml up
```

That brings up Django, Postgres 17, Redis, two Celery workers (`docs` and `media` queues), the
scheduler, the Stirling PDF sidecar, the Next.js frontend and an nginx proxy.

| URL | What |
|---|---|
| `http://localhost:41002` | Entry point — nginx, serving frontend and API |
| `http://localhost:41000` | Django directly, bypassing the proxy |
| `http://localhost:41000/api/v1/health/` | Health probe — expect `200` |
| `http://localhost:41000/api/v1/openapi.json` | Machine-readable API schema |

The `backend/` directory is bind-mounted into the container, so Python edits reload without a
rebuild. Changing dependencies or the Dockerfile does need one:

```bash
docker compose --env-file .env -f docker/local/compose.yml build
```

## Database

The service name is `django`; the container name is `indox-django`. `docker compose exec` takes the
service name.

```bash
C="docker compose --env-file .env -f docker/local/compose.yml"

$C exec django python manage.py showmigrations   # [X] applied, [ ] pending
$C exec django python manage.py migrate
$C exec django python manage.py createsuperuser --noinput
```

`createsuperuser --noinput` reads Django's own `DJANGO_SUPERUSER_*` variables; compose maps your
`SUPERUSER_*` values onto them for you.

## Tests and lint

Both run inside the container — do not install dependencies on the host.

```bash
C="docker compose --env-file .env -f docker/local/compose.yml"

$C exec django pytest -q
$C exec django pytest apps/<app>/ -q
$C exec django ruff check .
```

## Teardown

```bash
C="docker compose --env-file .env -f docker/local/compose.yml"

$C down --remove-orphans   # stop; Postgres data survives
$C down -v                 # destructive: wipes volumes, including the database
```

After `down -v` you must re-run `migrate` and re-create the superuser.
