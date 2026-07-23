---
description: Harvest this session's knowledge into your Kovault — the knowledge vault / wiki / database — now.
allowed-tools: Bash, Read
---

Harvest step (/kovault:update). Writes are always immediate; this is the deliberate "capture
what we learned" moment.

1. Review **this session's** conversation for anything worth keeping: new facts, changed
   facts, decisions made, tasks agreed, sources used.
2. For each candidate, **`lookup` first** to see if it already exists:
   - Not present → `write` a new block (a page + chunks, or a task/decision/source as fits).
   - Present but changed → `fetch` it, then `write` the change (supersede a whole page by writing
     the new one and setting the old page's `freshness = archived`).
3. Record decisions as `decisions` rows; agreed work as `tasks`; link related content with
   normal `[text](kind:uuid)` markdown — the server turns it into graph edges.
4. Group related items with the `group` tool if a project/topic/area is emerging.
5. **Task status recheck (scoped).** For tasks referenced this session — plus tasks belonging to any
   project/group discussed this session — check their `status` is still right and fix it with `write`
   (e.g. set `status: done` on work that finished; `done` stamps `completed_at` automatically). Do
   NOT sweep every task in the vault; keep it to what this session actually touched.

Keep it tight: only durable knowledge, not chit-chat. Report what you wrote (ids + a line each).
