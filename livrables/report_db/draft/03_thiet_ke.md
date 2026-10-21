## 3. Thiết kế cơ sở dữ liệu

### 3.1 Tổng quan lược đồ

Lược đồ gồm 16 bảng và 5 view, chia thành năm nhóm (Hình 3.1, Bảng 3.1). DDL đầy đủ nằm ở `src/system/db/schema.sql`, `views.sql` và `feed.sql`.

![Hình 3.1. Sơ đồ quan hệ của lược đồ MariaDB. Số ở góc là số dòng; mũi tên đi từ bảng con tới bảng cha theo khóa ngoại.](figures/fig_er.png)

**Bảng 3.1.** Các bảng lớn và khối lượng dữ liệu (21/10/2026)

| Bảng | Số dòng | Dữ liệu + chỉ mục |
|---|---|---|
| `article` | 84.132 | 1.413 + 14 MB |
| `article_item` (transaction) | 4.146.151 | 215 + 87 MB |
| `article_itemset` | 3.114.776 | 90 + 77 MB |
| `article_vector` | 420.660 (5 lần chạy × 84.132) | 341 + 6 MB |
| `prediction` | 352.611 (7 bộ phân loại × 50.373) | 72 + 12 MB |
| `item` | 135.546 | 7 + 4 MB |

Các bảng còn lại đều nhỏ:
- `itemset`: 3.586 dòng; `itemset_item`: 5.485 dòng.
- `model_run`: 15 dòng; `eval_result`: 42 dòng.
- Ba bảng RSS và hai bảng nhật ký.

### 3.2 Collation tiếng Việt

Collation mặc định của server, `utf8mb4_uca1400_ai_ci`, **không phân biệt dấu**. Trên bản cài thật, `'bàn' = 'bán'` trả về 1, và FULLTEXT tìm "bàn" khớp cả "bán" lẫn "bạn". Với tiếng Việt, dấu thanh phân biệt nghĩa, nên đây là lỗi chứ không phải tiện ích. Lược đồ dùng hai collation:
- **Cột văn bản:** `utf8mb4_uca1400_vietnamese_as_ci`. Collation này giữ dấu, không phân biệt hoa thường, và sắp xếp đúng bảng chữ cái tiếng Việt.
- **`item.token`, `itemset.label`:** `utf8mb4_bin`, so khớp tuyệt đối như từ vựng của gensim. Nhờ vậy hai token khác nhau trong mô hình không thể trùng nhau trong CSDL.

Collation của **kết nối** cũng phải đặt giống như vậy (`src/system/config.py`). Hằng chuỗi trong câu SQL được so theo collation của kết nối, nên nếu để mặc định thì `WHERE token = 'bàn'` vẫn gộp dấu.

### 3.3 Transaction và tập phổ biến: quan hệ nhiều–nhiều

Dữ liệu cho khai phá FI thường là tệp "mỗi dòng một transaction". Trong CSDL, lưu như vậy là một cột chứa danh sách, vi phạm dạng chuẩn 1. Lược đồ tách thành các bảng:
- **`item`:** từ vựng. `idf` để `NULL` cho từ dừng và từ quá hiếm; các từ này không vào transaction nhưng vẫn được lưu để giải thích.
- **`article_item(article_id, item_id, tf, tfidf, rnk)`:** **bảng transaction**, mỗi dòng là một cặp (bài, từ). Cột `rnk` lưu thứ hạng trong top-50, nên dựng được transaction với k nhỏ hơn bằng `WHERE rnk <= k` mà không phải tính lại.
- **`itemset`:** mỗi FI một dòng, gắn với lần khai phá đã sinh ra nó (`run_id`). Bảng có `UNIQUE(run_id, label)` và cột `wilson_lo` (cận dưới khoảng tin cậy Wilson của support).
- **`itemset_item`:** các phần tử của FI.
- **`article_itemset`:** FI nào khớp bài nào, dùng để giải thích kết quả, ví dụ "bài này chứa {bóng, đội}".

Thiết kế này cho phép dùng SQL để kiểm chứng thuật toán. Một truy vấn tìm FI có tập cha trực tiếp cùng support trả về **rỗng**, tức mọi FI đều đóng. Kết quả này khớp với kiểm tra bằng Python và dẫn tới một đính chính cho bài khảo sát: ở cấu hình này, bước lọc FI đóng không có tác dụng.

### 3.4 Lịch sử mô hình: `model_run`

Mỗi lần khai phá FI, huấn luyện embedding hay huấn luyện bộ phân loại tạo một dòng `model_run`:
- `kind` là loại lần chạy: `fim`, `trans-it`, `trans2vec-joi`, `lr`, `svm`…
- `parent_id` là khóa ngoại tự tham chiếu. Ví dụ: bộ phân loại có cha là lần chạy embedding, embedding có cha là lần khai phá FI.
- `params` và `metrics` có kiểu `JSON` kèm `CHECK (JSON_VALID(...))`. Mỗi loại mô hình có bộ siêu tham số khác nhau; nếu tách thành cột thì sẽ có hàng chục cột phần lớn là `NULL`.
- Các giá trị **cần truy vấn thường xuyên** nằm ở bảng riêng `eval_result(run_id, task, metric, config, value)`. Ứng dụng chỉ việc `SELECT … WHERE metric = 'macro_f1'` mà không phải phân tích JSON.

