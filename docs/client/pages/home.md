# Home / Landing Page

**Route:** `/` (locale root)
**File:** `src/app/[locale]/(apps)/page.tsx`
**Layout group:** `(apps)` — full header + footer
**Component:** `@/components/pages/(Conversion)/landing`

## Purpose

The main marketing/landing page. Entry point for unauthenticated visitors. Showcases the platform's file conversion capabilities and drives users toward signing up or trying a conversion.

## Key Responsibilities

- Hero section with CTA
- Highlight supported conversion types
- Drive traffic to `/conversions` or specific `[conversionSlug]` pages

## Notes

- This page is inside the `(apps)` layout group so it shares header/footer with Pricing, Privacy, and Terms
- Metadata and SEO are handled at the layout level for this group
