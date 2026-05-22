# Production config patterns

The operational discipline behind the report's recommendations. These are not LightRAG defaults; they are choices that emerged from running multiple workspaces in production through the April benchmark and the May drift incident.

The file is split into two parts. **Part A** describes the transferable patterns: choices another operator can adopt independent of their hardware, gateway, or corpus shape. **Part B** records this operator's specific knob values as point-in-time reference: useful as a starting point for sizing your own ingest, not a recommendation to copy verbatim.

---

## Part A: Transferable patterns

## One LightRAG process per workspace

Most operators run a single multi-tenant LightRAG with all workspaces sharing one process. The operator runs one process per workspace, six total at the time of writing, enforced by a fleet-registry flag:

```toml
[lightrag]
require_dedicated_api_per_workspace = true
max_parallel_per_api = 1
```

The reason is per-workspace extractor and embedder choice. A multi-tenant LightRAG with workspace A on Gemini 2.5 Flash and workspace B on Sonnet 4.6 would either (a) need per-call routing logic inside the LightRAG core, or (b) share an LLM cache across the two extractors and silently cross-contaminate the graph. Per-workspace processes make the choice structural: workspace A is one binary with its own env vars, workspace B is another binary with different env vars, the LLM cache is workspace-scoped by virtue of being process-scoped. The cost is a few hundred megabytes of RAM per workspace.

## Per-workspace plist generated from a template

Each workspace's launchd plist is rendered from a template that takes the workspace name and the chosen extractor as parameters. A small Python script reads the workspace declaration and writes the plist; an installer puts it under `~/Library/LaunchAgents/ai.lightrag.<workspace>.plist`. The render plus install is the per-workspace step; copy-pasting another workspace's plist is not.

This is what makes the report's §10 "render deployed extractor config from a templated source" recommendation concrete. Without the renderer the per-workspace step is implicit; with the renderer it is one parameterised invocation. The drift incident in §09 was a hand-edit that bypassed the renderer; the recovery was to re-run the renderer with the correct parameters.

## Backup-on-edit discipline for the plists themselves

When the deployed config changes for any reason (operator edit, recovery action, gateway swap), the previous version is saved alongside the live file with a model-and-date suffix:

```text
ai.lightrag.my-workspace.plist
ai.lightrag.my-workspace.plist.bak.gemini-2026-05-20
ai.lightrag.my-workspace.plist.bak.sonnet-2026-05-20
ai.lightrag.my-workspace.plist.bak.openrouter-2026-05-20
```

This is the auditable trail the §09 drift incident required and did not have at the time. The deployed state is always one diff away from any prior intent, with the model name encoded in the filename so a glance at the directory tells the story.

## Embedder served from a separate host

The embedder runs on a different machine from the extractor, served over Tailscale with its own concurrency budget. This is the resolution to the cascade-fail story in §07: when LightRAG's `EMBEDDING_FUNC_MAX_ASYNC` exceeded LM Studio's `Parallel` setting on the same host, in-flight embedding requests overran worker slots and the LightRAG side amplified the failure on retry. Moving the embedder to a separate host with its own concurrency cap decouples the two failure modes; LightRAG's parallelism setting becomes purely a function of the extractor's throughput, not of the local embedder's worker count.

The same pattern applies to any inference-server pair (Ollama + LM Studio, two LM Studio instances, vLLM + Triton). The decoupling matters more than which servers you use.

## Smoke corpus pinned by explicit file list

The 20-document smoke corpus is pinned in a YAML file by relative path, not selected by directory glob or "first N files." A benchmark that selects files dynamically silently drifts as new files land in the source directory; the matrix is not reproducible against itself across weeks. The file-list discipline is small (a YAML file, a few lines per entry) and the cost of not having it is "we can't tell whether the matrix got worse or the corpus got bigger."

## Canary anchored to expected references, not "did it respond"

The foundation gate's canary check passes a query through the substrate and asserts on:

1. The response does not start with the LLM's empty-retrieval phrase ("no relevant context found" or equivalent, with leading-whitespace tolerance).
2. The response cites at least one expected reference by name.

Both checks are necessary. An empty graph fails the first check because the response begins with the empty-retrieval phrase; it also fails the second check because no real references appear. A healthy graph passes the second check by citing real references; the first check is a fast shortcut when the graph is completely empty. The week's foundation-gate merge that caught the drift incident in §09 was exactly the addition of the second check; before it landed, an empty substrate had been passing canaries that only looked for "did the substrate respond without error."

---

## Part B: This deployment's knob values, point-in-time

The values below are the live config on the test host at the time the report was finalised. They are NOT a transferable recommendation. Document length, chunk count, gateway rate-limit shape, embedder throughput, and the extractor's intrinsic per-call latency all vary; the values that work here will not be the values that work on your hardware against your corpus.

What is worth taking is the shape: small `max_async` (not large), embedder concurrency decoupled from extractor concurrency, LLM cache enabled for extract, merge-summary gated by a chunk threshold rather than always-on. The specific numbers below are starting points to measure against, not endpoints to copy.

### Parallel ingestion settings actually used

For reference, the live production config at the time of writing:

```ini
max_parallel_insert         = 2     # whole-document concurrency in the LightRAG pipeline
max_async                   = 2     # in-flight LLM extraction calls per workspace
embedding_func_max_async    = 8     # in-flight embedding calls (safe because embedder is on a separate host)
embedding_batch_num         = 10    # batch size per embedding call
force_llm_summary_on_merge  = 8     # entity-merge-summary triggers at >=8 chunks per entity
enable_llm_cache_for_extract = true # extraction results cached; near-free re-runs
```

Per-call wall-clock on a real ingest run (Gemini 2.5 Flash via the operator's gateway, 17 short documents averaging 2.6 KB each, 1.4 chunks per document mean): min 82 s, p50 185 s, mean 218 s, p95 762 s. This is per-document, not per-chunk; chunk-normalised, the median call ran in roughly 130 seconds.

These numbers will not generalise. Document length and chunk count vary; the gateway's rate-limit behaviour shapes the upper tail; the extractor's intrinsic per-call latency is a moving target. They are reported here so a reader has a concrete starting point when sizing their own ingest job.
