# Contributing

This is a working-drafts series of practitioner research notes. Contributions are welcome from other practitioners working on similar enterprise-AI deployment problems: gateways, memory, agent harnesses, telemetry, evaluation methodology, cost analysis, production adoption.

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

Each note is a single HTML file under `notes/<slug>.html`, built on the Atelier reading style (cover, sticky rail, roughly eight numbered sections, findings, captioned figures, references, colophon). The clearest exemplars are:

- [`notes/value-layer.html`](notes/value-layer.html): a prose-led decision memo
- [`notes/harness-viability.html`](notes/harness-viability.html): a data-heavy empirical note with figures and tables

A note ships its companion material under `artefacts/<slug>/` (or links the relevant companion repository). The reproducibility-grade notes ship:

- `methodology.md`: test design, scoring rubric, aggregation formula, what the methodology is NOT
- `claims.md`: claims ledger (every headline tagged `measured` / `inferred` / `hypothetical` / `recommendation` / `scope`)
- `invalidation.md`: Popperian falsification conditions per finding
- Subject-specific reference files (e.g. `adoption-bar.md`, `task-families.md`, `pricing-snapshot/`, `telemetry-schema.md`, `canary-harness/`)

A new report should ship at least `methodology.md` + `claims.md` + `invalidation.md` alongside the HTML.

## Voice and framing

- **State the adoption bar before the measurement.** A bar applied post-hoc rationalises; a bar applied a priori constrains.
- **Publish the weighting before the score.** Uniform vs production-weighted aggregates often disagree; the disagreement is usually the finding.
- **Name the scope limits as plainly as the headline.** Every report's §11 lists the conditions under which the magnitudes do not transfer.
- **Cite prior public work explicitly.** Call out the gap when none exists.
- **Use "EPAM DIAL" only as a product reference**, never as institutional warrant. See [`ABOUT.md`](ABOUT.md) for the disclaimer language; the mechanical rule is in the v22 council ADR.

## Visual identity

The site uses the Atelier reading style, owned by Claude Design, under `assets/`:

- `theme.css`: the design language (tokens and primitives). **Never edit it.**
- `notes.css`: the shared note stylesheet (cover, rail, sections, findings, figures, tables, colophon). Edit here to change all notes.
- `atelier-figures.js`: the inline-SVG figure renderer (measure / bars / scatter / flow).
- `atelier-rooms.js`: the room background; the publication tier is `data-mood="paper"`.

Every page is set in Newsreader, Schibsted Grotesk, and Spline Sans Mono only. Fonts load from Google Fonts; do not vendor font files.

Before opening a PR, confirm the publication gates hold across every published page:

- Google Analytics tag (`G-HHYGP07F16`) present in every page `<head>`.
- Zero placeholder links: `grep -rn 'href="#"' index.html notes/*.html` returns nothing.
- Zero em or en dashes in published HTML (the house rule is `·`, commas, or "X to Y").
- A `<title>`, a `<meta name="description">`, and a `<link rel="canonical">` on every page.

The note-creation discipline (titling, openings, gates) lives in the `applied-ai-note` skill in the authoring repository.

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
