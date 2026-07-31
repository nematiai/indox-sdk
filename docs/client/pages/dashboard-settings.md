# Dashboard — Settings

Settings has its own nested layout at `dashboard/settings/layout.tsx` with two sub-pages.

---

## General Settings

**Route:** `/dashboard/settings/general`
**File:** `src/app/[locale]/dashboard/settings/general/page.tsx`
**Component:** `@/components/pages/(Dashboard)/dashboardPage/settings/general` *(inferred)*

### Key Responsibilities

- Display name, language/locale preference
- Email notification preferences
- Theme / UI preferences
- Delete account link → Account page

---

## Integrations Settings

**Route:** `/dashboard/settings/integrations`
**File:** `src/app/[locale]/dashboard/settings/integrations/page.tsx`
**Component:** `@/components/pages/(Dashboard)/dashboardPage/settings/integrations`

### Purpose

Manage connected cloud storage providers. Each provider has its own connect/disconnect flow.

### Supported Providers

| Provider | OAuth App |
|---|---|
| Google Drive | `google_integration` (backend) |
| Box | `box_integration` |
| Dropbox | `dropbox_integration` |
| OneDrive | `onedrive_integration` |

### Key Responsibilities

- Show connection status per provider (connected / disconnected)
- "Connect" → triggers OAuth flow → callback → token stored on backend
- "Disconnect" → revokes token, removes integration
- Error states: expired token, revoked access

### Component Structure (from `components/` tree)

```
components/
└── (Dashboard)/dashboardPage/settings/integrations/
    (each provider likely has its own sub-component)
```
