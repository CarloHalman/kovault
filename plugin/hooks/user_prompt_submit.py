#!/usr/bin/env python3
"""UserPromptSubmit hook.

When update mode = auto, inject a short harvest reminder as quiet additionalContext before
Claude answers the new prompt — so it saves this turn's new decisions/tasks/facts to the vault
as part of answering, not via a Stop hook that blocks after the answer already showed. A
decision reached in plain chat (no tool call) still gets saved: the nudge fires on every
message, not only after tool use. Stdlib only.
"""
import json
import sys
from pathlib import Path

CONFIG = Path.home() / ".kovault" / "config.json"

REMINDER = ("Kovault auto: save this turn's new decisions/tasks/facts to the vault (lookup first, "
            "fetch before editing). One line per write: <action> - <title> <table>.")


def main() -> None:
    try:
        json.load(sys.stdin)                       # consume hook input (unused)
    except Exception:
        pass
    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        cfg = {}
    if cfg.get("update_mode") != "auto":
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": REMINDER,
        }
    }))


if __name__ == "__main__":
    main()
