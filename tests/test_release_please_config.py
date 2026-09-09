#!/usr/bin/env python3
"""Unit tests for release-please configuration and manifest synchronization.

Validates that release-please-config.json and .release-please-manifest.json adhere to
repository release standards and maintain synchronization across plugin manifests.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "release-please-config.json"
MANIFEST_PATH = REPO_ROOT / ".release-please-manifest.json"


class TestReleasePleaseConfig(unittest.TestCase):
    """Test suite for validating release-please-config.json."""

    def setUp(self) -> None:
        """Load release-please-config.json before each test."""
        self.assertTrue(CONFIG_PATH.exists(), f"Configuration file {CONFIG_PATH} must exist.")
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self.config = json.load(f)

    def test_root_package_configuration(self) -> None:
        """Table-driven test verifying root package properties in release-please-config.json."""
        packages = self.config.get("packages", {})
        self.assertIn(".", packages, "Root package '.' must be configured under 'packages'.")
        root_pkg = packages["."]

        test_cases = [
            {
                "name": "release-type must be 'simple'",
                "key": "release-type",
                "expected": "simple",
            },
            {
                "name": "package-name must be 'swe-agent-skills'",
                "key": "package-name",
                "expected": "swe-agent-skills",
            },
            {
                "name": "include-component-in-tag must be False to preserve clean vX.Y.Z tags",
                "key": "include-component-in-tag",
                "expected": False,
            },
        ]

        for case in test_cases:
            with self.subTest(case=case["name"]):
                actual = root_pkg.get(case["key"])
                self.assertEqual(
                    actual,
                    case["expected"],
                    f"Expected '{case['key']}' to be {case['expected']}, but got {actual}",
                )

    def test_extra_files_exist_and_contain_version(self) -> None:
        """Table-driven test verifying extra-files existence and version field."""
        root_pkg = self.config.get("packages", {}).get(".", {})
        extra_files = root_pkg.get("extra-files", [])
        self.assertGreater(len(extra_files), 0, "extra-files must contain at least one file entry.")

        semver_pattern = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$")

        for entry in extra_files:
            rel_path = entry.get("path")
            with self.subTest(path=rel_path):
                file_path = REPO_ROOT / rel_path
                self.assertTrue(file_path.exists(), f"Configured extra-file '{rel_path}' must exist.")
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.assertIn("version", data, f"'{rel_path}' must have a 'version' field.")
                self.assertTrue(
                    semver_pattern.match(data["version"]),
                    f"Version '{data['version']}' in '{rel_path}' must follow SemVer format.",
                )


class TestReleasePleaseManifest(unittest.TestCase):
    """Test suite for validating .release-please-manifest.json."""

    def test_manifest_version_matches_extra_files(self) -> None:
        """Verify that .release-please-manifest.json matches plugin versions."""
        self.assertTrue(MANIFEST_PATH.exists(), f"Manifest file {MANIFEST_PATH} must exist.")
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertIn(".", manifest, "Root package '.' must exist in manifest.")
        root_version = manifest["."]

        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        extra_files = config.get("packages", {}).get(".", {}).get("extra-files", [])
        for entry in extra_files:
            rel_path = entry.get("path")
            with self.subTest(target=rel_path):
                file_path = REPO_ROOT / rel_path
                with open(file_path, "r", encoding="utf-8") as f:
                    plugin_data = json.load(f)
                self.assertEqual(
                    plugin_data.get("version"),
                    root_version,
                    f"Plugin version in '{rel_path}' must match root manifest version '{root_version}'.",
                )


if __name__ == "__main__":
    unittest.main()
