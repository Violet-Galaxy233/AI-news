# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated daily AI news aggregation and visualization system. Claude Code fetches news from multiple sources, deduplicates/evaluates them, generates structured JSON data files, and a Vue 3 frontend displays them as formatted news cards with a luxury gold theme.

Two main workflows exist:
1. **News generation** — Claude Code follows `WORKFLOW.md` to fetch, filter, and write `data/YYYY-MM-DD.json` files
2. **Frontend viewer** — Vue 3 + Vite app that loads and displays the most recent JSON data file

## Commands

```bash
npm install          # Install dependencies
npm run dev          # Dev server at http://localhost:5173 (host: 0.0.0.0)
npm run build        # Production build to dist/
npm run preview      # Preview production build
```

No test suite or linter is configured.

## Architecture

**Frontend (Vue 3 Composition API + Vite 5):**

```
index.html → src/main.js → App.vue → NewsViewer.vue → NewsCard.vue
```

- **NewsViewer.vue** — Loads `/data/{date}.json`, auto-falls back through the last 7 days. Splits news by importance: `critical` → headlines section, `high`/`medium` → briefs section.
- **NewsCard.vue** — Two render modes: `headline` (numbered, expanded) and `brief` (bullet, compact).
- **style.css** — Global gold theme (primary: `#C9A86A`, bg: `#1A1410`), watermark overlay, responsive max-width 520px.

**Data files (`data/YYYY-MM-DD.json`):**

Each file contains a `news[]` array where each item has: `id`, `title` (≤15 chars), `content`, `importance` (critical/high/medium), `source`, `url`, `keywords[]`, `category`, plus top-level `metadata`.

## News Generation Workflow

`WORKFLOW.md` is the authoritative reference (290 lines). Key points:

- **Sources:** AI Breakfast, TechCrunch, AIBase, Hacker News, 36kr, AI News (fetched via WebFetch/WebSearch)
- **Filtering:** 24-48 hour window, 85%+ similarity = duplicate, target 8-12 final items
- **Content rules:** Chinese text with mandatory Chinese-English spacing; forbidden technical terms (RAG → 智能检索, tokens → 处理量, LLM → 大语言模型, etc.); quantified metrics required instead of vague adjectives
- **Length by importance:** critical 50-80 chars, high 35-50 chars, medium 20-35 chars

## Key Files

| File | Role |
|------|------|
| `WORKFLOW.md` | Complete 6-step news generation instructions |
| `src/components/NewsViewer.vue` | Data loading, importance filtering, date formatting |
| `src/components/NewsCard.vue` | Headline vs brief card rendering |
| `src/assets/style.css` | Gold theme, watermark, responsive layout |
| `data/*.json` | Generated news data (one file per date) |
