# gRPC & WebSocket

## WebSocket

WebSocket connections are detected automatically and intercepted as part of the HTTPS MITM flow.

### How it works

1. The client sends a CONNECT request to the proxy.
2. paxy terminates TLS (same as HTTPS MITM).
3. When paxy sees `Upgrade: websocket` in the decrypted stream, it switches to WebSocket relay mode.
4. Frames are relayed between client and server while being logged.

### Frame logging

```
ws frame entry=12 dir=client text={"type":"ping"}
ws frame entry=12 dir=server text={"type":"pong"}
```

### In the UI

WebSocket connections appear in the traffic list with the `websocket` tag and `ws` protocol.
Individual frames are logged to the console. Per-frame display in the UI is planned for a future release.

### Limitations

- Frame-level modification is not yet supported in the rule engine. Use a Python script hook instead.
- `permessage-deflate` compressed frames are relayed as-is without decompression.

---

## gRPC

gRPC uses HTTP/2 over TLS with a 5-byte length-prefix framing.
paxy detects it via the `Content-Type: application/grpc` header.

### How it works

1. TLS is terminated normally as part of HTTPS MITM.
2. The `application/grpc` content type triggers frame decoding.
3. Each frame's metadata (compressed flag, length) is logged.

### Frame logging

```
grpc frame entry=7 dir=request  index=0 compressed=False len=42
grpc frame entry=7 dir=response index=0 compressed=False len=128
```

### Decoding Protobuf

paxy stores raw bytes. Use external tooling to decode:

```bash
# Fetch the entry, decode the base64 body, pipe to protoc
curl -s http://localhost:8081/api/traffic/7 \
  | python3 -c "
import sys, json, base64
d = json.load(sys.stdin)
print(base64.b64decode(d['req_body']).hex())
"
```

---

## Certificate pinning

Apps that use certificate pinning will reject paxy's dynamically generated certificate.
Add those hosts to the `ignore` list in the config to tunnel them through without MITM:

```yaml
proxy:
  ignore:
    - pinned-api.example.com
```

paxy will create a raw TCP tunnel for ignored hosts instead of intercepting them.
