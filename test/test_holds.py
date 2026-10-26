"""The full demo holds longer on the steps that have more to show."""

from ovos_skill_gui1_demo import HOLD_SECONDS, STEP_SECONDS
from ovos_skill_gui1_demo.templates import LONG_TEXT, TEMPLATE_DATA


def test_the_text_template_sends_enough_words_to_page():
    assert len(LONG_TEXT.split()) >= 120
    assert TEMPLATE_DATA["SYSTEM_text"](0)["text"] is LONG_TEXT


def test_the_long_holds_cover_the_paging_and_the_media_views():
    assert HOLD_SECONDS["SYSTEM_text"] >= 20, "two page turns at 10 s a page"
    assert HOLD_SECONDS["SYSTEM_media_player"] > STEP_SECONDS
    assert set(HOLD_SECONDS) <= set(TEMPLATE_DATA)
