# Methodology

## Question

Which LLM should a knowledge-graph RAG system (the class that includes Microsoft GraphRAG, LightRAG, and similar pipelines) use as its entity and relation extractor during ingestion, on a coding-orchestration and knowledge-base corpus class, evaluated against a fixed retrieval-acceptance rubric. Measurements run on LightRAG specifically as the representative implementation.

## Variable under study

The extractor LLM only. Five things were held constant across all eleven model rows.

| Held constant | Value | Why |
|---|---|---|
| Corpus | 20 documents, pinned by file list | Same chunks for every model so extraction differences are not confounded by content differences. |
| Chunking | 1200 tokens, 100 token overlap (LightRAG defaults) | Default to the system's own published defaults so reproducers do not need to change config. |
| Embedder | `text-embedding-mxbai-embed-large-v1` (1024-dim, local via LM Studio) | Held constant so changes in retrieval quality reflect extractor differences, not embedder differences. |
| Smoke rubric | 6 canary queries x 4 retrieval modes = 24 cells | Defined before any model ran. Pass / marginal / fail per cell against named expected reference. |
| Reporting columns | entities per doc, relations per doc, rel/ent ratio, smoke score, measured cost on 20-doc subset | Fixed columns prevent the "interesting metric" cherry-pick after the run. |

## Corpus

Two corpora.

- **Smoke corpus.** 20 documents drawn from a curated knowledge-base corpus. Mixed prose plus structured notes, average roughly 5 pages each. Implicit entity types: people, projects, decisions, dates, concepts. Pinned by file list so every model ingests the same 20 files in the same order.
- **Production-class validation corpus.** 482 documents from a legal-domain corpus (specific identity withheld for sensitivity reasons). Used only to validate the smoke-rubric winner before locking it as production default. Not used to score every model; running 11 ingest runs on a 482-doc corpus would have cost roughly 25 times what the smoke corpus cost.

## Smoke rubric

Six canary queries chosen before any model ran. Each query has a documented expected reference (the file or section that should appear in the returned chunks). Each query runs in all four LightRAG retrieval modes:

| Mode | What it does |
|---|---|
| `naive` | Pure vector similarity. No graph traversal. |
| `local` | Entity neighbourhood traversal, single hop. |
| `global` | Whole-graph traversal with relation paths. |
| `hybrid` | Local plus global, merged. |

Six queries x four modes = 24 cells per model. Each cell is scored:

- **pass**: returned chunks include the expected reference.
- **marginal**: returned chunks include related but not exact reference, or the expected reference appears further down the ranking than expected.
- **fail**: expected reference absent from returned chunks.

Scoring is a single human evaluator looking at returned chunks against the rubric. Not a separate LLM judge. The smoke rubric is small enough (24 cells x 11 models = 264 calls) that human scoring was tractable.

## Cost measurement

Cost on the smoke corpus is the invoice-level cost from the provider (OpenRouter for all commercial rows, zero-cost for all local rows). Per-1M-token list prices used in the cost-model artefact are public rate cards verified at run time.

The per-100-document derivation in [`cost-model.md`](cost-model.md) multiplies estimated token-per-document (derived from chunk size and observed extraction shape, not invoice token logs) by published list price, then projects to 100 documents. It does not include amortised infrastructure cost (LM Studio host, local GPU power), gateway markup, or contract-pricing adjustments.

## What this method does not measure

- **End-to-end retrieval quality on the full production corpus.** The smoke rubric is a fast acceptance gate. The 482-document validation corpus tested the winner only; eleven full validations were not run.
- **Latency or throughput at scale.** Suitable for batch ingest, not streaming workloads. A streaming ingest study would have different binding constraints (steady-state TPS, per-call p99 latency, queue backpressure).
- **Sensitivity to chunk size or embedder choice.** Both held constant on purpose; varying them would warrant separate studies.
- **Long-tail commercial models.** Several frontier models were scoped as candidates but never run (Claude Haiku 4.5, Gemini 2.5 Pro, GPT-4.1, DeepSeek V3, Mistral Large 2). They are listed in the pending-rows table in [`model-matrix.md`](model-matrix.md), not costed in [`cost-model.md`](cost-model.md).
- **Cross-corpus generalisation.** The smoke corpus is mixed Markdown notes with implicit entity types. Different corpus shapes may produce different model rankings; the scope section in the main report names which axes likely shift the ranking.

## Provenance

The eleven model runs were executed late April 2026 with extensions in early May 2026 (the Gemini 3.x variants). The drift incident described in §09 happened mid-May 2026 and is documented separately in the operator's internal investigation log; it is referenced here as the operational lesson, not as a data point in the matrix.

Original ingest logs, per-cell smoke transcripts, and the estimated token counts that feed the cost model are held in an internal investigation log. They are not published verbatim because they contain corpus content from non-public workspaces. Re-running the rubric on your own corpus is the reproducibility path; the rubric itself is the reusable artefact.
