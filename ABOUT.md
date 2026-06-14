# About this series

## Authorship and editorial independence

Written and published independently by **Arseny Gorokh**, a practitioner at EPAM Applied AI.

**This is not an official EPAM publication.** Reports describe one engineer's stack, one engineer's measurements, and one engineer's deployment decisions. Findings are not contractually binding on EPAM, do not represent EPAM's official position on any vendor or tool named, and have not been through EPAM's formal editorial or legal review process.

Where "EPAM DIAL" is named in the reports, it is named as a **product reference** (DIAL is EPAM's public AI gateway), the same way an AWS-based report would name "AWS Bedrock" without implying AWS sponsorship. EPAM owns the DIAL trademark; this series is unaffiliated commentary that happens to be authored by someone whose day job touches DIAL.

## What kind of research this is

These are **applied AI engineering research notes**, not academic papers, not peer-reviewed work, not controlled benchmarks with public datasets. The intended category is closer to a postmortem or engineering decision memo: real stack, measured trials, cost analysis, failure-mode analysis, caveats, and an adoption recommendation.

The reproducibility discipline the series aims for is:

- State the adoption bar before any candidate is scored.
- Publish the weighting before the aggregate number.
- Name the scope limits as plainly as the headline.
- Cite prior public work where it exists, and call out the gap explicitly when it does not.
- Ship supporting artefacts (methodology, claims ledger, falsification conditions) inside each paper's folder, not as vapor in the prose.

The artefact bundle for each report lives at `<paper-slug>/artefacts/` in this repository.

## Audience

Other practitioners running enterprise AI deployments, platform engineers, applied-AI architects, AI-platform product teams. Not vendor evaluators, not academic readers, not customers being sold to. If you are reading this as a customer of EPAM or any other firm, treat the reports as one engineer's published notes, not as a procurement document.

## How to cite or reference

> Gorokh, A. (2026). *[Note title]*. Applied Intelligence, applied AI research notes. [URL]. CC BY 4.0.

Or just link the report URL directly. The series exists to be discussed and re-measured against on your own stack.

## What invalidates findings

Each report carries an `artefacts/invalidation.md` file naming the specific re-measurement that would falsify the headline finding. If you run that re-measurement and the result inverts, please open an issue, the bar is the durable artefact, the magnitude is workload-specific.

## License

Reports and accompanying MD artefacts: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), share, adapt, attribute. Code samples in the artefacts directories: MIT.

## Contact

GitHub issues on this repository for technical comments, methodology pushback, or proposals for new reports. The author's professional contact is intentionally not the channel for this series.
