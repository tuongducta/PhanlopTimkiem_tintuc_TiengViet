# Kết quả thực nghiệm phía CSDL (GĐ-H6, 20/10/2026)

## Giao thức chung

Giao thức giống GĐ6 (`src/experiments/`) để hai phần so sánh được với nhau:
- **Truy vấn:** 1.000 bài test (100 bài mỗi chuyên mục, rng seed 0).
- **Kho tìm kiếm:** 33.759 bài train.
- **Bài liên quan:** bài cùng chuyên mục với truy vấn.
- **Hai loại truy vấn:**
  - `doc`: 50 item có tf·idf cao nhất của bài.
  - `kw`: 3 item có tf·idf cao nhất (như A6).
- **Độ đo chất lượng:** P@10, MAP@100, nDCG@10.
- **Độ trễ:** đo từ client Python (pymysql) trên cùng máy, nên đã gồm chi phí mạng loopback.
- **Phiên bản:** MariaDB 11.8.9, Manticore 29.9.0, cả hai chạy Docker trên macOS.

Số liệu gốc nằm ở `src/system/bench/results/*.json`, log ở `src/system/bench/*.log`.

---

## E-DB1: InnoDB FULLTEXT so với Manticore (cùng cột `body_seg`)

InnoDB được chỉnh để công bằng hơn: `innodb_ft_min_token_size=1`, tắt stopword. Chế độ `NATURAL LANGUAGE MODE`.

| Engine | Truy vấn | P@10 | MAP@100 | nDCG@10 | p50 (ms) | p95 (ms) | QPS (4 luồng) |
|---|---|---|---|---|---|---|---|
| InnoDB | kw | 0,595 | 0,401 | 0,596 | 8,8 | 44,9 | 240 |
| Manticore | kw | 0,643 | 0,419 | **0,655** | **1,2** | 2,7 | **2.498** |
| InnoDB | doc | 0,600 | 0,436 | 0,597 | 213,1 | 355,8 | 14 |
| Manticore | doc | 0,733 | 0,550 | **0,739** | **11,1** | 17,7 | **244** |

Chi phí dựng chỉ mục:

| Engine | Thời gian dựng | Dung lượng |
|---|---|---|
| InnoDB | 28,2 s | 135 MB |
| Manticore | 22,2 s | 113 MB |

**Nhận xét:**
- Manticore tốt hơn về chất lượng: nDCG@10 hơn 0,06 với kw và 0,14 với doc. Nguyên nhân là BM25 chuẩn, có chuẩn hóa độ dài, trong khi InnoDB xếp hạng theo kiểu tf·idf riêng.
- Manticore nhanh hơn 7–19 lần.
- Với truy vấn dài (doc, 50 từ), InnoDB chỉ đạt 14 QPS nên không dùng được cho tìm kiếm tương tự bài.

---

## E-DB2: Vector, MariaDB MHNSW so với Manticore HNSW

- **Dữ liệu:** 33.759 vector Trans2Vec-JOI (128 chiều), 1.000 truy vấn.
- **Chân lý:** top-10 cosine chính xác tính bằng numpy.
- **Mốc so sánh:** numpy vét cạn cho nDCG@10 = 0,8158, MAP@100 = 0,6808, 1,9 ms mỗi truy vấn (nhân ma trận theo lô).

Recall@10 (so với tìm vét cạn) và p50:

| ef | MariaDB M=6 | Manticore M=6 | MariaDB M=16 | Manticore M=16 |
|---|---|---|---|---|
| 10 | 0,877 · 0,44 ms | 0,860 · 0,78 ms | 0,985 · 0,53 ms | 0,929 · 0,85 ms |
| 20 | 0,937 · 0,34 ms | 0,860 · 0,45 ms | 0,993 · 0,46 ms | 0,929 · 0,56 ms |
| 40 | 0,969 · 0,36 ms | 0,888 · 0,52 ms | **0,997 · 0,46 ms** | 0,940 · 0,59 ms |
| 100 | 0,988 · 0,57 ms | 0,956 · 0,51 ms | 1,000 · 0,50 ms | 0,966 · 0,52 ms |
| 200 | 0,995 · 0,49 ms | 0,983 · 0,59 ms | 1,000 · 0,74 ms | 0,987 · 0,61 ms |

Chi phí dựng và lưu trữ:

| Cấu hình | Thời gian dựng | Dung lượng |
|---|---|---|
| MariaDB M=6 | 1,7 s | 52 MB (gồm dữ liệu và chỉ mục) |
| MariaDB M=16 | 7,1 s | 58 MB |
| Manticore M=6 | 7,1 s | 38 MB, RAM 18 MB |
| Manticore M=16 | 8,4 s | 41 MB, RAM 18 MB |
| MariaDB không chỉ mục (quét toàn bảng) | — | recall 1,0, p50 7,1 ms, p95 8,0 ms (đo 100 truy vấn) |

