## 4. Chỉ mục và tối ưu truy vấn

Mọi kế hoạch thực thi trong chương lấy từ `EXPLAIN` trên CSDL thật (MariaDB 11.8.9). Thời gian đo bằng `SHOW PROFILES`.

### 4.1 Khóa chính cụm và thứ tự cột trong `article_item`

Trong InnoDB, khóa chính là **chỉ mục cụm**: các dòng được lưu theo thứ tự khóa chính trong lá cây B+, và mỗi chỉ mục phụ chứa sẵn các cột khóa chính. Vì vậy thứ tự cột trong khóa của `article_item` quyết định truy vấn nào nhanh:

| Khóa | Truy vấn được phục vụ | Cách đọc |
|---|---|---|
| `PRIMARY KEY (article_id, item_id)` | Lấy transaction của một bài | Khoảng 50 dòng liền nhau trên một trang lá |
| `KEY ix_item_article (item_id, article_id)` | Bài nào chứa từ *t*; đếm support; khớp FI | Chỉ mục phụ có đủ hai cột nên là **chỉ mục phủ**, không phải quay về bảng |

Nếu chỉ có một chỉ mục, một trong hai hướng truy vấn sẽ phải quét toàn bộ 4,15 triệu dòng. Cái giá của chỉ mục thứ hai là 87 MB, khoảng 40% dung lượng dữ liệu của bảng. Ví dụ, đếm support của mọi từ trên tập train (bước đầu của khai phá FI bằng SQL):

```sql
EXPLAIN SELECT ai.item_id, COUNT(*) FROM article a
JOIN article_item ai ON ai.article_id = a.id
WHERE a.split = 'train' GROUP BY ai.item_id;
```

| table | type | key | ref | rows | Extra |
|---|---|---|---|---|---|
| a | ref | ix_split_cat | const | 44.251 | Using where; Using index; Using temporary; Using filesort |
| ai | ref | PRIMARY | a.id | 49 | |

Bộ tối ưu làm hai bước:
1. Lấy id các bài train qua `ix_split_cat`. Id là khóa chính nên có sẵn trong chỉ mục phụ, vì vậy kế hoạch ghi "Using index".
2. Với mỗi bài, tra khoảng 49 dòng `article_item` qua khóa chính cụm.

Truy vấn chạy 2,4 giây trên 1,66 triệu dòng transaction train. Con số 44.251 chỉ là ước lượng (số thật là 33.759), vì InnoDB ước lượng bằng cách lấy mẫu trang.

### 4.2 Chỉ mục toàn văn InnoDB

`ALTER TABLE article ADD FULLTEXT (body_seg)` mất 28,2 giây và tạo chỉ mục 135 MB. Để dùng được với tiếng Việt phải làm ba việc:
- hạ độ dài token tối thiểu xuống 1;
- tắt stopword tiếng Anh;
- đặt collation giữ dấu, vì chỉ mục toàn văn so token theo collation của cột.

Ký tự `_` của pyvi ("giá_vàng") được InnoDB coi là một phần của từ, nên từ ghép được giữ nguyên. Tuy vậy, InnoDB xếp hạng bằng một biến thể tf·idf riêng, không chuẩn hóa độ dài như BM25 và không chỉnh được tham số. Chương 7 cho thấy đây là nguyên nhân chính khiến InnoDB kém Manticore.

### 4.3 Chỉ mục vector MariaDB và điều kiện để được dùng

MariaDB cài đặt chỉ mục vector theo thuật toán HNSW [@malkov2020], gọi là MHNSW [@mariadbvector]. Bảng thử nghiệm của E-DB2:

```sql
CREATE TABLE vec_m16 (id INT UNSIGNED PRIMARY KEY, v VECTOR(128) NOT NULL,
                      VECTOR INDEX (v) M=16 DISTANCE=cosine) ENGINE=InnoDB;
```

Chỉ mục chỉ được dùng khi truy vấn có **đúng** dạng `ORDER BY VEC_DISTANCE_<hàm>(cột, hằng) LIMIT k`, và hàm trùng với `DISTANCE` lúc tạo chỉ mục:

