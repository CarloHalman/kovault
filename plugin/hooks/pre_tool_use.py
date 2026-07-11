#!/usr/bin/env python3
"""PreToolUse hook. When local `debug` is on, stamp the start time of a
Kovault tool call so PostToolUse can compute its latency. Matched to `mcp__kovault__.*` in hooks.json.
Stdlib only; never blocks the turn (always exits 0)."""
import json
import sys
import tempfile
import time
from pathlib import Path

CONFIG = Path.home() / ".kovault" / "config.json"


def main() -> None:
    try:
        data = json.load(sys.stdin)
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return
    debug = bool(cfg.get("debug"))
    # gate the raw `sql` tool on debug mode (block it with a message when debug is off)
    if (data.get("tool_name") or "").endswith("__sql") and not debug:
        print("The Kovault `sql` tool is debug-only. Enable debug in /settings-kovault to use it.", file=sys.stderr)
        raise SystemExit(2)
    if not debug:
        return
    tuid = data.get("tool_use_id")
    if not tuid:
        return
    try:
        (Path(tempfile.gettempdir()) / f"kovault-debug-{tuid}").write_text(
            str(time.time()), encoding="utf-8")
    except Exception:
        pass


if __name__ == "__main__":
    main()
