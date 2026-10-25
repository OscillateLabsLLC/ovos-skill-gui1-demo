"""What ovos-bus-client's GUIInterface (used by ovos-workshop's SkillGUI) puts on the wire without the skill's help.

These pin the findings in DEMO_SKILL.md. A failure here means GUIInterface changed: re-check the finding.
"""

import pytest
from conftest import RecordingBus, utterance
from ovos_bus_client.apis.gui import GUIInterface

NAMESPACE = "finding.test"


@pytest.fixture
def plain_gui():
    bus = RecordingBus()
    bus.run_forever()
    return GUIInterface(NAMESPACE, bus=bus, config={}), bus


def show_in_handler(gui, message):
    gui["text"] = "hello"
    gui.show_page("SYSTEM_text")


def test_gui_messages_lose_the_utterance_session(plain_gui):
    gui, bus = plain_gui
    show_in_handler(gui, utterance("show_template"))
    assert {m.context["session"]["session_id"] for m in bus.gui()} == {"default"}


def test_show_page_sends_null_idle_and_an_unspecified_reserved_key(plain_gui):
    gui, bus = plain_gui
    gui.show_page("SYSTEM_text")
    page = bus.gui()[-1].data
    assert "__idle" in page and page["__idle"] is None
    assert page["__animations"] is False


def test_each_key_after_show_is_its_own_full_map_value_set(plain_gui):
    gui, bus = plain_gui
    gui.show_page("SYSTEM_text")
    bus.sent.clear()
    gui["text"] = "one"
    gui["title"] = "two"
    assert [sorted(m.data) for m in bus.gui()] == [["__from", "text"], ["__from", "text", "title"]]


def test_a_removed_key_is_sent_as_null_again_on_every_later_sync(plain_gui):
    gui, bus = plain_gui
    gui["title"] = "set once"
    gui.show_page("SYSTEM_text")
    gui["title"] = None
    bus.sent.clear()
    gui["text"] = "later"
    assert bus.gui()[-1].data["title"] is None


@pytest.mark.parametrize(
    "helper, args, legacy_name", [("show_text", ("x",), "SYSTEM_TextFrame"), ("show_face", (), "SYSTEM_Face")]
)
def test_convenience_helpers_send_legacy_page_names(plain_gui, helper, args, legacy_name):
    gui, bus = plain_gui
    getattr(gui, helper)(*args)
    assert bus.gui()[-1].data["page_names"] == [legacy_name]
