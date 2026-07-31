# @indox/sdk (TypeScript / JavaScript)

Official Indox API v1 client. Covers JavaScript consumers via the same package.

## Install (when published)

```bash
npm install @indox/sdk
```

Local (this monorepo):

```bash
cd sdk/typescript
# generated OpenAPI client lives in ./generated
# convenience wrapper: ./src/client.ts
```

## Auth

```ts
import { Indox } from "@indox/sdk";

const client = new Indox({
  apiKey: process.env.INDOX_API_KEY,
  baseUrl: process.env.INDOX_BASE_URL || "https://indox.org",
});

const health = await client.health.commonHealthViewsHealth();
```

`Authorization: Bearer ak_…`

## Regenerate

```bash
make sdk-openapi
make sdk-gen LANG=typescript
```

## Smoke

```bash
INDOX_API_KEY=ak_… INDOX_BASE_URL=http://localhost:41000 node sdk/typescript/smoke.mjs
```

**Publish:** only with explicit approval — do not npm publish until CI allowlist smoke is green.
