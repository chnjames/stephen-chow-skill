#!/usr/bin/env python3
"""Flag suspicious overlap with operator-supplied, lawfully obtained references."""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    return "".join(ch for ch in text if ch.isalnum())


def chunks(text: str, size: int) -> set[str]:
    if len(text) < size:
        return {text} if text else set()
    return {text[i : i + size] for i in range(len(text) - size + 1)}


def line_candidates(text: str, minimum: int) -> list[str]:
    return [normalize(x) for x in re.split(r"[\r\n。！？!?]+", text) if len(normalize(x)) >= minimum]


def inspect(candidate: str, references: list[str], ngram: int, ratio: float) -> list[str]:
    findings: list[str] = []
    candidate_norm = normalize(candidate)
    candidate_chunks = chunks(candidate_norm, ngram)
    for ref_index, reference in enumerate(references, 1):
        ref_norm = normalize(reference)
        overlap = candidate_chunks & chunks(ref_norm, ngram)
        if overlap:
            findings.append(f"reference {ref_index}: found {len(overlap)} shared normalized {ngram}-character spans")
        for line in line_candidates(candidate, ngram):
            match = SequenceMatcher(None, line, ref_norm).find_longest_match()
            local_ratio = match.size / max(1, len(line))
            if match.size >= ngram and local_ratio >= ratio:
                findings.append(
                    f"reference {ref_index}: candidate segment has {local_ratio:.0%} contiguous overlap "
                    f"({match.size} normalized characters)"
                )
                break
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--references", required=True, type=Path, nargs="+")
    parser.add_argument("--ngram", type=int, default=12)
    parser.add_argument("--ratio", type=float, default=0.72)
    args = parser.parse_args()
    if args.ngram < 6 or not 0 < args.ratio <= 1:
        parser.error("--ngram must be >= 6 and --ratio must be in (0, 1]")
    candidate = args.candidate.read_text(encoding="utf-8")
    references = [path.read_text(encoding="utf-8") for path in args.references]
    findings = inspect(candidate, references, args.ngram, args.ratio)
    if findings:
        print("Potential protected-expression overlap detected:")
        for finding in findings:
            print(f"- {finding}")
        print("Review manually; this heuristic is neither a copyright ruling nor proof of infringement.")
        return 2
    print("No configured overlap threshold was triggered.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
