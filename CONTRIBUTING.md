# Contributing

This is a working-drafts series of practitioner research notes. Contributions are welcome from other practitioners working on similar enterprise-AI deployment problems — gateways, memory, agent harnesses, telemetry, evaluation methodology, cost analysis, production adoption.

## What kind of contribution

### 1. Open an issue

For:
- A correction to a report (numbers, citations, broken link, factual error)
- A re-measurement on a different stack that confirms or invalidates a headline finding (see each report's `artefacts/invalidation.md` for the specific re-measurement that would falsify each claim)
- A pointer to prior public work the report missed
- A proposal for a new report (open an issue with the abstract + the corpus you plan to measure against)

### 2. Open a pull request

For corrections, broken-link fixes, methodology clarifications, or new sub-artefacts under an existing report's `artefacts/` directory. Larger contributions (a new report, a structural design change) should start as an issue so we can agree on the scope before you spend time.

## How to write a report

Each report follows a 13-section spine. The clearest exemplars are:

- [`2026-05-19_choosing-memory-for-enterprise-agents/index.html`](2026-05-19_choosing-memory-for-enterprise-agents/index.html) — depth piece with weighted-aggregate methodology
- [`2026-05-15_claude-code-via-dial-poc/index.html`](2026-05-15_claude-code-via-dial-poc/index.html) — engineering brief on a routing pattern + cost matrix

Both ship a parallel `artefacts/` directory with:

- `methodology.md` — test design, scoring rubric, aggregation formula, what the methodology is NOT
- `claims.md` — claims ledger (every headline tagged `measured` / `inferred` / `hypothetical` / `recommendation` / `scope`)
- `invalidation.md` — Popperian falsification conditions per finding
- Subject-specific reference files (e.g. `adoption-bar.md`, `task-families.md`, `pricing-snapshot/`, `telemetry-schema.md`, `canary-harness/`)

A new report should ship at least `methodology.md` + `claims.md` + `invalidation.md` alongside the HTML.

## Voice and framing

- **State the adoption bar before the measurement.** A bar applied post-hoc rationalises; a bar applied a priori constrains.
- **Publish the weighting before the score.** Uniform vs production-weighted aggregates often disagree; the disagreement is usually the finding.
- **Name the scope limits as plainly as the headline.** Every report's §11 lists the conditions under which the magnitudes do not transfer.
- **Cite prior public work explicitly.** Call out the gap when none exists.
- **Use "EPAM DIAL" only as a product reference**, never as institutional warrant. See [`ABOUT.md`](ABOUT.md) for the disclaimer language; the mechanical rule is in the v22 council ADR.

## Visual identity

The site uses the dialx CSS subsystem under `assets/dialx/`:

- `tokens.css` — colour palette + font stacks
- `type.css` — semantic type roles
- `research.css` — page primitives (sections, hero, tier cards, callouts, tables, pills)

Do not introduce inline `<style>` blocks or per-report CSS overrides. If a layout primitive is missing, extend `research.css` and document the new class.

The structural check in `scripts/check_research_structure.sh` enforces:
- 13 `<section>` elements per report (hero + 12 numbered)
- 3–15 `.rs-callout` elements per report
- Exactly one `<h1>` with exactly one `<em>` inside
- 0–30 `<h3>` elements per report
- No `<div class="rs-container">` wrappers
- No inline `<style>` blocks
- No links to `research-overrides.css`
- Landing has `rs-index-hero` + `rs-posts` with one post per report

Run `bash scripts/check_research_structure.sh` before opening a PR.

## Licensing

By contributing, you agree that:

- Content (reports, MD artefacts, design files) is contributed under [CC BY 4.0](LICENSE)
- Code samples (scripts, future runnable artefacts) are contributed under [MIT](LICENSE-CODE)
- You have the right to make the contribution under these terms (i.e., not encumbered by another employer's IP claim)

If your employer requires a CLA or has open-source contribution restrictions, please open an issue first so we can discuss.

## What this series is NOT

See [`ABOUT.md`](ABOUT.md). Short version: not academic research, not vendor benchmarks, not an official EPAM publication. Practitioner engineering memos with stated scope, published independently.

## Code of conduct

Be excellent to each other. Disagreements about methodology are good; bring them as issues with the specific re-measurement that would settle the question. Personal attacks, harassment, or off-topic spam will be moderated.

## Companion projects

See [COMPANION-REPOS.md](COMPANION-REPOS.md).
