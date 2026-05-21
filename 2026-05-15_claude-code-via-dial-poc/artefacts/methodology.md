# Methodology — Claude Code via EPAM DIAL · POC report

Companion to [the POC report](../). This document specifies the test design, the 8-task portfolio shape, the costing formula, and the harness invocation pattern in enough detail that a practitioner could re-instantiate the evaluation on their own gateway with their own task set.

It deliberately does **not** publish the held-out T1–T8 prompts or the hidden `pytest` validators — those need to stay private for the harness to remain a fair fixture on re-runs.

---

## 1. Scope

| Parameter | Value | Notes |
|---|---|---|
| Harness | Claude Code 2.1 (unmodified) | The CLI shipped by Anthropic. Same binary used in all 192 trials. |
| Routing | Anthropic-shape ingress translated to OpenAI-shape outbound, forwarded to EPAM DIAL | The ~600-line translation adapter is open-source at [https://github.com/agorokh/sdlc-dial-adapter](https://github.com/agorokh/sdlc-dial-adapter); its conformance shape is also described in §5 below. |
| Upstreams measured | 8 | Claude Haiku 4.5, Sonnet 4.6, Opus 4.7 (Anthropic Bedrock); Qwen3-Coder 480B-A35B, Qwen3-Coder 30B-A3B (Alibaba); Kimi K2.5 (Moonshot); MiniMax M2.5; DeepSeek v3.2. Two additional candidates (Mistral Devstral 123B, Gemma 27B IT) were retired pre-matrix on smoke. |
| Trials per cell | 3 | Each (model × task) cell run three times, results aggregated. |
| Tasks per model | 8 | The held-out T1–T8 portfolio. |
| Total trials | 192 | 8 upstreams × 8 tasks × 3 runs. |
| Pricing source | AWS Bedrock pricing console, US East (Ohio), captured 2026-05-14 | Transcribed in [`pricing-snapshot/bedrock-us-east-ohio-2026-05-14.md`](pricing-snapshot/bedrock-us-east-ohio-2026-05-14.md). |
| Pricing reference window | 18:19–20:15 UTC, 2026-05-14 | Two evaluation waves run on the same calendar day to keep token prices comparable. |

## 2. The 8-task portfolio shape

The held-out tasks are NOT published — but their **shape** is. Each task family is one of the following functional classes, weighted equally in the matrix (each task = 1/8 of the model's pass-rate). The shape descriptions are sufficient to construct a comparable portfolio on a different corpus.

| Task ID | Functional class | What the agent has to do | Why it discriminates |
|---|---|---|---|
| T1 | Single-file generation against spec | Write a function that satisfies a written spec, in one file, with no tool calls. | Baseline. Distinguishes models that can't even produce syntactically valid code. |
| T2 | Multi-file generation with state | Add a feature across 2–3 existing files; state has to thread through. | Distinguishes models that only handle single-buffer tasks. |
| T3 | Bug fix from failing test | Locate the bug given the failing test; minimal patch. | Distinguishes models that overgenerate (rewrite half the file). |
| T4 | Refactor preserving behaviour | Restructure existing code; hidden validator checks behavioural equivalence. | Distinguishes models that "improve" the code in ways that change behaviour. |
| T5 | API integration | Use a documented library API to perform a task; library shape provided. | Distinguishes models with weak grounding in tool-call discipline. |
| T6 | Long-context comprehension | Answer a question that requires reading a ~5k-line file; the answer is at line ~3500. | Distinguishes context-budget behaviour and middle-of-context recall. |
| T7 | Trap comprehension | The prompt sounds like one task but a careful read makes a different task the right one. | Distinguishes models that pattern-match on superficial cues. |
| T8 | Refactor → test → document chain | A multi-step tool-call loop: refactor, write a new test, document the change. | Distinguishes models that sustain multi-turn state across loops. |

All eight tasks have hidden `pytest` validators that decide pass/fail. Hidden = the model never sees the validator code; only the human-written task prompt.

### Pass criterion per task

Pass = the validator reports zero failures within a 15-turn agentic loop budget. Partial pass is collapsed to **fail** for matrix aggregation; partial-credit scoring would let weak models accumulate noise.

## 3. Aggregation

For each model, the published pass rate is:

```text
pass_rate = (number of (task, run) cells where validator passed) / (8 tasks × 3 runs)
          = N_pass / 24
```

The published $/success is:

```text
total_bedrock_spend = Σ (tokens_in_i × $/M_in + tokens_out_i × $/M_out)  over all 24 cells
cost_per_success    = total_bedrock_spend / N_pass
```

When `N_pass = 0`, `cost_per_success = ∞`. When some passes exist, partial-pass cells still contribute to `total_bedrock_spend` (the model burned tokens; that token spend counts against the model's economics even on tasks where the validator failed).

The $/M rates used are the AWS Bedrock list rates captured 2026-05-14, US East Ohio. **Not** EPAM DIAL contract rates. See [`pricing-snapshot/`](pricing-snapshot/) for the rates table and Wayback URL.

## 4. Two-wave evaluation

The 192 trials were not run as a single block. Two evaluation waves:

| Wave | Time (UTC) | Models added | Trials | Reason |
|---|---|---|---|---|
| 1 | 2026-05-14 18:19 | Anthropic Haiku / Sonnet / Opus; Qwen3-Coder 480B; Qwen3-Coder 30B; DeepSeek v3.2 | 5 models × 8 tasks × 3 runs = 120 | First-pass viability cluster. Devstral and Gemma had been retired pre-wave on smoke. |
| 2 | 2026-05-14 20:15 | Kimi K2.5; MiniMax M2.5 | 2 models × 8 tasks × 3 runs = 48 (note: 72 reported because of an early Sonnet re-run) | Second-pass additional contenders surfaced after wave-1 results were inspected. |

Two-wave structure means inter-wave variance is possible but small at this sample size; both waves used the identical harness, identical task portfolio, identical DIAL routing, identical pricing snapshot.

## 5. Adapter conformance

The adapter is open-source at **[https://github.com/agorokh/sdlc-dial-adapter](https://github.com/agorokh/sdlc-dial-adapter)** — the reference implementation of the wire contract described below. The conformance shape, for reproducing it from scratch:

- **Ingress contract**: `POST /v1/messages` with the Anthropic Messages API shape (system + messages + max_tokens + temperature + stop_sequences + tools).
- **Egress contract**: OpenAI Chat Completions API shape, forwarded to the DIAL gateway via the engineer's project key.
- **Cache-control handling**: `cache_control` blocks on user/assistant messages are stripped on every non-Anthropic upstream (else DIAL returns `502 No route`). On Anthropic Bedrock upstreams, `cache_control` is forwarded unchanged.
- **SSE handling**: The adapter consumes the upstream's chat-completions SSE stream and re-emits it in the Anthropic streaming shape (`message_start` → `content_block_start` → `content_block_delta` → `content_block_stop` → `message_delta` → `message_stop`).
- **Per-request telemetry**: On every `response_out`, the adapter writes a structured JSON record into InfluxDB measurements `adapter_metrics`, `claude_code_events`, `claude_code_traces`. The field set is in [`telemetry-schema.md`](telemetry-schema.md).

A new adapter (re-implementing the above shape, or forking [https://github.com/agorokh/sdlc-dial-adapter](https://github.com/agorokh/sdlc-dial-adapter)) should be wire-compatible with the harness. The next iteration of the adapter — including the productionisation patches the report's §10 proposes — will ship in the same repository alongside follow-on research.

## 6. What the methodology is NOT

- Not a controlled benchmark. N = 24 per model is a viability test, not a measurement claim with confidence intervals.
- Not a vendor-comparison benchmark. The intent is "which of these can replace what we run today on this stack", not "rank these models on coding ability."
- Not portable to a different task corpus without re-measurement. A team running this approach on a different harness (different tasks, different validator harness, different agent CLI) should expect the rankings to shift; the cost-per-success *formula* is portable, the *numbers* are not.
- Not a statement about contract pricing. Bedrock list prices are the floor; EPAM DIAL contract pricing may include markup or discount that shifts absolute magnitudes (the report's §11 markup-factor caveat applies).

## 7. Re-instantiation on another stack

To reproduce the *shape* of this evaluation on your own gateway with your own task corpus:

1. Pick 8 task families that match the workload you actually care about. The shape descriptions in §2 are a starting point; substitute as appropriate.
2. Write hidden validators (e.g., `pytest` or equivalent) so the pass criterion is automatic.
3. Run 3 trials per (model × task) cell. Keep the agentic loop budget the same across cells.
4. Capture the same telemetry shape (tokens in / out, elapsed ms, stop reason, cost estimate at your gateway's pricing) per trial.
5. Aggregate per the formula in §3 using **your gateway's pricing**, then re-derive at vendor list pricing for cross-comparability.
6. Publish the ranking with the same caveats: list-pricing-only ranking, markup-stability range, no human-eval cross-check.

The pattern transfers. The specific numbers (Qwen3-Coder 480B at $0.101/success, etc.) do not — they are specific to this corpus, this date, and this stack.
