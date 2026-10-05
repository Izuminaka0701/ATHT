#!/usr/bin/env python3
"""Kịch bản tấn công mô phỏng (trong lab compose) — không khai thác thật."""

import sys

from netprobe import NO_TOOL, is_running, tcp_probe


def run_attack(name: str, container: str, host: str, port: int) -> bool:
    """True = tấn công THÀNH CÔNG (tức là có lỗ hổng)."""
    print(f"\n[ATTACK] {name}")
    print(f"  {container} → {host}:{port}")
    if not is_running(container):
        print(f"  Bỏ qua: container '{container}' không chạy (KHÔNG tính là phòng thủ OK)")
        raise SystemExit(2)
    rc = tcp_probe(container, host, port)
    if rc == NO_TOOL:
        print(f"  Lỗi: '{container}' không có nc lẫn python3")
        raise SystemExit(2)
    success = rc == 0
    print(f"  Kết nối: {'THÀNH CÔNG — LỖ HỔNG!' if success else 'THẤT BẠI — phòng thủ OK'}")
    return success


def main():
    print("=== Kịch bản tấn công Chủ đề G (lab nội bộ) ===")
    attacks = [
        ("DMZ bị chiếm → truy cập trực tiếp DB", "dmz-web", "data-db", 5432),
        ("Đi tắt gateway → DMZ tới app-api trực tiếp", "dmz-web", "app-api", 5000),
        ("APP đi tắt → kết nối DB trực tiếp", "app-api", "data-db", 5432),
        ("Leo thang ngược DATA → DMZ", "data-db", "dmz-web", 8080),
    ]
    vulnerabilities = [a[0] for a in attacks if run_attack(*a)]

    print("\n=== Kết quả ===")
    if vulnerabilities:
        print(f"PHÁT HIỆN {len(vulnerabilities)} lỗ hổng — chạy make defend")
        sys.exit(1)
    print("Tất cả tấn công bị chặn — phòng thủ hoạt động đúng.")
    sys.exit(0)


if __name__ == "__main__":
    main()