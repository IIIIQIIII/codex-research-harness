# Design Notes

## The problem

Long-horizon coding agents face several coupled control problems:

1. **goal drift after compaction**: a compressed summary becomes the practical objective and subtle constraints from the original request disappear;
2. **short-horizon optimization**: the agent overreacts to noisy intermediate results and repeatedly pivots before obtaining representative evidence;
3. **anti-pivot overcorrection**: adding a strong "do not stop" instruction makes the agent reluctant to intervene even when a run is objectively invalid;
4. **experiment ambiguity**: repeated multi-factor changes make it unclear which change caused an improvement or regression;
5. **state reconstruction failure**: after a restart, the agent remembers conclusions but not the evidence, run policy, or why a route was chosen.

## State separation

The harness uses different artifacts for different epistemic roles:

| Artifact | Role | Mutability |
| --- | --- | --- |
| `RESEARCH_BRIEF.md` | user intent and research constitution | stable; user-authorized changes only |
| `STATE.md` | current phase and next actions | mutable |
| `EVIDENCE.md` | observations and source links | append/update with evidence |
| `DECISIONS.md` | route-change rationale | append-oriented |
| `RUN_SPEC.md` | precommitted policy for one experiment | stable during the run |
| `EXPERIMENTS.tsv` | experiment ledger | append-oriented |
| session files | resumable working state | mutable |
| conversation | temporary working memory | disposable |

The crucial property is that no compacted conversational summary is asked to preserve every role at once.

## Belief versus action

A training agent should be allowed to think early without being allowed to act early.

This creates two parallel states:

```text
Epistemic state:  What do I currently believe about this run?
Control state:    What intervention is authorized right now?
```

The first may update every time a metric changes. The second changes only when an explicit condition or review gate is reached.

## Why hysteresis matters

Without persistence requirements, a noisy metric can cause control oscillation:

```text
metric falls -> stop -> new route -> early metric falls -> stop -> new route
```

A persistence rule changes this to:

```text
bad signal -> concern
bad review -> stronger concern
repeated bad review at eligible gate -> soft-stop authority
```

Hard failures remain outside this hysteresis path and can interrupt immediately.

## Why a deterministic checker exists

Language-model instructions such as "do not stop too early" are inherently open to reinterpretation. A small deterministic policy checker makes one narrow question testable:

> Given the precommitted policy and verified run state, is an intervention authorized now?

The current `trainctl.py` intentionally does not control processes. Keeping authorization and actuation separate makes the policy easier to inspect and test.

## Future extensions

Useful adapters can be added without changing the conceptual model:

- W&B and TensorBoard state readers;
- Slurm and Kubernetes job adapters;
- checkpoint-preserving stop hooks;
- RL framework adapters for GRPO/PPO/RLVR;
- campaign-budget accounting;
- automated drift-audit reports;
- plugin packaging for easier skill distribution.
