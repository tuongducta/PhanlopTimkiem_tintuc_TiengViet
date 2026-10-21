# AGENTS.md — Quy tắc chung cho mọi agent

- Làm đúng phạm vi task được giao, không tự mở rộng.
- Được ghi vào:
  - `src/` (mã nguồn);
  - `contexte/` (kế hoạch, kết quả, ghi chú);
  - `livrables/*/draft/` và `livrables/*/figures/` (nguồn của sản phẩm nộp);
  - `PLAN.md`.
- Chỉ đọc: `sources/`, `.venv*/`.
- Không xóa file ngoài `livrables/` khi chưa được xác nhận. Không xóa bảng trong CSDL khi chưa được xác nhận.
- Số liệu đưa vào tài liệu phải lấy từ kết quả thật (`src/system/bench/results/*.json`, `src/experiments/results/`, bảng `eval_result`). Không ước đoán.
- Kết thúc task: tóm tắt 3–5 dòng thay đổi, kèm danh sách file đã sửa và cách đã kiểm tra.

## Lệnh thường dùng (chạy từ thư mục gốc)

| Việc | Lệnh |
|---|---|
| Bật CSDL | `docker compose -f src/system/docker-compose.yml up -d` |
| Kiểm tra kết nối | `cd src/system/bench && ../../../.venv-exp/bin/python check_setup.py` |
| Chạy ứng dụng | `scripts/run-app.sh` (http://127.0.0.1:8501) |
| Build survey và báo cáo | `scripts/build-docs.sh` |
| Đếm trang báo cáo | `scripts/count-pages.sh` (xuất PDF qua Word vào thư mục tạm) |
| Kiểm tra cú pháp | `.venv-exp/bin/python -m py_compile $(find src livrables -name '*.py')` |

Sau khi sửa `src/system/app/search.py` hoặc `classify.py` phải khởi động lại Streamlit, vì `st.cache_resource` giữ đối tượng cũ.
