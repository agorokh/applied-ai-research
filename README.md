# Applied AI Research — practitioner notes

Independent applied-AI engineering notes by [Arseny Gorokh](https://github.com/agorokh), a practitioner at EPAM Applied AI. **Not an official EPAM publication.** Each report takes one frontier or consumer-grade AI capability — memory, agents, gateways, observability — and measures what it takes to make it enterprise-deployable on a real stack.

**Live site:** <https://agorokh.github.io/applied-ai-research/>

Working drafts. Published independently. See [ABOUT.md](ABOUT.md) for the full disclaimer.

**Companion repositories:** [COMPANION-REPOS.md](COMPANION-REPOS.md)

## The series

| Date | Report | Iteration |
|------|--------|-----------|
| 2026-05-19 | [Choosing memory for enterprise agents](https://agorokh.github.io/applied-ai-research/2026-05-19_choosing-memory-for-enterprise-agents/) | 3 |
| 2026-05-15 | [Claude Code via EPAM DIAL · POC report](https://agorokh.github.io/applied-ai-research/2026-05-15_claude-code-via-dial-poc/) | 3 |

## What "applied AI research" means here

Not academic research. Not peer-reviewed. Not a controlled benchmark with a public dataset and reproducible runs. These are **engineering decision memos** based on real stacks, measured trials, cost curves, named failure modes, and deployment constraints — written so another practitioner can re-instantiate the canary on their own corpus rather than rely on a vendor's published number.

The discipline is: state the adoption bar before the measurement, publish the weighting before the score, name the scope limits as plainly as the headline.

## Format

Each report is a single self-contained HTML file in the dialx visual subsystem (Tiempos serif for display, Söhne for body, JetBrains Mono for labels and code, dark palette with violet + magenta accents). Reports are designed to read at 1280px or wider. Each report's folder also contains an `artefacts/` directory with the methodology, claims ledger, falsification conditions, and supporting reference files referenced inline from the report.

## Contributing

Open to issues and pull requests from practitioners working on similar enterprise-AI deployment problems. To propose a report, open an issue with the abstract and the corpus you plan to measure against. The series is independent of any organisation's editorial process; the framing rules in [ABOUT.md](ABOUT.md) apply to any contribution.

## License

Reports and supporting MD artefacts: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code samples: MIT. EPAM DIAL is named throughout as a product reference; EPAM owns its own trademarks.
