# Error Codes

All errors follow the shape:

```json
{
  "error": "human-readable message",
  "code": "MACHINE_READABLE_CODE",
  "details": { … optional }
}
```

## HTTP status reference

| Status | When | Common causes |
|---|---|---|
| `400` | Bad request | Missing field, unsupported format, malformed JSON |
| `401` | Unauthorized | Missing/expired token |
| `402` | Payment required | Free quota exhausted, paid balance = 0 |
| `403` | Forbidden | Token valid but permission denied for this resource |
| `404` | Not found | Wrong `conversion_id`, deleted resource |
| `405` | Method not allowed | Bad auth payload (e.g. token without `user_id`) |
| `413` | Payload too large | File exceeds tier limit — see [Limits](limits.md) |
| `415` | Unsupported media type | Format not in the service's supported list |
| `429` | Too many requests | Rate-limited; back off |
| `500` | Server error | Bug — report with `conversion_id` |
| `502` | Bad gateway | Upstream worker crashed; retry safe |
| `503` | Service unavailable | Maintenance, transient infra issue |

## Free-quota example

```http
HTTP/1.1 402 Payment Required
Content-Type: application/json

{"error": "Free quota ended. Try paid version."}
```

## Paid-tier no-credits example

```http
HTTP/1.1 402 Payment Required
Content-Type: application/json

{"error": "No credits. Please recharge your account."}
```
