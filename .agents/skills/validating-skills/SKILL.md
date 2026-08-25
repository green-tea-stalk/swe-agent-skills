---
name: validating-skills
description: >-
  Use this skill when creating, modifying, or refactoring skills, subagents, or plugins in the swe-agent-skills repository to verify compliance with Agent Skills standards.
---

# Validating Skills and Plugins

This local skill dynamically validates that all skills, subagents, and plugin configurations in this repository adhere to the latest Agent Skills open standards, best practices, and structure requirements by dynamically referring to the official documentation.

## Workflow

1. **Check Validation Cache**:
   Execute the validation cache manager script from the repository root to check if up-to-date validation axes exist:
   ```bash
   python3 .agents/skills/validating-skills/scripts/manage_validation_cache.py
   ```

2. **Update Cache if Required (Exit Code 1)**:
   If the script exits with code 1 (missing or outdated cache), you MUST:
   - Read the official Agent Skills documentation strictly from the following primary sources:
     - Specification: `https://agentskills.io/specification`
     - Best Practices: `https://agentskills.io/skill-creation/best-practices`
     - Optimizing Descriptions: `https://agentskills.io/skill-creation/optimizing-descriptions`
     - Evaluating Skills: `https://agentskills.io/skill-creation/evaluating-skills`
     - Using Scripts: `https://agentskills.io/skill-creation/using-scripts`
   - Extract the current required structure, constraints, and best practices from the documentation.
   - Summarize the extracted validation axes (checklist format) into a markdown file.
   - Save the markdown file precisely to `.agents/skills/validating-skills/.cache/validation_axes.md` (creating the directory if needed).
   - Re-run the script in step 1 to confirm the cache is now valid.

3. **Dynamic Review & Verification Step (Exit Code 0)**:
   If the script exits with code 0, it will output the current `--- VALIDATION AXES ---`.
   - As an AI agent, carefully read the provided validation axes.
   - Review the target skill, subagent, or plugin files in this repository against these axes.
   - If any discrepancies or violations are found, fix the offending files.
   - Report the review results to the user.
