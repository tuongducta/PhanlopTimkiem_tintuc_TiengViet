## 7. Thực nghiệm

### 7.1 Giao thức chung

Các thực nghiệm dùng cùng giao thức với phần tìm kiếm của bài khảo sát, để hai phần so sánh được với nhau:
- **Kho:** 33.759 bài train.
- **Truy vấn:** 1.000 bài test, mỗi chuyên mục 100 bài (seed 0), ở hai dạng:
  - **doc:** 50 item có tf·idf cao nhất của bài, mô phỏng "tìm bài tương tự";
  - **kw:** 3 item cao nhất, mô phỏng truy vấn từ khóa ngắn.
- **Độ liên quan:** bài cùng chuyên mục với truy vấn. Đây là proxy (xem Mục 9.1).
- **Độ đo:**
  - chất lượng: P@10, MAP@100, nDCG@10; với chỉ mục vector thêm recall@10 so với tìm vét cạn;
  - hiệu năng: độ trễ p50/p95 đo từ client Python trên cùng máy, QPS khi chạy 4 luồng, thời gian dựng và dung lượng chỉ mục.

E-DB3 (khai phá FI bằng SQL) và E-DB6 (ghi kép có lỗi) đã bỏ khỏi phạm vi khi chốt kế hoạch. Mã nguồn ở `src/system/bench/`, số liệu gốc ở `src/system/bench/results/`.

### 7.2 E-DB1: InnoDB FULLTEXT so với Manticore BM25

**Thiết lập:** cùng cột `body_seg`. InnoDB dùng `NATURAL LANGUAGE MODE`, đã chỉnh như Mục 4.2. Manticore dùng BM25 với k1 = 1,2 và b = 0,75.

**Bảng 7.1.** Kết quả E-DB1

| Engine | Truy vấn | P@10 | MAP@100 | nDCG@10 | p50 (ms) | p95 (ms) | QPS (4 luồng) |
|---|---|---|---|---|---|---|---|
| InnoDB | kw | 0,595 | 0,401 | 0,596 | 8,8 | 44,9 | 240 |
| Manticore | kw | 0,643 | 0,419 | **0,655** | **1,2** | 2,7 | **2.498** |
| InnoDB | doc | 0,600 | 0,436 | 0,597 | 213,1 | 355,8 | 14 |
| Manticore | doc | 0,733 | 0,550 | **0,739** | **11,1** | 17,7 | **244** |

![Hình 7.1. E-DB1: chất lượng (trái) và độ trễ p50 thang log (phải).](figures/fig_edb1.png){width=85%}

**Nhận xét:**
- **Manticore tốt hơn cả về chất lượng lẫn tốc độ.** nDCG@10 cao hơn 0,06 (kw) và 0,14 (doc); độ trễ thấp hơn 7–19 lần. Chi phí dựng chỉ mục của hai bên gần nhau: InnoDB 28,2 s, 135 MB; Manticore 22,2 s, 113 MB.
- **Khoảng cách chất lượng lớn nhất ở truy vấn dài.** BM25 chuẩn hóa độ dài văn bản (b) và bão hòa tần suất từ (k1). InnoDB không làm hai việc này, nên bài dài chứa nhiều từ phổ biến dễ được xếp cao.
- **Với truy vấn dài, InnoDB chỉ đạt 14 QPS**, không dùng được cho tính năng "bài tương tự". Tìm kiếm xếp hạng nên giao cho engine chuyên dụng.

### 7.3 E-DB2: Chỉ mục vector MariaDB MHNSW so với Manticore HNSW

**Thiết lập:**
- 33.759 vector Trans2Vec-JOI 128 chiều, khoảng cách cosine.
- M ∈ {6, 16}, ef ∈ {10, 20, 40, 100, 200}.
- Chân lý: top-10 vét cạn bằng numpy (nDCG@10 = 0,8158; 1,9 ms mỗi truy vấn khi tính theo lô).

**Bảng 7.2.** Recall@10 và độ trễ p50 (M = 16)

| ef | MariaDB | Manticore |
|---|---|---|
| 10 | 0,985 · 0,53 ms | 0,929 · 0,85 ms |
| 40 | **0,997 · 0,46 ms** | 0,940 · 0,59 ms |
| 200 | 1,000 · 0,74 ms | 0,987 · 0,61 ms |

