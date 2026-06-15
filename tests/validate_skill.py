#!/usr/bin/env python3
"""Repository-local structural checks for CI environments without Codex tooling."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"


def main() -> int:
    errors: list[str] = []
    text = SKILL.read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not frontmatter:
        errors.append("SKILL.md must start with YAML frontmatter")
    else:
        header = frontmatter.group(1)
        if not re.search(r"^name: stephen-chow-skill$", header, re.MULTILINE):
            errors.append("frontmatter name must match the directory")
        if not re.search(r"^description: .+", header, re.MULTILINE):
            errors.append("frontmatter description is required")
        keys = re.findall(r"^([a-z_]+):", header, re.MULTILINE)
        if set(keys) != {"name", "description"}:
            errors.append("frontmatter may contain only name and description")

    referenced = set(re.findall(r"`((?:references|scripts)/[^`]+)`", text))
    for relative in sorted(referenced):
        if " " in relative or relative.endswith(".txt"):
            continue
        if not (ROOT / relative).exists():
            errors.append(f"missing referenced file: {relative}")

    expected = [
        ROOT / "agents" / "openai.yaml",
        ROOT / "references" / "rights-and-safety.md",
        ROOT / "references" / "evaluation-rubric.md",
        ROOT / "scripts" / "quote_guard.py",
    ]
    for path in expected:
        if not path.exists():
            errors.append(f"missing required repository file: {path.relative_to(ROOT)}")

    if errors:
        print("Skill structure validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Skill structure is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
