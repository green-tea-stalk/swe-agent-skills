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
- **Executable Single Source of Truth**: Active authoring standards (naming patterns, Frontmatter schemas, line limits, relative path requirements, portability checks, validation step checks) are maintained directly within the validator script ([`validate_skills.py`](.agents/skills/validating-skills/scripts/validate_skills.py)) with dynamic caching and spec updates.
- **Enforcement**: Whenever a skill, agent, or plugin is created or modified, you must execute the validator and ensure all items pass with exit code `0`. Refer to the validator output for actionable compliance errors and remediation steps.

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
- **Tooling**: Python 3 standard library for local validator script.
