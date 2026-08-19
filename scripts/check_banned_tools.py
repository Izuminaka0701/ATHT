#!/usr/bin/env python3
"""CI gate: từ chối công cụ trong danh mục cấm."""

import sys
from pathlib import Path

BANNED = [
    "metasploit",
    "msfconsole",
    "sqlmap",
    "exploit-db",
    "searchsploit",
]

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules"}


def main():
    violations = []
    for path in ROOT.rglob("*"):
        if any(s in path.parts for s in SKIP_DIRS):
            continue
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        for banned in BANNED:
            if banned in text and path.name != "check_banned_tools.py":
                violations.append(f"{path.relative_to(ROOT)}: contains '{banned}'")

    if violations:
        print("BANNED TOOLS DETECTED:")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)
    print("No banned tools found.")
    sys.exit(0)


if __name__ == "__main__":
    main()
