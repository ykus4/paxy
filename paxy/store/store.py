from __future__ import annotations

import asyncio
import threading
from typing import Callable, List, Optional, Tuple

from .models import Entry, Filter


class Store:
    def __init__(self) -> None:
        self._entries: List[Entry] = []
        self._by_id: dict[int, Entry] = {}
        self._counter = 0
        self._lock = threading.Lock()
        self._subscribers: List[asyncio.Queue] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def add(self, entry: Entry) -> Entry:
        with self._lock:
            self._counter += 1
            entry.id = self._counter
            self._entries.append(entry)
            self._by_id[entry.id] = entry
        self._publish(entry)
        return entry

    def update(self, entry: Entry) -> None:
        with self._lock:
            self._by_id[entry.id] = entry
        self._publish(entry)

    def get(self, entry_id: int) -> Optional[Entry]:
        return self._by_id.get(entry_id)

    def list(
        self, f: Filter, offset: int = 0, limit: int = 100
    ) -> Tuple[List[Entry], int]:
        with self._lock:
            filtered = [e for e in self._entries if f.matches(e)]
        total = len(filtered)
        if limit == 0:
            return filtered[offset:], total
        return filtered[offset: offset + limit], total

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
            self._by_id.clear()

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=512)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        with self._lock:
            try:
                self._subscribers.remove(q)
            except ValueError:
                pass

    def _publish(self, entry: Entry) -> None:
        if self._loop is None:
            return
        with self._lock:
            subs = list(self._subscribers)
        for q in subs:
            try:
                self._loop.call_soon_threadsafe(q.put_nowait, entry)
            except asyncio.QueueFull:
                pass
