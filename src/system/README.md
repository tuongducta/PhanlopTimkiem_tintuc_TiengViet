# Hệ thống Trans2Vec + MariaDB + Manticore

Kế hoạch đầy đủ: `contexte/plans/KE_HOACH_HE_THONG_DB.md`. Mọi lệnh dưới đây chạy **từ thư mục gốc dự án**. Thư mục này **không** sửa `src/experiments/`. Logic mô hình được import từ `src/experiments/t2v.py`.

## Thành phần

| Dịch vụ | Image | Cổng (chỉ 127.0.0.1) | Vai trò |
|---|---|---|---|
| MariaDB | `mariadb:11.8.9` | 3307 → 3306 | Nguồn dữ liệu gốc, có `VECTOR` + `VECTOR INDEX` |
| Manticore | `manticoresearch/manticore:29.9.0` | 9306 (MySQL), 9308 (HTTP) | Chỉ mục BM25 + KNN, dựng lại được từ MariaDB |

Tài khoản mặc định (chỉ dùng cho máy cá nhân): `t2v` / `t2v_pass`, database `trans2vec`. Ghi đè bằng biến môi trường, xem `config.py`.

## Chạy

```bash
docker compose -f src/system/docker-compose.yml up -d   # dữ liệu nằm trong volume trans2vec_mariadb_data, trans2vec_manticore_data
docker compose -f src/system/docker-compose.yml ps      # cả hai phải ở trạng thái healthy
(cd src/system/bench && ../../../.venv-exp/bin/python check_setup.py)   # kiểm tra kết nối và cú pháp
```

Lấy tin mới nhất từ RSS của VnExpress, Tuổi Trẻ, Thanh Niên (tự tạo bảng `news_source`, `feed_item`, `fetch_log` theo `db/feed.sql`):
```bash
.venv-exp/bin/python src/system/pipeline/fetch_news.py              # một lần
.venv-exp/bin/python src/system/pipeline/fetch_news.py --loop 15    # mỗi 15 phút
.venv-exp/bin/python src/system/pipeline/fetch_news.py --latest 10  # xem 10 tin mới nhất
```

Nạp dữ liệu VNTC (GĐ-H2, khoảng 2 phút; cần `sources/data/vntc/processed/corpus.tsv.gz` và `sources/data/vntc/raw/`):
```bash
docker exec -i t2v-mariadb mariadb -ut2v -pt2v_pass trans2vec < src/system/db/schema.sql   # XÓA và tạo lại bảng lõi
.venv-exp/bin/python src/system/pipeline/load_articles.py
docker exec -i t2v-mariadb mariadb -ut2v -pt2v_pass trans2vec < src/system/db/views.sql
.venv-exp/bin/python src/system/bench/check_load.py
```
Huấn luyện (GĐ-H3, khoảng 4 phút; ghi model_run, itemset, article_vector, prediction, eval_result và lưu mô hình vào `src/system/models/`):
```bash
.venv-exp/bin/python src/system/pipeline/train_models.py
.venv-exp/bin/python src/system/bench/check_models.py     # đối chiếu với E5/E6
```
Mốc Trans2Vec gốc (mã tác giả ở `sources/repos/Trans2Vec`), TRANS-FI, Trans2Vec-IND và mô hình cải tiến Trans2Vec-CAT (Mục 17, khoảng 3,5 phút; chạy sau `train_models.py`, bước nào đã có run thì dùng lại):
```bash
.venv-exp/bin/python src/system/pipeline/train_variants.py
```
Đồng bộ Manticore và kiểm tra tìm kiếm (GĐ-H4, khoảng 1 phút + 3 phút):
```bash
.venv-exp/bin/python src/system/pipeline/sync_manticore.py       # DROP + dựng lại bảng `news` từ MariaDB
.venv-exp/bin/python src/system/bench/smoke_search.py            # BM25 / KNN / hybrid theo giao thức GĐ6
```

Giao diện (GĐ-H5), mở http://127.0.0.1:8501. Chạy **từ thư mục gốc dự án** để Streamlit đọc `.streamlit/config.toml` (nền sáng, xanh #1F4E99 theo bản phác):
```bash
scripts/run-app.sh      # = .venv-exp/bin/streamlit run src/system/app/streamlit_app.py
```

