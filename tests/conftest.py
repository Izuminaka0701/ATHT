"""Fixtures pytest — kiểm tra stack đang chạy trước khi test."""

import subprocess

import pytest


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
