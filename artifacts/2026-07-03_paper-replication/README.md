# Replication evidence: SINDy (arXiv 1509.03580) through the paper-replication harness (arXiv 2607.02134)

Sanitized evidence bundle for the Applied Intelligence note ai-09
(["Done" is a workspace state, not a sentence](https://agorokh.github.io/applied-ai-research/notes/replication-gate.html)).
This is the complete workspace record of the run: everything the harness registered,
as it registered it, plus the run ledger and the compiled report.

The harness is the authors' released Claude Code skill, unmodified, pinned at commit
46ad437 of [PredictiveScienceLab/paper-replication-paper](https://github.com/PredictiveScienceLab/paper-replication-paper);
the driving agent was Claude (the paper's runs used Codex/GPT-5.4). Independent
replication report filed as
[issue #1](https://github.com/PredictiveScienceLab/paper-replication-paper/issues/1) on the release repo.

## Contents

- `reproduction_matrix.csv`: the final target inventory, 11 of 11 MATCHED, with
  pre-registered acceptance modes and tolerances.
- `targets.md`: the target plan as derived from the paper's claim inventory, with the
  recorded scope exclusion (cylinder-wake DNS example).
- `run_index.jsonl`: the full run ledger, superseded runs preserved. The four gate
  refusals live here and in the assumptions log.
- `assumptions_and_unknowns.md`: every setup hypothesis, and the resolution log for the
  superseded runs the validators refused.
- `validate_spec.json`, `validate_progress.json`, `validate_report.json`,
  `completion.json`: all four external validator outputs, including the completion gate.
- `metrics/`: per-target comparison metrics under each target's acceptance rule.
- `provenance/`: per-target provenance records as registered at MATCHED time
  (run_id, artifact sha256, code/config/trace sha256, method components, seed).
- `figures/`: all generated figures.
- `replication_report.pdf`: the compiled replication report (presentation copy: byline
  neutralized for publication; content identical to the run artifact).

## Sanitization note

Command and path strings in `run_index.jsonl` and the validator JSONs were rewritten to
host-neutral forms (`python3 ...`, `<workspace>/...`) before commit. No hashes, run ids,
timestamps, metrics, or outcomes were altered. The method implementation itself
(`src/`, `configs/`) was a session-local reconstruction from the paper text under
`author_code_policy=forbid_by_default` and is not part of this record; its sha256
fingerprints are pinned in `provenance/`.
