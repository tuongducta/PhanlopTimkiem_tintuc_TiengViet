# KẾ HOẠCH HỆ THỐNG: Trans2Vec + MariaDB + Manticore Search

**Mục đích:** dùng chung một hệ thống cho hai môn:
- **Tri thức dữ liệu:** survey Trans2Vec, khai phá tập phổ biến (FI), học biểu diễn.
- **Hệ cơ sở dữ liệu nâng cao:** thiết kế lưu trữ, chỉ mục, truy vấn, tìm kiếm toàn văn và vector, tính nhất quán, hiệu năng.

**Ngày lập:** 20/10/2026 · **Trạng thái:** ✅ *đã duyệt H1–H6 (20/10)*, xem Mục 10 · ✅ GĐ-H1 xong (Mục 11) · ✅ GĐ-H2 xong (Mục 12) · ✅ GĐ-H3 xong (Mục 13) · ✅ GĐ-H4 xong (Mục 14) · ✅ GĐ-H5 xong (Mục 15) · ✅ GĐ-H6 xong (Mục 16, `contexte/results/RESULTS_DB.md`) · ✅ Mục 17 xong (6 mô hình ở trang Phân loại, 21/10) · ✅ GĐ-H7 xong (Mục 19.4: báo cáo `livrables/report_db/`, đoạn chèn survey `contexte/survey-notes/he_thong_db.md`, 21/10). · ✅ P1, P2 xong (Mục 20, 21/10).

**Quan hệ với các file khác:**
- File này **bổ sung** cho `KE_HOACH_SURVEY_v3.md` (phần survey) và **thay thế** "bản chạy thật dùng Streamlit đơn thuần" đã nhắc ở các trao đổi trước.
- Không sửa `KE_HOACH_SURVEY.md`, `src/experiments/` hay bản survey hiện có.
- Giao diện vẫn theo bản phác đã duyệt bố cục: https://claude.ai/artifact/MvVm7icEkfFGJfjm3Jj2eU

**Môi trường đã kiểm tra (20/10):**
- Đã có: Docker 28.3.2 (VM cấp 7,6 GB RAM), Homebrew, 131 GB đĩa trống.
- Chưa có: MariaDB, Manticore, driver MySQL cho Python.
- Đề xuất chạy cả hai bằng **Docker Compose**, không cài trực tiếp lên máy.

---

## 1. Phân vai: ai giữ cái gì

| Thành phần | Vai trò | Lý do |
|---|---|---|
| **MariaDB 11.8 LTS** | **Nguồn dữ liệu gốc (source of truth)**: bài báo, chuyên mục, transaction, FI, mô hình, dự đoán, nhật ký truy vấn, kết quả đánh giá | ACID, ràng buộc toàn vẹn, truy vấn phân tích (CTE, window function), JSON. Từ bản 11.8 có sẵn **kiểu `VECTOR` và `VECTOR INDEX` (HNSW)** để so sánh với Manticore |
| **Manticore Search** | **Chỉ mục tìm kiếm phái sinh**: toàn văn (BM25) và vector (KNN/HNSW) trên real-time table, kèm thuộc tính để lọc (chuyên mục, ngày) | Tìm kiếm toàn văn nhanh hơn InnoDB FULLTEXT; có KNN trên `float_vector`; **nói giao thức MySQL (cổng 9306)**, nên Python dùng chung một driver cho cả hai hệ |
| **Python (`.venv-exp`)** | Tiền xử lý (pyvi), khai phá FI, huấn luyện Trans2Vec (gensim), suy luận vector, bộ phân loại LR, API và giao diện | Mô hình nằm ở tầng ứng dụng. CSDL chỉ lưu dữ liệu, vector và kết quả |

**Nguyên tắc:** mọi thứ trong Manticore đều **dựng lại được từ MariaDB**. Manticore có thể xóa và nạp lại bất kỳ lúc nào. Đây là điểm để thảo luận về tính nhất quán giữa hai hệ (Mục 5).

---

## 2. Flow tổng thể

```
══════════════════════ A. LUỒNG OFFLINE (chạy lô) ══════════════════════

 VNTC raw (UTF-16)                                           ┌───────────── MariaDB ─────────────┐
   │  [A1] nạp + chuẩn hóa NFC ─────────────────────────────►│ category, article (raw text)      │
   │  [A2] pyvi tách từ, chọn top-k item mỗi bài ───────────►│ article_item  (transaction ~4,2tr dòng) │
   │  [A3] khai phá FI trên train (Python; đối chứng: SQL) ─►│ itemset, itemset_item, article_itemset │
   │  [A4] huấn luyện Trans2Vec-JOI, suy luận vector ───────►│ model_run, article_vector (VECTOR(128)) │
   │  [A5] huấn luyện LR, dự đoán tập test ─────────────────►│ prediction, eval_result           │
   │                                                         └───────────────┬───────────────────┘
   │  [A6] đồng bộ sang Manticore (bulk REPLACE theo lô)                     │
   ▼                                                                         ▼
                                    ┌──────────── Manticore (RT table `news`) ────────────┐
                                    │ title, body_seg (full-text, BM25)                    │
                                    │ category_id, published, split  (thuộc tính lọc)      │
                                    │ vec float_vector HNSW 128 chiều, COSINE              │
                                    └──────────────────────────────────────────────────────┘

══════════════════════ B. LUỒNG ONLINE (giao diện 3 tab) ══════════════════════

 [Phân loại]  văn bản ─► pyvi ─► item ─► khớp FI (bảng FI nạp sẵn vào bộ nhớ, gốc ở MariaDB)
                        ─► infer_vector (Trans2Vec) ─► LR ─► chuyên mục + top-3
                        ─► tô sáng từ thuộc FI ─► ghi `classify_log` (MariaDB)

 [Tìm kiếm]   truy vấn ─► pyvi ─┬─► Manticore MATCH()  (BM25)        ─┐
                                └─► infer_vector ─► Manticore KNN()  ─┤─► hợp nhất RRF ─► lọc chuyên mục
                                                                      ┘   ─► lấy chi tiết bài + FI từ MariaDB
                                                                          ─► ghi `search_log`

 [Dữ liệu và đánh giá]  đọc `eval_result`, thống kê FI theo chuyên mục (view/CTE trong MariaDB)
```

**Đổi so với bản trước:**
- Phần tìm kiếm trước đây chỉ dùng cosine trên vector JOI. Nay có **3 chế độ: BM25, vector, hybrid**. Đây là đóng góp mới cho **RQ6** của survey (Mục 6).
- Bộ lọc chuyên mục được đẩy xuống Manticore dưới dạng điều kiện thuộc tính, không lọc trong Python.

---

## 3. Thiết kế dữ liệu

### 3.1 Lược đồ MariaDB (bản nháp, sẽ chốt ở GĐ-H2)

| Bảng | Khóa / cột chính | Ghi chú thiết kế (nội dung cho môn CSDL) |
|---|---|---|
| `category` | `id` PK, `code` (XH…VT) UNIQUE, `name` | 10 dòng |
| `article` | `id` PK, `category_id` FK, `split` ENUM('train','test'), `source_file` UNIQUE, `title`, `body` MEDIUMTEXT, `body_seg` MEDIUMTEXT, `n_tokens` | 84.132 dòng. Thử **FULLTEXT InnoDB** trên `body` làm đối chứng với Manticore |
| `item` | `id` PK, `token` UNIQUE, `df_train` | Từ vựng sau tách từ (khoảng 44 nghìn từ) |
| `article_item` | PK (`article_id`, `item_id`), `tfidf` | **Bảng transaction**: khoảng 84 nghìn × 50 ≈ **4,2 triệu dòng**. Dùng cho bài về chỉ mục phủ, **partition theo `split`**, thứ tự cột trong khóa |
| `itemset` | `id` PK, `run_id` FK, `size`, `support`, `is_closed`, `wilson_lo` | Khoảng 3.586 FI ở δ = 0,535%. `wilson_lo` phục vụ lọc CICFI (K25) |
| `itemset_item` | PK (`itemset_id`, `item_id`) | Quan hệ nhiều–nhiều |
| `article_itemset` | PK (`article_id`, `itemset_id`) | FI khớp từng bài, dùng cho tô sáng và giải thích |
| `model_run` | `id` PK, `kind`, `params` JSON, `created_at`, `metrics` JSON | Lưu siêu tham số và kết quả từng lần chạy (tái lập) |
| `article_vector` | PK (`article_id`, `run_id`), `vec` **VECTOR(128)** + `VECTOR INDEX … DISTANCE=cosine` | So sánh trực tiếp **MariaDB Vector và Manticore KNN** |
| `prediction` | PK (`article_id`, `run_id`), `pred_category_id`, `proba` JSON | |
| `eval_result` | `run_id`, `metric`, `value` | Nguồn số liệu cho tab "Dữ liệu và đánh giá" |
| `search_log`, `classify_log` | `id`, `ts`, `query`/`text_hash`, `mode`, `latency_ms`, `result_ids` JSON | Nhật ký; partition theo tháng; dùng để đo độ trễ |

**View và thủ tục dự kiến (minh họa cho môn CSDL):**
- `v_category_fi`: top FI theo chuyên mục (window function `ROW_NUMBER() OVER (PARTITION BY …)`).
- `v_confusion`: ma trận nhầm lẫn từ `prediction`.
- Thủ tục `sp_pair_support(min_sup)`: **đếm support cặp item bằng self-join SQL**. Đây là phiên bản "khai phá FI trong DBMS" (hướng SETM / tích hợp DBMS) để so sánh với cài đặt Python (E-DB3).

### 3.2 Bảng Manticore `news` (bản nháp, cú pháp phải kiểm tra lại trên phiên bản cài thật)

