# Dashboard — API Keys

**Route:** `/dashboard/keys`
**File:** `src/app/[locale]/dashboard/keys/page.tsx`
**Layout:** `dashboard` layout (sidebar)
**Component:** `@/components/pages/(Dashboard)/dashboardPage/ApiKeys`

## Purpose

Lets users manage their API keys for programmatic access to the INDOX platform.

## Key Responsibilities

- List existing API keys (name, created date, last used, masked secret)
- Create new key (name input → generated secret shown once)
- Revoke / delete a key
- Copy key to clipboard
- Possibly scope keys by permission level (read / write)

## Backend Endpoint

Talks to `/api/keys/` (or equivalent) on the Django backend.
