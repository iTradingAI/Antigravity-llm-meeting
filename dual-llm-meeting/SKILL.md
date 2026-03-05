---
name: dual-llm-meeting
description: Run a round-based meeting workflow between Codex CLI and Antigravity Opus (kept in Antigravity UI), with Chair arbitration and auditable outputs (decision, patch plan, tests, risks). Use when the user needs multi-LLM convergence instead of free-form chat.
---

# Dual-LLM Meeting (Codex × Antigravity Opus)

Use this skill when you need two LLMs to converge on an implementation plan while keeping Opus inside Antigravity.

## What this skill enforces

- **Round-based orchestration** (not free chat)
- **Chair-led conflict arbitration**
- **Structured artifacts** under `<project>/.meeting/<workspace>/`
- **Role separation**:
  - Codex = implementation plan and tests
  - Opus = critique, risks, conflict pressure
  - Chair = conflict consolidation and final decision

## Required workflow

1. **Initialize meeting workspace in the project directory**
   - Run:
     - `python3 dual-llm-meeting/scripts/init_meeting.py --root <project_repo_path> --workspace <project-or-problem-id>`
   - This creates a scoped workspace at:
     - `<project_repo_path>/.meeting/<project-or-problem-id>/`

2. **Create Round 0 context package**
   - Fill `<workspace>/repo_snapshot.md` with tree/module summary and hard constraints.
   - Fill `<workspace>/agenda.md` with goals, non-goals, acceptance criteria, and constraints.

3. **Run rounds (0 → 2 required, 3 optional)**
   - Round 0: context alignment
   - Round 1: proposal vs critique
   - Round 2: conflict convergence and finalization
   - Round 3 (optional): execute patch plan

4. **Persist each participant output as JSON**
   - Save per-round responses under `<workspace>/rounds/`.
   - Validate JSON against schema in `<workspace>/schemas/round.schema.json`.

5. **Produce final bundle**
   - `<workspace>/decision.md`
   - `<workspace>/patch_plan.json`
   - `<workspace>/tests.md`
   - `<workspace>/risk_register.md`
   - `<workspace>/transcript.md`

## tmux bus constraints

- Use fixed pane IDs:
  - A: Chair orchestrator
  - B: Codex
  - C: Antigravity Opus UI
- Opus output must end with `<<<END_JSON>>>` for reliable `capture-pane` extraction.

## Output contract

Use the schema in `references/round.schema.json`.

Required emphasis:
- **Codex must fill**: `patch_plan`, `tests`, `tradeoffs`
- **Opus must fill**: `risks`, `conflicts`, `open_questions`

## References

- For round prompts and role prompt templates, read: `references/prompt-contract.md`
- For structured output schema, read: `references/round.schema.json`