```sql
CREATE TABLE news (
  title text, body_seg text,
  category_id uint, split string, published timestamp,
  vec float_vector knn_type='hnsw' knn_dims='128' hnsw_similarity='COSINE'
) charset_table='…' ;   -- xem lưu ý tiếng Việt bên dưới

-- Toàn văn:  SELECT id, WEIGHT() FROM news WHERE MATCH('giá_vàng tăng') AND category_id=4 LIMIT 10;
-- Vector:    SELECT id, knn_dist() FROM news WHERE knn(vec, 10, (0.12, …)) ;
```

**Lưu ý tiếng Việt (quan trọng, cần thực nghiệm):**
- Theo blog chính thức, `charset_table` mặc định (`non_cjk`) **gộp dấu thanh**, nên "tiếng" khớp với "tieng". Như vậy *bàn*, *bán*, *bạn* sẽ thành cùng một token. Tìm không dấu thì tiện, nhưng độ chính xác giảm.
- Kế hoạch: so sánh **(a) mặc định gộp dấu** với **(b) `charset_table` tự định nghĩa giữ nguyên chữ có dấu**, và thêm `_` làm ký tự của từ để giữ token pyvi như `giá_vàng`.
- Manticore không có tách từ hay stopword cho tiếng Việt. Vì vậy **nạp văn bản đã tách bằng pyvi** (`body_seg`), dùng cùng bộ tách từ với Trans2Vec.

---

## 4. Thực nghiệm phía CSDL (mới)

| Mã | Câu hỏi | Thiết lập | Độ đo |
|---|---|---|---|
| **E-DB1** | Tìm kiếm toàn văn: InnoDB FULLTEXT hay Manticore BM25? | 1.000 truy vấn từ khóa (giao thức A6 sẵn có) + 1.000 truy vấn là bài báo | Độ trễ p50/p95, QPS, kích thước chỉ mục, thời gian dựng; nDCG@10 (proxy cùng chuyên mục) |
| **E-DB2** | Tìm kiếm vector: MariaDB `VECTOR INDEX` hay Manticore HNSW? So với tìm vét cạn chính xác | Vector JOI 128 chiều của 84.132 bài; quét tham số M / ef | Recall@10 so với kết quả chính xác, độ trễ, bộ nhớ, thời gian dựng |
| **E-DB3** | Khai phá FI trong DBMS (SQL self-join / thủ tục) hay ngoài DBMS (Python)? | Cùng transaction, cùng δ; cặp và bộ ba | Thời gian, bộ nhớ, kế hoạch thực thi (EXPLAIN), tác dụng của chỉ mục và partition |
| **E-DB4** | **Hybrid** BM25 + vector (RRF) có tốt hơn từng thành phần không? | Như E-DB1; RRF với k = 60; có và không lọc chuyên mục | nDCG@10, MAP@100, P@10; tách theo truy vấn có/không chứa FI |
| **E-DB5** | Giữ dấu hay gộp dấu trong Manticore? | Cấu hình (a) và (b) ở Mục 3.2 | nDCG@10 và độ trễ |
| E-DB6 *(tùy chọn)* | Nhất quán khi ghi kép | Thêm bài mới: ghi MariaDB, rồi Manticore; cố ý gây lỗi giữa chừng | Số bản ghi lệch; thời gian đối soát lại |

E-DB4 và E-DB5 **đồng thời phục vụ survey (RQ6)**: BM25 là baseline truy hồi chuẩn mà v2 còn thiếu.

---

## 5. Ánh xạ sang nội dung môn "Hệ cơ sở dữ liệu nâng cao"

| Chủ đề môn | Thể hiện trong hệ thống |
|---|---|
| Thiết kế lược đồ, chuẩn hóa, ràng buộc | Lược đồ Mục 3.1: transaction và itemset dạng quan hệ nhiều–nhiều; FK; ENUM; JSON cho siêu tham số |
| Chỉ mục (B+tree, chỉ mục phủ, toàn văn, vector) | `article_item` (thứ tự khóa); FULLTEXT InnoDB; `VECTOR INDEX`; so với chỉ mục đảo ngược và HNSW của Manticore (E-DB1, E-DB2) |
| Tối ưu truy vấn | `EXPLAIN`/`ANALYZE` cho self-join đếm support (E-DB3); điều kiện để MariaDB dùng vector index (`ORDER BY VEC_DISTANCE… LIMIT`) |
| Phân vùng (partitioning) | `article_item` theo `split`; các bảng log theo tháng |
| Giao dịch, ACID, mức cô lập | Nạp lô theo transaction; ghi `prediction` cùng `model_run` một cách nguyên tử |
| View, thủ tục, trigger | `v_category_fi`, `v_confusion`, `sp_pair_support`; trigger đánh dấu bài cần đồng bộ sang Manticore (hàng đợi outbox) |
| CSDL phân tán / đa hệ, nhất quán | MariaDB (gốc) và Manticore (phái sinh); mẫu **outbox** hoặc dựng lại định kỳ; nhất quán cuối cùng (E-DB6) |
| CSDL cho truy hồi thông tin | BM25, chỉ mục đảo ngược, ANN/HNSW, hybrid search, xử lý tiếng Việt (E-DB5) |
| Đánh giá hiệu năng | Benchmark độ trễ, QPS, kích thước, thời gian dựng (Mục 4) |

---

## 6. Ảnh hưởng tới kế hoạch survey (`KE_HOACH_SURVEY_v3.md`)
- **RQ6 (tìm kiếm):** thêm baseline **BM25** và **hybrid**. Đây đúng là điểm yếu đã nêu trong phiếu K06 (proxy "cùng chuyên mục", PV yếu ở khớp truy vấn).
- **Chương 9 (đề xuất hệ thống):** vẽ lại kiến trúc theo Mục 2. Bổ sung mô-đun lưu trữ/chỉ mục. Lập luận chọn MariaDB/Manticore bằng số liệu E-DB1, E-DB2.
- **Tài liệu bổ sung cần tìm và xác minh ở GĐ11:**
  - khai phá luật kết hợp tích hợp DBMS (ví dụ Houtsma & Swami 1995, SETM; Sarawagi et al. 1998);
  - BM25 (Robertson & Zaragoza 2009);
  - HNSW (Malkov & Yashunin 2018/2020);
  - RRF (Cormack et al. 2009).
- **Phạm vi:** survey môn Tri thức dữ liệu chỉ cần **một mục ngắn** về kiến trúc. Chi tiết CSDL nằm trong báo cáo riêng của môn CSDL (câu hỏi H1).

---

## 7. Cấu trúc thư mục dự kiến (mới, không đụng `src/experiments/`)

```
src/system/
├── docker-compose.yml      # mariadb:11.8 + manticoresearch/manticore (ghim phiên bản khi cài)
├── db/
│   ├── schema.sql          # Mục 3.1
│   ├── views_procs.sql     # view, thủ tục, trigger
│   └── manticore.sql       # Mục 3.2
├── pipeline/               # A1–A6: load, segment, mine_fi, train, predict, sync_manticore
│   └── (tái dùng src/experiments/t2v.py, không sao chép logic)
├── app/                    # API + giao diện 3 tab theo bản phác
├── bench/                  # E-DB1 … E-DB6
└── README.md               # cách chạy
```

**Thư viện cần cài thêm vào `.venv-exp`** (xin phép trước khi cài):
- `pymysql` (một driver dùng cho cả MariaDB lẫn Manticore cổng 9306);
- `streamlit` (giao diện);
- tùy chọn `fastapi` + `uvicorn` nếu muốn tách API.

---

## 8. Lộ trình

| Giai đoạn | Công việc | Sản phẩm | Ước tính |
|---|---|---|---|
| GĐ-H1 | Docker Compose, khởi động 2 dịch vụ, kiểm tra kết nối, **kiểm tra cú pháp Manticore và MariaDB Vector trên bản cài thật** | `src/system/docker-compose.yml`, README | 0,5 ngày |
| GĐ-H2 | Chốt lược đồ, nạp dữ liệu A1–A2 (84 nghìn bài, 4,2 triệu dòng transaction) | `schema.sql`, `pipeline/load*.py` | 1 ngày |
| GĐ-H3 | A3–A5: FI, Trans2Vec, LR; ghi `model_run`, `prediction`, `eval_result`. Đối chiếu số liệu với GĐ6 (Macro-F1 JOI khoảng 0,849) | `pipeline/*.py` | 1 ngày |
| GĐ-H4 | A6 đồng bộ Manticore; tìm kiếm 3 chế độ | `manticore.sql`, `sync_manticore.py` | 0,5–1 ngày |
| GĐ-H5 | Giao diện 3 tab nối với dữ liệu thật | `app/` | 1 ngày |
| GĐ-H6 | Benchmark E-DB1 đến E-DB5 (E-DB6 tùy chọn) | `bench/`, `contexte/results/RESULTS_DB.md` | 1–2 ngày |
| GĐ-H7 | Đưa kết quả vào survey (RQ6, Chương 9) và báo cáo môn CSDL | cập nhật theo H1 | — |

GĐ8 (phiếu đọc) đã xong. GĐ9 (ma trận tổng hợp v3) làm song song được với GĐ-H1 đến GĐ-H3.

---

## 9. Câu hỏi cần anh/chị quyết định

