# Architecture

## Overview

```
┌──────────────────────────────────────────────────────────┐
│  Client (browser / mobile app)                           │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTP / CONNECT
┌────────────────────────▼─────────────────────────────────┐
│  paxy/proxy/proxy.py  (port :8080)                       │
│  asyncio TCP server                                      │
│  ├─ HTTP  → intercept → forward upstream                 │
│  ├─ CONNECT → terminate TLS (MITM)                       │
│  │    ├─ HTTP/HTTPS → intercept → forward upstream       │
│  │    ├─ WebSocket  → paxy/proto/ws.py                   │
│  │    └─ gRPC       → paxy/proto/grpc.py                 │
│  └─ ignored hosts → raw TCP tunnel (passthrough)         │
└─────────────┬────────────────────────┬───────────────────┘
              │                        │
┌─────────────▼──────┐    ┌────────────▼──────────────────┐
│  paxy/cert/ca.py   │    │  paxy/interceptor/             │
│  CA + per-host     │    │  apply rules, record entries   │
│  SSL Context cache │    └────────────┬───────────────────┘
└────────────────────┘                 │
                          ┌────────────▼───────────────────┐
                          │  paxy/store/store.py           │
                          │  in-memory traffic store       │
                          │  asyncio pub/sub               │
                          └────────────┬───────────────────┘
                                       │
          ┌────────────────────────────┼──────────────────────┐
          │                            │                      │
┌─────────▼──────────┐   ┌─────────────▼─────────┐  ┌────────▼──────────┐
│  paxy/api/         │   │  paxy/ui/app.py        │  │  paxy/ui/cui.py   │
│  FastAPI REST API  │   │  NiceGUI browser UI    │  │  rich terminal UI │
│  + WebSocket /ws   │   │  (GUI mode)            │  │  (CUI mode)       │
└────────────────────┘   └────────────────────────┘  └───────────────────┘
```

## Package overview

| Package | Responsibility |
|---------|----------------|
| `paxy/proxy` | asyncio TCP server; plain HTTP forwarding; TLS MITM for CONNECT; raw tunnel for ignored hosts |
| `paxy/cert` | CA certificate generation; per-host SSL Context cache |
| `paxy/interceptor` | Apply rules to requests and responses; record entries in the store |
| `paxy/rule` | Rule evaluation engine; condition matching; priority ordering |
| `paxy/store` | Thread-safe in-memory traffic store; asyncio pub/sub for live updates |
| `paxy/api` | FastAPI REST endpoints and WebSocket streaming |
| `paxy/ui/app` | NiceGUI browser UI (GUI mode) |
| `paxy/ui/cui` | rich terminal UI (CUI mode) |
| `paxy/proto/ws` | WebSocket frame relay and logging |
| `paxy/proto/grpc` | gRPC length-prefix frame decoding |
| `paxy/script` | Python script engine; `on_request` / `on_response` hooks |
| `paxy/replay` | Async HTTP replay and parallel fuzzing via httpx |
| `paxy/config` | YAML config loading |

## Key design decisions

### asyncio TCP server

The proxy is a raw `asyncio.start_server` TCP server that parses HTTP manually.
This lets a single connection handle HTTP/1.1 keep-alive, CONNECT tunnels, and WebSocket upgrades
without switching servers mid-connection.

### TLS termination with `loop.start_tls()`

After responding `200 Connection Established` to a CONNECT request, paxy calls `loop.start_tls()`
to upgrade the existing asyncio transport to TLS server-side. This avoids creating a second connection
and keeps the code path simple. Per-host certificates are cached as `ssl.SSLContext` objects so they
are only generated once per hostname per process lifetime.

### Store pub/sub across threads

The proxy runs in the asyncio event loop. When it calls `store.add()` or `store.update()` from a
coroutine, the store uses `loop.call_soon_threadsafe` to push the entry into each subscriber's
`asyncio.Queue`. The UI and API layers `await` these queues to receive live updates with no polling.

### GUI vs CUI startup

In **GUI mode**, `ui.run()` owns the event loop and the proxy is launched via `nicegui_app.on_startup`.
In **CUI mode**, `asyncio.run()` owns the loop and `asyncio.gather` runs the proxy, uvicorn API server,
and rich TUI concurrently. Both modes expose the same REST API at `:8081`.

### Python script engine

Scripts are loaded with `importlib.util.spec_from_file_location` into their own module namespace.
`on_request` and `on_response` are looked up by name and called if they exist.
The full Python standard library and any installed packages are available with no extra configuration.
