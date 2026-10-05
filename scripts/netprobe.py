"""Probe TCP dùng chung cho attack.py / defend.py.

Dùng `nc` nếu container có (nginx/alpine/postgres), không thì dùng python3
(app-api build từ python:3.12-slim, không có nc).
Mã trả về 127 = container không có công cụ nào để probe (KHÔNG phải DENY).
"""

import subprocess

NO_TOOL = 127

_PROBE_SH = (
    'if command -v nc >/dev/null 2>&1; then nc -z -w 3 "$1" "$2"; '
    'elif command -v python3 >/dev/null 2>&1; then '
    'python3 -c "import socket,sys; '
    'socket.create_connection((sys.argv[1], int(sys.argv[2])), 3).close()" "$1" "$2"; '
    f"else exit {NO_TOOL}; fi"
)


def is_running(container: str) -> bool:
    r = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container],
        capture_output=True, text=True,
    )
    return r.stdout.strip() == "true"


def tcp_probe(container: str, host: str, port: int) -> int:
    """0 = kết nối được, 1 = không kết nối được, 127 = thiếu công cụ."""
    r = subprocess.run(
        ["docker", "exec", container, "sh", "-c", _PROBE_SH, "probe", host, str(port)],
        capture_output=True, text=True,
    )
    if r.returncode == NO_TOOL:
        return NO_TOOL
    return 0 if r.returncode == 0 else 1