**Nhận xét:**
- **Chất lượng tìm kiếm gần như không phụ thuộc chỉ mục.** nDCG@10 của mọi cấu hình nằm trong khoảng 0,811–0,818, lệch so với vét cạn không quá 0,005. Lý do: proxy "cùng chuyên mục" ít nhạy với việc lấy nhầm một vài hàng xóm gần nhất. Recall@10 vì vậy là độ đo phù hợp hơn để so sánh hai engine.
- **Với cùng M và ef, MariaDB MHNSW cho recall cao hơn Manticore.** M=16, ef=40 đạt recall 0,997 ở 0,46 ms. Manticore cần ef=200 mới tới 0,987.
- **Ở Manticore, ef=10 và ef=20 cho kết quả trùng nhau hoàn toàn.** Có thể engine áp một ngưỡng ef tối thiểu, nhưng điều này chưa được kiểm chứng trong tài liệu.
- **MAP@100 gần như không đổi theo ef.** Với LIMIT 100, script đặt ef = max(ef, 100).
- **Độ trễ của cả hai engine dưới 1 ms**, nhỏ hơn nhiều so với infer_vector của gensim (khoảng 3–5 ms, xem E-DB4). Nút cổ chai vì thế nằm ở mô hình chứ không ở chỉ mục.
- **Ở quy mô 34 nghìn vector, quét toàn bảng cũng chỉ mất 7 ms.** Chỉ mục vector mới thật sự cần khi kho lớn hơn hoặc tải cao.
- **Chọn cho hệ thống:** Manticore, để BM25 và vector nằm cùng một bảng, có lọc và lấy được top-k trong một truy vấn. Cấu hình M=16, ef=400 (dùng ở GĐ-H4) đạt recall ≥ 0,99. MariaDB giữ vai trò nguồn gốc của vector (`article_vector`); nếu cần một phương án tìm kiếm thuần SQL thì MariaDB với M=16, ef=40 là lựa chọn rất tốt.

---

## E-DB4: Hybrid BM25 + vector (RRF)

Mọi phương pháp chạy trên Manticore `news`, lọc `split='train'`.
- **bm25:** BM25 k1=1,2, b=0,75 trên `title_seg`, `body_seg`.
- **knn:** infer_vector trên item và FI của truy vấn, sau đó HNSW với ef=400.
- **RRF:** gộp hai danh sách theo hạng; *d* là số kết quả lấy từ mỗi nguồn trước khi gộp.

Số liệu dưới đây đo lại ngày 21/10, sau khi bảng `news` có thêm trường gộp dấu (P1, xem E-DB5). So với lần đo đầu (`results/edb4_hybrid_before_p1.json`), mọi nDCG@10 lệch không quá 0,005 và các kết luận giữ nguyên. Nguyên nhân lệch có lẽ là Manticore tính idf trên cả bảng chứ không theo trường (xem E-DB5); điều này chưa được kiểm chứng riêng.

| Truy vấn | Phương pháp | P@10 | MAP@100 | nDCG@10 | p50 (ms) |
|---|---|---|---|---|---|
| kw | bm25 | 0,640 | 0,423 | 0,653 | 1,8 |
| kw | knn (JOI) | 0,688 | **0,596** | 0,690 | 5,2 (gồm infer) |
| kw | **hybrid k=60, d=100** | **0,698** | 0,525 | **0,704** | 6,9 |
| doc | bm25 | 0,744 | 0,558 | 0,749 | 10,0 |
| doc | knn (JOI) | 0,809 | **0,682** | 0,816 | 8,4 |
| doc | **hybrid k=60, d=100** | **0,812** | 0,639 | **0,819** | 18,4 |

**Độ nhạy theo k và d (nDCG@10):**

| d | k=10 kw | k=10 doc | k=60 kw | k=60 doc | k=200 kw | k=200 doc |
|---|---|---|---|---|---|---|
| 20 | 0,687 | 0,795 | 0,687 | 0,796 | 0,687 | 0,796 |
| 100 | 0,691 | 0,803 | 0,704 | 0,819 | 0,704 | 0,819 |

- d=20 kém hơn d=100.
- k=60 và k=200 gần như ngang nhau; k=10 kém hơn.
- MAP@100 ở d=20 rất thấp (0,21–0,25) chỉ vì danh sách gộp có tối đa 40 bài. Đây là hệ quả của cách đo, không phải chất lượng xếp hạng.

