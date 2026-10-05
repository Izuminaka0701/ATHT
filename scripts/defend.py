#!/usr/bin/env python3
"""Xác minh phòng thủ sau khi hardening."""

import sys
import time

from netprobe import NO_TOOL, is_running, tcp_probe

RETRY_SECONDS = 30  # chỉ áp dụng cho luồng hợp lệ (ALLOW), chờ dịch vụ khởi động


def check(label: str, container: str, host: str, port: int, should_connect: bool) -> bool:
    expect = "ALLOW" if should_connect else "DENY"
    head = f"{label}: {container} → {host}:{port} (expect {expect})"

    # Container chết thì KHÔNG được coi là "DENY thành công"
    if not is_running(container):
        print(f"  [FAIL] {head}\n         container '{container}' không chạy — "
              f"xem: docker logs {container}")
        return False

    deadline = time.time() + (RETRY_SECONDS if should_connect else 0)
    while True:
        rc = tcp_probe(container, host, port)
        if rc == NO_TOOL:
            print(f"  [FAIL] {head}\n         '{container}' không có nc lẫn python3")
            return False
        connected = rc == 0
        if connected == should_connect or time.time() >= deadline:
            break
        time.sleep(2)

    ok = connected == should_connect
    print(f"  [{'OK' if ok else 'FAIL'}] {head}")
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
    results = [check(*c) for c in checks]
    print(f"\nKết quả: {sum(results)}/{len(results)} ca đạt")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()