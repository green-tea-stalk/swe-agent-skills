#!/usr/bin/env python3
"""Deterministic pre-commit helper script for committing-changes skill.

Analyzes the current Git repository state, dynamically verifies branch protection
and default branch configuration via GitHub CLI (`gh`), inspects staged files for
secrets and noise, and extracts diff statistics.

Follows a strict Fail-Closed principle: if GitHub CLI is unavailable or unauthenticated,
execution stops immediately with an error rather than risking incorrect assumptions.
"""

# /// script
# requires-python = ">=3.9"
# ///

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Compiled regex patterns for sensitive files that should not be committed
SENSITIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^\.env(\..+)?$"),                   # .env, .env.local, .env.production (excluding .example/.template)
    re.compile(r".*\.pem$"),                         # RSA / SSL private keys
    re.compile(r".*\.key$"),                         # Private keys
    re.compile(r".*\.pfx$"),                         # PKCS#12 certificates
    re.compile(r".*\.p12$"),                         # PKCS#12 certificates
    re.compile(r".*id_rsa.*"),                       # SSH private keys
    re.compile(r".*id_ed25519.*"),                   # SSH private keys
    re.compile(r".*id_ecdsa.*"),                     # SSH private keys
    re.compile(r".*id_dsa.*"),                       # SSH private keys
    re.compile(r"^credentials\.json$"),              # API credentials
    re.compile(r".*service[-_]account.*\.json$"),    # Cloud service account keys
    re.compile(r".*\.p8$"),                          # Apple private keys
    re.compile(r".*\.keystore$"),                    # Java keystores
    re.compile(r".*\.jks$"),                         # Java keystores
]

# Patterns explicitly allowed even if matching general secret patterns
ALLOWED_SECRET_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r".*\.env\.example$"),
    re.compile(r".*\.env\.template$"),
    re.compile(r".*\.env\.sample$"),
    re.compile(r".*\.env\.dist$"),
]

# Compiled regex patterns for build noise / OS artifacts that should usually be ignored
NOISE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^\.DS_Store$"),
    re.compile(r"^Thumbs\.db$"),
    re.compile(r".*\.pyc$"),
    re.compile(r".*__pycache__/.*"),
    re.compile(r"^node_modules/.*"),
    re.compile(r"^\.terraform/.*"),
    re.compile(r"^target/.*"),
]

COMMAND_TIMEOUT_SECONDS = 15


@dataclass(frozen=True)
class BranchStatus:
    """Structured branch protection and default branch inspection result."""

    branch: str
    is_protected: bool
    is_default: bool
    force_push_restricted: bool
    message: str


def run_git_cmd(args: list[str]) -> tuple[int, str, str]:
    """Execute a Git command and return (exit_code, stdout, stderr)."""
    try:
        res = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except FileNotFoundError:
        return 127, "", "git executable not found in PATH."
    except subprocess.TimeoutExpired:
        return 124, "", f"git command timed out after {COMMAND_TIMEOUT_SECONDS}s."


def run_gh_cmd(args: list[str]) -> tuple[int, str, str]:
    """Execute a GitHub CLI command and return (exit_code, stdout, stderr)."""
    if not shutil.which("gh"):
        return 127, "", "gh CLI not installed."
    try:
        res = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except FileNotFoundError:
        return 127, "", "gh CLI not found."
    except subprocess.TimeoutExpired:
        return 124, "", f"gh command timed out after {COMMAND_TIMEOUT_SECONDS}s."


def is_git_repository() -> bool:
    """Verify that current working directory is inside a Git repository."""
    code, out, _ = run_git_cmd(["rev-parse", "--is-inside-work-tree"])
    return code == 0 and out == "true"


def get_current_branch() -> str:
    """Retrieve current branch name."""
    code, out, _ = run_git_cmd(["branch", "--show-current"])
    if code == 0 and out:
        return out
    # Fallback for detached HEAD
    code, out, _ = run_git_cmd(["rev-parse", "--short", "HEAD"])
    return out if code == 0 else "unknown"


