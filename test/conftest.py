import os
import tempfile

_FS = tempfile.mkdtemp(prefix="gui1-demo-test-")
for _name in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME", "XDG_STATE_HOME"):
    os.environ[_name] = os.path.join(_FS, _name.lower())

import pytest  # noqa: E402
from ovos_bus_client.message import Message  # noqa: E402
from ovos_utils.fakebus import FakeBus  # noqa: E402

from ovos_skill_gui1_demo import GUI1DemoSkill  # noqa: E402

SKILL_ID = "ovos-skill-gui1-demo.oscillatelabs"
SESSION = "kitchen"
GUI_TYPES = ("gui.value.set", "gui.page.show", "gui.clear.namespace")


class RecordingBus(FakeBus):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sent: list[Message] = []

    def emit(self, message):
        super().emit(message)
        self.sent.append(message)

    def gui(self, prefixes=("gui.",)) -> list[Message]:
        return [m for m in self.sent if m.msg_type.startswith(prefixes)]


@pytest.fixture
def bus():
    fake = RecordingBus()
    fake.run_forever()
    return fake


@pytest.fixture
def skill(bus):
    instance = GUI1DemoSkill(skill_id=SKILL_ID, bus=bus)
    instance.runner.time_scale = 0
    bus.sent.clear()
    yield instance
    instance.runner.cancel()


def utterance(intent: str, **data) -> Message:
    return Message(f"{SKILL_ID}:{intent}", data, {"session": {"session_id": SESSION}, "skill_id": SKILL_ID})