**Tách truy vấn kw theo việc có chứa FI độ dài ≥ 2 hay không (nDCG@10):**

| Tập | n | bm25 | knn | hybrid k=60, d=100 |
|---|---|---|---|---|
| có FI | 56 | 0,769 | 0,863 | **0,870** |
| không FI | 944 | 0,646 | 0,679 | **0,694** |

**Độ trễ khi lọc theo chuyên mục** (kw, gọi `search()` đầy đủ, gồm tách từ pyvi): bm25 1,1 ms, knn 3,3 ms, hybrid 7,8 ms (p50).

**Nhận xét:**
- Hybrid cho P@10 và nDCG@10 cao nhất ở cả hai loại truy vấn.
- Lợi ích rõ ở truy vấn ngắn: kw tăng 0,014 so với knn và 0,051 so với bm25. Với truy vấn dài, hybrid gần như ngang knn (+0,003).
- **Đổi lại, MAP@100 của hybrid thấp hơn knn.** Phần đuôi danh sách bị các bài BM25 kém kéo xuống. Hybrid hợp cho trang kết quả top-10; nếu cần thu hồi sâu thì knn vẫn tốt hơn.
- Truy vấn kw có FI (5,6%) dễ hơn hẳn, và ở nhóm này knn hơn bm25 khoảng 0,09. Điều này khớp xu hướng Bảng 3 của GĐ6, nhưng n = 56 nên chỉ là quan sát.
- Hybrid tốn độ trễ gần bằng tổng hai nhánh (khoảng 7–18 ms), vẫn dưới mức người dùng cảm nhận được.

---

## E-DB5: Giữ dấu hay gộp dấu trong Manticore (BM25)

Bốn cấu hình:
- **(a) fold:** bảng `news_fold`, `charset_table='non_cjk'`. Dấu bị gộp, `_` là dấu tách, nên từ ghép được tìm như cụm âm tiết.
- **(b) vi:** bảng `news`, charset giữ dấu và giữ `_`.
- **(c) vi+syl:** như (b) và khớp thêm âm tiết trên `body_syl`.
- **(d) vi-fold (P1, đã triển khai 21/10):** trường `title_fold`, `body_fold` trong chính bảng `news`. Văn bản được gộp dấu bằng `src/system/vi_text.fold()` trước khi đánh chỉ mục, vì `charset_table` áp cho cả bảng. Từ ghép khớp dạng cụm như (a). Hệ thống tự dùng nhánh này khi truy vấn không có dấu nào (`Searcher.bm25_fold`).

Số liệu đo lại ngày 21/10, sau khi thêm trường gộp dấu vào `news`.

| Truy vấn | Cấu hình | P@10 | MAP@100 | nDCG@10 | Truy vấn rỗng | p50 (ms) | p95 (ms) |
|---|---|---|---|---|---|---|---|
| kw (có dấu) | (a) fold | 0,607 | 0,382 | 0,621 | 0% | 4,0 | 8,6 |
| kw (có dấu) | **(b) vi** | **0,640** | **0,423** | **0,653** | 0% | 2,2 | 6,4 |
| kw (có dấu) | (c) vi+syl | 0,636 | 0,415 | 0,651 | 0% | 3,6 | 8,5 |
| kw (có dấu) | (d) vi-fold | 0,600 | 0,377 | 0,615 | 0% | 3,2 | 5,8 |
| kw không dấu | (a) fold | 0,594 | 0,374 | 0,607 | 0% | 3,2 | 6,5 |
| kw không dấu | (b) vi | 0,387 | 0,227 | 0,394 | **9%** | 1,1 | 2,6 |
| kw không dấu | (c) vi+syl | 0,394 | 0,232 | 0,398 | 0% | 2,8 | 5,3 |
| kw không dấu | **(d) vi-fold** | **0,600** | **0,377** | **0,615** | 0% | 2,7 | 4,8 |
| doc | (a) fold | 0,660 | 0,439 | 0,665 | 0% | 45,2 | 76,6 |
| doc | **(b) vi** | **0,744** | **0,558** | **0,749** | 0% | 11,0 | 18,3 |
| doc | (c) vi+syl | 0,627 | 0,420 | 0,632 | 0% | 71,3 | 126,4 |
| doc | (d) vi-fold | 0,659 | 0,436 | 0,664 | 0% | 36,4 | 50,9 |

**Đầu-cuối với truy vấn gõ tự do** (1.000 truy vấn kw đã bỏ dấu, gõ cách nhau bằng dấu cách nên không biết từ ghép, đi qua `Searcher.search()`; nDCG@10):

