#!/usr/bin/env python3
"""
validate_skills.py - Rule-driven skill validator for swe-agent-skills

Validates that all skills, subagents, and plugins in the repository
adhere to the latest Agent Skills best practices and multi-agent standards.
"""

import sys
import os
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

# Constants
CACHE_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days
CACHE_DIR_NAME = ".cache"
CACHE_FILE_NAME = "validation_rules.json"

# Default schema definition for Agent Skills best practices (2026-08 baseline)
BASELINE_RULES = {
    "version": "2026.08.1",
    "updated_at": "2026-08-24T00:00:00Z",
    "naming": {
        "max_length": 64,
        "pattern": r"^[a-z0-9]+(-[a-z0-9]+)*$",
        "recommended_pattern": r"^[a-z0-9]+ing(-[a-z0-9]+)*$",  # gerund (verb-ing)
        "reserved_words": ["anthropic", "claude", "google", "gemini", "openai"],
        "banned_names": ["utils", "helper", "tools", "scripts", "temp", "test"]
    },
    "frontmatter": {
        "required_fields": ["name", "description"],
        "max_description_length": 1024,
        "third_person_indicators": ["use this skill when", "when", "guides", "provides", "assists", "executes", "performs", "する際に", "を行う"]
    },
    "progressive_disclosure": {
        "max_lines": 500,
        "recommended_subdirs": ["references", "scripts", "resources", "examples", "assets"]
    },
    "context_leak": {
        "forbidden_patterns": [
            r"/Users/[a-zA-Z0-9_-]+",
            r"/home/[a-zA-Z0-9_-]+",
            r"C:\\[Uu]sers\\[a-zA-Z0-9_-]+"
        ]
    },
    "multi_agent_compatibility": {
        "forbidden_env_vars_in_instructions": [r"\$\{CLAUDE_PLUGIN_ROOT\}", r"\$CLAUDE_PLUGIN_ROOT"]
    }
}


def get_cache_path(script_dir: Path) -> Path:
    cache_dir = script_dir.parent / CACHE_DIR_NAME
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / CACHE_FILE_NAME


def fetch_or_load_rules(script_dir: Path) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Loads rules from the local 7-day cache, or initializes the cache with the
    verified specifications. Implements fail-fast behavior.
    """
    cache_path = get_cache_path(script_dir)
    
    # 1. Check if cache exists and is within TTL
    if cache_path.exists():
        try:
            mtime = cache_path.stat().st_mtime
            age = time.time() - mtime
            if age < CACHE_TTL_SECONDS:
                with open(cache_path, "r", encoding="utf-8") as f:
                    rules = json.load(f)
                    return rules, f"Loaded from cache (age: {int(age / 86400)}d, TTL: 7d)"
        except Exception as e:
            # Cache corrupted
            pass

    # 2. In an active networked environment, this would fetch from remote spec endpoints.
    # For standalone repository self-containment, initialize / refresh cache with baseline.
    try:
        rules = BASELINE_RULES.copy()
        rules["cached_at"] = time.time()
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)
        return rules, "Cache initialized / refreshed with latest specifications"
    except Exception as e:
        return None, f"Failed to acquire or initialize rules: {e}"


def parse_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """Extract YAML frontmatter and body from a Markdown file."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter_raw = parts[1]
    body = parts[2]

    frontmatter = {}
    current_key = None
    multiline_val = []

    for line in frontmatter_raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        
        # Key-value line (e.g. name: foo or description: >-)
        if ":" in line and not line.startswith(" ") and not line.startswith("\t"):
            if current_key and multiline_val:
                frontmatter[current_key] = " ".join(multiline_val).strip()
                multiline_val = []
            
            key, val = line.split(":", 1)
            current_key = key.strip()
            val_clean = val.strip().strip("\"'")
            if val_clean in [">-", ">", "|", "|-"]:
                multiline_val = []
            elif val_clean:
                frontmatter[current_key] = val_clean
        elif current_key:
            multiline_val.append(line.strip().strip("\"'"))

    if current_key and multiline_val:
        frontmatter[current_key] = " ".join(multiline_val).strip()

    return frontmatter, body


