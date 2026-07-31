# INDOX Client — Pages Index

Frontend: Next.js (App Router) · i18n: `next-intl` · Located at `front/src/app/[locale]/`

## Python SDK (pip)

| Doc | Description |
|---|---|
| [sdk-pip-usage.md](sdk-pip-usage.md) | Install, auth, all `client.fonts.*` methods, error handling |

---

## Page Map

### Public Pages (no auth required)

| Page | URL | Doc |
|---|---|---|
| Home / Landing | `/` | [home.md](pages/home.md) |
| Conversions List | `/conversions` | [conversions.md](pages/conversions.md) |
| Conversion Tool | `/<from>-to-<to>` | [conversion-slug.md](pages/conversion-slug.md) |
| Pricing | `/pricing` | [pricing.md](pages/pricing.md) |
| Privacy Policy | `/privacy` | [privacy.md](pages/privacy.md) |
| Terms of Service | `/terms` | [terms.md](pages/terms.md) |
| Support | `/support` | [support.md](pages/support.md) |

### Auth Pages

| Page | URL | Doc |
|---|---|---|
| Account | `/account` | [account.md](pages/account.md) |

### Dashboard (auth required)

| Page | URL | Doc |
|---|---|---|
| My Files | `/dashboard/files` | [dashboard-files.md](pages/dashboard-files.md) |
| File History | `/dashboard/history` | [dashboard-history.md](pages/dashboard-history.md) |
| History Detail | `/dashboard/history/[id]` | [dashboard-history.md](pages/dashboard-history.md) |
| Conversions | `/dashboard/conversions` | [dashboard-conversions.md](pages/dashboard-conversions.md) |
| API Keys | `/dashboard/keys` | [dashboard-keys.md](pages/dashboard-keys.md) |
| Usage Stats | `/dashboard/usage` | [dashboard-usage.md](pages/dashboard-usage.md) |
| Settings · General | `/dashboard/settings/general` | [dashboard-settings.md](pages/dashboard-settings.md) |
| Settings · Integrations | `/dashboard/settings/integrations` | [dashboard-settings.md](pages/dashboard-settings.md) |

## Layout Groups

| Group | Folder | Used for |
|---|---|---|
| `(apps)` | Full header + footer | Home, Pricing, Privacy, Terms |
| `(with-header-only)` | Header only, no footer | Conversions list |
| `(account)` | Account shell | Account page |
| `(support)` | Support shell | Support page |
| `dashboard` | Sidebar layout | All `/dashboard/*` routes |

## Project Structure

```
front/src/
├── app/
│   ├── [locale]/          ← all user-facing pages
│   └── api/fe/            ← Next.js API routes (upload_object, inspect_url, verify)
├── components/
│   ├── pages/
│   │   ├── (Conversion)/  ← landing, conversions, account, conversionSlug
│   │   └── (Dashboard)/   ← all dashboard page components
│   ├── shared/
│   ├── ui/
│   └── providers/
├── hooks/
├── stores/
├── lib/
├── constants/
└── i18n/
```
