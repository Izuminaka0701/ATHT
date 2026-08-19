"""Tiện ích dùng chung cho pytest."""

import subprocess


def _run_in_network(container: str, cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Chạy lệnh trong network namespace của container."""
    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "--network", f"container:{container}",
            "alpine:3.20",
        ] + cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def docker_exec(container: str, cmd: list[str], timeout: int = 10) -> tuple[int, str, str]:
    result = subprocess.run(
        ["docker", "exec", container] + cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def tcp_connect_from(container: str, host: str, port: int, timeout: int = 5) -> bool:
    rc, _, _ = _run_in_network(
        container,
        ["sh", "-c", f"nc -z -w {timeout} {host} {port}"],
    )
    return rc == 0


def http_get_from(container: str, url: str) -> tuple[int, str]:
    rc, out, err = _run_in_network(
        container,
        ["wget", "-qO-", "-S", url, "2>&1"],
    )
    status = 0
    for line in (out + err).splitlines():
        if "HTTP/" in line:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    status = int(parts[1])
                except ValueError:
                    pass
    return status, out + err


def get_container_ip(container: str) -> str:
    rc, out, _ = docker_exec(container, ["hostname", "-i"])
    return out.strip().split()[0] if rc == 0 else ""
