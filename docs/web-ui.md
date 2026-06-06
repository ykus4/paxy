# Web UI

## GUI Mode

Start paxy in GUI mode (the default) and open `http://localhost:8081`.
The UI is built with [NiceGUI](https://nicegui.io/) and runs in the same Python process as the proxy.

### Layout

```
┌──────────────────────────────────────────────────────┐
│  toolbar: paxy ● | Search | Method | Protocol | Clear│
├────────────────────────┬─────────────────────────────┤
│  Traffic list          │  Detail panel               │
│  (left 60%)            │  (right 40%)                │
│  click row to select   │  Request / Response         │
│                        │  Headers + Body             │
│                        │  Replay button              │
└────────────────────────┴─────────────────────────────┘
```

### Traffic list

New requests are prepended to the top of the list in real time via WebSocket.

| Column | Description |
|--------|-------------|
| ID | Sequential capture number |
| Method | HTTP method (color-coded badge) |
| Host | Hostname |
| Path | Path including query string |
| Status | HTTP status (color-coded badge) |
| ms | Response time in milliseconds |
| Tags | `blocked`, `modified`, `websocket`, etc. |

Row highlights:
- **Yellow** — entry was modified by a rule
- **Red** — entry was blocked by a rule

### Filters

All filters apply instantly without a page reload.

| Filter | Description |
|--------|-------------|
| Search box | Substring match on host + path |
| Method | Exact match (GET, POST, …) |
| Protocol | `http` / `https` / `ws` / `grpc` |

### Detail panel

Click any row to open the detail panel on the right.

**Request**

- Method and full URL
- Request headers (key/value table)
- Request body (pretty-printed if JSON)

**Response**

- Status code and response time
- Response headers
- Response body (pretty-printed if JSON)

**Replay button** — resends the original request and shows the result as a toast notification.

### Clear

The **Clear** button in the toolbar deletes all captured entries from memory.

---

## CUI Mode

```bash
uv run python main.py --mode cui
```

A rich-rendered table updates in real time inside the terminal.

```
┌─ paxy  MITM Proxy  [42 requests] ──────────────────────────────┐
│                                                                  │
│  ID  Method   Host                Path               Status  ms │
│  42  GET      api.example.com     /v1/users             200  134│
│  41  POST     auth.example.com    /login                200   89│
│  40  GET      cdn.example.com     /assets/main.js       304   12│
│  ...                                                             │
└──────────────────────────────────────────────────────────────────┘
  proxy :8080  API http://localhost:8081/api    q: quit  c: clear
```

### Key bindings

| Key | Action |
|-----|--------|
| `q` / `Ctrl+C` | Quit |
| `c` | Clear traffic |

The REST API remains available at `:8081` in CUI mode, so you can query it from another terminal with `curl`.
