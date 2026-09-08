#!/usr/bin/env python3
"""Unit tests for prepare_commit.py helper script in committing-changes skill.

Validates sensitive file detection, noise filtering, and CLI argument parsing.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Ensure the scripts directory is in sys.path for importing prepare_commit
SCRIPT_DIR = str(Path(__file__).resolve().parent.parent / "scripts")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import prepare_commit


class TestSensitiveFiles(unittest.TestCase):
    """Test suite for sensitive credentials and secret pattern detection."""

    def test_sensitive_file_detection(self) -> None:
        """Table-driven test verifying secret file detection and whitelist filtering."""
        test_cases = [
            {
                "name": "Standard .env file must be flagged",
                "path": ".env",
                "expected_flagged": True,
            },
            {
                "name": "Environment-specific .env.production file must be flagged",
                "path": ".env.production",
                "expected_flagged": True,
            },
            {
                "name": "Whitelisted .env.example must NOT be flagged",
                "path": ".env.example",
                "expected_flagged": False,
            },
            {
                "name": "Whitelisted .env.template must NOT be flagged",
                "path": ".env.template",
                "expected_flagged": False,
            },
            {
                "name": "RSA private key must be flagged",
                "path": "certs/server.pem",
                "expected_flagged": True,
            },
            {
                "name": "SSH id_rsa must be flagged",
                "path": "keys/id_rsa",
                "expected_flagged": True,
            },
            {
                "name": "Google service account JSON must be flagged",
                "path": "service-account.json",
                "expected_flagged": True,
            },
            {
                "name": "Normal source file must NOT be flagged",
                "path": "src/app.py",
                "expected_flagged": False,
            },
        ]

        for tc in test_cases:
            with self.subTest(msg=tc["name"]):
                staged = [("M", tc["path"])]
                flagged = prepare_commit.check_sensitive_files(staged)
                if tc["expected_flagged"]:
                    self.assertIn(
                        tc["path"],
                        flagged,
                        f"Expected {tc['path']} to be flagged as sensitive",
                    )
                else:
                    self.assertNotIn(
                        tc["path"],
                        flagged,
                        f"Expected {tc['path']} to be allowed (not flagged)",
                    )


class TestNoiseFiles(unittest.TestCase):
    """Test suite for build artifact and OS noise pattern detection."""

    def test_noise_file_detection(self) -> None:
        """Table-driven test verifying OS noise and build artifact detection."""
        test_cases = [
            {
                "name": "macOS .DS_Store must be flagged as noise",
                "path": ".DS_Store",
                "expected_flagged": True,
            },
            {
                "name": "Windows Thumbs.db must be flagged as noise",
                "path": "Thumbs.db",
                "expected_flagged": True,
            },
            {
                "name": "Python compiled pyc must be flagged as noise",
                "path": "app.pyc",
                "expected_flagged": True,
            },
            {
                "name": "Python __pycache__ must be flagged as noise",
                "path": "src/__pycache__/app.cpython-311.pyc",
                "expected_flagged": True,
            },
            {
                "name": "Normal source file must NOT be flagged as noise",
                "path": "src/main.py",
                "expected_flagged": False,
            },
        ]

        for tc in test_cases:
            with self.subTest(msg=tc["name"]):
                staged = [("A", tc["path"])]
                flagged = prepare_commit.check_noise_files(staged)
                if tc["expected_flagged"]:
                    self.assertIn(
                        tc["path"],
                        flagged,
                        f"Expected {tc['path']} to be flagged as noise",
                    )
                else:
                    self.assertNotIn(
                        tc["path"],
                        flagged,
                        f"Expected {tc['path']} to NOT be flagged as noise",
                    )


class TestArgumentParser(unittest.TestCase):
    """Test suite for CLI argument parsing behavior in prepare_commit."""

    def test_argument_parser_options(self) -> None:
        """Table-driven test verifying --json flag resolution."""
        test_cases = [
            {
                "name": "No arguments defaults json to False",
                "args": [],
                "expected_json": False,
            },
            {
                "name": "--json flag sets json to True",
                "args": ["--json"],
                "expected_json": True,
            },
        ]

        for tc in test_cases:
            with self.subTest(msg=tc["name"]):
                parser = prepare_commit.build_parser()
                parsed = parser.parse_args(tc["args"])
                self.assertEqual(parsed.json, tc["expected_json"])


if __name__ == "__main__":
    unittest.main()
