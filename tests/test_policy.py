"""Kiểm tra chính sách mặc định và cấu hình an toàn."""

import json
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "compose" / "docker-compose.yml"
POLICY = ROOT / "config" / "policy" / "default-deny.yaml"


class TestDefaultPolicy:
    """Chính sách mặc định DENY với ngoại lệ có lý do."""

    def test_policy_file_exists(self):
        assert POLICY.exists(), "Thiếu config/policy/default-deny.yaml"

    def test_policy_default_is_deny(self):
        with open(POLICY) as f:
            policy = yaml.safe_load(f)
        assert policy["default_action"] == "DENY"

    def test_policy_has_documented_exceptions(self):
        with open(POLICY) as f:
            policy = yaml.safe_load(f)
        exceptions = policy.get("exceptions", [])
        assert len(exceptions) >= 2, "Cần ít nhất 2 ngoại lệ có lý do"
        for exc in exceptions:
            assert "reason" in exc, f"Ngoại lệ thiếu lý do: {exc}"
            assert "from" in exc and "to" in exc

    def test_compose_networks_isolated(self):
        with open(COMPOSE) as f:
            compose = yaml.safe_load(f)
        nets = compose["networks"]
        assert nets["net_app"]["internal"] is True
        assert nets["net_data"]["internal"] is True

    def test_gateway_only_dual_homed_containers(self):
        """Chỉ gateway được nối hai miền — không có dịch vụ khác."""
        with open(COMPOSE) as f:
            compose = yaml.safe_load(f)
        dual = []
        for name, svc in compose["services"].items():
            nets = svc.get("networks", {})
            if isinstance(nets, dict) and len(nets) >= 2:
                dual.append(name)
        assert set(dual) == {"gateway-dmz-app", "gateway-app-data", "probe"}, (
            f"Chỉ gateway được dual-homed, tìm thấy: {dual}"
        )

    def test_no_privileged_containers(self):
        with open(COMPOSE) as f:
            compose = yaml.safe_load(f)
        for name, svc in compose["services"].items():
            if name == "probe":
                continue
            assert svc.get("privileged") is not True, f"{name} không được privileged"

    def test_cap_drop_all_services(self):
        with open(COMPOSE) as f:
            compose = yaml.safe_load(f)
        for name, svc in compose["services"].items():
            if name == "probe":
                continue
            caps = svc.get("cap_drop", [])
            assert "ALL" in caps, f"{name} phải cap_drop ALL"


class TestTopologyFromCompose:
    """Sơ đồ luồng sinh từ compose — không vẽ tay."""

    def test_flow_diagram_generated(self):
        diagram = ROOT / "evidence" / "flow-diagram.mmd"
        if not diagram.exists():
            subprocess.run(["make", "export-evidence"], cwd=ROOT, check=False)
        assert diagram.exists(), "Chạy make export-evidence để sinh sơ đồ"

    def test_compose_config_valid(self):
        result = subprocess.run(
            ["docker", "compose", "-f", str(COMPOSE), "config"],
            capture_output=True, text=True, cwd=ROOT / "compose",
        )
        assert result.returncode == 0, result.stderr
