## 2. Kiến trúc hệ thống

### 2.1 Phân vai: nguồn gốc và phái sinh

Hệ thống có ba thành phần (Hình 2.1). Nguyên tắc xuyên suốt: **mọi dữ liệu trong Manticore đều dựng lại được từ MariaDB**, nên Manticore có thể bị xóa và nạp lại bất kỳ lúc nào. Đây là mô hình "hệ thống ghi nhận và dữ liệu phái sinh" [@kleppmann2017]: hệ ghi nhận giữ phiên bản đúng duy nhất, còn hệ phái sinh là bản sao đã biến đổi, tối ưu cho một kiểu truy vấn.

**Bảng 2.1.** Phân vai giữa các thành phần

| Thành phần | Vai trò | Lý do chọn |
|---|---|---|
| MariaDB 11.8.9 | Nguồn dữ liệu gốc: bài báo, transaction, FI, mô hình, vector, dự đoán, đánh giá, nhật ký, tin RSS | ACID, khóa ngoại, CTE và window function, JSON; có kiểu `VECTOR` và chỉ mục vector [@mariadbvector] |
| Manticore Search 29.9.0 | Chỉ mục tìm kiếm: toàn văn BM25, vector HNSW, lọc thuộc tính | Engine chuyên dụng; dùng giao thức MySQL nên Python dùng chung một driver cho cả hai hệ [@manticoreknn] |
| Python 3.11 | Tách từ (pyvi [@pyvi]), khai phá FI, Doc2Vec (gensim [@gensim]), bộ phân loại, ứng dụng Streamlit | Mô hình nằm ở tầng ứng dụng; CSDL chỉ lưu dữ liệu, vector và kết quả |

Không dùng một hệ duy nhất vì InnoDB FULLTEXT kém Manticore rõ rệt với tiếng Việt (Chương 7). Ngược lại, Manticore không có khóa ngoại, không có giao dịch nhiều câu lệnh đầy đủ và không có truy vấn phân tích phong phú, nên không giữ được vai trò nguồn gốc.

![Hình 2.1. Kiến trúc hệ thống: luồng xử lý lô ghi vào MariaDB; Manticore được dựng lại từ MariaDB; ứng dụng đọc cả hai.](figures/fig_arch.png)

### 2.2 Luồng xử lý lô và luồng trực tuyến

**Bảng 2.2.** Các bước xử lý lô (đánh số như trong mã nguồn)

| Bước | Công việc | Script | Bảng ghi |
|---|---|---|---|
| A1 | Đọc VNTC (UTF-16), chuẩn hóa NFC, tách tiêu đề và thân bài | `load_articles.py` | `category`, `article` |
| A2 | Tách từ pyvi, xây từ vựng trên train, chọn top-50 item theo tf·idf | `load_articles.py` | `item`, `article_item` |
| A3 | Đọc transaction **từ MariaDB**, khai phá FI trên train (δ = 0,535%) | `train_models.py` | `model_run`, `itemset`, `itemset_item`, `article_itemset` |
| A4 | Huấn luyện Doc2Vec cho từng biến thể, suy luận vector | `train_models.py`, `train_variants.py` | `model_run`, `article_vector` |
| A5 | Huấn luyện bộ phân loại, dự đoán tập test, đánh giá | như trên | `prediction`, `eval_result` |
| A6 | Dựng lại bảng Manticore từ MariaDB | `sync_manticore.py` | Manticore `news` |

Bước A3 đọc dữ liệu từ CSDL chứ không từ tệp trung gian. Nhờ vậy mọi mô hình truy ngược được về đúng các dòng `article_item` đã dùng. Các bước A3–A5 tái hiện kết quả của bài khảo sát với sai lệch Macro-F1 không quá 0,004. Phần sai lệch này đến từ việc gensim huấn luyện đa luồng nên không tất định.

Tin RSS của VnExpress, Tuổi Trẻ và Thanh Niên do `fetch_news.py` thu thập. Tin được ghi vào các bảng riêng, **không trộn** vào `article`, để dữ liệu ngoài không làm bẩn tập train và test.

**Luồng trực tuyến:**
- **Phân loại:** tách từ, chọn top-50 item, khớp FI (bảng FI nạp sẵn trong bộ nhớ), suy luận vector, chạy 6 bộ phân loại, ghi `classify_log`.
- **Tìm kiếm:**
  1. Manticore chạy `MATCH()` (BM25) và `knn()`, mỗi nhánh lấy 100 ứng viên; lọc chuyên mục được đẩy xuống Manticore.
  2. Ứng dụng gộp hai danh sách bằng RRF.
  3. Khử trùng theo `body_md5` của MariaDB.
  4. Lấy chi tiết bài và FI từ MariaDB, rồi ghi `search_log`.

### 2.3 Triển khai

Hai dịch vụ chạy bằng Docker Compose với phiên bản ghim cố định, và chỉ mở cổng trên 127.0.0.1. Các tham số đáng chú ý của MariaDB:
- `innodb-buffer-pool-size=1G`: đủ để phần nóng của `article_item` nằm trong bộ nhớ.
- `mhnsw-max-cache-size=512M`: bộ đệm cho đồ thị HNSW.
- `innodb-ft-min-token-size=1` và `innodb-ft-enable-stopword=0`: tiếng Việt có nhiều âm tiết 1–2 ký tự, và danh sách stopword mặc định là tiếng Anh.
- `max-allowed-packet=256M`: câu `INSERT` theo lô chứa toàn văn bài báo.

Toàn bộ dữ liệu, gồm cả các bảng phụ cho thực nghiệm, chiếm khoảng 2,4 GB trong MariaDB và khoảng 1 GB trong Manticore.
