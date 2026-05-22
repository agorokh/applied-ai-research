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
| measured | Gemini 2.5 Flash scored 24/0/0 on the smoke rubric; Sonnet 4.6 scored 22/0/2 (two fail cells, zero marginals). | Smoke rubric tabulation. |
| inferred | Breadth of entity index dominates density of relation index for LightRAG's traversal-then-fetch retrieval shape. | Mechanism derivation in §05; consistent with the smoke results but not independently A/B tested by restricting traversal mode. |
| inferred | gpt-4o-mini ingests at roughly 20% to 40% of Gemini Flash's list-priced cost (calculator, not invoice) but loses smoke cells (19/3/2). | Smoke rubric tabulation; cost-model.md list-price derivation per 100 docs. |
| measured | Sonnet 4.6's 20-document smoke ingest invoice was ~30× to ~33× Gemini Flash's invoice (smoke score 22/0/2 in row above). | Smoke run invoices recorded at run time. |
| measured | Gemini 3-flash-preview and 3.1-flash-lite-preview both scored below Gemini 2.5 Flash on the smoke rubric. | Smoke rubric rows for Gemini 3 variants (21/3/0 and 22/1/1). |
| measured | Six local open-source trials at two hardware tiers all scored below Gemini 2.5 Flash; highest smoke pass count among structurally usable local graphs (Qwen 3.5 4B no-think) scored 8/4/12 (Llama 3.2 3B Q4 logged 11/13/0 but parser-dropped most relation output); best M1 Max completion (Qwen 2.5 14B GGUF Q4) scored 5/4/15. | Local trial logs; smoke rubric scoring; model-matrix.md. |

## Method (§03)

| Tag | Claim | Source |
|---|---|---|
| measured | LightRAG default chunking: 1200 tokens, 100 overlap. | Upstream LightRAG paper §4 and default config. |
| inferred | LightRAG ingest runs ~2.5 LLM calls per chunk on average (entity extraction + relation extraction + occasional merge-summary). | Derived from upstream pipeline structure plus observed extraction shape; not directly measured per-call. The 482-document legal corpus closeout reports 1,692 chunks / 482 docs = ~3.5 chunks/doc as a real-corpus data point. |
| inferred | Per chunk on this corpus: ~8K input + ~2K output tokens per LLM call. | Estimated from chunk size plus typical extraction-prompt overhead; not directly measured against the LLM-cache JSON. Label as estimate in cost-model.md. |

## Mechanism (§05)

| Tag | Claim | Source |
|---|---|---|
| inferred | Doubling entity count roughly doubles the surface area the entity index covers, which roughly doubles probability that a query lands on at least one entity per relevant chunk. | Stated as mechanism, not measured directly. Consistent with the measured smoke results. |
| hypothetical | The breadth-over-density pattern generalises to other retrieval-augmented systems that traverse an entity graph (not to systems that score retrieval purely on relation paths). | Stated as expectation; not measured on other systems. |

## Cost (§06)

| Tag | Claim | Source |
|---|---|---|
| inferred | Approximate per-100-document ingest cost on this corpus (list-price calculator from estimated token counts, not invoice logs): ~$7 to $10 (Gemini 2.5 Flash), ~$54 to $69 (Sonnet 4.6, with gleaning uplift), ~$2 to $3 (gpt-4o-mini), $0 (local open-source). | cost-model.md; methodology §03 token estimates. |
| measured | Sonnet's 20-document smoke ingest invoice was ~30× to ~33× Gemini Flash's invoice on the same corpus. | Smoke run invoices recorded at run time. |
| inferred | Cost ratios inside the matrix are more stable than absolute magnitudes against contract pricing variation. | Inferred from observation that all commercial rows use the same per-token shape and differ only on price; not independently validated against any specific contract. |

## Open source (§07)

| Tag | Claim | Source |
|---|---|---|
| measured | Llama 3.2 3B Q4 produced hundreds of schema-violation warnings on the 20-document corpus, with most extracted relations dropped by LightRAG's parser. | Local trial log. (Earlier vault notes cite a specific count of 518; the report body uses the softer phrasing pending re-verification of the raw counter.) |
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
| measured | The canary instrumentation that caught the drift had itself landed that week; before it existed, an empty substrate was showing green. | Same; the foundation-gate merge that added expected-reference assertion. |
| recommendation | Anchor the ingest-health canary to expected entities, not "did the substrate respond". | Operational lesson; implemented as the dual check in production-config.md. |
| recommendation | Render deployed extractor config from a templated source; alarm on divergence between deployed file and rendered template. | Operational lesson; see production-config.md for the renderer pattern. |
| recommendation | Save backup-on-edit with model-tagged filenames for every plist edit. | Operational lesson; see production-config.md. |

## Production config (production-config.md)

| Tag | Claim | Source |
|---|---|---|
| measured | Deployed config at time of writing: `max_parallel_insert=2`, `max_async=2`, `embedding_func_max_async=8`, `embedding_batch_num=10`, `force_llm_summary_on_merge=8`. | LightRAG `/health` endpoint on the test host. |
| measured | Per-document wall-clock on a recent run (Gemini 2.5 Flash, 17 short documents averaging 2.6 KB, 1.4 chunks per document mean): min 82s, p50 185s, mean 218s, p95 762s. | Doc-status JSON exported from the test host during a partial re-ingest. |
| measured | A working-corpus graph at a partial-ingest checkpoint (Gemini 2.5 Flash, 17 documents processed): 1,019 entities, 1,127 relations, 59.9 ent/doc, 66.3 rel/doc, 1.11 rel/ent. | `vdb_entities.json` / `vdb_relationships.json` on the test host. |
| measured | The fleet registry enforces `require_dedicated_api_per_workspace = true`, one process per workspace. | The operator's fleet-registry configuration file. |
| measured | A developer-tier Gemini Flash daily quota of 2,000,000 tokens was exhausted during the partial re-ingest cited above, leaving the remaining documents queued. | 429 response from the gateway during the run. |
| recommendation | For full re-ingest workloads, plan for higher-tier pricing or stagger ingest across days. | Operational lesson from the daily-cap incident. |

## Scope (§11)

| Tag | Claim | Source |
|---|---|---|
| scope | Results apply to mixed-Markdown corpora with implicit entity types. Different corpus shapes may produce different model rankings. | Stated explicitly; the smoke rubric is reusable on your corpus. |
| scope | The 82.5 entities per document headline is corpus-specific. Same model and chunking measured 39.8 ent/doc on a 482-document legal corpus and 59.9 ent/doc on a 17-document partial re-ingest. The breadth ranking (Flash > Sonnet > others) held in every case; the absolute magnitudes vary by ~2x. | Cross-corpus comparison in model-matrix.md. |
| scope | Results apply at LightRAG-default chunking (1200/100). | Stated explicitly; re-derive cost if you change chunking. |
| scope | Embedder held constant; results do not control for embedder choice. | Stated explicitly. |
| scope | List prices used for cost ratios. Contract pricing changes absolute magnitudes but typically preserves ranking within the cluster. | Stated explicitly. |
| scope | Breadth-over-density holds for traversal-then-fetch retrieval shape. Systems that score retrieval on multi-hop relation paths may reward density more. | Stated explicitly. |
| scope | Frontier models update frequently; specific named models may behave differently in later versions. | Stated explicitly. |
