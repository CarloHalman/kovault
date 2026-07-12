---
description: Ingest text / a webpage / attached files / the _inbox into your Kovault (knowledge vault / wiki / database).
argument-hint: "[path | url | -inbox]"
allowed-tools: Bash, Read, WebFetch
---

Ingest content into Kovault (/kovault:ingest). The AI loads the content into context and
structures it; the Kovault MCP server does the embedding, linking and source attribution. Steps:

1. **Get the content** from `$ARGUMENTS`: a file path, a URL (WebFetch it), pasted/attached
   text in this session, or everything in the Kovault `_inbox/` folder.

2. **Structure it into a page**:
   - Split at headings **H1–H3**; deeper headings stay inside the body of their chunk.
   - Text before the first heading becomes the index-0 chunk titled **"(intro)"**.
   - Write a concise **page summary** and, per chunk, a one-line **blurb** + the **body**.
   - Compute each chunk's **path** = `page.title > H1 > H2 > H3` (drop H1 if it equals the
     page title). Keep one idea per chunk so embeddings stay clean.
   - Keep the chunk **title** concise (**≤ 64 chars**); if a heading is longer, use a short
     title and let the full heading live in the body. (Field limits: see Kovault `CLAUDE.md`.)

3. **Create the source row** first via the Kovault `insert` tool (`table: sources`) with
   `type`, `reference` (path/url), a `sha256` of the original, and a short `summary`.
   **Dedupe**: before inserting, `lookup`/`rows` for an existing source with the same
   `sha256`; if found, skip re-ingest, reuse that source, and append today's date to its
   summary via `update` (its `created_at` keeps the first date).

4. **Insert the page + chunks**: `insert table: pages` for the page, then `insert
   table: headers` for each chunk (pass `page_id`, `index`, `level`, `title`, `blurb`,
   `body`, `path`, and `source_ids: [<the source id>]` for attribution). The server embeds
   each chunk, parses `[text](kind:uuid)` links into the graph, and writes header_sources.

5. **Persist every original into `<vault_path>/sources/`** (the local Kovault folder set in
   `/kovault:setup`). `sources/` is the single durable home for ingested originals:
   - **In-context content** — pasted text, an attachment, or a fetched webpage — is written
     into `<vault_path>/sources/` (sensible filename from the title, keep the extension).
   - **Files dropped in `<vault_path>/_inbox/`** are **moved into `<vault_path>/sources/`** after
     ingest (no `_inbox/_raw/`).
   - In both cases set the source row's `reference` to the saved path in `sources/`.
   - Files you were merely pointed at by an existing on-disk path stay where they are (the
     `reference` is that original path).

Report what you created (page id + chunk count + source id), where the original was saved,
and any dangling-link warnings.
