# Other language SDKs

Clients for PHP, Ruby, Java, C#, Go, and Rust are built from the same public OpenAPI schema as
the Python and TypeScript SDKs.

!!! warning "None of these are published"
    No PHP, Ruby, Java, C#, Go, or Rust Indox package is available from a registry yet, so
    `composer require`, `gem install`, a Maven/NuGet dependency, `go get`, and `cargo add`
    will not resolve. See the [SDK status table](index.md).

## Until they ship — call the API directly

Each client is a thin wrapper over the same REST endpoints, so no functionality is gated on
the packages. Create an API key under **Dashboard → API keys** and send it as a bearer token
against `https://indox.org`:

```bash
curl -sS https://indox.org/api/v1/health/ \
  -H "Authorization: Bearer $INDOX_API_KEY" \
  -H "Accept: application/json"
```

The [API reference](../client/api-reference.md) lists every public endpoint, request shape,
and response schema — enough to write a client in any language with an HTTP library.

## What the packages will look like

All of them read the API key from `INDOX_API_KEY`, default the base URL to `https://indox.org`,
and accept an override (`INDOX_BASE_URL`) for self-hosted deployments.
