# Applied Intelligence: applied AI research notes

Independent applied-AI engineering notes by [Arseny Gorokh](https://github.com/agorokh), a practitioner at EPAM Applied AI. **Not an official EPAM publication.** Each note takes one frontier or consumer-grade AI capability (agent data, open models, telemetry, memory) and measures what it takes to make it enterprise-deployable on a real stack.

**Live site:** <https://agorokh.github.io/applied-ai-research/>

Working drafts. Published independently. See [ABOUT.md](ABOUT.md) for the full disclaimer.

**Companion repositories:** [COMPANION-REPOS.md](COMPANION-REPOS.md)

## The series

| Date | Note | Decision it informs |
|------|------|---------------------|
| 2026-06-13 | [MCP harvesting: trustworthy data when your agent has a connector, not an API](https://agorokh.github.io/applied-ai-research/notes/mcp-harvesting.html) | agent data |
| 2026-06-05 | [A memory-and-policy layer above the model: the build-versus-buy case](https://agorokh.github.io/applied-ai-research/notes/value-layer.html) | agent memory |
| 2026-05-15 | [Claude Code through DIAL: eight models, 192 runs, metering every request](https://agorokh.github.io/applied-ai-research/notes/telemetry-plane.html) | agent telemetry |
| 2026-05-14 | [Which models can run Claude Code through DIAL?](https://agorokh.github.io/applied-ai-research/notes/harness-viability.html) | open models |

## What "applied AI research" means here

Not academic research. Not peer-reviewed. Not a controlled benchmark with a public dataset and reproducible runs. These are **engineering decision memos** based on real stacks, measured trials, cost curves, named failure modes, and deployment constraints, written so another practitioner can re-instantiate the canary on their own corpus rather than rely on a vendor's published number.

The discipline is: state the adoption bar before the measurement, publish the weighting before the score, name the scope limits as plainly as the headline.

## Format

Each note is a single self-contained HTML file under `notes/`, set in the Atelier reading style (Newsreader serif for display, Schibsted Grotesk for body, Spline Sans Mono for labels and code, a warm paper palette with hairline rules). Notes are designed to read at 1280px or wider. Companion material (methodology, claims ledger, falsification conditions, reproducibility artefacts) lives under `artefacts/<slug>/` or in a linked companion repository, referenced inline from the note. The design language is owned by Claude Design; `assets/theme.css` is its tokens and primitives and is never edited by hand.

## Contributing

Open to issues and pull requests from practitioners working on similar enterprise-AI deployment problems. To propose a report, open an issue with the abstract and the corpus you plan to measure against. The series is independent of any organisation's editorial process; the framing rules in [ABOUT.md](ABOUT.md) apply to any contribution.

## License

Reports and supporting MD artefacts: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code samples: MIT. EPAM DIAL is named throughout as a product reference; EPAM owns its own trademarks.
