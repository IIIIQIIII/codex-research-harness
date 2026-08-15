---
name: session-memory
description: Preserve and recover durable working state for long-running Codex research or experimentation across context compaction, disconnects, restarts, branch switches, and handoffs. Do not use for short tasks that can be reconstructed trivially.
---

# Session Memory

Persist enough verified state that a fresh agent can resume without relying on a summary of a summary.

## Core rule

Stable intent and mutable session state are different things.

- Stable intent lives in `.research/RESEARCH_BRIEF.md`.
- Session state records where the work is now.
- A handoff never replaces the research brief.

## Start or resume

Use `.research/session/<timestamp>/` for one working session.

Create:

- `session_state.md` from `assets/session_state.md`;
- `timeline.md` from `assets/timeline.md`;
- `files.md` from `assets/files.md`;
- `handoff.md` from `assets/handoff.md`.

When resuming an existing project:

1. Find the latest relevant session directory.
2. Read `.research/RESEARCH_BRIEF.md` first when it exists.
3. Read `handoff.md`, then `session_state.md`, then the recent tail of `timeline.md`.
4. Read the active run spec and latest experiment row when a run or campaign exists.
5. Verify claims against the actual repo, process/job state, logs, and git state before acting.

## Checkpoint rhythm

Checkpoint after:

- forming or materially changing the plan;
- meaningful code or configuration edits;
- launching or finishing a long-running command;
- starting or ending an experiment;
- switching branches/worktrees;
- receiving user steering that changes the current subtask;
- a review gate or intervention decision;
- completing a drift audit;
- before handoff or final response when work should remain resumable.

During active long-running work, update the session whenever enough state has changed that losing the current context would cause duplicated work or a wrong decision.

## Compaction recovery protocol

After context compaction, disconnect, restart, or a long gap:

1. Re-read the research brief from disk. Never reconstruct it from memory if the file exists.
2. Re-read the current handoff and state files.
3. Re-read the active run spec before touching a running experiment.
4. Verify git branch/status and the actual job/process state.
5. Verify the last authoritative metric directly from its source when practical.
6. Restate internally:
   - original objective;
   - current subtask;
   - non-goals;
   - campaign stop conditions;
   - active run and next review gate;
   - what interventions are currently authorized.
7. Append a recovery event to `timeline.md` with any discrepancy found.
8. Continue only after re-anchoring.

## Quality rules

- Keep session notes compact and factual; they are state, not a transcript.
- Keep the overall goal stable unless the user explicitly changes it.
- Record the current subtask separately so follow-up steering does not overwrite the overall objective.
- Record important failed checks and skipped verification.
- Do not store secrets, credentials, or large raw logs.
- Prefer links/paths to evidence over copying large outputs into session files.
- If old notes become large, summarize historical detail while preserving current next actions and unresolved risks.
