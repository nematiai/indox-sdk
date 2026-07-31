# Conversions List Page

**Route:** `/conversions`
**File:** `src/app/[locale]/(with-header-only)/conversions/page.tsx`
**Layout group:** `(with-header-only)` — header, no footer
**Component:** `@/components/pages/(Conversion)/conversions`

## Purpose

Displays all available file conversion pairs (e.g. PDF→Word, PNG→JPG). Acts as a directory of every supported conversion tool on the platform.

## SEO / Metadata

- Title: `"File Conversion Platform - Convert Documents & Media Instantly"`
- Full structured data (JSON-LD `WebPage` + `Service` schemas)
- `canonical` URL: `<metadataBase>/conversions` for `en-US`, locale-prefixed for others
- OpenGraph + Twitter card configured
- `robots: index: true`

## Key Responsibilities

- Grid/list of all conversion types sourced from `mergedJsonData`
- Each item links to the corresponding `[conversionSlug]` page
- i18n: locale-aware canonical and alternate URLs

## Related

- [`conversion-slug.md`](conversion-slug.md) — the individual tool page each item links to
