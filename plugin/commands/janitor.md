---
description: Kovault maintenance (your knowledge vault / wiki / database) — diagnose (bare) or act with flags.
argument-hint: "[-lint] [-freshness] [-dedupe] [-embed]"
allowed-tools: Bash
---

Run Kovault maintenance via the Kovault `janitor` MCP tool, passing whatever flags are in
`$ARGUMENTS` as the tool's `flags` list (/kovault:janitor).

- **Bare `/kovault:janitor`** (no flags) → diagnose only: runs the checks, writes a `janitor_reports`
  row (report + advice + counts), changes nothing.
- **`-lint`** → fix structure: renumber header indexes to be contiguous, and prune redundant
  task-dependency edges (drop a direct block that is already implied through an intermediate).
- **`-freshness`** → recompute `hot/warm/cold` from age (thresholds in `settings`); never
  touches `static` / `archived` / `trashed`.
- **`-dedupe`** → merge duplicate sources (same sha256) and identical headers; losers are
  **trashed, never deleted**.
- **`-embed`** → re-embed any row with `embedded_at < updated_at` or null.

There is no delete flag — nothing is ever hard-deleted; trash is the terminal state. After
the run, summarise the returned report and counts for the user.
