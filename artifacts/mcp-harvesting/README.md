# Companion artifact: provenance-atom v0.1 + the gate-ablation experiment

This folder is the reusable, checkable half of the article *MCP Harvesting: Sampling a
Tool Surface You Don't Control*. It contains the primitive the article ships (a typed
provenance atom and a deterministic structural gate) and the experiment that tests the
article's one falsifiable claim (section 7).

## The primitive

- `provenance_atom.schema.json` : the `provenance-atom v0.1` format. One typed claim with an
  evidence strength (`stated` / `implied` / `inferred`) and a locator carrying the source, the
  content hash, the location, and a literal quote. The quote is the falsifiability handle.
- `gate.py` : a dependency-free validator plus the **deterministic** half of the grounding gate.
  `structural_gate(atom, source_text)` rejects any atom whose quote is missing or does not appear
  verbatim in the cited source, with no model in the loop. Run `python3 gate.py` for the self-test.

The semantic half (does the source actually *support* the claim, beyond the quote merely
appearing) needs an entailment or reasoning model. That half, and the evidence that it beats a
similarity gate, is the experiment below.

## The experiment (section 7 of the article)

**Claim under test.** When a grounding gate must decide whether a cited source supports a claim,
an entailment or reasoning gate catches materially more unsupported claims than an
embedding-similarity gate, at a false-refuse rate low enough to be worth the cost.

- `dataset.jsonl` : 72 hand-authored claim/source pairs in generic enterprise domains, 28
  supported and 44 not (unsupported or contradicted). Five design cells, built to be hard in both
  directions: unsupported claims with high source overlap (scope, quantity, temporal, modality,
  attribution, entity shifts) and supported claims worded so differently that surface similarity is
  low. Neither a similarity threshold nor an LLM is handed an easy win.
- `run_eval.py` : runs four gates over the same pairs (lexical cosine, neural-embedding cosine,
  LLM entailment, LLM reasoning on two model families), sweeps the similarity thresholds to build
  the full catch-versus-false-refuse frontier, and compares the LLM gates at *matched* false-refuse.
- `results.md` / `results.json` / `predictions.jsonl` : the output, regenerated on every run.

### Result (this run)

At the LLM gate's 0.07 false-refuse operating point, the embedding-similarity gate catches **27%**
of unsupported claims and the lexical gate catches **0%**, against the LLM gates' **98 to 100%**.
The reason is structural: the unsupported similarity-traps average a 0.89 embedding cosine to their
source and the contradicted pairs 0.87, both higher than the genuinely supported paraphrases at
0.77, so no similarity threshold separates supported from unsupported (best balanced accuracy 0.64
versus the LLM gates' 0.96 to 0.97). The pre-registered falsification condition did not trigger.

### Honest caveats

- The corpus is **synthetic and single-author**: I wrote and labeled all 72 pairs, so there is no
  independent label check and no inter-rater reliability. It is built to contain the adversarial
  cases the grounding literature documents in the wild; the finding is the *gap between gate types*
  on those cases, not a production rate.
- The "embedding-similarity gate" is a **bi-encoder cosine**. A cross-encoder or a fine-tuned
  natural-language-inference model would do better and shades into the entailment gate. The honest
  boundary of the result: similarity *scoring* cannot separate related from supported; *entailment
  judgment*, whether a small fine-tuned model or an LLM, can.
- The LLM gate's near-perfect catch reflects a set where support is cleanly decidable; on subtler
  real claims its false-refuse would rise. Its two false-refuses here were both genuine inferences,
  the conservative direction you want a gate to fail in.
- The larger ablation the protocol also names, the full harvest pipeline against a single
  long-context model reading the raw files, was **not** run. That is the next experiment.

## Reproduce

```bash
doppler run --project YOUR_PROJECT --config YOUR_CONFIG -- python3 run_eval.py
```

Needs `OPENROUTER_API_KEY` (LLM gates) and `FIREWORKS_API_KEY` (embeddings). Every API response is
cached under `.cache/`, so a re-run is free and the exact model outputs are auditable. The only
non-stdlib import is `httpx`. Cost of a cold run: ~33k LLM tokens across 216 calls plus 144
embedding calls, cents not dollars.
