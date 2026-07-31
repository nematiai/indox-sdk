# Dashboard — Conversions

**Route:** `/dashboard/conversions`
**File:** `src/app/[locale]/dashboard/conversions/page.tsx`
**Layout:** `dashboard` layout (sidebar)
**Component:** `@/components/pages/(Dashboard)/dashboardPage/...` *(check page file)*

## Purpose

In-dashboard conversion tool — lets authenticated users run file conversions without leaving the dashboard. May offer batch conversion or cloud-file conversion (from integrated providers).

## Difference from Public Conversion Pages

| | Public `[conversionSlug]` | Dashboard Conversions |
|---|---|---|
| Auth required | No | Yes |
| Source | Local upload | Local + Cloud (Google, Box, etc.) |
| History saved | Maybe | Yes |
| Batch support | No | Possibly |

## Key Responsibilities

- Pick source format and target format
- Upload file or pick from connected cloud storage
- Track conversion job progress
- Result saved to My Files automatically
