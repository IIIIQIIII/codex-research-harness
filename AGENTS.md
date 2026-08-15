# Repository Instructions

This repository contains reusable Codex skills for long-horizon research and experimentation.

## Design invariants

Preserve these principles in every change:

1. The original research intent must have a durable source of truth outside conversation memory.
2. Stable intent and mutable progress must be stored separately.
3. Diagnosis must not automatically imply intervention.
4. Long-running experiments need precommitted evidence horizons, review gates, and stopping rules.
5. Hard stops and soft stops are different classes of decision.
6. Experiment history must remain auditable through run specs, decisions, and a ledger.
7. After context compaction or handoff, re-anchor from durable files before continuing.
8. A drift audit must derive the desired trajectory from the research brief, not justify the current trajectory after the fact.

## Skill authoring

- Put repo-scoped Codex skills under `.agents/skills/<skill-name>/SKILL.md`.
- Every skill must include `name` and `description` frontmatter.
- Keep each skill focused on one primary job.
- Put deterministic behavior in scripts when language-only rules are too easy to reinterpret.
- Put reusable templates under the owning skill's `assets/` directory.
- Put longer explanations or schemas under `references/` rather than bloating `SKILL.md`.
- Descriptions must state both when the skill should trigger and important non-goals.

## Training-controller changes

Any change to `.agents/skills/training-controller/scripts/trainctl.py` must preserve these behaviors:

- hard-stop conditions override protected windows;
- protected windows prevent metric-driven soft stops;
- a soft stop is only allowed at an eligible review gate;
- consecutive bad-review requirements are respected;
- the helper never launches, kills, or signals a training process itself.

Run:

```bash
python .agents/skills/training-controller/scripts/trainctl.py self-test
```

before considering controller changes complete.

## Research artifacts

Do not commit generated `.research/session/` state, training logs, checkpoints, credentials, or large experiment outputs to this harness repository. Examples and templates belong in skill assets or `docs/`.

## External sources

Paraphrase external workflows rather than copying them verbatim. Attribute public designs in `docs/REFERENCES.md` when they materially influence the harness.

## Licensing

Do not add or change a repository license without an explicit maintainer decision.
