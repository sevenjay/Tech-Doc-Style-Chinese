from __future__ import annotations

import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "tech-doc-style-chinese-tw"
LINTER = runpy.run_path(
    str(SKILL_DIR / "scripts" / "lint_copy_rules.py"),
    run_name="lint_copy_rules_test",
)
scan_markdown = LINTER["scan_markdown"]


class CopyLintRulesTest(unittest.TestCase):
    def scan(self, text: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.md"
            path.write_text(text, encoding="utf-8")
            return scan_markdown(path)

    def test_detects_multiword_ai_terms(self):
        findings = self.scan("呼叫 openai api，並使用 fine tune。")
        messages = [item.message for item in findings]
        self.assertTrue(any("OpenAI API" in message for message in messages))
        self.assertTrue(any("fine-tuning" in message for message in messages))

    def test_masks_single_segment_api_path(self):
        findings = self.scan("呼叫 /api 回傳 json。")
        messages = [item.message for item in findings]
        self.assertFalse(any("「api」" in message for message in messages))
        self.assertTrue(any("JSON" in message for message in messages))

    def test_context_dependent_words_are_warnings(self):
        findings = self.scan("截止日期。登陸月球。依比例配製溶液。製作 H5 頁面。")
        self.assertTrue(findings)
        self.assertFalse(any(item.severity == "error" for item in findings))
        self.assertTrue(any(item.kind == "context" for item in findings))
        self.assertTrue(any(item.kind == "abbreviation" for item in findings))

    def test_high_confidence_typo_is_error(self):
        findings = self.scan("請調整閥值，不要佈署舊版本。")
        self.assertEqual({item.severity for item in findings}, {"error"})

    def test_ignores_code_urls_paths_and_link_targets(self):
        text = "\n".join(
            [
                "`openai api`",
                "```text",
                "openai api",
                "```",
                "https://example.com/openai/api",
                "[說明](https://example.com/openai/api)",
                "/api",
            ]
        )
        self.assertEqual(self.scan(text), [])

    def test_inline_ignore_marker(self):
        findings = self.scan("閥值 <!-- copy-lint-disable-line -->")
        self.assertEqual(findings, [])

    def test_context_warning_does_not_fail_default_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.md"
            path.write_text("截止日期。登陸月球。", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_DIR / "scripts" / "lint_copy_rules.py"),
                    str(path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 0)
        self.assertIn("PASS WITH ADVICE", result.stdout)

    def test_high_confidence_error_fails_default_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.md"
            path.write_text("閥值。", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SKILL_DIR / "scripts" / "lint_copy_rules.py"),
                    str(path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("FAIL", result.stdout)


if __name__ == "__main__":
    unittest.main()
