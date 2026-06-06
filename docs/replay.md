# Replay & Fuzzing

Resend any captured request as-is, or fire hundreds of parallel copies for load testing and fuzzing.

## Replay from the GUI

1. Click any row in the traffic list to open the detail panel.
2. Click the **Replay** button.
3. The result (status code and body size) appears as a toast notification.

## Replay via API

```bash
curl -X POST http://localhost:8081/api/replay \
  -H 'Content-Type: application/json' \
  -d '{
    "entry_id": 42,
    "options": {}
  }'
```

Response:

```json
[
  {
    "entry_id": 42,
    "status_code": 200,
    "body": "...(base64)...",
    "duration_ms": 134,
    "error": ""
  }
]
```

## Options

| Field | Type | Description |
|-------|------|-------------|
| `override_host` | string | Send to a different host (e.g. staging) |
| `extra_headers` | object | Headers to add or override |
| `timeout_seconds` | int | Per-request timeout (default 30) |
| `count` | int | Number of parallel replays (default 1) |

## Parallel replay (load test / fuzz)

```bash
curl -X POST http://localhost:8081/api/replay \
  -H 'Content-Type: application/json' \
  -d '{
    "entry_id": 42,
    "options": {
      "count": 100,
      "timeout_seconds": 10
    }
  }'
```

100 requests are issued concurrently via `asyncio.gather`. The response is an array of 100 results.

## Replay to a different host

Useful for running production traffic against a staging environment:

```bash
curl -X POST http://localhost:8081/api/replay \
  -H 'Content-Type: application/json' \
  -d '{
    "entry_id": 42,
    "options": {
      "override_host": "staging.example.com"
    }
  }'
```

## Replacing the auth token

```bash
curl -X POST http://localhost:8081/api/replay \
  -H 'Content-Type: application/json' \
  -d '{
    "entry_id": 42,
    "options": {
      "extra_headers": {
        "Authorization": "Bearer new-token"
      }
    }
  }'
```
