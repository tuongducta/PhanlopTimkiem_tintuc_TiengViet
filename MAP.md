# MAP.md — Bản đồ dự án

| Đường dẫn | Vai trò |
|---|---|
| `SPEC.md` | Mục tiêu, phạm vi, tiêu chí hoàn thành |
| `PLAN.md` | Lộ trình và trạng thái; trỏ tới kế hoạch chi tiết |
| `README.md` | Cài đặt và cách chạy |
| **`sources/`** | **Tài liệu thô, chỉ đọc** |
| `sources/papers/` | PDF tài liệu khảo sát (`[1]`–`[13]`); `Paper_KDD_Data/` là các bài K* |
| `sources/repos/` | Mã tham khảo: `Trans2Vec/` (đang dùng làm mốc gốc), `GE-FSG/`, `Sqn2Vec/`, `UIT-ViON-Dataset/` |
| `sources/data/vntc/` | VNTC-10: `raw/` (UTF-16), `processed/corpus.tsv.gz` (pyvi), hai file `.rar` gốc |
| **`contexte/`** | **Những gì AI học được** |
| `contexte/plans/` | `KE_HOACH_SURVEY.md` (v2, không sửa), `KE_HOACH_SURVEY_v3.md`, `KE_HOACH_HE_THONG_DB.md` (GĐ-H1–H7, Mục 17–20), `KE_HOACH_TAI_CAU_TRUC.md` |
| `contexte/results/` | `RESULTS.md` (thực nghiệm Trans2Vec E1–E7), `RESULTS_DB.md` (E-DB1, 2, 4, 5) |
| `contexte/survey-notes/` | Phiếu đọc, `synthesis.md`, `review_log.md`, `candidates.md`, `he_thong_db.md` (đoạn chèn survey) |
| `contexte/archive/` | `TIEP_TUC*.md` (ghi chú tiếp tục cũ, ngày 08/10; đã thay bằng file này) |
| **`livrables/`** | **Sản phẩm nộp** |
| `livrables/survey/` | `Survey_Trans2Vec_VN_News.docx/.md` (build), `draft/` (nguồn + `refs.tsv` + `build.py` + `docx/`), `figures/` |
| `livrables/report_db/` | `BaoCao_CSDL_Trans2Vec.docx/.md` (build), `draft/`, `figures/`, `make_figures.py`, `build.py` |
| **`src/`** | **Mã nguồn** |
| `src/experiments/` | Thực nghiệm Trans2Vec (`t2v.py`, `prepare.py`, `run_*.py`, `make_report.py`), kết quả ở `results/` |
| `src/system/` | Hệ thống MariaDB + Manticore: `docker-compose.yml`, `db/` (DDL), `pipeline/` (nạp, huấn luyện, đồng bộ, RSS), `app/` (Streamlit), `bench/` (E-DB*), `models/` (mô hình đã huấn luyện), `README.md` |
| `scripts/` | `build-docs.sh`, `run-app.sh`, `count-pages.sh`, `init-git.sh` |
| `docs/` | Ảnh mẫu cấu trúc `harness-project_template_demo.png`, `sync-guide.md` (commit và gộp nhánh) |
| `WORKTREE.md` | Luật chạy nhiều phiên song song bằng git worktree; dùng chung CSDL nên có giới hạn |
| `.git/` | Nhánh `main`; remote `origin` = GitHub riêng tư `tuongducta/PhanlopTimkiem_tintuc_TiengViet`. Dữ liệu lớn nằm ngoài git (`.gitignore`) |
| `.claude/` | Cấu hình Claude Code: settings, rules, skills, agents |
| `.streamlit/config.toml` | Giao diện sáng; Streamlit chỉ đọc file này khi chạy từ thư mục gốc |
| `.venv-exp/` | Python 3.11, môi trường chính. `.venv/` (Python 3.14) không dùng cho dự án |
