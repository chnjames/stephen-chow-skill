#!/usr/bin/env python3
"""Validate the skill's source registry using only the Python standard library."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from urllib.parse import urlparse


REQUIRED = {"id", "title", "publisher", "url", "source_type", "verified_at", "topics", "confidence"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read valid JSON: {exc}"]

    sources = payload.get("sources")
    if not isinstance(sources, list) or not sources:
        return ["sources must be a non-empty list"]

    seen: set[str] = set()
    today = dt.date.today()
    for index, item in enumerate(sources):
        label = f"sources[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = REQUIRED - item.keys()
        if missing:
            errors.append(f"{label} missing: {', '.join(sorted(missing))}")
        source_id = item.get("id")
        if source_id in seen:
            errors.append(f"{label} duplicate id: {source_id}")
        if isinstance(source_id, str):
            seen.add(source_id)
        parsed = urlparse(str(item.get("url", "")))
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"{label} must use an absolute HTTPS URL")
        try:
            verified = dt.date.fromisoformat(str(item.get("verified_at")))
            if verified > today:
                errors.append(f"{label} verified_at is in the future")
        except ValueError:
            errors.append(f"{label} verified_at must be YYYY-MM-DD")
        confidence = item.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
            errors.append(f"{label} confidence must be between 0 and 1")
        topics = item.get("topics")
        if not isinstance(topics, list) or not topics or not all(isinstance(x, str) and x for x in topics):
            errors.append(f"{label} topics must be a non-empty string list")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("registry", type=Path)
    args = parser.parse_args()
    errors = validate(args.registry)
    if errors:
        print("Source registry validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Source registry is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