![Hình 7.2. E-DB2: recall@10 theo ef. Nét liền là M = 16, nét đứt là M = 6.](figures/fig_edb2.png){width=75%}

**Nhận xét:**
- **Ở cùng M và ef, MariaDB cho recall cao hơn rõ rệt.** Manticore cần ef = 200 mới đạt 0,987. Ở Manticore, ef = 10 và ef = 20 cho kết quả trùng nhau hoàn toàn; có thể engine áp một ngưỡng ef tối thiểu, nhưng tài liệu chưa xác nhận điều này.
- **Chi phí dựng:** MariaDB 1,7 s (M = 6) và 7,1 s (M = 16), dung lượng 52–58 MB gồm cả dữ liệu. Manticore 7,1–8,4 s, 38–41 MB.
- **Độ trễ của cả hai đều dưới 1 ms**, nhỏ hơn nhiều thời gian suy luận vector truy vấn (3–5 ms). Nút cổ chai nằm ở mô hình chứ không ở chỉ mục. Ở quy mô này, quét toàn bảng trong MariaDB cũng chỉ mất 7 ms.
- **nDCG@10 của mọi cấu hình nằm trong khoảng 0,811–0,818**, vì proxy "cùng chuyên mục" ít nhạy với việc lấy nhầm vài láng giềng. Khi so sánh chỉ mục ANN, độ đo đúng là recall so với vét cạn.

**Lựa chọn cho hệ thống: Manticore**, dù recall thấp hơn. Lý do là BM25 và vector nằm cùng một bảng, có lọc thuộc tính, và lấy top-k trong một truy vấn. Cấu hình đang dùng (M = 16, ef = 400) đạt recall ≥ 0,99. Nếu cần tìm kiếm thuần SQL, MariaDB với M = 16, ef = 40 là lựa chọn rất tốt.

### 7.4 E-DB4: Hybrid BM25 + vector

**Thiết lập:** bảng `news` của Manticore. RRF dùng k = 60, mỗi nguồn đóng góp d = 100 ứng viên. Số liệu đo sau khi thêm trường gộp dấu (Mục 7.5); so với lần đo trước đó, nDCG@10 lệch không quá 0,005.

**Bảng 7.3.** Kết quả E-DB4. Độ trễ của vector gồm cả thời gian suy luận.

| Truy vấn | Phương pháp | P@10 | MAP@100 | nDCG@10 | p50 (ms) |
|---|---|---|---|---|---|
| kw | BM25 | 0,640 | 0,423 | 0,653 | 1,8 |
| kw | Vector (JOI) | 0,688 | **0,596** | 0,690 | 5,2 |
| kw | **Hybrid RRF** | **0,698** | 0,525 | **0,704** | 6,9 |
| doc | BM25 | 0,744 | 0,558 | 0,749 | 10,0 |
| doc | Vector (JOI) | 0,809 | **0,682** | 0,816 | 8,4 |
| doc | **Hybrid RRF** | **0,812** | 0,639 | **0,819** | 18,4 |

![Hình 7.3. E-DB4: nDCG@10; truy vấn kw được tách theo có hay không chứa FI độ dài ≥ 2.](figures/fig_edb4.png){width=85%}

**Nhận xét:**
- **Hybrid cho P@10 và nDCG@10 cao nhất.** Lợi ích rõ ở truy vấn ngắn: +0,014 so với vector và +0,051 so với BM25. Với truy vấn dài, hybrid gần như ngang vector (+0,003).
- **MAP@100 của hybrid thấp hơn vector** (0,525 so với 0,596 với kw), vì BM25 kéo bài sai chuyên mục vào phần đuôi. Hybrid hợp cho trang top-10; nếu cần thu hồi sâu thì vector tốt hơn.
- **Độ nhạy theo tham số:** d = 20 kém d = 100 (kw 0,687 so với 0,704); k = 60 và k = 200 gần như ngang nhau.
- **Truy vấn kw có chứa FI (56/1.000) dễ hơn hẳn**, và ở nhóm này vector hơn BM25 khoảng 0,09. Kết quả khớp lập luận của bài khảo sát, nhưng n nhỏ nên mới chỉ là gợi ý.
- **Độ trễ của hybrid gần bằng tổng hai nhánh.** Khi lọc theo chuyên mục, gồm cả tách từ, p50 là 1,1 ms với BM25, 3,3 ms với vector và 7,8 ms với hybrid. Có thể giảm độ trễ bằng cách chạy song song hai nhánh.