1. **H1 – Sản phẩm nộp:** môn CSDL nộp **báo cáo riêng** (survey chỉ có một mục ngắn về kiến trúc), hay gộp vào cùng một tài liệu?
2. **H2 – Yêu cầu bắt buộc của môn CSDL:** đề bài có bắt buộc chủ đề nào không (ví dụ replication, phân tán, trigger, phân quyền, sao lưu)? Em sẽ bổ sung vào Mục 5.
3. **H3 – Chạy bằng Docker:** đồng ý chạy MariaDB 11.8 và Manticore bằng Docker Compose? Hay anh/chị muốn cài trực tiếp bằng Homebrew?
4. **H4 – Giao diện:** Streamlit (nhanh, giống bản phác), hay FastAPI + trang web riêng (tách tầng rõ hơn, hợp để trình bày kiến trúc CSDL)?
5. **H5 – Cài thư viện:** đồng ý cài `pymysql` và `streamlit` (cộng `fastapi` nếu chọn) vào `.venv-exp`?
6. **H6 – Phạm vi thực nghiệm:** chạy đủ E-DB1 đến E-DB5, hay chỉ E-DB1, E-DB2, E-DB4 (đủ cho cả hai môn)?

---

## 10. Quyết định đã chốt (20/10/2026)

| Câu | Quyết định |
|---|---|
| H1 | **Báo cáo riêng** cho môn CSDL. Survey chỉ có một mục ngắn về kiến trúc |
| H2 | Đề bài **không có yêu cầu riêng**. Dùng phạm vi ở Mục 5 |
| H3 | **Docker Compose** cho MariaDB 11.8 và Manticore |
| H4 | **Streamlit** (không tách FastAPI) |
| H5 | Được cài `pymysql` và `streamlit` vào `.venv-exp` |
| H6 | Chạy **E-DB1, E-DB2, E-DB4, E-DB5**. Bỏ E-DB3 (FI bằng SQL) và E-DB6 (ghi kép) |

Hệ quả: thủ tục `sp_pair_support` (Mục 3.1) và trigger outbox (Mục 5) chuyển thành *tùy chọn*, chưa làm.

---

## 11. Kết quả GĐ-H1 (20/10/2026)

**Đã làm:**
- `src/system/docker-compose.yml`: MariaDB **11.8.9** (cổng 3307) và Manticore **29.9.0** (9306/9308). Cả hai healthy.
- Đã cài `pymysql` 1.2.3 và `streamlit` 1.66.0 vào `.venv-exp`. numpy 2.2.6 và scipy 1.15.3 giữ nguyên.
- Thêm `src/system/config.py`, `src/system/README.md`, `src/system/bench/check_setup.py`.

**Phát hiện từ `check_setup.py` (ảnh hưởng thiết kế):**

| Kiểm tra | Kết quả | Hệ quả |
|---|---|---|
| MariaDB `VECTOR INDEX` cosine | Chạy được. `EXPLAIN` cho `key = v` khi có `ORDER BY VEC_DISTANCE_COSINE … LIMIT` | E-DB2 dùng được như thiết kế |
| InnoDB FULLTEXT, collation `utf8mb4_uca1400_ai_ci` | "bàn" khớp cả "bán" và "bạn" (**gộp dấu** do collation `ai`). `_` được coi là ký tự của từ, nên "giá_vàng" khớp nguyên token | Muốn giữ dấu thì cột `body_seg` phải dùng collation `utf8mb4_uca1400_as_ci`. Đưa vào E-DB1/E-DB5 như một cấu hình đối chứng |
| Manticore `charset_table` mặc định | "bàn" = "ban" = "bán"; `_` là dấu tách, nên "giá_vàng" thành "gia" + "vang" | Đúng như dự đoán ở Mục 3.2 (cấu hình a) |
| Manticore charset giữ dấu (`VI_CHARSET` trong `check_setup.py`) | Tách ra "bàn", "bán", "đường", "ước", "giá_vàng". Chữ hoa có dấu được hạ đúng | Cấu hình (b) cho E-DB5 |
| Manticore `knn(vec, k, …)` | `k` không giới hạn số dòng (k=2 vẫn trả 4 dòng); lọc `category_id` chạy được | Luôn kèm `LIMIT k` |
| Từ ghép pyvi khi giữ `_` | Truy vấn "vàng" **không** khớp tài liệu chứa "giá_vàng" | Truy vấn phải tách từ bằng pyvi giống tài liệu. E-DB5 thêm cấu hình (c): đánh chỉ mục cả âm tiết lẫn từ ghép (hai trường `body_syl` và `body_seg`) |

---

## 12. Bổ sung: thu thập tin mới nhất từ 3 báo (20/10/2026)

**Nguồn:** VnExpress, Tuổi Trẻ, Thanh Niên. Đây đều là báo lớn và là nguồn gốc của bộ VNTC, nên tin mới cùng miền dữ liệu với mô hình đã huấn luyện. Người Lao Động trả RSS với content-type `text/html`; VietnamPlus trả feed rỗng. Hai báo này để dự phòng.

**Cơ chế** (`src/system/pipeline/fetch_news.py`, `src/system/db/feed.sql`):
- Chỉ đọc **RSS công khai** (tiêu đề, mô tả ngắn, link, ảnh, giờ đăng). **Không** tải trang bài viết.
- Chống trùng bằng `UNIQUE(url_hash)` (SHA-1 của URL) với `INSERT IGNORE`. Gửi kèm ETag / Last-Modified để máy chủ có thể trả 304. Ba báo hiện chưa trả 304, luôn trả 200.
- Mỗi báo một transaction: tin mới, ETag và dòng `fetch_log` (HTTP, số tin, số tin mới, độ trễ, lỗi). Một báo lỗi không làm dừng các báo khác.
- Giờ đăng lưu theo UTC. Tuổi Trẻ dùng dạng `MM/DD/YYYY h:mm:ss AM` không ghi múi giờ, nên coi là giờ VN (+07).
- `--loop N` để lấy định kỳ, tối thiểu 5 phút một lần.
- Dữ liệu thu thập nằm ở bảng riêng `feed_item`, **không trộn với `article` (VNTC)**, để không làm bẩn tập train/test.

**Lần chạy đầu (16:35, 20/10):** VnExpress 49, Tuổi Trẻ 50, Thanh Niên 60 tin, độ trễ 116 / 118 / 338 ms. Chạy lại ngay thì có 1 tin mới thật, không bị trùng. Feed Tuổi Trẻ thay đổi giữa các lần tải, nên cần lấy định kỳ.

**Việc còn lại:** điền `pred_category` khi có mô hình (GĐ-H3); đồng bộ `feed_item` sang Manticore và đặt `indexed_at` (GĐ-H4); tab "Tin mới nhất" trong app (GĐ-H5, đã có trong bản phác).

---

## 12. Kết quả GĐ-H2 (20/10/2026)

**Quyết định:** cột văn bản tiếng Việt dùng `utf8mb4_uca1400_vietnamese_as_ci`, giữ dấu (anh/chị duyệt 20/10). `item.token` dùng `utf8mb4_bin`. Kết nối Python cũng đặt collation này (`src/system/config.py`). Lý do: hằng chuỗi được so theo collation của kết nối, nên nếu để mặc định thì `'bàn' = 'bán'` vẫn ra 1.

**File:**
- `src/system/db/schema.sql`: 13 bảng.
- `src/system/db/views.sql`: `v_corpus_stats`, `v_category_top_item`, `v_category_fi`, `v_confusion`.
- `src/system/pipeline/load_articles.py`: dùng lại `t2v.Vocab`, có assert khớp với `t2v.transactions`.
- `src/system/bench/check_load.py`.
- Các bảng RSS (`feed.sql`, `fetch_news.py`) được thêm song song, nằm ngoài schema này và không bị `schema.sql` xóa.

**Thay đổi so với bản nháp Mục 3.1:**
- `article.id` bằng thứ tự dòng trong `corpus.tsv.gz` cộng 1, vì Manticore không cho phép id 0.
- Thêm `body_syl` để chuẩn bị cho cấu hình (c) của E-DB5.
- `article_item` có thêm `tf` và `rnk`.
- **Không phân vùng `article_item`**, vì InnoDB không hỗ trợ khóa ngoại trên bảng phân vùng. Phần minh họa phân vùng chuyển sang `search_log` và `classify_log`, theo tháng.
- `article_vector` có PK (`article_id`, `run_id`), **không** có VECTOR INDEX. Lý do: VECTOR INDEX của MariaDB không lọc được theo `run_id`. E-DB2 sẽ chép vector của một lần chạy sang bảng riêng có index.

**Số liệu sau khi nạp (99 giây):**

| Đại lượng | Giá trị |
|---|---|
| Bài báo | 84.132 (train 33.759, test 50.373) |
| Token train / item dùng được / từ dừng | 135.546 / 43.777 / 78 |
| Dòng `article_item` | 4.146.151 (trung bình 49,28 item/bài; 5.650 bài có ít hơn 50 item) |
| Dung lượng | `article` khoảng 1,4 GB (văn bản gốc, âm tiết, từ); `article_item` 215 MB data + 87 MB index |
| Đếm support 1-item trên train bằng SQL | 2,4 giây; `EXPLAIN` dùng `ix_split_cat` rồi tra PK của `article_item` |

Kiểm tra toàn vẹn: không có transaction nào chứa từ dừng, không có tiêu đề rỗng, và "bàn" chỉ khớp "bàn".

---

## 13. Kết quả GĐ-H3 (20/10/2026)

**File:**
- `src/system/pipeline/train_models.py`: đọc transaction **từ MariaDB**, chạy FIM, TRANS-IT, Trans2Vec-JOI, TF-IDF và LR, rồi ghi ngược vào CSDL. Tổng thời gian 234 giây.
- `src/system/bench/check_models.py`.
- Mô hình lưu ở `src/system/models/` (khoảng 130 MB): `run2_it.model`, `run4_joi.model`, các file LR và TF-IDF dạng `.pkl`.

**Các lần chạy trong `model_run`:**

