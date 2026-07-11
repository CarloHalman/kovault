---
description: Change your local Kovault config (username / nickname / update mode / debug).
allowed-tools: Bash, Write, Read
---

Change the user's **local** Kovault config (per-user, on this machine).

1. Read `~/.kovault/config.json`. Show the current values (include `debug`, default off).
2. Apply whatever the user asked to change in `$ARGUMENTS` (username, nickname, update mode,
   endpoint, vault_path, `debug`). Write the file back.
3. If `username` or `endpoint` changed, re-register the MCP server:
   `claude mcp remove kovault` then the `claude mcp add … --header "X-Kovault-User: <username>"`
   from `/setup-kovault`.
4. **Debug mode** (`debug`: true/false, default false): when on, the PostToolUse hook logs every
   Kovault tool call (tool, inputs, result shape, **token cost**, latency, and the user message + your
   text that led to it) into the `debug_log` table, and the raw read-only `sql` tool is unlocked for
   experimenting with retrieval. If the user is toggling debug, confirm on or off explicitly; it
   stays off unless they ask for it.

Note: **server-wide** settings (RRF k, cutoff ladder, freshness thresholds, embedding
model/endpoint) live in the DB `settings` table, not here — they are admin-tunable via SQL,
not per user.
