# Repository Guidelines

## Project Structure & Module Organization

The Vue 3 application lives in `src/`. `src/main.js` mounts the app, `src/router.js` defines routes, reusable cards and page-level viewers are in `src/components/`, and global styling is in `src/assets/style.css`. Static assets belong in `public/`.

Generated content is organized by pipeline: daily briefs in `data/YYYY-MM-DD.json`, paper selections in `papers/YYYY-MM-DD.json`, and weekly editions in `weekly/YYYY-WNN.json`. Keep their corresponding `index.json` files synchronized. Workflow specifications (`WORKFLOW.md`, `WORKFLOW_PAPERS.md`, and `WORKFLOW_WEEKLY.md`) are authoritative for content shape and editorial rules. Node index builders are in `scripts/`; root-level Python and shell files support publishing and screenshots. Production output goes to `dist/` and must not be edited manually.

## Build, Test, and Development Commands

- `npm install`: install pinned dependencies from `package-lock.json`.
- `npm run dev`: start the Vite development server, normally at `http://localhost:5173`.
- `npm run build`: rebuild daily and weekly indexes, bundle the app, and copy content into `dist/`.
- `npm run preview`: serve the production bundle for a final local check.
- `npm run build-index` / `npm run build-weekly-index`: refresh one generated index after content changes.
- `npm run weekly:publish` and `npm run weekly:split`: run weekly publishing utilities.

## Coding Style & Naming Conventions

Follow the existing Vue Composition API and `<script setup>` style. Use two-space indentation, single quotes in JavaScript, and omit semicolons. Name Vue components in PascalCase (`WeeklyStoryCard.vue`), JavaScript variables in camelCase, and Python functions in snake_case. Keep route components focused on loading and grouping data; move repeated presentation into card components. Preserve the established responsive gold theme unless a design change is intentional.

## Testing Guidelines

No automated test suite or coverage threshold is configured. Every change must pass `npm run build`. For UI work, also run `npm run dev` or `npm run preview` and check affected routes at desktop and narrow mobile widths. For content edits, parse the changed JSON, rebuild its index, and verify the entry renders. Name future tests after their subject, for example `NewsViewer.spec.js`.

## Commit & Pull Request Guidelines

History uses short, scoped subjects such as `news: 2026-07-10 AI 新闻简报…` and `docs: …`; follow `<scope>: <concise summary>` with scopes like `news`, `docs`, `ui`, or `build`. Keep generated indexes in the same commit as their source data. Pull requests should explain the change, list validation performed, link related issues, and include screenshots for visible UI changes. Call out schema or workflow changes explicitly.