| Đường đi | nDCG@10 |
|---|---|
| Trước P1: pyvi → BM25 trên trường giữ dấu | 0,399 |
| Sau P1, chế độ bm25 (trường gộp dấu) | **0,534** |
| Sau P1, chế độ hybrid (bỏ nhánh vector khi không dấu) | **0,534** |
| Sau P1, chế độ knn | 0,354 |

Kết quả thấp hơn cấu hình (d) trong bảng trên (0,615), vì truy vấn gõ tự do không còn thông tin từ ghép để khớp theo cụm. Trong lần đo thử, nếu hybrid giữ nhánh vector thì chỉ đạt 0,473: vector suy luận từ chữ không dấu kéo kết quả lạc đề. Vì vậy hybrid bỏ nhánh vector khi truy vấn không dấu.

**Dung lượng:**
- `news` tăng từ khoảng 390 MB lên 533 MB (+143 MB) khi thêm hai trường gộp dấu.
- Giữ riêng bảng `news_fold` thì tốn 391 MB.

**Nhập nhằng khi gộp dấu** (số bài train khớp từ):

| Từ | bàn | bán | bản | ban | bạn |
|---|---|---|---|---|---|
| Giữ dấu (`body_seg`) | 3.520 | 4.183 | 1.946 | 3.687 | 6.410 |
| Gộp dấu `non_cjk` (`news_fold`) | 21.316 | 21.316 | 21.316 | 21.316 | 7.397 |
| Gộp dấu `fold()` (`body_fold`, âm tiết) | 23.788 | 23.788 | 23.788 | 23.788 | 23.788 |

Trên `news_fold`, `bạn` vẫn khác các từ còn lại, có vẻ do `non_cjk` không gộp `ạ` (U+1EA1) về `a`. `fold()` gộp đều cả năm từ. Con số cao hơn vì `body_fold` chứa âm tiết, nên "ban" khớp cả âm tiết trong từ ghép.

**Nhận xét:**
- **Với truy vấn có dấu, giữ dấu tốt hơn và nhanh hơn.** kw tăng 0,032, doc tăng 0,084, và doc nhanh hơn 4 lần. Lý do: gộp dấu gom 4–5 từ khác nghĩa thành một token, và từ ghép phải khớp theo cụm.
- Khớp thêm âm tiết (c) không giúp gì mà còn làm hại truy vấn dài.
- **Với truy vấn không dấu, giữ dấu gần như hỏng:** nDCG còn 0,39, 9% truy vấn rỗng. **Nhánh (d) đạt 0,615**, nhỉnh hơn bảng riêng (a) 0,607, và chỉ tốn thêm 143 MB thay vì 391 MB.
- **Hệ thống hiện chọn tự động:** truy vấn có dấu đi (b), truy vấn không dấu đi (d). Như vậy, với bộ truy vấn này, hệ thống đạt 0,653 cho kw có dấu và 0,615 cho kw không dấu.
- **Tác dụng phụ:** sau khi thêm trường gộp dấu, (b) và (c) đổi nhẹ so với lần đo đầu (kw có dấu 0,654 → 0,653; doc 0,746 → 0,749; kw không dấu với (b) 0,362 → 0,394). Giả thuyết là Manticore tính idf của một từ trên toàn bảng, không tách theo trường; âm tiết không dấu trong `body_fold` làm tăng df của các token không dấu. Giả thuyết này chưa được kiểm chứng riêng. Nếu muốn tách hẳn thống kê, phải dùng bảng riêng như (a).
- Bảng `news_fold` giờ chỉ còn dùng cho thực nghiệm này và có thể xóa.

---

## Tóm tắt cho báo cáo môn CSDL

1. **Full-text:** Manticore tốt hơn InnoDB FULLTEXT cả về chất lượng (nDCG@10 hơn 0,06–0,14) lẫn tốc độ (7–19 lần), đúng với vai trò engine tìm kiếm chuyên dụng.
2. **Vector:** chỉ mục vector của MariaDB 11.8 cho recall cao hơn Manticore ở cùng tham số, độ trễ của cả hai dưới 1 ms. Thời gian infer của mô hình mới là nút cổ chai.
3. **Hybrid:** RRF với k=60, d=100 cho top-10 tốt nhất. Lợi ích rõ nhất ở truy vấn ngắn; đổi lại MAP@100 thấp hơn so với chỉ dùng vector.
4. **Tiếng Việt:** giữ dấu là cấu hình mặc định đúng cho truy vấn có dấu. Truy vấn không dấu cần một nhánh gộp dấu riêng; nhánh này đã có (trường `body_fold`, nDCG@10 0,615 so với 0,394).
