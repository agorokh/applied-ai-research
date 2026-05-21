# What would invalidate this report

Per-finding Popperian commitments for [the memory-substrate report](../). For each headline finding, the specific re-measurement that would falsify or materially change it.

## Headline finding 1 — Production-weighted retrieval separates the substrates by 36 points

**Invalidation conditions (any one of these would force a re-publish):**

- A re-run on the same 8 task families with the same paired-question protocol and the same production weighting where the LightRAG-vs-Graphiti gap falls below the 20pp threshold. Likely cause: an upgrade in Graphiti's extraction step that preserves more literal source phrasing through the ingest LLM-rewrite would close the gap on current-canonical-text queries (the family carrying 50% of the weight).
- A re-run on a corpus where entity disambiguation carries >25% of production weight (a customer-support knowledge base where the same product is named differently across regions, for instance) where the report's substrate-default would invert. The pattern ("weight by your production distribution") still holds; only the specific recommendation flips. This is not falsification of the methodology — it's falsification of the *default* for SDLC-shaped corpora extended to a different corpus class.
- A re-derivation of the production query distribution on the same corpus that produces materially different weights. If the production frequencies were measured on an unrepresentative interval (e.g., a sprint focused on entity-disambiguation queries), re-measuring on a longer window could shift the weights enough to close the gap.

## Headline finding 2 — Reliability: 0 versus 4 out of 128 paired trials

**Invalidation conditions:**

- A second pass with the same 128-question budget where Graphiti's hallucination count falls to ≤1 / 128 AND LightRAG's hallucination count rises to ≥2 / 128. Hallucination at N=128 is too small for statistical significance on its own; the structural-class claim ("extraction-mediated substrates can synthesise relations no source records; chunk-text substrates cannot") would survive even if the counts equalised, but the empirical hook in the headline would not.
- Identification of a Graphiti extraction-step configuration that prevents the temporal-supersession synthesis observed in the report (e.g., a stricter extraction prompt that refuses to emit `superseded_by` relations without an explicit supersession verb in the source). The 4 hallucinations clustered on temporal-supersession queries specifically; an extraction-step patch that resolves those would invert the reliability comparison.

## Headline finding 3 — Stale-fact inversion across executor tiers (pilot data)

This is explicitly flagged as **pilot data, not the formal closed-loop suite**, in §07. The invalidation conditions are correspondingly looser:

- The formal closed-loop 8-task suite, when it runs, produces a result that does not show the sign flip across Sonnet 4.5 vs Flash 2.5. Likely cause: the pilot N (8 tasks per cell) is small enough that the 2 → 0 and 0 → 2 counts could be noise rather than structural. The formal suite is the test that promotes pilot → finding.
- Addition of a third executor checkpoint (e.g., GPT-5 Mini at the smaller tier, Claude Opus 4.7 at the flagship) where the bi-temporal-context flip does NOT replicate. Two checkpoints from two families can be capability-tier OR family bias; three checkpoints across three families would disambiguate.
- An ablation showing the inversion is driven by a specific token-level interaction (e.g., the explicit `valid-from / superseded-on` payload formatting overlapping with a regex the model was trained on). If so, "context design must match executor capability" becomes "context payload format matters at the tokeniser level", which is a different and more constrained finding.

## Headline finding 4 — Tencent DB Agent-Memory fails 4 of 5 adoption criteria

**Invalidation conditions:**

- Tencent ships a material release that addresses any of the failing criteria. The four failures were: integration surface (TypeScript-only), install hygiene (post-install rewrites a sibling package), test coverage (zero test files in published source), operational fit (no MCP surface). Any one of these resolved by an upstream release would warrant a re-evaluation against the same bar.
- Identification of an evaluator error in the audit (e.g., the test files exist but are namespaced under a directory the search missed). If a reviewer re-runs the audit against the same project at the same version and reports different criterion scores, the report is happy to be the second non-vendor evaluation and to publish the reconciliation.

## Architectural finding — The canary harness is the durable artefact

This is **process claim**, not a substrate claim. The conditions under which the claim would be invalidated:

- The harness shape published at [`canary-harness/`](canary-harness/) cannot be re-instantiated on a different corpus class in a day by a practitioner with comparable tooling. The report's §10 claim ("re-runnable in a day") is operational; one practitioner running this on a different corpus and reporting >1 day to re-instantiate would invalidate that specific claim. The shape would still be useful — just not as cheap to deploy as advertised.

## Methodology

If any of these invalidations is observed, the right response is to open an issue on this repository with the new measurement attached. **The bar is the durable artefact; specific magnitudes expire when models, corpora, or substrate implementations change.**

The whole point of publishing the methodology + claims ledger + invalidation conditions is to make this kind of structured push-back cheap. A two-line issue ("re-ran the canary on corpus X, got Y") is more useful than a 500-word debate over whether the report was overstating.
