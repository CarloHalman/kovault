---
description: First-run setup — connect Kovault (your knowledge vault / wiki / database) to its backend and write local config.
argument-hint: "[endpoint] [username] [nickname]"
allowed-tools: Bash, Write, Read
---

First-run setup for Kovault. Do this:

Prerequisite: the Kovault **backend** is already running (see the kovault-backend repo), with an
embedding endpoint configured — either one the user already runs, or the bundled `embedding/`
service stood up alongside it. `/setup-kovault` only connects the plugin to that backend.

1. Collect these (use any provided in `$ARGUMENTS`, otherwise ask concisely):
   - **MCP endpoint** — the Kovault backend URL, e.g. `http://kovault-host:8000/mcp`.
   - **Username** — stamped as `edited_by` on every edit (leading identity).
   - **Nickname** — how Kovault addresses the user in-session.
   - **Update mode** — `auto` (harvest each turn via the Stop hook) or `manual` (only on `/update-kovault`).
   - **Local Kovault folder** — **ask where they want it** and accept any absolute path. Different
     users keep it in different places: a Documents subfolder, a project directory, a drive
     root, a synced vault, etc. This folder holds `CLAUDE.md`, the `_inbox/` drop folder, and
     the `sources/` folder where in-context originals are saved on ingest.

2. **Scaffold the Kovault folder** at the chosen path (create if missing):
   ```
   <vault_path>/
     _inbox/            drop files here for /ingest-kovault
     sources/           every ingested original is moved/saved here (durable copy)
     CLAUDE.md          copy the plugin's templates/CLAUDE.md here
     AGENTS.md          copy the plugin's templates/AGENTS.md here
   ```
   Use `mkdir -p` for `_inbox/` and `sources/`, and copy `CLAUDE.md`/`AGENTS.md` from the
   plugin's `templates/` folder into `<vault_path>/` (the SessionStart hook loads `CLAUDE.md`).

3. Write `~/.kovault/config.json`:
   ```json
   {
     "endpoint": "<endpoint>",
     "username": "<username>",
     "nickname": "<nickname>",
     "update_mode": "auto|manual",
     "vault_path": "<the folder from step 1>",
     "debug": false
   }
   ```

4. Register the MCP server so the tools appear (username goes in a header — the model never
   sets identity):
   ```
   claude mcp add --transport http kovault "<endpoint>" \
     --header "X-Kovault-User: <username>" --header "X-Kovault-Actor: ai"
   ```

5. Verify: call the Kovault `lookup` tool with a trivial term (or `rows` on `settings`) and
   confirm it responds, and that `<vault_path>/sources/` and `<vault_path>/_inbox/` exist.
   Report success and remind the user they can change any of this with `/settings-kovault`.
