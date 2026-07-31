# Account Page

**Route:** `/account`
**File:** `src/app/[locale]/(account)/account/page.tsx`
**Layout group:** `(account)`
**Component:** `@/components/pages/(Conversion)/account`

## Purpose

Authenticated user account management — profile info, password change, danger zone (delete account).

## SEO / Metadata

- Title from `next-intl` translation key `AccountMetadata.name`
- `robots: index: false, follow: true` — intentionally excluded from search engines

## Key Responsibilities

- Display and edit user profile (name, email, avatar)
- Password / security settings
- Account deletion flow
- Locale: uses `next-intl` `getTranslations`
