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
Execute the deterministic helper script from the skill directory to inspect branch safety, secrets, staging state, and diff statistics:

```bash
python3 scripts/prepare_commit.py
```

Inspect the generated report:
1. **Branch Safety**:
   - If marked as `[PROTECTED]`, evaluate whether direct commit to default branch is intended. If working on a collaborative project or protection rules apply, switch to a feature branch (`git checkout -b feat/<name>`).
2. **Staging & Security Check**:
   - If **SECURITY WARNING** appears (`.env`, private keys, credentials), immediately unstage them (`git reset HEAD <file>`).
   - If **NOISE WARNING** appears (`.DS_Store`, build artifacts), unstage or add them to `.gitignore`.
3. **Atomic Scope**:
   - Ensure the staged files represent a single logical unit of work (Atomic Commit). If unrelated changes are staged together, split them into separate commits.

---

### Step 2: Construct Context-Rich Conventional Commit Message
Formulate the commit message using **Conventional Commits** format combined with the **conversation context (the "Why")** and a model-specific **Co-Authored-By** trailer:

#### Structure
```text
<type>(<scope>): <imperative subject summary (max 50 chars)>

<body explaining WHY this change was made, referencing user requests, design decisions, or problem context>

Co-Authored-By: <AgentName> <ModelName> <<email>>
```

#### Co-Author Trailer Guidelines
Append the co-author trailer matching the active AI coding agent and specific model:
- **Format**: `Co-Authored-By: <AgentName> <ModelName> <<email>>`
  - *Note: If the model name contains parentheses (e.g., `Gemini 3.1 Pro (High)`), you MUST enclose the entire author name in double quotes to prevent breaking Git/GitHub parsing. (e.g. `Co-Authored-By: "Antigravity Gemini 3.1 Pro (High)" <gemini@google.com>`)*
- **Examples**:
  - **Claude Code**: `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`
  - **Google Antigravity**: `Co-Authored-By: "Antigravity Gemini 3.1 Pro (High)" <gemini@google.com>`
  - **OpenAI Codex**: `Co-Authored-By: Codex GPT-5.6 Sol <codex@openai.com>`

#### Type Selection Guidelines
- `feat`: New feature or user-facing capability.

- `fix`: Bug fix.
- `refactor`: Code change that neither fixes a bug nor adds a feature.
- `perf`: Performance improvement.
- `test`: Adding or correcting tests.
- `docs`: Documentation only changes.
- `build`: Build system or external dependency changes.
- `ci`: CI configuration files and scripts.
- `chore`: Maintenance tasks, repo tooling, or housekeeping.

- **Subject**: Imperative mood, present tense (e.g. `add user authentication`, not `added` or `adds`). No trailing period.
- **Body**: Essential context derived from user conversations (the motivation, alternative considerations, or problem background).

---

### Step 3: Execute Commit
Run the commit command with the constructed message and Co-Author trailer:

```bash
git commit -m "<type>(<scope>): <subject>" -m "<body explaining why and what>" -m 'Co-Authored-By: <AgentName> <ModelName> <<email>>'
```


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
