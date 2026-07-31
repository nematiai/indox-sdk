# Pricing Page

**Route:** `/pricing`
**File:** `src/app/[locale]/(apps)/pricing/page.tsx`
**Layout group:** `(apps)` — full header + footer
**Component:** `@/components/pages/(Conversion)/pricing` *(inferred)*

## Purpose

Displays subscription plans and pricing tiers. Drives users to subscribe or upgrade.

## Key Responsibilities

- Show available plans (Free, Pro, etc.) with feature comparison
- CTA buttons linking to billing/checkout flow
- Connects to `/api/billing/plans/` on the backend

## Notes

- Same `(apps)` layout as Home — consistent marketing shell
- Locale-aware (i18n via `next-intl`)
