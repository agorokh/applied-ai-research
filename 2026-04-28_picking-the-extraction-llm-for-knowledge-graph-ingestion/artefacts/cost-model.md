# Cost model

Per-100-document ingest cost derivation. Normalised so a reader can multiply by their own corpus size.

## A note on what is measured vs estimated

The per-call token counts in this artefact are derivations from the chunk size and observed extraction shape, not direct measurements from the LLM's token-usage records. They are within an order of magnitude of what an audit pass over the on-disk LLM-cache JSON would report; they are not invoice-level numbers. The list-price table below yields **~$7 to $10 per 100 documents** for Gemini 2.5 Flash: ~$7 at the no-gleaning baseline, with the high end reflecting the documented 30% to 50% gleaning uplift on output cost. The calculator is the appropriate number for negotiating per-token contract pricing; for projecting future spend on a similar corpus, re-measure invoice cost on a representative subset of your own corpus rather than projecting from this calculator.

## Per-document token accounting (estimated)

LightRAG ingest does roughly three LLM operations per chunk:

1. Entity extraction
2. Relation extraction
3. Merge summary (only when an entity appears in 8 or more chunks)

Operations 1 and 2 always run. Operation 3 runs sparsely. On this corpus the average works out to roughly **2.5 LLM calls per chunk**. Each call consumes roughly **8K input tokens + 2K output tokens** (the chunk plus the system prompt, then a structured extraction).

Each document averages roughly **4 chunks** at LightRAG default chunking (1200 tokens, 100 overlap). So per document:

- Calls: 2.5 calls / chunk x 4 chunks = **10 calls**
- Input tokens: 10 calls x 8K = **80K input**
- Output tokens: 10 calls x 2K = **20K output**

Per 100 documents:

- **8M input tokens, 2M output tokens.**

