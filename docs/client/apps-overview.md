# Apps Overview

All apps live under `indox/apps/`. Each is a self-contained Django app with its own models, serializers, views, and URLs.

## Core Document & Media Apps

| App | Purpose |
|---|---|
| `docs_core` | Core document management — CRUD, versioning, sharing |
| `docs_notification` | Notifications scoped to document events |
| `media_core` | Core media asset management (upload, store, retrieve) |
| `media_notifications` | Notifications scoped to media events |
| `pdf_handler` | PDF generation, parsing, and manipulation |
| `image_converter` | Image format conversion and processing |
| `video_converter` | Video format conversion and processing |
| `fonts` | Font management and serving |

## Cloud Storage Integrations

| App | Service |
|---|---|
| `google_integration` | Google Drive — OAuth, file sync |
| `box_integration` | Box — OAuth, file sync |
| `dropbox_integration` | Dropbox — OAuth, file sync |
| `onedrive_integration` | OneDrive — OAuth, file sync |

## User & Auth Apps

| App | Purpose |
|---|---|
| `user` | User model, profile, preferences |
| `social_auth` | Social login (Google, etc.) |
| `oidc` | OpenID Connect provider/consumer |
| `business` | Organization / team / workspace management |

## Platform Apps

| App | Purpose |
|---|---|
| `billing` | Subscription plans, payments, usage limits |
| `notifications` | Global notification system (in-app) |

## Shared Code

- `indox/common/` — base models, mixins, permissions, utilities used across apps
- `indox/config/` — `settings.py`, root `urls.py`, `wsgi.py`, `asgi.py`
