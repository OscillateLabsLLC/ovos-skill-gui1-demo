"""The demo's temperatures follow the device's unit system."""

from ovos_skill_gui1_demo.templates import AMBIENT_WEATHER, in_system_unit


def test_imperial_converts_every_temperature_including_the_forecast():
    data = in_system_unit(AMBIENT_WEATHER(0), "imperial")
    assert (data["current_temp"], data["min_temp"], data["max_temp"]) == (75, 63, 88)
    assert [(day["min_temp"], day["max_temp"]) for day in data["forecast"]] == [(64, 84), (66, 82), (68, 81)]
    assert data["condition_code"] == "clear"


def test_metric_passes_the_payload_through_untouched():
    data = AMBIENT_WEATHER(0)
    assert in_system_unit(data, "metric") is data
    assert data["current_temp"] == 24


def test_a_temperature_that_is_not_a_number_is_left_alone():
    assert in_system_unit({"current_temp": "warm", "condition": "Warm"}, "imperial") == {
        "current_temp": "warm",
        "condition": "Warm",
    }
