from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "tech-doc-style-chinese-tw"


class SkillStructureTest(unittest.TestCase):
    def test_skill_name_matches_its_directory(self):
        self.assertFalse((ROOT / "SKILL.md").exists())
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        name_match = re.search(r"^name:\s*([^\s]+)$", skill, re.MULTILINE)
        self.assertIsNotNone(name_match)
        self.assertEqual(name_match.group(1), SKILL_DIR.name)

        openai_yaml = (SKILL_DIR / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        self.assertIn(f"${SKILL_DIR.name}", openai_yaml)

    def test_core_skill_stays_concise(self):
        lines = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").splitlines()
        self.assertLessEqual(len(lines), 250)

    def test_local_resources_from_skill_exist(self):
        skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        targets = re.findall(r"\[[^]]+]\(((?:references|scripts)/[^)]+)\)", skill)
        self.assertTrue(targets)
        for target in targets:
            with self.subTest(target=target):
                self.assertTrue((SKILL_DIR / target).is_file())

    def test_controlled_writing_has_four_groups_and_twelve_examples(self):
        reference = (
            SKILL_DIR / "references" / "controlled-technical-chinese.md"
        ).read_text(encoding="utf-8")
        for heading in ("操作手冊", "API 文件", "疑難排解", "產品介紹"):
            with self.subTest(heading=heading):
                self.assertIn(f"### {heading}", reference)
        self.assertEqual(len(re.findall(r"^#### 範例 \d+$", reference, re.MULTILINE)), 12)

    def test_project_override_is_explicitly_a_template(self):
        reference = (
            SKILL_DIR / "references" / "project-overrides-example.md"
        ).read_text(encoding="utf-8")
        self.assertIn("本檔案只是範本", reference)
        self.assertFalse((SKILL_DIR / "references" / "Project-Overrides.md").exists())


if __name__ == "__main__":
    unittest.main()
