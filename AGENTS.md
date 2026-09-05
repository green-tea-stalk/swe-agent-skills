# AGENTS.md

Welcome to `swe-agent-skills` repository. This document serves as the **Single Source of Truth** for all AI coding agents working on, maintaining, or contributing to this repository.

---

## 1. Project Overview & Vision

`swe-agent-skills` is a repository dedicated to providing reusable **Software Engineering (SWE) skills, workflows, and subagent definitions** packaged as plugins for Google Antigravity, Claude Code, and Codex CLI.

### Target Agents


- **Google Antigravity (AGY)**: `plugin.json`, `skills/`, `agents/`, `AGENTS.md`
- **Claude Code**: `.claude-plugin/plugin.json`, `skills/`, `agents/`, `AGENTS.md`
- **Codex CLI**: `.codex-plugin/plugin.json`, `skills/`, `agents/`, `AGENTS.md`

---

## 2. Context Isolation Principle (CRITICAL)

Agents working in this repository **MUST** understand the strict separation between two distinct execution contexts:

```text
┌────────────────────────────────────────────────────────┐
│ 1. Repository Meta-Development Context (This Repo)     │
│    - Rules in this AGENTS.md apply ONLY while editing  │
│      and maintaining this repository.                  │
└──────────────────────────┬─────────────────────────────┘
                           │ produces
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Runtime / Target Project Context (Distributed End)  │
│    - Skills in plugins/ will be installed into users'  │
│      external, diverse projects.                       │
│    - MUST NOT contain local paths or maintainer rules. │
│    - MUST adapt to target repository's own guidelines. │
└────────────────────────────────────────────────────────┘
```

---

## 3. Agent Operating Rules

Operational rules, context isolation constraints, and automated validation triggers for agents editing this repository are managed in:

👉 **[`.agents/rules/agent-workflow.md`](.agents/rules/agent-workflow.md)**

All AI agents editing this repository must adhere to the rules defined in `.agents/rules/`.

---

## 4. Skill & Agent Authoring Standards

To prevent rule drift and ensure continuous compliance with the evolving Agent Skills open standards, all skills, subagents, and plugin configurations in this repository are **dynamically validated** by the project-local validation skill:


👉 **[`.agents/skills/validating-skills/`](.agents/skills/validating-skills/)**

### Core Compliance Philosophy
- **Dynamic Specification Analysis**: Validation criteria are not statically fixed; instead, the **`skill-spec-analyst`** subagent autonomously interprets the latest official primary documentation (managed via [`manage_validation_cache.py`](.agents/skills/validating-skills/scripts/manage_validation_cache.py)) to formulate the necessary validation axes (`validation_axes.md`).
- **Objective Parallel Auditing**: Whenever skills are created or modified, each target skill is audited objectively and in parallel by dedicated **`skill-reviewer`** subagents (`.agents/agents/skill-reviewer.md`) based on the formulated axes.
- **Incremental Convergence**: If any issues are flagged (`CHANGES_REQUIRED`), the offending files must be fixed and re-audited (running the reviewer subagent only on modified skills) until all target skills achieve an `APPROVED` verdict.

### Key Architectural Decisions
- **Unified Rule-Driven Workflow over Runtime Hooks**: Lifecycle hooks (`hooks.json`) are restricted to executing deterministic shell commands and cannot invoke AI prompt workflows or reviewer subagents. Splitting automated checks across hooks while leaving qualitative AI reviews to explicit rules creates fragmented responsibility. Therefore, we deliberately rely on a unified rule-driven workflow (`.agents/rules/`) that orchestrates cache management scripts (`manage_validation_cache.py`), specification analysis (`skill-spec-analyst.md`), and reviewer subagents (`skill-reviewer.md`, `python-reviewer.md`) in a single consistent framework.

---

## 5. Plugin Architecture


Plugins are packaged units distributing skills and subagents together.

```text
plugins/<plugin-name>/
├── plugin.json                # Google Antigravity manifest
├── .claude-plugin/
│   └── plugin.json            # Claude Code manifest
├── .codex-plugin/
│   └── plugin.json            # Codex CLI manifest
├── skills/                    # Skills (kebab-case gerund directories)
│   └── <skill-name>/
│       ├── SKILL.md
│       ├── scripts/           # Optional
│       └── references/        # Optional
└── agents/                    # Subagents (role-based .md files)
    └── <agent-role>.md
```

---

## 6. Environment & Maintenance

- **Tested Environment**: macOS with Google Antigravity (AGY) only. (The maintainer actively verifies behavior on macOS using AGY. Compatibility for other agents like Claude Code and Codex CLI is maintained strictly by adhering to their official open specifications).
- **Runtime & Tooling Requirements**: Git, GitHub CLI (`gh`), and Python 3 (standard library only, no external dependencies).

---

## 7. Release Management

This repository uses **[release-please](https://github.com/googleapis/release-please)** for automated changelog generation and release creation. All releases are created via GitHub Actions based on Conventional Commits. Agents should format their commits correctly to ensure releases are generated accurately.

---

## 8. Documentation & Localization Policy

To ensure global accessibility, cognitive consistency, and mechanical auditability across all AI coding agents and human engineers, this repository enforces a strict bilingual documentation policy:

- **English as Single Source of Truth (SSOT)**:
  All primary documentation, skill specifications, and architectural definitions are authored in English first (`README.md`, `SKILL.md`).
- **Japanese Derived Documentation (`*.ja.md`)**:
  - The repository root provides a companion `README.ja.md` mirrored from `README.md`.
  - Every skill directory provides a companion `README.ja.md` mirrored from its `README.md`.
- **Strict 1:1 Mirror Parity**:
  - Derived Japanese documentation must strictly mirror the structural outline, section headings, Mermaid topologies, and table schemas of the English SSOT.
  - Documents must maintain exact line-by-line parity (identical line counts) to enable deterministic drift detection via automated diffs and line count assertions.
- **Workflow Sequence**:
  Always draft, review, and finalize changes in the English SSOT before translating and synchronizing them into the Japanese companion document. Never update the Japanese documentation in isolation.
