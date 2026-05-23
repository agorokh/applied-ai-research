# GitHub Issue Reconciliation Report - 2026-05-22

Repository: `agorokh/applied-ai-research`
Default branch: `main`
Audit branch: `chore/issue-reconciliation-20260522`
Default-branch commit audited: `8f9b45433d02262f2c70c75fb9ac3893e52d0552`

## Executive Summary

Open GitHub issues reviewed: 0

| Classification | Count |
|---|---:|
| Verified complete | 0 |
| Complete but needs housekeeping | 0 |
| Partially implemented | 0 |
| Duplicate | 0 |
| Superseded / obsolete | 0 |
| Not implemented | 0 |
| Unverifiable | 0 |

Result: there are currently no open non-PR GitHub issues to reconcile. No issue was closed, labeled, edited, or commented on.

## Startup Evidence

| Check | Evidence |
|---|---|
| Default branch | `gh repo view --json nameWithOwner,defaultBranchRef,viewerPermission` returned `defaultBranchRef.name=main`, repository `agorokh/applied-ai-research`, viewer permission `ADMIN`. |
| Current branch before audit branch | `git status --short --branch` showed detached `HEAD`; `git symbolic-ref refs/remotes/origin/HEAD` showed `refs/remotes/origin/main`. |
| Latest default branch fetched | `git fetch origin main --prune` completed successfully. |
| Audited default-branch state | `git rev-parse HEAD origin/main` returned `8f9b45433d02262f2c70c75fb9ac3893e52d0552` for both. |
| GitHub auth | `gh auth status` reported logged in to `github.com` as `agorokh` with `repo` scope. |
| GitHub API availability | `gh api --method GET repos/agorokh/applied-ai-research` succeeded. |
| GitHub app / MCP availability | GitHub plugin tools were available for PR comments and review threads; issue inventory was collected with `gh` because it exposes issue listing and REST pagination directly. |
| Local tooling | `git`, `gh`, `rg`, shell, `bash`, and `python3` were available. |

## Repository Operating Rules Read

| File / path | Relevant rule evidence |
|---|---|
| `README.md` | Repository is a practitioner-notes site; live site is GitHub Pages; report folders are self-contained HTML plus `artefacts/`. |
| `CONTRIBUTING.md` | Corrections and larger contributions should start as issues; PRs are for corrections, broken links, methodology clarifications, or new sub-artefacts. Visual identity lives under `assets/dialx/`; do not introduce inline styles or per-report CSS overrides. Run `bash scripts/check_research_structure.sh` before opening a PR. |
| `.github/` | No `.github` files were present in the checkout. |
| `AGENTS.md`, `CLAUDE.md`, `CURSOR.md`, `.cursor/rules`, `.claude/rules`, `docs/process/` | None were present in the checkout. |

## Open Issue Inventory

| Source | Result |
|---|---|
| `gh issue list --state open --limit 200 --json number,title,labels,assignees,milestone,createdAt,updatedAt,author,url` | `[]` |
| `gh api --method GET --paginate repos/agorokh/applied-ai-research/issues -f state=open -F per_page=100 --jq '[.[] | select(.pull_request|not) | ...]'` | `[]` |
| `gh api --method GET repos/agorokh/applied-ai-research --jq '{full_name, default_branch, open_issues_count, pushed_at, updated_at}'` | `open_issues_count=0` |
| `gh issue list --state all --limit 100 --json number,title,state,createdAt,updatedAt,closedAt,author,url,labels` | `[]` |
| Independent sidecar verifier | Confirmed `gh issue list --state open --limit 100` returned `[]`; also confirmed `gh pr list --state open` returned `[]`. |

## Recent Merged PR Context

Recent merged PRs were checked to determine whether any open issues might be missing closing references. Because the open issue set is empty, no issue-specific PR or review mining was required.

`gh pr list --state merged --limit 30 --json number,title,mergedAt,author,url,baseRefName,headRefName,labels,closingIssuesReferences` returned 21 merged PRs, `#1` through `#21`. All returned `closingIssuesReferences: []`.

Most recent merged PRs:

| PR | Title | Merged | Closing issue refs |
|---|---|---|---|
| #21 | `[codex] restore Google Analytics tag` | 2026-05-22T08:55:42Z | none |
| #20 | `fix: remove Google Analytics, retrofit table styles to all three reports` | 2026-05-22T08:20:57Z | none |
| #19 | `[codex] add Google Analytics tracking` | 2026-05-22T07:39:28Z | none |
| #18 | `content: drop operator-environment limitations dressed as research intel (iteration 9)` | 2026-05-22T06:59:22Z | none |
| #17 | `feat(tables): two-line headers, footnotes, wide-table escape, winner row, link micro-typography` | 2026-05-22T02:39:14Z | none |
| #16 | `fix(report): sanitize personal-anecdote voice (s09 drift incident + artefact sweep)` | 2026-05-22T00:31:35Z | none |

## Issue Table

| Issue | Title | Classification | Confidence | Action Taken | Evidence Summary |
|---|---|---|---|---|---|
| None | No open non-PR issues | Not applicable | High | None | `gh issue list`, paginated REST issues endpoint, repository `open_issues_count`, and all-issues listing returned no issues. |

## Detailed Evidence Per Issue

No open non-PR issues existed at audit time, so no issue requirement matrix was produced.

## Drift Patterns Found

- No open issue drift found because the repository has no open issues.
- Recent merged PRs `#1` through `#21` do not contain closing issue references, but this is not currently actionable because there are no open issues left to reconcile.
- The repository appears PR-driven for recent work; issue-driven contribution rules exist in `CONTRIBUTING.md`, but the GitHub issue tracker is empty.

## Recommended Cleanup

### Safe Immediate Cleanup

- None.

### Needs User Decision

- None.

### Needs Implementation

- None identified by issue reconciliation.

### Needs Repo-Process Improvement

- Optional: if future work should remain issue-driven, require PR descriptions to include issue references or explicitly state "No issue" so later reconciliation can distinguish intentional PR-only work from missing linkage.

## GitHub Write Actions Performed

None. `ALLOW_GITHUB_WRITE_ACTIONS` was not provided, and there were no open issues to comment on, label, edit, or close.

## Verification

| Command | Result |
|---|---|
| `bash scripts/check_research_structure.sh` | Passed: `check_research_structure: OK`. |
| `python3 scripts/validate_reports.py` | Passed: `validate_reports: OK (3 reports)`. |
| `gh api --method GET repos/agorokh/applied-ai-research/commits/8f9b45433d02262f2c70c75fb9ac3893e52d0552/status --jq ...` | Returned `state=pending`, `total_count=0`, `statuses=[]`; no commit statuses were available through the statuses endpoint. |

## Limitations

- No issue body, issue comments, timeline events, cross-references, review comments, bot comments, or comments-after-last-commit were inspected because the open non-PR issue set was empty.
- The commit statuses endpoint reported no statuses for the audited default-branch commit; local repository checks were run instead.
- No GitHub write actions were performed because write permission was not explicitly enabled by the directive.
