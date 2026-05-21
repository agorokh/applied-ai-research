# Cost model

Per-100-document ingest cost derivation. Normalised so a reader can multiply by their own corpus size.

## A note on what is measured vs estimated

The per-call token counts in this artefact are derivations from the chunk size and observed extraction shape, not direct measurements from the LLM's token-usage records. They are within an order of magnitude of what an audit pass over the on-disk LLM-cache JSON would report; they are not invoice-level numbers. Where the report cites "~$20 per 100 documents" for Gemini 2.5 Flash, that number is the invoice-extrapolation from the smoke run ("~$4 for 20 documents" became "~$20 for 100"), not the list-price calculator below. Where the calculator and the invoice disagree, the invoice is the truthier number for projecting future spend on a similar corpus; the calculator is the truthier number for negotiating per-token contract pricing.

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
| gpt-4o-mini | $0.15 | $0.60 | $1.20 | $1.20 | **~$2 to $3** | 0.2× to 0.3× |
| Claude Sonnet 4.6 | $3.00 | $15.00 | $24.00 | $30.00 | **~$54 to $69** | ~6× to ~9× (at list) |
| Llama 3.2 3B (local Ollama) | $0 | $0 | $0 | $0 | **$0** (electricity) | 0× |
| Qwen 2.5 14B GGUF Q4 (local M1 Max) | $0 | $0 | $0 | $0 | **$0** (electricity + wall-clock) | 0× |

Range reflects gleaning vs no-gleaning. Operators on a fresh corpus typically see the gleaning-active numbers.

## Why the report says "~33x" for Sonnet vs Gemini Flash

The benchmark paper that locked in Gemini 2.5 Flash measured the cost ratio empirically on the 20-document smoke corpus, where Sonnet's invoice came in roughly 33 times Gemini Flash's invoice. The ~7x to ~10x figure in the table above is the list-price derivation; the gap between list-derived and invoice-measured ratios reflects three things:

1. Sonnet's output cost dominates its bill on this workload (extraction generates more output per chunk than the schema implies because of explanatory text the model adds).
2. Gemini Flash's actual usage came in below the per-1M estimate because the model emits more compact extractions per call.
3. Gleaning ran differently on the two models; Sonnet triggered more gleaning passes.

Both numbers are correct. The ~33x is the measured invoice ratio on this specific corpus. The ~7x to ~10x is the calculator-grade list-price derivation. Use the larger one when projecting cost-of-mistake (e.g. "if I accidentally re-ingest on Sonnet for a week"); use the smaller one when negotiating contract pricing.

## What this model does NOT include

- **Embedder cost.** Held constant across all rows (local embedder). If you use a hosted embedder, add its cost separately; it does not change the ranking inside the matrix.
- **Gateway markup.** OpenRouter adds a small markup on top of provider list. Enterprise gateways may charge differently. The ratios above are robust to multiplicative pricing factors below roughly 10x.
- **Infrastructure cost.** Local rows show $0 inference cost but absorb the cost of the workstation, power, and (for M1 Max) wall-clock hours that the operator is not otherwise using the machine.
- **Storage and graph database cost.** Neo4j or PostgreSQL hosting cost is independent of extractor choice.
- **Re-ingest cost.** Multiplies all of the above by the number of re-ingest events. The drift incident in §09 of the main report was costly precisely because it forced a full re-ingest at the wrong model's rate.

## Projection to your corpus

Multiply the per-100-document figure by your corpus size in hundreds. For a 1,500-document corpus on Gemini 2.5 Flash: ~$100 to $150 at list, including gleaning. For the same corpus on Sonnet 4.6: ~$810 to $1,035 at list.

Re-derive the table for your own list prices and your own measured per-chunk token shape. The ratio claims survive substantial pricing variation; the absolute claims do not.
