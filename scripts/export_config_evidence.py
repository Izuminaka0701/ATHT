#!/usr/bin/env python3
"""Xuất bằng chứng cấu hình trước/sau hardening."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
BEFORE = EVIDENCE / "config-before"
AFTER = EVIDENCE / "config-after"

# Cấu hình mặc định KHÔNG AN TOÀN (trước hardening)
INSECURE = {
    "postgresql.conf": """\
listen_addresses = '*'
port = 5432
""",
    "compose-ports": "ports:\n  - '8080:8080'  # bind 0.0.0.0 — không an toàn",
    "network": "# Tất cả container trên một mạng bridge duy nhất",
}

# Cấu hình sau hardening (copy từ config/)
SECURE_FILES = [
    ("postgresql.conf", ROOT / "config" / "data-db" / "postgresql.conf"),
    ("pg_hba.conf", ROOT / "config" / "data-db" / "pg_hba.conf"),
    ("nginx-dmz.conf", ROOT / "config" / "dmz-web" / "nginx.conf"),
    ("gateway-dmz-app.conf", ROOT / "config" / "gateway-dmz-app" / "nginx.conf"),
    ("policy.yaml", ROOT / "config" / "policy" / "default-deny.yaml"),
}


def main():
    BEFORE.mkdir(parents=True, exist_ok=True)
    AFTER.mkdir(parents=True, exist_ok=True)

    for name, content in INSECURE.items():
        (BEFORE / name).write_text(content, encoding="utf-8")

    for name, src in SECURE_FILES:
        if src.exists():
            (AFTER / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    diff_lines = ["# Config hardening — trước vs sau", ""]
    for name, src in SECURE_FILES:
        before_file = BEFORE / name
        if before_file.exists() or name in INSECURE:
            diff_lines.append(f"## {name}")
            diff_lines.append("TRƯỚC: listen_addresses='*', single network, no gateway")
            diff_lines.append(f"SAU: xem evidence/config-after/{name}")
            diff_lines.append("")

    (EVIDENCE / "config-hardening-summary.md").write_text(
        "\n".join(diff_lines), encoding="utf-8"
    )
    print(f"Generated config before/after in {EVIDENCE}")


if __name__ == "__main__":
    main()
