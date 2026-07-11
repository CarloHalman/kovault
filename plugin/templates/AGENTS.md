# CLAUDE.md: working inside your Kovault

This Kovault is a knowledge vault. Ingested knowledge lives in PostgreSQL, not
loose files. Reach it **only** through the Kovault MCP tools; never write SQL. This file loads
at SessionStart; `AGENTS.md` is the same content for non-Claude runtimes.

## Using Kovault
- **Search before answering.** Always `lookup` first; never answer from memory. Read the
  returned CHUNKS/PAGES index, then `fetch` what likely holds the answer (a whole page, a
  single chunk, or a task/decision/source). For a big page, ask `lookup` for its outline.
- **Tools only, never SQL:** `lookup`, `fetch`, `snippet`, `insert`, `update`, `delete`,
  `link`, `group`. `rows` is the **backup path only**, used when the main tools fall short
  (every `rows` call is logged so the tools can be improved).
- **`fetch` before editing** a page/chunk, so edits build on current content.
- **Superseding a page:** write the new one, then set the old page's `freshness = archived`.
- **`group`** related work into projects / topics / areas, loose and flexible (a topic can
  be a server, another a program; a project can span both).
- **Trash, never delete.** `delete` only trashes; nothing is hard-deleted. Recover with `update`.
- Address the user by the **nickname** in the local config.

## Output efficiency (spend few tokens)
- Do the Kovault ops, then answer. Do not narrate each `lookup` / `fetch` / write as you go.
- No long recap after `/ingest-kovault` / `/update-kovault` / `/janitor-kovault`: one line saying what changed + the id.
- Never restate a fetched page or chunk in more words than it holds. Quote the needed line or cite
  its id; do not re-describe what the user can already read.
- Lead with the answer, skip preamble.

## Authoring (so pages embed and link well)
- **Page shape:** `title`, a `summary`, then chunks (headers), each with a one-line `blurb`
  and a `body`. One idea per chunk (keeps each embedding clean).
- **Clean titles:** no parentheses in a title. A version may stay as plain text (`build v1.3`,
  not `(v1.3)`). Put a content type in the `type` field and any other qualifier in the
  `summary`/`blurb`.
- **Group new content:** when you add pages (or a set of pages), assign them to a relevant
  existing `group`, or create a new group if none fits. Keep related pages grouped so the graph
  stays navigable.
- **Links:** markdown `[text](<kind>:<uuid>)`, kind = page/header/task/decision/source. The
  server parses these into graph edges; fix any misses with the `link` tool. Plain `http(s)`
  links stay text. Obsidian-style `[[wikilinks]]` are resolved by title and converted to
  graph links on save.
- **Timestamps in words**, e.g. `10th of December 2020 21:20`; the server composes embedding
  text deterministically from your fields.
- **Decisions** go in `decisions` rows, **agreed work** in `tasks`. Every edit is attributed
  to your username automatically.

## Field limits (DB-enforced; exceed one and the write fails)
- **title** (page/chunk/task/decision/source) and **group name**: **≤ 64 chars**, a short
  label. Longer heading? Use a concise title and keep the full heading in the body.
- **chunk blurb**: **≤ 256 chars** (one-line summary).
- **page/source summary**: **≤ 512 chars**.
- **task/decision description**: **≤ 1024 chars**.
- **source reference** (path/url): **≤ 256 chars**.
- each **person name** (responsible / participants / contributors): **≤ 64 chars**.

## The Kovault folder
Lives at `vault_path` from `/setup-kovault` (any absolute path: Documents, a project dir, a vault
root, ...). Layout:
- `_inbox/`: drop files here for `/ingest-kovault`.
- `sources/`: durable home for **every ingested original**. `_inbox/` files and in-session
  content (pasted text, an attachment, a fetched page) are moved/saved here on ingest, and
  the source `reference` points at the saved file. Files you were merely pointed at on disk
  keep their own path.
- `CLAUDE.md` / `AGENTS.md`: these rules, loaded at SessionStart.

## Freshness
`hot/warm/cold` are recomputed from age by `/janitor-kovault -freshness`. Via `update`, set `static`
for never-stale reference pages (company/product details) and `archived` when a page is
superseded. `-freshness` never touches `static` / `archived` / `trashed`.
