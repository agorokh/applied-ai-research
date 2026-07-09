# Artefacts — Choosing memory for enterprise agents

Supporting MD artefacts for the [memory-substrate report](../). Each file is linked inline from the report at the point it appears.

## Index

| File | Used by report at | Purpose |
|------|-------------------|---------|
| [`methodology.md`](methodology.md) | §03 (adoption bar), §04 (test design), §05 (headline result), §11 (scope) | Paired-question + position-swap fixture, 64-question budget, two-judge protocol, pre-registered rule-change threshold, frequency-weighting derivation. |
| [`claims.md`](claims.md) | §01 (findings), §05, §06, §07, §11 | Claims ledger — every headline tagged `measured` / `inferred` / `hypothetical` / `recommendation`. |
| [`invalidation.md`](invalidation.md) | §11 (scope), §12 (closing) | "What would falsify this finding" — per-headline Popperian commitments. |
| [`adoption-bar.md`](adoption-bar.md) | §03, §08 (Tencent scorecard) | The five-criterion bar in standalone form, plus the Tencent scorecard re-rendered as a reusable rubric. |
| [`task-families.md`](task-families.md) | §04 (test design), §05 (headline result) | The 8 task-family classification and the production-weight derivation. |
| [`canary-harness/README.md`](canary-harness/README.md) | §11 (closing pointer), §12 (durable artefact claim) | The canary harness shape: paired-question protocol, fixture format, scoring rubric. **Honours the §11 promise that the harness is the durable artefact published with the report.** |
| [`canary-harness/schema.md`](canary-harness/schema.md) | same | JSONL input/output schema for the paired-question fixture. |
| [`canary-harness/example-fixture.jsonl`](canary-harness/example-fixture.jsonl) | same | 2–3 neutral-domain example paired questions to make the schema concrete. |

## What is intentionally NOT here

- The 64 real paired questions from the SDLC corpus. They encode internal project nouns (repo names, ADR titles, system names). The `example-fixture.jsonl` shows the *shape* on a neutral domain instead.
- The actual `pytest`-equivalent validators. The harness is designed to be re-runnable on any corpus; the validators that judged this report are the report's held-out fixture and stay private.
- Judge model raw transcripts. Re-distribution of model outputs may violate provider ToS. Aggregated counts are in the report body.
- Per-trial cost / token records. Specific to this deployment + project key.

Everything that does not require the held-out fixture or per-deployment IDs to verify is here.

## License

Same as the report: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
