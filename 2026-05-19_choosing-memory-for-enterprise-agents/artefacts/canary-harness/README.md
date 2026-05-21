# Canary harness — the durable artefact

The [memory-substrate report](../../) makes a load-bearing promise in §11 and §12: *"the canary harness is the durable artefact"* and *"publishes the canary harness so the next account team can re-instantiate it on their corpus in a day."*

This directory honours that promise. Not as runnable code (the actual harness is wired to a specific deployment and validators), but as the **harness shape** — the protocol, the fixture format, the scoring rubric, and an example fixture in a neutral domain — which is the form that actually transfers.

A practitioner with comparable LLM-call tooling, a corpus to evaluate against, and 60–80 paired questions can implement this on the substrate of their choice in a day or less.

## What's here

| File | Purpose |
|------|---------|
| [`README.md`](README.md) | This file. The protocol description + the re-instantiation checklist. |
| [`schema.md`](schema.md) | JSONL input/output schema for the paired-question fixture and the judged-record output. |
| [`example-fixture.jsonl`](example-fixture.jsonl) | 4 paired questions (4 JSONL records) on a neutral domain (the Linux kernel's documented `sched_ext` scheduler interface). Concrete enough to validate a harness implementation; specific enough to NOT leak the SDLC corpus. |

## The protocol

The harness implements one job: given two retrieval substrates and a fixture of paired questions, produce a position-swap-judged comparison with the 5-label scoring rubric and the pre-registered rule-change threshold.

### 1. Inputs

- **Substrate A** and **Substrate B**: each presents a `retrieve(query: str) -> str` interface that returns up to N tokens of retrieved context for a query. The harness does not care what's inside — chunk-text, entity-graph, filesystem grep, whatever.
- **Fixture**: a JSONL file with N paired questions (recommended 60-80). Schema in [`schema.md`](schema.md).
- **Judges**: two LLM endpoints, from different model families. The harness does not care which providers — any pair where the cost / latency profile is acceptable.
- **Pre-registered threshold**: from [`../methodology.md`](../methodology.md) §5 — `≥20pp absolute gap` OR `≥2× fabrication-rate ratio` OR `CI on win-rate gap excludes zero at 95%`.

### 2. Run sequence

For each question in the fixture:

1. Substrate A retrieves; record `retrieval_a`.
2. Substrate B retrieves; record `retrieval_b`.
3. Judge 1 sees `(question, retrieval_a, retrieval_b)` — picks the better retrieval, applies the 5-label rubric to each.
4. Judge 1 sees `(question, retrieval_b, retrieval_a)` — swapped ordering. Picks again, applies rubric again.
5. Judge 2 sees both orderings. Picks twice, applies rubric twice.
6. Collapse: a pair "wins" only when the same candidate is preferred by the same judge in both orderings, AND both judges agree.

Total LLM-judge calls per fixture: `N × 2 orderings × 2 judges = 4N`. For N=64, that's 256 calls per substrate pair.

### 3. Aggregation

Per task-family (see [`../task-families.md`](../task-families.md) for the family taxonomy):

```text
family_win_rate(A, family) = count(pair wins where pair.family == family AND winner == A)
                           / count(pair.family == family)
```

Per substrate aggregate, both ways:

```text
uniform_score(A)    = mean over families of family_win_rate(A, family)
weighted_score(A)   = Σ over families of family_weight × family_win_rate(A, family)
```

**Publish both numbers.** Where they diverge, the divergence is the finding.

Fabrication counts:

```text
fab_count(substrate) = count of distinct question_id where any judged record marks that substrate's retrieval `hallucinated` (any judge, any ordering)
```

Apply the pre-registered threshold against `weighted_score`, against `fab_count` ratio, against the CI on `weighted_score(A) - weighted_score(B)`.

### 4. Output

A JSONL file of per-trial judged records (schema in [`schema.md`](schema.md)). Plus the aggregate scores. Plus the threshold-pass decision.

## Re-instantiation checklist

To put this on your own stack in a day or less:

- [ ] Identify the corpus class. (SDLC-history? Business / domain? Other?) — see [`../task-families.md`](../task-families.md) for the discriminating dimensions.
- [ ] Pick the 8 task families that match your corpus. Use [`../task-families.md`](../task-families.md) as the starting taxonomy; substitute where needed.
- [ ] Sample your production query log to derive frequencies. Publish them up front.
- [ ] Pre-register the rule-change threshold (the §5 thresholds are a starting point; calibrate to your corpus size).
- [ ] Write 60–80 paired questions covering your 8 families. Hold this set out from any model training or substrate tuning that follows.
- [ ] Stand up two retrieval substrates with the `retrieve(query) -> context` interface.
- [ ] Pick two LLM judges from different model families. Wire them through whatever gateway you use in production (this matters — judge behaviour across gateways at temperature 0 is plausibly invariant but not separately measured by this report).
- [ ] Run the protocol above. Emit JSONL per [`schema.md`](schema.md).
- [ ] Apply the threshold. Publish both aggregates, the per-family table, and the scope limits.
- [ ] If the result clears the threshold, the durable artefact is the harness + the bar + the section arc of the deployment-decision memo — not the magnitudes.

## What this harness does NOT do

- Does not include the LLM call client itself. Use `openai`, `anthropic`, `litellm`, or whatever your stack already runs.
- Does not include the substrate implementations. The whole point is that you bring your own; the harness measures.
- Does not include scoring beyond the 5-label rubric. If you need richer scoring (e.g., per-criterion grades on the retrieved chunks), extend the rubric in [`schema.md`](schema.md) before running — not after, to avoid post-hoc threshold drift.
- Does not handle the closed-loop pilot (§07). That's a different protocol with executor-in-the-loop counting; the retrieval canary above isolates the substrate from the executor.

## Why the report doesn't ship runnable code

Two reasons stated in §11 + the [parent README](../README.md):

1. The validators that judged this report's 128 paired trials are the held-out fixture. Publishing them contaminates re-runs.
2. The LLM-call adapter wiring in the actual harness is tied to a specific deployment, project keys, and rate-limit posture. Publishing that wiring would expose information that doesn't transfer.

The shape is the durable thing. Code is not the contribution; the protocol + threshold discipline + scope-statement discipline is.
