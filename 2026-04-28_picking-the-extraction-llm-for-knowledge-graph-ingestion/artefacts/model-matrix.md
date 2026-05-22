# Model matrix

The eleven model rows measured against the 20-document smoke corpus and 24-cell rubric. Sorted by smoke pass count.

## Headline matrix

| Rank | Model | Provider / runtime | Ent / doc | Rel / doc | Rel / ent | Smoke (pass / marg / fail) | Notes |
|---:|---|---|---:|---:|---:|---|---|
| 1 | **Gemini 2.5 Flash** | Google via OpenRouter | 82.5 | 95.0 | 1.15 | **24 / 0 / 0** | Clean pass on the 20-doc smoke. Validated on a separate 482-document legal corpus where it scored 23/24 on a stricter rubric and produced 39.8 ent/doc, 56.9 rel/doc, 1.43 rel/ent (lower breadth, higher density than the smoke). Production answer for this report. |
| 2 | Gemini 3.1 flash-lite preview | Google via OpenRouter | 19.6 | 23.3 | 1.19 | 22 / 1 / 1 | Newer Gemini line extracts more conservatively; loses cells on breadth queries. Missed the canary-token cell. |
| 3 | Claude Sonnet 4.6 | Anthropic via OpenRouter | 40.8 | 58.4 | 1.43 | 22 / 0 / 2 | Two fail cells; does not clear the rubric at strict pass count. ~30x to 33x Gemini Flash's measured invoice ratio. |
| 4 | Gemini 3 flash preview | Google via OpenRouter | 34.0 | 40.0 | 1.18 | 21 / 3 / 0 | More expensive than 2.5 and worse on the rubric. |
| 5 | OpenAI gpt-4o-mini | OpenAI via OpenRouter | n/a | n/a | n/a | 19 / 3 / 2 | The implicit LightRAG default. Loses cross-file synthesis. Cheapest of the commercial cluster. Ent/rel/doc not shown: density was measured on a separate 150-document baseline, not the 20-doc smoke corpus used for every other row. |
| 6 | Llama 3.2 3B Q4 | Ollama, consumer GPU | 17.4 | 6.0 | 0.34 | 11 / 13 / 0 | 518 schema-violation warnings on 20 docs. Most relation output dropped by parser. |
| 7 | Qwen 3.5 4B (no-think) | Ollama, consumer GPU | 53.3 | 34.2 | 0.64 | 8 / 4 / 12 | Highest smoke pass count among structurally usable local graphs (Llama 3.2 3B logged 11/13/0 but parser-dropped most relations). High entity count for a small model; low rel/ent indicates weak relation extraction. |

## Local rows attempted but not comparable

These local candidates were attempted on consumer-class GPU (6 GB VRAM) and 32 GB Apple Silicon hardware tiers but did not complete the 20-document smoke corpus, and so are not cross-comparable to the ranked rows above. They are recorded for completeness only; they are not data points in the matrix.

| Model | Hardware tier | Why it did not complete |
|---|---|---|
| Qwen 2.5 14B GGUF Q4_K_M | 32 GB Apple Silicon | Mid-size GGUF on Apple Silicon at this memory tier did not finish the 20-document corpus within a default worker-timeout shape. |
| Gemma 4 26B Q4 | Consumer-class GPU | 26B-class thinking-mode emits an internal monologue per chunk that exceeds the per-chunk worker timeout. |
| Qwen 2.5 32B Q4 | Consumer-class GPU | 32B-class does not fit in 6 GB VRAM at any quantisation that preserves the schema-emission quality required by the parser. |
| Qwen 2.5 14B 4-bit MLX | 32 GB Apple Silicon | MLX backend collided with concurrent embedder calls when co-located on the same host. |

## Pending rows (not measured in this report)

The following models were scoped as candidates for a future matrix extension but were never run. They are not costed in the current [`cost-model.md`](cost-model.md) artefact (which covers only the five rows in its table). Their absence is not evidence about their quality.

| Model | Why not run |
|---|---|
| Claude Haiku 4.5 | Released after the matrix locked. |
| Gemini 2.5 Pro | Deferred; uncertain quality delta on this task versus Gemini 2.5 Flash. |
| GPT-4.1, GPT-4.1 mini | Deferred. |
| DeepSeek V3 | Deferred. |
| Mistral Large 2 | Deferred. |

## Reading the columns

- **Ent / doc**: average entities extracted per document across the 20-document corpus. Direct count from the resulting graph.
- **Rel / doc**: average relations extracted per document. Same.
- **Rel / ent**: relation-to-entity ratio. A diagnostic, not an optimisation target. High ratio plus low absolute entity count indicates a dense small graph; low ratio plus high absolute entity count indicates a wide sparse graph that traverses better on this corpus.
- **Smoke**: pass / marginal / fail counts across 24 cells (6 canary queries x 4 retrieval modes). "Effective" pass count counts marginals as passes when a follow-up traversal would surface the expected reference; this is the more generous read.
- **Notes**: failure mode if applicable, or the specific reason this row is interesting.

## Cross-corpus comparison for the production answer

Same model (Gemini 2.5 Flash), same chunking, two corpora:

| Corpus | Doc count | Ent / doc | Rel / doc | Rel / ent | Smoke / rubric |
|---|---:|---:|---:|---:|---|
| 20-doc smoke corpus (knowledge base) | 20 | 82.5 | 95.0 | 1.15 | 24 / 24 |
| 482-document legal corpus (production validation) | 482 | 39.8 | 56.9 | 1.43 | 23 / 24 on a stricter rubric |

The breadth ranking (Flash > Sonnet > others) holds on both corpora. The absolute entity-per-document number varies by roughly a factor of two. Project the rankings, not the magnitudes.

## Sources

All commercial rows ingested via OpenRouter at run time. All local rows ingested via Ollama or LM Studio on consumer-class GPU and 32 GB Apple Silicon hardware tiers. Raw smoke transcripts and ingest logs are not published because the surrounding corpus contains non-public material; the rubric file is the reusable artefact.
