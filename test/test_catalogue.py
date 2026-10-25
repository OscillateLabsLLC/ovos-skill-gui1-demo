"""The skill's data against the spec's catalogue (3.4), typing rules (3.3) and image delivery (3.5)."""

import time
from pathlib import Path

import pytest
from spec_catalogue import (
    CATALOGUE,
    CONDITION_CODES,
    FORBIDDEN_TEMPLATES,
    FORECAST_KEYS,
    IMAGE_KEYS,
    ITEM_KEYS,
    MEDIA_PLAYLIST_KEYS,
    MEDIA_SEARCH_KEYS,
    SPOKEN_WORDS,
)

from ovos_skill_gui1_demo.faults import BARE_PATH_IMAGE, FAULTS
from ovos_skill_gui1_demo.templates import TEMPLATE_DATA, template_for

LOCALE = Path(__file__).parent.parent / "ovos_skill_gui1_demo" / "locale" / "en-us"
MAX_INTENT_LINES = 12
NOW = time.time()


def image_values(value):
    if isinstance(value, dict):
        for key, inner in value.items():
            if key in IMAGE_KEYS:
                yield inner
            yield from image_values(inner)
    elif isinstance(value, list):
        for inner in value:
            yield from image_values(inner)


def test_every_catalogue_template_has_demo_data():
    assert set(TEMPLATE_DATA) == set(CATALOGUE)
    assert not FORBIDDEN_TEMPLATES & set(TEMPLATE_DATA)


@pytest.mark.parametrize("word", SPOKEN_WORDS)
def test_every_spoken_word_reaches_its_template(word):
    assert template_for(word) == "SYSTEM_" + word.replace(" ", "_")
    assert template_for(f"the {word}") == template_for(word)


@pytest.mark.parametrize("template", sorted(CATALOGUE))
def test_demo_data_fills_every_key_and_no_other(template):
    required, optional = CATALOGUE[template]
    assert set(TEMPLATE_DATA[template](NOW)) == required | optional


@pytest.mark.parametrize("template", sorted(ITEM_KEYS))
def test_list_and_grid_items_carry_every_item_key(template):
    for item in TEMPLATE_DATA[template](NOW)["items"]:
        assert set(item) == ITEM_KEYS[template]


def test_media_player_nested_entries_carry_every_key():
    data = TEMPLATE_DATA["SYSTEM_media_player"](NOW)
    assert all(set(entry) == MEDIA_PLAYLIST_KEYS for entry in data["media_playlist"])
    assert all(set(entry) == MEDIA_SEARCH_KEYS for entry in data["media_search_results"])
    assert data["media_playback_state"] in {"playing", "paused", "stopped", "loading", "error"}


def test_weather_uses_listed_condition_codes_and_three_forecast_entries():
    data = TEMPLATE_DATA["SYSTEM_weather"](NOW)
    forecast = data["forecast"]
    assert data["condition_code"] in CONDITION_CODES
    assert len(forecast) == 3 and all(set(entry) == FORECAST_KEYS for entry in forecast)
    assert {entry["condition_code"] for entry in forecast} <= CONDITION_CODES
    assert [entry["time"] for entry in forecast] == sorted(entry["time"] for entry in forecast)


def test_timer_ends_two_minutes_out():
    assert TEMPLATE_DATA["SYSTEM_timer"](NOW)["end_time"] - NOW == pytest.approx(120, abs=1)


def test_table_rows_match_columns():
    data = TEMPLATE_DATA["SYSTEM_table"](NOW)
    assert all(len(row) == len(data["columns"]) for row in data["rows"])


@pytest.mark.parametrize("template", sorted(CATALOGUE))
def test_no_image_key_holds_a_path(template):
    for value in image_values(TEMPLATE_DATA[template](NOW)):
        assert value.startswith(("data:", "https://", "http://")), value[:40]


def test_only_the_labelled_fault_carries_a_path():
    paths = [f.label for f in FAULTS for v in image_values(f.data) if not v.startswith(("data:", "http"))]
    assert paths == ["bare file path as image"]
    assert BARE_PATH_IMAGE.startswith("/")


def test_every_fault_is_labelled_in_its_title():
    assert all(f.data["title"].startswith("Fault: ") for f in FAULTS)
    assert len({f.data["title"] for f in FAULTS}) == len(FAULTS)


@pytest.mark.parametrize("path", sorted(LOCALE.glob("intents/*.intent")), ids=lambda p: p.name)
def test_intent_files_stay_small(path):
    assert len(path.read_text().splitlines()) < MAX_INTENT_LINES
