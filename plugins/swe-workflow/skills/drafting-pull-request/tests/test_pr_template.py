#!/usr/bin/env python3
"""Unit tests for pr-template.md and drafting-pull-request SKILL.md alignment.

Validates the canonical PR body template structure, ensuring the adoption of
the third-person narrative summary recipe, elimination of redundant diff sections
(Changes Made, Context & Motivation), generic test execution recording format,
and bidirectional alignment with SKILL.md execution instructions.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

# Paths to the target reference files
SKILL_DIR = Path(__file__).resolve().parent.parent
PR_TEMPLATE_PATH = SKILL_DIR / "references" / "pr-template.md"
SKILL_MD_PATH = SKILL_DIR / "SKILL.md"


class TestPRTemplateStructure(unittest.TestCase):
    """Test suite validating structure, rules, and placeholders in pr-template.md."""

    @classmethod
    def setUpClass(cls) -> None:
        """Load reference template content before running assertions."""
        cls.template_content = PR_TEMPLATE_PATH.read_text(encoding="utf-8")
        cls.skill_content = SKILL_MD_PATH.read_text(encoding="utf-8")

    def test_pr_template_required_headings(self) -> None:
        """Verify that pr-template.md contains the canonical primary headings in exact order."""
        expected_headings = [
            "## Summary",
            "## Key Design Decisions & Trade-offs",
            "## Breaking Changes",
            "## Related Issues",
            "## Verification & Testing",
        ]

        # Extract all Level 2 markdown headings before the <details> folding block
        main_content = self.template_content.split("<details>")[0]
        actual_headings = [
            line.strip()
            for line in main_content.splitlines()
            if line.startswith("## ")
            and not line.startswith("## 1.")
            and not line.startswith("## 2.")
            and not line.startswith("## 3.")
        ]

        self.assertEqual(
            actual_headings,
            expected_headings,
            f"PR template Level 2 headings mismatch. Expected {expected_headings}, but got {actual_headings}",
        )

    def test_elimination_of_legacy_redundant_headings(self) -> None:
        """Verify that legacy redundant headings (Context & Motivation, Changes Made) are eliminated."""
        forbidden_patterns = [
            r"^##\s+Context\s*&\s*Motivation",
            r"^##\s+Summary\s*&\s*Motivation",
            r"^##\s+Changes\s+Made",
            r"^###\s+.*Changes\s+Made",
            r"^###\s+.*Context\s*&\s*Motivation",
        ]

        for pattern in forbidden_patterns:
            with self.subTest(pattern=pattern):
                match = re.search(pattern, self.template_content, re.MULTILINE | re.IGNORECASE)
                self.assertIsNone(
                    match,
                    f"Forbidden legacy heading matching '{pattern}' was found in pr-template.md: {match.group(0) if match else ''}",
                )

    def test_summary_narrative_recipe_and_perspective_rules(self) -> None:
        """Verify that pr-template.md embeds strict narrative recipe and third-person perspective rules."""
        required_guidance_tokens = [
            "NARRATIVE RECIPE",
            "Problem / Why",
            "Solution / What",
            "third-person",
            "NEVER use first-person pronouns",
            "DO NOT list file paths",
        ]

        for token in required_guidance_tokens:
            with self.subTest(token=token):
                self.assertIn(
                    token,
                    self.template_content,
                    f"Required narrative guidance token '{token}' not found in pr-template.md comments.",
                )

    def test_verification_testing_execution_record_format(self) -> None:
        """Verify that Verification & Testing enforces execution records rather than empty checkboxes."""
        # Must not contain empty checkboxes in the template
        self.assertNotIn(
            "- [x] <Validation step 1>",
            self.template_content,
            "Legacy empty checkbox placeholder should be removed from pr-template.md",
        )
        self.assertNotIn(
            "- [ ] <Verification step 2>",
            self.template_content,
            "Legacy empty checkbox placeholder should be removed from pr-template.md",
        )

        # Must enforce Automated Tests and Manual Verification categories
        self.assertIn(
            "Automated Tests",
            self.template_content,
            "Verification & Testing must include 'Automated Tests' placeholder category.",
        )
        self.assertIn(
            "Manual Verification",
            self.template_content,
            "Verification & Testing must include 'Manual Verification' placeholder category.",
        )

    def test_localized_details_full_translation_mirror(self) -> None:
        """Verify that the localized <details> block defines strict <summary> syntax and mirrors all English sections."""
        self.assertIn("<details>", self.template_content)
        self.assertIn("</details>", self.template_content)
        details_content = self.template_content.split("<details>")[1].split("</details>")[0]

        # Must conform to the strict <summary> token syntax rule for Translation
        expected_summary_tag = '<summary>{flag} {Native "Translation" Label} ({English Language Name} Translation)</summary>'
        self.assertIn(
            expected_summary_tag,
            details_content,
            f"Localized details block must use exact syntax: {expected_summary_tag}",
        )

        # Must instruct full translation strictly mirroring all English sections
        self.assertIn(
            "{Full translation of all above sections into the active conversation language",
            details_content,
            "Localized details block must instruct full translation mirroring the English sections.",
        )

        # Ensure no hardcoded language-specific strings remain in the generic template
        forbidden_hardcoded_words = ["破壊的変更", "自動テスト", "手動・環境確認", "実際に実行したコマンド"]
        for word in forbidden_hardcoded_words:
            with self.subTest(word=word):
                self.assertNotIn(
                    word,
                    details_content,
                    f"Hardcoded language-specific word '{word}' found in generic localized template section.",
                )

    def test_decision_and_issues_fallback_rules(self) -> None:
        """Verify that fallbacks for decisions (- None) and issues (None) are explicitly guided."""
        self.assertIn(
            "- None (straightforward implementation following existing patterns)",
            self.template_content,
            "Key Design Decisions must provide an explicit fallback for straightforward changes.",
        )
        self.assertIn(
            "| None}",
            self.template_content,
            "Related Issues placeholder must provide None option when no issue exists.",
        )

    def test_no_angle_bracket_placeholders_in_markdown(self) -> None:
        """Verify that all template placeholders use curly braces ({...}) instead of confusing angle brackets (<...>)."""
        allowed_tags = {"<details>", "</details>", "<summary>", "</summary>", "<!--", "-->"}
        raw_tags = re.findall(r"<[^>]+>", self.template_content)
        unallowed_pseudo_tags = [
            tag
            for tag in raw_tags
            if not any(tag.startswith(allowed) or tag.endswith("-->") for allowed in allowed_tags)
        ]
        self.assertEqual(
            unallowed_pseudo_tags,
            [],
            f"Found confusing pseudo-HTML angle bracket placeholders in pr-template.md: {unallowed_pseudo_tags}. Use {{...}} instead.",
        )

    def test_skill_md_step5_heading_alignment(self) -> None:
        """Verify that SKILL.md Step 5 references pr-template.md and outlines the canonical sections."""
        # Must link to pr-template.md as the canonical reference
        self.assertIn(
            "[`./references/pr-template.md`](./references/pr-template.md)",
            self.skill_content,
            "SKILL.md Step 5 must explicitly reference pr-template.md.",
        )

        expected_skill_section_tokens = [
            "## Summary",
            "## Key Design Decisions & Trade-offs",
            "## Breaking Changes",
            "## Related Issues",
            "## Verification & Testing",
        ]

        for token in expected_skill_section_tokens:
            with self.subTest(token=token):
                self.assertIn(
                    token,
                    self.skill_content,
                    f"SKILL.md Step 5 must outline '{token}' matching pr-template.md.",
                )

        # Ensure legacy contradictory phrases are absent from SKILL.md
        self.assertNotIn(
            "Summary & Motivation",
            self.skill_content,
            "SKILL.md should not use legacy 'Summary & Motivation' composite heading.",
        )
        self.assertNotIn(
            "Changes Made",
            self.skill_content,
            "SKILL.md should not prescribe deprecated 'Changes Made' section.",
        )


if __name__ == "__main__":
    unittest.main()
