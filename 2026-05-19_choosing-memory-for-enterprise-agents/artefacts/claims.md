# Claims ledger — Choosing memory for enterprise agents

Every headline claim in [the report](../) tagged by category and pointed at the evidence row that backs it.

## Legend

| Category | Meaning |
|---|---|
| **measured** | Direct observation from the 128 paired trials, the closed-loop pilot, or the public-source review of Tencent DB Agent-Memory. |
| **inferred** | Conclusion drawn from the measured data, conditioned on a stated mechanism. |
| **hypothetical** | Scenario described to illustrate the form of an analysis. Not on this stack. |
| **recommendation** | Proposed deployment default or process step. Grounded in measured + inferred. |

## Ledger

| # | Report § | Category | Claim | Evidence pointer | Scope |
|---|---|---|---|---|---|
| 1 | Hero, §01 F1, §05 | **measured** | LightRAG (chunk-text) beats Graphiti (entity-graph) by ~36 percentage points under production-frequency weighting. | 128 paired trials, both judges in both orderings; uniform-vs-weighted aggregation in [`methodology.md`](methodology.md) §6. | One SDLC-history corpus, ~130 docs, production weighting stated in §04. |
| 2 | §01 F1, §05 | **measured** | Under uniform weighting the two substrates are statistically tied; the CI on the win-rate gap crosses zero. | Same trials, different aggregation. | Same scope. |
| 3 | §05 | **inferred** | The 36-point gap is driven by the two task families that carry 70% of production weight (current canonical text + handoff continuity). | Per-family win rates in the methodology; weights stated in §04 and [`task-families.md`](task-families.md). | The pattern transfers ("weight by your own production distribution"); the magnitude does not transfer without re-measurement. |
| 4 | Hero, §01 F2, §06 | **measured** | LightRAG produced 0 hallucinated retrievals across 128 paired appearances; Graphiti produced 4. | Position-swap judged trials; `hallucinated` label in the 5-label rubric. | 0 / 128 vs 4 / 128. 4 is too small for statistical significance on its own (see threshold #2 in [`methodology.md`](methodology.md) §5) — it's a structural-class indicator, not a measurement claim. |
| 5 | §06 | **inferred** | All four of Graphiti's hallucinated outputs were on temporal-supersession queries — exactly the family where bi-temporal metadata was expected to help. | Per-family hallucination breakdown. | Inference about mechanism (extraction step occasionally synthesises a supersession relation when no source document records it). |
| 6 | §06, §08 (Graphiti retirement callout) | **inferred / recommendation** | Autonomous-writeback paths should default to chunk-text retrieval, not entity-graph. | Combination of #1 + #4 + the structural failure-mode argument in §06. | Recommendation, grounded in measured rows above. |
| 7 | §01 F3, §07 | **measured** | On an 8-task closed-loop pilot: bi-temporal payload moved Gemini 2.5 Flash stale-fact citations 2→0; Claude Sonnet 4.5 went 0→2. | Closed-loop pilot, 8 tasks × 2 checkpoints × 3 conditions. | **Pilot data only**, not the formal closed-loop suite. Two executor checkpoints from two model families cannot fully separate capability-tier effects from family-specific effects. |
| 8 | §07 | **inferred / recommendation** | Bi-temporal context should default ON for cheaper / smaller executors, default OFF for more-capable executors. | Pilot #7 above, plus the mechanism (smaller executor benefits from explicit supersession; more-capable executor over-trusts the metadata). | Recommendation conditioned on the pilot. Formal closed-loop suite needs to confirm before this becomes a measurement claim. |
| 9 | §01 F4, §08 | **measured** | Tencent DB Agent-Memory fails 4 of 5 adoption criteria and 1 partial. | Public-source review against the bar stated in [`adoption-bar.md`](adoption-bar.md). | Project state as of mid-May 2026. Re-evaluable on next material release. |
| 10 | §08 (Graphiti retirement callout) | **inferred / recommendation** | Graphiti is retained for the narrow entity-disambiguation side path; the default deployment path no longer routes to it. | Combination of #1 + #4 + #6 + the substrate-vs-corpus pairing argument in §05. | Recommendation, framed as downstream consequence of measured findings. |
| 11 | §05 ("What the bar caught before deployment" callout) | **measured / process** | The pre-measurement prior (Graphiti as canonical substrate, based on published vendor numbers) was inverted by the frequency-weighted canary in the first measurement pass. | The pre-prior is documented in the engagement notes; the inversion is observable in the win-rate aggregate. | Process claim about the canary's value, not a substrate claim. |
| 12 | §09 (Four DIAL-routed defaults) | **recommendation** | Four platform defaults: chunk-text for SDLC corpora, bi-temporal gated on capability tier, autonomous-writeback uses the substrate with no extraction step, all routes via EPAM DIAL gateway. | Grounded in #1, #6, #8. | Specific to a DIAL-routed deployment; defaults 1–3 generalise to any sanctioned-inference gateway. |
| 13 | §10 (Three time-horizons) | **recommendation** | This quarter: identify the corpus class, run a 20–60 question canary, write the adoption bar a priori. This year: build a re-runnable harness, cross-tier the canary, establish a default-rejection profile. | Grounded in the methodology + the canary-as-durable-artefact claim. | Recommendations for any delivery team running comparable enterprise-agent stacks. |
| 14 | §11 (Scope limits 1–9) | **scope** | One corpus class, one work instance; small N per family; naïve filesystem baseline; two-judge consensus inflates ties; provider invariance assumed at temperature 0; tier-interaction rests on two checkpoints; adoption-bar evaluation is point-in-time; cost-per-decision not in scope; closed-loop counts are pilot-level. | Scope-limit table in §11. | Each limit applies to one or more headline findings; consult [`invalidation.md`](invalidation.md) for the specific re-measurements that would falsify the headlines. |
| 15 | §12 (closing) | **process** | The durable artefact is the canary harness shape, the adoption bar, and the section arc of a deployment-decision memo — not the headline magnitudes. | The harness shape is published at [`canary-harness/`](canary-harness/). The bar is at [`adoption-bar.md`](adoption-bar.md). | The framing is the report's strongest claim; magnitudes expire when models or corpora change. |

## Use

When citing externally, quote **measured** rows with the scope qualifier attached, **inferred** rows as "the report infers", **hypothetical** rows only as scenarios, and **recommendation** rows as the author's proposed defaults. **Process** rows are claims about the methodology itself, not about substrates.