Hiện có 15 lần chạy:
- id 1: khai phá FI.
- Mỗi biểu diễn một cặp (embedding, bộ phân loại): TRANS-IT 2/3, JOI 4/5, TF-IDF 6/7, mã gốc 8/9, TRANS-FI 10/12, IND 11/13, CAT 15/16.
- Id 14 bị trống do một lần chạy lỗi đã rollback (Mục 5.2).

Câu hỏi "Macro-F1 0,857 đến từ mô hình nào, dùng FI nào, siêu tham số gì?" được trả lời bằng một truy vấn đệ quy trên `parent_id`.

### 3.5 Vector, dự đoán và cột sinh

**`article_vector(article_id, run_id, vec VECTOR(128))`** lưu vector đã chuẩn hóa L2. Khóa chính hai cột cho phép nhiều lần chạy cùng tồn tại. Vì vậy bảng **không** có chỉ mục vector; Mục 4.3 giải thích lý do.

**`prediction`** có hai phần:
- Nhãn dự đoán là cột riêng, có khóa ngoại tới `category` và chỉ mục `(run_id, pred_category_id)`, phục vụ ma trận nhầm lẫn.
- Phân phối xác suất (`proba`) để dạng JSON vì chỉ dùng để hiển thị.

**Cột sinh `body_md5`.** VNTC có bài trùng y hệt nội dung: 3.415 nhóm, tức 4.984 bản thừa. 3.056 bài test (6,1%) có bản sao trong train, và 380 nhóm mang nhãn khác nhau. Để khử trùng, lược đồ thêm cột:

```sql
body_md5 BINARY(16) AS (UNHEX(MD5(body))) STORED,  KEY ix_body_md5 (body_md5)
```

Cột khai báo `STORED` chứ không `VIRTUAL`: hash của văn bản dài được tính một lần khi ghi, và cột đánh chỉ mục được. Kiểu `BINARY(16)` chỉ tốn một nửa chỗ so với chuỗi hex. Lệnh `ALTER TABLE` mất 18 giây. Tác dụng của cột này nằm ở Mục 4.4.

### 3.6 Phân vùng bảng nhật ký, và vì sao không phân vùng `article_item`

Thiết kế ban đầu định phân vùng `article_item` theo `split`. Ý định này va vào một giới hạn của InnoDB: **bảng phân vùng không được có khóa ngoại, và cũng không được là đích của khóa ngoại** [@mariadbpartition]. Nhóm giữ khóa ngoại, vì ba lý do:
- Hai khóa ngoại bảo đảm transaction chỉ chứa bài và từ có thật.
- `split` không nằm trong `article_item`, nên muốn phân vùng theo cột này phải phi chuẩn hóa.
- Truy vấn trên `article_item` luôn đi theo khóa chính. Phân vùng không giúp loại bỏ phân vùng nào, mà còn bắt mỗi lần tra phải mở nhiều cây B+.

Phân vùng được dùng ở hai bảng **nhật ký** `search_log` và `classify_log`. Hai bảng này chỉ ghi thêm, thường được truy vấn theo khoảng thời gian, và cần xóa dữ liệu cũ theo lô. Thiết lập phân vùng:
- `RANGE COLUMNS(ts)` theo tháng, thêm phân vùng `pmax`.
- Không có khóa ngoại.
- Khóa chính (`id`, `ts`), vì khóa chính phải chứa cột phân vùng.

Xóa một tháng nhật ký là `DROP PARTITION`, tức thao tác trên siêu dữ liệu, không phải `DELETE` từng dòng.

### 3.7 Bảng RSS và view phân tích

Phần RSS gồm ba bảng:
- **`news_source`:** giữ `etag` và `last_modified` để gửi yêu cầu HTTP có điều kiện.
- **`feed_item`:** chống trùng bằng `url_hash BINARY(20)` (SHA-1 của URL) có ràng buộc `UNIQUE`, ghi bằng `INSERT IGNORE`. Khóa 20 byte gọn hơn `UNIQUE` trên `url VARCHAR(512)` và không vướng giới hạn độ dài khóa chỉ mục.
- **`fetch_log`:** ghi mã HTTP, số tin mới, độ trễ và lỗi của mỗi lần lấy.

Bốn view thể hiện truy vấn phân tích của SQL hiện đại:
- **`v_corpus_stats`:** thống kê corpus.
- **`v_category_top_item`, `v_category_fi`:** top từ hoặc FI của mỗi chuyên mục, dùng `ROW_NUMBER() OVER (PARTITION BY c.id ORDER BY COUNT(*) DESC)` trên kết quả `GROUP BY`. Ví dụ: Thể thao có {bóng, đội} ở 1.393 bài.
- **`v_confusion`:** ma trận nhầm lẫn của một lần chạy bất kỳ.
