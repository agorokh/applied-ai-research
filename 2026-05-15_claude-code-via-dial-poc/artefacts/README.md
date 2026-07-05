# Artefacts — Claude Code via EPAM DIAL · POC report

Supporting MD artefacts for the [POC report](../). Each file is linked inline from the report at the point it appears.

## Index

| File | Used by report at | Purpose |
|------|-------------------|---------|
| [`methodology.md`](methodology.md) | §02 (bridge), §03 (matrix), §04 (data plane) | Test-design shapes, the 8-task portfolio classification (without the held-out prompts), Bedrock costing formula, harness invocation pattern. |
| [`claims.md`](claims.md) | §01 (findings), §03 (table), §11 (caveats) | Claims ledger — every headline finding tagged as `measured` / `inferred` / `hypothetical` / `recommendation` with an evidence pointer. |
| [`invalidation.md`](invalidation.md) | §11 (caveats), §12 (closing) | "What would falsify this finding" — the specific re-measurements that would invert each headline. |
| [`pricing-snapshot/bedrock-us-east-ohio-2026-05-14.md`](pricing-snapshot/bedrock-us-east-ohio-2026-05-14.md) | §03 (matrix), §11 (caveats) | AWS Bedrock list-price rates transcribed from the pricing console, with Wayback URL for archival. |
| [`telemetry-schema.md`](telemetry-schema.md) | §04 (data plane), §05 (telemetry layers) | The ~30 GFLog fields and the Layer A / B / C categorisation. |

## What is intentionally NOT here

- The actual T1–T8 task prompts and hidden `pytest` validators. Publishing them contaminates any future re-run against the same harness; the held-out set is the fair-fixture property.
- Per-trial cost log records. Tied to a specific engineer / project key / InfluxDB instance; would also expose DIAL contract pricing if cross-referenced with the public Bedrock rates.
- Per-task raw judge transcripts. Provider ToS + bloat.

What the report claims and what these artefacts back up is everything that does not require the held-out fixture to verify — the adapter is openly published (see Companion repository below).

## Companion repository

The Anthropic↔OpenAI translation adapter referenced throughout the report is open-source at **[https://github.com/agorokh/sdlc-dial-adapter](https://github.com/agorokh/sdlc-dial-adapter)**. The methodology document's §5 ("Adapter conformance") describes the wire contract; the linked repository is the reference implementation. The next iteration of the adapter will ship in the same repository alongside the follow-on research.

## License

Same as the report: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
