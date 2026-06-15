#!/usr/bin/env python3
"""Run deterministic preflight checks and emit a human-review scorecard."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


IDENTITY_PATTERNS = [
    r"我是周星驰",
    r"周星驰本人(?:创作|出演|推荐|授权)",
    r"official\s+stephen\s+chow",
]
CLONE_PATTERNS = [r"克隆(?:周星驰|星爷).{0,8}(?:声音|声线|脸|肖像)", r"clone.{0,20}stephen\s+chow"]


def scorecard(text: str, mode: str) -> dict:
    hard_fails: list[str] = []
    for pattern in IDENTITY_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            hard_fails.append("possible identity impersonation or false endorsement")
            break
    for pattern in CLONE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
            hard_fails.append("possible unauthorized voice or likeness cloning")
            break

    metrics = {
        "length_characters": len(text),
        "has_clear_structure": bool(re.search(r"(^|\n)(#{1,3}\s|\d+[.、]|场景|内景|外景|setup|beat)", text, re.I)),
        "has_action_or_consequence_language": bool(re.search(r"于是|导致|结果|却|因此|转身|拿起|放下|because|therefore|but", text, re.I)),
        "has_emotional_language": bool(re.search(r"尊严|梦想|害怕|在乎|道歉|孤独|爱|信任|dignity|dream|care|trust", text, re.I)),
    }
    review_dimensions = (
        ["causal_logic", "character_agency", "comic_clarity", "escalation", "originality", "format_fit"]
        if mode == "script"
        else ["source_authority", "factual_precision", "fact_interpretation_separation", "currency", "citation_completeness"]
    )
    return {
        "mode": mode,
        "hard_fails": hard_fails,
        "automated_preflight": metrics,
        "human_review_required": {key: None for key in review_dimensions},
        "release_ready": False,
        "note": "Set 1-5 human scores. Release only with no hard fails, all scores >=3, and average >=4.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--mode", choices=("script", "research"), default="script")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = scorecard(args.input.read_text(encoding="utf-8"), args.mode)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 2 if report["hard_fails"] else 0


if __name__ == "__main__":
    sys.exit(main())
