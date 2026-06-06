# API Reference

The API server runs on `http://localhost:8081` by default.
In GUI mode it is mounted under `/api` on the NiceGUI server.
In CUI mode it is served directly by uvicorn.

## Traffic

### `GET /api/traffic`

List captured entries.

**Query parameters:**

| Parameter | Description |
|-----------|-------------|
| `offset` | Pagination offset (default 0) |
| `limit` | Max results (default 100) |
| `method` | Filter by HTTP method |
| `host` | Filter by exact hostname |
| `search` | Substring match on host + path |
| `protocol` | Filter by `http`, `https`, `ws`, or `grpc` |

**Response:**

```json
{
  "entries": [...],
  "total": 42,
  "offset": 0,
  "limit": 100
}
```

### `GET /api/traffic/{id}`

Get a single entry by ID.

---

## Rules

### `GET /api/rules`

List all rules.

### `POST /api/rules`

Create a rule. Body: Rule object (omit `id`).

### `PUT /api/rules/{id}`

Update a rule. Body: full Rule object.

### `DELETE /api/rules/{id}`

Delete a rule. Returns `204 No Content`.

---

## Replay

### `POST /api/replay`

Replay a captured entry.

**Body:**

```json
{
  "entry_id": 42,
  "options": {
    "override_host": "staging.example.com",
    "extra_headers": { "X-Test": "1" },
    "timeout_seconds": 30,
    "count": 1
  }
}
```

**Response:** Array of `ReplayResult` objects.

---

## Misc

### `POST /api/clear`

Delete all captured entries. Returns `204 No Content`.

---

## WebSocket

### `GET /ws`

Upgrade to WebSocket. Receives a stream of `Entry` JSON objects as traffic is captured.

```javascript
const ws = new WebSocket('ws://localhost:8081/ws')
ws.onmessage = (e) => {
  const entry = JSON.parse(e.data)
  console.log(entry.method, entry.host, entry.status_code)
}
```

---

## Schemas

### Entry

```python
{
  "id":           int,
  "created_at":   str,                    # ISO 8601
  "method":       str,
  "scheme":       str,                    # "http" | "https" | "ws"
  "host":         str,
  "path":         str,
  "query":        str,
  "req_headers":  dict[str, list[str]],
  "req_body":     str,                    # base64-encoded
  "status_code":  int,
  "resp_headers": dict[str, list[str]],
  "resp_body":    str,                    # base64-encoded
  "duration_ms":  int,
  "protocol":     str,
  "tags":         list[str],
  "modified":     bool
}
```

### Rule

```python
{
  "id":            int,
  "name":          str,
  "enabled":       bool,
  "priority":      int,
  "conditions":    list[Condition],
  "action":        "passthrough" | "modify" | "block" | "redirect",
  "modifications": list[Modification],
  "redirect_url":  str
}
```

### ReplayResult

```python
{
  "entry_id":    int,
  "status_code": int,
  "body":        str,   # base64-encoded
  "duration_ms": int,
  "error":       str
}
```
