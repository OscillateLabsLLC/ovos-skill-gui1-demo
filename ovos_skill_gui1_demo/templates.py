"""Realistic session data for every OVOS-GUI-1 catalogue template, every key filled (3.4)."""

from collections.abc import Callable

TIMER_SECONDS = 120
HOUR = 3600
DAY = 24 * HOUR
VIDEO_URI = "https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4"
AUDIO_URI = "https://upload.wikimedia.org/wikipedia/commons/c/c8/Example.ogg"
COMMONS_FILE = "https://commons.wikimedia.org/wiki/Special:FilePath/"


def photo(name: str, width: int | None = 320) -> str:
    """A Wikimedia Commons image by file name, scaled server-side; ``width=None`` is the original (an animated GIF).

    Real photographs, so the demo shows pictures and not the striped stand-ins the skill draws in memory (``images.py``,
    still used where no photo fits). Needs the network; a backend shows its image fallback without it.
    """
    return f"{COMMONS_FILE}{name}" if width is None else f"{COMMONS_FILE}{name}?width={width}"


WATERFALL = photo("Hopetoun_falls.jpg", 640)
EARTH = photo("Rotating_earth_(large).gif", None)
MILK, BREAD, COFFEE = photo("Glass_of_milk.jpg", 160), photo("Sourdough_bread.jpg", 160), photo("Roasted_coffee_beans.jpg", 160)
APPLE, SUNFLOWER, CAT, LION = (
    photo("Red_Apple.jpg"),
    photo("Sunflower_from_Silesia2.jpg"),
    photo("Cat03.jpg"),
    photo("Lion_waiting_in_Namibia.jpg"),
)
FLOWER = photo("JPEG_example_flower.jpg")
SUN_ICON = photo("Weather-clear.svg", 240)

DataBuilder = Callable[[float], dict]


def _image(now: float) -> dict:
    return {
        "image": WATERFALL,
        "caption": "Hopetoun Falls, Victoria (Wikimedia Commons)",
        "title": "SYSTEM_image",
        "fill": "fit",
        "background_color": "#101820",
    }


def _animated_image(now: float) -> dict:
    return {
        "image": EARTH,
        "caption": "A turning Earth (Wikimedia Commons)",
        "title": "SYSTEM_animated_image",
        "fill": "crop",
        "background_color": "#000000",
    }


def _list(now: float) -> dict:
    items = [
        {"title": "Milk", "subtitle": "Two litres", "image": MILK},
        {"title": "Bread", "subtitle": "Sourdough", "image": BREAD},
        {"title": "Coffee", "subtitle": "Whole bean", "image": COFFEE},
    ]
    return {"title": "Shopping list", "items": items}


def _grid(now: float) -> dict:
    photos = [("Apple", APPLE), ("Sunflower", SUNFLOWER), ("Cat", CAT), ("Lion", LION)]
    return {"title": "Photo grid", "items": [{"image": image, "title": name} for name, image in photos]}


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
        "icon": SUN_ICON,
        "location": "San Antonio",
        "forecast": _forecast(now),
    }


def _audio_player(now: float) -> dict:
    return {
        "title": "Example Ogg",
        "artist": "Wikimedia Commons",
        "album": "Sample Sounds",
        "image": FLOWER,
        "position": 42000,
        "duration": 187000,
        "playing": True,
    }


def _playlist() -> list[dict]:
    return [
        {
            "title": "Big Buck Bunny",
            "artist": "Blender Foundation",
            "image": SUNFLOWER,
            "uri": VIDEO_URI,
            "duration": 596000,
        },
        {"title": "Example Ogg", "artist": "Wikimedia Commons", "image": FLOWER, "uri": AUDIO_URI, "duration": 187000},
        {
            "title": "Live stream",
            "artist": "Demo Radio",
            "image": WATERFALL,
            "uri": "https://example.org/live",
            "duration": -1,
        },
    ]


def _search_results() -> list[dict]:
    return [
        {
            "title": "Big Buck Bunny",
            "artist": "Blender Foundation",
            "image": SUNFLOWER,
            "uri": VIDEO_URI,
            "skill_id": "ovos-skill-gui1-demo.oscillatelabs",
            "match_confidence": 0.92,
        },
        {
            "title": "Elephants Dream",
            "artist": "Blender Foundation",
            "image": LION,
            "uri": "https://download.blender.org/ED/ED_1024.avi",
            "skill_id": "ovos-skill-gui1-demo.oscillatelabs",
            "match_confidence": 0.71,
        },
    ]


def _media_player(now: float) -> dict:
    return {
        "media_title": "Big Buck Bunny",
        "media_artist": "Blender Foundation",
        "media_album": "Open Movies",
        "media_image": SUNFLOWER,
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

TEMPERATURE_KEYS = ("current_temp", "min_temp", "max_temp")


def fahrenheit(celsius: float) -> int:
    return round(celsius * 9 / 5 + 32)


def in_system_unit(data: dict, system_unit: str) -> dict:
    """The payload with its Celsius temperatures converted when the device is imperial; any other unit passes through.

    ``SYSTEM_weather`` has no unit key (gui-1.md 3.4), so the numbers are in whatever unit the device is set to, and
    the demo's figures are written in Celsius. The forecast entries convert the same way.
    """
    if system_unit != "imperial":
        return data
    out = {k: fahrenheit(v) if k in TEMPERATURE_KEYS and isinstance(v, (int, float)) else v for k, v in data.items()}
    if isinstance(out.get("forecast"), list):
        out["forecast"] = [in_system_unit(day, system_unit) for day in out["forecast"]]
    return out


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