### 7.5 E-DB5: Giữ dấu hay gộp dấu

**Thiết lập:** bốn cấu hình BM25, thêm một bộ truy vấn kw đã bỏ dấu để mô phỏng người dùng gõ không dấu.
- (a) bảng riêng `news_fold` dùng `non_cjk`: gộp dấu, `_` là dấu tách.
- (b) bảng `news`: giữ dấu và giữ từ ghép.
- (c) như (b), khớp thêm âm tiết trên `body_syl`.
- (d) trường `title_fold`, `body_fold` trong chính bảng `news`. Văn bản được gộp dấu ở Python (bỏ dấu, đ→d) trước khi đánh chỉ mục, vì `charset_table` áp cho cả bảng.

Cấu hình (d) được thêm sau lần đo đầu, theo kết quả của chính thực nghiệm này.

**Bảng 7.4.** Kết quả E-DB5 (nDCG@10, p50 tính bằng ms)

| Cấu hình | kw có dấu | kw không dấu | Truy vấn rỗng (kw không dấu) | doc | p50 doc |
|---|---|---|---|---|---|
| (a) bảng gộp dấu | 0,621 | 0,607 | 0% | 0,665 | 45,2 |
| **(b) giữ dấu** | **0,653** | 0,394 | **9%** | **0,749** | **11,0** |
| (c) giữ dấu + âm tiết | 0,651 | 0,398 | 0% | 0,632 | 71,3 |
| (d) trường gộp dấu | 0,615 | **0,615** | 0% | 0,664 | 36,4 |

![Hình 7.4. E-DB5: nDCG@10 theo cách xử lý dấu.](figures/fig_edb5.png){width=85%}

**Nhận xét:**
- **Gộp dấu gây nhập nhằng nghiêm trọng.** "bàn", "bán", "bản", "ban" khi giữ dấu khớp lần lượt 3.520, 4.183, 1.946 và 3.687 bài. Với `non_cjk`, cả bốn thành một token khớp 21.316 bài (63% kho). Riêng "bạn" vẫn tách riêng: `non_cjk` không gộp "ạ", tức việc gộp dấu của cấu hình mặc định không đều.
- **Với truy vấn có dấu, giữ dấu tốt hơn và nhanh hơn.** So với (a), kw tăng 0,032 và doc tăng 0,084, doc nhanh hơn 4 lần. Khớp thêm âm tiết (c) không có lợi, và với truy vấn dài còn chậm gấp 6 lần.
- **Với truy vấn không dấu, bảng giữ dấu gần như hỏng:** nDCG 0,39, 9% truy vấn rỗng. Trường gộp dấu (d) đạt 0,615, nhỉnh hơn bảng riêng (a). Dung lượng chỉ tăng 143 MB (bảng `news` từ 390 lên 533 MB), thay vì thêm một bảng 391 MB.
- **Hệ thống chọn nhánh tự động:** truy vấn có ít nhất một chữ có dấu đi (b); truy vấn không có dấu nào đi (d). Đo đầu-cuối với 1.000 truy vấn gõ tự do không dấu (không biết từ ghép), nDCG@10 tăng từ 0,399 lên 0,534. Ở chế độ hybrid, vector suy luận từ chữ không dấu kéo kết quả xuống 0,473, nên hybrid bỏ nhánh vector khi truy vấn không dấu.
- **Tác dụng phụ:** sau khi thêm hai trường, điểm của (b) và (c) cũng đổi nhẹ. Với truy vấn có dấu, mức lệch không quá 0,003; với (b) trên truy vấn không dấu, nDCG tăng từ 0,362 lên 0,394. Giả thuyết là Manticore tính idf của một từ trên toàn bảng, không theo trường, nên token không dấu trong `body_fold` làm đổi trọng số ở các trường khác. Giả thuyết này chưa được kiểm chứng riêng. Muốn tách hẳn thống kê thì phải dùng bảng riêng như (a), với cái giá gần gấp ba dung lượng tăng thêm.
