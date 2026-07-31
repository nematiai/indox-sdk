# Dashboard — File History

**Routes:**
- `/dashboard/history` — list
- `/dashboard/history/[id]` — detail

**Files:**
- `src/app/[locale]/dashboard/history/page.tsx`
- `src/app/[locale]/dashboard/history/[id]/page.tsx`

**Layout:** `dashboard` layout (sidebar)
**Components:**
- List: `@/components/pages/(Dashboard)/dashboardPage/file-history`
- Detail: component inside `history/[id]/page.tsx`

## Purpose

Shows a chronological log of all file conversion jobs the user has run.

## List Page

- Paginated table/list of past conversions
- Columns: file name, from/to format, date, status, size
- Clickable rows → detail page

## Detail Page (`[id]`)

- Full detail for a single history entry
- Download original + converted file
- Re-run the same conversion
- Dynamic route: `params.id` identifies the job
