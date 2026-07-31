# Third-Party Integrations

## Cloud Storage Providers

### Google Drive (`google_integration`)
- Auth: OAuth 2.0 via `social_auth` / `oidc`
- Scopes needed: `drive.readonly`, `drive.file`
- Env vars: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- Callback URL: `/api/integrations/google/callback/`

### Box (`box_integration`)
- Auth: Box OAuth 2.0
- Env vars: `BOX_CLIENT_ID`, `BOX_CLIENT_SECRET`
- Callback URL: `/api/integrations/box/callback/`

### Dropbox (`dropbox_integration`)
- Auth: Dropbox OAuth 2.0
- Env vars: `DROPBOX_APP_KEY`, `DROPBOX_APP_SECRET`
- Callback URL: `/api/integrations/dropbox/callback/`

### OneDrive (`onedrive_integration`)
- Auth: Microsoft OAuth 2.0 (MSAL)
- Env vars: `ONEDRIVE_CLIENT_ID`, `ONEDRIVE_CLIENT_SECRET`, `ONEDRIVE_TENANT_ID`
- Callback URL: `/api/integrations/onedrive/callback/`

---

## Payment / Billing (Stripe)

App: `billing`

- Env vars: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PUBLISHABLE_KEY`
- Webhook endpoint: `/api/billing/webhook/` — must be registered in Stripe dashboard
- Supports: subscription creation, upgrade/downgrade, cancellation, usage metering

---

## Social Auth

App: `social_auth`

- Uses `django-allauth` or `social-django` (verify in `requirements/base.txt`)
- Supported providers: Google (configured), extendable to GitHub, Facebook, etc.
- Env vars: `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`, `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET`

---

## OIDC

App: `oidc`

- Acts as OIDC consumer (login via external IdP) and optionally as provider
- Env vars: `OIDC_RP_CLIENT_ID`, `OIDC_RP_CLIENT_SECRET`, `OIDC_OP_*` (provider endpoints)

---

## Email

- Backend configured in Django settings (`EMAIL_BACKEND`)
- For local dev: `django.core.mail.backends.console.EmailBackend`
- For production: SMTP or SendGrid / SES — set `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`

---

## Celery / Redis

- Broker: Redis (`REDIS_URL`)
- Result backend: Redis or PostgreSQL
- Beat scheduler: `django-celery-beat` (tasks stored in DB)
- Worker start: `celery -A indox worker -l info`
- Beat start: `celery -A indox beat -l info`
