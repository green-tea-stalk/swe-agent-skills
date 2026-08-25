---
name: drafting-pull-request
description: >-
  Use this skill when creating a new draft pull request or updating an existing PR on GitHub. Inspects repository state, uncommitted changes, branch safety, and remote sync, extracts objective design decisions and trade-offs via decision-analyst subagent, and formats release-please compatible PRs with localized folding.
---

# Drafting Pull Requests

This skill guides the inspection, preparation, design decision analysis, and execution of new Draft Pull Requests (or automated updates of existing open PRs) on GitHub.

---

## Workflow Protocol

Follow these sequential steps whenever drafting or updating a Pull Request:

### Step 1: Run Pre-PR Inspection Script
Execute the deterministic helper script from the skill directory to inspect repository metadata, branch safety, uncommitted changes, remote sync status, and existing PRs:

```bash
python3 scripts/prepare_pr.py
```

Inspect the generated report carefully:
1. **Target Repository**: Verify the working repository NWO (`owner/repo`) and default branch.
2. **Branch Protection**: Note if current branch is `[PROTECTED]`.
3. **Uncommitted Changes**: Note any staged, unstaged, or untracked changes.
4. **Remote Sync Status**: Check whether push or synchronization is required.
5. **Existing PR Status**: Check if current branch already has an open PR.

---

### Step 2: Handle Branch Safety & Uncommitted Changes

1. **Branch Protection Protocol (First)**:
   - If the current branch is marked as `[PROTECTED]`, synthesize an appropriate feature branch name from the conversation context (e.g. `feat/user-authentication` or `fix/cache-invalidation`) and switch to it first:
     ```bash
     git checkout -b <branch-name>
     ```

2. **Uncommitted Changes Protocol**:
   - If active task changes exist in the working tree, execute the `committing-changes` skill to construct an atomic Conventional Commit.
   - If build noise or OS artifacts exist, add them to `.gitignore`.
   - If uncommitted changes cannot be safely classified, **HALT execution safely (Fail-Closed)** and inform the user. Never run auto-stash or destructive discard.

3. **Zero Commits Validation (Fail-Closed)**:
   - After resolving uncommitted changes, if the commit count against the base branch is still 0 (no diff commits exist), **HALT execution safely (Fail-Closed)** and inform the user that a PR cannot be created because there are no new commits.

---

### Step 3: Ensure Remote Synchronization

Synchronize the local branch with the remote repository according to the sync status:
- **`NO_UPSTREAM`**: Run `git push -u origin <branch>` to publish the branch.
- **`AHEAD`**: Run `git push` to upload local commits.
- **`UP_TO_DATE`**: Skip push (already synchronized).
- **`BEHIND`**: Run `git pull --ff-only` to integrate remote changes without history rewriting.
- **`DIVERGED`**: **STOP safely (Fail-Closed)**. Do not execute `rebase` or `push --force`. Report diverged state to the user.

---

### Step 4: Extract Design Decisions via `decision-analyst` Subagent

Invoke the dedicated `decision-analyst` subagent to analyze the session context and diff:
- **Purpose**: Extract genuine, high-value design decisions and architectural trade-offs where multiple viable approaches existed.
- **Filter**: Exclude bug fix iterations, AI hallucinations, and trivial choices.

---

### Step 5: Construct PR Title & Structured Body

Formulate the PR title and body following the specification in [`pr-template.md`](./references/pr-template.md):

1. **PR Title (`release-please` compatible)**:
   - Format: `<type>(<scope>): <subject>` (e.g. `feat(git-workflow): add drafting-pull-request skill`)
2. **PR Body Structure**:
   - **Summary**: High-level bullet points.
   - **Context & Motivation**: The problem and why this change was made.
   - **Key Design Decisions & Trade-offs**: Extracted by `decision-analyst`.
   - **Changes Made**: Structured technical breakdown.
   - **Related Issues**: `Closes #<id>`, `Fixes #<id>`, or `Relates to #<id>`.
   - **Verification & Testing**: Commands and validation steps performed.
3. **Conversation Language Dynamic Folding**:
   - If the user conversation is in English: Omit the `<details>` block.
   - If the conversation is in any other language (e.g. Japanese, Chinese, Spanish, French): Append the `<details>` section containing full translations.

---

### Step 6: Create or Update Pull Request

Execute the appropriate GitHub CLI command based on existing PR and extension status:

#### Scenario A: Create New Draft PR (Standard)
```bash
gh pr create --repo <owner/repo> --draft --title "<title>" --body "<body>"
```

#### Scenario B: Update Existing Open PR
If an open PR already exists for the current branch, update its title and body with the latest changes:
```bash
gh pr edit <pr-url> --title "<title>" --body "<body>"
```

#### Scenario C: Create Stacked Draft PR (when `gh-stack` is available)
If the base branch has an open PR and the `gh-stack` extension is installed:
```bash
# 1. Create the draft PR targeting the parent base branch
gh pr create --repo <owner/repo> --base <parent-branch> --draft --title "<title>" --body "<body>"

# 2. Link the new PR with the parent branch into a GitHub stack
gh stack link <parent-branch> <current-branch>
```

---

## Validation Steps

Verify the Pull Request creation or update:

1. **Verify PR URL & State**:
   ```bash
   gh pr view --json number,title,url,isDraft,state
   ```
   Confirm the PR exists in Draft state (or active state) with the intended title.
2. **Review Rendered Description**:
   Ensure all sections, issue links, and localized details blocks render properly on GitHub.
