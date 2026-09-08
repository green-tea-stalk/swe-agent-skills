"""Unit tests for specification templates frontmatter and lifecycle compliance."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

VALID_STATUSES = {"draft", "in-review", "approved", "superseded"}
SEMVER_REGEX = re.compile(r"^\d+\.\d+\.\d+$")
DATE_REGEX = re.compile(r"^(\d{4}-\d{2}-\d{2}|<YYYY-MM-DD>)$")


def parse_frontmatter(content: str) -> dict[str, str | dict[str, str]]:
    """Parse simple YAML frontmatter between leading --- delimiters."""
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", content, re.DOTALL)
    if not match:
        raise ValueError("Document does not contain valid YAML frontmatter delimiters.")

    raw_yaml = match.group(1)
    result: dict[str, str | dict[str, str]] = {}
    current_parent: str | None = None

    for line in raw_yaml.splitlines():
        line_clean = line.rstrip()
        if not line_clean or line_clean.strip().startswith("#"):
            continue

        # Check nested dictionary indent (e.g., upstream:)
        if line_clean.startswith("  ") and current_parent:
            sub_key, _, sub_val = line_clean.strip().partition(":")
            nested_dict = result.setdefault(current_parent, {})
            if isinstance(nested_dict, dict):
                nested_dict[sub_key.strip()] = sub_val.strip()
            continue

        # Top-level key-value pair
        key, sep, val = line_clean.partition(":")
        if sep:
            key_stripped = key.strip()
            val_stripped = val.strip()
            if not val_stripped:
                current_parent = key_stripped
                result[key_stripped] = {}
            else:
                current_parent = None
                result[key_stripped] = val_stripped

    return result


class TestSpecificationTemplates(unittest.TestCase):
    """Test suite verifying specification templates conform to frontmatter and lifecycle standards."""

    def setUp(self) -> None:
        """Locate specification templates directory."""
        self.references_dir = (
            Path(__file__).resolve().parent.parent / "references"
        )
        self.assertTrue(
            self.references_dir.is_dir(),
            f"References directory must exist: {self.references_dir}",
        )

    def test_template_existence_and_frontmatter_structure(self) -> None:
        """Verify all three specification templates exist with valid frontmatter fields."""
        template_cases = [
            (
                "requirements-template.md",
                "requirements",
                ["feature", "document_type", "version", "status", "updated_at"],
                [],
            ),
            (
                "design-template.md",
                "design",
                [
                    "feature",
                    "document_type",
                    "version",
                    "status",
                    "updated_at",
                    "upstream",
                ],
                ["requirements"],
            ),
            (
                "tasks-template.md",
                "tasks",
                [
                    "feature",
                    "document_type",
                    "version",
                    "status",
                    "updated_at",
                    "upstream",
                ],
                ["requirements", "design"],
            ),
        ]

        for filename, expected_doc_type, required_keys, upstream_keys in template_cases:
            with self.subTest(
                template=filename, expected_doc_type=expected_doc_type
            ):
                template_path = self.references_dir / filename
                self.assertTrue(
                    template_path.is_file(),
                    f"Template file {filename} must exist.",
                )

                content = template_path.read_text(encoding="utf-8")
                frontmatter = parse_frontmatter(content)

                # Verify required top-level keys
                for key in required_keys:
                    self.assertIn(
                        key,
                        frontmatter,
                        f"{filename} frontmatter must contain '{key}'",
                    )

                # Verify document type
                self.assertEqual(
                    frontmatter.get("document_type"),
                    expected_doc_type,
                    f"{filename} document_type must match {expected_doc_type}",
                )

                # Verify version format
                version = str(frontmatter.get("version", ""))
                self.assertTrue(
                    SEMVER_REGEX.match(version),
                    f"{filename} version '{version}' must follow SemVer 2.0.0 format.",
                )

                # Verify status belongs to allowed vocabulary
                status = str(frontmatter.get("status", ""))
                self.assertIn(
                    status,
                    VALID_STATUSES,
                    f"{filename} status '{status}' must be one of {VALID_STATUSES}.",
                )
                self.assertEqual(
                    status,
                    "draft",
                    f"{filename} initial template status must be 'draft'.",
                )

                # Verify updated_at date format
                updated_at = str(frontmatter.get("updated_at", ""))
                self.assertTrue(
                    DATE_REGEX.match(updated_at),
                    f"{filename} updated_at '{updated_at}' must match YYYY-MM-DD format.",
                )

                # Verify nested upstream keys if required
                if upstream_keys:
                    upstream_val = frontmatter.get("upstream")
                    self.assertIsInstance(
                        upstream_val,
                        dict,
                        f"{filename} upstream must be a mapping.",
                    )
                    for u_key in upstream_keys:
                        assert isinstance(upstream_val, dict)
                        self.assertIn(
                            u_key,
                            upstream_val,
                            f"{filename} upstream must contain '{u_key}'",
                        )

    def test_template_guidelines_contain_lifecycle_rules(self) -> None:
        """Verify each template contains embedded guidelines describing the status lifecycle."""
        template_files = [
            "requirements-template.md",
            "design-template.md",
            "tasks-template.md",
        ]

        for filename in template_files:
            with self.subTest(template=filename):
                template_path = self.references_dir / filename
                content = template_path.read_text(encoding="utf-8")

                self.assertIn(
                    "Frontmatter Status Lifecycle",
                    content,
                    f"{filename} guidelines must document Frontmatter Status Lifecycle.",
                )
                self.assertIn(
                    "in-review",
                    content,
                    f"{filename} guidelines must mention 'in-review' status.",
                )
                self.assertIn(
                    "approved",
                    content,
                    f"{filename} guidelines must mention 'approved' status.",
                )
                self.assertIn(
                    "superseded",
                    content,
                    f"{filename} guidelines must mention 'superseded' status.",
                )
                self.assertIn(
                    "updated_at",
                    content,
                    f"{filename} guidelines must mandate updating updated_at.",
                )

    def test_design_template_data_models_table_structure(self) -> None:
        """Verify design-template.md Section 3 specifies data models using structured Markdown tables."""
        design_path = self.references_dir / "design-template.md"
        content = design_path.read_text(encoding="utf-8")

        # Extract Section 3 content up to Section 4
        section_match = re.search(
            r"## 3\. Data Models & Schema Constraints\s*\n(.*?)\n## 4\.",
            content,
            re.DOTALL,
        )
        self.assertIsNotNone(
            section_match,
            "design-template.md must contain '## 3. Data Models & Schema Constraints'",
        )
        assert section_match is not None
        section_3_content = section_match.group(1)

        # Expected table column sets for data models
        expected_table_headers = [
            (
                "Input/Output Model Table",
                ["Field Name", "Type", "Required / Optional", "Constraints", "Description"],
            ),
            (
                "Database Entity Table",
                ["Column Name", "Data Type", "Nullable", "Key / Default", "Indexes", "Description"],
            ),
        ]

        for table_label, columns in expected_table_headers:
            with self.subTest(table=table_label):
                for col in columns:
                    self.assertIn(
                        col,
                        section_3_content,
                        f"design-template.md Section 3 must contain column header '{col}' for {table_label}",
                    )

        # Verify guidance for hierarchical / nested fields is present
        self.assertIn(
            "dot notation",
            section_3_content.lower(),
            "design-template.md Section 3 must provide guidance on hierarchical fields using dot notation.",
        )


if __name__ == "__main__":
    unittest.main()

