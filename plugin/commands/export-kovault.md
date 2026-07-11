---
description: Export your Kovault (knowledge vault / wiki / database) to a folder as an OKF markdown bundle (no AI, no context bloat).
argument-hint: "[folder] [all | pages,tasks,decisions,sources,groups | <ids>]"
allowed-tools: Bash, Read
---

Export the Kovault DB to a folder as a Google OKF markdown bundle. The MCP server renders and
zips the bundle; you download it straight to disk with `curl`, so the file contents never
enter context. This is the no-AI backup/interchange path.

1. **Resolve config.** Read `~/.kovault/config.json`. The download base is `endpoint` with a
   trailing `/mcp` removed (e.g. `http://host:8000/mcp` gives base `http://host:8000`).
   Default target folder is `<vault_path>/export` unless `$ARGUMENTS` names one.

2. **Decide scope** from `$ARGUMENTS`:
   - nothing or `all` gives every table (`pages,tasks,decisions,sources,groups`),
   - a comma list picks tables,
   - bare UUIDs restrict to those row ids (add `&ids=<id>,<id>` to the query).
   Optionally call the Kovault `export` tool first for a manifest (counts + the exact path) so
   you can confirm scope. The manifest carries no file contents.
   To export Obsidian-style, add `&wikilinks=1` to the query (or pass `wikilinks: true` to the
   `export` tool): every `[text](kind:uuid)` link becomes a `[[Title]]` wikilink in the files.

3. **Download and unzip in ONE Bash step** so the bytes go to disk, never into context:
   ```
   curl -fsS "<base>/export?tables=pages,tasks,decisions,sources,groups" -o "$TMPDIR/kovault-export.zip" \
     && mkdir -p "<folder>" \
     && unzip -oq "$TMPDIR/kovault-export.zip" -d "<folder>" \
     && rm -f "$TMPDIR/kovault-export.zip"
   ```
   (Use a real temp path if `$TMPDIR` is unset.)

4. **Report** the folder path and file count (`find "<folder>" -name '*.md' | wc -l`). Do NOT
   `cat` the exported files; the point is to keep them out of context. The bundle has
   `pages/ tasks/ decisions/ sources/ groups/` folders plus `index.md` and `log.md`.
