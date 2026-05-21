# Artefacts

Companion material to [`../index.html`](../index.html). Each artefact stands on its own; the report cites them inline.

| File | Purpose |
|---|---|
| [`methodology.md`](methodology.md) | Test design: corpus, chunking, smoke rubric, embedder, what the method does not measure. |
| [`claims.md`](claims.md) | Every headline claim in the report, tagged measured / inferred / hypothetical / recommendation / scope, with the supporting evidence. |
| [`invalidation.md`](invalidation.md) | Falsification conditions: what re-measurement would invalidate each finding. |
| [`model-matrix.md`](model-matrix.md) | The full eleven-row table with provider, runtime, raw counts, smoke score, per-row notes, and a cross-corpus comparison for the production answer. |
| [`cost-model.md`](cost-model.md) | Per-100-document cost derivation. Token accounting (estimated, not invoice-measured), list-price multiplication, the ratios that survive contract pricing. |
| [`production-config.md`](production-config.md) | Operational discipline: one process per workspace, plist rendered from template, backup-on-edit, embedder on separate host, smoke-corpus pinned by file list, canary anchored to expected references, parallel-ingest settings used in practice. |
| [`smoke-rubric/`](smoke-rubric/) | The reusable rubric apparatus. Protocol (6 query shapes × 4 retrieval modes), YAML schema for your own canary file, and an example fixture on a neutral domain (Linux kernel scheduler) you can use to validate a harness implementation before pointing it at your real corpus. |

## Scope of measurement

The eleven model rows were measured on LightRAG specifically, as the canonical open-source implementation of the knowledge-graph RAG class. The findings about extractor breadth, the cost ratios at scale, and the failure modes of small open-source extractors should generalise to other systems in the same class (Microsoft GraphRAG, Neo4j vector-plus-graph setups, similar ingestion pipelines). The absolute entity counts and the per-pipeline cost numbers depend on prompt templates, gleaning aggressiveness, and chunking defaults that differ across implementations. Re-derive on yours before treating the magnitudes as portable.

## Report shell layout (static HTML)

Each report is a standalone `index.html` under its dated folder. Hero metadata (read time, KPI tiles, artefact footer links) intentionally duplicates patterns from the site landing page because these pages ship as static files without a build step. When adding a fourth report, copy the shell from the most recent report and update: `<title>`, hero KPIs, section count, artefact paths, and the landing-page card in [`../../index.html`](../../index.html). A shared template would reduce drift but is out of scope for this PR; the checklist above is the sync contract.

## How to reproduce

The smoke rubric is the reusable apparatus. Re-instantiate it on your own corpus and your own pipeline before committing to a default extractor:

1. Pick 20 documents that match the shape of your production corpus (mixed prose plus structured notes worked here; pick what is representative of yours).
2. Pin them in a list file so the same files are ingested for every model row.
3. Write six canary queries that match real questions your retrieval would receive. For each query, name the document or section that should appear in the returned chunks.
4. For every model you evaluate, ingest the same 20 documents with the same chunking and embedder, then run each canary query in each of LightRAG's four retrieval modes (24 cells total per model).
5. Score each cell pass / marginal / fail against the expected reference.
6. Tabulate entities per document, relations per document, smoke score, and measured cost on the 20-document subset.

The rubric is small enough to live in a repo alongside the model matrix. Re-run it whenever a new model lands or your corpus shape changes.

## Companion reports

- [Choosing memory for enterprise agents](../../2026-05-19_choosing-memory-for-enterprise-agents/) (the substrate question; this report answers the immediately downstream extractor question).
- [Claude Code via EPAM DIAL POC](../../2026-05-15_claude-code-via-dial-poc/) (the inference-routing question; orthogonal to extractor choice but the same operator-tier discipline).
