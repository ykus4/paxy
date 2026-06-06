# Rule Engine

Rules let you block, modify, or redirect traffic without writing code.

## Rule structure

```json
{
  "id": 1,
  "name": "Block ads",
  "enabled": true,
  "priority": 10,
  "conditions": [
    { "field": "host", "op": "contains", "value": "ads.example.com" }
  ],
  "action": "block"
}
```

## Actions

| Action | Effect |
|--------|--------|
| `passthrough` | Allow without change (useful for whitelisting over a broader rule) |
| `block` | Return HTTP 403 to the client |
| `modify` | Apply `modifications` to the request and/or response |
| `redirect` | Return HTTP 302 to `redirect_url` |

## Conditions

All conditions in a rule must match (AND logic). Use multiple rules if you need OR logic.

### Fields

| Field | Evaluated against |
|-------|------------------|
| `host` | Host header |
| `path` | URL path |
| `method` | HTTP method |
| `header` | Any header value (format: `Header-Name: value`) |
| `body` | Request body as a string |

### Operators

| Op | Description |
|----|-------------|
| `equals` | Exact match |
| `contains` | Substring match |
| `prefix` | Starts with |
| `regex` | Python `re`-compatible regular expression |

Set `"negate": true` to invert any condition.

## Modifications

Used with `action: modify`.

```json
{
  "action": "modify",
  "modifications": [
    {
      "target": "req_header",
      "key": "X-Debug",
      "value": "1",
      "operation": "set"
    },
    {
      "target": "resp_body",
      "operation": "find_replace",
      "find": "production",
      "replace": "staging"
    }
  ]
}
```

### Targets

| Target | Description |
|--------|-------------|
| `req_header` | Request header |
| `resp_header` | Response header |
| `req_body` | Request body |
| `resp_body` | Response body |

### Operations

| Operation | Description |
|-----------|-------------|
| `set` | Set header key to value (overwrites) |
| `delete` | Delete header key |
| `append` | Append value to header |
| `replace` | Replace entire body with `value` |
| `find_replace` | Replace `find` with `replace` in body |

## Priority

Higher `priority` = evaluated first. When multiple rules match, only the highest-priority rule fires.

## Managing rules via API

```bash
# Create
curl -X POST http://localhost:8081/api/rules \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "Add debug header",
    "enabled": true,
    "priority": 5,
    "conditions": [{"field": "host", "op": "contains", "value": "api.example.com"}],
    "action": "modify",
    "modifications": [{"target": "req_header", "key": "X-Debug", "value": "true", "operation": "set"}]
  }'

# List
curl http://localhost:8081/api/rules

# Update rule 1
curl -X PUT http://localhost:8081/api/rules/1 \
  -H 'Content-Type: application/json' \
  -d '{"enabled": false, ...}'

# Delete rule 1
curl -X DELETE http://localhost:8081/api/rules/1
```
