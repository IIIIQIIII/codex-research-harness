# References and influences

This repository is an independent implementation. The following public material informed its design.

## OpenAI Codex skills

- OpenAI, **Build skills**: https://learn.chatgpt.com/codex/build-skills
  - Skill directories use `SKILL.md` plus optional scripts, references, assets, and metadata.
  - Repo-scoped Codex skills are discovered under `.agents/skills`.
- OpenAI, **Save workflows as skills**: https://learn.chatgpt.com/codex/use-cases/reusable-codex-skills
  - Motivates moving repeatable workflow instructions out of ad-hoc prompts and into reusable skills.

## NVIDIA NeMo-RL agent skills

- NVIDIA, `nemo-rl-auto-research`: https://github.com/NVIDIA/skills/tree/main/skills/nemo-rl-auto-research
- NVIDIA, `nemo-rl-session-memory`: https://github.com/NVIDIA/skills/tree/main/skills/nemo-rl-session-memory

The NVIDIA skills demonstrate useful public patterns including durable session state, experiment ledgers, branch-per-hypothesis workflows, explicit campaign stop conditions, and reloading durable state after compaction/handoff.

`codex-research-harness` extends these ideas with a stronger distinction between campaign stopping and **in-run intervention authority**, especially for noisy long-running RL/ML training.
