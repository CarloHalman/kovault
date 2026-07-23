#!/usr/bin/env python3
"""PreToolUse hook (Kovault). Best-effort, never breaks the turn:
  1. gate the debug-only raw SQL tools (`read_sql` / `write_sql`) when debug is off.
  2. de-dup whole-page `fetch`es in a session (F1): a page already returned this session is denied
     UNLESS it was edited since (its `updated_at` moved) — an edited page is always re-fetchable.
     A repeat of an already-denied fetch is also allowed (escape hatch for a compacted context).
  3. when debug is on, stamp the tool start time for PostToolUse latency.
Matched to `mcp__kovault__.*` in hooks.json. Stdlib only; exits 0 except the deliberate deny (2)."""
import json
import re
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

CONFIG = Path.home() / ".kovault" / "config.json"


def _state_path(session_id) -> Path:
    sid = re.sub(r"[^A-Za-z0-9_-]", "_", str(session_id or "nosession"))
    return Path(tempfile.gettempdir()) / f"kovault-fetched-{sid}.json"


def _load(p: Path) -> dict:
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return {"pages": dict(d.get("pages") or {}), "denied": list(d.get("denied") or [])}
    except Exception:
        return {"pages": {}, "denied": []}


def _base(endpoint: str) -> str:
    e = (endpoint or "").rstrip("/")
    return e[:-4] if e.endswith("/mcp") else e


def _current_updated(base: str, ids: list) -> dict | None:
    """GET /page-meta -> {id: updated_iso}. None on any failure (caller then fails OPEN = allow)."""
    if not base:
        return None
    try:
        url = base + "/page-meta?ids=" + ",".join(ids)
        with urllib.request.urlopen(url, timeout=3) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None


def _dedup(data: dict, endpoint: str) -> None:
    """Deny a whole-page fetch whose every page was already returned this session AND is unchanged."""
    if not (data.get("tool_name") or "").endswith("__fetch"):
        return
    ti = data.get("tool_input") or {}
    if ti.get("outline"):
        return                                   # outline is cheap — never dedup it
    pages = [str(x) for x in (ti.get("pages") or [])]
    if not pages or any(ti.get(k) for k in ("headers", "tasks", "decisions", "sources", "groups")):
        return                                   # only a pure page fetch is deduped
    st = _load(_state_path(data.get("session_id")))
    seen = st["pages"]
    if not all(p in seen for p in pages):
        return                                   # something new -> allow (PostToolUse records it)
    current = _current_updated(_base(endpoint), pages)
    if current is None:
        return                                   # can't verify freshness -> fail open (allow)
    if any(current.get(p, "") != seen.get(p, "") for p in pages):
        return                                   # edited since we fetched it -> allow the re-fetch
    if all(p in set(st["denied"]) for p in pages):
        return                                   # already denied once -> allow the retry (escape hatch)
    st["denied"] = sorted(set(st["denied"]) | set(pages))
    try:
        _state_path(data.get("session_id")).write_text(json.dumps(st), encoding="utf-8")
    except Exception:
        pass
    print("Already fetched this page this session and it is unchanged. Use `fetch outline=true` then "
          "fetch the one chunk you need — or re-issue this exact fetch to force a full re-read.",
          file=sys.stderr)
    raise SystemExit(2)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    cfg = {}
    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        pass
    if (data.get("tool_name") or "").endswith("_sql") and not bool(cfg.get("debug")):
        print("The Kovault raw SQL tools (`read_sql` / `write_sql`) are debug-only. "
              "Enable debug in /kovault:settings to use them.", file=sys.stderr)
        raise SystemExit(2)
    try:
        _dedup(data, cfg.get("endpoint"))        # may raise SystemExit(2) to deny
    except SystemExit:
        raise
    except Exception:
        pass                                     # dedup must never break a turn
    if not cfg.get("debug"):
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