This is before the gleaning second pass (LightRAG's default gleaning=1 reruns extraction once to recover missed entities). Gleaning roughly doubles output tokens on the second pass but only on chunks where the first pass left material on the table; observed empirically as a ~30% to ~50% multiplier on output cost, depending on corpus. The numbers below use the no-gleaning baseline; add 30% to 50% to output cost for the gleaning case.

## Per-100-document cost at list prices

Using public list prices verified at run time. Per-million-token rates are quoted as input rate / output rate.

| Model | Per-1M input | Per-1M output | Input cost per 100 docs | Output cost per 100 docs | Total per 100 docs | Ratio (vs Gemini Flash) |
|---|---:|---:|---:|---:|---:|---:|
| **Gemini 2.5 Flash** | $0.30 | $2.50 | $2.40 | $5.00 | **~$7 to $10** | 1.0× |
| gpt-4o-mini | $0.15 | $0.60 | $1.20 | $1.20 | **~$2 to $3** | ~0.2× to ~0.4× |
| Claude Sonnet 4.6 | $3.00 | $15.00 | $24.00 | $30.00 | **~$54 to $69** | ~6× to ~9× (at list) |
| Llama 3.2 3B (local Ollama) | $0 | $0 | $0 | $0 | **$0** (electricity) | 0× |

**Partial local run (not in table above):** Qwen 2.5 14B GGUF Q4 on M1 Max completed **19/20** smoke documents at $0 list (electricity + wall-clock only), scoring **5 / 24**. Not cross-comparable to full-corpus rows; see [`model-matrix.md`](model-matrix.md) partial-runs section.

Range reflects gleaning vs no-gleaning. Operators on a fresh corpus typically see the gleaning-active numbers.

## Why measured invoices can exceed the list-price calculator

The list-price calculator above derives spend from per-1M-token rates at the per-document token shape. Measured invoices on the same corpus can come in higher than the calculator predicts because (1) extraction output frequently exceeds the schema (models add explanatory text the calculator does not anticipate), (2) gleaning fires more aggressively on some models than the no-gleaning baseline assumes, and (3) actual per-call usage varies from the per-1M estimate by model. The calculator is the right number for negotiating contract pricing; for projecting spend on a specific corpus and model pairing, re-measure invoice cost on a representative subset.

## What this model does NOT include

- **Embedder cost.** Held constant across all rows (local embedder). If you use a hosted embedder, add its cost separately; it does not change the ranking inside the matrix.
- **Gateway markup.** OpenRouter adds a small markup on top of provider list. Enterprise gateways may charge differently. The ratios above are robust to multiplicative pricing factors below roughly 10x.
- **Infrastructure cost.** Local rows show $0 inference cost; workstation, GPU, power, and wall-clock hours are independent of the model choice and not included.
- **Storage and graph database cost.** Neo4j or PostgreSQL hosting cost is independent of extractor choice.
- **Re-ingest cost.** Multiplies all of the above by the number of re-ingest events. A model swap or a chunking change forces a full re-ingest at the new configuration's rate; budget for this when picking the substrate.

## Projection to your corpus

Multiply the per-100-document figure by your corpus size in hundreds. For a 1,500-document corpus on Gemini 2.5 Flash: ~$100 to $150 at list, including gleaning. For the same corpus on Sonnet 4.6: ~$810 to $1,035 at list.

Re-derive the table for your own list prices and your own measured per-chunk token shape. The ratio claims survive substantial pricing variation; the absolute claims do not.

## Enterprise-scale worked examples

Two corpus shapes that a delivery lead at a mid-size enterprise actually has to size. **Example A** uses the smoke-corpus per-document token shape (~4 chunks per document, ~100K tokens per document). **Example B** uses a separate, shorter-document shape (~1 to 2 chunks per document); its dollar rows are illustrative on that reduced token basis and are not directly comparable to Example A without re-deriving. Real enterprise corpora vary; use these as a budget conversation starter, not a forecast.

### Example A: a 50,000-document Confluence export

Average document length similar to the smoke corpus (mixed prose, ~5 pages). Annual change rate 30 percent (15,000 documents updated or added per year).

| Cost line | Gemini 2.5 Flash | Sonnet 4.6 |
|---|---:|---:|
| One-time backfill (50,000 docs, list) | ~$3,500 to ~$5,000 | ~$27,000 to ~$34,500 |
| Annual delta-ingest (15,000 docs / year) | ~$1,050 to ~$1,500 / year | ~$8,100 to ~$10,350 / year |
| Re-ingest under model swap (full, ~once / 18 months) | ~$3,500 to ~$5,000 | ~$27,000 to ~$34,500 |
| Total year-1 cost at list (backfill + delta) | ~$4,500 to ~$6,500 | ~$35,000 to ~$45,000 |

Peak ingest load for Example A: 50,000 documents at the smoke-corpus shape (~80K input + ~20K output tokens per document) is on the order of **5 billion tokens** total. Wall-clock cost depends on your contracted per-minute and per-day rate limits on the chosen tier; verify the throughput shape against your re-ingest volume before sizing the dollar budget. The pricing rows above answer "how much does it cost"; the wall-clock answer is a separate question determined by your gateway contract, not by list price.

### Example B: a 200,000-document ticket archive

Average document much shorter than the smoke corpus (~10 lines per ticket on average). **Token basis:** ~1 to 2 chunks per document (~25K to 50K tokens per document at the same per-chunk rates), not the smoke-corpus ~100K. Annual change rate 60 percent (assumes ticket creation and closure churn). Dollar figures below are illustrative on this reduced shape; re-derive from your own measured chunk count before budgeting.

| Cost line | Gemini 2.5 Flash | Sonnet 4.6 |
|---|---:|---:|
| One-time backfill (200,000 docs, list) | ~$5,000 to ~$8,000 | ~$40,000 to ~$65,000 |
| Annual delta-ingest (120,000 docs / year) | ~$3,000 to ~$5,000 / year | ~$24,000 to ~$40,000 / year |
| Total year-1 cost at list | ~$8,000 to ~$13,000 | ~$64,000 to ~$105,000 |

This corpus shape benefits from extractor breadth more than the Confluence example because per-document text is shorter and a wider entity index covers more of it. The Gemini Flash advantage probably widens. The exact ratio is a re-measurement on your own ticket corpus, not a projection.

### What these examples are not

These are list-price calculations at the per-100-document shape measured on the smoke corpus described in the main report's §03. Enterprise contract pricing through DIAL or any other gateway will shift absolute magnitudes. Real ticket corpora have higher entropy than mixed-prose knowledge-base notes; real Confluence exports include attached PDFs and code blocks that ingest differently. The numbers above are the calculator output you bring to a budget conversation; the real figure your team should plan against comes from re-running the smoke rubric on a 20-document subset of your own corpus first.
