#!/usr/bin/env python3
"""Stop hook.

When update mode = auto, inject the harvest instruction at end of turn so the model runs the
/update flow for the turn's changes. Guards against looping via `stop_hook_active` (set by
Claude Code when the turn is already continuing from a Stop hook). Stdlib only.
"""
import json
import sys
from pathlib import Path

CONFIG = Path.home() / ".kovault" / "config.json"


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    if data.get("stop_hook_active"):               # already harvesting — let it stop
        return
    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        cfg = {}
    if cfg.get("update_mode") != "auto":
        return
    reason = (
        "Auto-harvest (Kovault update mode = auto): review THIS turn's conversation for new or "
        "changed knowledge, decisions, tasks, or sources. Write anything worth keeping to the "
        "Kovault now via the Kovault MCP insert/update tools (the /update-kovault flow) — lookup first to "
        "avoid duplicates, fetch before editing. If nothing is worth saving, stop."
    )
    print(json.dumps({"decision": "block", "reason": reason}))


if __name__ == "__main__":
    main()
