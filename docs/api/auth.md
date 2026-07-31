# Auth API

The conversion API authenticates with a **Bearer token**:

```
Authorization: Bearer <external_token>
```

- **Free tier** needs no credentials — anonymous requests are served within the free quota.
- **Authenticated** requests carry an Indox `external_token`, issued by **Google or Apple sign-in** or an **OIDC** token. The web app sends it automatically as a `Secure`, `HttpOnly` session cookie.

## Identity flows (allauth headless)

Signup, email/password login, logout, and password reset are served by **allauth headless** under `/_allauth/app/v1/` (no trailing slash):

| Method | Path | Purpose |
|---|---|---|
| `GET`    | `/_allauth/app/v1/config` | Enabled auth methods & providers |
| `POST`   | `/_allauth/app/v1/auth/signup` | Create an account |
| `POST`   | `/_allauth/app/v1/auth/login` | Email/password login |
| `GET`    | `/_allauth/app/v1/auth/session` | Current session |
| `DELETE` | `/_allauth/app/v1/auth/session` | Log out |
| `POST`   | `/_allauth/app/v1/auth/password/request` | Request a password reset |

## Profile & sessions (`/api/v1/user/`)

| Method | Path | Purpose |
|---|---|---|
| `GET`/`PATCH` | `/api/v1/user/me/` | Current user profile |
| `GET`    | `/api/v1/user/auth/sessions/` | List active sessions |
| `DELETE` | `/api/v1/user/auth/sessions/{session_id}/` | Revoke one session |
| `DELETE` | `/api/v1/user/auth/sessions/revoke-all/` | Revoke all sessions |

> The `external_token` used as the conversion-API Bearer is issued by social sign-in (Google/Apple) or OIDC. The allauth session token authenticates the identity endpoints above, **not** the conversion API.

See [Quickstart](../quickstart.md) for a worked example.
