#!/usr/bin/env python3
"""Xác minh phòng thủ sau khi hardening."""

import subprocess
import sys


def check(label: str, container: str, host: str, port: int, should_connect: bool):
    cmd = f"nc -z -w 3 {host} {port} 2>/dev/null"
    result = subprocess.run(
        ["docker", "exec", container, "sh", "-c", cmd],
        capture_output=True,
    )
    connected = result.returncode == 0
    ok = connected == should_connect
    status = "OK" if ok else "FAIL"
    expect = "ALLOW" if should_connect else "DENY"
    print(f"  [{status}] {label}: {container} → {host}:{port} (expect {expect})")
    return ok


def main():
    print("=== Xác minh phòng thủ ===")
    checks = [
        ("Luồng hợp lệ DMZ→gateway", "dmz-web", "gateway-dmz-app", 8000, True),
        ("Luồng hợp lệ APP→gateway-data", "app-api", "gateway-app-data", 5432, True),
        ("Chặn DMZ→DB trực tiếp", "dmz-web", "data-db", 5432, False),
        ("Chặn DMZ→APP trực tiếp", "dmz-web", "app-api", 5000, False),
        ("Chặn APP→DB trực tiếp", "app-api", "data-db", 5432, False),
    ]
    all_ok = all(check(*c) for c in checks)
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
