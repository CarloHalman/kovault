#!/usr/bin/env python3
"""Export the Kovault DB to an OKF markdown bundle in the local Kovault folder. No AI, no SQL.

  python kovault_export.py                 export everything to <vault_path>/kovault-export
  python kovault_export.py --tables tasks,decisions
  python kovault_export.py --no-wikilinks  keep [text](kind:uuid) links instead of [[Title]]
  python kovault_export.py --out /some/dir override the destination

Reads ~/.kovault/config.json for `endpoint`, `vault_path`, `username`. The server's read-only
/export route streams a ready-made zip whose folder tree is already nested
(pages/<type>/, tasks/<status>/, decisions/<ISO-week>/, sources/<sourcetype>/ with
`file` sources split by extension, groups/<grouptype>/), so this client just unzips it. The
destination is wiped first so the export is a clean mirror of the DB, not an accreting pile.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

CONFIG = Path.home() / ".kovault" / "config.json"
TABLES = ("pages", "tasks", "decisions", "sources", "groups")


def load_config() -> dict:
    if not CONFIG.exists():
        sys.exit(f"no config at {CONFIG}; run /kovault:setup first")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def base_url(endpoint: str) -> str:
    e = (endpoint or "").rstrip("/")
    return e[:-4] if e.endswith("/mcp") else e


def download_zip(endpoint: str, tables: list[str], wikilinks: bool, user: str | None,
                 group: str | None = None, linked_to: str | None = None) -> bytes:
    qs = {"tables": ",".join(tables)}
    if wikilinks:
        qs["wikilinks"] = "1"
    if group:
        qs["group"] = group
    if linked_to:
        qs["linked_to"] = linked_to
    url = base_url(endpoint) + "/export?" + urllib.parse.urlencode(qs)
    req = urllib.request.Request(url, headers={"X-Kovault-User": user or "script"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main() -> None:
    ap = argparse.ArgumentParser(description="Export the Kovault DB to <vault_path>/kovault-export (OKF bundle).")
    ap.add_argument("--tables", default=",".join(TABLES), help="comma list; default all")
    ap.add_argument("--no-wikilinks", action="store_true", help="keep markdown links, not [[Title]]")
    ap.add_argument("--group", default="", help="restrict scope to one group's members")
    ap.add_argument("--linked-to", default="", help="restrict scope to an id + its 1-hop neighbours")
    ap.add_argument("--out", default="", help="destination dir (default <vault_path>/kovault-export)")
    args = ap.parse_args()

    cfg = load_config()
    tables = [t.strip() for t in args.tables.split(",") if t.strip() in TABLES]
    if not tables:
        sys.exit(f"no valid tables; choose from {','.join(TABLES)}")
    out = Path(args.out).expanduser() if args.out else Path(cfg["vault_path"]).expanduser() / "kovault-export"

    data = download_zip(cfg.get("endpoint", ""), tables, not args.no_wikilinks, cfg.get("username"),
                        args.group or None, args.linked_to or None)

    if out.exists():
        shutil.rmtree(out)          # clean mirror: drop files for rows that moved/renamed/left the DB
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    with zipfile.ZipFile(tmp_path) as zf:
        names = [n for n in zf.namelist() if not n.endswith("/")]
        zf.extractall(out)
    Path(tmp_path).unlink(missing_ok=True)

    md = sum(1 for n in names if n.endswith(".md") and n not in ("index.md", "log.md"))
    print(f"exported {md} entit(y/ies) + index.md + log.md to {out}")


if __name__ == "__main__":
    main()
