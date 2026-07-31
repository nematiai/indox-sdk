# Official SDKs

Status of the official Indox API v1 SDK packages.

!!! warning "No Indox SDK is published yet"
    Every package below is **not yet published**. `pip install`, `npm install`,
    `composer require`, `gem install`, `go get`, and `cargo add` will **not** resolve for
    these names today. Until a row below says *Published*, talk to the API directly over
    HTTPS — see [Using the API in the meantime](#using-the-api-in-the-meantime).

| Language | Package | Status | Registry |
|---|---|---|---|
| Python | `indox-client` 0.4.0 | Not yet published | PyPI |
| TypeScript / JavaScript | `@indox/sdk` 0.1.0 | Not yet published | npm |
| PHP | `indox/indox` 0.1.0 | Not yet published | Packagist |
| Ruby | `indox` 0.1.0 | Not yet published | RubyGems |
| Java | `org.indox:indox-sdk` 0.1.0 | Not yet published | Maven Central |
| C# / .NET | `Indox.Sdk` 0.1.0 | Not yet published | NuGet |
| Go | `github.com/nematiai/indox-go` | Not yet published | Go module proxy |
| Rust | `indox` 0.1.0 | Not yet published | crates.io |

**Not planned as SDKs:** SQL, HTML/CSS. **Deferred:** C++, R, Kotlin, Swift.

## Using the API in the meantime

Every SDK is a thin wrapper over the same public REST API, so nothing is blocked on the
packages shipping. Create an API key in the web app under **Dashboard → API keys**, then
call `https://indox.org` with a bearer token:

```bash
curl -sS https://indox.org/api/v1/health/ \
  -H "Authorization: Bearer $INDOX_API_KEY" \
  -H "Accept: application/json"
```

See the [API reference](../client/api-reference.md) for the full endpoint list, and
[Integrations](../client/integrations.md) for end-to-end conversion flows.

This page is the single source of truth for availability. A language is only announced as
available once its package is live on the registry listed above.
