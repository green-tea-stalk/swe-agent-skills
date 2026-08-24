---
trigger: "glob"
globs:
  - "plugins/**/scripts/*.py"
  - ".agents/**/scripts/*.py"
description: "Enforces Python 3 standard library purity and mandatory code review via python-reviewer subagent with convergence loop."
---

# Python Script Quality & Review Rules

Operational standards and review protocol for authoring Python helper scripts in `swe-agent-skills`.

---

## 1. Python 3 Standard Library Purity

All executable helper scripts under `skills/*/scripts/` and `.agents/**/scripts/`:

- **Standard Library Modules Only**: MUST be written using Python 3 standard library modules only. Zero external `pip` dependencies.
- **No Raw Shell Scripts**: Always prefer Python 3 over raw shell scripts to eliminate cross-platform incompatibilities (e.g. macOS BSD vs. Linux GNU tool differences) and ensure robust escaping.

---

## 2. Mandatory Subagent Code Review & Convergence Loop

Whenever creating, modifying, or refactoring Python helper scripts:

- **Delegation to Reviewer Subagent**: You MUST spawn a subagent configured with the dedicated reviewer definition 👉 **[`.agents/agents/python-reviewer.md`](../agents/python-reviewer.md)** to audit the script.
- **Review Scope**: Evaluates against the comprehensive checklist in `python-reviewer.md` (Standard library purity, modern typing, Fail-Closed design, timeouts, compiled regex, and clean architecture).
- **Convergence Loop**: If the reviewer subagent identifies defects (Critical / Warning), apply corrections and request re-review iteratively until the reviewer outputs **`[APPROVED]` (Zero findings)**.
