"""Deliberately broken template requests, one fault each, so a backend's degradation (OVOS-GUI-1 6.5) is visible.

These break producer MUSTs on purpose (3.3, 3.4, 3.5, 8.1). Only the degradation demo sends them.
"""

from dataclasses import dataclass

BARE_PATH_IMAGE = "/usr/share/pixmaps/gui1-demo.png"
UNLISTED_CONDITION_CODE = "volcanic_ash"
UNKNOWN_TEMPLATE = "SYSTEM_hologram"


@dataclass(frozen=True)
class Fault:
    label: str
    template: str
    data: dict


FAULTS: tuple[Fault, ...] = (
    Fault("missing required key text", "SYSTEM_text", {"title": "Fault: missing required key text"}),
    Fault(
        "wrong type: current_temp is a string",
        "SYSTEM_weather",
        {"title": "Fault: current_temp is a string", "current_temp": "seventy two", "condition": "Sunny"},
    ),
    Fault("bare file path as image", "SYSTEM_image", {"title": "Fault: bare file path as image", "image": BARE_PATH_IMAGE}),
    Fault(
        "table row of the wrong length",
        "SYSTEM_table",
        {
            "title": "Fault: table row of the wrong length",
            "columns": ["Route", "Stop", "Minutes"],
            "rows": [["2", "Main Plaza", 4], ["36", "Pearl"]],
        },
    ),
    Fault(
        "unlisted condition_code",
        "SYSTEM_weather",
        {
            "title": "Fault: unlisted condition_code",
            "current_temp": 24,
            "condition": "Ash cloud",
            "condition_code": UNLISTED_CONDITION_CODE,
        },
    ),
    Fault("unknown template SYSTEM_hologram", UNKNOWN_TEMPLATE, {"title": "Fault: unknown template SYSTEM_hologram"}),
)
