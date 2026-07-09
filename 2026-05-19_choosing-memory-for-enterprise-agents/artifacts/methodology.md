# Methodology — Choosing memory for enterprise agents

Companion to [the memory-substrate report](../). Specifies the paired-question protocol, the two-judge position-swap fixture, the pre-registered rule-change threshold, the frequency-weighting derivation, and the corpus shape — in enough detail that a practitioner could re-instantiate the canary on their own corpus with their own 60–80 paired questions.

It deliberately does **not** publish the 64 paired questions on the actual SDLC corpus, or the judge prompts, or the corpus content. Those need to stay private for the harness to remain a fair fixture on re-runs. The [`canary-harness/`](canary-harness/) directory ships the *shape* + a neutral-domain example fixture sufficient to re-instantiate.

---

## 1. Scope

| Parameter | Value | Notes |
|---|---|---|
| Corpus | SDLC-history-shaped, ~130 documents | ADRs, design records, ticket history, post-incident reviews, runbooks, architecture invariants. Corpus content is internal and not published. |
| Substrates measured | 3 | LightRAG (chunk-text retrieval); Graphiti (entity-graph with bi-temporal metadata); filesystem baseline (keyword grep). |
| Candidates considered + rejected pre-canary | 1 | Tencent DB Agent-Memory — see [`adoption-bar.md`](adoption-bar.md) for the scorecard. |
| Candidates considered + excluded by class duplication | 1 | Mem0 — same architectural class as Graphiti (extraction-mediated semantic store with LLM-rewrite at ingest). |
| Paired questions per substrate pair | 64 | Each pair (A vs filesystem; B vs filesystem; A vs B) saw the same 64 questions. |
| Substrate pairs | 3 | LightRAG vs filesystem, Graphiti vs filesystem, LightRAG vs Graphiti. |
| Judges per pair | 2 | Chosen from different model families to surface family-specific bias as judge disagreement. |
| Orderings per judge per pair | 2 | Position-swap collapse: a pair "wins" only when the same candidate is preferred in both orderings by both judges. |
| Total LLM-judge calls per substrate pair | 256 | 64 questions × 2 orderings × 2 judges. |
| Trials per pair | 128 paired appearances per substrate | (64 questions × 2 orderings; aggregated across both judges to 128 paired appearances per substrate per pair). |
| Closed-loop pilot for tier-interaction | 8 tasks per cell × 3 conditions × 2 executor checkpoints | Pilot N, not formal benchmark. |

## 2. Task-family weighting

The 8 task families used in the retrieval canary, and the production query distribution observed on the actual workload, are documented separately in [`task-families.md`](task-families.md). Summary:

| Task family | Production frequency | Why it discriminates |
|---|---|---|
| Current canonical text | ~50% | Literal-source retrieval. Distinguishes substrates that paraphrase at ingest. |
| Handoff continuity | ~20% | Cross-session state recall. Distinguishes summary vs literal substrates. |
| Entity disambiguation | ~10% | Alias resolution. The one family where entity-graph wins decisively. |
| Temporal supersession | ~4% | Time-windowed fact recall. The bi-temporal-metadata test. |
| Multi-hop traversal | ~4% | Chained-evidence retrieval. Distinguishes graph vs flat retrieval. |
| Knowledge updates | ~4% | New-doctrine recall. Tests substrate's response to corpus mutation. |
| Abstention on false premise | ~4% | Refusal discipline. Tests whether substrate over-confidently invents. |
| Link-graph traversal | ~4% | Reverse-link retrieval. Distinguishes graph-shaped indexes. |

## 3. Position-swap judging protocol

The same question is shown to each judge **twice** — once with substrate A's retrieval shown first, once with substrate B's retrieval shown first. A pair "wins" only when the same candidate is preferred in both orderings.

| Outcome of judge call | Position-swap collapse |
|---|---|
| Both orderings prefer A | A wins |
| Both orderings prefer B | B wins |
| Orderings disagree | tie (information discarded) |

Two judges (different model families) score independently. A pair wins on the **intersection**: both judges must agree in both orderings.