| id | kind | parent | Ghi chú |
|---|---|---|---|
| 1 | fim | — | δ = 0,535% (elbow), 3.586 FI (2.102 / 1.069 / 415 theo độ dài 1/2/3), khai phá mất 2,4 giây |
| 2 | trans-it | 1 | PV-DBOW d = 128, seed 1, 20 epoch; vector train suy luận lại như test |
| 3 | lr | 2 | C = 1 |
| 4 | trans2vec-joi | 1 | item ∪ FI(≥2) |
| 5 | lr | 4 | C = 1 |
| 6 | tfidf | — | toàn văn `body_seg`, từ vựng 43.777 |
| 7 | lr | 6 | C = 10 (như E5) |

**Đối chiếu với thực nghiệm GĐ6** (pipeline đọc dữ liệu từ CSDL tái hiện đúng kết quả cũ):

| Mô hình | Macro-F1 (MariaDB / GĐ6) | Accuracy | nDCG@10 (MariaDB / GĐ6) |
|---|---|---|---|
| TRANS-IT | 0,8469 / 0,8473 | 0,8736 | 0,8043 / 0,8029 |
| Trans2Vec-JOI | 0,8488 / 0,8487 | 0,8752 | 0,8158 / 0,8117 |
| TF-IDF | 0,9065 / 0,9065 | 0,9246 | 0,7402 / ≈0,740 |

Sai lệch không quá 0,004. Nguyên nhân là gensim huấn luyện đa luồng nên không tất định.

**Dữ liệu ghi thêm:** 3,11 triệu dòng `article_itemset` (167 MB); 168.264 vector (2 lần chạy × 84.132 bài, khoảng 101 MB); 151.119 dòng `prediction` (3 bộ phân loại × 50.373 bài test).

**Phát hiện: với cấu hình này, mọi FI đều là FI đóng.** Có hai kiểm chứng độc lập: `t2v.closed_only`, và một truy vấn SQL tìm itemset có tập cha trực tiếp cùng support (kết quả rỗng). Lý do: support tối thiểu là 181 bài, và FI chỉ dài tới 3, nên không có tập con nào trùng support với tập cha. Hệ quả:
1. Chênh lệch 0,770 so với 0,766 ở ablation A3 (GĐ6) là **do dao động ngẫu nhiên**, không phải do lọc FI đóng.
2. Ở cấu hình này, phần "closed FI" của E9 (H2, H8 trong survey) **không có tác dụng**. Muốn kiểm chứng H8 thì phải hạ δ hoặc nâng `max_len`. Cần sửa lại câu "Top-k ≈ 50 và FI đóng là đủ" ở RESULTS.md mục H2 khi làm GĐ11 của survey.

**Ví dụ từ các view:**
- `v_category_fi`: Thể thao → bóng|đội (1.393 bài), trận|đội; Kinh doanh → giá|tăng, giá|thị_trường.
- `v_confusion` (JOI): cặp nhầm nhiều nhất là KD→XH (549), XH→PL (362), XH→KD (255).

---

## 14. Kết quả GĐ-H4 (20/10/2026)

**File:**
- `src/system/db/manticore.sql`: DDL của bảng `news`. Các trường `title` (lưu và đánh chỉ mục), `title_seg`, `body_seg`, `body_syl` (chỉ đánh chỉ mục); thuộc tính `category_id`, `split`; `vec` (HNSW cosine, M = 16, ef_construction = 200); `charset_table` giữ dấu.
- `src/system/pipeline/sync_manticore.py`: dựng lại bảng từ MariaDB trong 61 giây, 84.132/84.132 tài liệu, khoảng 392 MB trên đĩa. Có tùy chọn `--table/--charset` để dựng biến thể gộp dấu cho E-DB5.
- `src/system/app/search.py`: lớp `Searcher` với 3 chế độ BM25 / KNN / hybrid RRF (k = 60), lọc theo chuyên mục, truy vấn tự do đi qua pyvi → transaction → FI → `infer_vector`.
- `src/system/bench/smoke_search.py`.

**Cú pháp Manticore 29.9 (khác bản nháp Mục 3.2):**
- `stored_fields` không dùng được trong `CREATE TABLE` của bảng RT. Thay bằng khai báo `text indexed` cho từng trường.
- Tham số ef viết dạng `knn(vec, k, (…), {ef=200})`.
- Ranker `bm25` mặc định của Manticore không chuẩn hóa độ dài, nên dùng `ranker=expr('10000*bm25a(1.2,0.75)')` cùng `idf='plain,tfidf_unnormalized'`.

**Kiểm tra nhanh** (giao thức GĐ6: 1.000 bài test làm truy vấn, kho là 33.759 bài train, liên quan = cùng chuyên mục):

| Chế độ | P@10 | MAP@100 | nDCG@10 | p50 / p95 (ms) |
|---|---|---|---|---|
| BM25 (top-50 item làm truy vấn OR) | 0,741 | 0,556 | 0,746 | 11,5 / 20,2 |
| BM25 + âm tiết (cấu hình c) | 0,617 | 0,414 | 0,622 | 72,3 / 126,5 |
| KNN HNSW (vector JOI) | 0,810 | 0,681 | 0,816 | 4,8 / 12,1 |
| KNN vét cạn (numpy) | 0,810 | 0,681 | 0,816 | — |
| Hybrid RRF | 0,811 | 0,638 | **0,818** | 16,5 / 30,3 |

Nhận xét:
1. KNN của Manticore cho đúng nDCG như tìm vét cạn ở GĐ-H3 (0,8158); recall@10 so với vét cạn đạt 0,997.
2. BM25 (0,746) ngang với TF-IDF cosine (0,740), hợp lý vì cùng là biểu diễn thưa.
3. Hybrid chỉ nhỉnh hơn KNN ở nDCG@10 (+0,002) nhưng **thấp hơn ở MAP@100** (−0,043). Lý do: BM25 kéo các bài sai chuyên mục vào vùng thứ hạng sâu. Cần kiểm chứng ở E-DB4 với truy vấn từ khóa ngắn. Đó mới là trường hợp hybrid được kỳ vọng phát huy.
4. Khi truy vấn là cả bài báo, khớp thêm âm tiết **làm kết quả kém hẳn** và chậm gấp 6 lần, vì số term OR tăng mạnh. Cấu hình (c) chỉ đáng thử với truy vấn ngắn (E-DB5).

**Phát hiện: VNTC có bài trùng lặp.**
- Có 3.415 nhóm bài trùng y hệt nội dung, gồm 8.399 bài, tức 4.984 bản thừa. Trong đó 2.522 nhóm có mặt ở cả train lẫn test, và **3.056 bài test (6,1%) có bản sao trong train**. 380 nhóm mang nhãn chuyên mục khác nhau, tức là nhiễu nhãn.
- **Ảnh hưởng tới phân loại không đáng kể.** Bỏ 3.056 bài đó thì Macro-F1 gần như không đổi: JOI 0,8498 so với 0,8488; TF-IDF 0,9063 so với 0,9065. Ngay trên chính các bài trùng, Macro-F1 còn thấp hơn (0,765), một phần do nhiễu nhãn. Kết luận của GĐ6 vì vậy vẫn giữ nguyên, nhưng survey nên ghi chú ở mục dữ liệu và giao thức (RQ5).
- **Ảnh hưởng tới giao diện:** kết quả tìm kiếm hiện ra bài lặp, nên cần khử trùng khi hiển thị.
- Bài học CSDL: JOIN trên `MD5(body)` chạy quá 5 phút vì không dùng được chỉ mục. Tính hash một lần vào bảng có chỉ mục thì chỉ mất 2,4 giây. Đề xuất: thêm cột sinh `body_md5 BINARY(16) AS (UNHEX(MD5(body))) STORED` có chỉ mục (chờ duyệt).

---

## 15. Kết quả GĐ-H5 (20/10/2026)

**Cột `body_md5` (duyệt 20/10):** `BINARY(16) AS (UNHEX(MD5(body))) STORED` có chỉ mục. Đã `ALTER` trên CSDL đang chạy (mất 18 giây) và đưa vào `schema.sql`. Kết quả: 79.148 nội dung khác nhau trên 84.132 bài.

**File:**
- `src/system/app/search.py` (viết lại). Mỗi kết quả kèm điểm và hạng BM25, điểm và hạng vector. Khử trùng theo `body_md5`. `details()` lấy thêm FI và tệp nguồn. Ghi `search_log`.
- `src/system/app/classify.py`: so sánh 3 mô hình (TF-IDF, TRANS-IT, Trans2Vec-JOI, cùng LR). Mô hình và Macro-F1 lấy từ `model_run`/`eval_result`. Có FI khớp để giải thích; ghi `classify_log`.
- `src/system/app/streamlit_app.py`: 4 mục theo bản phác.
  1. **Phân loại:** các bài ví dụ lấy từ tập test, 3 thẻ mô hình kèm biểu đồ top-3, tô sáng từ thuộc FI.
  2. **Tìm kiếm:** truy vấn mẫu, 3 chế độ, lọc chuyên mục, top 5/10, các chỉ số tổng quan, bảng kết quả kèm hạng BM25/vector, khung chi tiết bài, phân bố chuyên mục.
  3. **Dữ liệu và đánh giá:** chỉ số tổng quan, bảng phân loại và tìm kiếm đọc từ `eval_result`, ma trận nhầm lẫn (`v_confusion`), `v_corpus_stats`, `v_category_fi`, thống kê nhật ký.
  4. **Tin mới nhất:** trạng thái 3 nguồn RSS, nút "Lấy tin ngay" (tối đa một lần mỗi 5 phút, dùng kết nối riêng vì `fetch_all` cần transaction), "Phân loại bài này" ghi kết quả vào `feed_item.pred_category`.

**Kiểm thử:** dùng `streamlit.testing.v1.AppTest` đi qua cả 4 mục: phân loại một bài ví dụ, truy vấn mẫu ở hybrid/BM25, lọc Thể thao, phân loại một tin RSS. Không có exception. Các dòng nhật ký sinh ra khi kiểm thử đã xóa.

