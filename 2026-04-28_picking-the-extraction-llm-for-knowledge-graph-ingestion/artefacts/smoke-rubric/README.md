# Smoke rubric for extraction-LLM evaluation

The [report](../../) names this rubric in §03 and uses it as the dependent variable for every model row in the matrix. This directory ships the rubric shape so another practitioner can re-instantiate it on their own corpus and produce a comparable matrix in a day or two.

The operator's specific 6 canary queries are not published verbatim because they reference personal-corpus content. What is published is the **rubric protocol**, the **query shapes** that cover the failure modes the matrix is actually sensitive to, the **scoring rules**, and an **example fixture** on a neutral domain (the Wikipedia article on the Linux kernel scheduler) that a reader can use to validate a harness implementation before running it on their own corpus.

## Honest limitations of this rubric

This is a fast acceptance gate, not a full benchmark. Three things it does not do, called out so a reader knows what they are inheriting.

1. **Single human evaluator.** The operator scored all 264 cells (11 models × 24 cells) personally. There is no inter-rater check against a second scorer or a second pass after a cooling-off period. The 24-vs-22 distinctions that drive the headline ranking sit inside one person's judgement. Two of the models in the matrix recover from `fail` to `pass` under a softer scoring read; the report flags this honestly in §01.
2. **No LLM-as-judge cross-check.** The companion memory-substrate report uses two LLM judges from different model families with position-swap ordering. This rubric does not, because the scoring task here (does the retrieval return the expected reference?) is binary enough that LLM judging adds noise without adding rigor. That judgement is itself a judgement and may be wrong; a measurement replicator who wants to test it should re-score N rows with an LLM judge and report agreement.
3. **The rubric is sensitive to the canary set.** Six queries is a small sample. If your corpus has a different topic distribution than the operator's (which is mostly mixed-prose Markdown notes on people, projects, decisions, dates), your six queries will look different and your ranking may shift. Rerun before generalising.

## What's here

| File | Purpose |
|---|---|
| [`README.md`](README.md) | This file. Protocol description plus the six query shapes the operator's canary set covers. |
| [`schema.md`](schema.md) | YAML schema for your own canary file plus the scoring spreadsheet shape. |
| [`example-fixture.yml`](example-fixture.yml) | 6 example queries on a neutral domain (Linux kernel scheduler Wikipedia article) so you can validate a harness against your LightRAG (or other knowledge-graph RAG) deployment before running on your real corpus. |

## The protocol

For each candidate extraction LLM:

1. **Ingest** the pinned 20-document corpus through your chosen knowledge-graph RAG pipeline (LightRAG, Microsoft GraphRAG, etc.) with that LLM as the extractor. Hold chunking, embedder, and retrieval config constant across all candidate models.
2. **Query** the resulting substrate with each of the 6 canary queries, in each of the 4 retrieval modes the pipeline exposes (LightRAG uses `naive`, `local`, `global`, `hybrid`; substitute the equivalent for your pipeline).
3. **Score** each of the 24 cells (6 queries × 4 modes) as one of three outcomes:
   - `pass`: returned context names the expected reference exactly or paraphrases it recognisably.
   - `marginal`: returned context contains related material from the expected reference's section but does not name it directly, OR the expected reference appears further down the ranked context list than expected.
   - `fail`: returned context does not include the expected reference at all.
4. **Tabulate** as a `pass / marginal / fail` triple per model. A clean 24/0/0 is the production-ready ceiling; anything below it needs §07-style triage on the specific failures.
5. **Record** entities-per-document and relations-per-document from the resulting graph so the report's breadth-vs-density discussion is reproducible.

## The six query shapes

Six queries chosen before any model ran. Each tests a different failure surface of the extractor.

| # | Shape | What it tests | What failure looks like |
|---|---|---|---|
| 1 | **Single-entity recall.** "What does the corpus say about X" where X is a specific entity that appears in exactly one document. | Whether the extractor noticed X at all and indexed it as a queryable entity. | gpt-4o-mini class models silently skip low-frequency entities and the query returns nothing or returns unrelated chunks. |
| 2 | **Cross-document synthesis.** "What is the relationship between A and B" where A and B appear in separate documents that are conceptually linked. | Whether the extractor's relation graph is wide enough to connect the two without a multi-hop traversal. | Low-breadth extractors put A and B in disconnected subgraphs and the retrieval cannot bridge them. |
| 3 | **Recency / temporal.** "What is the most recent decision about X" where X has been mentioned multiple times across the corpus and the right answer is in the chronologically last document. | Whether the extractor preserves enough temporal context (dates, versions) that the retrieval can rank correctly. | Extractors that strip dates from entity descriptions retrieve all mentions equally; the recency signal is lost. |
| 4 | **Disambiguation.** "Which X" when two entities share a name but refer to different things (e.g. two projects with the same code name). | Whether the extractor produces distinguishable entity descriptions that the retrieval can disambiguate. | Extractors with low rel/ent ratios produce two entries called "X" with no qualifying detail; the retrieval returns both indiscriminately. |
| 5 | **Multi-hop traversal.** "What links A to B through C" where the path is two hops in the graph. | Whether the relation density is sufficient for the pipeline's multi-hop retrieval mode to find the path. | Sparse-relation extractors (low rel/ent) miss the middle hop; the pipeline cannot construct the path. |
| 6 | **Negation / contrast.** "What does the corpus NOT say about Y" or "What did we decide AGAINST regarding Y". | Whether the extractor recognises contrastive structure (decisions against, alternatives rejected) rather than reading every mention of Y as an endorsement. | Extractors that flatten contrastive language miss the negation; the retrieval returns mentions of Y without the contrast. |

The four retrieval modes (LightRAG's `naive` / `local` / `global` / `hybrid`) test the orthogonal dimension of whether the pipeline's retrieval strategy can find what the extractor put in the graph.

## Re-instantiation checklist for your corpus

1. Pick 20 documents that match the shape of your production retrieval workload. Pin them in a YAML file by relative path so the same files are ingested for every model row.
2. Write 6 canary queries that match the six shapes above, adapted to your corpus topic and entity types. For each query, name the document or section that should appear in the returned context (the expected reference). Commit the queries to the repo alongside the file list.
3. For each model you evaluate, ingest the 20-document corpus through your chosen knowledge-graph RAG pipeline with that LLM as the extractor, then run all 24 cells. Score by hand or by a script that compares returned context against the expected references.
4. Tabulate `pass / marginal / fail` plus entities-per-document plus relations-per-document plus measured cost on the 20-document subset.
5. Decide on a default. The cheapest model that hits 24/24 is the production answer; below that, the cost/quality trade-off is corpus-specific.

If you do this and your ranking comes out different from the report's, the report's invalidation conditions in [`../invalidation.md`](../invalidation.md) name what would falsify which finding. Write back through the issue tracker on the report's repository; a re-measurement that overturns a ranking is more valuable than a re-measurement that confirms one.
