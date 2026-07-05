# What would invalidate this report

Per-finding Popperian commitments — the specific re-measurements that would falsify or materially change each headline claim in [the POC report](../).

## Headline finding 1 — Qwen3-Coder 480B is the cheapest 100%-pass model

**Invalidation conditions (any one of these would force a re-publish):**

- A re-run on the same task portfolio at the same Bedrock list pricing where Qwen3-Coder 480B drops below 100% pass (e.g., 21/24 or worse). Likely cause: the held-out tasks would need to be replaced with a different set, since this set is the harness; but a *new* portfolio with different proportions of T6 / T8 could plausibly demote Qwen 480B.
- A markup factor on Qwen 480B input rates greater than ~6.7× that flips the ranking inside the 100%-pass cluster. EPAM DIAL contract pricing or any other gateway's contract pricing crossing that threshold would invert the cost-leader call. The threshold is computed against the published Bedrock list pricing — re-derive it for your contract before deployment.
- A reproducibility re-run on a different harness (one-shot, no agentic loop) where Qwen 480B no longer dominates. The 8.3 avg-turns count is the agentic-loop assumption; a one-shot harness with no loop budget would change the cost calculation entirely.

## Headline finding 2 — Below the Sonnet tier, no OSS we tested can replace Anthropic on this task surface

**Invalidation conditions:**

- A sub-Sonnet OSS model that passes 20+ out of 24 on this portfolio. As of evaluation, the closest sub-Sonnet OSS contender that passed was MiniMax M2.5 at 17/24 (B partial) — close enough that a more capable next-generation OSS release could plausibly cross the line within 6 months.
- The pass criterion is relaxed (e.g., 5-of-8 task families instead of 8-of-8). MiniMax M2.5 and Kimi K2.5 both pass T1–T7 reliably; if T8 (refactor → test → document multi-loop) is downgraded to optional, the partial cluster becomes "viable on scoped surfaces", which the report already acknowledges.

## Headline finding 3 — The failure signature below Sonnet scale is scale-driven, not vendor-driven

**Invalidation conditions:**

- A sub-Sonnet OSS model from a fifth vendor family (i.e., not Alibaba, DeepSeek, Mistral, Google) that passes the matrix. The current finding rests on four vendor families failing at the loop level with similar break shape. One success from a fifth family would broaden the scale-vs-vendor finding; two successes would invert it.
- Identification of a model-architecture variable (e.g., MoE expert count, attention-head topology) that systematically separates the failing OSS from the passing OSS. The report currently uses "scale" as a proxy for whatever's actually doing the work; if a specific architectural feature explains the failure mode, "scale-driven" becomes misleading.

## Headline finding 4 — The adapter incidentally became a structured telemetry plane

**Invalidation conditions:**

- This is operationally true (the JSON records are in InfluxDB today) — not really falsifiable as a binary observation. The contingent claim is that *centralising the adapter into DIAL preserves the telemetry property*. That would be invalidated if DIAL's ingress codepath constraints prevent the per-request JSON record (e.g., DIAL's middleware pipeline strips arbitrary fields by default). The §10 productionisation pilot would expose this within the first week.

## Architectural ask — Layer C enables per-tenant analyses

**Conditions under which the ask would change shape:**

- EPAM (or any operating organisation) data-governance policy forbids the proposed business-identity headers on each Claude Code request. The Layer C tag set assumes the gateway is permitted to retain `project_code` / `team_id` / `industry_vertical` per request; if data-governance forbids it, the analyses in §07–§09 are not achievable on this stack.
- The Layer C tags can be wired but the cardinality explodes beyond what InfluxDB can index efficiently. Empirically unlikely (project + team + industry produces ~thousands of tag combinations on a delivery firm's scale), but worth a separate measurement during the §10 pilot.

## Methodology

If any of these invalidations is observed, the right response is to open an issue on this repository with the new measurement attached. The bar (the criteria + methodology) is the durable artefact; specific magnitudes expire when models, prices, or gateway behaviour change.
