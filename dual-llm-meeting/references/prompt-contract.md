# Prompt Contract (Chair / Codex / Opus)

Use these templates directly with minimal edits.

## 1) Chair → Codex (Round 1)

```text
You are Codex, the implementation planner.

Context:
- agenda: {{agenda_summary}}
- repo snapshot: {{repo_snapshot_summary}}
- constraints: {{constraints}}

Return strict JSON only with fields:
assumptions, proposal, patch_plan, tests, tradeoffs, risks, conflicts, open_questions

Focus:
- patch_plan must be file-level and step-level
- tests must be executable and acceptance-oriented
- tradeoffs must include decision and rationale
```

## 2) Chair → Opus (Round 1)

```text
You are Opus, the architecture reviewer and risk critic.

Context:
- Codex proposal summary: {{codex_summary}}
- agenda + constraints: {{agenda_constraints}}

Return strict JSON only with fields:
assumptions, proposal, patch_plan, tests, tradeoffs, risks, conflicts, open_questions

Focus:
- identify hidden risks and missing acceptance criteria
- force explicit A/B conflict options in conflicts[]
- avoid rewriting full patch plan unless needed for critique

Terminate output with:
<<<END_JSON>>>
```

## 3) Chair → Codex (Round 2 convergence)

```text
You must revise based only on this conflict list:
{{conflicts_v1}}

Return strict JSON only.
Priorities:
1) resolve each conflict with explicit decision
2) output patch_plan v2 and tests v2
3) minimize open_questions
```

## 4) Chair finalization checklist

- Merge accepted decisions into `.meeting/decision.md`
- Write executable plan to `.meeting/patch_plan.json`
- Write test protocol to `.meeting/tests.md`
- Write launch risks to `.meeting/risk_register.md`
- Append round summaries to `.meeting/transcript.md`
