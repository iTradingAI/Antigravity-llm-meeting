#!/usr/bin/env python3
"""Initialize per-project/per-task .meeting workspace for dual-LLM round workflow."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

FILES = {
    "agenda.md": "# Agenda\n\n## Goal\n\n## Non-goals\n\n## Acceptance Criteria\n\n## Hard Constraints\n",
    "repo_snapshot.md": "# Repo Snapshot\n\n## Relevant Tree\n\n## Key Modules\n\n## Constraints\n",
    "transcript.md": "# Transcript\n\n",
    "conflicts.md": "# Conflicts\n\n",
    "decision.md": "# Decision\n\n## Final Plan\n\n## Why This Decision\n",
    "patch_plan.json": "[]\n",
    "tests.md": "# Tests\n\n## Verification Steps\n",
    "risk_register.md": "# Risk Register\n\n",
}

ROUND_FILES = [
    "codex_round1.json",
    "opus_round1.json",
    "codex_round2.json",
    "opus_round2.json",
]


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def normalize_workspace_name(raw: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", raw.strip()).strip("-._")
    return slug or "default"


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize .meeting workspace")
    parser.add_argument("--root", default=".", help="Project root path (artifacts are written here)")
    parser.add_argument(
        "--workspace",
        default="default",
        help="Workspace folder name under <root>/.meeting/ (use project/task identifier)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    workspace_name = normalize_workspace_name(args.workspace)

    meeting_root = root / ".meeting"
    meeting = meeting_root / workspace_name
    rounds = meeting / "rounds"
    schemas = meeting / "schemas"

    rounds.mkdir(parents=True, exist_ok=True)
    schemas.mkdir(parents=True, exist_ok=True)

    for name, content in FILES.items():
        write_if_missing(meeting / name, content)

    for round_file in ROUND_FILES:
        write_if_missing(rounds / round_file, "{}\n")

    schema_source = Path(__file__).resolve().parent.parent / "references" / "round.schema.json"
    schema_target = schemas / "round.schema.json"
    if schema_source.exists() and not schema_target.exists():
        schema_target.write_text(schema_source.read_text(encoding="utf-8"), encoding="utf-8")

    metadata = (
        "# Meeting Workspace Metadata\n\n"
        f"- project_root: {root}\n"
        f"- workspace: {workspace_name}\n"
    )
    write_if_missing(meeting / "workspace.md", metadata)

    print(f"Initialized meeting workspace at: {meeting}")


if __name__ == "__main__":
    main()
