# Dashboard — My Files

**Route:** `/dashboard/files`
**File:** `src/app/[locale]/dashboard/files/page.tsx`
**Layout:** `dashboard` layout (sidebar)
**Component:** `@/components/pages/(Dashboard)/dashboardPage/my-files`

## Purpose

Primary dashboard page. Shows the user's uploaded and converted files. Also serves as the landing page after a Stripe checkout redirect.

## Payment Redirect Handling

The page reads `?status` and `?session_id` query params to handle post-checkout states:

| `status` param | `session_id` present | Renders |
|---|---|---|
| `success` | yes | `<PaymentSuccess sessionId={sessionId} />` |
| `cancel` | — | `<PaymentCanceled />` |
| *(none)* | — | `<MyFiles />` (normal view) |

Components: `PaymentSuccess`, `PaymentCanceled` from `my-files/components`.

## Wrapped in `<Suspense>`

`useSearchParams()` requires Suspense boundary — the page wraps `FilesPageContent` in `<Suspense fallback={<div>Loading...</div>}>`.

## Key Responsibilities

- List user's files (upload date, type, size, status)
- Download / delete / re-convert actions
- Handle payment success and cancel states from Stripe redirect
