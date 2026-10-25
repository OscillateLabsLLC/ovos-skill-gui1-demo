"""Turn a dump_client.py capture into a replayable fixture: drop the handshake, keep the stream frames.

python trim_frames.py RAW.jsonl OUT.jsonl "utterances that produced it"
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HANDSHAKE_TYPES = {"welcome"}


def stream_frames(lines: list[str]) -> list[dict]:
    frames = [json.loads(line) for line in lines if line.strip()]
    stream = [f for f in frames if f.get("type") not in HANDSHAKE_TYPES]
    if stream and stream[0].get("type") == "snapshot":
        stream = stream[1:]
    return stream


def main(raw: str, out: str, utterances: str) -> None:
    frames = stream_frames(Path(raw).read_text().splitlines())
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    note = {
        "_note": f"recorded {stamp} by ovos-gui-plugin-visage tool/dump_client.py (client-side wire frames) "
        f"while ovos-skill-gui1-demo served: {utterances}"
    }
    Path(out).write_text("".join(json.dumps(f) + "\n" for f in [note, *frames]))
    print(f"{out}: {len(frames)} frames, types {sorted({f['type'] for f in frames})}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
