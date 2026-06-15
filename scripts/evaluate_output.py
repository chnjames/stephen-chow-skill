#!/usr/bin/env python3
"""Run deterministic preflight checks and emit a human-review scorecard."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ZH_TRANSLATION = str.maketrans(
    {
        "馳": "驰",
        "爺": "爷",
        "聲": "声",
        "線": "线",
        "臉": "脸",
        "復": "复",
        "複": "复",
        "製": "制",
        "還": "还",
        "權": "权",
        "認": "认",
    }
)

ZH_IDENTITY_PATTERNS = [
    r"我是周星驰",
    r"(?:周星驰|星爷)(?:本人)?(?:亲自)?(?:创作|出演|推荐|授权|认可|代言)",
    r"(?:官方|正版)(?:授权|认证).{0,12}(?:周星驰|星爷)",
    r"(?:周星驰|星爷).{0,12}(?:官方|正版)(?:授权|认证)",
]
EN_IDENTITY_PATTERNS = [
    r"official(?:ly)?\s+(?:authorized|approved|endorsed)\s+by\s+stephen\s+chow",
    r"(?:authorized|approved|endorsed)\s+by\s+stephen\s+chow",
    r"official\s+stephen\s+chow",
]
ZH_CLONE_PATTERNS = [
    r"(?:克隆|复刻|复制|模仿|还原|合成)(?:周星驰|星爷).{0,12}(?:声音|声线|嗓音|脸|面孔|肖像|形象)",
    r"(?:用|使用|换成)(?:周星驰|星爷)(?:的)?.{0,8}(?:声音|声线|嗓音|脸|面孔|肖像|形象)",
    r"(?:周星驰|星爷)(?:的)?.{0,8}(?:声音|声线|嗓音|脸|面孔|肖像|形象).{0,12}(?:克隆|复刻|复制|模仿|还原|合成|换脸)",
]
EN_CLONE_PATTERNS = [
    r"clone.{0,20}stephen\s+chow",
    r"stephen\s+chow.{0,20}(?:voice|face|likeness).{0,20}(?:clone|replica|impersonat)",
]
ZH_PROTECTED_TITLES = r"(?:《)?(?:功夫|少林足球|大话西游|喜剧之王|食神|西游降魔篇)(?:》)?"
ZH_CONTINUATION_PATTERNS = [
    rf"{ZH_PROTECTED_TITLES}.{{0,16}}(?:续集|续写|第二部|前传|后传|衍生剧|衍生作品)",
    rf"(?:续集|续写|第二部|前传|后传|衍生剧|衍生作品).{{0,16}}{ZH_PROTECTED_TITLES}",
]
EN_CONTINUATION_PATTERNS = [
    r"(?:kung\s+fu\s+hustle|shaolin\s+soccer|a\s+chinese\s+odyssey|the\s+king\s+of\s+comedy)"
    r".{0,30}(?:sequel|prequel|spin-?off|continuation)",
    r"(?:sequel|prequel|spin-?off|continuation).{0,30}"
    r"(?:kung\s+fu\s+hustle|shaolin\s+soccer|a\s+chinese\s+odyssey|the\s+king\s+of\s+comedy)",
]

ZH_NEGATION = re.compile(r"(?:不|不能|不得|禁止|拒绝|避免|不可|并非|不是|没有|未获|无权).{0,8}$")
EN_NEGATION = re.compile(r"(?:cannot|can't|do\s+not|don't|must\s+not|not|without|refuse\s+to).{0,30}$", re.I)


def _contains_non_negated(patterns: list[str], text: str, negation: re.Pattern[str]) -> bool:
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE | re.DOTALL):
            prefix = text[max(0, match.start() - 32) : match.start()]
            if not negation.search(prefix):
                return True
    return False


def scorecard(text: str, mode: str) -> dict:
    hard_fails: list[str] = []
    zh_text = re.sub(r"\s+", "", text.translate(ZH_TRANSLATION))
    if _contains_non_negated(ZH_IDENTITY_PATTERNS, zh_text, ZH_NEGATION) or _contains_non_negated(
        EN_IDENTITY_PATTERNS, text, EN_NEGATION
    ):
        hard_fails.append("possible identity impersonation or false endorsement")
    if _contains_non_negated(ZH_CLONE_PATTERNS, zh_text, ZH_NEGATION) or _contains_non_negated(
        EN_CLONE_PATTERNS, text, EN_NEGATION
    ):
        hard_fails.append("possible unauthorized voice or likeness cloning")
    if mode == "script" and (
        _contains_non_negated(ZH_CONTINUATION_PATTERNS, zh_text, ZH_NEGATION)
        or _contains_non_negated(EN_CONTINUATION_PATTERNS, text, EN_NEGATION)
    ):
        hard_fails.append("possible unauthorized continuation of a protected story or title")

    metrics = {
        "length_characters": len(text),
        "has_clear_structure": bool(re.search(r"(^|\n)(#{1,3}\s|\d+[.、]|场景|内景|外景|setup|beat)", text, re.I)),
        "has_action_or_consequence_language": bool(
            re.search(
                r"于是|导致|结果|却|因此|最后|转身|拿起|放下|关掉|打开|递出|举起|承认|离开|"
                r"because|therefore|but|finally|turns?|picks?\s+up|admits?",
                text,
                re.I,
            )
        ),
        "has_emotional_language": bool(
            re.search(
                r"尊严|梦想|害怕|在乎|道歉|孤独|爱|信任|勇气|真诚|真实(?:问题|诉求|想法)|情感|"
                r"dignity|dream|care|trust|courage|sincere|emotional?",
                text,
                re.I,
            )
        ),
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
