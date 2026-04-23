# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated daily AI news aggregation and visualization system. Claude Code fetches news from multiple sources, deduplicates/evaluates them, generates structured JSON data files, and a Vue 3 frontend displays them as formatted news cards with a luxury gold theme.

Two main workflows exist:
1. **News generation** — Claude Code follows `WORKFLOW.md` to fetch, filter, and write `data/YYYY-MM-DD.json` files. A weekly-paper workflow (`WORKFLOW_PAPERS.md`) writes to `papers/YYYY-MM-DD.json` (Monday dates).
2. **Frontend viewer** — Vue 3 + Vite + vue-router app with three routes that load and display the JSON data.

## Commands

```bash
npm install          # Install dependencies
npm run dev          # Dev server at http://localhost:5173 (host: 0.0.0.0)
npm run build        # Production build to dist/ (also copies data/ and papers/)
npm run preview      # Preview production build
npm run build-index  # Rebuild data/index.json from all data/*.json files
```

macOS helper scripts (optional, for publishing screenshots): `npm run capture` / `shoot` / `trim` / `caption` — see `capture.py`, `shoot.sh`, `trim.py`, `gen_caption.py`.

No test suite or linter is configured.

## Architecture

**Frontend (Vue 3 Composition API + Vite 5 + vue-router):**

```
index.html → src/main.js → App.vue (<RouterView/>) → one of three pages:
  /          → NewsViewer.vue   → NewsCard.vue         (today's daily brief)
  /timeline  → TimelineViewer.vue                      (topic tracking + archive)
  /papers    → PaperViewer.vue  → PaperCard.vue        (weekly arxiv picks)
```

- **NewsViewer.vue** — Loads latest date via `/data/index.json`, falls back to 7-day scan. Splits news by importance: `critical` → headlines, `high` + `medium` → briefs.
- **TimelineViewer.vue** — Two sidebar tabs (topics/archive). Topics: filter across `keywords[]` + `category` with lazy-loaded full content. Archive: calendar-style date picker rendering the full daily brief for any past date.
- **PaperViewer.vue** — Scans back 5 Mondays looking for `papers/YYYY-MM-DD.json`; renders three tiers (featured/notable/briefs) via `PaperCard.vue`.
- **src/assets/style.css** — Global gold theme (primary: `#C9A86A`, bg: `#1A1410`), watermark overlay, responsive max-width 520px for card layouts.

**Data files:**

- `data/YYYY-MM-DD.json` — daily briefs. Each `news[]` item has: `id`, `title` (≤15 chars), `content`, `importance` (critical/high/medium), `reasoning`, `source`, `url`, `keywords[]`, `category`. Top-level: `date`, `date_formatted`, `title`, `metadata`.
- `data/index.json` — flat lightweight index (one entry per news item, no `content`/`reasoning`/`url`/`source`). Rebuild with `npm run build-index` after adding new files.
- `papers/YYYY-MM-DD.json` — weekly arxiv picks. `papers[]` items have: `title`, `original_title`, `authors_org`, `arxiv_url`, `summary`, `impact`, `importance`.

**Build-time data copy:** `vite.config.js` has a `closeBundle` plugin that copies `data/` into `dist/data/` so static hosting (Vercel) can serve them. Same pattern should apply to `papers/` if that subsystem is active.

## News Generation Workflow

`WORKFLOW.md` is the authoritative reference. Key points:

- **Active sources:** TechCrunch, AIBase News (`news.aibase.com/news`), Hacker News, CNBC, The Decoder; WebSearch multi-round queries are often the most effective. AIBase Daily, 36kr API (orz.ai), and AI Breakfast are deprecated — don't use.
- **Filtering:** 24-48 hour window, 85%+ similarity = duplicate, read `data/{date-1..-3}.json` to build a "do-not-re-cover" list.
- **Content rules:** Chinese with mandatory Chinese-English spacing; forbidden technical terms (RAG → 智能检索, tokens → 处理量/字符, LLM → AI 模型, etc.); quantified metrics required (≥3 per item); ≥2 independent sources per item.
- **JSON quote rule:** inside `content` and `reasoning`, use CJK 「」 not ASCII `"` (the latter breaks JSON parsing).
- **Length by importance (word count: 汉字=1, 英文单词=1, 数字串=1):** critical 120-200 words, high 80-120, medium 40-80.

## Key Files

| File                           | Role                                                            |
| ------------------------------ | --------------------------------------------------------------- |
| `WORKFLOW.md`                  | Authoritative 7-step news-generation instructions               |
| `WORKFLOW_PAPERS.md`           | Weekly-paper workflow (separate pipeline)                       |
| `src/router.js`                | Routes: `/` `/timeline` `/papers`                               |
| `src/components/NewsViewer.vue` + `NewsCard.vue` | Daily brief view                              |
| `src/components/TimelineViewer.vue`              | Topic tracking + archive                      |
| `src/components/PaperViewer.vue` + `PaperCard.vue` | Weekly papers view                          |
| `src/assets/style.css`         | Gold theme, watermark, responsive layout                        |
| `scripts/build-index.js`       | Rebuilds `data/index.json` from all daily JSON files            |
| `data/*.json` + `data/index.json` | Generated news data                                          |
| `papers/*.json`                | Generated weekly paper picks                                    |
