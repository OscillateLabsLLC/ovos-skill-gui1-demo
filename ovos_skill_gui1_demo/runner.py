"""Runs one demo at a time on a worker thread, so a long demo never blocks the intent handler and stop can end it."""

import threading
from collections.abc import Callable

from ovos_bus_client.message import Message
from ovos_utils.log import LOG

JOIN_SECONDS = 5

Pause = Callable[[float], bool]
Demo = Callable[[Message, Pause], None]


class DemoRunner:
    def __init__(self, time_scale: float = 1.0):
        self.time_scale = time_scale
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    @property
    def busy(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self, name: str, demo: Demo, message: Message) -> None:
        """Cancel any running demo, then run ``demo`` with the message it serves."""
        self.cancel()
        self._stop = threading.Event()
        self._thread = threading.Thread(
            target=self._run, args=(message, name, demo, self._stop), daemon=True, name=f"gui1-demo-{name}"
        )
        self._thread.start()

    def cancel(self) -> bool:
        """Stop the running demo. True if one was running."""
        was_busy = self.busy
        self._stop.set()
        self.join()
        return was_busy

    def join(self, timeout: float = JOIN_SECONDS) -> None:
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout)

    def _run(self, message: Message, name: str, demo: Demo, stop: threading.Event) -> None:
        def pause(seconds: float) -> bool:
            return not stop.wait(seconds * self.time_scale)

        try:
            demo(message, pause)
        except Exception:
            LOG.exception(f"gui1-demo: demo {name} failed")
