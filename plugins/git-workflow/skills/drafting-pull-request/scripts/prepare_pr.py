#!/usr/bin/env python3
"""Deterministic pre-PR helper script for drafting-pull-request skill.

Analyzes Git repository state, verifies GitHub CLI (`gh`) authentication,
inspects target repository information (always prioritizing the current working repo),
detects branch protection, uncommitted changes, remote sync status, existing open PRs,
associated issue candidates, and gh-stack extension availability.

Follows a strict Fail-Closed principle: stops immediately on prerequisite failures.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import urllib.parse
from dataclasses import dataclass
from typing import Any

ISSUE_NUM_PATTERN = re.compile(r"(?:#|issue-|issue/|gh-)(\d+)", re.IGNORECASE)
COMMAND_TIMEOUT_SECONDS = 15


@dataclass(frozen=True)
class TargetRepoInfo:
    """Target repository metadata."""

    owner: str
    name: str
    nwo: str
    default_branch: str
    is_fork: bool


@dataclass(frozen=True)
class BranchInfo:
    """Branch protection and status."""

    name: str
    is_protected: bool
    is_default: bool
    message: str


@dataclass(frozen=True)
class SyncInfo:
    """Remote upstream synchronization status."""

    status: str
    ahead: int
    behind: int
    upstream: str
    message: str


@dataclass(frozen=True)
class ExistingPRInfo:
    """Existing open PR information for the current branch."""

    exists: bool
    number: int | None
    url: str | None
    title: str | None
    is_draft: bool | None


@dataclass(frozen=True)
class IssueCandidate:
    """GitHub issue candidate."""

    number: int
    title: str
    is_matched: bool


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
        print("        Run `gh auth login` to authenticate before preparing PRs.", file=sys.stderr)
        sys.exit(1)


def get_target_repo_info() -> TargetRepoInfo:
    """Retrieve target working repository metadata via GitHub CLI."""
    code, out, err = run_gh_cmd([
        "repo", "view",
        "--json", "owner,name,defaultBranchRef,isFork",
    ])
    if code != 0 or not out:
        print(f"[ERROR] Failed to query GitHub repository information: {err}", file=sys.stderr)
        sys.exit(1)

    try:
        data: dict[str, Any] = json.loads(out)
        owner_data = data.get("owner") or {}
        owner = owner_data.get("login", "") if isinstance(owner_data, dict) else ""
        name = data.get("name") or ""
        nwo = f"{owner}/{name}" if owner and name else ""
        default_ref = data.get("defaultBranchRef") or {}
        default_branch = default_ref.get("name", "main") if isinstance(default_ref, dict) else "main"
        is_fork = bool(data.get("isFork", False))
        return TargetRepoInfo(
            owner=owner,
            name=name,
            nwo=nwo,
            default_branch=default_branch,
            is_fork=is_fork,
        )
    except json.JSONDecodeError as exc:
        print(f"[ERROR] Failed to parse repository metadata JSON: {exc}", file=sys.stderr)
        sys.exit(1)


def check_branch_protection(branch: str, default_branch: str) -> BranchInfo:
    """Check branch protection dynamically via GitHub API and default branch comparison."""
    is_default = branch == default_branch
    is_protected = is_default

    encoded_branch = urllib.parse.quote(branch, safe="")
    prot_code, prot_out, _ = run_gh_cmd(["api", f"repos/:owner/:repo/branches/{encoded_branch}/protection"])
    if prot_code == 0 and prot_out:
        is_protected = True

    if is_protected:
        message = (
            f"WARNING: Branch '{branch}' is protected or default on GitHub.\n"
            "         You must create and switch to a feature branch (`git checkout -b <name>`) before creating a PR."
        )
    else:
        message = f"SAFE (Working on non-protected branch '{branch}')"

    return BranchInfo(
        name=branch,
        is_protected=is_protected,
        is_default=is_default,
        message=message,
    )


def get_uncommitted_changes() -> tuple[list[str], list[str], list[str]]:
    """Inspect git status and categorize uncommitted changes into (staged, unstaged, untracked)."""
    code, out, _ = run_git_cmd(["status", "--porcelain"])
    if code != 0 or not out:
        return [], [], []

    staged: list[str] = []
    unstaged: list[str] = []
    untracked: list[str] = []

    for line in out.splitlines():
        if len(line) < 3:
            continue
        index_status = line[0]
        worktree_status = line[1]
        filepath = line[2:].strip()

        if index_status == "?" and worktree_status == "?":
            untracked.append(filepath)
        else:
            if index_status not in (" ", "?"):
                staged.append(filepath)
            if worktree_status not in (" ", "?"):
                unstaged.append(filepath)

    return staged, unstaged, untracked


def get_remote_sync_status(branch: str) -> SyncInfo:
    """Inspect remote tracking branch synchronization status (ahead/behind counts)."""
    code, upstream, _ = run_git_cmd(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if code != 0 or not upstream:
        return SyncInfo(
            status="NO_UPSTREAM",
            ahead=0,
            behind=0,
            upstream="",
            message=f"No remote tracking branch set. Must run `git push -u origin {branch}`.",
        )

    code, counts, _ = run_git_cmd(["rev-list", "--left-right", "--count", f"HEAD...{upstream}"])
    if code != 0 or not counts:
        return SyncInfo(
            status="UNKNOWN",
            ahead=0,
            behind=0,
            upstream=upstream,
            message=f"Could not determine sync status with {upstream}.",
        )

    parts = counts.split()
    ahead = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
    behind = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0

    if ahead == 0 and behind == 0:
        return SyncInfo(
            status="UP_TO_DATE",
            ahead=0,
            behind=0,
            upstream=upstream,
            message="Local branch is fully up-to-date with remote. Push is not needed.",
        )
    if ahead > 0 and behind == 0:
        return SyncInfo(
            status="AHEAD",
            ahead=ahead,
            behind=0,
            upstream=upstream,
            message=f"Local branch is ahead by {ahead} commit(s). Run `git push` before creating PR.",
        )
    if ahead == 0 and behind > 0:
        return SyncInfo(
            status="BEHIND",
            ahead=0,
            behind=behind,
            upstream=upstream,
            message=f"Local branch is behind remote by {behind} commit(s). Run `git pull --ff-only`.",
        )
    return SyncInfo(
        status="DIVERGED",
        ahead=ahead,
        behind=behind,
        upstream=upstream,
        message=f"Branch has diverged (Ahead: {ahead}, Behind: {behind}). Do NOT rebase/force-push; resolve safely.",
    )


def check_existing_pr(branch: str) -> ExistingPRInfo:
    """Check if an open pull request already exists for the current branch."""
    code, out, _ = run_gh_cmd([
        "pr", "list",
        "--head", branch,
        "--state", "open",
        "--json", "number,url,title,isDraft",
    ])
    if code != 0 or not out:
        return ExistingPRInfo(exists=False, number=None, url=None, title=None, is_draft=None)

    try:
        prs: list[dict[str, Any]] = json.loads(out)
        if prs:
            first = prs[0]
            return ExistingPRInfo(
                exists=True,
                number=first.get("number"),
                url=first.get("url"),
                title=first.get("title"),
                is_draft=first.get("isDraft"),
            )
    except json.JSONDecodeError:
        pass
    return ExistingPRInfo(exists=False, number=None, url=None, title=None, is_draft=None)


def get_commit_diff_stats(base_branch: str) -> tuple[int, list[str], str]:
    """Retrieve commit count, commit logs, and diff stat compared to the base branch."""
    cnt_code, cnt_out, _ = run_git_cmd(["rev-list", "--count", f"{base_branch}..HEAD"])
    commit_count = int(cnt_out) if cnt_code == 0 and cnt_out.isdigit() else 0

    log_code, log_out, _ = run_git_cmd(["log", f"{base_branch}..HEAD", "--oneline", "-n", "10"])
    commits = log_out.splitlines() if log_code == 0 and log_out else []

    diff_code, diff_out, _ = run_git_cmd(["diff", f"{base_branch}...HEAD", "--stat"])
    diff_stat = diff_out if diff_code == 0 else ""

    return commit_count, commits, diff_stat


def find_issue_candidates(branch: str, commits: list[str]) -> list[IssueCandidate]:
    """Find open issue candidates and match against branch name and commit messages."""
    found_nums: set[int] = set()

    for match in ISSUE_NUM_PATTERN.finditer(branch):
        found_nums.add(int(match.group(1)))

    for commit in commits:
        for match in ISSUE_NUM_PATTERN.finditer(commit):
            found_nums.add(int(match.group(1)))

    candidates: list[IssueCandidate] = []
    code, out, _ = run_gh_cmd([
        "issue", "list",
        "--state", "open",
        "--limit", "10",
        "--json", "number,title",
    ])
    if code == 0 and out:
        try:
            issues: list[dict[str, Any]] = json.loads(out)
            for iss in issues:
                num = iss.get("number", 0)
                title = iss.get("title", "")
                is_matched = num in found_nums
                candidates.append(IssueCandidate(number=num, title=title, is_matched=is_matched))
        except json.JSONDecodeError:
            pass

    return candidates


def check_gh_stack_availability(base_branch: str, default_branch: str) -> tuple[bool, str]:
    """Check if gh-stack extension is installed and if base branch has an open PR."""
    code, out, _ = run_gh_cmd(["extension", "list"])
    is_stack_installed = False
    if code == 0 and out:
        for line in out.splitlines():
            if "stack" in line.lower():
                is_stack_installed = True
                break

    if not is_stack_installed:
        return False, "gh-stack extension is not installed."

    if base_branch == default_branch:
        return False, f"gh-stack is installed (Base '{base_branch}' is default branch; standard draft PR applies)."

    pr_info = check_existing_pr(base_branch)
    if pr_info.exists:
        return True, f"gh-stack is installed and base branch '{base_branch}' has open PR #{pr_info.number} (Stacked PR applicable)."

    return False, f"gh-stack is installed, but base branch '{base_branch}' has no open PR (Stacked PR not applicable)."


def main() -> int:
    if not is_git_repository():
        print("[ERROR] Current directory is not a Git repository.", file=sys.stderr)
        return 1

    verify_gh_prerequisites()

    repo_info = get_target_repo_info()
    base_branch = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].strip() else repo_info.default_branch
    current_branch = get_current_branch()
    branch_info = check_branch_protection(current_branch, repo_info.default_branch)
    staged, unstaged, untracked = get_uncommitted_changes()
    sync_info = get_remote_sync_status(current_branch)
    existing_pr = check_existing_pr(current_branch)
    commit_count, commits, diff_stat = get_commit_diff_stats(base_branch)
    issue_candidates = find_issue_candidates(current_branch, commits)
    stack_ready, stack_msg = check_gh_stack_availability(base_branch, repo_info.default_branch)

    print("=" * 60)
    print("Pre-PR Inspection Report")
    print("=" * 60)

    # 1. Target Repository
    print("\n[1] Target Repository (Current Working Repo)")
    print(f"  * Repository NWO   : {repo_info.nwo}")
    print(f"  * Default Branch   : {repo_info.default_branch}")
    print(f"  * Base Branch      : {base_branch}")
    print(f"  * Is Fork Repo     : {repo_info.is_fork} (PR will target {repo_info.nwo})")

    # 2. Branch & Protection Status
    print("\n[2] Branch & Protection Status")
    status_label = "[PROTECTED]" if branch_info.is_protected else "[SAFE]"
    print(f"  * Current Branch   : {current_branch} {status_label}")
    print(f"  * Protection Info  : {branch_info.message}")

    # 3. Uncommitted Changes
    total_uncommitted = len(staged) + len(unstaged) + len(untracked)
    print(f"\n[3] Uncommitted Changes ({total_uncommitted} items)")
    if total_uncommitted == 0:
        print("  * Working Tree     : Clean (No uncommitted changes).")
    else:
        print("  [!] WARNING: Uncommitted changes detected in working tree:")
        for path in staged:
            print(f"      [Staged]   {path}")
        for path in unstaged:
            print(f"      [Unstaged] {path}")
        for path in untracked:
            print(f"      [Untracked]{path}")
        print("  * Action Protocol  : Commit active task changes via committing-changes skill,")
        print("                       add noise to .gitignore, or halt safely. Do NOT run auto-stash.")

    # 4. Remote Sync Status
    print("\n[4] Remote Synchronization Status")
    print(f"  * Sync Status      : [{sync_info.status}]")
    print(f"  * Details          : {sync_info.message}")

    # 5. Commit & Diff Statistics
    print(f"\n[5] Commits & Diff vs Base ('{base_branch}')")
    print(f"  * Commit Count     : {commit_count} commit(s)")
    if commit_count == 0:
        print("  [!] WARNING: Zero commits between base branch and HEAD.")
        print("      Cannot create PR without commits. Stage and commit your changes first.")
    else:
        for c in commits:
            print(f"      - {c}")
        if diff_stat:
            print("\n  * Diff Statistics  :")
            for line in diff_stat.splitlines()[:10]:
                print(f"      {line}")

    # 6. Existing PR Status
    print("\n[6] Existing PR Status on Current Branch")
    if existing_pr.exists:
        draft_label = "[Draft]" if existing_pr.is_draft else "[Open]"
        print(f"  * Existing PR      : #{existing_pr.number} {draft_label} - {existing_pr.title}")
        print(f"  * PR URL           : {existing_pr.url}")
        print(f"  * Recommended Mode : UPDATE (Run `gh pr edit {existing_pr.url} --title ... --body ...`)")
    else:
        print("  * Existing PR      : None (Ready for new Draft PR creation).")

    # 7. Issue Candidates
    print("\n[7] Associated Issue Candidates")
    if issue_candidates:
        for iss in issue_candidates:
            star = "[MATCHED] " if iss.is_matched else "          "
            print(f"  {star}#{iss.number}: {iss.title}")
    else:
        print("  * No open issue candidates found.")

    # 8. Stacked PR & Extension Info
    print("\n[8] Stacked PR Readiness")
    print(f"  * gh-stack Status  : {stack_msg}")

    # 9. Next Steps
    print("\n" + "=" * 60)
    print("Actionable Recommendations:")
    if branch_info.is_protected:
        print("  1. Switch to a feature branch: `git checkout -b feat/<name>`")
    if total_uncommitted > 0:
        print("  2. Resolve uncommitted changes before proceeding.")
    if sync_info.status == "NO_UPSTREAM":
        print(f"  3. Push branch to remote: `git push -u origin {current_branch}`")
    elif sync_info.status == "AHEAD":
        print(f"  3. Push local commits to remote: `git push`")

    if existing_pr.exists:
        print(f"  4. Invoke `decision-analyst` and UPDATE PR via:")
        print(f"     `gh pr edit {existing_pr.url} --title \"...\" --body \"...\"`")
    elif base_branch != repo_info.default_branch and stack_ready:
        print(f"  4. Invoke `decision-analyst` and CREATE Stacked draft PR via:")
        print(f"     `gh pr create --repo {repo_info.nwo} --base {base_branch} --draft --title \"...\" --body \"...\"`")
        print(f"     `gh stack link {base_branch} {current_branch}`")
    else:
        print(f"  4. Invoke `decision-analyst` and CREATE draft PR via:")
        print(f"     `gh pr create --repo {repo_info.nwo} --draft --title \"...\" --body \"...\"`")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
