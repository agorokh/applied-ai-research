# Gate-ablation result

N = 72 labelled claim/source pairs (28 supported, 44 not supported: unsupported + contradicted). Hand-authored, generic enterprise domains. LLM gate model: `anthropic/claude-3.5-haiku` (robustness check: `openai/gpt-4o-mini`); embeddings: `nomic-ai/nomic-embed-text-v1.5`.

A gate ACCEPTS a claim it judges supported and REJECTS otherwise. **catch** = fraction of not-supported claims rejected; **false-refuse** = fraction of supported claims wrongly rejected. Higher catch and lower false-refuse are better.

## Headline

| gate | catch | false-refuse | accuracy |
|---|---|---|---|
| LLM reasoning (anthropic/claude-3.5-haiku) | 0.98 | 0.07 | 0.96 |
| LLM reasoning (openai/gpt-4o-mini) | 1.00 | 0.07 | 0.97 |
| LLM entailment (NLI label) | 0.98 | 0.04 | 0.97 |
| embedding similarity, best threshold | 0.84 | 0.68 | 0.64 |
| lexical similarity, best threshold | 0.86 | 0.71 | 0.64 |

## The fair comparison: catch at matched false-refuse (<= 0.07, the LLM reasoning gate's rate)

| similarity gate | best catch achievable at that false-refuse |
|---|---|
| embedding | 0.27 (at false-refuse 0.00) |
| lexical | 0.00 (at false-refuse 0.00) |

## Catch by design cell (where the gates differ)

| gate | unsupported similarity trap | contradicted high overlap | unsupported offtopic |
|---|---|---|---|
| LLM reasoning | 1.00 | 1.00 | 0.92 |
| LLM entailment | 0.94 | 1.00 | 1.00 |
| embedding (best thr) | 0.62 | 0.94 | 1.00 |
| lexical (best thr) | 0.69 | 0.94 | 1.00 |

The similarity-trap and contradicted cells are the ones with high surface overlap, where a claim looks related to its source but is not supported. That is where a similarity gate is structurally blind: it cannot separate 'related' from 'supported'.


Cost: 33269 LLM tokens across 216 calls (entailment + two reasoning models), plus 144 embedding calls. Cents, not dollars.


_Reproduce:_ `doppler run --project YOUR_PROJECT --config YOUR_CONFIG -- python3 run_eval.py`. All API responses are cached under `.cache/`; predictions are in `predictions.jsonl`.
