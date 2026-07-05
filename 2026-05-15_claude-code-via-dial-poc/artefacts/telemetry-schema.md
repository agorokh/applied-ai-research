# Telemetry schema — adapter GFLog record

The ~30 fields the adapter writes on every `response_out`. Companion to [POC report](../) §04 (data plane) and §05 (telemetry layers).

## Layer separation

The report classifies fields into three layers:

| Layer | What | Status today |
|---|---|---|
| **A** | Fields already reaching InfluxDB measurements + Grafana dashboards. Operational health view. | Deployed. |
| **B** | Fields the adapter captures in its JSON log but does not currently promote to InfluxDB tags. Mechanical to wire, no client change required. | Promotion is a one-line exporter patch per field. |
| **C** | Fields that would require business-identity headers Claude Code is not sending today. | Requires the operating organisation's data-governance review + header-allowlist policy. |

## Layer A — captured today, in InfluxDB and Grafana

These fields land as Influx tags or fields on every `response_out`. They power the operational dashboard.

| Field | Type | Source | Tag / field | Example |
|---|---|---|---|---|
| `model_id` | string | translation adapter | tag | `claude-sonnet-4.6` |
| `target_model_family` | string | adapter (derived from `model_id`) | tag | `anthropic` |
| `client_name` | string | adapter (`User-Agent` header parse) | tag | `claude-code-cli` |
| `request_ts` | timestamp | adapter | field | `2026-05-14T18:19:42.103Z` |
| `tokens_input` | int | upstream response | field | `1547` |
| `tokens_output` | int | upstream response | field | `412` |
| `cost_usd_estimate` | float | adapter (Bedrock-priced) | field | `0.00712` |
| `elapsed_ms` | int | adapter timing | field | `2841` |
| `ttft_ms` | int | adapter timing (first token) | field | `412` |
| `cache_control_strat` | string | adapter cache policy | field | `forwarded` / `stripped_oss` |
| `final_stop_reason` | string | upstream response | field | `end_turn` / `max_tokens` / `tool_use` |
| `upstream_provider` | string | adapter (resolved from DIAL routing) | tag | `bedrock-us-east-2` |

## Layer B — in the wire, not yet promoted to tags

These fields exist in the adapter's JSON log record today but are written as InfluxDB *fields*, not *tags*. Promoting them to tags is mechanical — change the InfluxDB write to include them in the tag set on the line-protocol record.

| Field | Type | Source | Why it matters | Lift |
|---|---|---|---|---|
| `session.id` | UUID | Claude Code session | Enables per-session cost-per-session curves, per-session loop-depth percentiles. | One-line exporter patch. |
| `tool_inventory_hash` | string (sha256:hex8) | adapter (tools[] array hash) | Enables agent-profile clustering: identify which tool-call patterns correlate with high completion. | Same. Cardinality concern: ~hundreds of distinct hashes across a delivery firm. |
| `mcp_servers_seen[]` | string array (joined to single tag) | adapter (MCP discovery in tools[]) | Enables per-tool routing analysis: which MCP integrations are in active use. | Same. Joining to a single tag is the standard pattern. |

## Layer C — requires business-identity headers

These fields are *not* in the wire today. Adding them requires a header allowlist policy at the operating organisation, plus the Claude Code wrapper script forwarding the headers.

| Field | Type | Source (proposed) | Why it matters | Pre-requisite |
|---|---|---|---|---|
| `project_code` | string | project registry (issue tracker) | Per-account cost reporting (Application A in §09). | Header allowlist + wrapper script. |
| `team_id` | string | enterprise SSO / org directory | Per-team cost curves (Application A, §08 Use Case 2). | Same. |
| `industry_vertical` | string | project metadata | Segment-specific fitness reports (Application B, §08 Use Case 1). | Same + a project-to-vertical mapping. |
| `use_case_label` | string | derived per request from commit-message + diff shape | Use-case-driven adaptive routing (Application C, §08 Use Case 3). | Adapter-side classifier or downstream join. |

## Wire format

Every `response_out` emits a single JSON line into `/var/log/adapter/gflog.jsonl`:

```json
{
  "ts": "2026-05-14T18:19:42.103Z",
  "request_id": "req-7f2c...",
  "session.id": "sess-bf91...",
  "model_id": "claude-sonnet-4.6",
  "target_model_family": "anthropic",
  "upstream_provider": "bedrock-us-east-2",
  "client_name": "claude-code-cli",
  "tokens_input": 1547,
  "tokens_output": 412,
  "cost_usd_estimate": 0.00712,
  "elapsed_ms": 2841,
  "ttft_ms": 412,
  "cache_control_strat": "forwarded",
  "final_stop_reason": "end_turn",
  "tool_inventory_hash": "sha256:a3f1d2e8",
  "mcp_servers_seen": ["repo-explorer", "test-runner"]
}
```

Layer-C fields (`project_code`, `team_id`, `industry_vertical`, `use_case_label`) would join this record once the header allowlist is in place.

## Sidecar exporters

Two sidecars tail this JSONL and write to InfluxDB:

| Sidecar | Measurement | Cadence | Tags vs fields |
|---|---|---|---|
| `gflog-to-influx-metrics` | `adapter_metrics` | per request | tag set = Layer A tag-marked; field set = Layer A fields + Layer B (until promoted). |
| `gflog-to-influx-events` | `claude_code_events` | per request | tag set = same as above; field set = expanded with `request_id`, `session.id`. |
| `gflog-to-influx-traces` | `claude_code_traces` | per request | tag set = same as `adapter_metrics`; field set = trace-oriented payload (tool-inventory deltas, MCP transitions) for drill-down dashboards. |

All three measurements are written today; Grafana queries them to populate the operational dashboard the report describes in §06 (KPI framework). `claude_code_traces` is the trace drill-down companion to the aggregate counters in `adapter_metrics` and the event stream in `claude_code_events`.

## Field cardinality concerns

Promoting Layer B fields to tags trades indexability for cardinality. The estimates (based on this deployment):

- `session.id`: ~100s of distinct values per day. High cardinality but standard for session-keyed analytics.
- `tool_inventory_hash`: ~tens of distinct values across a delivery firm — agents reuse standard tool kits.
- `mcp_servers_seen[]` joined: ~tens of distinct combinations.

Adding all three to the tag set adds ~thousands of tag-value cells per measurement per day. InfluxDB handles this comfortably at this scale. If the deployment grows by 10× or more, partition by date-bucket retention to keep the tag-cardinality bounded.

## What the schema does NOT include

- The actual `prompt` body. Never logged. Privacy + provider ToS.
- The actual `response` body. Same.
- Tool call payloads. Same.
- Per-trial Bedrock invoice rows (Bedrock side-channel; logged by AWS Cost Explorer separately, not by the adapter).
