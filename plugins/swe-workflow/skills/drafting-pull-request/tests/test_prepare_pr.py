#!/usr/bin/env python3
"""Unit tests for prepare_pr.py helper script.

Validates recommendation command synthesis across varied PR environments,
ensuring strict adherence to base branch arguments for Stacked PRs regardless
of gh-stack extension availability.
"""

from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Ensure the scripts directory is in sys.path for importing prepare_pr
SCRIPT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "scripts")
)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import prepare_pr


class TestGenerateRecommendations(unittest.TestCase):
    """Test suite for recommendation command generation in prepare_pr."""

    def test_recommendation_scenarios(self) -> None:
        """Table-driven test verifying recommendation commands across PR scenarios."""
        test_cases = [
            {
                "name": "Non-default base branch without gh-stack must still include --base",
                "base_branch": "docs/feature-spec",
                "default_branch": "main",
                "current_branch": "feat/feature-phase1",
                "existing_pr": prepare_pr.ExistingPRInfo(
                    exists=False, number=None, url=None, title=None, is_draft=None
                ),
                "stack_ready": False,
                "expected_base_flag": "--base docs/feature-spec",
                "expected_stack_link": False,
                "expected_edit_cmd": False,
            },
            {
                "name": "Non-default base branch with gh-stack must include both --base and gh stack link",
                "base_branch": "feat/feature-phase1",
                "default_branch": "main",
                "current_branch": "feat/feature-phase2",
                "existing_pr": prepare_pr.ExistingPRInfo(
                    exists=False, number=None, url=None, title=None, is_draft=None
                ),
                "stack_ready": True,
                "expected_base_flag": "--base feat/feature-phase1",
                "expected_stack_link": True,
                "expected_edit_cmd": False,
            },
            {
                "name": "Default branch target should create standard PR without --base",
                "base_branch": "main",
                "default_branch": "main",
                "current_branch": "feat/feature-single",
                "existing_pr": prepare_pr.ExistingPRInfo(
                    exists=False, number=None, url=None, title=None, is_draft=None
                ),
                "stack_ready": False,
                "expected_base_flag": None,
                "expected_stack_link": False,
                "expected_edit_cmd": False,
            },
            {
                "name": "Existing open PR should trigger gh pr edit instead of gh pr create",
                "base_branch": "docs/feature-spec",
                "default_branch": "main",
                "current_branch": "feat/feature-phase1",
                "existing_pr": prepare_pr.ExistingPRInfo(
                    exists=True,
                    number=42,
                    url="https://github.com/owner/repo/pull/42",
                    title="WIP: Phase 1",
                    is_draft=True,
                ),
                "stack_ready": False,
                "expected_base_flag": None,
                "expected_stack_link": False,
                "expected_edit_cmd": True,
            },
        ]

        for tc in test_cases:
            with self.subTest(msg=tc["name"]):
                repo_info = prepare_pr.TargetRepoInfo(
                    owner="test-owner",
                    name="test-repo",
                    nwo="test-owner/test-repo",
                    default_branch=tc["default_branch"],
                    is_fork=False,
                )
                branch_info = prepare_pr.BranchInfo(
                    name=tc["current_branch"],
                    is_protected=False,
                    is_default=False,
                    message="SAFE",
                )
                sync_info = prepare_pr.SyncInfo(
                    status="UP_TO_DATE",
                    ahead=0,
                    behind=0,
                    upstream="origin/" + tc["current_branch"],
                    message="Up to date",
                )

                recommendations = prepare_pr.generate_recommendations(
                    branch_info=branch_info,
                    total_uncommitted=0,
                    sync_info=sync_info,
                    existing_pr=tc["existing_pr"],
                    base_branch=tc["base_branch"],
                    repo_info=repo_info,
                    stack_ready=tc["stack_ready"],
                    current_branch=tc["current_branch"],
                )

                combined_output = "\n".join(recommendations)

                if tc["expected_edit_cmd"]:
                    self.assertIn("gh pr edit", combined_output)
                    self.assertIn(tc["existing_pr"].url, combined_output)
                    self.assertNotIn("gh pr create", combined_output)
                else:
                    self.assertIn("gh pr create", combined_output)
                    if tc["expected_base_flag"]:
                        self.assertIn(
                            tc["expected_base_flag"],
                            combined_output,
                            f"Failed on: {tc['name']} - output was: {combined_output}",
                        )
                    else:
                        self.assertNotIn(
                            "--base",
                            combined_output,
                            f"Failed on: {tc['name']} - should not include --base",
                        )

                    if tc["expected_stack_link"]:
                        self.assertIn(
                            f"gh stack link {tc['base_branch']} {tc['current_branch']}",
                            combined_output,
                        )
                    else:
                        self.assertNotIn("gh stack link", combined_output)


class TestArgumentParser(unittest.TestCase):
    """Test suite for CLI argument parsing behavior in prepare_pr."""

    def test_argument_parser_combinations(self) -> None:
        """Table-driven test verifying CLI argument resolution."""
        test_cases = [
            {
                "name": "No arguments provided should default base_branch to None",
                "argv": ["prepare_pr.py"],
                "expected_base_branch": None,
                "expected_json": False,
            },
            {
                "name": "Positional base branch argument provided",
                "argv": ["prepare_pr.py", "docs/feature-spec"],
                "expected_base_branch": "docs/feature-spec",
                "expected_json": False,
            },
            {
                "name": "Positional base branch with --json flag",
                "argv": ["prepare_pr.py", "feat/phase-1", "--json"],
                "expected_base_branch": "feat/phase-1",
                "expected_json": True,
            },
            {
                "name": "Only --json flag provided without base branch",
                "argv": ["prepare_pr.py", "--json"],
                "expected_base_branch": None,
                "expected_json": True,
            },
        ]

        for tc in test_cases:
            with self.subTest(msg=tc["name"]):
                parser = prepare_pr.build_parser()
                args = parser.parse_args(tc["argv"][1:])
                self.assertEqual(args.base_branch, tc["expected_base_branch"])
                self.assertEqual(args.json, tc["expected_json"])


if __name__ == "__main__":
    unittest.main()
