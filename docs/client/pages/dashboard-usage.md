# Dashboard — Usage Stats

**Route:** `/dashboard/usage`
**File:** `src/app/[locale]/dashboard/usage/page.tsx`
**Layout:** `dashboard` layout (sidebar)
**Component:** `@/components/pages/(Dashboard)/dashboardPage/usage`

## Purpose

Displays the user's consumption against their plan limits — conversions used, storage used, API calls, etc.

## Key Responsibilities

- Usage meters / progress bars per resource (conversions, storage, API calls)
- Current plan name and limits
- Period reset date
- Upgrade CTA if approaching limits
- Data sourced from `/api/billing/usage/` or similar backend endpoint
