"""Each intent's exact GUI-1 wire sequence, through a FakeBus."""

from conftest import GUI_TYPES, SESSION, SKILL_ID, utterance
from ovos_plugin_manager.skills import find_skill_plugins

from ovos_skill_gui1_demo.faults import FAULTS
from ovos_skill_gui1_demo.templates import TEMPLATE_DATA

VS, PS, CL = GUI_TYPES
SPEAK = "ovos.utterance.speak"


def run(skill, handler, intent: str, **data):
    handler(utterance(intent, **data))
    skill.runner.join()
    return skill.bus.gui()


def spoken(skill):
    return [m for m in skill.bus.sent if m.msg_type == SPEAK]


def shape(messages) -> list:
    return [(m.msg_type, m.data["page_names"]) if m.msg_type == PS else m.msg_type for m in messages]


def assert_conforming_envelope(messages) -> None:
    for m in messages:
        assert m.data["__from"] == SKILL_ID, m.msg_type
        assert m.context["session"]["session_id"] == SESSION, m.msg_type


def show_sequence(templates) -> list:
    sequence = []
    for i, template in enumerate(templates):
        sequence += ([CL] if i else []) + [VS, (PS, [template])]
    return sequence + [CL]


def test_entry_point_is_discoverable():
    assert SKILL_ID in find_skill_plugins()


def test_show_template_weather(skill):
    sent = run(skill, skill.handle_show_template, "show_template", template="weather")
    assert shape(sent) == [VS, (PS, ["SYSTEM_weather"]), CL]
    assert_conforming_envelope(sent)
    assert set(sent[0].data) == set(TEMPLATE_DATA["SYSTEM_weather"](0)) | {"__from"}
    assert sent[1].data["__idle"] == 30


def test_show_template_media_player_sends_position_update(skill):
    sent = run(skill, skill.handle_show_template, "show_template", template="media player")
    assert shape(sent) == [VS, (PS, ["SYSTEM_media_player"]), VS, CL]
    assert_conforming_envelope(sent)
    assert sent[0].data["media_position"] == 0
    assert sent[2].data["media_position"] == 4000
    assert sent[2].data["media_playlist"] == sent[0].data["media_playlist"]


def test_show_template_unknown_word_sends_nothing(skill):
    assert run(skill, skill.handle_show_template, "show_template", template="hologram") == []
    assert [m.data["utterance"] for m in spoken(skill)] == ["I have no demo for hologram."]


def test_full_demo_cycles_every_template_then_clears(skill):
    sent = run(skill, skill.handle_full_demo, "run_full_demo")
    assert shape(sent) == show_sequence(TEMPLATE_DATA)
    assert_conforming_envelope(sent)
    assert all(m.data["__idle"] is True for m in sent if m.msg_type == PS)
    speeches = spoken(skill)
    assert len(speeches) == len(TEMPLATE_DATA) + 1
    assert {m.context["session"]["session_id"] for m in speeches} == {SESSION}


def test_degradation_demo_sends_each_fault_then_clears(skill):
    sent = run(skill, skill.handle_degradation_demo, "demo_degradation")
    assert shape(sent) == show_sequence([f.template for f in FAULTS])
    assert_conforming_envelope(sent)
    titles = [m.data["title"] for m in sent if m.msg_type == VS]
    assert titles == [f.data["title"] for f in FAULTS]


def test_update_demo_changes_text_then_removes_title_with_null(skill):
    sent = run(skill, skill.handle_update_demo, "demo_update")
    assert shape(sent) == [VS, (PS, ["SYSTEM_text"]), VS, VS, CL]
    assert_conforming_envelope(sent)
    first, changed, removed = sent[0].data, sent[2].data, sent[3].data
    assert changed["text"] != first["text"] and changed["title"] == first["title"]
    assert "title" in removed and removed["title"] is None


def test_ambient_demo_shows_no_template(skill):
    sent = run(skill, skill.handle_ambient_demo, "demo_ambient")
    assert [m.msg_type for m in sent] == ["gui.ambient.weather", "gui.ambient.notifications", "gui.ambient.notifications"]
    assert_conforming_envelope(sent)
    assert [m.data.get("count") for m in sent[1:]] == [3, 0]
    assert {"current_temp", "condition"} <= set(sent[0].data)


def test_stop_intent_interrupts_and_clears(skill):
    skill.runner.time_scale = 1
    skill.handle_show_template(utterance("show_template", template="text"))
    skill.handle_stop_demo(utterance("demo_stop"))
    skill.runner.join()
    sent = skill.bus.gui()
    assert shape(sent) == [VS, (PS, ["SYSTEM_text"]), CL]
    assert_conforming_envelope(sent)


def stop_from_pipeline(skill, message):
    return skill.stop()


def test_stop_method_clears_in_the_stop_message_session(skill):
    skill.runner.time_scale = 1
    skill.handle_show_template(utterance("show_template", template="clock"))
    assert skill.can_stop(utterance("stop")) is True
    assert stop_from_pipeline(skill, utterance("stop")) is True
    sent = skill.bus.gui()
    assert shape(sent) == [VS, (PS, ["SYSTEM_clock"]), CL]
    assert_conforming_envelope(sent)
    assert skill.can_stop(utterance("stop")) is False
