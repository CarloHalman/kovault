# Kovault

AI-first knowledge vault for Claude Code, inspired by Karpathy's LLM-wiki. Knowledge lives in a
Postgres database. Claude reaches it through an MCP server over a fixed tool set (`lookup`,
`fetch`, `write`, …); the model has raw SQL only in debug mode. Search is hybrid semantic + keyword + graph;
two-part retrieval keeps recall fast and cheap: `lookup` returns a compact ranked index, then
`fetch` pulls the page or chunk you need.

This is the **plugin**. Install it, point it at your own Kovault backend you host yourself.

> **No backend? :** https://github.com/CarloHalman/kovault-backend

## Install

```
/plugin marketplace add https://github.com/CarloHalman/kovault
/plugin install kovault@kovault
/kovault:setup
```

`/kovault:setup` connects the plugin to your own backend endpoint (`http://<your-host>:8000/mcp`),
writes `~/.kovault/config.json`, and scaffolds your local Kovault folder.

> **Install hiccup?** The interactive `/plugin install` can fail right after a fresh `marketplace add`
> (stale cache). If it does, run the CLI instead: `claude plugin install kovault@kovault`.

## Commands

- **/kovault:setup** — first-run: point the plugin at the MCP endpoint, set your local config.
- **/kovault:settings** — change your local config (username / nickname / update mode / debug).
- **/kovault:ingest** — add pasted text, a webpage, attached files, or anything in `_inbox`.
- **/kovault:update** — harvest this session's new/changed knowledge into Kovault now.
- **/kovault:janitor** — maintenance: bare diagnoses; `-lint -freshness -dedupe -embed` do work.
- **/kovault:export** — download Kovault to a folder as an OKF markdown bundle (no AI).
- **/kovault:help** — the command list.

Natural language works too: "update the wiki", "search the vault", "add this to the database"
all route to the right command.
