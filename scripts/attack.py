#!/usr/bin/env python3
"""Kịch bản tấn công mô phỏng (trong lab compose) — không khai thác thật."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "compose" / "docker-compose.yml"


def run_attack(name: str, container: str, cmd: str) -> bool:
    print(f"\n[ATTACK] {name}")
    print(f"  $ docker exec {container} sh -c '{cmd}'")
    result = subprocess.run(
        ["docker", "exec", container, "sh", "-c", cmd],
        capture_output=True, text=True,
    )
    success = result.returncode == 0
    print(f"  Exit: {result.returncode} ({'THÀNH CÔNG — LỖ HỔNG!' if success else 'THẤT BẠI — phòng thủ OK'})")
    if result.stdout:
        print(f"  stdout: {result.stdout[:200]}")
    if result.stderr:
        print(f"  stderr: {result.stderr[:200]}")
    return success


def main():
    print("=== Kịch bản tấn công Chủ đề G (lab nội bộ) ===")
    attacks = [
        ("DMZ bị chiếm → truy cập trực tiếp DB",
         "dmz-web", "nc -z -w 3 data-db 5432"),
        ("Đi tắt gateway → DMZ tới app-api trực tiếp",
         "dmz-web", "nc -z -w 3 app-api 5000"),
        ("APP đi tắt → kết nối DB trực tiếp",
         "app-api", "nc -z -w 3 data-db 5432"),
        ("Leo thang ngược DATA → DMZ",
         "data-db", "nc -z -w 3 dmz-web 8080"),
    ]

    vulnerabilities = []
    for name, container, cmd in attacks:
        if run_attack(name, container, cmd):
            vulnerabilities.append(name)

    print("\n=== Kết quả ===")
    if vulnerabilities:
        print(f"PHÁT HIỆN {len(vulnerabilities)} lỗ hổng — chạy make defend")
        sys.exit(1)
    else:
        print("Tất cả tấn công bị chặn — phòng thủ hoạt động đúng.")
        sys.exit(0)


if __name__ == "__main__":
    main()
