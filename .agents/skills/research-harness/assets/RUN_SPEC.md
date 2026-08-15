# Run Spec

- Run ID: <run-id>
- Created: <timestamp>
- Parent / baseline: <commit, checkpoint, or experiment id>
- Status: planned

## Hypothesis

<One falsifiable or decision-relevant hypothesis.>

## Change Under Test

<Describe the smallest meaningful configuration/code/data change.>

## Authoritative Metrics

- Primary: <metric and source>
- Secondary: <metric and source>

## Expected Completion Horizon

- Steps / epochs / wall time: <value>

## Minimum Evidence Horizon

Before this horizon, metric quality may update beliefs but must not authorize a soft stop.

- Steps / epochs / wall time: <value>
- Rationale: <why evidence before this point is not representative>

## Review Gates

- <gate 1>
- <gate 2>
- <gate 3>
- Final: <completion horizon>

## Hard-stop Conditions

These may authorize immediate intervention from any running state. Define objective conditions before launch.

- <crash / invalid experiment / persistent NaN / infrastructure failure condition>
- <condition with persistence threshold>

## Soft-stop Conditions

These may authorize stopping only at an eligible review gate.

- Minimum eligible review gate: <gate>
- Required consecutive failed reviews: <N>
- Failure criterion: <precommitted threshold>

## Success Criteria

- <criterion>

## Intervention Budget

- Major factors allowed to change after this run: <guidance>
- Cooldown / next minimum evidence horizon after a material change: <value>

## Launch Command

```bash
<command>
```

## Logging / Checkpoint Paths

- Logs: <path>
- Checkpoints: <path>

## Prelaunch Confirmation

- [ ] Hypothesis is concrete.
- [ ] Minimum evidence horizon is defined.
- [ ] Review gates are defined.
- [ ] Hard and soft stops are distinct.
- [ ] Success criteria are defined.
- [ ] Compute use is authorized by the campaign plan.
