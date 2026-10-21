# Trans2Vec cho tin tức tiếng Việt: khảo sát và hệ thống MariaDB + Manticore

Dự án cho hai môn sau đại học ở HUTECH: **Tri thức dữ liệu** và **Hệ cơ sở dữ liệu nâng cao**. Cấu trúc thư mục theo mẫu *Claude Code Harness*, tầng 2 (xem `MAP.md` và `docs/harness-project_template_demo.png`).

| Tầng | Nội dung |
|---|---|
| 1. Nền tảng | `CLAUDE.md`, `MAP.md`, `contexte/`, `livrables/` |
| 2. Harness | + `CLAUDE.local.md`, `AGENTS.md`, `SPEC.md`, `PLAN.md`, `.mcp.json`, `.claude/`, `sources/`, `scripts/`, `docs/`, CI, `.env.example` |

## Cài đặt
1. **Python 3.11** trong `.venv-exp/`. Các gói chính: gensim, scikit-learn, pyvi, pymysql, streamlit. Phải ghim numpy 2.2.6 và scipy 1.15.3, vì gensim lỗi với numpy 2.4.
2. **Docker:**
   ```bash
   docker compose -f src/system/docker-compose.yml up -d
   ```
   Lệnh này bật MariaDB 11.8.9 (cổng 3307) và Manticore 29.9.0 (cổng 9306/9308). Mật khẩu chỉ dùng cho máy cá nhân; muốn đổi thì chép `.env.example` thành `src/system/.env`.
3. **Pandoc** (để build `.docx`), và Microsoft Word nếu cần đếm trang.

## Chạy
| Việc | Lệnh |
|---|---|
| Ứng dụng Streamlit | `scripts/run-app.sh` rồi mở http://127.0.0.1:8501 |
| Build survey và báo cáo CSDL | `scripts/build-docs.sh` |
| Đếm trang báo cáo CSDL | `scripts/count-pages.sh` |
| Nạp lại dữ liệu và mô hình từ đầu | Xem `src/system/README.md` |
| Chạy lại thực nghiệm Trans2Vec | Xem mục "Tái lập" trong `contexte/results/RESULTS.md`; các script nằm ở `src/experiments/` |

## Bắt đầu với Claude Code
Mở thư mục này, chạy `claude`. Claude đọc `CLAUDE.md`, `AGENTS.md`, `MAP.md`, rồi `SPEC.md` và `PLAN.md` trước mỗi task.
