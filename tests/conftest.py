"""Fixtures pytest — kiểm tra stack đang chạy trước khi test."""

import subprocess
import sys
from pathlib import Path

import pytest

# Đảm bảo thư mục tests/ nằm trong sys.path để import helpers hoạt động
sys.path.insert(0, str(Path(__file__).resolve().parent))


def _container_running(name: str) -> bool:
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", name],
        capture_output=True, text=True,
    )
    return result.stdout.strip() == "true"


@pytest.fixture(scope="session", autouse=True)
def require_stack():
    required = ["dmz-web", "gateway-dmz-app", "app-api", "gateway-app-data", "data-db"]
    missing = [c for c in required if not _container_running(c)]
    if missing:
        pytest.skip(f"Stack chưa chạy — thiếu container: {missing}. Chạy: make up")
