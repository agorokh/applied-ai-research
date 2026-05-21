# Claims ledger

Every headline claim in the report, tagged by epistemic status.

- **measured**: direct measurement on the 20-document smoke corpus or the 482-document validation corpus.
- **inferred**: extrapolated from measurements but not directly measured.
- **hypothetical**: stated as a model or expectation, not measured.
- **recommendation**: operational advice derived from the measured results.
- **scope**: condition that limits where the magnitudes transfer.

## Findings (§01)

| Tag | Claim | Source |
|---|---|---|
| measured | Gemini 2.5 Flash extracts ~2x more entities and ~1.6x more relations per document than Sonnet 4.6 on the same chunks. | Smoke matrix rows for Gemini 2.5 Flash (82.5 ent/doc, 95.0 rel/doc) vs Sonnet 4.6 (40.8 ent/doc, 58.4 rel/doc). |
| measured | Gemini 2.5 Flash relation-to-entity ratio (1.15) is lower than Sonnet 4.6's (1.43). | Same rows. |
| measured | Gemini 2.5 Flash scored 24/0/0 on the smoke rubric; Sonnet 4.6 scored 22/0/2 with effective 24/0/0 after marginal recovery. | Smoke rubric tabulation. |
| inferred | Breadth of entity index dominates density of relation index for LightRAG's traversal-then-fetch retrieval shape. | Mechanism derivation in §05; consistent with the smoke results but not independently A/B tested by restricting traversal mode. |
| measured | gpt-4o-mini ingests at roughly 20% to 30% of Gemini Flash's list-priced cost but loses smoke cells (19/3/2). | Smoke matrix gpt-4o-mini row; cost model derivation per 100 docs. |
| measured | Sonnet 4.6 ingests at roughly 30x to 33x Gemini Flash's cost at parity quality. | Cost model derivation; published list rates verified at run time. |
| measured | Gemini 3-flash-preview and 3.1-flash-lite-preview both scored below Gemini 2.5 Flash on the smoke rubric. | Smoke rubric rows for Gemini 3 variants (21/3/0 and 22/1/1). |
| measured | Six local open-source trials at two hardware tiers all scored below Gemini 2.5 Flash; best local result (Qwen 2.5 14B GGUF Q4) scored 5/4/15. | Local trial logs; smoke rubric scoring. |

## Method (§03)

| Tag | Claim | Source |
|---|---|---|
| measured | LightRAG default chunking: 1200 tokens, 100 overlap. | Upstream LightRAG paper §4 and default config. |
| measured | LightRAG ingest runs ~2.5 LLM calls per chunk on average (entity extraction + relation extraction + occasional merge-summary). | Upstream pipeline structure plus operator measurement on this corpus. |
| measured | Per chunk on this corpus: ~8K input + ~2K output tokens per LLM call. | Operator measurement during smoke runs. |

## Mechanism (§05)

| Tag | Claim | Source |
|---|---|---|
| inferred | Doubling entity count roughly doubles the surface area the entity index covers, which roughly doubles probability that a query lands on at least one entity per relevant chunk. | Stated as mechanism, not measured directly. Consistent with the measured smoke results. |
| hypothetical | The breadth-over-density pattern generalises to other retrieval-augmented systems that traverse an entity graph (not to systems that score retrieval purely on relation paths). | Stated as expectation; not measured on other systems. |

## Cost (§06)

| Tag | Claim | Source |
|---|---|---|
| measured | Approximate per-100-document ingest cost on this corpus: ~$7 to $10 (Gemini 2.5 Flash, list-derived), ~$54 to $80 (Sonnet 4.6, list-derived), ~$2 to $3 (gpt-4o-mini, list-derived), $0 (local open-source). Sonnet's measured 20-doc invoice ratio vs Gemini Flash is ~30× to ~33×. | Smoke run invoices; per-1M-token list prices applied to measured token counts. |
| inferred | Cost ratios inside the matrix are more stable than absolute magnitudes against contract pricing variation. | Inferred from observation that all commercial rows use the same per-token shape and differ only on price; not independently validated against any specific contract. |

## Open source (§07)

| Tag | Claim | Source |
|---|---|---|
| measured | Llama 3.2 3B Q4 produced 518 schema-violation warnings on 20 documents. | Local trial log. |
| measured | Gemma 4 26B Q4 on consumer GPU timed out on chunk 1. | Local trial log. |
| measured | Qwen 2.5 14B GGUF Q4_K_M on M1 Max (32 GB) completed 19/20 documents in ~4 hours, scored 5/4/15. | Local trial log. |
| recommendation | For local-only corpora, use Qwen 2.5 14B GGUF Q4_K_M in LM Studio on Apple Silicon (32 GB or more) and pair with a separate query-time synthesis model. | Recommendation derived from the local-trial measurements. |

## No-think discipline (§08)

| Tag | Claim | Source |
|---|---|---|
| measured | Some Ollama versions silently ignore `think: false` on `/v1/chat/completions` and honour it only on `/api/chat`. | Operator measurement during Gemma 4 26B and Qwen 3 trials. |
| inferred | Per-call latency increases roughly 5x when reasoning mode is enabled for structured-extraction calls; reasoning tokens are billable as output tokens. | Inferred from per-call wall-clock measurements; specific multiplier varies by model. |
| recommendation | Disable reasoning mode on any extractor that supports it; verify the flag actually disables reasoning end-to-end. | Recommendation from the latency and cost observations. |

## Drift incident (§09)

| Tag | Claim | Source |
|---|---|---|
| measured | A re-ingest at Sonnet 4.6 rates ran to substantial completion before the canary detected retrieval was failing. | Operator's internal incident log (May 2026). |
| measured | The canary instrumentation that caught the drift had itself landed that week; before it existed, an empty substrate was showing green. | Same. |
| recommendation | Anchor the ingest-health canary to expected entities, not "did the substrate respond". | Operational lesson from the incident. |
| recommendation | Diff deployed extractor config against repo template on every cron tick. | Operational lesson from the incident. |

## Scope (§11)

| Tag | Claim | Source |
|---|---|---|
| scope | Results apply to mixed-Markdown corpora with implicit entity types. Different corpus shapes may produce different model rankings. | Stated explicitly; the smoke rubric is reusable on your corpus. |
| scope | Results apply at LightRAG-default chunking (1200/100). | Stated explicitly; re-derive cost if you change chunking. |
| scope | Embedder held constant; results do not control for embedder choice. | Stated explicitly. |
| scope | List prices used for cost ratios. Contract pricing changes absolute magnitudes but typically preserves ranking within the cluster. | Stated explicitly. |
| scope | Breadth-over-density holds for traversal-then-fetch retrieval shape. Systems that score retrieval on multi-hop relation paths may reward density more. | Stated explicitly. |
| scope | Frontier models update frequently; specific named models may behave differently in later versions. | Stated explicitly. |
