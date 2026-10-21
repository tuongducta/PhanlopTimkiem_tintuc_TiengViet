## 6. Manticore Search: chỉ mục tìm kiếm phái sinh

### 6.1 Bảng real-time `news`

Manticore có bảng *plain* (dựng một lần từ nguồn) và bảng *real-time* (RT, ghi được bằng `INSERT`/`REPLACE`). Hệ thống dùng bảng RT (`src/system/db/manticore.sql`):

```sql
CREATE TABLE news (
  title       text,                -- lưu + đánh chỉ mục, để HIGHLIGHT()
  title_seg   text indexed,        -- tiêu đề đã tách từ
  body_seg    text indexed,        -- toàn văn đã tách từ (giá_vàng là một token)
  body_syl    text indexed,        -- toàn văn theo âm tiết (cấu hình c của E-DB5)
  category_id uint,
  split       string attribute,
  vec         float_vector knn_type='hnsw' knn_dims='128'
              hnsw_similarity='COSINE' hnsw_m='16' hnsw_ef_construction='200'
) charset_table='…' min_word_len='1';
```

Ba lựa chọn thiết kế:
- **`text indexed`** chỉ đánh chỉ mục, không lưu nội dung. Toàn văn đã có ở MariaDB, nên ứng dụng lấy id từ Manticore rồi tra chi tiết từ MariaDB. Mỗi hệ làm đúng việc của nó.
- **Thuộc tính `category_id`, `split`** dùng để lọc ngay trong engine, cùng lúc với xếp hạng.
- **Cột vector** chứa vector Trans2Vec-JOI, biến thể cho nDCG@10 tìm kiếm cao nhất (0,816).

Kiểm tra trên bản 29.9 phát hiện vài chỗ cú pháp khác tài liệu cũ:
- `stored_fields` không dùng được trong `CREATE TABLE` của bảng RT.
- ef viết dạng `knn(vec, k, (…), {ef=200})`.
- Trong `knn(vec, k, …)`, `k` **không giới hạn số dòng trả về**, nên mọi truy vấn phải kèm `LIMIT k`.

### 6.2 Tách từ và bộ ký tự tiếng Việt

Manticore không có bộ tách từ cho tiếng Việt. Vì vậy hệ thống **đánh chỉ mục văn bản đã tách bằng pyvi**, dùng cùng bộ tách với mô hình, và tách truy vấn theo đúng cách đó.

Bộ ký tự mặc định `non_cjk` có hai vấn đề:
- **Gộp dấu:** "bàn", "bán", "bản", "ban" thành một token.
- **Coi `_` là dấu tách:** "giá_vàng" thành "gia" và "vang".

Hệ thống dùng một `charset_table` tự định nghĩa [@manticoretoken]:
- giữ nguyên các chữ có dấu (Latin-1, Latin Extended-A, khối U+1EA0–U+1EF9), chỉ hạ chữ hoa về chữ thường;
- giữ `_` là ký tự của từ;
- kèm `min_word_len='1'`.

Hệ quả là truy vấn "vàng" **không** khớp bài chỉ chứa "giá_vàng". Trường `body_syl` được thêm để thử khắc phục, nhưng không có lợi (Mục 7.5). Ngoài ra, bảng có thêm hai trường `title_fold` và `body_fold` chứa văn bản đã gộp dấu ở Python, dành cho truy vấn gõ không dấu.

### 6.3 Ba chế độ truy vấn

**BM25.** Ranker mặc định của Manticore (`proximity_bm25`) không chuẩn hóa độ dài như BM25 chuẩn [@robertson2009], nên hệ thống chỉ định tường minh:

```sql
SELECT id, WEIGHT() FROM news
WHERE MATCH('@(title_seg,body_seg) (giá_vàng | tăng | mạnh)') AND split = 'train' LIMIT 100
OPTION ranker=expr('10000*bm25a(1.2,0.75)'), idf='plain,tfidf_unnormalized', max_matches=1000;
```

Truy vấn dài (dán cả bài) được rút còn top-50 item theo tf·idf. Nếu để nguyên, số term OR quá lớn và truy vấn chậm.

**Vector.** Ứng dụng suy luận vector truy vấn bằng Doc2Vec (3–5 ms), rồi chạy `SELECT id, knn_dist() FROM news WHERE knn(vec, 400, (…), {ef=400}) AND category_id = 8 LIMIT 100`. Khi có bộ lọc, ứng dụng xin gấp 4 lần số ứng viên để bù phần bị lọc. MariaDB không làm được điều này (Mục 4.3).

**Hybrid.** Hai danh sách top-100 được gộp bằng Reciprocal Rank Fusion [@cormack2009]: điểm(d) = Σ 1/(k + hạng(d)), với k = 60. RRF chỉ dùng thứ hạng, nên không phải chuẩn hóa điểm BM25 (hàng nghìn) với cosine (0–1). Sau đó ứng dụng **khử trùng** bằng `body_md5` lấy từ MariaDB (Mục 3.5). Nếu không khử trùng, top-10 có thể chứa hai, ba bản giống hệt nhau.

### 6.4 Đồng bộ từ MariaDB

`sync_manticore.py` dựng lại bảng theo bốn bước:
1. `DROP` rồi `CREATE TABLE` từ tệp DDL.
2. Đọc `article ⋈ article_vector` bằng con trỏ, 500 dòng mỗi lần.
3. `REPLACE INTO news … VALUES (…), (…)` theo lô.
4. `FLUSH RAMCHUNK`.

Bước 2–3 xử lý 84.132 tài liệu trong **99 giây**, gồm cả tách từ tiêu đề bằng pyvi và gộp dấu. Bảng chiếm khoảng 533 MB. Cuối script, số tài liệu ở Manticore được so với MariaDB; nếu lệch, script thoát với mã lỗi, nên đồng bộ không thể lặng lẽ thành công một nửa. Dùng `REPLACE` thay `INSERT` giúp chạy lại an toàn. Cùng script, với `--table news_fold --charset non_cjk`, dựng bảng gộp dấu cho E-DB5.

Đây là cách **dựng lại toàn bộ**: đơn giản và luôn nhất quán sau khi chạy xong, nhưng không phản ánh ngay các thay đổi lẻ. Mục 9.2 thảo luận phương án tăng dần.
