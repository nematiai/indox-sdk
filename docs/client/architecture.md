# System Architecture

## High-Level Overview

```
Client (Frontend / Mobile)
        │
        │ HTTPS / REST API
        ▼
┌─────────────────────────┐
│     Django (Gunicorn)   │  ← indox/config/wsgi.py
│  DRF Views & Serializers│
└────────┬────────────────┘
         │
    ┌────┴─────────────────────────┐
    │                              │
    ▼                              ▼
PostgreSQL                      Redis
(primary data store)        (cache + Celery broker)
                                   │
                                   ▼
                             Celery Workers
                          (async tasks: conversion,
                           notifications, sync jobs)
```

## Request Lifecycle

1. Request hits Django → `config/urls.py` routes to the correct app
2. DRF handles auth (JWT / OIDC token validation)
3. View calls service/model layer
4. Long-running work (file conversion, cloud sync) dispatched to Celery
5. Response returned; notification triggered if needed

## Auth Flow

```
User → POST /auth/login/ → JWT access + refresh tokens
User → GET /auth/social/google/ → redirect to Google → callback → JWT
OIDC clients → OIDC discovery endpoint → token exchange
```

## File Conversion Pipeline

```
Upload → media_core stores raw file
       → Celery task dispatched (image_converter / pdf_handler / video_converter)
       → Converted file saved back to media_core
       → media_notifications fires event
       → Client polls or receives WebSocket push
```

## Cloud Sync Flow

```
User connects provider (OAuth callback stored in integration app)
→ User triggers sync OR scheduled Celery beat task runs
→ Integration app fetches file list from provider API
→ New/changed files downloaded → stored in media_core
→ Deletions reconciled
```

## Key Django Settings Modules

| File | Used when |
|---|---|
| `config/settings/base.py` | All environments |
| `config/settings/development.py` | `DEBUG=True` local dev |
| `config/settings/production.py` | Deployed instances |

Select with `DJANGO_SETTINGS_MODULE` env var.
