# CLAUDE.md: working inside your Kovault

This Kovault is a knowledge vault. Ingested knowledge lives in PostgreSQL, not
loose files. Reach it **only** through the Kovault MCP tools; never write SQL. This file loads
at SessionStart; `AGENTS.md` is the same content for non-Claude runtimes.

## Using Kovault
- **Search before answering.** Always `lookup` first; never answer from memory. Read the
  returned CHUNKS/PAGES index, then `fetch` what likely holds the answer (a whole page, a
  single chunk, or a task/decision/source). For a big page, ask `lookup` for its outline.
- **Tools only, never SQL:** `lookup`, `fetch`, `snippet` (read); `write` (create / update / trash
  every entity — see **Writing** below); `group` + `link` (membership + junction rows). `rows` is
  the **backup path only**, logged. (`insert` / `update` / `delete` still work this release but are
  deprecated in favor of `write`.)
- **Exact lists / counts:** `lookup(filters=[{column, op, value}], count=true)` (precise mode) for
  deterministic audits and aggregates, instead of `rows` / `sql`.
- **`fetch` before editing** a page/chunk, so edits build on current content.
- **Superseding a page:** write the new one, then set the old page's `freshness = archived`.
- **`group`** related work into projects / topics / areas, loose and flexible (a topic can
  be a server, another a program; a project can span both).
- **Trash, never delete.** Trash via `write` (`trashed: true`); nothing is hard-deleted. Recover by writing the row live again. (One exception: a `type: edit` block with `trashed: true` hard-deletes that audit-log row — for pruning noisy log entries, not recoverable.)
- Address the user by the **nickname** in the local config.

## Writing (the `write` tool)
- One `write` takes a LIST of `---`-fenced templates — the SAME shape `fetch` returns, so you write
  what you read: `blocks: ["---\ntype: task\ntitle: …\n---", …]`. Batch = several blocks in the list.
- `id:` present → UPDATE that row (only the fields you include change; omit a field to leave it, set
  it empty to clear). `id:` absent → INSERT. An `id:` that matches no live row is an error, not a new row.
- A chunk is `type: header` with `page_id`, `index`, `title`, `blurb`, then the body AFTER the closing
  `---`. Chunk ids come from `fetch(outline=true)` — a whole-page fetch doesn't show them.
- Enum values (a wrong one is rejected with the valid list): status `todo|doing|done`, priority
  `low|medium|high|urgent`, scope `minutes|hours|days|weeks`, page freshness
  `hot|warm|cold|static|archived|trashed`, source type `website|file|server|database`, group type `project|topic|area`.

## Output efficiency (spend few tokens)
- Do the Kovault ops, then answer. Do not narrate each `lookup` / `fetch` / write as you go.
- No long recap after `/kovault:ingest` / `/kovault:update` / `/kovault:janitor`: one line saying what changed + the id.
- Never restate a fetched page or chunk in more words than it holds. Quote the needed line or cite
  its id; do not re-describe what the user can already read.
- Lead with the answer, skip preamble.
- **Name entities by title, never by bare id.** When you mention a page/task/decision/source/group
  in chat, refer to it by its title (e.g. "finished the *making-things-better* task"), not its
  UUID. Ids are for tool calls and links, not for talking to the user — never print a bare UUID in
  chat unless the user explicitly asks for the id.

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
Lives at `vault_path` from `/kovault:setup` (any absolute path: Documents, a project dir, a vault
root, ...). Layout:
- `_inbox/`: drop files here for `/kovault:ingest`.
- `sources/`: durable home for **every ingested original**. `_inbox/` files and in-session
  content (pasted text, an attachment, a fetched page) are moved/saved here on ingest, and
  the source `reference` points at the saved file. Files you were merely pointed at on disk
  keep their own path.
- `CLAUDE.md` / `AGENTS.md`: these rules, loaded at SessionStart.

## Freshness
`hot/warm/cold` are recomputed from age by `/kovault:janitor -freshness`. Via `update`, set `static`
for never-stale reference pages (company/product details) and `archived` when a page is
superseded. `-freshness` never touches `static` / `archived` / `trashed`.
