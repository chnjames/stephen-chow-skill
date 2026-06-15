#!/usr/bin/env python3
"""Repository-local structural checks for CI environments without Codex tooling."""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"


def local_links(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    markdown = re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)
    html = re.findall(r"(?:href|src)=\"([^\"]+)\"", text)
    return {
        target.split("#", 1)[0]
        for target in markdown + html
        if target and not re.match(r"^(?:https?://|mailto:|#)", target)
    }


def main() -> int:
    errors: list[str] = []
    try:
        text = SKILL.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(f"SKILL.md is not valid UTF-8: {exc}")
        return 1
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

    for readme_name in ("README.md", "README.en.md"):
        readme = ROOT / readme_name
        if not readme.exists():
            errors.append(f"missing repository file: {readme_name}")
            continue
        for target in sorted(local_links(readme)):
            if not (ROOT / target).exists():
                errors.append(f"{readme_name} has a broken local link: {target}")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or ".idea" in path.parts:
            continue
        if path.suffix.lower() in {".md", ".py", ".json", ".yaml", ".yml", ".svg", ".txt"}:
            try:
                decoded = path.read_text(encoding="utf-8")
            except UnicodeDecodeError as exc:
                errors.append(f"file is not valid UTF-8: {path.relative_to(ROOT)} ({exc})")
                continue
            if "\ufffd" in decoded:
                errors.append(f"file contains Unicode replacement characters: {path.relative_to(ROOT)}")

    try:
        ET.parse(ROOT / "assets" / "hero.svg")
    except (ET.ParseError, OSError) as exc:
        errors.append(f"assets/hero.svg is not valid XML: {exc}")

    metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if "$stephen-chow-skill" not in metadata:
        errors.append("agents/openai.yaml default_prompt must invoke $stephen-chow-skill")
    if 'display_name: "周星驰.skill"' not in metadata:
        errors.append("agents/openai.yaml must expose the expected display name")

    workflow = (ROOT / ".github" / "workflows" / "validate.yml").read_text(encoding="utf-8")
    for command in (
        "python scripts/source_validator.py references/source-registry.json",
        "python -m unittest discover -s tests -v",
        "python tests/validate_skill.py",
    ):
        if command not in workflow:
            errors.append(f"GitHub Actions is missing validation command: {command}")

    if errors:
        print("Skill structure validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Skill structure is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
