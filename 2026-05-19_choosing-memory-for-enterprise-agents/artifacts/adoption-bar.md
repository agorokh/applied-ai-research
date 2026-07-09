# Adoption bar — five-criterion rubric

The five criteria used to evaluate memory-substrate candidates in [the report](../). Stated in standalone form so any reviewer can run the same bar against a different candidate, and so the Tencent rejection in §08 is reproducible against a public rubric.

The bar is stated **before** any candidate is scored. A bar applied post-hoc rationalises a decision already made; a bar applied a priori constrains the decision.

## The five criteria

| Criterion | Weight | Pass bar | What it asks |
|---|---|---|---|
| **Integration surface** | 0.25 | Python-callable read path, MCP-compatible agent interface, multi-tenant per-workspace mode | Does the candidate ship the integration shape the consuming stack already runs? Same-language parity with the consumer code. |
| **Install hygiene** | 0.20 | Clean install — no post-install scripts that patch sibling packages, modify the host environment, or silently fall through on error | Does installing the candidate leave third-party software in the host environment unchanged? |
| **Test coverage in the public surface** | 0.20 | Suite present and non-trivial (i.e., the test runner is configured AND there are test files that exercise the public API) | A wired-but-empty test harness fails this. |
| **Maintenance posture** | 0.15 | ≥2 active contributors, ≥6 months project age, sustainable release cadence | Has the project surfaced common bugs and stabilised the API? |
| **Operational fit** | 0.20 | Model calls routed through the sanctioned-inference gateway (here, EPAM DIAL), telemetry via the existing observability stack, secrets via a managed secret store | Does the candidate fit the team's actual delivery surface, or does it require bespoke infrastructure the platform team would maintain indefinitely? |

## Why these weights

The weights are calibrated to **one specific delivery context** — a Python-first stack running through the EPAM DIAL gateway with an MCP-compatible agent surface. A team with a TypeScript-only stack would weight "integration surface" differently; a team with no gateway requirement would re-state "operational fit"; a team in a research context where rapid prototyping matters more than long-term maintenance would weight "maintenance posture" near zero.

**The discipline is to publish the bar.** The contents of the bar are domain-specific; the act of stating it up front is what makes the rejection reproducible.

## Tencent DB Agent-Memory scorecard (re-rendered from §08)

| Criterion | Status on the candidate | Verdict |
|---|---|---|
| Integration surface | Distributed primarily as a TypeScript / Node package targeted at a single coding-agent framework. The consuming stack is Python-first; no Python integration surface ships. | **fail** |
| Install hygiene | The package's post-install step rewrites a sibling package's runtime files on install, silently falling through on error. Canonical supply-chain pattern treated as a fail. | **fail** |
| Test coverage in the public surface | Test harness wired (test runner configured, test commands in the build manifest); a search for test files in the published source surface returns zero. The harness exists; the suites do not. | **fail** |
| Maintenance posture | Project age at evaluation: roughly six weeks at most recent release. Two contributors visible in the public history; one author responsible for the majority of commits. | **partial** |
| Operational fit | No MCP server surface for agent integration; no graph database (depends on a local vector store and a third-party vector-DB SDK); no fit with the per-workspace HTTP server pattern or with DIAL-gateway-routed model calls. | **fail** |

**Net**: 4 fails, 1 partial. The decision is reproducible against the stated bar; another reviewer applying the same bar to the same project would reach the same conclusion.

The project may mature into a serious option; against the bar today, it does not fit. The four-of-five failure does not say the project is poorly designed — the four-layer pipeline idea is reasonable, the lack of an MCP surface is a deliberate choice given the framework it targets, and the post-install patch is solving a real integration problem in its host framework. **"Did not fit this adoption bar" is not the same as "is a bad project".**

## Re-use the bar

The starting point for using this bar on a different candidate:

1. State the candidate version under evaluation (project + commit hash or release tag).
2. Score each criterion against the candidate's public surface — never internal artefacts you have private access to.
3. Document the evidence per criterion in a table identical in shape to the Tencent scorecard above.
4. Re-evaluate when the candidate ships material changes against the failing criteria. The bar is permanent; the rejection is re-evaluable.

For a different stack (different language, different gateway, different agent surface), restate the bar with the same five-criterion shape but criteria calibrated to your context. The pattern transfers; the specific pass thresholds do not.
