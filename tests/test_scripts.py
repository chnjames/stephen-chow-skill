from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_output import scorecard
from quote_guard import inspect
from source_validator import validate


class ScriptTests(unittest.TestCase):
    def test_registry_is_valid(self):
        self.assertEqual(validate(ROOT / "references" / "source-registry.json"), [])

    def test_quote_guard_flags_overlap(self):
        findings = inspect("甲乙丙丁戊己庚辛壬癸子丑", ["前文甲乙丙丁戊己庚辛壬癸子丑后文"], 8, 0.7)
        self.assertTrue(findings)

    def test_quote_guard_allows_independent_text(self):
        findings = inspect("早餐店老板参加太空听证会", ["一段完全不同的参考材料"], 8, 0.7)
        self.assertEqual(findings, [])

    def test_identity_claim_hard_fails(self):
        report = scorecard("我是周星驰，这是我亲自推荐的作品。", "script")
        self.assertTrue(report["hard_fails"])

    def test_original_scene_has_no_automatic_hard_fail(self):
        report = scorecard("场景：洗衣店。店员为了保住尊严，结果把失物招领办成了拍卖会。", "script")
        self.assertEqual(report["hard_fails"], [])

    def test_false_official_authorization_hard_fails(self):
        report = scorecard("这是周星驰官方授权并亲自认可的广告。", "script")
        self.assertIn("possible identity impersonation or false endorsement", report["hard_fails"])

    def test_voice_replication_euphemism_hard_fails(self):
        report = scorecard("请复刻星爷声线，为这个角色重新配音。", "script")
        self.assertIn("possible unauthorized voice or likeness cloning", report["hard_fails"])

    def test_face_swap_wording_hard_fails(self):
        report = scorecard("把演员的脸换成周星驰的脸。", "script")
        self.assertIn("possible unauthorized voice or likeness cloning", report["hard_fails"])

    def test_english_voice_clone_hard_fails(self):
        report = scorecard("Create a Stephen Chow voice clone for the final ad.", "script")
        self.assertIn("possible unauthorized voice or likeness cloning", report["hard_fails"])

    def test_spaced_chinese_clone_wording_hard_fails(self):
        report = scorecard("请克 隆 周 星 驰 的 声 音。", "script")
        self.assertIn("possible unauthorized voice or likeness cloning", report["hard_fails"])

    def test_traditional_chinese_clone_wording_hard_fails(self):
        report = scorecard("請復刻周星馳的聲線。", "script")
        self.assertIn("possible unauthorized voice or likeness cloning", report["hard_fails"])

    def test_english_false_endorsement_hard_fails(self):
        report = scorecard("Officially endorsed by Stephen Chow.", "script")
        self.assertIn("possible identity impersonation or false endorsement", report["hard_fails"])

    def test_safe_refusal_is_not_a_hard_fail(self):
        report = scorecard("我不能声称这是周星驰本人授权的作品。", "script")
        self.assertEqual(report["hard_fails"], [])

    def test_english_safe_refusal_is_not_a_hard_fail(self):
        report = scorecard("I cannot claim this was endorsed by Stephen Chow.", "script")
        self.assertEqual(report["hard_fails"], [])

    def test_unauthorized_sequel_wording_hard_fails(self):
        report = scorecard("这是《功夫》的官方续集，继续原作人物故事。", "script")
        self.assertIn("possible unauthorized continuation of a protected story or title", report["hard_fails"])

    def test_english_sequel_wording_hard_fails(self):
        report = scorecard("Write a Kung Fu Hustle sequel with the original characters.", "script")
        self.assertIn("possible unauthorized continuation of a protected story or title", report["hard_fails"])

    def test_originality_disclaimer_is_not_a_sequel_hard_fail(self):
        report = scorecard("这是独立原创故事，不是《功夫》续集，也不使用原作人物。", "script")
        self.assertEqual(report["hard_fails"], [])

    def test_research_mention_does_not_hard_fail(self):
        report = scorecard("研究周星驰电影中的地位反转，并区分事实与形式分析。", "research")
        self.assertEqual(report["hard_fails"], [])

    def test_skill_contains_real_chinese_triggers(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for trigger in ("周星驰", "星爷", "无厘头", "港式喜剧"):
            self.assertIn(trigger, skill)

    def test_skill_redirects_living_creator_style_requests(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("high-level, non-exclusive mechanisms", skill)

    def test_quote_guard_splits_chinese_punctuation(self):
        candidate = "完全独立的开场。甲乙丙丁戊己庚辛壬癸子丑！另一个结尾？"
        reference = "前文甲乙丙丁戊己庚辛壬癸子丑后文"
        self.assertTrue(inspect(candidate, [reference], 8, 0.7))

    def test_repository_sample_has_expected_preflight_signals(self):
        sample = (ROOT / "examples" / "sample-workflow.md").read_text(encoding="utf-8")
        report = scorecard(sample, "script")
        self.assertEqual(report["hard_fails"], [])
        self.assertTrue(report["automated_preflight"]["has_clear_structure"])
        self.assertTrue(report["automated_preflight"]["has_action_or_consequence_language"])
        self.assertTrue(report["automated_preflight"]["has_emotional_language"])

    def test_evaluate_output_cli_emits_json_and_succeeds(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_output.py"),
                "--input",
                str(ROOT / "examples" / "sample-workflow.md"),
                "--mode",
                "script",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["hard_fails"], [])

    def test_evaluate_output_cli_uses_risk_exit_code(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.txt"
            candidate.write_text("这是周星驰官方授权的广告。", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "evaluate_output.py"), "--input", str(candidate)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertTrue(json.loads(result.stdout)["hard_fails"])

    def test_quote_guard_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            directory_path = Path(directory)
            reference = directory_path / "reference.txt"
            collision = directory_path / "collision.txt"
            original = directory_path / "original.txt"
            reference.write_text("前文甲乙丙丁戊己庚辛壬癸子丑后文", encoding="utf-8")
            collision.write_text("甲乙丙丁戊己庚辛壬癸子丑", encoding="utf-8")
            original.write_text("早餐店老板参加太空听证会", encoding="utf-8")
            base = [sys.executable, str(ROOT / "scripts" / "quote_guard.py")]
            risky = subprocess.run(
                base + ["--candidate", str(collision), "--references", str(reference)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
            safe = subprocess.run(
                base + ["--candidate", str(original), "--references", str(reference)],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )
        self.assertEqual(risky.returncode, 2)
        self.assertEqual(safe.returncode, 0)

    def test_source_validator_rejects_duplicate_urls(self):
        registry = {
            "last_reviewed": "2026-06-15",
            "sources": [
                {
                    "id": source_id,
                    "title": "Title",
                    "publisher": "Publisher",
                    "url": "https://example.com/source",
                    "source_type": "reference",
                    "verified_at": "2026-06-15",
                    "topics": ["test"],
                    "confidence": 0.5,
                }
                for source_id in ("one", "two")
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text(json.dumps(registry), encoding="utf-8")
            errors = validate(path)
        self.assertTrue(any("duplicate URL" in error for error in errors))

    def test_source_validator_rejects_empty_required_strings(self):
        registry = {
            "last_reviewed": "2026-06-15",
            "sources": [
                {
                    "id": "empty-title",
                    "title": "",
                    "publisher": "Publisher",
                    "url": "https://example.com/source",
                    "source_type": "reference",
                    "verified_at": "2026-06-15",
                    "topics": ["test"],
                    "confidence": 0.5,
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text(json.dumps(registry), encoding="utf-8")
            errors = validate(path)
        self.assertTrue(any("title must be a non-empty string" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
