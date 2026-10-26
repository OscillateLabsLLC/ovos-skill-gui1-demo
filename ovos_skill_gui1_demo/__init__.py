"""A skill that shows every OVOS-GUI-1 template and surface through a real intent pipeline."""

import time
from typing import Any

from ovos_bus_client.message import Message, dig_for_message
from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill

from ovos_skill_gui1_demo.faults import FAULTS
from ovos_skill_gui1_demo.producer import Display, OriginBus
from ovos_skill_gui1_demo.runner import DemoRunner, Pause
from ovos_skill_gui1_demo.templates import (
    AMBIENT_WEATHER,
    TEMPLATE_DATA,
    in_system_unit,
    template_for,
    template_in_utterance,
)

SINGLE_HOLD_SECONDS = 20
IDLE_MARGIN_SECONDS = 10
STEP_SECONDS = 4
UPDATE_STEP_SECONDS = 3
AMBIENT_HOLD_SECONDS = 5
MEDIA_POSITION_DELAY_SECONDS = 4
NOTIFICATION_COUNT = 3
PERSISTENT = True


def spoken_name(template: str) -> str:
    return template.removeprefix("SYSTEM_").replace("_", " ")


class GUI1DemoSkill(OVOSSkill):
    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            internet_before_load=False,
            network_before_load=False,
            gui_before_load=False,
            requires_internet=False,
            requires_network=False,
            requires_gui=False,
            no_internet_fallback=True,
            no_network_fallback=True,
            no_gui_fallback=True,
        )

    def __init__(self, *args, **kwargs):
        self.runner = DemoRunner()
        super().__init__(*args, **kwargs)

    def initialize(self):
        self.display = Display(self.gui, OriginBus(self.bus), self.skill_id)

    @intent_handler("show_template.intent")
    def handle_show_template(self, message: Message):
        template = self._requested_template(message)
        if template is None:
            spoken = message.data.get("template") or message.data.get("utterance", "")
            self.log.info(f"gui1-demo: no template for {spoken!r}")
            self.speak_dialog("unknown_template", {"template": spoken})
            return
        self.runner.start(template, lambda origin, pause: self._single(origin, pause, template), message)

    def _requested_template(self, message: Message) -> str | None:
        spoken = message.data.get("template")
        if spoken:
            return template_for(spoken)
        utterance = message.data.get("utterance", "")
        template = template_in_utterance(utterance)
        self.log.warning(
            f"gui1-demo: the pipeline sent no 'template' slot (match_data keys {sorted(message.data)}); "
            f"read {template} from the utterance {utterance!r}"
        )
        return template

    @intent_handler("run_full_demo.intent")
    def handle_full_demo(self, message: Message):
        self.runner.start("full", self._full, message)

    @intent_handler("demo_degradation.intent")
    def handle_degradation_demo(self, message: Message):
        self.runner.start("degradation", self._degradation, message)

    @intent_handler("demo_update.intent")
    def handle_update_demo(self, message: Message):
        self.runner.start("update", self._update_demo, message)

    @intent_handler("demo_ambient.intent")
    def handle_ambient_demo(self, message: Message):
        self.runner.start("ambient", self._ambient_demo, message)

    @intent_handler("demo_stop.intent")
    def handle_stop_demo(self, message: Message):
        self._halt(message)
        self.speak_dialog("stopped")

    def can_stop(self, message: Message) -> bool:
        return self.runner.busy or bool(self.gui.page)

    def stop(self) -> bool:
        return self._halt(dig_for_message())

    def shutdown(self):
        self.runner.cancel()

    def _single(self, message: Message, pause: Pause, template: str) -> None:
        hold = SINGLE_HOLD_SECONDS
        self._show(message, template, TEMPLATE_DATA[template](time.time()), hold + IDLE_MARGIN_SECONDS)
        self._speak(message, "showing", template=spoken_name(template))
        if template == "SYSTEM_media_player":
            if not pause(MEDIA_POSITION_DELAY_SECONDS):
                return
            self._set(message, "media_position", MEDIA_POSITION_DELAY_SECONDS * 1000)
            hold -= MEDIA_POSITION_DELAY_SECONDS
        if pause(hold):
            self._clear(message)

    def _full(self, message: Message, pause: Pause) -> None:
        for template, build in TEMPLATE_DATA.items():
            self._show(message, template, build(time.time()), PERSISTENT)
            self._speak(message, "showing", template=spoken_name(template))
            if not pause(STEP_SECONDS):
                return
        self._finish(message)

    def _degradation(self, message: Message, pause: Pause) -> None:
        for fault in FAULTS:
            self.log.info(f"gui1-demo: fault {fault.label!r}")
            self._show(message, fault.template, fault.data, PERSISTENT)
            self._speak(message, "fault", fault=fault.label)
            if not pause(STEP_SECONDS):
                return
        self._finish(message)

    def _update_demo(self, message: Message, pause: Pause) -> None:
        self._show(message, "SYSTEM_text", {"title": "Update demo", "text": "This text will change."}, PERSISTENT)
        self._speak(message, "update_shown")
        if not pause(UPDATE_STEP_SECONDS):
            return
        self._set(message, "text", "The text changed with one gui.value.set.")
        self._speak(message, "update_text")
        if not pause(UPDATE_STEP_SECONDS):
            return
        self._set(message, "title", None)
        self._speak(message, "update_title")
        if pause(UPDATE_STEP_SECONDS):
            self._finish(message)

    def _ambient_demo(self, message: Message, pause: Pause) -> None:
        self.display.serve(message)
        self.display.clear_if_showing()
        self._ambient(message, "gui.ambient.weather", AMBIENT_WEATHER(time.time()))
        self._ambient(message, "gui.ambient.notifications", {"count": NOTIFICATION_COUNT})
        self._speak(message, "ambient_sent")
        if not pause(AMBIENT_HOLD_SECONDS):
            return
        self._ambient(message, "gui.ambient.notifications", {"count": 0})
        self._speak(message, "ambient_cleared")

    def _show(self, message: Message, template: str, data: dict, idle: bool | int) -> None:
        self.log.info(f"gui1-demo: show {template} keys={sorted(data)} idle={idle}")
        self.display.serve(message)
        self.display.show(template, in_system_unit(data, self.system_unit), idle)

    def _set(self, message: Message, key: str, value: Any) -> None:
        self.log.info(f"gui1-demo: gui.value.set {key}={'null' if value is None else 'value'} on {self.gui.page}")
        self.display.serve(message)
        self.display.update(key, value)

    def _clear(self, message: Message) -> None:
        self.log.info(f"gui1-demo: clear {self.gui.page}")
        self.display.serve(message)
        self.display.clear()

    def _ambient(self, message: Message, topic: str, data: dict) -> None:
        self.log.info(f"gui1-demo: ambient {topic} keys={sorted(data)}")
        self.display.serve(message)
        self.display.ambient(topic, in_system_unit(data, self.system_unit))

    def _finish(self, message: Message) -> None:
        self._clear(message)
        self._speak(message, "finished")

    def _halt(self, message: Message | None) -> bool:
        was_running = self.runner.cancel()
        was_showing = bool(self.gui.page)
        if message is not None:
            self.display.serve(message)
        self.log.info(f"gui1-demo: halt and clear {self.gui.page} (running={was_running}, showing={was_showing})")
        self.display.clear()
        return was_running or was_showing

    def _speak(self, message: Message, dialog: str, **data: str) -> None:
        self.speak_dialog(dialog, data)
