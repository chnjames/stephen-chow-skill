from pathlib import Path
import sys
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


if __name__ == "__main__":
    unittest.main()
