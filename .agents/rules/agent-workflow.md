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
- **Standard 5-Section Skill Documentation Contract**: Every skill's `README.md` and `README.ja.md` MUST strictly follow this uniform 5-section architecture:
  1. `## 1. Overview & Objectives` / `## 1. 概要と目的`
  2. `## 2. Core Standards & Architectural Pillars` / `## 2. アーキテクチャの柱とコア標準` (includes foundational SWE standards table)
  3. `## 3. Tooling & Subagent Architecture` / `## 3. ツールとサブエージェントアーキテクチャ` (includes directory layout and component map)
  4. `## 4. Sequential Workflow Protocol` / `## 4. シーケンシャルワークフロープロトコル` (includes Mermaid flowchart and step breakdown)
  5. `## 5. Output Artifacts & Verification` / `## 5. 生成成果物と検証` (includes artifact contract and verification commands)
- **Bilingual Documentation Policy & 1:1 Parity**: When adding or updating a skill, you MUST create or update the English `README.md` first as the Single Source of Truth (SSOT). Only after finalizing the English documentation may you derive and update the Japanese `README.ja.md`. Both documents MUST maintain strict 1:1 line-by-line mirror parity (exact identical line counts) and topological parity for tables and Mermaid diagrams.

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
