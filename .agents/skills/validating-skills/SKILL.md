---
name: validating-skills
description: >-
  Use this skill when verifying one or more skills in this repository for compliance
  with Agent Skills open standards, repository context isolation rules, and execution safety.
---

# Validating Skills and Plugins

This local skill validates that skills in this repository comply with Agent Skills standards, repository isolation rules, and execution safety by orchestrating the `skill-spec-analyst` and `skill-reviewer` subagents.

---

## Invocation Arguments

Provide one or more target skill paths when invoking this skill:
- **Single Skill**: e.g., `plugins/git-workflow/skills/committing-changes`
- **Multiple Skills**: e.g., `plugins/git-workflow/skills/committing-changes`, `plugins/git-workflow/skills/drafting-pull-request`

---

## Workflow Protocol

### Step 1: Ensure Fresh Validation Axes
Invoke the **`skill-spec-analyst`** subagent to ensure that the dynamic validation axes (`.agents/skills/validating-skills/.cache/validation_axes.md`) are up-to-date.

---

### Step 2: Audit Target Skills in Parallel
For each target skill provided in the invocation arguments:
- Launch a dedicated **`skill-reviewer`** subagent.
- When multiple skills are specified, launch individual `skill-reviewer` subagents **in parallel** (one subagent instance per skill).
- Provide each subagent with:
  1. The target skill path (e.g. `plugins/git-workflow/skills/committing-changes`).
  2. The validation axes (`.agents/skills/validating-skills/.cache/validation_axes.md`).

---

### Step 3: Collect Review Verdicts
Collect the audit report from each `skill-reviewer` subagent:
- **`APPROVED`**: The skill passes all validation criteria.
- **`CHANGES_REQUIRED`**: The skill has Critical Issues or Warnings that must be addressed.

---

### Step 4: Incremental Remediation Loop
If any skill receives a `CHANGES_REQUIRED` verdict:
1. Fix the identified issues in the offending skill files.
2. Re-launch the `skill-reviewer` subagent **ONLY for the modified skills** (skip skills that are already `APPROVED`).
3. Repeat until all target skills achieve an `APPROVED` verdict.

---

### Step 5: Report Results
Report the final aggregated review summary across all evaluated skills to the user.