**Đo nhanh:** nạp mô hình 2,1 giây (một lần nhờ `st.cache_resource`); phân loại 3 mô hình 13–40 ms; tìm kiếm hybrid kèm khử trùng khoảng 50–170 ms.

**Chạy:** `.venv-exp/bin/streamlit run src/system/app/streamlit_app.py`, rồi mở http://127.0.0.1:8501

---

## 16. Kết quả GĐ-H6 (20/10/2026)

Chi tiết và bảng đầy đủ: `contexte/results/RESULTS_DB.md`. Số liệu gốc: `src/system/bench/results/*.json`. Cả bốn thực nghiệm dùng giao thức GĐ6 (1.000 truy vấn test, kho train).

- **E-DB1 (full-text):** Manticore hơn InnoDB FULLTEXT ở cả chất lượng và tốc độ.
  - kw: nDCG@10 0,655 so với 0,596; p50 1,2 ms so với 8,8 ms.
  - doc: nDCG@10 0,739 so với 0,597; QPS 244 so với 14.
- **E-DB2 (vector):** ở cùng M/ef, MariaDB MHNSW cho recall cao hơn Manticore HNSW.
  - Với M=16, ef=40: MariaDB đạt 0,997, Manticore 0,940.
  - Cả hai dưới 1 ms. Quét toàn bảng mất 7 ms.
  - nDCG@10 gần như không đổi (0,811–0,818) vì proxy "cùng chuyên mục" ít nhạy với recall.
  - Ở Manticore, ef=10 và ef=20 cho kết quả trùng nhau (chưa rõ nguyên nhân).
- **E-DB4 (hybrid):** RRF với k=60, d=100 cho nDCG@10 tốt nhất.
  - kw: 0,703 (knn 0,689, bm25 0,654).
  - doc: 0,818 (knn 0,816).
  - MAP@100 thấp hơn knn (0,525 so với 0,596 với kw), nên hybrid hợp cho top-10, không hợp cho thu hồi sâu.
  - Chọn d=20 thì kém hơn. k=60 và k=200 gần như như nhau.
- **E-DB5 (dấu):**
  - Truy vấn có dấu: giữ dấu tốt hơn gộp dấu (kw 0,654 so với 0,621; doc 0,746 so với 0,665, nhanh hơn 4 lần).
  - Truy vấn không dấu: bảng giữ dấu sụp còn 0,362, 9% truy vấn rỗng; gộp dấu giữ được 0,607.
  - Gộp dấu dồn bàn/bán/bản/ban thành cùng một token (21.316 bài).
  - Khớp thêm âm tiết không có lợi.

**Đề xuất** (✅ P1 và P2 đã duyệt 21/10; thực hiện ở Mục 20):
- (P1) Khi truy vấn hoàn toàn không dấu, chuyển sang tìm trên `news_fold`, hoặc thêm trường `body_fold` vào `news`.
- (P2) Survey RQ6 dùng recall@10 thay vì nDCG cho phần so sánh chỉ mục vector.

**Bảng phụ còn lại:** MariaDB `vec_m6`, `vec_m16`; Manticore `ft_only`, `vec_m6`, `vec_m16`, `news_fold`. Xóa được bất cứ lúc nào.

---

## 17. Kế hoạch: so sánh 4 biến thể Trans2Vec và 1 mô hình cải tiến ở mục Phân loại (21/10/2026, ✅ đã duyệt và làm xong, kết quả ở 17.5)

**Yêu cầu:** mục "So sánh mô hình" hiển thị thêm 4 biến thể là TRANS-IT, TRANS-FI, Trans2Vec-IND, Trans2Vec-JOI, cùng một mô hình cải tiến được xây từ 4 biến thể đó. **Mốc so sánh là Trans2Vec gốc**, thay cho TF-IDF (người dùng chốt ngày 21/10). Tổng cộng 6 mô hình. TF-IDF vẫn còn trong mục Dữ liệu và đánh giá.

### 17.1 Các mô hình

4 biến thể và mô hình cải tiến dùng cấu hình đã hiệu chỉnh của E6: d=128, seed 1, 20 epoch, vector train được suy luận lại như test, LR C=1. Mốc dùng cấu hình mã nguồn gốc của tác giả.

| Mô hình | Cách tạo | Trạng thái |
|---|---|---|
| **Trans2Vec gốc (mốc)** | Chạy đúng mã của tác giả ở `sources/repos/Trans2Vec/codes/trans2vec_joi_classify.py` (xem 17.1a) | **cần huấn luyện mới**, khoảng 3–4 phút |
| TRANS-IT | PV-DBOW trên item | có sẵn (run 2/3) |
| **TRANS-FI** | PV-DBOW trên token FI (gồm cả FI 1 phần tử), `t2v.pattern_tokens(mode="fi")` | **cần huấn luyện mới**, khoảng 1–2 phút |
| **Trans2Vec-IND** | trung bình của vector IT và FI đã chuẩn hóa, theo đúng định nghĩa ở survey `05_trans2vec.md` | không phải huấn luyện embedding, chỉ cần LR mới |
| Trans2Vec-JOI | PV-DBOW trên item ∪ FI(≥2) | có sẵn (run 4/5) |
| **Mô hình cải tiến** | chọn 1 trong 2 ứng viên ở 17.2 | mới |

Kết quả GĐ6 trên cùng cấu hình (Macro-F1, LR): IT 0,847, FI 0,826, JOI 0,849. IND chưa đo theo cấu hình suy luận lại.

**17.1a Trans2Vec gốc theo `sources/repos/Trans2Vec`.** Em giữ nguyên quy trình của mã tác giả, chỉ đổi những chỗ bắt buộc phải đổi.

Giữ nguyên:
- **Đầu vào dạng "Items-FIs"**: mỗi bài là một dòng `nhãn \t item … FI …`, giống file `*_items_fis_*.txt` mà `FIM_Trans.exe` xuất ra.
- **Doc2Vec PV-DBOW:** d=128, 50 epoch, min_count=0, các tham số còn lại để mặc định.
- **Học transductive như mã gốc:** Doc2Vec học trên toàn bộ 84.132 bài, gồm cả bài test nhưng không dùng nhãn của chúng. Vector lấy từ `docvecs`.
- **Phân loại:** `LinearSVC()` mặc định (C=1), không chuẩn hóa vector, báo Macro-F1 trên tập test.

Bắt buộc phải đổi:
- **Khai phá FI:** `FIM_Trans.exe` là chương trình .NET chạy trên Windows, không chạy được trên macOS. Em dùng chính bộ 3.586 FI của hệ thống (cùng δ = 0,535%), nên đầu vào của mốc và của 4 biến thể giống hệt nhau.
- **Phiên bản gensim:** mã gốc viết cho gensim 3.4. Em đổi tên tham số sang gensim 4.4 (`size`→`vector_size`, `iter`→`epochs`, `docvecs`→`dv`), giống cách đã làm ở E7 (`src/experiments/replicate_snippets.py`).
- **Cách chia train/test:** dùng cách chia gốc của VNTC (33.759/50.373). Lý do: với dữ liệu không phải Snippets, mã gốc lấy 80% số dòng đầu làm train.
- **Bài mới trên giao diện:** mô hình gốc không xử lý được bài chưa có lúc huấn luyện, nên em sinh vector bằng `infer_vector` rồi đưa vào SVM. Thẻ trên giao diện sẽ ghi rõ điểm này.
- **Xác suất:** SVM không cho xác suất, nên thẻ hiển thị điểm quyết định đã qua softmax, có ghi chú rõ.

Ghi chú khi đọc số liệu: transductive là giao thức có lợi cho mốc vì mô hình đã thấy văn bản test. Theo E7, trên Snippets, transductive chênh inductive từ −0,5 đến +1,9 điểm accuracy.

### 17.2 Hai ứng viên cho mô hình cải tiến

Cả hai chỉ dùng 4 biến thể trên. Em chọn ứng viên tốt hơn bằng **3-fold CV trên tập train**, không nhìn tập test, để tránh rò rỉ.

- **(C1) Trans2Vec-CAT:** nối ba vector [IT ‖ FI ‖ JOI], mỗi khối chuẩn hóa L2 (384 chiều), rồi chạy LR.
  - Mỗi biến thể nhìn bài theo một góc khác nhau; khi nối, LR tự học trọng số cho từng góc.
  - IND không cần đưa vào vì nó là tổ hợp tuyến tính của IT và FI.
- **(C2) Trans2Vec-STACK:** lấy xác suất out-of-fold của 4 LR (IT, FI, IND, JOI; 40 cột), rồi học một LR meta trên đó.
  - Gộp ở mức quyết định nên giải thích được mô hình tin biến thể nào hơn.

Cả hai đều rẻ: embedding đã có, chỉ phải fit thêm LR. Mô hình được chọn sẽ hiển thị với tên của chính nó.

**Lưu ý trung thực:** em dự đoán mô hình cải tiến chỉ tăng khoảng 0,5–2 điểm so với JOI, tức Giao diện sẽ ghi rõ mức chênh so với Trans2Vec gốc, tách thành hai phần: phần nhờ hiệu chỉnh cách đánh giá (suy luận lại vector train) và phần nhờ mô hình cải tiến.

### 17.3 Thay đổi code

1. **`src/system/pipeline/train_variants.py` (mới).**
   - Chạy thêm trên CSDL hiện có, không đòi `model_run` rỗng, không đụng các run 1–7.
   - Tạo các run: `trans2vec-orig` (mốc), `trans-fi` (kèm `article_vector`, đánh giá tìm kiếm), `trans2vec-ind`, `trans2vec-cat` hoặc `trans2vec-stack`, mỗi run có `lr`, `prediction`, `eval_result`.
   - Mô hình lưu vào `src/system/models/`.
   - Ước tính 3–5 phút, chạy nền.
