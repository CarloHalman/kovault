---
description: Export your Kovault (knowledge vault / wiki / database) to a folder as an OKF markdown bundle (no AI, no context bloat).
argument-hint: "[all | pages,tasks,decisions,sources,groups] [--group <name>] [--linked-to <id>] [--no-wikilinks] [--out <folder>]"
allowed-tools: Bash, Read
---

Export the Kovault DB to a Google OKF markdown bundle. A bundled script does the whole job with
no AI and no context bloat: the MCP server renders and zips an already-nested tree, the script
downloads it straight to disk and unzips it into your Kovault folder. File contents never enter
context.

**Run the script — one Bash step.** It reads `~/.kovault/config.json` (`endpoint`, `vault_path`,
`username`) itself, so it needs no other input.
```
"$(command -v python3 || command -v python)" "${CLAUDE_PLUGIN_ROOT}/scripts/kovault_export.py" $ARGUMENTS
```
(picks `python3` where it exists — Ubuntu/WSL ships only `python3` — and falls back to `python`.)
- No args → exports every table to `<vault_path>/kovault-export`, Obsidian `[[wikilinks]]` on.
- `--tables pages,tasks` → subset. `--no-wikilinks` → keep `[text](kind:uuid)` links.
- `--group <name>` → only that group's members. `--linked-to <id>` → an id + its 1-hop neighbours.
- `--out <folder>` → a different destination (default is always `<vault_path>/kovault-export`).

The destination is wiped and rewritten each run, so it stays a clean mirror of the DB. The tree:
```
pages/<type>/                 tasks/<status>/       decisions/<ISO-week>/
sources/<sourcetype>/         (file sources split again by extension: sources/file/<ext>/)
groups/<grouptype>/           index.md   log.md
```
Two rows that slug to the same filename in one folder get `-01`, `-02` suffixes (no silent
overwrite). Just report the script's summary line and the folder path; never `cat` the exported
files — the point is to keep them out of context.
