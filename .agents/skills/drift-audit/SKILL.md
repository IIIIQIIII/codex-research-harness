---
name: drift-audit
description: Audit a long-running Codex research or experiment campaign for goal drift after compaction, many iterations, or an attractive side path. Use before major route changes and final synthesis. Do not use as a generic progress summary.
---

# Drift Audit

Judge the current trajectory from the original objective downward. Do not start from the current trajectory and invent reasons it is aligned.

## Audit procedure

1. Temporarily suspend the rationale in `STATE.md` and `DECISIONS.md`.
2. Read `.research/RESEARCH_BRIEF.md` from disk.
3. Read the `Original Request` verbatim before reading the current plan.
4. Independently derive:
   - the exact research question;
   - why it matters;
   - non-goals;
   - critical distinctions;
   - evidence standard;
   - success criteria;
   - campaign stop conditions.
5. Only then read `STATE.md`, `DECISIONS.md`, `EVIDENCE.md`, active `RUN_SPEC.md`, and recent experiment rows.
6. Classify current work into:
   - **direct**: clearly necessary to answer the brief;
   - **supporting**: useful but bounded supporting work;
   - **drift**: interesting work whose connection to the brief is weak or has expanded beyond the necessary scope.
7. Identify original requirements receiving too little attention.
8. Identify assumptions that entered through compaction, prior summaries, or repeated local optimization but are not actually in the brief.
9. Propose the next three actions as if starting today with the evidence already collected.

## Route-change test

Before a major route change, answer:

- What new evidence motivates the change?
- Which success criterion does the new route help answer?
- What current work should stop or be bounded?
- Is this a hypothesis update or an objective change?
- If it is an objective change, did the user explicitly authorize changing the research brief?

Do not edit `RESEARCH_BRIEF.md` for a mere hypothesis update.

## Output format

Produce a compact audit with:

```text
ORIGINAL QUESTION
<one paragraph>

DIRECTLY USEFUL WORK
<items>

POSSIBLE DRIFT
<items>

UNDEREXPLORED ORIGINAL REQUIREMENTS
<items>

NEXT 3 ACTIONS
1. ...
2. ...
3. ...

BRIEF CHANGE REQUIRED?
No / Yes, because the user explicitly changed ...
```

Do not continue research during the audit unless the user asks you to do so. The audit is a control checkpoint, not another exploration phase.
