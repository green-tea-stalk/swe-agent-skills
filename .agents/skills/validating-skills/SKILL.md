---
name: validating-skills
description: >-
  Use this skill when creating, modifying, or refactoring skills, subagents, or plugins in the swe-agent-skills repository to verify compliance with Agent Skills standards.
---

# Validating Skills and Plugins

This local skill validates that all skills, subagents, and plugin configurations in this repository adhere to the latest Agent Skills open standards, best practices, and multi-agent portability rules.

## Workflow

1. **Run the Validation Script**:
   Execute the rule-driven validation script from the repository root:
   ```bash
   python3 .agents/skills/validating-skills/scripts/validate_skills.py
   ```

2. **Inspect Validation Output**:
   - **Frontmatter & Naming**: Confirms `name` matches parent directory, follows `kebab-case` (gerund preferred), and `description` is in third-person without reserved words.
   - **Progressive Disclosure**: Verifies line count stays within recommended limits (< 500 lines) and complex reference material is moved to `references/`.
   - **Multi-Agent Portability**: Ensures standard relative paths are used instead of tool-specific environment variables or hardcoded local paths.
   - **Validation Steps**: Ensures procedural skills include verification instructions.

3. **Validation / Verification Step**:

   - If any errors are reported, fix the offending files and rerun the validation script until `[RESULT] ALL ITEMS PASSED VALIDATION` is displayed with exit code 0.
