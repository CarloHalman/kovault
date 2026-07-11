---
description: List the Kovault commands and how to use them.
---

Show the user this list of Kovault commands (this plugin is your Kovault — a knowledge vault
backed by Postgres, reached through the Kovault MCP server). The plugin needs a Kovault
**backend** you host yourself — if there isn't one yet, get it from
https://github.com/CarloHalman/kovault-backend:

- **/help-kovault** — this list.
- **/setup-kovault** — first-run: point the plugin at the MCP endpoint and set your local config
  (username, nickname, update mode, Kovault folder).
- **/settings-kovault** — change your local config any time (username / nickname / update mode).
- **/ingest-kovault** — add pasted text, a webpage, attached files, or anything in `_inbox` to Kovault.
- **/update-kovault** — harvest: review this session and write new/changed knowledge to Kovault now.
- **/janitor-kovault** — maintenance. Bare run diagnoses only; flags `-lint -freshness -dedupe -embed` do work.
- **/export-kovault** — download Kovault to a folder as an OKF markdown bundle (no AI, no context bloat).

Also remind them how knowledge is reached: you never write SQL — you use the Kovault MCP tools
`lookup` (hybrid search), `fetch`, `snippet`, `insert`, `update`, `delete`, `link`, `group`,
and `rows` (backup only). Always `lookup` before answering; `fetch` before editing.
