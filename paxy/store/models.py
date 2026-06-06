from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class Entry:
    id: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Request
    method: str = ""
    scheme: str = ""
    host: str = ""
    path: str = ""
    query: str = ""
    req_headers: Dict[str, List[str]] = field(default_factory=dict)
    req_body: bytes = b""

    # Response
    status_code: int = 0
    resp_headers: Dict[str, List[str]] = field(default_factory=dict)
    resp_body: bytes = b""
    duration_ms: int = 0

    # Meta
    protocol: str = "http"
    tags: List[str] = field(default_factory=list)
    modified: bool = False

    def to_dict(self) -> dict:
        import base64
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "method": self.method,
            "scheme": self.scheme,
            "host": self.host,
            "path": self.path,
            "query": self.query,
            "req_headers": self.req_headers,
            "req_body": base64.b64encode(self.req_body).decode() if self.req_body else "",
            "status_code": self.status_code,
            "resp_headers": self.resp_headers,
            "resp_body": base64.b64encode(self.resp_body).decode() if self.resp_body else "",
            "duration_ms": self.duration_ms,
            "protocol": self.protocol,
            "tags": self.tags,
            "modified": self.modified,
        }


@dataclass
class Filter:
    method: str = ""
    host: str = ""
    search: str = ""
    protocol: str = ""

    def matches(self, entry: Entry) -> bool:
        if self.method and entry.method != self.method:
            return False
        if self.host and entry.host != self.host:
            return False
        if self.protocol and entry.protocol != self.protocol:
            return False
        if self.search and self.search.lower() not in (entry.host + entry.path).lower():
            return False
        return True
