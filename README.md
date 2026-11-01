# Trans2Vec cho tin tức tiếng Việt: khảo sát và hệ thống MariaDB + Manticore

Dự án cho hai môn sau đại học ở HUTECH: **Tri thức dữ liệu** và **Hệ cơ sở dữ liệu nâng cao**. Cấu trúc thư mục theo mẫu *Claude Code Harness*, tầng 3: git nhánh `main`, remote `origin` = GitHub riêng tư `tuongducta/PhanlopTimkiem_tintuc_TiengViet` (xem `MAP.md` và `docs/harness-project_template_demo.png`).

| Tầng | Nội dung |
|---|---|
| 1. Nền tảng | `CLAUDE.md`, `MAP.md`, `contexte/`, `livrables/` |
| 2. Harness | + `CLAUDE.local.md`, `AGENTS.md`, `SPEC.md`, `PLAN.md`, `.mcp.json`, `.claude/`, `sources/`, `scripts/`, `docs/`, CI, `.env.example` |
| 3. Đồng bộ | + `WORKTREE.md`, `scripts/init-git.sh`, `docs/sync-guide.md`, git cục bộ (nhánh `main`) |

## Cài đặt
1. **Python 3.11** trong `.venv-exp/`. Các gói chính: gensim, scikit-learn, pyvi, pymysql, streamlit. Phải ghim numpy 2.2.6 và scipy 1.15.3, vì gensim lỗi với numpy 2.4.
2. **Docker:**
   ```bash
   docker compose -f src/system/docker-compose.yml up -d
   ```
   Lệnh này bật MariaDB 11.8.9 (cổng 3307) và Manticore 29.9.0 (cổng 9306/9308). Mật khẩu chỉ dùng cho máy cá nhân; muốn đổi thì chép `.env.example` thành `src/system/.env`.
3. **Pandoc** (để build `.docx`), và Microsoft Word nếu cần đếm trang.

## Khởi động hệ thống
Chạy các lệnh từ thư mục gốc dự án, sau khi đã cài đặt và nạp dữ liệu.

1. **Mở Docker Desktop** và chờ Docker sẵn sàng:
   ```bash
   open -a Docker
   docker info
   ```
   Lặp lại `docker info` nếu còn báo `Cannot connect to the Docker daemon`.
2. **Bật MariaDB và Manticore**, chờ đến khi cả hai healthy:
   ```bash
   docker compose -f src/system/docker-compose.yml up -d --wait
   ```
3. **Kiểm tra kết nối** (dòng cuối phải in `OK`):
   ```bash
   (cd src/system/bench && ../../../.venv-exp/bin/python check_setup.py)
   ```
4. **Chạy ứng dụng:**
   ```bash
   scripts/run-app.sh
   ```
   Mở http://127.0.0.1:8501. Nhấn `Ctrl+C` trong terminal này để dừng.

**Khởi động lại Streamlit** khi app báo lỗi kết nối dù CSDL đã bật, hoặc sau khi sửa `search.py`, `classify.py`:
```bash
kill $(lsof -tiTCP:8501 -sTCP:LISTEN)
scripts/run-app.sh
```

**Tắt CSDL** (dữ liệu vẫn được giữ trong Docker volume):
```bash
docker compose -f src/system/docker-compose.yml stop
```

**Mở dòng lệnh SQL** khi cần truy vấn trực tiếp:
```bash
docker exec -it t2v-mariadb mariadb -ut2v -p trans2vec   # MariaDB, nhập mật khẩu khi được hỏi
docker exec -it t2v-manticore mysql -h0 -P9306           # Manticore
```

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
