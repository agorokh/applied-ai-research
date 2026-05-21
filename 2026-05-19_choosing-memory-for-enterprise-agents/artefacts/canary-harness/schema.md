# Canary harness — schema

JSONL input/output formats for the paired-question fixture and the judged-record output.

## Input — paired-question fixture

One JSON object per line. Each line is one **paired question**: the same query is run through both substrates, then judged across two orderings and two judges.

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | yes | Stable identifier for the question. Used in output records for trace-back. Format suggestion: `<family-prefix>-<NNN>`. |
| `family` | string | yes | Task-family classification. One of: `current_canonical`, `handoff_continuity`, `entity_disambiguation`, `temporal_supersession`, `multi_hop`, `knowledge_update`, `abstention_false_premise`, `link_graph`. (See [`../task-families.md`](../task-families.md).) |
| `query` | string | yes | The actual question text the substrate retrieves against. |
| `expected_label` | string | optional | One of the 5 rubric labels: `correct`, `partial`, `incorrect`, `abstained`, `hallucinated`. Use when you know what the "right" retrieval looks like; the judge will check against this. Omit for questions where the right behaviour is "any defensible retrieval is acceptable". |
| `expected_doc_id` | string | optional | If the expected retrieval should point at a specific source document, name it here. Lets the harness check `incorrect` (real but wrong source) vs `correct`. Omit if no single expected source. |
| `notes` | string | optional | Free text — for example, why this question is in the fixture, what edge case it exercises. Useful for human review; the harness ignores it. |

### Example

```jsonl
{"id": "current_canonical-001", "family": "current_canonical", "query": "What is the current sched_ext eviction policy when the BPF program returns SCX_ENQ_REENQ?", "expected_label": "correct", "expected_doc_id": "Documentation/scheduler/sched-ext.rst", "notes": "Tests literal-source retrieval on a documented kernel interface; the answer is one paragraph in one file."}
```

## Output — judged-record JSONL

For each input paired-question and each (judge × ordering), the harness emits one JSON object.

### Fields

| Field | Type | Description |
|---|---|---|
| `question_id` | string | From input. |
| `family` | string | From input. |
| `judge` | string | Identifier for the judging model. Recommended format: `<provider>:<model>:<version>`. |
| `ordering` | string | `a_first` or `b_first`. |
| `substrate_a_id` | string | Identifier for substrate A. |
| `substrate_b_id` | string | Identifier for substrate B. |
| `retrieval_a` | string | The actual retrieved context from substrate A (truncated to a publication-safe length if needed). |
| `retrieval_b` | string | Same for B. |
| `winner` | string | One of: `a`, `b`, `tie`. The judge's choice for this ordering. |
| `label_a` | string | The 5-label score for retrieval A. One of: `correct`, `partial`, `incorrect`, `abstained`, `hallucinated`. |
| `label_b` | string | Same for B. |
| `judge_rationale` | string | One-line free-text explanation from the judge. Useful for spot-checking judge sanity; not used by aggregation. |
| `elapsed_ms` | int | Wall-clock for this single judge call. |
| `cost_usd_estimate` | float | Optional. Token cost at the judge's listed rates. |

### Example

```jsonl
{"question_id": "current_canonical-001", "family": "current_canonical", "judge": "anthropic:claude-sonnet-4.6:bedrock", "ordering": "a_first", "substrate_a_id": "lightrag:v2.3", "substrate_b_id": "graphiti:v0.8", "retrieval_a": "...literal chunk from sched-ext.rst...", "retrieval_b": "...summarised entity-graph response...", "winner": "a", "label_a": "correct", "label_b": "partial", "judge_rationale": "A returns the literal documented policy; B returns a paraphrase that drops the SCX_ENQ_REENQ specifics.", "elapsed_ms": 1843}
```

## Position-swap collapse

The harness consumes the output JSONL and applies the collapse rule:

```
For each (question_id, judge):
  ordering_a = the record with ordering == "a_first"
  ordering_b = the record with ordering == "b_first"
  if ordering_a.winner == "a" AND ordering_b.winner == "a": pair_winner[judge] = "a"
  elif ordering_a.winner == "b" AND ordering_b.winner == "b": pair_winner[judge] = "b"
  else: pair_winner[judge] = "tie"

For each question_id:
  if pair_winner[judge1] == pair_winner[judge2]: final_winner = pair_winner[judge1]
  else: final_winner = "tie"
```

The `pair_winner` per-judge result is itself useful for diagnostic — judges that disagree often signal a question that exercises judge-family bias. The final `tie` rate is the position-swap inflation; it discards information but rules out the position-bias artefact.

## Aggregation reference

See [`README.md`](README.md) §3 for the per-family + per-substrate aggregation formulas, and [`../methodology.md`](../methodology.md) §6 for the uniform vs frequency-weighted derivation.

## Hallucination counting

```
fabricated_retrievals(substrate) = count of records where (substrate_a_id == substrate AND label_a == "hallucinated")
                                 + count of records where (substrate_b_id == substrate AND label_b == "hallucinated")
```

Apply per-substrate, then take the ratio across substrates for the rule-change threshold check.

## Schema versioning

This is **v1** of the schema. Future revisions (additional rubric labels, per-criterion grade breakdowns, multi-judge consensus weighting) will bump to `v2` and ship side-by-side; v1 will remain valid for re-running this report's protocol.
