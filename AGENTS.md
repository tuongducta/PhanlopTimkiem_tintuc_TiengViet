# AGENTS.md — Quy tắc chung cho mọi agent

- Làm đúng phạm vi task được giao, không tự mở rộng.
- Được ghi vào:
  - `src/` (mã nguồn);
  - `contexte/` (kế hoạch, kết quả, ghi chú);
  - `livrables/*/draft/` và `livrables/*/figures/` (nguồn của sản phẩm nộp);
  - `PLAN.md`.
- Chỉ đọc: `sources/`, `.venv*/`.
- Không tự `git commit` hay `git push`: người dùng tự làm. Chỉ gợi ý câu commit.
- Không xóa file ngoài `livrables/` khi chưa được xác nhận. Không xóa bảng trong CSDL khi chưa được xác nhận.
- Số liệu đưa vào tài liệu phải lấy từ kết quả thật (`src/system/bench/results/*.json`, `src/experiments/results/`, bảng `eval_result`). Không ước đoán.
- Kết thúc task: tóm tắt 3–5 dòng thay đổi, kèm danh sách file đã sửa và cách đã kiểm tra.

## Hợp đồng bàn giao (pipeline `/pipeline`)

| Agent | Đọc | Ghi | Được sửa |
|---|---|---|---|
| `architect` | mô tả task, `src/` | `01_kien_truc.md`, ADR | `contexte/handoff/`, `contexte/decisions/` |
| `spec-writer` | `01` | `02_dac_ta.md` (AC đánh số) | `contexte/handoff/`; `livrables/*/draft/` nếu task là tài liệu |
| `developer` (điều khiển Codex CLI) | `01`, `02`; vòng sửa thêm `04`, `05` | `codex_prompt.md`, `codex_last.md`, `03_trien_khai.md` | Codex sửa đúng các file trong phiếu duyệt |
| `code-reviewer` | `02`, `03`, `git diff` | trả kết quả, phiên điều phối ghi `04_review.md` | không sửa file |
| `tester` | `02`, `03` | `05_kiem_thu.md`, `shots/` | `contexte/handoff/`; xóa log kiểm thử của chính mình |

- File bàn giao nằm ở `contexte/handoff/<task>/`, theo mẫu `_template.md`.
- **Agent không tự gọi agent khác, không tự sang bước sau.** Phiên điều phối trình phiếu duyệt trước mỗi agent.
- Codex (khi được `developer` gọi) cũng tuân theo file này: chỉ sửa file được giao, không chạy `schema.sql`, `sync_manticore.py`, benchmark, không cài thư viện, không commit.

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
