# Claims ledger — Claude Code via EPAM DIAL · POC report

Every headline claim in [the report](../) tagged by category and pointed at the evidence row that backs it. Use this to distinguish "measured on this stack" from "inferred from the same data" from "recommendation grounded in the measurement" from "hypothetical scenario sketched to show what the data would unlock."

## Legend

| Category | Meaning | Strength of claim |
|---|---|---|
| **measured** | Direct observation from the 192 trials or from the telemetry the adapter emits today. | Strongest. Subject to the §11 caveats but the number is on-stack. |
| **inferred** | Conclusion drawn from the measured data, not directly observed. | Weaker. Holds under stated mechanism; new data could invert. |
| **hypothetical** | Scenario described to illustrate the form of an analysis. Numbers are illustrative, not measured. | Not a claim. Sets up an architectural ask. |
| **recommendation** | Proposed deployment default or productionisation step. Grounded in measured + inferred rows above. | Action item, not a finding. |

## Ledger

| # | Report § | Category | Claim (verbatim or paraphrased) | Evidence pointer | Scope |
|---|---|---|---|---|---|
| 1 | Hero, §01 F2, §03 | **measured** | Qwen3-Coder 480B is the cheapest 100%-pass model at $0.101 per success. | 192-trial matrix, 8-model ranked table in §03. Bedrock list pricing per [`pricing-snapshot/`](pricing-snapshot/). | One stack, one task corpus, one date. List pricing only. |
| 2 | §01 F2 | **measured** | Qwen3-Coder 480B costs 38% below Haiku 4.5, 4.7× below Sonnet 4.6, 6.8× below Opus 4.7 on $/success. | Same table. | Same scope. |
| 3 | §01 F2, §03 | **measured** | Three OSS upstreams (Mistral Devstral 123B, Qwen3-Coder 30B-A3B, DeepSeek v3.2) fail the harness at the loop level. | 192-trial matrix; per-model pass counts in §03. | DeepSeek 0/24, Qwen 30B 9/24, Devstral retired after 8/21. Same harness; same agentic loop budget. |
| 4 | §01 F2, §03 | **inferred** | The failure signature is scale-driven, not vendor-driven. | Four vendor families (Alibaba, DeepSeek, Mistral, Google) all fail at the same loop level with similar break shape. | Inference from the cross-vendor distribution at the sub-Sonnet scale. Could be invalidated by a sub-Sonnet model that passes. |
| 5 | Hero, §01 F1, §02 | **measured** | 192 trials produced zero authentication incidents on the EPAM-compliant inference path. | Adapter audit log; manual review of the 192 request traces. | This deployment, this DIAL project key, this evaluation window. |
| 6 | §02 | **measured** | The bridge requires no Claude Code source modifications. | The harness is the shipped `claude` CLI; one environment variable + a wrapper script. | Specific to Claude Code 2.1; future CLI versions might change the env-var contract. |
| 7 | §02 | **measured** | The adapter strips `cache_control` on every non-Anthropic upstream (else DIAL returns `502 No route`). | Adapter code path; reproduced by inspecting the adapter's request handler. | DIAL gateway behaviour at evaluation time; the gateway team may resolve this. |
| 8 | §01 F3, §04, §05 (Layer A) | **measured** | Each `response_out` writes a structured JSON record with token counts, tool inventory hash, MCP servers seen, cache strategy, elapsed milliseconds, Bedrock-priced `cost_usd_estimate`. The record lands in InfluxDB measurements `adapter_metrics`, `claude_code_events`, `claude_code_traces`. | [`telemetry-schema.md`](telemetry-schema.md). | Operational reality of this adapter today; Grafana dashboards query these. |
| 9 | §01 F3, §05 (Layer B) | **inferred** | Three identifiers already in the wire (`session.id`, `tool_inventory_hash`, `mcp_servers_seen[]`) can be promoted to InfluxDB tags with no client change. | Exporter code path; the fields are present in the JSON record but currently emitted as InfluxDB fields, not tags. | Confidence is high but ungrounded until someone ships the exporter patch. |
| 10 | §01 F3, §05 (Layer C), §08 | **hypothetical** | Business-context tags (project, team, industry, use-case) would unlock per-tenant analyses. | Layer-C tags are not in the wire today; the three illustrative scenarios in §08 are sketches, not measurements. | The numbers in §08 use cases are not on this stack. |
| 11 | §03 (closing callout) | **inferred** | Below the Sonnet tier, no OSS in this matrix can replace Anthropic on this task surface. | Same matrix; conditioned on the 100%-pass cluster definition. | This task surface; this cluster definition. A more lenient pass criterion (e.g., 5-of-8 tasks) would change the conclusion. |
| 12 | §06 (KPI framework) | **measured / hypothetical** | Tiers 1 + 3 of the KPI framework are populated from current telemetry. Tier 2 requires the test-harness join. Tier 4 requires Layer C. | Tier 1 = Layer A direct emit. Tier 3 = the Bedrock-priced `cost_usd_estimate` field. Tier 2/4 numbers in the table are explicitly labelled illustrative. | Stated in the report; the illustrative numbers are not measurements. |
| 13 | §07 (Q1–Q5) | **hypothetical** | Five management-level questions become answerable once Layer C is wired. | None of Q1–Q5 are answerable on POC data today. The data joins are described in the methodology but not run. | Illustrative for any delivery firm running a coding-agent gateway. |
| 14 | §08 (Use cases A–C) | **hypothetical** | Three Layer-C-enabled scenarios (per-industry routing, per-team cost, per-task-class adaptive routing). | None of the per-scenario numbers are measured. | Labelled hypothetical in the report body. |
| 15 | §09 (Applications) | **inferred / recommendation** | Three application classes follow from the same Layer-C join. | The applications are achievable once the Layer-C tags exist; the report does not claim they exist today. | Architectural ask, not a deployed system. |
| 16 | §10 (Productionisation) | **recommendation** | Port the translation core into DIAL's ingress codepath, behind a feature flag. 2–3 friendly pilot projects, 2–4 week observation window. | The recommendation is grounded in claims 5, 6, 7, 8, 9 above. | Specific to the DIAL stack; the pattern generalises to any sanctioned-inference gateway. |
| 17 | §11 | **measured / scope** | Bedrock list-pricing ranking inside the 100%-pass cluster is stable under markup factors below ~6.7× on Qwen 480B input rates. | Sensitivity analysis on the Bedrock list rates; markup factor at which the Qwen-vs-Haiku ordering flips. | Inside the 100%-pass cluster only; the toy/partial tiers are not part of this sensitivity. |
| 18 | §11 | **scope** | All 192 trials originate from one engineer's laptop, one DIAL deployment, one network path. | Single-operator caveat. | Latency tails include single-network RTT variance that production deployments would see differently. |

## Use

When citing the report externally, quote the **measured** rows freely with the scope qualifier attached. Quote the **inferred** rows as "the report infers" or "the report's interpretation is". Quote the **hypothetical** rows only as scenarios, never as findings. The **recommendation** row is a proposal addressed to whichever organisation is deploying — including but not limited to the originating one.
