"""The skill's GUI-1 producer: ovos-workshop's GUIInterface, plus the two things it cannot do on its own.

1. GUIInterface builds every message as ``Message(type, data)`` with no context, so the bus client stamps its
   own session (``default``) instead of the session of the utterance being served (OVOS-GUI-1 5.1, 8.1).
   ``OriginBus`` copies the originating message's context onto each GUI message before it is sent.
2. GUIInterface has no call for the ambient topics (6.9.1), so ``Display.ambient`` emits them on the bus.
"""

import copy
from typing import Any

from ovos_bus_client.apis.gui import GUIInterface
from ovos_bus_client.message import Message


class OriginBus:
    """A bus proxy that gives each context-less message the context of ``origin``."""

    def __init__(self, bus):
        self._bus = bus
        self.origin: Message | None = None

    def emit(self, message: Message):
        if self.origin is not None and "session" not in message.context:
            message.context = {**copy.deepcopy(self.origin.context), **message.context}
        return self._bus.emit(message)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._bus, name)


class Display:
    """One namespace's display, driven only through GUIInterface's public calls."""

    def __init__(self, gui: GUIInterface, origin_bus: OriginBus, skill_id: str):
        self.gui = gui
        self.origin_bus = origin_bus
        self.skill_id = skill_id
        gui.set_bus(origin_bus)

    def serve(self, message: Message) -> None:
        """Send what follows in the context of ``message``."""
        self.origin_bus.origin = message

    def show(self, template: str, data: dict, idle: bool | int) -> None:
        """Clear stale keys, then one batched ``gui.value.set`` and one ``gui.page.show`` (8.2)."""
        self.clear_if_showing()
        for key, value in data.items():
            self.gui[key] = value
        self.gui.show_page(template, override_idle=idle)

    def update(self, key: str, value: Any) -> None:
        """Set one key, or remove it with an explicit ``None`` (3.3); GUIInterface sends ``gui.value.set``."""
        self.gui[key] = value

    def clear_if_showing(self) -> bool:
        if not self.gui.page:
            return False
        self.gui.clear()
        return True

    def clear(self) -> None:
        self.gui.clear()

    def ambient(self, topic: str, data: dict) -> None:
        self.origin_bus.emit(Message(topic, {"__from": self.skill_id, **data}))

    def notify(self, record: dict) -> dict:
        """Raise a notification popup as ovos-shell's notification API does (``ovos.notification.api.set``); the
        record is returned filled in, so the same one can clear it later."""
        full = {"sender": self.skill_id, "duration": 10, "action": None, "type": "transient", "style": "info"}
        full.update({"callback_data": {}, **record})
        self.origin_bus.emit(Message("ovos.notification.api.set", full))
        return full

    def clear_notification(self, record: dict) -> None:
        """Take a popup down and off storage (``ovos.notification.api.pop.clear.delete``), by sender and text."""
        self.origin_bus.emit(Message("ovos.notification.api.pop.clear.delete", {"notification": record}))
