# swe-agent-skills

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/green-tea-stalk/swe-agent-skills)](https://github.com/green-tea-stalk/swe-agent-skills/releases)
[![Release Please](https://github.com/green-tea-stalk/swe-agent-skills/actions/workflows/release-please.yml/badge.svg)](https://github.com/green-tea-stalk/swe-agent-skills/actions/workflows/release-please.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
> Reusable software engineering skills, workflows, and subagents for modern AI coding agents.

[日本語 (Japanese)](./README.ja.md)

---

## Overview

`swe-agent-skills` provides reusable software engineering (SWE) practices, development workflows, and specialized subagents packaged as plugins for Google Antigravity, Claude Code, and Codex CLI.

### Supported AI Coding Agents


Directly supported as native plugins in the following AI coding assistants:

- **Google Antigravity (AGY)**: Native plugin discovery via `plugins/<name>/plugin.json`.
- **Claude Code**: Native plugin discovery via `.claude-plugin/plugin.json` and Plugin Marketplace.
- **Codex CLI**: Native plugin discovery via `.codex-plugin/plugin.json` and plugin management via `/plugins`.

### Prerequisites

- **Git**
- **GitHub CLI (`gh`)**
- **Python 3** (Standard library only; no external `pip` packages required)

---

## Available Plugins

- **git-workflow**: Essential Git workflow automation and best practices.
  - [committing-changes](./plugins/git-workflow/skills/committing-changes/README.md)
  - [drafting-pull-request](./plugins/git-workflow/skills/drafting-pull-request/README.md)

---

## Quickstart (Installation & Usage)

Because the plugins provided in this repository are project-agnostic SWE practices, they are intended to be **installed at the user scope (globally across your machine)** to be seamlessly available across all your projects.


Follow the instructions below for your agent environment:

### 1. Google Antigravity (AGY)
Clone the repository locally and register it in your global configuration:

```bash
# 1. Clone into your local directory
git clone https://github.com/green-tea-stalk/swe-agent-skills.git ~/git/swe-agent-skills
```

**Configuration (Recommended)**: Register the path in `~/.gemini/config/plugins.json`:
```json
{
  "entries": [
    { "path": "~/git/swe-agent-skills/plugins" }
  ]
}
```
*(Or symlink plugins directly: `ln -s ~/git/swe-agent-skills/plugins/<plugin-name> ~/.gemini/config/plugins/<plugin-name>`)*

### 2. Claude Code

Add this repository as a marketplace and install the desired plugin globally:
```bash
# Add marketplace
/plugin marketplace add https://github.com/green-tea-stalk/swe-agent-skills

# Install a plugin (e.g., general-swe)
/plugin install <plugin-name>@swe-agent-skills
```

### 3. Codex CLI
Add plugins directly within the Codex CLI terminal (enabled globally):
```bash
# Add plugin
/plugins add https://github.com/green-tea-stalk/swe-agent-skills
```

---


## Contributing & Development Philosophy

This repository is designed with an **Agent-First** philosophy (built for and maintained by AI coding agents). Rather than manual authoring, contributors are encouraged to use AI coding agents to create and refine plugins and skills.

### Single Source of Truth for Agents
All specifications for plugin architecture, authoring standards, environment isolation principles, and operational rules are unified in:

👉 **[AGENTS.md](./AGENTS.md)**

### Autonomous Rule Compliance & Validation
When an AI agent modifies skills or plugins in this repository, workspace rules ([`.agents/rules/`](./.agents/rules/)) automatically guide the agent to trigger the self-validation skill ([`.agents/skills/validating-skills`](./.agents/skills/validating-skills/)), ensuring continuous compliance with open standards.
