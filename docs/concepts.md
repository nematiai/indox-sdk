# Concepts

## Auth

- Requests authenticate with `Authorization: Bearer <external_token>`, or the web app's `HttpOnly` session cookie (backend auth is cookie-or-bearer).
- The free tier needs no credentials — anonymous requests are served within the free quota.
- `external_token`s are issued by Google/Apple sign-in or OIDC. Identity flows (signup, login, password reset) are served by allauth headless at `/_allauth/app/v1/` — see [Auth](api/auth.md).

## Conversions are asynchronous

Every conversion is a 3-step flow:

1. **Submit** — `POST /api/v1/<service>/convert/` returns `202` with a `conversion_id`.
2. **Poll** — `GET /api/v1/<service>/conversion/{id}/` returns `{ status, … }`.
3. **Download** — `GET /api/v1/<service>/{id}/download/` redirects to a presigned URL.

Statuses: `pending → processing → completed | failed`.

## Polling cadence

- Document conversions: poll every 2-5 s.
- Font conversions: poll every 1-2 s (most finish in <2 s).

Use exponential backoff if a conversion is still `processing` after 60 s.

## Credits

- **Free tier**: 10 conversions per IP per 30 days.
- **Paid**: 1 credit per conversion (some video conversions cost more — see [Limits](limits.md)).

## Locales & RTL

The API is language-agnostic. Client UIs support `en`, `fa`, `ar`. RTL is handled client-side (`dir="rtl"` on `fa`/`ar`).
