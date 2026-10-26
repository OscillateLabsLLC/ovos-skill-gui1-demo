# ovos-skill-gui1-demo

An OVOS skill that shows every [OVOS-GUI-1](https://github.com/OpenVoiceOS/architecture/blob/b6c1583/gui-1.md) template and every other GUI-1 surface.
Use it to drive a render backend (for example Visage) through a real intent pipeline, to test conformance, and to record wire fixtures.

The skill is a conforming GUI-1 producer ([8.1](https://github.com/OpenVoiceOS/architecture/blob/b6c1583/gui-1.md#81-a-conforming-producer-application-side-interface-must), [8.2](https://github.com/OpenVoiceOS/architecture/blob/b6c1583/gui-1.md#82-a-conforming-producer-should)).
There are two exceptions, and both are deliberate:

- The degradation demo breaks producer rules on purpose.
- The media player demo sends `SYSTEM_media_player`, which only the media subsystem may send. The demo keeps it because no media subsystem on the test stack sends it, and a backend still needs a live source for that template.

## Install

The skill needs `ovos-workshop` and `ovos-bus-client`. The command below installs it into the isolated GUI-1 venv:

```bash
just install          # uv pip install --python ~/.venvs/ovos-gui1/bin/python --no-deps -e .
```

Restart the skills service after you install. ovos-core does not import a package that was installed after it started.

Skill id: `ovos-skill-gui1-demo.oscillatelabs`. Entry point group: `opm.skill`.

## Utterances

| Say | The skill does this |
|---|---|
| "show me the {template} demo", "demo the {template} template", "gui demo {template}" | Shows that one template with data in every key of the catalogue, says "Here is the {template} template.", waits 20 s, then clears the namespace. |
| "run the gui demo", "show every template" | Shows all 19 templates in catalogue order, 4 s each, except the text template (24 s, so its pages turn) and the media player (20 s, so its three views can be tapped through), then clears the namespace. |
| "show the broken gui demo" | Sends six faulty requests, 4 s each, then clears. Each `title` names its fault. |
| "show the gui update demo" | Shows `SYSTEM_text`. After 3 s it changes `text`. After 3 s more it removes `title` with an explicit `null`. After 3 s more it clears. |
| "show the ambient demo" | Sends `gui.ambient.weather` and `gui.ambient.notifications` with `count` 3. After 5 s it sends `count` 0. It shows no template. |
| "stop the gui demo", or "stop" | Stops the running demo and clears the namespace. |

The `{template}` words are: text, image, animated image, list, grid, table, html, url, error, status, loading, clock, timer, weather, map, face, audio player, video player, media player.

Data details:

- Images are photographs from Wikimedia Commons, fetched by file name through `Special:FilePath` and scaled server-side (`templates.py`, `photo`), so the demo needs the network; `SYSTEM_animated_image` is the turning-Earth GIF. The weather `icon` is the Tango clear-sky icon, an SVG that Commons renders to PNG. The in-memory image makers (`images.py`) stay for the degradation demo and tests. No image is a file path ([3.5](https://github.com/OpenVoiceOS/architecture/blob/b6c1583/gui-1.md#35-image-delivery)).
- The text demo sends about 160 words, so a display that pages long text shows it turning: on Visage that is five pages at 432 × 736, one every 10 s.
- The weather demo sends `condition_code` and a forecast of three entries.
- The timer demo sends an `end_time` 120 s after the request.
- The media player demo sends a playlist and search results. After 4 s it sends `media_position` 4000 in a new `gui.value.set`.

Degradation faults, in order:

1. `SYSTEM_text` without its required `text`.
2. `SYSTEM_weather` with `current_temp` as a string.
3. `SYSTEM_image` with a bare file path as `image`.
4. `SYSTEM_table` with a row that is shorter than `columns`.
5. `SYSTEM_weather` with the unlisted `condition_code` `volcanic_ash`.
6. The unknown template `SYSTEM_hologram`.

## How the skill sends GUI messages

The skill uses `self.gui`, the `GUIInterface` from ovos-workshop. It calls `show_page` with spec template names, not the legacy helper names.
It sets all keys before `show_page`, so each template is one `gui.value.set` and one `gui.page.show`.
Before it shows a different template, it clears the namespace. This removes the keys of the previous template.

Two things `GUIInterface` cannot do. The skill adds them:

1. `GUIInterface` sends each message without a context. The bus client then puts its own `default` session on the message.
   The skill gives `GUIInterface` a bus proxy (`OriginBus`) that copies the context of the utterance onto each GUI message.
   The skill does not set `session_id` itself.
2. `GUIInterface` has no call for the ambient topics. The skill emits `gui.ambient.weather` and `gui.ambient.notifications` on the bus. They carry `__from`.

The skill speaks with `speak_dialog`. Demos run on a worker thread, and the worker keeps the utterance message as an argument, so speech also keeps the session.

If the intent pipeline gives no `template` slot, the skill finds the template word in the utterance and logs a WARNING.
Switchboard 1.1.0 gives no slots to skills that are not in its canonical schema. This skill is not in it.

## Test and lint

```bash
just test             # pytest with FakeBus: the exact GUI message sequence per intent, catalogue coverage, image rules
just lint             # ruff, line length 130
```

`test/test_guiinterface_findings.py` records what `GUIInterface` sends without the skill's help. If one of those tests fails, `GUIInterface` changed.

## Record fixtures

Start the isolated stack (`gui1-upstream/stack/run_stack.sh` and `run_skills.sh`) with this skill installed. Then:

```bash
scripts/record.sh weather 24 "show me the weather demo"
```

The script connects the Visage adapter's `tool/dump_client.py` to `ws://127.0.0.1:28182/gui1` as one more GUI-1 client. It sends the utterance with the stack's `say.py`.
It writes the frames that a client receives to `fixtures/gui1/weather.jsonl`. The welcome frame and the first snapshot are removed. The first line is a `_note`.
The Visage adapter's `tool/replay_server.py` can replay the file.

Environment overrides: `GUI1_STACK`, `VISAGE_ADAPTER`, `GUI1_PYTHON`, `GUI1_URL`.

## License

Apache-2.0. Copyright 2026 OscillateLabs LLC.
