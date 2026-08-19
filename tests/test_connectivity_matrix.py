"""Kiểm tra ma trận kết nối — ai gọi được ai.

Ma trận (From → To):
                  dmz-web  gw-dmz-app  app-api  gw-app-data  data-db
  dmz-web            -        ALLOW      DENY      DENY        DENY
  gw-dmz-app       DENY       -          ALLOW     DENY        DENY
  app-api          DENY       DENY       -         ALLOW       DENY
  gw-app-data      DENY       DENY       DENY      -           ALLOW
  data-db          DENY       DENY       DENY      DENY        -
"""

import pytest
from helpers import tcp_connect_from, http_get_from


# ── Luồng hợp lệ (ALLOW) ──────────────────────────────────────────────

class TestAllowedFlows:
    """Các luồng được phép qua cổng kiểm soát."""

    def test_dmz_to_gateway_dmz_app_port_8000(self):
        """DMZ → gateway-dmz-app:8000 (cổng proxy HTTP)."""
        assert tcp_connect_from("dmz-web", "gateway-dmz-app", 8000)

    def test_gateway_dmz_app_to_app_api_port_5000(self):
        """gateway-dmz-app → app-api:5000 (proxy nội bộ APP)."""
        assert tcp_connect_from("gateway-dmz-app", "app-api", 5000)

    def test_app_api_to_gateway_app_data_port_5432(self):
        """app-api → gateway-app-data:5432 (proxy TCP DB)."""
        assert tcp_connect_from("app-api", "gateway-app-data", 5432)

    def test_gateway_app_data_to_data_db_port_5432(self):
        """gateway-app-data → data-db:5432."""
        assert tcp_connect_from("gateway-app-data", "data-db", 5432)

    def test_end_to_end_dmz_api_health(self):
        """Luồng end-to-end: dmz-web → gateway → app-api /health."""
        status, _ = http_get_from("dmz-web", "http://gateway-dmz-app:8000/health")
        assert status == 200

    def test_end_to_end_dmz_api_data(self):
        """Luồng end-to-end: dmz-web → gateway → app → gateway → db."""
        status, body = http_get_from("dmz-web", "http://gateway-dmz-app:8000/data")
        assert status == 200
        assert "records" in body


# ── Luồng bị chặn (DENY) — ít nhất 4 ca âm ───────────────────────────

class TestBlockedFlows:
    """Các luồng phải bị chặn — phòng đi tắt và leo thang."""

    def test_dmz_cannot_reach_app_api_directly(self):
        """[ĐE DỌA: đi tắt] dmz-web KHÔNG thể kết nối trực tiếp app-api:5000."""
        assert not tcp_connect_from("dmz-web", "app-api", 5000)

    def test_dmz_cannot_reach_data_db_directly(self):
        """[ĐE DỌA: container DMZ bị chiếm] dmz-web KHÔNG thể tới data-db:5432."""
        assert not tcp_connect_from("dmz-web", "data-db", 5432)

    def test_dmz_cannot_reach_gateway_app_data(self):
        """dmz-web KHÔNG thể tới gateway-app-data (miền APP/DATA)."""
        assert not tcp_connect_from("dmz-web", "gateway-app-data", 5432)

    def test_app_api_cannot_reach_data_db_directly(self):
        """[ĐE DỌA: đi tắt] app-api KHÔNG thể kết nối trực tiếp data-db:5432."""
        assert not tcp_connect_from("app-api", "data-db", 5432)

    def test_app_api_cannot_reach_dmz_web(self):
        """app-api KHÔNG thể kết nối ngược về dmz-web."""
        assert not tcp_connect_from("app-api", "dmz-web", 8080)

    def test_data_db_cannot_reach_dmz_web(self):
        """data-db KHÔNG thể kết nối ra dmz-web (cô lập miền DATA)."""
        assert not tcp_connect_from("data-db", "dmz-web", 8080)

    def test_data_db_cannot_reach_app_api_directly(self):
        """data-db KHÔNG thể kết nối trực tiếp app-api (chỉ nhận qua gateway)."""
        assert not tcp_connect_from("data-db", "app-api", 5000)

    def test_gateway_dmz_app_cannot_reach_data_db(self):
        """gateway-dmz-app KHÔNG thể nhảy thẳng tới data-db (không thuộc net_data)."""
        assert not tcp_connect_from("gateway-dmz-app", "data-db", 5432)