This is more conservative than single-judge / single-ordering setups. The over-counting of ties is a feature — it forces the headline result to survive judge order, which rules out the position-bias artefact that has surfaced in published LLM-judge benchmark critiques (see [arXiv:2506.06331](https://arxiv.org/abs/2506.06331) for the relevant prior work).

## 4. Scoring rubric (5 labels)

Each retrieval is labelled by both judges as one of:

| Label | Meaning |
|---|---|
| `correct` | Complete and accurate retrieval. |
| `partial` | Relevant but incomplete. |
| `incorrect` | A real source document, but the wrong one. |
| `abstained` | Substrate returned nothing usable. |
| `hallucinated` | Substrate returned content that does not exist in any source document. |

The `hallucinated` vs `incorrect` distinction is load-bearing. An incorrect-but-real source can be cross-checked; a fabricated source cannot. The §06 reliability finding turns on this distinction.

## 5. Pre-registered rule-change threshold

The rule-change threshold was **fixed before any retrieval ran**, to prevent post-hoc threshold selection from cherry-picking a clean headline. A result clears the threshold under any of:

| Condition | Threshold | Why this number |
|---|---|---|
| Absolute win-rate gap | ≥ 20 percentage points | Sample size N=128 paired appearances per substrate makes ≥20pp clearly outside noise envelope. |
| Fabrication-rate ratio | ≥ 2× | Doubling the fabrication rate is a structural-class change, not a marginal one. |
| Confidence interval on the win-rate gap | excludes zero | Statistical-significance check on the headline gap. |

The 36-point production-weighted gap (LightRAG vs Graphiti) clears the first condition. The 0-vs-4 fabrication count clears the second condition (∞× ratio; statistically too small to publish on its own but structurally informative). The CI on the production-weighted gap (not published in the report body for compactness) excludes zero at 95%.

## 6. Frequency-weighting derivation

Two aggregation methods compared:

**Uniform**: each of the 8 task families contributes 1/8 to the aggregate. Score = mean of per-family win rates.

**Frequency-weighted**: each task family contributes proportional to its production query frequency. Score = Σ (family_weight_i × family_win_rate_i).

The production query frequencies were measured on the actual workload over a representative interval prior to the canary (not derived from the canary itself). The weights used are stated up front in §04 of the report; they are also restated in [`task-families.md`](task-families.md).

Under uniform aggregation, the LightRAG-vs-Graphiti win-rate gap is small and the CI crosses zero (statistically tied). Under frequency weighting, the gap is ~36pp.

This is not a methodological gotcha — it's the **headline finding** of the report. The two task families that carry 70% of production weight (current canonical text + handoff continuity) are the two where chunk-text retrieval wins decisively; the family where entity-graph wins (entity disambiguation) carries 10% of the weight.

## 7. Executor checkpoints (closed-loop pilot, §07)

The stale-fact inversion finding (§07) uses a separate closed-loop pilot — not the retrieval canary above. Two executor checkpoints, 8 tasks per cell, 3 conditions (bi-temporal context OFF, ON, ablated).

| Tier | Checkpoint | Rationale |
|---|---|---|
| More-capable / flagship | Claude Sonnet 4.5 | Current-generation flagship from a major lab. |
| Smaller / cheaper | Gemini 2.5 Flash | Fast, lower-cost model from a different major lab (rules out family bias as the only explanation). |

Two checkpoints is **not** sufficient to claim "capability tier is the only factor". Family bias remains possible. The §07 finding is therefore stated as directional input to a per-tier default, not as a formal benchmark conclusion. The formal closed-loop 8-task suite is deferred to a follow-up.

## 8. Routing during the evaluation window

The bench harness routed model calls (judges, executors, extractor) through an interim provider path during the evaluation window — the EPAM DIAL workspace for this evaluation was provisioning concurrently. A DIAL-canonical re-run is in scope for the next iteration before any of the numbers should be cited as "DIAL-routed deployment-ready."

The assumption underlying this scoping choice: **at temperature 0, the same model returns the same answer regardless of routing**. Plausible (transformer inference is deterministic at temperature 0 for a fixed weight set), but not separately measured here. Provider-invariance verification is in the §11 scope-limit list.

## 9. What the methodology is NOT

- Not a peer-reviewed paper. N at the per-task-family level is 8 paired questions; large enough to detect large effects per family, not enough for fine-grained per-family CI.
- Not a vendor benchmark. The intent is "which substrate should this stack default to on SDLC-shaped corpora", not "rank substrates on a universal corpus."
- Not transferable to a different corpus class without re-measurement. The 36-point gap is for an SDLC-shaped corpus with the production weighting in §04 — a corpus where entity disambiguation dominates (a customer-support knowledge base where the same product is named differently across regions, for instance) would re-weight in favour of the entity-graph approach.
- Not transferable to a different gateway without re-measurement. A DIAL-canonical re-run is the pending follow-up; until then, treat the rankings as interim-path-derived.

## 10. Re-instantiation on another stack

To reproduce the *shape* of this canary on your own corpus:

1. Pick 60–80 paired questions covering your corpus's actual query distribution. Use [`task-families.md`](task-families.md) as the starting taxonomy; substitute as appropriate.
2. Set up two retrieval substrates you want to compare (one chunk-text, one entity-graph, or two of your candidates).
3. Use two judges from different model families. Run each question through both orderings on each judge.
4. Collapse position-swap disagreement to `tie`.
5. Compute uniform-weighted and frequency-weighted aggregates separately. **Publish both numbers**. Where they diverge, the divergence is the finding.
6. Pre-register the rule-change threshold before running any retrieval. Use the §5 thresholds as the starting point.
7. Publish the scope limits — what your corpus is, what the production query frequencies were, why they are what they are, and what would invalidate the headline.

The pattern transfers. The specific 36-point gap, the 0-vs-4 fabrication count, and the stale-fact inversion direction do not transfer without re-measurement.
