# Methodology: open models as drivers of a governance harness

Companion to the note *Three open models drove Claude Code through its governance
gates* (ai-07). This records how the runs were produced and scored, at enough
detail for another team to reproduce the shape of the result. Magnitudes are
corpus-specific and small; the method is what transfers.

## What is under test

The object of study is not the models in the abstract. It is three open-weight
coding models **as drivers** of a real agentic coding harness: stock Claude Code,
routed through a translation bridge at upstream models served by EPAM's DIAL
gateway. The three driver slots point at the open route: GLM 5.2, Qwen 3.7 Plus,
and Kimi K2.7 Code, as served on the date of the run. The bridge is the only
custom code on the path; the harness, system prompt, and tool inventory are
unchanged across models.

The harness is governed. On any non-trivial change the driver has to clear:

1. a **commit gate** that rejects an autostage which would add a file the change
   should not include;
2. a **deterministic memory gate** that hard-blocks a code-path edit when a
   mandatory memory query has not actually fired, decided from telemetry;
3. a **post-merge check** that the issue actually closed, not merely that a
   commit landed.

## Two instruments

**The controlled task (one per model).** A small numeric helper whose normalize
function divides by a count instead of a sum, so it crashes on an all-zero input,
shipped with a hidden test that fails until the function is fixed. The instruction
was narrow: fix the source, do not edit the test. Outcome is judged by the test
suite, not by a model-as-judge, so there is no prose-style bias. This instrument
measures clean-task competence only.

**The governance run (two of three models).** A real multi-step change driven all
the way to a merge through the governed chain above. This is where recovery,
judgment, tool economy, and protocol conduct become observable. GLM 5.2 and
Qwen 3.7 Plus each have one; Kimi K2.7 Code does not, and is therefore reported
as unrated under governance rather than ranked below the others.

## Scoring

Each run was scored on four axes (correctness, tool discipline, error recovery,
efficiency) and averaged. The averages are deliberately **not** treated as a
ranking in the note: a perfect average from the controlled-only model reflects an
unstressed task, while the two governance-tested models carry their only sub-five
marks precisely because they were stressed. The scoring was done by the author;
there is no second scorer. That is a stated limit, not a hidden one.

## The compliance scan

A separate, automated first read of the governance runs concluded that one model
had narrated a mandatory memory query it never performed. That conclusion was
tested against a strict detector over a 627-session corpus and **withdrawn**. The
detector, its definition, and its output are in `compliance-scan.md`; the
claim-by-claim status of every assertion in the note is in `claims.md`.

## Limits

One controlled run per model and two governance runs, on a single workstation and
one harness version, scored once by the author, with no human-eval cross-check.
This is enough to retire a benchmark that cannot separate the three models, and
not enough to settle their order. Treat every ranking as a routing prior and
re-run it before relying on it.