def validate_skill_file(skill_path: Path, rules: Dict[str, Any]) -> List[str]:
    """Validate a single SKILL.md against the rules."""
    errors = []
    
    try:
        with open(skill_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"Could not read file: {e}"]

    parent_dir_name = skill_path.parent.name
    total_lines = len(content.splitlines())
    frontmatter, body = parse_frontmatter(content)

    # 1. Frontmatter presence
    if not frontmatter:
        errors.append("Missing YAML Frontmatter (must start and close with '---')")
        return errors

    # 2. Required fields
    for field in rules["frontmatter"]["required_fields"]:
        if field not in frontmatter or not frontmatter[field]:
            errors.append(f"Missing required Frontmatter field: '{field}'")

    name = frontmatter.get("name", "")
    description = frontmatter.get("description", "")

    # 3. Naming convention
    naming_rules = rules["naming"]
    if name:
        if name != parent_dir_name:
            errors.append(f"Frontmatter 'name' ('{name}') must exactly match parent directory name ('{parent_dir_name}')")
        
        if len(name) > naming_rules["max_length"]:
            errors.append(f"Skill name exceeds max length ({len(name)} > {naming_rules['max_length']})")
        
        if not re.match(naming_rules["pattern"], name):
            errors.append(f"Skill name '{name}' must be kebab-case (lowercase alphanumeric and single hyphens only)")
        
        for reserved in naming_rules["reserved_words"]:
            if reserved in name:
                errors.append(f"Skill name contains reserved word '{reserved}'")
        
        if name in naming_rules["banned_names"]:
            errors.append(f"Skill name '{name}' is too generic or banned")

    # 4. Description validation
    if description:
        if len(description) > rules["frontmatter"]["max_description_length"]:
            errors.append(f"Description length ({len(description)}) exceeds max limit ({rules['frontmatter']['max_description_length']})")
        
        desc_lower = description.lower()
        has_indicator = any(ind in desc_lower for ind in rules["frontmatter"]["third_person_indicators"])
        if not has_indicator:
            errors.append("Description should use third-person triggers (e.g., 'Use this skill when...', 'When...', '〜する際に使用する')")

    # 5. Progressive Disclosure (Line count)
    max_lines = rules["progressive_disclosure"]["max_lines"]
    if total_lines > max_lines:
        errors.append(f"SKILL.md exceeds recommended line limit ({total_lines} > {max_lines} lines). Split large content into references/")

    # 6. Context Leak Check
    for pattern in rules["context_leak"]["forbidden_patterns"]:
        if re.search(pattern, content):
            errors.append(f"Context leak detected: Local absolute path matching '{pattern}' found in SKILL.md")

    # 7. Multi-Agent Portability (Avoid hardcoding agent-specific env vars in instructions)
    for env_var in rules["multi_agent_compatibility"]["forbidden_env_vars_in_instructions"]:
        if re.search(env_var, content):
            errors.append(f"Portability issue: Agent-specific environment variable '{env_var}' found in instructions. Use standard relative paths instead.")

    # 8. Validation Steps check (Encouraged for SWE skills)
    body_lower = body.lower()
    validation_keywords = ["validation", "verification", "verify", "test", "check", "検証", "テスト", "確認"]
    if not any(kw in body_lower for kw in validation_keywords):
        errors.append("Validation step missing: SWE skills must include instructions on how to verify results (test commands, logs, checks)")

    return errors


def validate_agent_file(agent_path: Path, rules: Dict[str, Any]) -> List[str]:
    """Validate a subagent Markdown file (agents/*.md)."""
    errors = []
    try:
        with open(agent_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"Could not read file: {e}"]

    # Context leak check
    for pattern in rules["context_leak"]["forbidden_patterns"]:
        if re.search(pattern, content):
            errors.append(f"Context leak detected: Local absolute path matching '{pattern}' found in {agent_path.name}")

    # Portability check
    for env_var in rules["multi_agent_compatibility"]["forbidden_env_vars_in_instructions"]:
        if re.search(env_var, content):
            errors.append(f"Portability issue: Agent-specific env var '{env_var}' found in {agent_path.name}")

    return errors


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parents[3]  # .agents/skills/validating-skills/scripts -> repo_root

    print("=" * 60)
    print("swe-agent-skills : Skill & Plugin Validator")
    print("=" * 60)

    # 1. Fetch / load rules with cache & fail-fast
    rules, status_msg = fetch_or_load_rules(script_dir)
    if not rules:
        print(f"\n[FAIL-FAST ERROR] {status_msg}")
        print("Cannot perform validation without verified rules. Aborting.")
        return 1

    print(f"[*] Rules Status: {status_msg} (Version: {rules.get('version', 'unknown')})")
    print(f"[*] Repository Root: {repo_root}\n")

    # 2. Discover all SKILL.md and agent files
    skill_files = list(repo_root.glob("**/SKILL.md"))
    agent_files = list(repo_root.glob("**/agents/*.md"))

    # Exclude .git and scratch
    skill_files = [f for f in skill_files if ".git" not in str(f) and "scratch" not in str(f)]
    agent_files = [f for f in agent_files if ".git" not in str(f) and "scratch" not in str(f)]

    total_inspected = len(skill_files) + len(agent_files)
    if total_inspected == 0:
        print("[!] No skills or subagents found to validate.")
        return 0

    has_errors = False

    # 3. Validate Skills
    print(f"--- Validating Skills ({len(skill_files)} files) ---")
    for sf in skill_files:
        rel_path = sf.relative_to(repo_root)
        errors = validate_skill_file(sf, rules)
        if errors:
            has_errors = True
            print(f"[FAIL] {rel_path}")
            for err in errors:
                print(f"       - {err}")
        else:
            print(f"[PASS] {rel_path}")

    # 4. Validate Agents
    if agent_files:
        print(f"\n--- Validating Subagents ({len(agent_files)} files) ---")
        for af in agent_files:
            rel_path = af.relative_to(repo_root)
            errors = validate_agent_file(af, rules)
            if errors:
                has_errors = True
                print(f"[FAIL] {rel_path}")
                for err in errors:
                    print(f"       - {err}")
            else:
                print(f"[PASS] {rel_path}")

    print("\n" + "=" * 60)
    if has_errors:
        print("[RESULT] VALIDATION FAILED. Please fix the issues above.")
        return 1
    else:
        print(f"[RESULT] ALL {total_inspected} ITEMS PASSED VALIDATION.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
