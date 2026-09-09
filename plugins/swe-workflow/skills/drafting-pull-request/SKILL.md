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
python3 scripts/prepare_pr.py [<base-branch>]
```

Pass `<base-branch>` explicitly when creating a Stacked PR or targeting a branch other than the default branch (e.g. `docs/<feature>-spec` or `feat/<feature>-part-1`). If omitted, it defaults to the repository default branch.

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

Invoke the dedicated `decision-analyst` subagent to analyze the session context and git diff:
- **Invocation**: Dispatch the `decision-analyst` subagent ([`../../agents/decision-analyst.md`](../../agents/decision-analyst.md)) to audit the session and diff.
- **Purpose**: Extract genuine, high-value design decisions and architectural trade-offs where multiple viable approaches existed (stating Context, Chosen Approach, Alternatives Considered, and Rationale).
- **Filter**: Strictly filter out bug fixes, syntax adjustments, AI hallucinations, and obvious implementation steps.

---

### Step 5: Construct PR Title & Structured Body

Formulate the PR title and structured description conforming to **Conventional Commits 1.0.0** and automated release workflows:
👉 Consult canonical specifications, templates, and agent instructions in [`./references/pr-template.md`](./references/pr-template.md)

1. **PR Title Construction**:
   - Construct `{type}({scope})[!]: {subject}` conforming to Section 1 of `pr-template.md`.
   - Derive `{type}` from highest SemVer impact in Step 1 commits.
   - Inherit mandatory `{scope}` directly from branch commits (`release-please` requirement).
   - Use imperative mood, present tense, no trailing period.
2. **PR Body Construction**:
   - Render the structured PR body adhering strictly to the template in Section 2 and agent instructions in Section 3 of `pr-template.md`.
   - Incorporate the third-person narrative `## Summary` (Why + What, 3-4 sentences).
   - Integrate architectural trade-offs from `decision-analyst` into `## Key Design Decisions & Trade-offs` (or `- None`).
   - Include `## Breaking Changes` only for SemVer MAJOR changes (otherwise omit).
   - Link issues via `## Related Issues` (`Closes #{id}`, `Fixes #{id}`, `Relates to #{id}`, or `None`).
   - Record actual executed test commands and results in `## Verification & Testing`.
   - If conversation language is not English, append `<details>` with full translation mirror titled `<summary>{flag} {Native "Translation" Label} ({English Language Name} Translation)</summary>`.

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

#### Scenario C: Create Stacked Draft PR (Targeting Base / Parent Branch)
When targeting a base branch other than the default branch (such as an upstream specification branch or a preceding PR branch in a stack):
```bash
# 1. Create the draft PR targeting the base branch
gh pr create --repo <owner/repo> --base <base-branch> --draft --title "<title>" --body "<body>"

# 2. Link the new PR into a GitHub stack (if gh-stack extension is installed)
gh stack link <base-branch> <current-branch>
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
