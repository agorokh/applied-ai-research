## Public-vitrine rule (read before any PR, commit, or comment)

This repository is a **public showcase**. Everything visible here is publication
copy: files, PR titles and bodies, commit messages, review-thread replies, issue
text. Before writing any of them, apply the same sanitization bar as the
published pages themselves:

- No internal process narration (review tooling, verification workflows,
  session or authoring mechanics, who directed what).
- No references to private repositories, private issue trackers, or internal
  project names.
- No strategy, outreach, propagation, or planning material of any kind; that
  class of content lives in the private authoring environment and never
  transits this repo.
- Commit messages and PR bodies describe **what the published artifact is**, in
  the publication's own voice, and nothing else.

## Learned User Preferences

- Routinely uses `/babysit <PR#>` to get pull requests merge-ready: resolve conflicts, fix valid bot review items, re-run checks, and report when green.
- After merges, expects autonomous repo hygiene: sync `main` with `origin`, use GitHub as source of truth, delete only fully-safe stale work with safe branch deletion, draft-PR anything with possible real work, and remove gitignored scratch (`.scratch/`) when low-risk.
- When running a zero-sampling PR comment audit, expects every thread and comment inventoried, a RESOLVED/UNRESOLVED ledger, post-push watermark checks, and no exit until checks are green and unresolved items are zero.
- Research report HTML should use neutral third-person voice; sanitize remaining first-person operator phrasing when editing reports.
- Validate substantive Bugbot/CodeRabbit/Codex findings before changing code; bot rate-limit, quota, and summary-only comments are not actionable in-repo fixes.
- If local `git config` user identity is unset, set `GIT_AUTHOR_*` and `GIT_COMMITTER_*` from recent commits on this repo before committing.

## Learned Workspace Facts

- GitHub repository `agorokh/applied-ai-research`; active line is `main` (feature branches are deleted after squash merges).
- Published notes are static HTML; the catalogue is the Atelier publication: `index.html` (journal cover + bound archive) and one file per note under `notes/` (`mcp-harvesting`, `harness-viability`, `telemetry-plane`, `value-layer`). The retired dated directories (`2026-04-28_…`, `2026-05-15_…`, `2026-05-19_…`) now hold GA-bearing redirect stubs that preserve their old URLs; their `artifacts/` folders are kept as linkable companion material.
- Extraction LLM report was renamed from `2026-05-20_picking-the-extraction-llm-for-lightrag` to `2026-04-28_picking-the-extraction-llm-for-knowledge-graph-ingestion`.
- Pre-merge local checks (Atelier publication gates): GA tag `G-HHYGP07F16` in every page `<head>`; `grep -rn 'href="#"' index.html notes/*.html` returns nothing; zero em or en dashes in published HTML; a `<title>`, `<meta name="description">`, and `<link rel="canonical">` on every page.
- Companion repositories are canonicalized in `COMPANION-REPOS.md` (`sdlc-dial-adapter`, `agentic-memory-mcp`); README, CONTRIBUTING, and `index.html` link there.
- Shared styling is the Atelier reading style under `assets/`: `theme.css` (Claude Design tokens and primitives, never edit), `notes.css` (shared note stylesheet), `atelier-figures.js` (inline-SVG figures), `atelier-rooms.js` (room background, publication tier `data-mood="paper"`). Fonts are Newsreader / Schibsted Grotesk / Spline Sans Mono from Google Fonts.
- `.gitignore` covers `.cursor/` and `.scratch/`; typical merge signal is CodeRabbit plus Cursor Bugbot green; Copilot reviewer rate limits are usually non-blocking.