| Truy vấn | type | key | rows | Extra |
|---|---|---|---|---|
| `ORDER BY VEC_DISTANCE_COSINE(v, @q) LIMIT 10` | index | v | 10 | |
| `ORDER BY VEC_DISTANCE_EUCLIDEAN(v, @q) LIMIT 10` | ALL | — | 32.589 | Using filesort |
| `ORDER BY VEC_DISTANCE_COSINE(v, @q)` (không `LIMIT`) | ALL | — | 32.589 | Using filesort |

Hai trường hợp sau rơi về quét toàn bảng. Kết quả vẫn đúng nên không có lỗi nào báo ra. Lý do: HNSW chỉ trả lời "k láng giềng gần nhất theo một hàm khoảng cách cố định"; muốn có toàn bộ thứ tự thì vẫn phải tính hết.

Bảng `article_vector` không có chỉ mục vector vì ba ràng buộc:
- Mỗi bảng chỉ có một chỉ mục vector.
- Chỉ mục không kết hợp được với điều kiện lọc. Với `WHERE run_id = 4 … LIMIT 10`, HNSW lấy 10 láng giềng của mọi lần chạy rồi mới lọc, nên có thể còn ít hơn 10 kết quả.
- `article_vector` chứa vector của 5 lần chạy.

Cách xử lý: E-DB2 chép vector của một lần chạy sang bảng riêng, còn hệ thống giao tìm kiếm vector cho Manticore. Manticore có lọc thuộc tính, và ứng dụng xin gấp 4 lần số ứng viên khi có bộ lọc.

### 4.4 Bài học: JOIN trên biểu thức

Câu hỏi "bao nhiêu bài test có bản sao trong train" lần đầu được viết như sau:

```sql
SELECT COUNT(DISTINCT a.id) FROM article a JOIN article b ON MD5(a.body) = MD5(b.body)
WHERE a.split = 'test' AND b.split = 'train';
```

Truy vấn chạy **hơn 5 phút** và phải dừng tay. Điều kiện nối là biểu thức trên cột nên không chỉ mục nào dùng được. Bộ tối ưu rơi về nested loop, về nguyên tắc phải tính MD5 cho 50.373 × 33.759 cặp văn bản. Lần thứ hai, hash được tính trước vào một bảng tạm có chỉ mục, và truy vấn chạy 2,4 giây. Cuối cùng, cột sinh `body_md5` (Mục 3.5) đưa lời giải vào lược đồ:

| table | type | key | ref | rows | Extra |
|---|---|---|---|---|---|
| a | ref | ix_split_cat | const | 44.251 | Using index condition; Using where |
| b | ref | ix_body_md5 | a.body_md5 | 1 | Using where |

Mỗi bài test giờ chỉ cần một lần tra B+tree trên khóa 16 byte. Truy vấn trả 3.056 bài sau **0,64 giây**, nhanh hơn ít nhất 470 lần. Bài học: **không đặt hàm lên cột trong điều kiện nối hay điều kiện lọc**. Nếu cần lọc theo biểu thức thì hiện thực hóa nó thành cột sinh có chỉ mục.

### 4.5 Loại bỏ phân vùng và thời gian của view

Với bảng nhật ký phân vùng theo tháng, điều kiện trên `ts` cho phép bộ tối ưu chỉ mở phân vùng liên quan:

```sql
EXPLAIN PARTITIONS SELECT COUNT(*), AVG(latency_ms) FROM search_log
WHERE ts >= '2026-11-01' AND ts < '2026-12-01';     -- partitions: p2026_11
```

Thời gian của các view:

| View | Khối lượng xử lý | Thời gian |
|---|---|---|
| `v_confusion` | 50.373 dòng `prediction` | 0,04 s |
| `v_category_fi` | 3,11 triệu dòng `article_itemset` | 0,66 s |
| `v_category_top_item` | 4,15 triệu dòng `article_item` | 3,8 s |

`v_category_top_item` chậm nhất vì phải gom nhóm toàn bộ transaction train rồi xếp hạng trong từng chuyên mục. Ứng dụng không gọi view này; trang thống kê dùng `v_category_fi` và lưu kết quả trong bộ nhớ đệm 1 giờ. Nếu cần dùng view này trực tuyến thì nên hiện thực hóa thành bảng, cập nhật sau mỗi lần nạp.
