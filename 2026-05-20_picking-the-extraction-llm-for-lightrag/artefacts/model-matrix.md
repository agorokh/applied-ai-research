# Model matrix

The eleven model rows measured against the 20-document smoke corpus and 24-cell rubric. Sorted by smoke pass count.

## Headline matrix

| Rank | Model | Provider / runtime | Ent / doc | Rel / doc | Rel / ent | Smoke (pass / marg / fail) | Notes |
|---:|---|---|---:|---:|---:|---|---|
| 1 | **Gemini 2.5 Flash** | Google via OpenRouter (Apr); routed differently in current production (see footnote) | 82.5 | 95.0 | 1.15 | **24 / 0 / 0** | Clean pass on the 20-doc smoke. Validated on a separate 482-document legal corpus where it scored 23/24 on a stricter rubric and produced 39.8 ent/doc, 56.9 rel/doc, 1.43 rel/ent (lower breadth, higher density than the smoke). Production answer for this report. |
| 2 | Gemini 3.1 flash-lite preview | Google via OpenRouter | 19.6 | 23.3 | 1.19 | 22 / 1 / 1 | Newer Gemini line extracts more conservatively; loses cells on breadth queries. Missed the canary-token cell. |
| 3 | Claude Sonnet 4.6 | Anthropic via OpenRouter | 40.8 | 58.4 | 1.43 | 22 / 0 / 2 (eff 24 / 0 / 0) | Two fails recover to pass under marginal-aware scoring. ~30x to 33x Gemini Flash's cost at parity. |
| 4 | Gemini 3 flash preview | Google via OpenRouter | 34.0 | 40.0 | 1.18 | 21 / 3 / 0 | More expensive than 2.5 and worse on the rubric. |
| 5 | OpenAI gpt-4o-mini | OpenAI via OpenRouter | 17.1 | 17.8 | 1.04 | 19 / 3 / 2 | The implicit LightRAG default. Loses cross-file synthesis. Cheapest of the commercial cluster. Density numbers come from a 150-doc full-corpus run (the larger baseline that motivated the 20-doc smoke for the other rows). |
| 6 | Llama 3.2 3B Q4 | Ollama, consumer GPU | 17.4 | 6.0 | 0.34 | 11 / 13 / 0 | 518 schema-violation warnings on 20 docs. Most relation output dropped by parser. |
| 7 | Qwen 3.5 4B (no-think) | Ollama, consumer GPU | 53.3 | 34.2 | 0.64 | 8 / 4 / 12 | High entity count for a small model; low rel/ent indicates weak relation extraction. |
| 8 | Qwen 2.5 14B GGUF Q4_K_M | LM Studio llama.cpp, M1 Max (32 GB) | 21.9 | 19.7 | 0.90 | 5 / 4 / 15 | Best local result. 19/20 documents in ~4 hours. |
| 9 | Gemma 4 26B Q4 | Ollama, consumer GPU (6 GB VRAM) | aborted | aborted | aborted | timeout on chunk 1 | Thinking-mode tokens push every call past worker timeout. |
| 10 | Qwen 2.5 32B Q4 | Ollama, consumer GPU | partial | partial | partial | HTTP 502 cascade | Out of VRAM, repeated load/unload cascade. |
| 11 | Qwen 2.5 14B 4-bit MLX | LM Studio MLX, M1 Max | partial | partial | partial | embed cascade abort | MLX backend interacted poorly with concurrent embedder calls. |

## Pending rows (projected, not measured)

The following models were costed in the cost-model artefact but never run. Their absence is not evidence about their quality.

| Model | Why not run | Where projected |
|---|---|---|
| Claude Haiku 4.5 | Released after the matrix locked. Projected cheaper than Sonnet 4.6 but more expensive than Gemini Flash. | Cost model. |
| Gemini 2.5 Pro | Projected more expensive than Gemini Flash with uncertain quality delta on this task. | Cost model. |
| GPT-4.1, GPT-4.1 mini | Projected on cost basis only. | Cost model. |
| DeepSeek V3 | Projected on cost basis only. | Cost model. |
| Mistral Large 2 | Projected on cost basis only. | Cost model. |

## Reading the columns

- **Ent / doc**: average entities extracted per document across the 20-document corpus. Direct count from the resulting graph.
- **Rel / doc**: average relations extracted per document. Same.
- **Rel / ent**: relation-to-entity ratio. A diagnostic, not an optimisation target. High ratio plus low absolute entity count indicates a dense small graph; low ratio plus high absolute entity count indicates a wide sparse graph that traverses better on this corpus.
- **Smoke**: pass / marginal / fail counts across 24 cells (6 canary queries x 4 retrieval modes). "Effective" pass count counts marginals as passes when a follow-up traversal would surface the expected reference; this is the more generous read.
- **Notes**: failure mode if applicable, or the specific reason this row is interesting.

## Cross-corpus comparison for the production answer

Same model (Gemini 2.5 Flash), same chunking, three corpora:

| Corpus | Doc count | Ent / doc | Rel / doc | Rel / ent | Smoke / rubric |
|---|---:|---:|---:|---:|---|
| 20-doc smoke corpus (knowledge base, April) | 20 | 82.5 | 95.0 | 1.15 | 24 / 24 |
| 482-document legal corpus (April production validation) | 482 | 39.8 | 56.9 | 1.43 | 23 / 24 on a stricter rubric |
| 17-document working corpus (May, partial re-ingest) | 17 | 59.9 | 66.3 | 1.11 | not run as rubric; live workspace |

The breadth ranking (Flash > Sonnet > others) holds on every corpus. The absolute entity-per-document number varies by roughly a factor of two. This is the report's headline caveat: project the rankings, not the magnitudes.

## Provider routing note

The April matrix above was run with all commercial rows ingested via OpenRouter. The operator's current production stack routes Gemini 2.5 Flash through an enterprise gateway over Tailscale for the primary working workspace, and still uses OpenRouter for the legal-corpus workspace. The pricing ratios in the cost-model artefact derive from public list prices and survive the routing change; the per-call latency and the per-day quota shape differ between OpenRouter and the enterprise gateway and would warrant their own measurement on whichever path you deploy.

## Sources

All commercial rows ingested via OpenRouter at run time (April 2026). All local rows ingested via Ollama or LM Studio on operator-owned hardware (M1 Max and a consumer GPU). Raw smoke transcripts and ingest logs are in the operator's vault under `docs/01_Vault/AgentFactory/02_Investigations/tier3-extraction-llm-benchmark-paper-2026-04-28.md` and adjacent companion notes. The 17-document live data point comes from the running LightRAG instance on the operator's M2 Pro at the time of writing.