def verify_gh_prerequisites() -> None:
    """Verify GitHub CLI is installed and authenticated. Exits on failure (Fail-Closed)."""
    if not shutil.which("gh"):
        print("[ERROR] GitHub CLI (`gh`) is not installed or not in PATH.", file=sys.stderr)
        print("        Install GitHub CLI (https://cli.github.com/) to continue.", file=sys.stderr)
        sys.exit(1)

    code, _, err = run_gh_cmd(["auth", "status"])
    if code != 0:
        print("[ERROR] GitHub CLI is not authenticated.", file=sys.stderr)
        print(f"        Details: {err or 'Authentication check failed'}", file=sys.stderr)
        print("        Run `gh auth login` to authenticate before preparing commits.", file=sys.stderr)
        sys.exit(1)


def check_branch_protection(branch: str) -> BranchStatus:
    """Check branch protection and default branch status dynamically via GitHub API."""
    is_protected = False
    is_default = False
    force_push_restricted = False
    message = "OK (Working on feature/task branch)"

    # 1. Query remote repository default branch
    gh_code, gh_out, gh_err = run_gh_cmd(["repo", "view", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"])
    if gh_code != 0:
        print(f"[ERROR] Failed to query GitHub repository information: {gh_err}", file=sys.stderr)
        sys.exit(1)

    default_branch = gh_out.strip()
    if branch == default_branch:
        is_default = True
        is_protected = True

    # 2. Query explicit branch protection rules
    prot_code, prot_out, _ = run_gh_cmd(["api", f"repos/:owner/:repo/branches/{branch}/protection"])
    if prot_code == 0 and prot_out:
        try:
            prot_data: dict[str, Any] = json.loads(prot_out)
            is_protected = True
            allow_force = prot_data.get("allow_force_pushes", {}).get("enabled", False)
            force_push_restricted = not allow_force
        except json.JSONDecodeError:
            pass

    if is_protected:
        if force_push_restricted:
            message = (
                f"WARNING! Branch '{branch}' is protected on GitHub (Force Push is FORBIDDEN).\n"
                "                     Consider switching to a feature branch (`git checkout -b feat/<name>`)."
            )
        else:
            message = (
                f"WARNING! Branch '{branch}' is a default/protected branch on GitHub.\n"
                "                     Consider creating a feature branch (`git checkout -b feat/<name>`)."
            )

    return BranchStatus(
        branch=branch,
        is_protected=is_protected,
        is_default=is_default,
        force_push_restricted=force_push_restricted,
        message=message,
    )


def get_staged_files() -> list[tuple[str, str]]:
    """Retrieve list of staged files as (status_code, file_path)."""
    code, out, _ = run_git_cmd(["diff", "--cached", "--name-status"])
    if code != 0 or not out:
        return []

    staged: list[tuple[str, str]] = []
    for line in out.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            staged.append((parts[0].strip(), parts[1].strip()))
    return staged


def get_unstaged_files_summary() -> list[str]:
    """Retrieve list of untracked and modified unstaged files."""
    code, out, _ = run_git_cmd(["status", "--porcelain"])
    if code != 0 or not out:
        return []

    unstaged: list[str] = []
    for line in out.splitlines():
        if len(line) >= 3:
            index_status = line[0]
            worktree_status = line[1]
            filepath = line[3:].strip()
            if index_status == " " or worktree_status != " ":
                unstaged.append(f"{line[:2]} {filepath}")
    return unstaged


def check_sensitive_files(staged_files: list[tuple[str, str]]) -> list[str]:
    """Detect staged files matching sensitive secret patterns."""
    warnings: list[str] = []
    for _, filepath in staged_files:
        filename = Path(filepath).name
        if any(p.match(filename) for p in ALLOWED_SECRET_PATTERNS):
            continue
        if any(p.match(filename) or p.match(filepath) for p in SENSITIVE_PATTERNS):
            warnings.append(filepath)
    return warnings


def check_noise_files(staged_files: list[tuple[str, str]]) -> list[str]:
    """Detect staged files matching build artifact or OS noise patterns."""
    noise: list[str] = []
    for _, filepath in staged_files:
        filename = Path(filepath).name
        if any(p.match(filename) or p.match(filepath) for p in NOISE_PATTERNS):
            noise.append(filepath)
    return noise


def get_diff_stat() -> str:
    """Retrieve git diff stat for staged changes."""
    code, out, _ = run_git_cmd(["diff", "--cached", "--stat"])
    return out if code == 0 else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-commit inspection script.")
    parser.parse_args()

    if not is_git_repository():
        print("[ERROR] Current directory is not a Git repository.", file=sys.stderr)
        return 1

    # Strict prerequisite check (Fail-Closed)
    verify_gh_prerequisites()

    branch = get_current_branch()
    branch_info = check_branch_protection(branch)
    staged_files = get_staged_files()
    unstaged_summary = get_unstaged_files_summary()
    sensitive_warnings = check_sensitive_files(staged_files)
    noise_warnings = check_noise_files(staged_files)
    diff_stat = get_diff_stat()

    print("=" * 60, file=sys.stderr)
    print("Pre-Commit Inspection Report", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # 1. Branch Status
    print("\n[1] Branch Status", file=sys.stderr)
    status_label = "[PROTECTED]" if branch_info.is_protected else "[SAFE]"
    print(f"  * Current Branch : {branch} {status_label}", file=sys.stderr)
    print(f"  * Branch Safety  : {branch_info.message}", file=sys.stderr)

    # 2. Staging & Safety Inspection
    print("\n[2] Staging & Safety Inspection", file=sys.stderr)
    if not staged_files:
        print("  * Staged Files   : None (No changes staged for commit).", file=sys.stderr)
        print("  * Action Needed  : Run `git add <files>` to stage specific atomic changes before committing.", file=sys.stderr)
    else:
        print(f"  * Staged Count   : {len(staged_files)} file(s)", file=sys.stderr)
        for status, path in staged_files:
            print(f"      [{status}] {path}", file=sys.stderr)

    # Safety Warnings
    if sensitive_warnings:
        print("\n  [!] SECURITY WARNING - Sensitive files detected in staging:", file=sys.stderr)
        for path in sensitive_warnings:
            print(f"      - {path}", file=sys.stderr)
        print("      Action: Run `git reset HEAD <file>` to unstage sensitive files before committing.", file=sys.stderr)

    if noise_warnings:
        print("\n  [!] NOISE WARNING - Build artifacts/OS noise detected in staging:", file=sys.stderr)
        for path in noise_warnings:
            print(f"      - {path}", file=sys.stderr)
        print("      Action: Unstage or add to .gitignore.", file=sys.stderr)

    # 3. Diff Statistics
    print("\n[3] Staged Changes Summary", file=sys.stderr)
    if diff_stat:
        for line in diff_stat.splitlines():
            print(f"  {line}", file=sys.stderr)
    else:
        print("  (No staged diff available)", file=sys.stderr)

    # 4. Unstaged / Untracked Context
    if unstaged_summary:
        print(f"\n[4] Unstaged / Untracked Changes ({len(unstaged_summary)} items)", file=sys.stderr)
        for item in unstaged_summary[:10]:
            print(f"  {item}", file=sys.stderr)
        if len(unstaged_summary) > 10:
            print(f"  ... and {len(unstaged_summary) - 10} more items.", file=sys.stderr)

    print("\n" + "=" * 60, file=sys.stderr)
    print("Ready to construct Conventional Commit message:", file=sys.stderr)
    print("  Format : <type>(<scope>): <subject>", file=sys.stderr)
    print("           <blank line>", file=sys.stderr)
    print("           <body describing WHY and WHAT based on conversation context>", file=sys.stderr)
    print("           <blank line>", file=sys.stderr)
    print("           Co-Authored-By: <ModelName> <<email>>", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    report_data = {
        "branch_status": {
            "branch": branch,
            "is_protected": branch_info.is_protected,
            "is_default": branch_info.is_default,
            "force_push_restricted": branch_info.force_push_restricted,
            "message": branch_info.message
        },
        "staged_files": [{"status": s, "path": p} for s, p in staged_files],
        "unstaged_summary": unstaged_summary,
        "sensitive_warnings": sensitive_warnings,
        "noise_warnings": noise_warnings,
        "diff_stat": diff_stat
    }
    
    print(json.dumps(report_data, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
