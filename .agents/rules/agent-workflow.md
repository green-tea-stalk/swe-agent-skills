---
trigger: "glob"
globs:
  - "plugins/**"
  - ".agents/skills/**"
description: "Enforces mandatory skill self-validation and context isolation when modifying skills, subagents, or plugins in this repository."
---

# Agent Workflow & Validation Rules

Operational guidelines for AI coding agents developing, maintaining, or refactoring in `swe-agent-skills`.

---

## 1. Mandatory Self-Validation Trigger Rules

Run the validator script (`python3 .agents/skills/validating-skills/scripts/validate_skills.py`) before completing your task:

- **Trigger Validation (MUST run and pass with exit code 0)**:
  - Added or modified files in `plugins/*/skills/` (`SKILL.md`, `scripts/`, `references/`)
  - Added or modified subagents in `plugins/*/agents/*.md`
  - Added or modified manifests (`plugins/*/plugin.json`, `plugins/*/.claude-plugin/plugin.json`, `plugins/*/.codex-plugin/plugin.json`)
  - Added or modified meta-skills in `.agents/skills/`

---

## 2. Context Isolation Principle (CRITICAL)

Strictly isolate repository meta-development rules from distributed runtime skills:

- **Scope**: Applies strictly to distributed assets under `plugins/`. Local meta-skills under `.agents/skills/` (e.g. `validating-skills`) are internal repository maintenance tools and are not distributed.
- **No Leaked Local Paths**: Never include paths matching `/Users/...` or `~/.gemini/...` in `plugins/`.
- **No Meta-Rule Leak**: Never embed maintainer language preferences (e.g. "respond in Japanese") or repository development rules into distributed skills under `plugins/`.
- **Respect Target Project Context**: Ensure distributed skills inspect the target project's own configuration (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, lint configs).
