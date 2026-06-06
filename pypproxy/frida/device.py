from __future__ import annotations

import asyncio
import logging
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


def _frida_available() -> bool:
    try:
        import frida  # noqa: F401

        return True
    except ImportError:
        return False


@dataclass
class DeviceInfo:
    id: str
    name: str
    type: str  # usb, local, remote

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "type": self.type}


@dataclass
class ProcessInfo:
    pid: int
    name: str
    identifier: str = ""  # bundle id / package name

    def to_dict(self) -> dict:
        return {"pid": self.pid, "name": self.name, "identifier": self.identifier}


@dataclass
class InjectionSession:
    device_id: str
    target: str  # pid or bundle id
    script_name: str
    running: bool = False
    output: list[str] = field(default_factory=list)
    error: str = ""
    _script: Any = field(default=None, repr=False)
    _session: Any = field(default=None, repr=False)
    _on_message: Callable | None = field(default=None, repr=False)


class FridaManager:
    """Manages Frida device enumeration, process listing, and script injection."""

    def __init__(self) -> None:
        self._sessions: dict[str, InjectionSession] = {}
        self._lock = threading.Lock()

    def is_available(self) -> bool:
        return _frida_available()

    def list_devices(self) -> list[DeviceInfo]:
        if not _frida_available():
            return []
        try:
            import frida

            devices = frida.enumerate_devices()
            return [
                DeviceInfo(
                    id=d.id,
                    name=d.name,
                    type=d.type,
                )
                for d in devices
                if d.type in ("usb", "local", "remote")
            ]
        except Exception as e:
            logger.warning("frida.enumerate_devices failed: %s", e)
            return []

    def list_processes(self, device_id: str) -> list[ProcessInfo]:
        if not _frida_available():
            return []
        try:
            import frida

            device = frida.get_device(device_id)
            processes = device.enumerate_processes()
            return [
                ProcessInfo(
                    pid=p.pid,
                    name=p.name,
                    identifier=getattr(p, "identifier", "") or "",
                )
                for p in processes
            ]
        except Exception as e:
            logger.warning("enumerate_processes failed: %s", e)
            return []

    async def inject(
        self,
        device_id: str,
        target: str,  # bundle id / package name, or "pid:<number>"
        script_source: str,
        on_message: Callable[[str], None] | None = None,
        spawn: bool = True,
    ) -> InjectionSession:
        """Inject a Frida script into the target app."""
        if not _frida_available():
            sess = InjectionSession(
                device_id=device_id,
                target=target,
                script_name="script",
                error="frida is not installed. Run: pip install frida",
            )
            return sess

        sess = InjectionSession(
            device_id=device_id,
            target=target,
            script_name="pypproxy_script",
            _on_message=on_message,
        )

        loop = asyncio.get_event_loop()

        def _run() -> None:
            try:
                import frida

                device = frida.get_device(device_id)

                if target.startswith("pid:"):
                    pid = int(target[4:])
                    session = device.attach(pid)
                elif spawn:
                    pid = device.spawn([target])
                    session = device.attach(pid)
                    device.resume(pid)
                else:
                    session = device.attach(target)

                sess._session = session

                script = session.create_script(script_source)
                sess._script = script

                def _on_msg(message: dict, data: Any) -> None:
                    text = ""
                    if message.get("type") == "log":
                        text = str(message.get("payload", ""))
                    elif message.get("type") == "error":
                        text = (
                            f"[ERROR] {message.get('description', '')} {message.get('stack', '')}"
                        )
                    else:
                        text = str(message)

                    sess.output.append(text)
                    if on_message:
                        loop.call_soon_threadsafe(on_message, text)

                script.on("message", _on_msg)
                script.load()
                sess.running = True
                logger.info("Frida script injected into %s on device %s", target, device_id)

            except Exception as e:
                sess.error = str(e)
                sess.running = False
                logger.warning("Frida injection failed: %s", e)

        await loop.run_in_executor(None, _run)

        with self._lock:
            self._sessions[f"{device_id}:{target}"] = sess

        return sess

    def detach(self, device_id: str, target: str) -> None:
        key = f"{device_id}:{target}"
        with self._lock:
            sess = self._sessions.get(key)
        if sess:
            try:
                if sess._script:
                    sess._script.unload()
                if sess._session:
                    sess._session.detach()
            except Exception as e:
                logger.debug("detach error: %s", e)
            sess.running = False
            with self._lock:
                self._sessions.pop(key, None)

    def list_sessions(self) -> list[InjectionSession]:
        with self._lock:
            return list(self._sessions.values())
