#!/usr/bin/env bash
# Record the GUI-1 wire frames that a render client receives while one utterance runs.
#
#   scripts/record.sh NAME WAIT_SECONDS "utterance" ["utterance" ...]
#
# Connects the Visage adapter's tool/dump_client.py to the adapter's GUI-1 endpoint as a second client,
# sends each utterance with the stack's say.py, then writes fixtures/gui1/NAME.jsonl (stream frames only;
# the welcome and the first snapshot are dropped, a _note line says where the frames came from).
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STACK="${GUI1_STACK:-$HOME/coding/OscillateLabs/gui1-upstream/stack}"
ADAPTER="${VISAGE_ADAPTER:-$HOME/coding/OscillateLabs/ovos-gui-plugin-visage}"
PY="${GUI1_PYTHON:-$HOME/.venvs/ovos-gui1/bin/python}"
URL="${GUI1_URL:-ws://127.0.0.1:28182/gui1}"
CONNECT_SECONDS=1

name="$1" wait_seconds="$2"
shift 2
raw="$(mktemp -t "gui1-$name")"
"$PY" "$ADAPTER/tool/dump_client.py" "$URL" >"$raw" &
dump_pid=$!
trap 'kill "$dump_pid" 2>/dev/null || true; rm -f "$raw"' EXIT
sleep "$CONNECT_SECONDS"
XDG_CONFIG_HOME="$STACK/config" "$PY" "$STACK/say.py" --wait "$wait_seconds" "$@"
kill "$dump_pid"
wait "$dump_pid" 2>/dev/null || true
"$PY" "$REPO/scripts/trim_frames.py" "$raw" "$REPO/fixtures/gui1/$name.jsonl" "$*"
