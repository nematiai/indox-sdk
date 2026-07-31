# Document Conversion API

Base path: `/api/v1/pdf_handler/`

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/convert/` | Submit conversion → `202 { conversion_id }` |
| `GET`  | `/conversion/{id}/` | Get status |
| `GET`  | `/{id}/download/` | Redirect to presigned URL |

See [Quickstart](../quickstart.md) for a worked example and [Concepts → Polling cadence](../concepts.md#polling-cadence) for backoff guidance.