Benchmark (GĐ-H6, khoảng 15 phút cho cả bốn; kết quả ở `src/system/bench/results/*.json`, tổng hợp trong `contexte/results/RESULTS_DB.md`):
```bash
# E-DB1 đọc dung lượng tablespace nên cần quyền PROCESS (cấp một lần):
docker exec -i t2v-mariadb mariadb -uroot -pt2v_root -e "GRANT PROCESS ON *.* TO 't2v'@'%'"
.venv-exp/bin/python src/system/bench/edb1_fulltext.py     # InnoDB FULLTEXT vs Manticore (cần các cờ innodb-ft-* trong docker-compose.yml)
.venv-exp/bin/python src/system/bench/edb2_vector.py       # MariaDB MHNSW vs Manticore HNSW, M ∈ {6,16}, ef ∈ {10…200}
.venv-exp/bin/python src/system/bench/edb4_hybrid.py       # BM25 / KNN / RRF
.venv-exp/bin/python src/system/bench/edb5_diacritics.py   # giữ dấu vs gộp dấu (tự dựng bảng news_fold nếu chưa có)
```
Các bảng phụ do benchmark tạo: MariaDB `vec_m6`, `vec_m16`; Manticore `ft_only`, `vec_m6`, `vec_m16`, `news_fold`. Xóa được bất cứ lúc nào bằng `DROP TABLE`.

Muốn chạy lại thì xóa run cũ trước: `DELETE FROM model_run;` (các bảng con tự xóa theo `ON DELETE CASCADE`), rồi xóa `src/system/models/`.

`schema.sql` không đụng tới các bảng RSS của `db/feed.sql`.

Dừng: `docker compose -f src/system/docker-compose.yml stop`. Xóa sạch dữ liệu: `… down -v`.

Truy cập thủ công:
```bash
docker exec -it t2v-mariadb mariadb -ut2v -pt2v_pass trans2vec
docker exec -it t2v-manticore mysql -h0 -P9306
```

## Thư mục

```
config.py        # kết nối dùng chung (pymysql cho cả hai hệ)
db/              # schema.sql, views_procs.sql, manticore.sql  (GĐ-H2, GĐ-H4)
pipeline/        # A1–A6: nạp, tách từ, FI, Trans2Vec, dự đoán, đồng bộ (GĐ-H2 → GĐ-H4)
app/             # search.py, classify.py, streamlit_app.py (4 mục, GĐ-H5)
bench/           # check_setup.py; E-DB1, E-DB2, E-DB4, E-DB5 (GĐ-H6)
```

## Lưu ý cú pháp đã kiểm tra trên bản cài thật (20/10/2026)

- **MariaDB vector:** `VECTOR(n)`, `VECTOR INDEX (v) M=8 DISTANCE=cosine`, `VEC_FromText('[...]')`. Chỉ mục chỉ được dùng khi truy vấn có dạng `ORDER BY VEC_DISTANCE_COSINE(v, …) LIMIT k`. Kiểm tra bằng `EXPLAIN`: cột `key = v`.
- **Manticore KNN:** `WHERE knn(vec, k, (…))`. Tham số `k` **không** giới hạn số dòng trả về, nên luôn kèm `LIMIT k`. Lọc thuộc tính (`AND category_id=…`) chạy được cùng KNN.
- **Charset tiếng Việt:** xem kết quả trong `contexte/plans/KE_HOACH_HE_THONG_DB.md` Mục 11.
- **Manticore 29.9:** trường không lưu nội dung khai báo `text indexed` (không dùng được `stored_fields` cho bảng RT); ef viết `knn(vec, k, (…), {ef=200})`; BM25 chuẩn dùng `ranker=expr('10000*bm25a(1.2,0.75)')`.

## Báo cáo môn CSDL (GĐ-H7)

```bash
scripts/build-docs.sh     # vẽ hình + build survey và báo cáo → livrables/report_db/BaoCao_CSDL_Trans2Vec.md/.docx
scripts/count-pages.sh    # đếm trang (giới hạn 25–30)
```
Nguồn ở `livrables/report_db/draft/`. Ảnh chụp giao diện (`figures/fig_ui_*.png`) chụp tay, không do script sinh.

**Truy vấn không dấu (P1):** bảng `news` có thêm `title_fold`, `body_fold` (gộp dấu bằng `src/system/vi_text.py`). Sau khi đổi `manticore.sql`, chạy lại `sync_manticore.py`; sau khi đổi `app/search.py`, khởi động lại Streamlit vì `st.cache_resource` giữ đối tượng cũ.
