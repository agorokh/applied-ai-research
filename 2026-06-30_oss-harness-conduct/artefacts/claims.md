# Claims ledger

Every load-bearing claim in ai-07, with its evidence and status. A claim that
cannot be shown from an artefact is marked as an observation, so a reader can tell
a measured fact from a single-run impression.

| # | Claim | Evidence | Status |
|---|---|---|---|
| 1 | All three open models solved an identical controlled bug-fix perfectly, four of four tests green, one turn, four to five tool calls, test untouched. | Controlled-run outcomes and per-model tool timelines. | **Measured.** Validator-judged, no model-as-judge. |
| 2 | Tool economy on the controlled task: GLM 4 calls, Qwen 5, Kimi 5; Kimi and Qwen each read twice before editing. | Per-model controlled timelines. | **Measured.** |
| 3 | GLM 5.2 recovered from a commit-gate rejection by satisfying the gate, root-caused its own shell-quoting bug from git status, and traced an un-closed issue to a commit trailer. | One governance-run timeline (sanitised). | **Observed**, single run. Shown in the timeline, not generalised. |
| 4 | Qwen 3.7 Plus preserved historical references while renaming only live ones, re-grounded git state after a timeout, and merged in thirty-three tool calls across fourteen turns. | One governance-run timeline (sanitised). | **Observed**, single run. Tool and turn counts are exact; the judgment reading is an impression of that run. |
| 5 | Kimi K2.7 Code has no governance run and is unrated under governance, not ranked below the others. | Absence of a Kimi governance timeline. | **Stated gap.** A missing measurement, reported as such. |
| 6 | The score average sorts opposite to the routing recommendation; the perfect row is one unstressed run. | The four-axis scores table. | **Measured** scores; the inversion is an interpretation of them. |
| 7 | A strict scan of 627 sessions found zero genuine faked-compliance; 328 narrated the step, 118 honest skips, 77 backed positive claims. | The compliance scan and its detector. | **Measured.** See `compliance-scan.md`. |
| 8 | The model the first read accused had been telling the truth; a session-start prefetch had performed its query. | The scan's backing check on that session. | **Measured.** |
| 9 | The score that docked Qwen on tool discipline was penalising the same phantom, so the corrected reading lifts its standing. | Cross-reading of the scores table against the scan. | **Inference**, stated as such in the note. |
| 10 | The per-model verifier was rejected because the deterministic memory gate already blocks an unbacked code-path query for every model alike. | The gate's behaviour and the corrected investigation. | **Design fact**, plus a decision. |

## Invalidation

What would overturn the note. The structural claim (a pass-or-fail task cannot
separate these three; conduct under the gates can) fails if a governance run shows
one of the open models flatly unable to drive the chain, or if a clean-task
benchmark is found that does separate them as sharply as the governance runs do.
The faked-compliance result fails if a session is produced that positively claims
a completed query with no backing and no disclosure. None has been found in 627.
The routing recommendation is provisional by construction: it is one run per
model plus two governance runs, scored once, and is meant to be re-run.
