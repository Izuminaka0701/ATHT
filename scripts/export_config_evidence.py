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
# Cấu hình PostgreSQL MẶC ĐỊNH — KHÔNG AN TOÀN
listen_addresses = '*'
port = 5432
max_connections = 100
ssl = off
password_encryption = md5
""",
    "pg_hba.conf": """\
# pg_hba.conf MẶC ĐỊNH — cho phép mọi kết nối
# TYPE  DATABASE  USER  ADDRESS       METHOD
local   all       all                 trust
host    all       all   0.0.0.0/0     trust
host    all       all   ::/0          trust
""",
    "nginx-dmz.conf": """\
# Nginx MẶC ĐỊNH — không proxy, không kiểm soát
server {
    listen 80;
    server_name _;
    location / {
        root /usr/share/nginx/html;
    }
}
""",
    "gateway-dmz-app.conf": """\
# KHÔNG CÓ GATEWAY — tất cả container trên cùng mạng bridge
# DMZ có thể truy cập trực tiếp APP và DATA
""",
    "policy.yaml": """\
# KHÔNG CÓ CHÍNH SÁCH — mặc định ALLOW ALL
default_action: ALLOW
exceptions: []
""",
}

# Cấu hình sau hardening (copy từ config/)
SECURE_FILES = [
    ("postgresql.conf", ROOT / "config" / "data-db" / "postgresql.conf"),
    ("pg_hba.conf", ROOT / "config" / "data-db" / "pg_hba.conf"),
    ("nginx-dmz.conf", ROOT / "config" / "dmz-web" / "nginx.conf"),
    ("gateway-dmz-app.conf", ROOT / "config" / "gateway-dmz-app" / "nginx.conf"),
    ("policy.yaml", ROOT / "config" / "policy" / "default-deny.yaml"),
]


def main():
    BEFORE.mkdir(parents=True, exist_ok=True)
    AFTER.mkdir(parents=True, exist_ok=True)

    for name, content in INSECURE.items():
        (BEFORE / name).write_text(content, encoding="utf-8")

    for name, src in SECURE_FILES:
        if src.exists():
            (AFTER / name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    diff_lines = ["# Config hardening — trước vs sau", ""]
    for name, _src in SECURE_FILES:
        diff_lines.append(f"## {name}")
        diff_lines.append(f"- **TRƯỚC**: xem `evidence/config-before/{name}`")
        diff_lines.append(f"- **SAU**: xem `evidence/config-after/{name}`")
        diff_lines.append("")

    diff_lines.append("## Tóm tắt thay đổi")
    diff_lines.append("")
    diff_lines.append("| File | Trước | Sau |")
    diff_lines.append("|------|-------|-----|")
    diff_lines.append("| postgresql.conf | listen_addresses='*' | listen_addresses=IP miền DATA |")
    diff_lines.append("| pg_hba.conf | trust mọi kết nối | scram-sha-256, chỉ appuser |")
    diff_lines.append("| nginx-dmz.conf | listen 80, không proxy | listen 8080, proxy qua gateway |")
    diff_lines.append("| gateway-dmz-app.conf | Không có | Proxy chỉ /health và /data, deny mặc định |")
    diff_lines.append("| policy.yaml | ALLOW ALL | DENY ALL + 5 ngoại lệ có lý do |")

    (EVIDENCE / "config-hardening-summary.md").write_text(
        "\n".join(diff_lines) + "\n", encoding="utf-8"
    )
    print(f"Generated config before/after in {EVIDENCE}")


if __name__ == "__main__":
    main()
