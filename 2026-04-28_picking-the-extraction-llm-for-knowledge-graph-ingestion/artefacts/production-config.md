# Production configuration notes

A short list of LightRAG configuration knobs that affect ingest cost, throughput, and graph quality, with the reasoning behind the choice rather than a recommended value. The right values depend on document length, chunk count, the gateway's rate-limit shape, embedder throughput, and the extractor's intrinsic per-call latency. Re-measure on your own deployment.

## Knobs worth setting deliberately

| Knob | What it controls | What to measure before choosing a value |
|---|---|---|
| `max_async` | In-flight LLM extraction calls per workspace | Provider per-minute rate limit and per-call latency variance. A higher value gives throughput up to the rate limit; past it you collect 429s and burn budget on retries. |
| `embedding_func_max_async` | In-flight embedding calls | The embedder server's worker concurrency. If you co-locate the embedder with the extractor on one host, this value must not exceed the embedder server's parallel-worker count, or you collect timeouts. Decoupling the embedder onto its own host removes this constraint. |
| `force_llm_summary_on_merge` | Per-entity merge-summary threshold (entity must appear in N or more chunks before the summary fires) | The per-entity chunk-occurrence distribution on your corpus. Setting it too low triggers a summary call on almost every entity and inflates cost; too high and high-traffic entities never get summarised. |
| `enable_llm_cache_for_extract` | Whether extraction results are cached on disk | Cost of re-ingest under iteration. Cache-on means re-running on the same chunks is near-free; off means every iteration pays full extraction cost. |
| Chunk size and overlap | Per-chunk extraction call shape | Per-call token cost vs entity-coverage trade-off. Larger chunks reduce call count and increase per-call output; smaller chunks increase call count and may improve entity coverage on dense passages. |

## Patterns worth adopting independent of the values above

- **Pin the smoke corpus by explicit file list, not by directory glob.** A benchmark that picks "the first 20 files" silently drifts as new files land in the source directory. Pinning by relative path is small (a YAML file, a few lines per entry) and keeps the matrix reproducible against itself across weeks.
- **Cache extraction results to disk so iteration is cheap.** Iterating on chunk size or extraction prompts is bounded by re-extraction cost; the on-disk cache makes the second iteration on the same chunks effectively free. Disable the cache only when comparing models, since cache hits short-circuit the extractor under test.
- **Match LightRAG's embedder concurrency to the embedder server's parallel-worker count, or decouple them entirely.** Co-located on one host, the two settings must not collide; on separate hosts, the LightRAG side can be tuned purely against extractor throughput.

These are not LightRAG defaults; they are the choices that affect cost, reproducibility, and iteration speed. The defaults are reasonable for a single-corpus experiment; the choices above start to matter when you run the same pipeline across multiple corpora or multiple iterations.

## What is NOT in this artefact

- **Deployment topology.** Whether to run one process per workspace, multi-tenant, or hybrid is an orchestration choice driven by how you partition workspaces, cache policy, and per-workspace billing requirements; it is not an extractor-model finding.
- **Per-call wall-clock numbers.** Latency depends on the provider gateway, the specific network path, the contract-tier per-minute and per-day caps, and the per-call variance the model exhibits on your corpus. Numbers measured on one deployment do not transfer.
- **Config-management hygiene.** Backups, templating, change-detection, alerting on drift are general operational discipline that any deployed system needs, not findings specific to extraction-LLM choice.