2. **`src/system/app/classify.py`:** `KINDS` gồm 6 mô hình: gốc, IT, FI, IND, JOI, cải tiến; bỏ TF-IDF khỏi trang này. IND được tính trực tuyến từ IT và FI; mô hình cải tiến dùng lại các vector đó. Phân loại một bài sẽ chậm thêm khoảng 10–20 ms vì phải infer thêm vector FI.
3. **`src/system/app/streamlit_app.py`, mục Phân loại:**
   - Một **bảng tóm tắt** gồm 6 dòng: mô hình, dự đoán, xác suất, Macro-F1. Mô hình có Macro-F1 cao nhất được đánh dấu.
   - Dòng tổng hợp chuyển thành "x/6 mô hình đồng ý".
   - 6 thẻ chi tiết xếp 2 hàng × 3, mỗi thẻ có biểu đồ top-3 như hiện tại.
   - Phần "Vì sao…" giữ cho JOI.
   - Mục Dữ liệu và đánh giá tự hiện thêm dòng vì đọc từ `eval_result`.
4. **Kiểm thử:** AppTest đi qua cả 4 mục; đối chiếu Macro-F1 của TRANS-FI với GĐ6 (0,826 ± 0,01).

### 17.4 Cần anh/chị duyệt

- **Q1:** đồng ý chọn mô hình cải tiến giữa C1 và C2 bằng CV trên train? Nếu muốn chỉ định thẳng một phương án thì báo em.
- ~~Q2~~ Đã chốt 21/10: mốc là Trans2Vec gốc.
- ~~Q3~~ Đã chốt 21/10: mốc là mã của tác giả trong `sources/repos/Trans2Vec` (17.1a).

### 17.5 Kết quả (21/10/2026)

**Huấn luyện:** `src/system/pipeline/train_variants.py` chạy khoảng 3,5 phút, log ở `src/system/pipeline/train_variants.log`. Các run mới:

| Run | Nội dung |
|---|---|
| 8 / 9 | `trans2vec-orig` / `svm` |
| 10 / 12 | `trans-fi` / `lr` |
| 11 / 13 | `trans2vec-ind` / `lr` |
| 15 / 16 | `trans2vec-cat` / `lr` |

Run 14 bị bỏ qua vì lần chạy đầu lỗi rồi rollback: vector CAT 384 chiều không vừa cột `VECTOR(128)`. Em đã sửa để không lưu `article_vector` cho CAT, và cho script chạy tiếp được từ chỗ dừng.

**Chọn mô hình cải tiến (3-fold CV trên train, Macro-F1):**

| Ứng viên | Macro-F1 CV |
|---|---|
| **CAT** | **0,873** |
| STACK | 0,866 |
| JOI (đơn) | 0,862 |
| IT (đơn) | 0,861 |
| IND (đơn) | 0,858 |
| FI (đơn) | 0,844 |

Kết quả: chọn **CAT**.

**Kết quả trên 50.373 bài test:**

| Mô hình | Macro-F1 | Accuracy | So với mốc | nDCG@10 (tìm kiếm) |
|---|---|---|---|---|
| Trans2Vec gốc (mốc, transductive, LinearSVC) | 0,823 | 0,852 | — | 0,762 |
| TRANS-IT | 0,847 | 0,874 | +0,024 | 0,804 |
| TRANS-FI | 0,826 | 0,854 | +0,003 | 0,776 |
| Trans2Vec-IND | 0,842 | 0,870 | +0,019 | 0,793 |
| Trans2Vec-JOI | 0,849 | 0,875 | +0,026 | **0,816** |
| **Trans2Vec-CAT (cải tiến)** | **0,857** | **0,882** | **+0,033** | 0,807 |
| *TF-IDF (tham khảo, trang Dữ liệu)* | *0,907* | *0,925* | | *0,740* |

**Nhận xét:**
- TRANS-FI đạt 0,826, khớp GĐ6 (0,826).
- Mốc gốc đạt 0,823 ở chế độ transductive, cao hơn bản inductive dùng `model.dv` của GĐ6 (0,766). Lý do: khi học transductive, vector của bài test cũng nằm trong `model.dv`, nên vector train và test cùng phân phối.
- CAT hơn JOI 0,008 Macro-F1. Tuy vậy, CAT kém JOI ở tìm kiếm (0,807 so với 0,816), nên tìm kiếm vẫn dùng JOI.
- Vẫn còn khoảng cách 0,05 với TF-IDF.

**Kiểm thử:**
- Phân loại trực tuyến 60 bài test: trung bình 10 ms cho cả 6 mô hình.
- Dự đoán trực tuyến của CAT trùng với `prediction` đã lưu ở 29/30 bài. Bài lệch là do `infer_vector` có yếu tố ngẫu nhiên.
- AppTest đi qua cả 4 mục, không có exception. Bảng 6 mô hình hiển thị đúng; ma trận nhầm lẫn chọn được CAT.
- Dòng `classify_log` sinh ra khi kiểm thử đã xóa.

**Thay đổi giao diện:**
- Trang Phân loại có bảng tóm tắt 6 mô hình: dự đoán, xác suất, Macro-F1, chênh lệch so với mốc, cách tạo. Kèm 6 thẻ xếp 2 hàng × 3, phần "Vì sao" giữ cho JOI.
- Trang Dữ liệu có thêm các dòng mới.
- Trang Tin mới nhất phân loại bằng CAT.

---

## 18. Chỉnh giao diện theo bản phác (21/10/2026)

Người dùng phản hồi giao diện xấu. Nguyên nhân: Streamlit đi theo chế độ tối của máy (nền tối, nút đỏ), chữ dự đoán quá to, bảng còn chữ `None`, tô sáng màu vàng, biểu đồ phân bố bị trống.

