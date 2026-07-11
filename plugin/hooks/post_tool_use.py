#!/usr/bin/env python3
"""PostToolUse hook. When local `debug` is on, log the Kovault tool call to
the `debug_log` table via the server's /debug-log route: tool, inputs, result shape, latency,
and the conversation context (last user message + assistant text so far) that the server never
sees. Matched to `mcp__kovault__.*` in hooks.json. Stdlib only; never blocks the turn (exits 0).

The transcript JSONL format is internal to Claude Code and may change between versions, so the
extraction below is best-effort and degrades to empty context rather than failing the turn."""
import json
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

CONFIG = Path.home() / ".kovault" / "config.json"
CAP = 4000        # cap the stored user/assistant text so a row stays reasonable
RESULT_CAP = 50000  # cap the stored raw result (result_tokens keeps the full-length estimate)


def _base(endpoint: str) -> str:
    e = (endpoint or "").rstrip("/")
    return e[:-4] if e.endswith("/mcp") else e


def _duration_ms(tuid: str | None):
    if not tuid:
        return None
    try:
        p = Path(tempfile.gettempdir()) / f"kovault-debug-{tuid}"
        start = float(p.read_text(encoding="utf-8"))
        try:
            p.unlink()
        except Exception:
            pass
        return int((time.time() - start) * 1000)
    except Exception:
        return None


def _resp_str(resp) -> str:
    try:
        return resp if isinstance(resp, str) else json.dumps(resp)
    except Exception:
        return str(resp)


def _summary(resp) -> str:
    s = _resp_str(resp)
    return f"{len(s)} chars / {s.count(chr(10)) + 1} lines"


def _tokens(resp) -> int:
    """Rough token cost of the tool result (chars / 4) — what it costs to read into context."""
    return len(_resp_str(resp)) // 4


def _role(e: dict) -> str:
    r = e.get("role") or (e.get("message") or {}).get("role")
    return r or {"user_message": "user", "assistant_message": "assistant",
                 "user": "user", "assistant": "assistant"}.get(e.get("type"), "")


def _content(e: dict):
    c = e.get("content")
    return c if c is not None else (e.get("message") or {}).get("content")


def _text_and_tools(content):
    """(joined_text, [tool_use_ids]) from a content value (str or list of blocks)."""
    if isinstance(content, str):
        return content, []
    texts, tools = [], []
    if isinstance(content, list):
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text" and b.get("text"):
                texts.append(b["text"])
            elif b.get("type") == "tool_use":
                tools.append(b.get("id"))
    return "\n".join(texts), tools


def _extract_context(path: str | None, tuid: str | None) -> tuple[str, str]:
    """Best-effort (last_user_text, assistant_text_before_this_tool_call)."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except Exception:
        return "", ""
    last_user, assistant_text = "", ""
    for ln in lines:
        try:
            e = json.loads(ln)
        except Exception:
            continue
        role = _role(e)
        if role == "user":
            txt, _ = _text_and_tools(_content(e))
            if txt.strip():
                last_user, assistant_text = txt.strip(), ""   # new turn resets assistant text
        elif role == "assistant":
            txt, tool_ids = _text_and_tools(_content(e))
            if txt.strip():
                assistant_text = (assistant_text + "\n" + txt).strip() if assistant_text else txt.strip()
            if tuid and tuid in tool_ids:
                break        # reached the call we are logging
    return last_user[:CAP], assistant_text[:CAP]


def main() -> None:
    try:
        data = json.load(sys.stdin)
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception:
        return
    if not cfg.get("debug"):
        return
    tool = data.get("tool_name") or ""
    tuid = data.get("tool_use_id")
    last_user, assistant_text = _extract_context(data.get("transcript_path"), tuid)
    payload = {
        "session_id": data.get("session_id"),
        "user": cfg.get("username"),
        "tool": tool.split("__")[-1] or tool,     # mcp__kovault__lookup -> lookup
        "tool_input": data.get("tool_input"),
        "result_summary": _summary(data.get("tool_response")),
        "result": _resp_str(data.get("tool_response"))[:RESULT_CAP],
        "result_tokens": _tokens(data.get("tool_response")),
        "duration_ms": _duration_ms(tuid),
        "last_user_msg": last_user,
        "assistant_text": assistant_text,
    }
    try:
        req = urllib.request.Request(
            _base(cfg.get("endpoint")) + "/debug-log",
            data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass        # a logging failure must never break the turn


if __name__ == "__main__":
    main()
