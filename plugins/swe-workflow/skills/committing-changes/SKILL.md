---
name: committing-changes
description: >-
  Use this skill when preparing, formatting, and executing Git commits, even if the user does not explicitly mention Git or Conventional Commits. Runs automated pre-commit checks (branch safety, secret detection, staging diff analysis) via helper script and constructs context-rich Conventional Commits with model-specific co-author attribution.
---

# Committing Changes

This skill guides the preparation, inspection, message construction, and execution of Git commits using automated pre-commit analysis and Conventional Commits conventions.

---

## Workflow Protocol

Follow these sequential steps whenever executing a commit:

### Step 1: Run Pre-Commit Inspection Script
Execute the deterministic helper script located in the skill's `scripts/` directory against the current workspace:

```bash
python3 {path-to-skill}/scripts/prepare_commit.py
```
*(Note: Run this command from your active workspace root; do NOT `cd` into the skill directory so Git inspects the target project)*

Inspect the generated report:
1. **Branch Safety**:
   - If marked as `[PROTECTED]`, evaluate whether direct commit to default branch is intended. If working on a collaborative project or protection rules apply, switch to a feature branch (`git checkout -b feat/{name}`).
2. **Staging & Security Check**:
   - If **SECURITY WARNING** appears (`.env`, private keys, credentials), immediately unstage them (`git reset HEAD {file}`).
   - If **NOISE WARNING** appears (`.DS_Store`, build artifacts), unstage or add them to `.gitignore`.
3. **Atomic Scope**:
   - Ensure the staged files represent a single logical unit of work (Atomic Commit). If unrelated changes are staged together, split them into separate commits.

---

### Step 2: Construct Context-Rich Conventional Commit Message
Formulate the commit message conforming to **Conventional Commits 1.0.0** and project release guidelines:

#### Reference Template & Specification
Consult the canonical template, full specification rules, and concrete examples:
👉 [`./references/commit-template.md`](./references/commit-template.md)

#### Structure
```text
{type}({scope})[!]: {imperative subject summary (max 50-72 chars)}

{body explaining WHY this change was made, referencing user requests, design decisions, or problem context}

[BREAKING CHANGE: {description of breaking changes}]
[Closes #{issue-number}]
Co-Authored-By: {AgentName} {ModelName} <{email}>
```

#### Commit Construction Protocol
1. **Type & SemVer Impact**: Select the type matching the code modification (`feat` for new features/MINOR, `fix` for bug fixes/PATCH, `refactor`, `perf`, `test`, `docs`, `style`, `build`, `ci`, `chore`, `revert` per reference).
2. **Scope**: Identify the specific component, package, or subsystem in lowercase `kebab-case` (e.g. `swe-workflow`, `backend`, `auth`). Never omit in component-tracked or monorepo projects.
3. **Breaking Changes**: Append `!` before the colon (e.g. `feat(api)!: ...`) or supply a `BREAKING CHANGE:` footer for breaking API changes (SemVer MAJOR).
4. **Subject**: Imperative mood, present tense (e.g. `add user authentication`, NOT `added` or `adds`), lowercase start recommended, no trailing period.
5. **Body (Required Blank Line)**: Separate from header by exactly one blank line. Detail the motivation, the "Why", and contrast with previous behavior.
6. **Footers (Required Blank Line)**: Separate from body by exactly one blank line. Include issue closure (`Closes #{id}`) and the model-specific `Co-Authored-By` trailer (enclose in double quotes if model name contains parentheses):
   - **Claude Code**: `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`
   - **Google Antigravity**: `Co-Authored-By: "Antigravity Gemini 3.1 Pro (High)" <gemini@google.com>`
   - **OpenAI Codex**: `Co-Authored-By: Codex GPT-5.6 Sol <codex@openai.com>`

---

### Step 3: Execute Commit
Run the commit command with the constructed message components:

```bash
git commit -m "{type}({scope}): {subject}" -m "{body explaining why and what}" -m 'Co-Authored-By: {AgentName} {ModelName} <{email}>'
```
*(Note: If footers like `BREAKING CHANGE:` or `Closes #123` are needed, append them via additional `-m` flags or combine within the footer paragraph)*


---

## Validation Steps

Verify the commit succeeded and message structure is accurate:

1. **Inspect Commit Log**:
   ```bash
   git log -1 --stat
   ```
2. **Check Post-Commit Status**:
   ```bash
   git status
   ```
   Confirm the working tree is clean or remaining unstaged changes are ready for subsequent atomic commits.
