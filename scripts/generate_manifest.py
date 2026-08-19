#!/usr/bin/env python3
"""Tạo MANIFEST.txt với sha256 cho mọi file trong evidence/."""

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
MANIFEST = EVIDENCE / "MANIFEST.txt"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    lines = []
    for f in sorted(EVIDENCE.rglob("*")):
        if f.is_file() and f.name != "MANIFEST.txt":
            digest = sha256_file(f)
            rel = f.relative_to(EVIDENCE)
            lines.append(f"{digest}  {rel}")

    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated: {MANIFEST} ({len(lines)} files)")


if __name__ == "__main__":
    main()
