# Conversion Tool Page (Dynamic)

**Route:** `/<from>-to-<to>` (e.g. `/pdf-to-word`, `/png-to-jpg`)
**File:** `src/app/[locale]/[conversionSlug]/page.tsx`
**Layout:** `src/app/[locale]/[conversionSlug]/layout.tsx`
**Component:** `@/components/pages/(Conversion)/conversionsSlug`

## Purpose

The actual conversion tool page for a specific format pair. Users upload a file, select options, and download the converted output.

## Slug Format

`[from]-to-[to]` — parsed by `parseConversionSlug()` from `@/lib/conversion-utils`.

Valid pairs are validated against `mergedJsonData`. Invalid slugs → `notFound()`.

## Metadata (dynamic)

Generated per conversion pair via `generateMetadata`:
- Title: `generateConversionTitle(from, to)`
- Description: `generateConversionDescription(from, to)`
- Keywords: `"${from} to ${to}, convert ${from}, ${from} converter, ..."`
- OpenGraph configured

## Static Generation

`generateStaticParams()` pre-generates all valid pairs for `en-US` locale at build time for performance.

## Key Utilities (`@/lib/conversion-utils`)

| Function | Purpose |
|---|---|
| `parseConversionSlug(slug)` | Extracts `{from, to}` from the URL slug |
| `isValidConversion(from, to)` | Checks pair exists in `mergedJsonData` |
| `getConversionData(from, to)` | Returns full conversion config object |
| `generateConversionTitle` | SEO-friendly page title |
| `generateConversionDescription` | SEO meta description |
| `generateConversionSlug` | Builds slug string from format pair |

## Props to Component

```tsx
<ConversionSlug fromDisplay={from.toUpperCase()} toDisplay={to.toUpperCase()} />
```
