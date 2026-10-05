# Config hardening — trước vs sau

## postgresql.conf
- **TRƯỚC**: xem `evidence/config-before/postgresql.conf`
- **SAU**: xem `evidence/config-after/postgresql.conf`

## pg_hba.conf
- **TRƯỚC**: xem `evidence/config-before/pg_hba.conf`
- **SAU**: xem `evidence/config-after/pg_hba.conf`

## nginx-dmz.conf
- **TRƯỚC**: xem `evidence/config-before/nginx-dmz.conf`
- **SAU**: xem `evidence/config-after/nginx-dmz.conf`

## gateway-dmz-app.conf
- **TRƯỚC**: xem `evidence/config-before/gateway-dmz-app.conf`
- **SAU**: xem `evidence/config-after/gateway-dmz-app.conf`

## policy.yaml
- **TRƯỚC**: xem `evidence/config-before/policy.yaml`
- **SAU**: xem `evidence/config-after/policy.yaml`

## Tóm tắt thay đổi

| File | Trước | Sau |
|------|-------|-----|
| postgresql.conf | listen_addresses='*' | listen_addresses=IP miền DATA |
| pg_hba.conf | trust mọi kết nối | scram-sha-256, chỉ appuser |
| nginx-dmz.conf | listen 80, không proxy | listen 8080, proxy qua gateway |
| gateway-dmz-app.conf | Không có | Proxy chỉ /health và /data, deny mặc định |
| policy.yaml | ALLOW ALL | DENY ALL + 5 ngoại lệ có lý do |
