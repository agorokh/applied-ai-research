# Task families and production weighting

The 8 task families used in the retrieval canary, the production-frequency weighting derived from the actual workload, and the rationale for why each family discriminates between substrates. Companion to [the report](../) §04 (test design) and §05 (headline result).

## The 8 families

| # | Task family | What the agent is trying to do | Production frequency | Why it discriminates between substrates |
|---|---|---|---|---|
| 1 | **Current canonical text** | "What is the current rule / invariant / decision for X?" Read the literal source so the agent can quote it back. | **~50%** | Chunk-text substrates return literal source; entity-graph substrates rewrite at ingest. Heaviest-weighted family. |
| 2 | **Handoff continuity** | "Where did the previous session leave off, and what is the next action?" Read the current handoff state. | **~20%** | Same chunk-text vs entity-graph distinction; handoff state is canonical text that has just been written. |
| 3 | **Entity disambiguation** | "Which of several entities sharing a name is meant in this context?" Resolve a noun across multiple sources. | **~10%** | Entity-graph substrates explicitly merge aliases; chunk-text substrates return multiple chunks and rely on the executor to disambiguate. **The one family where entity-graph wins decisively.** |
| 4 | Temporal supersession | "What changed between two points in time? What deprecated what?" | ~4% | The bi-temporal-metadata test. Entity-graph with bi-temporal metadata should win in principle; in practice (§06), this is where the hallucinations cluster — the extraction step occasionally synthesises a supersession relation no source records. |
| 5 | Multi-hop traversal | "Which investigations led to this decision? What chain of evidence supports this rule?" | ~4% | Graph-shaped indexes have a natural advantage; chunk-text substrates require iterative re-query. |
| 6 | Knowledge updates | "What did the new doctrine just impose that the old one did not?" | ~4% | Tests substrate response to corpus mutation. Both substrate types handle this with re-ingest; the test isolates ingest-pipeline freshness. |
| 7 | Abstention on false premise | "This question references a rule that does not exist. Refuse to answer." | ~4% | Refusal discipline. Tests whether the substrate over-confidently invents content (the `hallucinated` label in the rubric). |
| 8 | Link-graph traversal | "Which other documents link to this one?" | ~4% | Reverse-link retrieval. Distinguishes graph-shaped indexes from flat retrieval. |

## Production weighting derivation

The frequency column above is the production query distribution on the actual workload, observed over a representative interval **prior to** the canary. It is **not** derived from the canary itself — that would be circular (you cannot let the canary's task distribution decide which task is most important).

The interval was chosen to span:

- At least one full sprint cycle (to capture the normal mix of planning-phase queries — heavy on current-canonical-text — and post-mortem-phase queries — heavier on multi-hop traversal).
- At least one corpus-mutation event (to capture how knowledge-updates queries spike after a new ADR or invariant lands).
- Excluding any periods of unusual activity (e.g., a sprint that was entirely an entity-disambiguation cleanup would over-weight family 3).

The interval length was 6 weeks of agent traffic. Total queries in the interval: roughly 2,400, which is small enough that the per-family frequencies have observable uncertainty (±2pp on the headline families, ±1pp on the long-tail families). The weights stated above are mid-point estimates from that observation.

## Why these weights matter to the headline

The 36-point gap finding in §05 turns entirely on these weights. Under **uniform weighting** (each family contributes 1/8), the two substrates are statistically tied — the families where chunk-text wins (1, 2) and where entity-graph wins (3) average out across the other five (which are mixed).

Under **production weighting**, the two families that carry 70% of the load (1 + 2 = 70%) both favour chunk-text decisively, and the family where entity-graph wins (3) carries only 10%. The aggregate is dominated by what production actually does.

This is the report's central methodological argument: **the weighting decides the outcome, not the candidates**. A benchmark report that publishes only the uniform aggregate is reporting a number that does not map to production decisions.

## Re-derivation on another corpus

For a different corpus class (e.g., business / domain corpus per §02), the weights almost certainly invert:

- A customer-support knowledge base: entity disambiguation (family 3) likely dominates (multi-region product naming).
- A legal case archive: temporal supersession (family 4) plausibly dominates (precedent supersession, regulatory updates).
- A medical records system: family 1 (current canonical) and family 7 (abstention on false premise) both critical.

For each new corpus, the derivation steps are:

1. Sample the actual production query log for at least one full operational cycle.
2. Classify each query into the 8 families (or a corpus-appropriate refinement of them).
3. Tally the per-family frequencies.
4. Publish the weights up front, before running any canary.
5. **Re-derive the substrate ranking under the new weights.** Don't assume the SDLC-corpus ranking transfers.

The 8-family taxonomy is a starting point; corpora that have substantially different query patterns should refine or replace it. The key invariant is: state the weights before measuring, and the methodology survives the corpus change.

## What the per-family table in the report does NOT show

The §07 table (closed-loop pilot for tier interaction) uses a different task set — the 8-task closed-loop pilot tasks, not these 8 retrieval families. The closed-loop tasks test a different question (does extra structural context help the executor when memory is wired through the agentic loop), and they were not part of the 128-paired-question retrieval canary. The two evaluation surfaces are deliberately separate.
