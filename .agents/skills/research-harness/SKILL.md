---
name: research-harness
description: Run durable long-horizon research and iterative experiment campaigns with Codex. Use for multi-turn research, autoresearch, training campaigns, reproductions, ablations, or work likely to survive compaction/restarts. Do not use for short one-off questions, simple bug fixes, or a single quick command.
---

# Research Harness

Run long-horizon research as a durable state machine rather than a conversation that happens to be long.

## Authority order

When sources disagree, use this precedence:

1. the user's latest explicit change to the overall objective;
2. `.research/RESEARCH_BRIEF.md`;
3. the active run's `RUN_SPEC.md`;
4. `.research/STATE.md`, `DECISIONS.md`, `EVIDENCE.md`, the experiment ledger, and session handoff files;
5. conversation history or compacted memory.

Conversation memory is working memory, not the source of truth.

## Start a campaign

1. Read the user's original request.
2. Create `.research/` if it does not exist.
3. Create `.research/RESEARCH_BRIEF.md` from `assets/RESEARCH_BRIEF.md`.
4. Copy the user's original request verbatim into `Original Request` before summarizing it anywhere else.
5. Fill in the core question, why the work matters, non-goals, critical distinctions, evidence standard, success criteria, and campaign stop conditions.
6. Do not modify the brief later unless the user explicitly changes the research objective. Record ordinary steering in `STATE.md` or `DECISIONS.md` instead.
7. Create `STATE.md`, `EVIDENCE.md`, `DECISIONS.md`, and `EXPERIMENTS.tsv` from this skill's assets.
8. If the work is long-running or likely to cross compaction/restarts, invoke `session-memory` and create a durable session checkpoint.

Before spending meaningful compute, convert vague campaign limits into explicit values: experiment count, absolute or relative time budget, per-run budget, target metric, or another measurable termination condition.

## Separate campaign policy from run policy

Campaign policy answers:

- What overall question are we trying to answer?
- How many experiments or how much total budget may be used?
- What result would end the campaign?

Run policy answers:

- What hypothesis does this one run test?
- How long must it run before its evidence is representative?
- When may it be reviewed?
- What conditions authorize immediate versus review-gated stopping?

Never use a campaign-level statement such as "do not stop early" as a substitute for a run-level intervention policy.

## Experiment loop

For each experiment:

1. State one concrete hypothesis.
2. Choose a clean parent state: baseline for a clean A/B comparison, or a previously validated improvement for a cumulative experiment.
3. Change the smallest practical set of major factors. Avoid changing many unrelated variables at once.
4. Create `.research/runs/<run-id>/RUN_SPEC.md` from `assets/RUN_SPEC.md` before launch.
5. Record the hypothesis, parent, configuration delta, authoritative metric, expected horizon, minimum evidence horizon, review gates, hard stops, soft stops, and success criteria.
6. If the run is more than a smoke test or has expensive/long training dynamics, invoke `training-controller` before launch.
7. Treat smoke tests as plumbing validation only unless they actually satisfy the evidence horizon defined for the hypothesis.
8. Launch only after the campaign plan authorizes the required compute.
9. During the run, update beliefs freely but change actions only according to the active run policy.
10. When the run completes or validly stops, write its result to `EVIDENCE.md` and append a row to `EXPERIMENTS.tsv`.
11. Mark the experiment outcome with a factual status such as `keep`, `discard`, `crash`, `inconclusive`, or `complete`; explain why in `DECISIONS.md` if the result changes the research trajectory.
12. Re-check campaign stop conditions before launching another experiment.

## Re-anchor after compaction or handoff

Do not continue from compacted memory alone.

1. Re-read `RESEARCH_BRIEF.md` from disk.
2. Read the latest `session-memory` handoff and state files when present.
3. Read the active `RUN_SPEC.md` if a run is in progress.
4. Read the latest experiment-ledger row and relevant evidence.
5. Verify current git branch/status and the actual training/job state when applicable.
6. Restate internally: original objective, non-goals, campaign stop conditions, active hypothesis, intervention state, and next review gate.
7. Only then continue.

## Drift control

Invoke `drift-audit`:

- after several experiments in one direction;
- before a major research-route change;
- after repeated compactions or a long gap;
- before final synthesis;
- whenever the current work is interesting but its connection to the original question is unclear.

New ideas are candidates, not automatically new experiments. Store attractive but nonessential directions in `DECISIONS.md` or a candidate list rather than immediately consuming compute.

## Final synthesis

Before writing a final conclusion:

1. Re-read `RESEARCH_BRIEF.md` from disk.
2. Check every success criterion.
3. Separate evidence, inference, and speculation.
4. Report unresolved questions explicitly.
5. Explain meaningful discarded routes and methodological limitations.
6. Do not use experiment count as a proxy for evidence quality.

## Companion skills

- `session-memory`: durable checkpoints and recovery.
- `training-controller`: in-run intervention authority.
- `drift-audit`: top-down goal alignment check.
