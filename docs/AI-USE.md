# Khai báo sử dụng công cụ AI

## Công cụ
- **Cursor AI (Claude)** — hỗ trợ soạn cấu hình Docker, pytest, Makefile, tài liệu

## Phạm vi sử dụng
| Hạng mục | AI hỗ trợ | Con người rà soát |
|----------|-----------|-------------------|
| docker-compose.yml | Có | Có — kiểm tra topology 3 miền |
| Cấu hình nginx/postgres | Có | Có — đối chiếu policy |
| Test pytest | Có | Có — chạy make verify |
| threat-model.json | Có | Có — xác nhận ATT&CK whitelist |
| Báo cáo PDF / slides | Không | Nhóm tự viết |
| Chạy tấn công thật | Không | Không thực hiện |

## Cam kết
- Không dùng AI để tạo mã khai thác hoặc phân tích mã độc.
- Mọi khẳng định an toàn đều có test pytest tương ứng.
- ATT&CK techniques chỉ dùng mã trong danh sách trắng đề bài.
