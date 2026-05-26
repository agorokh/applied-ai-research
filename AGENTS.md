## Learned User Preferences

- Routinely uses `/babysit <PR#>` to get pull requests merge-ready: resolve conflicts, fix valid bot review items, re-run checks, and report when green.
- After merges, expects autonomous repo hygiene: sync `main` with `origin`, use GitHub as source of truth, delete only fully-safe stale work with safe branch deletion, draft-PR anything with possible real work, and remove gitignored scratch (`.scratch/`) when low-risk.
- When running a zero-sampling PR comment audit, expects every thread and comment inventoried, a RESOLVED/UNRESOLVED ledger, post-push watermark checks, and no exit until checks are green and unresolved items are zero.
- Research report HTML should use neutral third-person voice; sanitize remaining first-person operator phrasing when editing reports.
- Validate substantive Bugbot/CodeRabbit/Codex findings before changing code; bot rate-limit, quota, and summary-only comments are not actionable in-repo fixes.
- If local `git config` user identity is unset, set `GIT_AUTHOR_*` and `GIT_COMMITTER_*` from recent commits on this repo before committing.

## Learned Workspace Facts

- GitHub repository `agorokh/applied-ai-research`; active line is `main` (feature branches are deleted after squash merges).
- Published reports are static HTML under dated directories; on `main`: `2026-04-28_picking-the-extraction-llm-for-knowledge-graph-ingestion/`, `2026-05-19_choosing-memory-for-enterprise-agents/`, `2026-05-15_claude-code-via-dial-poc/`.
- Extraction LLM report was renamed from `2026-05-20_picking-the-extraction-llm-for-lightrag` to `2026-04-28_picking-the-extraction-llm-for-knowledge-graph-ingestion`.
- Pre-merge local checks: `bash scripts/check_research_structure.sh` and `python3 scripts/validate_reports.py`.
- Companion repositories are canonicalized in `COMPANION-REPOS.md` (`sdlc-dial-adapter`, `agentic-memory-mcp`); README, CONTRIBUTING, and `index.html` link there.
- Shared styling lives in `assets/dialx/research.css` with `rs-*` components; research pages use `.rs-page` (including a scoped `border-box` reset).
- `.gitignore` covers `.cursor/` and `.scratch/`; typical merge signal is CodeRabbit plus Cursor Bugbot green; Copilot reviewer rate limits are usually non-blocking.
