# TypeScript / JavaScript SDK

Package: `@indox/sdk` — covers both TypeScript and JavaScript (ESM).

!!! warning "Not yet published"
    `npm install @indox/sdk` does **not** resolve yet. See the
    [SDK status table](index.md) for the current state of every language.

## Until it ships — call the API directly

Auth is a bearer API key created under **Dashboard → API keys**. Keep it server-side; never
ship it to a browser bundle.

```js
const res = await fetch("https://indox.org/api/v1/health/", {
  headers: {
    Authorization: `Bearer ${process.env.INDOX_API_KEY}`,
    Accept: "application/json",
  },
  signal: AbortSignal.timeout(60_000),
});
const body = await res.json();
```

Conversions are asynchronous: `POST` the job, then poll the returned conversion id until it
reaches a terminal status, then download the result. The
[API reference](../client/api-reference.md) documents each endpoint.

## What the package will look like

Once published, the client reads `INDOX_API_KEY` from the environment (or takes an `apiKey`
option) and defaults its base URL to `https://indox.org`; `INDOX_BASE_URL` overrides it for
self-hosted deployments.
