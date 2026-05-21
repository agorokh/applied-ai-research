# Invalidation conditions

Falsification conditions per finding. Each row names the specific re-measurement that would invalidate the claim.

## Finding 1: breadth beats density for graph-traversal retrieval

**Stated claim:** On LightRAG's traversal-then-fetch retrieval shape, an extractor that produces more entities per document (Gemini 2.5 Flash) outperforms an extractor that produces a denser relation graph per entity (Sonnet 4.6), despite the latter's higher rel/ent ratio.

**Would be invalidated by:** Running the same 24-cell smoke rubric on a corpus where the canary queries are deliberately multi-hop ("what links A to B through C") and observing Sonnet 4.6 winning by a margin larger than the marginal-recovery slack. If the query distribution rewards density, the ranking flips and the breadth-over-density claim is corpus-conditional, not general.

**Would be reinforced by:** Re-running on a structurally different corpus (e.g. code documentation, scientific papers) and observing the same Gemini 2.5 Flash entity-count advantage and the same smoke ranking.

## Finding 2: the cost-quality Pareto has one sweet spot

**Stated claim:** Gemini 2.5 Flash hits the smoke ceiling at the lowest measured cost; gpt-4o-mini is much cheaper but loses cells; Sonnet 4.6 is much more expensive at the same quality ceiling.

**Would be invalidated by:** Measuring a not-yet-tested commercial model (e.g. Claude Haiku 4.5, GPT-4.1 mini, DeepSeek V3) that scores 24/24 on the smoke rubric at lower cost than Gemini 2.5 Flash. That would shift the Pareto point, not refute the Pareto-point pattern.

**Would be reinforced by:** Re-running on a different provider gateway with different list prices and observing the same ranking (Gemini Flash cheapest at 24/24, gpt-4o-mini cheapest with cells lost, Sonnet most expensive at parity).

## Finding 3: local open-source is hardware-bound, not capability-bound

**Stated claim:** Six local trials across two hardware tiers all scored below Gemini 2.5 Flash on the smoke rubric; the best local result (Qwen 2.5 14B GGUF Q4 on M1 Max) scored 5/4/15.

**Would be invalidated by:** Running an open-source model on a workstation with substantially larger memory (e.g. 80B-class model on a 96 GB or 128 GB Apple Silicon machine, or a 70B-class model on a multi-GPU server) and scoring 24/24 on the same rubric.

**Would be reinforced by:** Running additional 14B-class open-source models on M1 Max (e.g. Llama 3.1 14B, Mistral 13B) and observing the same schema-noise failure pattern.

## Finding 3.b: thinking-mode models burn the worker timeout

**Stated claim:** Reasoning-style models with default thinking enabled emit a long internal monologue that pushes per-chunk wall-clock past the worker timeout on LightRAG ingest.

**Would be invalidated by:** Running a reasoning-mode model with a worker timeout large enough to absorb the thinking tokens (e.g. 300+ seconds per call) and observing comparable or better smoke score than the same model family's no-think variant, justifying the latency cost.

**Would be reinforced by:** Running additional reasoning-mode models (e.g. DeepSeek R1 series, OpenAI o-series) on the same rubric and observing the same timeout pattern.

## Finding 4: cost ratios survive contract pricing better than absolutes

**Stated claim:** Per-100-document cost ratios inside the matrix (e.g. ~33x for Sonnet over Gemini Flash) are more stable than absolute magnitudes against contract pricing variation.

**Would be invalidated by:** Running the same 11 models through an enterprise gateway whose contract pricing inverts the ratio (e.g. a contract where Sonnet is bundled at zero marginal cost while Gemini is metered at list).

**Would be reinforced by:** Running on a different gateway with a known discount schedule and observing the ranking inside the smoke-pass cluster preserved.

## Operational lesson: empty substrate looks the same as healthy substrate to the wrong canary

**Stated claim:** A "no relevant context found" response from a healthy graph that the query missed is indistinguishable from the same response from an empty graph, unless the canary asserts specific expected references.

**Would be invalidated by:** Demonstrating a canary that reliably distinguishes empty from healthy without asserting expected references (e.g. via a metadata or schema check on the underlying graph store). That would shift the locus of the assertion, not refute the need for one.

**Would be reinforced by:** Running the same canary against a deliberately corrupted graph and observing it still passes (because the assertion is too weak).
