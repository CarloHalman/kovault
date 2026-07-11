#!/usr/bin/env python3
"""SessionStart hook.

Checks the MCP endpoint is reachable and injects the local config (username/nickname +
update mode) and the Kovault CLAUDE.md into context, before the model does any work. Stdlib
only — runs in the user's environment (Windows/macOS/Linux).
"""
import json
import socket
import sys
from pathlib import Path
from urllib.parse import urlparse

CONFIG = Path.home() / ".kovault" / "config.json"


def load_config() -> dict:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return {}


def reachable(endpoint: str) -> bool:
    try:
        u = urlparse(endpoint)
        port = u.port or (443 if u.scheme == "https" else 80)
        with socket.create_connection((u.hostname, port), timeout=2):
            return True
    except Exception:
        return False


def main() -> None:
    try:
        json.load(sys.stdin)                       # consume hook input (unused)
    except Exception:
        pass
    cfg = load_config()
    lines: list[str] = []
    if not cfg:
        lines.append("Kovault: no local config found. Run /setup-kovault to connect to your backend.")
    else:
        nick = cfg.get("nickname") or cfg.get("username") or "the user"
        lines.append(f"Kovault connected as '{cfg.get('username', '?')}'. Address the user as {nick}.")
        lines.append(f"Update mode: {cfg.get('update_mode', 'manual')}.")
        endpoint = cfg.get("endpoint")
        if endpoint and not reachable(endpoint):
            lines.append(f"WARNING: Kovault MCP endpoint {endpoint} is not reachable — check the server.")
        vault_path = cfg.get("vault_path")
        if vault_path:
            claude_md = Path(vault_path) / "CLAUDE.md"
            if claude_md.is_file():
                lines.append("\n--- Kovault CLAUDE.md ---\n" + claude_md.read_text(encoding="utf-8"))
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    }))


if __name__ == "__main__":
    main()
