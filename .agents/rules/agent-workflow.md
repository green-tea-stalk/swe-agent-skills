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

## 1. Skill Authoring Constraints

When authoring skills in `plugins/`:

- **Portable Frontmatter (Greatest Common Denominator)**: Use ONLY `name` and `description` in `SKILL.md` frontmatter. Do NOT include agent-specific or optional fields (`allowed-tools`, `compatibility`, `metadata`, `license`) to guarantee universal cross-agent compatibility.

---

## 2. Context Isolation Principle (CRITICAL)

Strictly isolate repository meta-development rules from distributed runtime skills:

- **Scope**: Applies strictly to distributed assets under `plugins/`. Local meta-skills under `.agents/skills/` (e.g. `validating-skills`) are internal repository maintenance tools and are not distributed.
- **No Leaked Local Paths**: Never include paths matching `/Users/...` or `~/.gemini/...` in `plugins/`.
- **No Meta-Rule Leak**: Never embed maintainer language preferences (e.g. "respond in Japanese") or repository development rules into distributed skills under `plugins/`.
- **Respect Target Project Context**: Ensure distributed skills inspect the target project's own configuration (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, lint configs).

---

## 3. Mandatory Self-Validation Trigger Rules

Execute the `validating-skills` skill (`.agents/skills/validating-skills/SKILL.md`) for all created or modified skills before completing your task, ensuring the validation workflow completes successfully:

- **Trigger Validation**:
  - Added or modified files in `plugins/*/skills/` (`SKILL.md`, `scripts/`, `references/`)
  - Added or modified subagents in `plugins/*/agents/*.md`
  - Added or modified manifests (`plugins/*/plugin.json`, `plugins/*/.claude-plugin/plugin.json`, `plugins/*/.codex-plugin/plugin.json`)
  - Added or modified meta-skills in `.agents/skills/`
