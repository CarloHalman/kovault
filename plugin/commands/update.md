---
description: Harvest this session's knowledge into your Kovault — the knowledge vault / wiki / database — now.
allowed-tools: Bash, Read
---

Harvest step (/kovault:update). Writes are always immediate; this is the deliberate "capture
what we learned" moment.

1. Review **this session's** conversation for anything worth keeping: new facts, changed
   facts, decisions made, tasks agreed, sources used.
2. For each candidate, **`lookup` first** to see if it already exists:
   - Not present → `insert` (a page + chunks, or a task/decision/source as fits).
   - Present but changed → `fetch` it, then `update` (supersede a whole page by writing the
     new one and setting the old page's `freshness = archived`).
3. Record decisions as `decisions` rows; agreed work as `tasks`; link related content with
   normal `[text](kind:uuid)` markdown — the server turns it into graph edges.
4. Group related items with the `group` tool if a project/topic/area is emerging.

Keep it tight: only durable knowledge, not chit-chat. Report what you wrote (ids + a line each).