**Đã sửa theo bản phác** (https://claude.ai/artifact/MvVm7icEkfFGJfjm3Jj2eU):
- `.streamlit/config.toml` ở thư mục gốc: nền sáng #F4F5F7, màu chủ đạo #1F4E99, thanh bên trắng, ẩn thanh công cụ.
- CSS trong `streamlit_app.py`: font Be Vietnam Pro, đầu trang có đường dẫn, tiêu đề và nhãn ngữ cảnh. Thanh bên là menu "Chức năng" và 3 thẻ "Kiến trúc".
- Phân loại:
  - Đoạn ví dụ dạng pill, chọn bài test mà mô hình mới nhất phân loại đúng.
  - Dòng tóm tắt và lưới 6 thẻ HTML gọn, top-3 vẽ bằng thanh mảnh, viền xanh cho Macro-F1 cao nhất.
  - Bảng chi tiết đưa vào mục mở rộng; phần "Vì sao" hiển thị dạng thẻ từ.
- Tìm kiếm: truy vấn mẫu dạng pill, ô chỉ số không còn mũi tên delta, phân bố chuyên mục vẽ bằng thanh HTML.
- Dữ liệu: ô chỉ số đồng bộ kiểu với các trang khác.
- Tin mới nhất:
  - Thẻ nguồn RSS có trạng thái xanh/đỏ; mỗi tin có nhãn chuyên mục (sửa lỗi `nan`).
  - Thêm nút "Phân loại N tin mới" (dùng Trans2Vec-CAT).

**Kiểm thử:**
- AppTest đi qua 4 trang, không có exception.
- Chụp màn hình bằng Chrome headless qua DevTools Protocol, đã xem từng trang.
- Nhật ký `search_log`/`classify_log` sinh ra khi kiểm thử đã xóa.

---

## 19. Kế hoạch GĐ-H7: đưa kết quả vào báo cáo (21/10/2026, ✅ đã duyệt Q-H7a, Q-H7b theo đề xuất; kết quả ở 19.4)

### 19.1 Báo cáo riêng môn "Hệ cơ sở dữ liệu nâng cao" (H1)

**Vị trí:** thư mục mới `livrables/report_db/`, gồm `draft/*.md`, `refs.tsv`, `build.py`, ra file `.md` và `.docx`. Build dùng pandoc như survey nhưng script riêng; không đụng `livrables/survey/`.

**Dàn ý dự kiến** (khoảng 20–25 trang A4):

| Chương | Nội dung | Nguồn số liệu |
|---|---|---|
| 1. Giới thiệu | Bài toán phân loại và tìm kiếm tin tức tiếng Việt; vì sao cần CSDL quan hệ kết hợp engine tìm kiếm | Mục 1–2 |
| 2. Kiến trúc | MariaDB giữ dữ liệu gốc, Manticore là bản phái sinh; luồng nạp → huấn luyện → đồng bộ → phục vụ; Docker Compose | Mục 2, 11 |
| 3. Thiết kế CSDL | Lược đồ ER (16 bảng gồm phần RSS); transaction/itemset dạng nhiều–nhiều; collation tiếng Việt giữ dấu; cột sinh `body_md5`; JSON cho siêu tham số; phân vùng bảng log, kèm lý do không phân vùng `article_item`; view | `schema.sql`, `views.sql`, `feed.sql`, Mục 12, 14 |
| 4. Chỉ mục và tối ưu truy vấn | B+tree theo thứ tự khóa; FULLTEXT; `VECTOR INDEX` (MHNSW) và điều kiện dùng được chỉ mục (EXPLAIN); bài học JOIN trên `MD5(body)` (hơn 5 phút xuống 2,4 giây) | Mục 13–15, E-DB2 |
| 5. Nạp dữ liệu và giao dịch | Nạp theo lô, transaction; `model_run` → `prediction`/`eval_result`; chạy tiếp được sau lỗi (rollback run 14) | `load_articles.py`, `train_*.py`, Mục 17.5 |
| 6. Manticore Search | Bảng RT, charset tiếng Việt, BM25, HNSW, lọc thuộc tính, RRF | `manticore.sql`, `search.py` |
| 7. Thực nghiệm | E-DB1, E-DB2, E-DB4, E-DB5: bảng và hình (độ trễ–recall, so sánh dấu) | `RESULTS_DB.md`, `bench/results/*.json` |
| 8. Ứng dụng | 4 trang Streamlit, nhật ký, RSS, 6 mô hình phân loại (ảnh chụp màn hình) | Mục 15, 17, 18 |
| 9. Thảo luận và hạn chế | Proxy "cùng chuyên mục"; nhất quán giữa hai hệ (dựng lại định kỳ, chưa có outbox); E-DB3, E-DB6 chưa làm; bài trùng VNTC | Mục 10, 14 |
| 10. Kết luận | | |

**Hình:**
- Sơ đồ kiến trúc và sơ đồ ER: vẽ bằng matplotlib vì máy không có graphviz.
- 4 biểu đồ benchmark.
- 3–4 ảnh chụp giao diện.

**Tài liệu tham khảo cần xác minh qua Crossref:** BM25 (Robertson & Zaragoza 2009), HNSW (Malkov & Yashunin 2020), RRF (Cormack et al. 2009), Trans2Vec (PAKDD 2018), VNTC (Hoang et al. 2007), tài liệu MariaDB Vector và Manticore.

### 19.2 Survey môn Tri thức dữ liệu

Phần này vướng **Q5 của `KE_HOACH_SURVEY_v3.md`**, vì chưa chốt sẽ sửa thẳng `livrables/survey/draft/` hay dựng `draft_v3/`.

**Đề xuất:** chưa sửa draft lúc này. Em soạn sẵn các đoạn cần chèn trong `contexte/survey-notes/he_thong_db.md`, rồi ráp vào khi làm GĐ11 của v3. Các đoạn gồm:
- Mục kiến trúc ngắn thay Hình 9.1.
- RQ6: bảng BM25 / vector / hybrid và kết luận về truy vấn ngắn.
- Bảng 6 mô hình phân loại (mốc gốc, 4 biến thể, CAT).
- Đính chính "mọi FI đều là FI đóng" (A3).
- Ghi chú bài trùng trong VNTC.

### 19.3 Cần anh/chị duyệt

- **Q-H7a:** báo cáo CSDL theo dàn ý trên, xuất `.docx` cùng định dạng survey (Times New Roman 13, A4)? Có giới hạn số trang không?
- **Q-H7b:** phần survey chỉ soạn sẵn đoạn chèn (đề xuất), hay sửa thẳng draft ngay (sao lưu bản cũ trước)?

### 19.4 Kết quả GĐ-H7 (21/10/2026)

**Báo cáo môn CSDL** (`livrables/report_db/`):

| File | Nội dung |
|---|---|
| `draft/00_front.md` … `10_ket_luan.md`, `draft/refs.tsv` | Nguồn của báo cáo, 10 chương theo dàn ý 19.1; 15 tài liệu tham khảo (bài báo đã xác minh qua Crossref, tài liệu web đã kiểm tra truy cập được) |
| `make_figures.py` → `figures/` | Sơ đồ kiến trúc, sơ đồ ER (16 bảng), 4 biểu đồ E-DB1/2/4/5; 3 ảnh chụp giao diện |
| `build.py` | Ghép .md, đánh số trích dẫn IEEE, xuất .docx bằng mẫu định dạng của survey (import `livrables/survey/draft/docx/build_docx.py`, không sửa gì trong `livrables/survey/`) |
| `BaoCao_CSDL_Trans2Vec.md`, `.docx` | Bản build: khoảng 9.300 từ, **30 trang A4** (đo bằng cách xuất PDF qua Word; PDF không lưu vào dự án) |

**Số trang:** người dùng cho giới hạn **25–30 trang** (21/10). Bản đầu dài 39 trang, đã rút còn 30. Cách rút:
- Mục lục chỉ còn tên chương (`--toc-depth=1`).
- Gộp các bảng phụ vào câu văn: thứ tự lần chạy, chi phí dựng chỉ mục E-DB2, bảng nhập nhằng dấu, bảng tổng hợp 7.6.
- Bảng E-DB2 rút còn 3 mức ef với M=16; cấu hình đầy đủ nằm ở Hình 7.2.
- Bỏ ảnh trang Tin mới nhất, thu nhỏ hai ảnh giao diện còn lại.
- Cô đọng các chương 1, 2, 3, 5, 9.

Định dạng giữ như survey: mỗi chương bắt đầu ở trang mới. Không còn dư chỗ, nên nếu thêm nội dung phải rút ở chỗ khác.

**Số liệu mới đo cho báo cáo** (trên CSDL thật):
- `EXPLAIN` chỉ mục vector theo 3 dạng truy vấn (cosine + LIMIT dùng chỉ mục; khác hàm khoảng cách hoặc thiếu LIMIT thì quét toàn bảng).
- JOIN theo `body_md5`: 0,64 giây.
- Loại bỏ phân vùng trên `search_log`.
- Thời gian các view: `v_confusion` 0,04 s, `v_category_fi` 0,66 s, `v_category_top_item` 3,8 s.
- Dung lượng từng bảng.

**Đoạn chèn survey** (`contexte/survey-notes/he_thong_db.md`, chưa chèn vào `livrables/survey/draft/`):
1. Thay Hình 9.1.
2. RQ6: bảng BM25 / vector / hybrid.
3. Bảng 6 mô hình phân loại.
4. Đính chính FI đóng.
5. Ghi chú bài trùng VNTC.
6. Ba tài liệu cần thêm vào `refs.tsv`.

**Sửa nhỏ ở ứng dụng:** trang Dữ liệu hiện "TB nan ms" khi nhật ký tìm kiếm rỗng; đã sửa. AppTest đạt; dòng nhật ký do kiểm thử sinh ra đã xóa.

**Còn chờ duyệt:** đề xuất P1 (nhánh gộp dấu cho truy vấn không dấu) và P2 (recall@10 cho so sánh chỉ mục; đã đưa vào đoạn chèn survey ở dạng đề xuất).

---

## 20. Thực hiện P1 và P2 (21/10/2026, người dùng duyệt cả hai)

### 20.1 P1: nhánh gộp dấu cho truy vấn không dấu

**Ràng buộc:** `charset_table` của Manticore áp cho cả bảng, nên không thể có trường giữ dấu và trường gộp dấu chỉ bằng cấu hình. Vì vậy em gộp dấu ở Python trước khi đánh chỉ mục.

**Thay đổi:**
- `src/system/vi_text.py` (mới): `fold()` (NFD bỏ dấu, đ→d, chữ thường) và `is_unaccented()`.
- `src/system/db/manticore.sql`: thêm `title_fold`, `body_fold` (`text indexed`).
- `src/system/pipeline/sync_manticore.py`: điền hai trường trên. Dựng lại `news` mất 99 giây (trước là 61 giây); dung lượng từ khoảng 390 MB lên 533 MB.
- `src/system/app/search.py`:
  - Thêm `Searcher.bm25_fold()`.
  - `search()` tự chuyển sang trường gộp dấu khi truy vấn không có dấu nào, và trả về `folded`.
  - Ở chế độ hybrid, khi truy vấn không dấu thì bỏ nhánh vector.
- `src/system/app/streamlit_app.py`: khi truy vấn không dấu, hiện ghi chú và tô sáng từ khớp theo dạng đã gộp dấu.
- `src/system/bench/edb5_diacritics.py`: thêm cấu hình (d) và phép đo đầu-cuối; đã chạy lại E-DB4 và E-DB5.

**Kết quả (nDCG@10, 1.000 truy vấn kw không dấu):**

| Phép đo | Trước P1 | Sau P1 |
|---|---|---|
| Giao thức E-DB5 (từ ghép khớp dạng cụm) | 0,394 (bảng giữ dấu), 9% truy vấn rỗng | 0,615 (cấu hình d), không có truy vấn rỗng |
| Đầu-cuối: truy vấn gõ tự do, qua `search()` | 0,399 | 0,534 (bm25 hoặc hybrid) |

Hybrid giữ cả nhánh vector với truy vấn không dấu chỉ đạt 0,473, nên phải bỏ nhánh vector. Bảng `news_fold` giờ chỉ còn dùng cho E-DB5 và có thể xóa.

**Tác dụng phụ:** sau khi thêm hai trường, điểm BM25 trên các trường cũ đổi nhẹ.
- Truy vấn có dấu: lệch không quá 0,005 nDCG ở cả E-DB4 lẫn E-DB5; kết luận giữ nguyên.
- Cấu hình (b) với truy vấn không dấu: 0,362 → 0,394.
- Giả thuyết: Manticore tính idf trên toàn bảng chứ không theo trường. Giả thuyết này chưa được kiểm chứng riêng.
- Số liệu E-DB4 cũ lưu ở `src/system/bench/results/edb4_hybrid_before_p1.json`.

**Kiểm thử:**
- AppTest đạt.
- Chụp màn hình trang Tìm kiếm với "gia vang tang manh": 10 bài Kinh doanh, có ghi chú, tô sáng đúng.
- Server Streamlit phải khởi động lại sau khi đổi `search.py`, vì `st.cache_resource` giữ đối tượng cũ.
- Dòng nhật ký do kiểm thử sinh ra đã xóa.

### 20.2 P2: recall@10 khi so sánh chỉ mục vector

Đã ghi vào đoạn chèn survey (`contexte/survey-notes/he_thong_db.md`, Mục 2). Báo cáo CSDL đã dùng recall@10 cho E-DB2 từ trước.

### 20.3 Cập nhật tài liệu

Đã cập nhật theo số liệu mới:
- `contexte/results/RESULTS_DB.md`, gồm E-DB4, E-DB5 và phần đầu-cuối;
- báo cáo `livrables/report_db/`, gồm Mục 7.4, 7.5, 6.2, 6.4, tóm tắt, kết luận và Hình 7.4;
- đoạn chèn survey.


---

## 21. Kế hoạch: áp dụng template HTML `sources/template_demo/` cho giao diện (22/10/2026, ✅ duyệt: Q-T1 = A, Q-T2 = nền tối, Q-T3 = giữ ảnh cũ)

### 21.1 Hiện trạng

Thư mục `sources/template_demo/` có 4 file HTML tĩnh, mỗi file ứng với một trang của app hiện tại:

| Template | Trang Streamlit |
|---|---|
| `demo_phanloaibaibao.html` | Phân loại bài báo |
| `demo_timkiemnangcao.html` | Tìm kiếm |
| `demo_dulieuvadanhgia.html` | Dữ liệu và đánh giá |
| `demo_tintucthoigianthuc.html` | Tin mới nhất |

**Phong cách của template:**
- Nền tối (#07090E), điểm nhấn cyan #00F2FE và indigo #6366F1, có hiệu ứng glow và gradient.
- Font Plus Jakarta Sans và JetBrains Mono.
- Tailwind qua CDN, thêm Font Awesome.

**Bố cục:**
- Thanh bên có logo T2V, 4 mục menu và thẻ "Kiến trúc hệ thống".
- Thanh trên có đường dẫn trang, nhãn tập dữ liệu và nhãn mô hình.
- Phần chính là banner ghi chú rồi tới các thẻ nội dung.

**Mâu thuẫn với quy tắc hiện hành:**
- CLAUDE.md và bộ nhớ đang ghi "giao diện bám bản phác artifact, nền sáng #1F4E99, Be Vietnam Pro".
- Template có **số liệu giả**: F1 94,8%, mô hình FastText, mã `LABEL_LAW_04`, mã phân tích `TX-984102`, "v2.4", chuông thông báo, avatar "AD". Banner còn ghi "dự đoán do bộ mô phỏng tính". Theo AGENTS.md, số liệu phải lấy từ kết quả thật, nên **chỉ lấy phong cách và bố cục, không lấy số**.
- Báo cáo CSDL (Chương 8) có 3 ảnh giao diện `fig_ui_*.png`. Ảnh được chụp từ giao diện sáng hiện tại.

### 21.2 Phương án

**A (đề xuất): giữ Streamlit, viết lại CSS và HTML theo template.**
- Logic giữ nguyên: `classify.py`, `search.py`, các truy vấn SQL.
- `st.html` không chạy script, nên không dùng được Tailwind CDN. Em sẽ dịch các lớp Tailwind cần dùng sang CSS thuần, đặt trong `streamlit_app.py`.
- Đổi `.streamlit/config.toml` sang theme tối theo bảng màu của template.
- Ưu điểm: không cài thư viện, AppTest vẫn chạy, Chương 8 báo cáo vẫn đúng ("ứng dụng Streamlit").
- Hạn chế: một số widget Streamlit (selectbox, bảng `st.dataframe`) chỉ chỉnh được màu, không giống template 100%.

**B: bỏ Streamlit, dùng FastAPI và trang HTML/Tailwind lấy từ template.**
- Giống template gần như tuyệt đối.
- Phải cài `fastapi` và `uvicorn` (chưa có trong `.venv-exp`).
- Phải viết API và JavaScript cho cả 4 trang, sửa `run-app.sh`, sửa Chương 8 và sơ đồ kiến trúc.
- Khối lượng lớn hơn A khoảng 3–4 lần.

### 21.3 Ánh xạ từng trang (theo phương án A)

| Trang | Lấy từ template | Giữ của app hiện tại (số thật) |
|---|---|---|
| Khung chung | Thanh bên tối với logo gradient và menu có vạch sáng ở mục đang chọn. Thẻ kiến trúc. Thanh trên có đường dẫn và các nhãn. | Nhãn "VNTC-10 · 84.132 bài". Bỏ chuông, avatar và "v2.4". |
| Phân loại | Thẻ nhập có bộ đếm ký tự và từ. Chip ví dụ. Nút gradient. Khối kết quả 3 cột: chuyên mục chính với thanh xác suất, so sánh mô hình, phân bố top-5. | 6 mô hình thật với Macro-F1 lấy từ `eval_result`. FI khớp, item tf·idf, tô sáng. Bảng chi tiết. |
| Tìm kiếm | 4 ô chỉ số. Thẻ truy vấn có chế độ, chuyên mục và số kết quả. Bố cục 7/5: bảng kết quả bên trái, chi tiết bài với điểm BM25/Vector/RRF bên phải. Phân bố chuyên mục. | Toàn bộ `Searcher`, ghi chú truy vấn không dấu, FI của truy vấn. |
| Dữ liệu và đánh giá | 5 ô KPI, 2 bảng đánh giá, lưới FI theo chuyên mục dạng thẻ. | Số đọc từ MariaDB. Heatmap ma trận nhầm lẫn đổi sang màu tối. Bảng `v_corpus_stats`. Dòng nhật ký. |
| Tin mới nhất | 3 thẻ nguồn RSS, thanh lọc và nút "Lấy tin ngay", danh sách tin dạng thẻ. | `fetch_news`, giới hạn tần suất, nút phân loại tin. |

Banner ghi chú: thay câu "bộ mô phỏng" bằng ghi chú thật, ví dụ "Liên quan = cùng chuyên mục (proxy)".

### 21.4 Các bước
1. Sửa `.streamlit/config.toml` và khối CSS trong `src/system/app/streamlit_app.py`.
2. Viết lại các hàm dựng HTML (`header`, `tiles`, `model_cards`, `hbars`) và từng trang theo 21.3.
3. Kiểm thử: `py_compile`, AppTest đi qua 4 trang, chụp màn hình từng trang bằng Chrome headless rồi so với template.
4. Xóa các dòng `search_log` và `classify_log` do kiểm thử sinh ra.
5. Tùy Q-T3: chụp lại `fig_ui_*.png`, build báo cáo, đếm trang.
6. Cập nhật CLAUDE.md, MAP.md, bộ nhớ và PLAN.md ("bám template `sources/template_demo/`").

### 21.5 Cần anh/chị duyệt
- **Q-T1:** chọn phương án A (đề xuất) hay B?
- **Q-T2:** chuyển hẳn sang nền tối như template? Đề xuất: có, và sửa quy tắc "nền sáng, bám bản phác artifact" trong CLAUDE.md thành "bám template".
- **Q-T3:** ảnh giao diện trong báo cáo CSDL xử lý thế nào? Đề xuất: chụp lại theo giao diện mới để báo cáo khớp với app. Ảnh nền tối in A4 vẫn đọc được nếu để rộng 62% như hiện tại. Phương án khác là giữ ảnh cũ.

**Quyết định (22/10/2026):**
- Q-T1: phương án A.
- Q-T2: chuyển sang nền tối. `sources/template_demo/` chỉ để tham khảo, không sửa hay phát triển trong thư mục này.
- Q-T3: giữ ảnh `fig_ui_*.png` cũ trong báo cáo, không chụp lại, không build lại báo cáo. Bỏ bước 5 của 21.4.

### 21.6 Kết quả (22/10/2026)

**Đã sửa:**
- `.streamlit/config.toml`: theme tối (#07090E, primary #22D3EE, thanh bên #0C0F17).
- `src/system/app/streamlit_app.py`: viết lại CSS và phần trình bày theo template. Logic, truy vấn SQL, `classify.py` và `search.py` giữ nguyên.
  - Khung chung: thanh bên có logo gradient, menu có vạch sáng, thẻ "Kiến trúc hệ thống" với trạng thái kết nối. Thanh trên có đường dẫn trang, nhãn VNTC-10 (đếm từ CSDL) và mô hình cải tiến. Mỗi trang có banner ghi chú thật.
  - Phân loại: thẻ nhập có bộ đếm ký tự và từ, chip ví dụ, 3 thẻ kết quả (chuyên mục chính, so sánh 6 mô hình, top-5), thẻ "Vì sao JOI chọn…".
  - Tìm kiếm: 4 ô chỉ số; chế độ dạng segmented control, thêm lựa chọn Top 20; bảng kết quả HTML 7/5; thẻ chi tiết có ô BM25/Vector/RRF; phân bố chuyên mục.
  - Dữ liệu: 5 ô KPI, 2 bảng đánh giá HTML (tô hàng JOI, in đậm giá trị tốt nhất), heatmap màu tối, bảng FI dạng chip.
  - Tin mới nhất: 3 thẻ nguồn RSS, lọc theo nguồn (mới), danh sách tin dạng thẻ.
  - Số thập phân dùng dấu phẩy như báo cáo.

**Ghi chú kỹ thuật:**
- `st.html` lọc bỏ `<svg>`, nên icon dùng font Material Symbols mà Streamlit đã nạp sẵn.
- Container có `key="card_*"` / `"news_*"` được tạo kiểu bằng `.stVerticalBlock[class*="st-key-…"]` kèm `!important`.
- Không được viết `*/` bên trong comment CSS: nó đóng comment sớm và làm hỏng rule ngay sau.

**Kiểm thử:**
- `py_compile` đạt.
- AppTest đi qua 4 trang, gồm chạy phân loại và tìm kiếm có dấu lẫn không dấu, không có exception.
- Chụp màn hình bằng Chrome headless (CDP, cổng 8502) cả 4 trang, có so với template.
- Đã xóa 8 dòng `search_log` (id > 9) và 5 dòng `classify_log` (id > 15) do kiểm thử sinh ra.
