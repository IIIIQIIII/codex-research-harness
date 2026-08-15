---
name: training-controller
description: Control long-running ML/RL training interventions with protected evidence windows, review gates, hard stops, soft stops, and hysteresis. Use when Codex monitors or manages expensive/noisy training runs. Do not use for trivial smoke tests or jobs where stopping policy is irrelevant.
---

# Training Controller

Prevent two opposite failure modes:

- premature pivoting because noisy early metrics look bad;
- pathological conservatism because a blanket instruction says not to stop.

The solution is explicit intervention authority, not stronger prose such as "do not stop early."

## Fundamental separation

**Diagnosis does not imply intervention.**

Codex may continuously update its belief about a run. It may only change the run when the active policy authorizes that action.

When reporting a running experiment, separate:

```text
BELIEF: what the evidence currently suggests.
ACTION AUTHORITY: what may be done right now under the run spec.
```

## Require a precommitted run policy

Before a meaningful training run starts, ensure its `RUN_SPEC.md` defines:

- expected completion horizon;
- minimum evidence horizon;
- review gates;
- hard-stop conditions;
- soft-stop conditions;
- required persistence / consecutive failed reviews;
- success criteria;
- authoritative metrics and log sources.

If these are missing, define them before launch. Do not invent a new stopping rule after seeing an inconvenient metric unless the user explicitly changes the policy.

## State machine

Use these conceptual states:

### PRELAUNCH

The run has not started. Validate configuration, data, logging, checkpoints, and the run policy.

### PROTECTED

The run has started but has not reached the minimum evidence horizon.

Allowed:

- inspect logs and resource utilization;
- update beliefs;
- record hypotheses for later review;
- prepare candidate follow-up experiments.

Not allowed:

- metric-driven soft stopping;
- changing hyperparameters or strategy because convergence looks slow;
- restarting merely because another route now seems more attractive.

Exception: a declared hard-stop condition is actually met.

### OBSERVE

The minimum evidence horizon has been reached, but the run is between review gates.

Continue observing. Poor intermediate metrics are evidence, not stop authority.

### REVIEW

A predeclared review gate has been reached. Evaluate the run against criteria committed before seeing this gate's result.

A soft stop may be authorized only if its persistence and threshold requirements are satisfied.

### INTERVENE

A hard stop is active, or a soft stop is authorized at a review gate.

Before changing route:

1. preserve useful logs/checkpoints when practical;
2. record the observed evidence;
3. record why the intervention is authorized;
4. state the next hypothesis;
5. change one major factor at a time when practical;
6. give the replacement run a fresh minimum evidence horizon.

### COMPLETE

The planned completion horizon or explicit success condition is reached. Evaluate the run before starting another route.

## Hard stops

Hard stops may interrupt a run from any running state, including PROTECTED. They should represent invalid or unsafe-to-continue experiments, for example:

- process crash or unrecoverable launcher failure;
- invalid dataset/configuration that makes the experiment uninterpretable;
- persistent NaN/Inf beyond a precommitted count;
- unrecoverable OOM or distributed deadlock;
- loss or another signal crossing a predeclared catastrophic-divergence threshold for the required persistence;
- no forward progress because infrastructure is broken.

Do not classify "reward is lower than hoped after a few minutes" as a hard stop.

## Soft stops

Soft stops are scientific or economic judgments about a healthy run. Require all of the following:

1. the minimum evidence horizon has passed;
2. the run is at an eligible review gate;
3. a precommitted failure criterion is met;
4. the required number of consecutive failed reviews or other hysteresis condition is met.

If a soft-stop hypothesis appears between gates, record it and continue to the next gate.

## Hysteresis

Use persistence to prevent oscillation:

```text
one bad signal -> update belief
repeated bad review -> increase concern
precommitted persistence threshold -> intervention may be authorized
```

After a material route change, apply a new protected window before considering another soft stop.

## Candidate ideas versus launched experiments

Idea generation is cheap; experiments are expensive.

Maintain candidate hypotheses without launching each one immediately. A new idea is not sufficient reason to interrupt a committed run.

## Deterministic gate checker

This skill includes `scripts/trainctl.py`. It accepts a JSON policy and JSON state and returns the current authorization class.

Example:

```bash
python scripts/trainctl.py evaluate \
  --policy assets/policy.example.json \
  --state assets/state.example.json \
  --pretty
```

The helper is intentionally advisory and side-effect free. It never launches, kills, signals, checkpoints, or edits a training job.

Read `references/policy-schema.md` before integrating it with a launcher.

## Ambiguous unanticipated problems

If a serious new problem appears that is not covered by the run policy:

- if it makes the experiment objectively invalid or the process is already failed, treat it as a hard failure and document why;
- if it is merely evidence that the run may underperform, keep observing until a review gate;
- if continuing could materially waste compute or corrupt valuable state but the classification is genuinely ambiguous, preserve state and seek a human policy decision rather than silently rewriting the run rules.
