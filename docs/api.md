# API Reference

The API server runs on `http://localhost:8081` by default.

## Traffic

### `GET /api/traffic`

List captured entries.

**Query parameters:** `offset`, `limit`, `method`, `host`, `search`, `protocol`

### `GET /api/traffic/{id}`

Get a single entry by ID.

---

## Rules

### `GET /api/rules` · `POST /api/rules` · `PUT /api/rules/{id}` · `DELETE /api/rules/{id}`

CRUD for intercept rules.

---

## Replay

### `POST /api/replay`

```json
{"entry_id": 42, "options": {"override_host": "staging.example.com", "count": 1}}
```

---

## Bulk Sender

### `POST /api/bulk`

```json
{"entry_id": 42, "mode": "payloads", "payloads": [{"label": "p1", "body": "..."}], "concurrency": 10}
```

`mode`: `"payloads"` or `"race"`

---

## Active Scan

### `POST /api/scan`

```json
{"entry_id": 42, "categories": ["xss", "sqli", "cmdi", "ssti", "path_traversal"], "concurrency": 5}
```

---

## Export / Import

| Endpoint | Description |
|----------|-------------|
| `GET /api/export/json` | Export all entries + rules as JSON |
| `GET /api/export/har` | Export all entries as HAR 1.2 |
| `POST /api/import/har` | Import entries from HAR body |
| `POST /api/import/json` | Import entries from paxy JSON body |
| `POST /api/import/rules` | Import rules from JSON body |

---

## Full-text Search

### `GET /api/search?q=keyword&limit=50`

Search across host, path, request body, response body, and headers using SQLite FTS5.

---

## Scope

### `GET /api/scope`

Returns `{"enabled": bool, "rules": [...]}`.

### `POST /api/scope`

```json
{"enabled": true, "add": {"pattern": "*.example.com", "mode": "glob"}}
{"remove": "*.example.com"}
```

---

## GraphQL

### `POST /api/graphql/introspect`

```json
{"url": "https://api.example.com/graphql", "headers": {"Authorization": "Bearer token"}}
```

### `GET /api/graphql/schemas`

List cached schemas: `[{"host": "api.example.com", "query_type": "Query", ...}]`

### `GET /api/graphql/schema/{host}`

Full schema object for a host.

### `DELETE /api/graphql/schema/{host}`

Remove cached schema. Returns `204`.

### `POST /api/graphql/replay`

```json
{"entry_id": 42, "query": "query { user { id } }", "variables": {"id": "123"}}
```

---

## Misc

### `POST /api/clear`

Delete all captured entries. Returns `204`.

---

## WebSocket

### `GET /ws`

Upgrade to WebSocket. Pushes `Entry` JSON objects in real time.

---

## Schemas

### Entry

```python
{
  "id": int, "created_at": str,
  "method": str, "scheme": str, "host": str, "path": str, "query": str,
  "req_headers": dict, "req_body": str,          # base64
  "status_code": int, "resp_headers": dict, "resp_body": str,  # base64
  "duration_ms": int, "protocol": str,
  "tags": list[str], "modified": bool, "color": str,
  "graphql_operation": str, "graphql_op_type": str
}
```
