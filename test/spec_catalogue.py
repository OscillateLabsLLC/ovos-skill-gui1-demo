"""OVOS-GUI-1 at b6c1583, 3.4: each template's required and optional keys. Copied from the spec, not from the skill."""

CATALOGUE: dict[str, tuple[set[str], set[str]]] = {
    "SYSTEM_loading": (set(), {"label"}),
    "SYSTEM_status": (set(), {"label", "success"}),
    "SYSTEM_error": ({"label"}, {"detail"}),
    "SYSTEM_text": ({"text"}, {"title"}),
    "SYSTEM_image": ({"image"}, {"caption", "title", "fill", "background_color"}),
    "SYSTEM_animated_image": ({"image"}, {"caption", "title", "fill", "background_color"}),
    "SYSTEM_list": (set(), {"title", "items"}),
    "SYSTEM_grid": (set(), {"title", "items"}),
    "SYSTEM_table": ({"columns", "rows"}, {"title"}),
    "SYSTEM_html": ({"html"}, {"resource_url"}),
    "SYSTEM_url": ({"url"}, set()),
    "SYSTEM_audio_player": ({"title"}, {"artist", "album", "image", "position", "duration", "playing"}),
    "SYSTEM_video_player": ({"uri"}, {"title", "playing"}),
    "SYSTEM_media_player": (
        set(),
        {
            "media_title",
            "media_artist",
            "media_album",
            "media_image",
            "media_uri",
            "media_position",
            "media_duration",
            "media_playback_state",
            "media_playlist",
            "media_search_results",
            "media_playlist_position",
        },
    ),
    "SYSTEM_clock": (set(), set()),
    "SYSTEM_timer": ({"end_time"}, {"label", "count_up"}),
    "SYSTEM_weather": ({"current_temp", "condition"}, {"min_temp", "max_temp", "condition_code", "icon", "location", "forecast"}),
    "SYSTEM_map": ({"latitude", "longitude"}, {"zoom", "label"}),
    "SYSTEM_face": (set(), {"sleeping"}),
}

ITEM_KEYS = {
    "SYSTEM_list": {"title", "subtitle", "image"},
    "SYSTEM_grid": {"image", "title"},
}
MEDIA_PLAYLIST_KEYS = {"title", "artist", "image", "uri", "duration"}
MEDIA_SEARCH_KEYS = {"title", "artist", "image", "uri", "skill_id", "match_confidence"}
FORECAST_KEYS = {"time", "min_temp", "max_temp", "condition_code"}
CONDITION_CODES = {"clear", "partly_cloudy", "cloudy", "fog", "drizzle", "rain", "snow", "sleet", "thunder", "wind"}
FORBIDDEN_TEMPLATES = {"SYSTEM_idle", "SYSTEM_confirm", "SYSTEM_select"}
IMAGE_KEYS = {"image", "icon", "media_image"}

SPOKEN_WORDS = [
    "text",
    "image",
    "animated image",
    "list",
    "grid",
    "table",
    "html",
    "url",
    "error",
    "status",
    "loading",
    "clock",
    "timer",
    "weather",
    "map",
    "face",
    "audio player",
    "video player",
    "media player",
]
