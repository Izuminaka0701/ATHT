#!/usr/bin/env python3
"""Pull ảnh Docker và ghim digest manifest vào compose/docker-compose.yml."""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "compose" / "docker-compose.yml"

IMAGES = [
    "nginx:1.27-alpine",
    "postgres:16-alpine",
    "alpine:3.20",
]


def get_manifest_digest(image: str) -> str:
    subprocess.run(["docker", "pull", image], check=True, capture_output=True)
    result = subprocess.run(
        ["docker", "inspect", "--format", "{{index .RepoDigests 0}}", image],
        capture_output=True,
        text=True,
        check=True,
    )
    ref = result.stdout.strip()
    if "@sha256:" not in ref:
        raise RuntimeError(f"Không lấy được digest cho {image}: {ref!r}")
    return ref.split("@", 1)[1]


def pin_compose(content: str, image: str, digest: str) -> str:
    repo = image.split(":")[0]
    tag = image.split(":")[1] if ":" in image else "latest"
    pattern = rf"({re.escape(repo)}:{re.escape(tag)})@sha256:[a-f0-9]{{64}}"
    replacement = rf"\1@{digest}"
    new_content, count = re.subn(pattern, replacement, content)
    if count == 0:
        # probe dùng tag không digest
        bare = rf"image: {re.escape(repo)}:{re.escape(tag)}\s*$"
        new_content, count = re.subn(
            bare,
            f"image: {image}@{digest}",
            new_content,
            flags=re.MULTILINE,
        )
    if count == 0:
        print(f"  WARN: không tìm thấy chỗ ghim cho {image}", file=sys.stderr)
    else:
        print(f"  OK {image}@{digest} ({count} chỗ)")
    return new_content


def main() -> int:
    if not COMPOSE.exists():
        print(f"Không tìm thấy {COMPOSE}", file=sys.stderr)
        return 1

    content = COMPOSE.read_text(encoding="utf-8")
    for image in IMAGES:
        print(f"Pull {image}...")
        digest = get_manifest_digest(image)
        content = pin_compose(content, image, digest)

    COMPOSE.write_text(content, encoding="utf-8")
    print(f"Đã cập nhật {COMPOSE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
