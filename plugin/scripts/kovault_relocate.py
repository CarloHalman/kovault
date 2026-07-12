#!/usr/bin/env python3
"""Relocate the local Kovault folder. No AI, no hand-written SQL.

  python kovault_relocate.py -new  /path/to/new     scaffold a FRESH Kovault folder there, leave the
                                                 old folder and the DB untouched, just repoint
                                                 config.vault_path. Old source references keep
                                                 pointing at the old folder (which still exists).

  python kovault_relocate.py -move /path/to/new     MOVE the current Kovault folder to the new path AND
                                                 rewrite the DB source references that lived under
                                                 it, then repoint config.vault_path.

Reads ~/.kovault/config.json for `endpoint` and `vault_path`. The only DB change (only for -move) is a
source-reference prefix rewrite, done through the MCP server's /relocate-sources route (the sole
component with DB access) so this script never needs DB credentials.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import urllib.request
from pathlib import Path

CONFIG = Path.home() / ".kovault" / "config.json"
# CLAUDE.md / AGENTS.md template fallbacks (used only if the current Kovault folder lacks them).
TEMPLATE_DIRS = [
    Path(__file__).resolve().parent.parent / "templates",   # plugin/templates/
]


def load_config() -> dict:
    if not CONFIG.exists():
        sys.exit(f"no config at {CONFIG}; run /kovault:setup first")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def save_config(cfg: dict) -> None:
    CONFIG.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def _find_template(name: str, prefer: Path | None) -> Path | None:
    for d in ([prefer] if prefer else []) + TEMPLATE_DIRS:
        if d and (d / name).exists():
            return d / name
    return None


def scaffold(path: Path, rules_from: Path | None) -> None:
    """Create _inbox/ and sources/, and copy CLAUDE.md/AGENTS.md (from the current Kovault folder
    when possible, else a bundled template)."""
    (path / "_inbox").mkdir(parents=True, exist_ok=True)
    (path / "sources").mkdir(parents=True, exist_ok=True)
    for name in ("CLAUDE.md", "AGENTS.md"):
        src = _find_template(name, rules_from)
        if src:
            shutil.copyfile(src, path / name)
        else:
            print(f"note: no {name} template found; copy it into {path} yourself", file=sys.stderr)


def base_url(endpoint: str) -> str:
    e = (endpoint or "").rstrip("/")
    return e[:-4] if e.endswith("/mcp") else e


def rewrite_refs(endpoint: str, old_prefix: str, new_prefix: str, user: str | None) -> dict:
    payload = json.dumps({"old_prefix": old_prefix, "new_prefix": new_prefix}).encode()
    req = urllib.request.Request(
        base_url(endpoint) + "/relocate-sources", data=payload,
        headers={"Content-Type": "application/json", "X-Kovault-User": user or "script"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main() -> None:
    ap = argparse.ArgumentParser(description="Relocate the local Kovault folder (-new or -move).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("-new", dest="new", metavar="PATH", help="scaffold a fresh folder here; old + DB untouched")
    g.add_argument("-move", dest="move", metavar="PATH", help="move the folder here and rewrite DB source refs")
    args = ap.parse_args()

    cfg = load_config()
    old = Path(cfg.get("vault_path", "")).expanduser()
    target = Path(args.new or args.move).expanduser().resolve()

    if args.new:
        scaffold(target, rules_from=old if old.exists() else None)
        cfg["vault_path"] = str(target)
        save_config(cfg)
        print(f"scaffolded fresh Kovault at {target}")
        print(f"config.vault_path -> {target}")
        print(f"old folder {old} and the DB (incl. source pointers) left untouched")
        return

    # -move
    if not str(old) or not old.exists():
        sys.exit(f"current vault_path {old!s} not found; nothing to move")
    if target.exists() and any(target.iterdir()):
        sys.exit(f"target {target} exists and is not empty")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(old), str(target))
    cfg["vault_path"] = str(target)
    save_config(cfg)
    print(f"moved {old} -> {target}")
    try:
        res = rewrite_refs(cfg.get("endpoint", ""), str(old), str(target), cfg.get("username"))
        print(f"rewrote {res.get('updated', 0)} DB source reference(s) under the old path")
    except Exception as e:  # folder already moved; make the DB step recoverable, do not crash
        print(f"WARNING: folder moved but DB reference rewrite failed: {e}", file=sys.stderr)
        print("fix later: re-run once the server is reachable, or repair refs via the Kovault tools.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
