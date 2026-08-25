#!/usr/bin/env python3
"""
manage_validation_cache.py - Validation Cache Manager for swe-agent-skills

This script manages the cache of validation axes.
If the cache is missing or expired, it automatically fetches the latest primary
documentation from official URLs and saves it locally for the AI to interpret.
"""

import sys
import time
import urllib.request
from pathlib import Path

CACHE_TTL_SECONDS = 7 * 24 * 60 * 60  # 7 days
CACHE_DIR_NAME = ".cache"
CACHE_FILE_NAME = "validation_axes.md"
RAW_DOCS_FILE_NAME = "raw_docs.md"

PRIMARY_URLS = [
    "https://agentskills.io/specification.md",
    "https://agentskills.io/skill-creation/best-practices.md",
    "https://agentskills.io/skill-creation/optimizing-descriptions.md",
    "https://agentskills.io/skill-creation/evaluating-skills.md",
    "https://agentskills.io/skill-creation/using-scripts.md"
]

def fetch_docs(cache_dir: Path) -> Path:
    """Fetch primary documentation and save it to the cache directory."""
    raw_docs_path = cache_dir / RAW_DOCS_FILE_NAME
    print("[*] Fetching latest primary documentation...")
    content_blocks = []
    
    for url in PRIMARY_URLS:
        print(f"  -> Fetching {url}")
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                markdown_content = response.read().decode('utf-8')
                content_blocks.append(f"<!-- SOURCE: {url} -->\n{markdown_content}\n")
        except urllib.error.URLError as e:
            print(f"  [!] Failed to fetch {url}: {e}")
            content_blocks.append(f"<!-- SOURCE: {url} (FAILED: {e}) -->\n")
            
    with open(raw_docs_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content_blocks))
        
    return raw_docs_path

def main() -> int:
    """Execute the validation cache manager."""
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
        except OSError as e:
            print(f"[!] Failed to read cache: {e}")
    else:
        print("[!] No cached validation axes found.")

    print("\n[ACTION REQUIRED]")
    raw_docs_path = fetch_docs(cache_dir)
    
    print("\nThe validation cache is missing or outdated.")
    print("As an AI agent, please perform the following steps:")
    print(f"1. Read the fetched raw documentation at: {raw_docs_path.resolve()}")
    print("2. Interpret the documentation to extract the latest structure, constraints, and best practices.")
    print(f"3. Write the extracted validation axes in Markdown format to: {cache_path.resolve()}")
    print("4. Re-run this script.")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())

