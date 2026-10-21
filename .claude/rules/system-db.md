# Quy tắc cho hệ thống CSDL (src/system/)
- MariaDB là nguồn dữ liệu gốc; Manticore dựng lại được hoàn toàn bằng `pipeline/sync_manticore.py`.
- Đổi DDL: sửa `db/*.sql`, ghi lý do vào `contexte/plans/KE_HOACH_HE_THONG_DB.md`, rồi chạy lại benchmark bị ảnh hưởng.
- Kết nối dùng collation `utf8mb4_uca1400_vietnamese_as_ci` (giữ dấu).
- Không xóa phần RSS (`db/feed.sql`, `pipeline/fetch_news.py`, các bảng `news_source`, `feed_item`, `fetch_log`).
- Kiểm thử xong thì xóa các dòng `search_log`, `classify_log` do kiểm thử sinh ra.
