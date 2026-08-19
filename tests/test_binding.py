"""Kiểm tra binding — dịch vụ không lắng nghe mọi giao diện."""

import subprocess

import pytest
from helpers import docker_exec, get_container_ip


def _proc_net_listen_ports(container: str) -> list[tuple[str, int]]:
    """Parse /proc/net/tcp để lấy (address, port) đang LISTEN."""
    rc, out, _ = docker_exec(container, ["cat", "/proc/net/tcp"])
    if rc != 0:
        return []
    listeners = []
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 2:
            continue
        local = parts[1]
        state = parts[3]
        if state != "0A":  # TCP_LISTEN
            continue
        addr_hex, port_hex = local.split(":")
        port = int(port_hex, 16)
        # addr_hex is little-endian hex IP
        octets = [str(int(addr_hex[i:i+2], 16)) for i in range(6, -1, -2)]
        addr = ".".join(octets)
        listeners.append((addr, port))
    return listeners


class TestServiceBinding:
    """[ĐE DỌA: bind 0.0.0.0] Dịch vụ chỉ lắng nghe trên IP miền của mình."""

    def test_postgres_not_listening_on_all_interfaces(self):
        """data-db: PostgreSQL KHÔNG bind 0.0.0.0 — chỉ IP miền DATA."""
        listeners = _proc_net_listen_ports("data-db")
        pg_listeners = [(a, p) for a, p in listeners if p == 5432]
        assert pg_listeners, "PostgreSQL phải đang lắng nghe cổng 5432"
        addrs = [a for a, _ in pg_listeners]
        assert "0.0.0.0" not in addrs, f"PostgreSQL bind 0.0.0.0: {pg_listeners}"
        data_ip = get_container_ip("data-db")
        assert data_ip in addrs, f"PostgreSQL phải bind {data_ip}, thấy: {addrs}"

    def test_app_api_not_listening_on_all_interfaces(self):
        """app-api: Gunicorn KHÔNG bind 0.0.0.0."""
        listeners = _proc_net_listen_ports("app-api")
        api_listeners = [(a, p) for a, p in listeners if p == 5000]
        assert api_listeners, "app-api phải đang lắng nghe cổng 5000"
        addrs = [a for a, _ in api_listeners]
        assert "0.0.0.0" not in addrs, f"app-api bind 0.0.0.0: {api_listeners}"

    def test_dmz_web_port_not_exposed_on_all_host_interfaces(self):
        """dmz-web: cổng host chỉ map 127.0.0.1:8080."""
        result = subprocess.run(
            ["docker", "port", "dmz-web", "8080"],
            capture_output=True, text=True,
        )
        port_mapping = result.stdout.strip()
        assert "127.0.0.1" in port_mapping, (
            f"Host mapping phải giới hạn localhost: {port_mapping}"
        )

    def test_postgres_hba_default_deny(self):
        """pg_hba.conf: mặc đnh từ chối — chỉ cho phép appuser từ mạng nội bộ."""
        rc, out, _ = docker_exec("data-db", ["cat", "/etc/postgresql/pg_hba.conf"])
        assert rc == 0
        lines = [l.strip() for l in out.splitlines() if l.strip() and not l.startswith("#")]
        host_rules = [l for l in lines if l.startswith("host")]
        assert len(host_rules) >= 1
        for rule in host_rules:
            fields = rule.split()
            assert fields[2] == "appuser", f"Chỉ cho phép appuser: {rule}"
