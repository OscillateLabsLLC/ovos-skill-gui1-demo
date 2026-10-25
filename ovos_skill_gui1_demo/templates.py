"""Realistic session data for every OVOS-GUI-1 catalogue template, every key filled (3.4)."""

from collections.abc import Callable

from ovos_skill_gui1_demo.images import animated_gif, png

TIMER_SECONDS = 120
HOUR = 3600
DAY = 24 * HOUR
BLUE, GOLD, RED, INK, GREEN, SKY = (20, 90, 160), (240, 200, 40), (200, 40, 60), (30, 30, 30), (40, 150, 90), (120, 180, 230)
VIDEO_URI = "https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4"
AUDIO_URI = "https://upload.wikimedia.org/wikipedia/commons/c/c8/Example.ogg"

DataBuilder = Callable[[float], dict]


def _image(now: float) -> dict:
    return {
        "image": png(BLUE, GOLD),
        "caption": "Stripes drawn in memory",
        "title": "SYSTEM_image",
        "fill": "fit",
        "background_color": "#101820",
    }


def _animated_image(now: float) -> dict:
    return {
        "image": animated_gif(RED, INK),
        "caption": "Two frames, looping",
        "title": "SYSTEM_animated_image",
        "fill": "crop",
        "background_color": "#000000",
    }


def _list(now: float) -> dict:
    items = [
        {"title": "Milk", "subtitle": "Two litres", "image": png(SKY, INK)},
        {"title": "Bread", "subtitle": "Sourdough", "image": png(GOLD, INK)},
        {"title": "Coffee", "subtitle": "Whole bean", "image": png(INK, GOLD)},
    ]
    return {"title": "Shopping list", "items": items}


def _grid(now: float) -> dict:
    colours = [("Blue", BLUE), ("Gold", GOLD), ("Red", RED), ("Green", GREEN)]
    return {"title": "Colour swatches", "items": [{"image": png(c, INK), "title": name} for name, c in colours]}


def _table(now: float) -> dict:
    return {
        "title": "Next departures",
        "columns": ["Route", "Stop", "Minutes"],
        "rows": [["2", "Main Plaza", 4], ["36", "Pearl", 11], ["100", "Airport", 23]],
    }


def _html(now: float) -> dict:
    html = "<h1>SYSTEM_html</h1><p>Discouraged escape hatch (3.6). <b>Bold</b> and <i>italic</i>.</p>"
    return {"html": html, "resource_url": "https://openvoiceos.org/"}


def _timer(now: float) -> dict:
    return {"end_time": int(now) + TIMER_SECONDS, "label": "Tea", "count_up": False}


def _forecast(now: float) -> list[dict]:
    start = int(now // DAY) * DAY
    codes = ["partly_cloudy", "rain", "thunder"]
    return [
        {"time": start + (i + 1) * DAY, "min_temp": 18 + i, "max_temp": 29 - i, "condition_code": code}
        for i, code in enumerate(codes)
    ]


def _weather(now: float) -> dict:
    return {
        "current_temp": 24,
        "min_temp": 17,
        "max_temp": 31,
        "condition": "Clear and sunny",
        "condition_code": "clear",
        "icon": png(GOLD, SKY),
        "location": "San Antonio",
        "forecast": _forecast(now),
    }


def _audio_player(now: float) -> dict:
    return {
        "title": "Example Ogg",
        "artist": "Wikimedia Commons",
        "album": "Sample Sounds",
        "image": png(RED, GOLD),
        "position": 42000,
        "duration": 187000,
        "playing": True,
    }


def _playlist() -> list[dict]:
    return [
        {
            "title": "Big Buck Bunny",
            "artist": "Blender Foundation",
            "image": png(GREEN, GOLD),
            "uri": VIDEO_URI,
            "duration": 596000,
        },
        {"title": "Example Ogg", "artist": "Wikimedia Commons", "image": png(RED, GOLD), "uri": AUDIO_URI, "duration": 187000},
        {
            "title": "Live stream",
            "artist": "Demo Radio",
            "image": png(BLUE, SKY),
            "uri": "https://example.org/live",
            "duration": -1,
        },
    ]


def _search_results() -> list[dict]:
    return [
        {
            "title": "Big Buck Bunny",
            "artist": "Blender Foundation",
            "image": png(GREEN, GOLD),
            "uri": VIDEO_URI,
            "skill_id": "ovos-skill-gui1-demo.oscillatelabs",
            "match_confidence": 92,
        },
        {
            "title": "Elephants Dream",
            "artist": "Blender Foundation",
            "image": png(INK, SKY),
            "uri": "https://download.blender.org/ED/ED_1024.avi",
            "skill_id": "ovos-skill-gui1-demo.oscillatelabs",
            "match_confidence": 71,
        },
    ]


def _media_player(now: float) -> dict:
    return {
        "media_title": "Big Buck Bunny",
        "media_artist": "Blender Foundation",
        "media_album": "Open Movies",
        "media_image": png(GREEN, GOLD),
        "media_uri": VIDEO_URI,
        "media_position": 0,
        "media_duration": 596000,
        "media_playback_state": "playing",
        "media_playlist": _playlist(),
        "media_search_results": _search_results(),
        "media_playlist_position": 0,
    }


TEMPLATE_DATA: dict[str, DataBuilder] = {
    "SYSTEM_loading": lambda now: {"label": "Fetching the forecast"},
    "SYSTEM_status": lambda now: {"label": "Lights turned off", "success": True},
    "SYSTEM_error": lambda now: {"label": "Could not reach the server", "detail": "Timed out after 10 seconds"},
    "SYSTEM_text": lambda now: {"text": "GUI-1 text template. It scrolls when the text is long. " * 4, "title": "SYSTEM_text"},
    "SYSTEM_image": _image,
    "SYSTEM_animated_image": _animated_image,
    "SYSTEM_list": _list,
    "SYSTEM_grid": _grid,
    "SYSTEM_table": _table,
    "SYSTEM_html": _html,
    "SYSTEM_url": lambda now: {"url": "https://openvoiceos.org/"},
    "SYSTEM_audio_player": _audio_player,
    "SYSTEM_video_player": lambda now: {"uri": VIDEO_URI, "title": "Big Buck Bunny", "playing": True},
    "SYSTEM_media_player": _media_player,
    "SYSTEM_clock": lambda now: {},
    "SYSTEM_timer": _timer,
    "SYSTEM_weather": _weather,
    "SYSTEM_map": lambda now: {"latitude": 29.4241, "longitude": -98.4936, "zoom": 12, "label": "San Antonio"},
    "SYSTEM_face": lambda now: {"sleeping": False},
}

SPOKEN_NAMES: dict[str, str] = {name.removeprefix("SYSTEM_").replace("_", " "): name for name in TEMPLATE_DATA}

AMBIENT_WEATHER = _weather


def template_for(spoken: str) -> str | None:
    """Map the spoken slot ("audio player", "the weather") to its template name."""
    words = spoken.lower().strip().removeprefix("the ").removesuffix(" template").strip()
    return SPOKEN_NAMES.get(words)


def template_in_utterance(utterance: str) -> str | None:
    """The template whose spoken name appears in the whole utterance, longest name first ("animated image")."""
    text = f" {utterance.lower()} "
    for name in sorted(SPOKEN_NAMES, key=len, reverse=True):
        if f" {name} " in text:
            return SPOKEN_NAMES[name]
    return None
