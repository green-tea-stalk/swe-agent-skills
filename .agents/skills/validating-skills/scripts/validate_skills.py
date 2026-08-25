#!/usr/bin/env python3
"""
validate_skills.py - Validation Cache Manager for swe-agent-skills

This script manages the cache of validation axes.
It does NOT perform static validation itself. Instead, it checks if the cached
validation axes (extracted dynamically from the official Agent Skills documentation)
are valid and up-to-date (within 7 days).
"""

import sys
import time
from pathlib import Path

CACHE_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days
CACHE_DIR_NAME = ".cache"
CACHE_FILE_NAME = "validation_axes.md"

def main() -> int:
    script_dir = Path(__file__).resolve().parent
    cache_dir = script_dir.parent / CACHE_DIR_NAME
    cache_path = cache_dir / CACHE_FILE_NAME

    cache_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("swe-agent-skills : Validation Cache Manager")
    print("=" * 60)

    if cache_path.exists():
        try:
            mtime = cache_path.stat().st_mtime
            age = time.time() - mtime
            if age < CACHE_TTL_SECONDS:
                print(f"[*] Cache is valid (age: {int(age / 86400)}d, TTL: 7d).")
                print("--- VALIDATION AXES ---")
                with open(cache_path, "r", encoding="utf-8") as f:
                    print(f.read())
                print("-----------------------")
                print("[RESULT] Please review the target skill files based on the above validation axes.")
                return 0
            else:
                print(f"[!] Cache has expired (age: {int(age / 86400)}d, TTL: 7d).")
        except Exception as e:
            print(f"[!] Failed to read cache: {e}")
    else:
        print("[!] No cached validation axes found.")

    print("\n[ACTION REQUIRED]")
    print("The validation cache is missing or outdated.")
    print("As an AI agent, please perform the following steps:")
    print("1. Read the official Agent Skills documentation to extract the latest structure and best practice requirements.")
    print(f"2. Write the extracted requirements in Markdown format to: {cache_path.resolve()}")
    print("3. Re-run this script.")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
