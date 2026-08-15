# codex-research-harness

Durable skills and control protocols for long-horizon Codex research, training, and autonomous experimentation.

> **Core principle:** update beliefs continuously; update actions only at precommitted intervention gates.

Long-running agent work fails in characteristic ways: compacted context drifts away from the original research intent, noisy early metrics trigger premature pivots, and attempts to prevent premature stopping can make the agent too conservative to intervene when a run is genuinely broken. This repository turns those failure modes into explicit workflow and control rules.

## What this repo is for

Use this harness when Codex is expected to work across many turns, context compactions, long-running commands, or iterative experiments such as:

- reinforcement learning and RLVR / GRPO experiments;
- SFT or other long model-training runs;
- benchmark and ablation campaigns;
- empirical software or systems research;
- literature-to-code reproduction work;
- autonomous research loops where compute and experiment launches are expensive.

It is intentionally not a general prompt collection. The repository separates research intent, working state, evidence, experiment history, and intervention authority so they do not collapse into one mutable conversation summary.

## Architecture

```text
                     USER OBJECTIVE
                           |
                           v
                  RESEARCH_BRIEF.md
                  stable source of truth
                           |
              +------------+------------+
              |                         |
              v                         v
        SESSION MEMORY             EXPERIMENT LOOP
       durable checkpoints      hypothesis -> run spec
              |                         |
              +------------+------------+
                           |
                           v
                 TRAINING CONTROLLER
          belief update != action update
              |         |          |
          protected   review     hard stop
           window      gates      conditions
              |         |          |
              +---------+----------+
                           |
                           v
                    EVIDENCE LEDGER
                           |
                           v
                       DRIFT AUDIT
```

## Included skills

| Skill | Purpose |
| --- | --- |
| `research-harness` | Orchestrates a long-horizon research or experiment campaign around an immutable research brief, explicit stop conditions, run specs, and an experiment ledger. |
| `session-memory` | Persists goal, current state, decisions, and handoff information across compaction, disconnects, restarts, and branch changes. |
| `training-controller` | Defines when a running experiment may be observed, reviewed, stopped, or changed. Includes a deterministic `trainctl.py` gate checker. |
| `drift-audit` | Re-derives the intended research trajectory from the original brief and checks whether current work has drifted. |

Codex discovers repo-scoped skills under `.agents/skills/`. Each skill here is intentionally self-contained enough to be copied into another repository or a user-level skills directory.

## Quick start

### Use repo-scoped skills in another project

Copy the skills you want into that project's `.agents/skills/` directory:

```bash
mkdir -p /path/to/project/.agents/skills
cp -R .agents/skills/research-harness /path/to/project/.agents/skills/
cp -R .agents/skills/session-memory /path/to/project/.agents/skills/
cp -R .agents/skills/training-controller /path/to/project/.agents/skills/
cp -R .agents/skills/drift-audit /path/to/project/.agents/skills/
```

### Use skills across repositories

Copy selected skill folders into your user skills directory:

```bash
mkdir -p ~/.agents/skills
cp -R .agents/skills/research-harness ~/.agents/skills/
cp -R .agents/skills/session-memory ~/.agents/skills/
cp -R .agents/skills/training-controller ~/.agents/skills/
cp -R .agents/skills/drift-audit ~/.agents/skills/
```

You can also use Codex's skill installer and ask it to install skills from this repository.

### Start a campaign

Invoke the main skill explicitly:

```text
$research-harness

Create a long-horizon research campaign for this objective:
<your objective>

Preserve my original request verbatim in the research brief.
Use the training controller for any run longer than a smoke test.
```

For a training-heavy project, invoke the controller too:

```text
$training-controller

Before launching this run, define the minimum evidence horizon,
review gates, hard-stop conditions, soft-stop conditions, and
success criteria. Do not infer stop authority from intermediate
metrics alone.
```

## The key separation

The harness treats these as different kinds of state:

```text
RESEARCH_BRIEF.md   why we are doing the work; stable
STATE.md            where the work currently is; mutable
EVIDENCE.md         what has been observed; append/update carefully
DECISIONS.md        why the trajectory changed; auditable
RUN_SPEC.md         precommitted rules for one experiment
EXPERIMENTS.tsv     experiment ledger
conversation        temporary working memory
```

A compacted conversation is never the authority on the original objective.

## Training-control model

A healthy run moves through explicit states:

```text
PRELAUNCH -> PROTECTED -> OBSERVE -> REVIEW -> COMPLETE
                                  \-> INTERVENE

HARD STOP may interrupt from any running state when a predeclared
failure condition is actually met.
```

The controller distinguishes:

- **belief:** what the agent currently thinks is happening;
- **action authority:** what the agent is allowed to change right now.

For example, Codex may believe with high confidence that the learning rate is too high while still being required to continue until the next review gate. Conversely, a persistent NaN condition or invalid experiment configuration can authorize immediate intervention even during the protected window.

## Deterministic gate checker

`training-controller` includes a standard-library-only helper:

```bash
python .agents/skills/training-controller/scripts/trainctl.py \
  evaluate \
  --policy .agents/skills/training-controller/assets/policy.example.json \
  --state .agents/skills/training-controller/assets/state.example.json \
  --pretty
```

It does not kill processes or launch jobs. It only evaluates whether the current state is protected, requires review, permits a soft stop, requires a hard stop, or is complete. Integrate it with your own launcher only after deciding what operations should be automated.

Run its built-in checks with:

```bash
python .agents/skills/training-controller/scripts/trainctl.py self-test
```

## Safety and scope

- Compute-intensive launches should be part of an explicitly approved campaign plan.
- Hard-stop rules should describe true failures or invalid experiments, not merely disappointing early metrics.
- Soft-stop criteria should be decided before the relevant evidence is observed.
- Do not silently rewrite a run's stopping criteria mid-run to justify a desired intervention.
- Preserve checkpoints and logs before destructive or irreversible actions when practical.
- This repository provides workflow and control scaffolding; it does not guarantee that any training configuration is scientifically valid.

## Status

This is an experimental v0.1 harness. The initial focus is durable research state, experiment discipline, and long-run training intervention policy. Framework-specific adapters for W&B, TensorBoard, Slurm, Kubernetes, and common RL stacks can be added later without changing the core state machine.

## References

See [`docs/REFERENCES.md`](docs/REFERENCES.md) for the public designs and documentation that informed this repository.
