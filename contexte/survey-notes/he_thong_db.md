# Đoạn chèn vào survey từ hệ thống MariaDB + Manticore (GĐ-H7, 21/10/2026)

**Trạng thái:** ✅ đã chèn vào `livrables/survey/draft/` ở GĐ11 (22/10/2026): §1 → Mục 9.1 và Hình 9.2; §2 → Bảng 9.6 và Mục 2.2; §3 → Bảng 9.4; §4 → đoạn "Đính chính" ở Mục 9.5; §5 → Mục 7.1; §6 → `refs.tsv`.

**Nguồn số liệu:**
- `contexte/results/RESULTS_DB.md`;
- `KE_HOACH_HE_THONG_DB.md`, các Mục 13, 14 và 17.5;
- báo cáo môn CSDL `livrables/report_db/BaoCao_CSDL_Trans2Vec.docx`.

**Quy ước:** khóa trích dẫn theo `livrables/survey/draft/refs.tsv`. Ba khóa mới cần thêm vào đó nằm ở Mục 6. Số hình, số bảng để dạng `9.x`, đánh lại khi ráp.

---

## 1. Thay Hình 9.1 (Mục 9.1, kiến trúc)

**Vị trí:** cuối Mục 9.1, sau sơ đồ ASCII. Có thể thay sơ đồ bằng `livrables/report_db/figures/fig_arch.png`, khi đó phải chép ảnh sang `livrables/survey/figures/`.

> Kiến trúc trên đã được hiện thực thành một hệ thống chạy được, gồm hai hệ lưu trữ với vai trò tách biệt.
> - **MariaDB 11.8** là nguồn dữ liệu gốc: bài báo, transaction (4,15 triệu dòng), tập phổ biến, các lần huấn luyện, vector `VECTOR(128)`, dự đoán, kết quả đánh giá và nhật ký truy vấn.
> - **Manticore Search** là chỉ mục tìm kiếm phái sinh, dựng lại được hoàn toàn từ MariaDB trong khoảng 100 giây. Manticore phục vụ đồng thời BM25 [@robertson2009] và tìm vector bằng HNSW [@malkov2020] trên cùng một bảng, kèm lọc theo chuyên mục.
>
> Mô-đun M7 vì vậy có ba chế độ: từ khóa (BM25), vector (Trans2Vec-JOI) và hybrid gộp hai danh sách bằng Reciprocal Rank Fusion [@cormack2009]. Thiết kế lưu trữ, chỉ mục và các phép đo hiệu năng được trình bày trong báo cáo riêng của môn Hệ cơ sở dữ liệu nâng cao.

---

## 2. RQ6: so sánh BM25, vector và hybrid (bổ sung Mục 9.5, sau Bảng 9.4)

> **Bảng 9.x.** Tìm kiếm trên Manticore (nDCG@10). Giao thức như Bảng 9.4: 1.000 truy vấn, kho 33.759 bài, "liên quan" là cùng chủ đề.
>
> | Phương pháp | Truy vấn là bài báo | Truy vấn 3 từ khóa | 3 từ khóa, có FI (n = 56) | 3 từ khóa, không FI (n = 944) |
> |---|---|---|---|---|
> | BM25 (k1 = 1,2; b = 0,75) | 0,749 | 0,653 | 0,769 | 0,646 |
> | Trans2Vec-JOI (HNSW) | 0,816 | 0,690 | 0,863 | 0,679 |
> | **Hybrid RRF (k = 60)** | **0,819** | **0,704** | **0,870** | **0,694** |
>
> Ba nhận xét bổ sung cho RQ6:
> 1. **BM25 không đổi kết luận của Bảng 9.4.** BM25 ngang TF-IDF cosine (0,749 so với 0,740 với truy vấn là bài báo), và Trans2Vec-JOI vẫn hơn biểu diễn thưa khoảng 7 điểm.
> 2. **Hybrid chỉ có ích rõ với truy vấn ngắn:** +0,014 so với vector và +0,051 so với BM25. Với truy vấn là bài báo, hybrid ngang vector (+0,003). Đổi lại, MAP@100 của hybrid thấp hơn vector (0,525 so với 0,596 với truy vấn ngắn), nên hybrid hợp cho trang top-10 hơn là cho thu hồi sâu.
> 3. **Truy vấn ngắn có chứa FI dễ hơn hẳn**, và ở nhóm này vector hơn BM25 khoảng 0,09. Quan sát này ủng hộ vai trò của FI trong tìm kiếm, nhưng n = 56 nên mới chỉ là gợi ý.
>
> **Về đánh giá chỉ mục vector** (P2, đã duyệt 21/10: dùng recall@10 khi so sánh chỉ mục): khi đổi chỉ mục ANN (HNSW, M và ef khác nhau), recall@10 so với tìm vét cạn thay đổi từ 0,86 đến 1,00, trong khi nDCG@10 theo proxy "cùng chủ đề" chỉ dao động trong khoảng 0,811–0,818. Proxy này không đủ nhạy để so sánh chỉ mục; phải dùng recall so với vét cạn. Đây là thêm một lý do cần tập truy vấn có nhãn liên quan do người gán (hạn chế của giao thức, RQ5).
>
> **Về dấu thanh** (liên hệ Mục 2): đánh chỉ mục giữ dấu tốt hơn gộp dấu với truy vấn có dấu (nDCG@10 0,653 so với 0,621). Với truy vấn gõ không dấu, chỉ mục giữ dấu chỉ còn 0,394 và 9% truy vấn không có kết quả. Hệ thống vì vậy chuyển truy vấn không dấu sang một trường đã gộp dấu, đạt 0,615. Gộp dấu dồn bàn/bán/bản/ban thành một token khớp 63% kho, nên không dùng nó cho truy vấn có dấu.

---

## 3. Bảng 6 mô hình phân loại (bổ sung Mục 9.5, sau Bảng 9.6)

> **Bảng 9.x.** So sánh với mã gốc của tác giả và mô hình kết hợp các biến thể (Macro-F1 trên 50.373 bài test, LR C = 1 trừ dòng đầu)
>
> | Mô hình | Macro-F1 | Accuracy | nDCG@10 tìm kiếm |
> |---|---|---|---|
> | Trans2Vec gốc: mã tác giả, transductive, LinearSVC | 0,823 | 0,852 | 0,762 |
> | TRANS-IT | 0,847 | 0,874 | 0,804 |
> | TRANS-FI | 0,826 | 0,854 | 0,776 |
> | Trans2Vec-IND (trung bình IT và FI) | 0,842 | 0,870 | 0,793 |
> | Trans2Vec-JOI | 0,849 | 0,875 | **0,816** |
> | **Trans2Vec-CAT** (nối IT ‖ FI ‖ JOI) | **0,857** | **0,882** | 0,807 |
>
> **Mốc "Trans2Vec gốc"** chạy đúng quy trình trong mã công bố: Doc2Vec học transductive trên toàn bộ bài, 50 epoch, vector lấy từ `model.dv`, LinearSVC mặc định. Chỉ hai điểm phải đổi:
> - dùng cùng bộ 3.586 FI, vì công cụ khai phá FI của tác giả chỉ chạy trên Windows;
> - đổi tên tham số sang gensim 4.
>
> Mốc đạt 0,823, cao hơn bản inductive dùng `model.dv` ở Bảng 9.3 (0,766), vì khi học transductive, vector train và test cùng phân phối.
>
> **Mô hình CAT** được chọn giữa hai ứng viên (CAT và stacking) bằng kiểm định chéo 3 phần **trên tập train** (0,873 so với 0,866), không nhìn tập test. CAT hơn JOI 0,008 Macro-F1. Mức tăng này nhỏ nhưng nhất quán với nhận định rằng mỗi biến thể nhìn bài báo từ một góc khác nhau. Ở tìm kiếm thì CAT lại kém JOI (0,807 so với 0,816), nên tìm kiếm vẫn dùng JOI. Khoảng cách với TF-IDF (0,907) vẫn còn khoảng 0,05.

---

## 4. Đính chính về FI đóng (giả thuyết A3, Mục 9.3, và RESULTS.md mục H2)

> Với cấu hình chính (k = 50, δ = 0,535%, FI dài tối đa 3), **mọi FI đều là FI đóng**. Điều này được kiểm chứng độc lập bằng hai cách:
> - lọc FI đóng trong Python;
> - một truy vấn SQL tìm FI có tập cha trực tiếp cùng support, kết quả rỗng.
>
> Lý do: support tối thiểu là 181 bài và FI rất ngắn, nên không có tập con nào trùng support với tập cha. Hệ quả:
> 1. Chênh lệch 0,770 so với 0,766 ở ablation A3 là dao động ngẫu nhiên, không phải tác dụng của việc lọc FI đóng.
> 2. Muốn kiểm chứng giả thuyết về FI đóng thì phải hạ δ hoặc tăng độ dài FI tối đa.
> 3. Câu "Top-k ≈ 50 và FI đóng là đủ" cần sửa thành "Top-k ≈ 50 là đủ; ở cấu hình này lọc FI đóng không có tác dụng vì mọi FI đều đóng".

---

## 5. Ghi chú bài trùng trong VNTC (Mục 7, giao thức đánh giá, RQ5)

> Khi đưa VNTC-10 vào CSDL và đánh chỉ mục theo hash nội dung, phát hiện có 3.415 nhóm bài trùng y hệt, gồm 8.399 bài, tức 4.984 bản thừa.
> - 2.522 nhóm có mặt ở cả train lẫn test: **3.056 bài test (6,1%) có bản sao trong tập train**.
> - 380 nhóm mang nhãn chuyên mục khác nhau, tức là nhiễu nhãn.
>
> Ảnh hưởng tới phân loại không đáng kể. Bỏ 3.056 bài đó thì Macro-F1 gần như không đổi: Trans2Vec-JOI 0,8498 so với 0,8488, TF-IDF 0,9063 so với 0,9065. Ngay trên chính các bài trùng, Macro-F1 còn thấp hơn (0,765), một phần do nhiễu nhãn. Dù vậy, đây là rò rỉ train–test mà các công trình dùng VNTC [@hoang2007] chưa đề cập. Một giao thức chuẩn nên khử trùng trước khi chia, và hệ thống tìm kiếm phải khử trùng khi hiển thị kết quả.

---

## 6. Tài liệu cần thêm vào `livrables/survey/draft/refs.tsv`

Cả ba đã xác minh qua Crossref ngày 21/10/2026 và cũng có trong `livrables/report_db/draft/refs.tsv`.

```
robertson2009	S. Robertson and H. Zaragoza, "The probabilistic relevance framework: BM25 and beyond," *Foundations and Trends in Information Retrieval*, vol. 3, no. 4, pp. 333–389, 2009, doi: 10.1561/1500000019.
malkov2020	Y. A. Malkov and D. A. Yashunin, "Efficient and robust approximate nearest neighbor search using hierarchical navigable small world graphs," *IEEE Trans. Pattern Anal. Mach. Intell.*, vol. 42, no. 4, pp. 824–836, 2020, doi: 10.1109/TPAMI.2018.2889473.
cormack2009	G. V. Cormack, C. L. A. Clarke, and S. Büttcher, "Reciprocal rank fusion outperforms Condorcet and individual rank learning methods," in *Proc. 32nd Int. ACM SIGIR Conf. Research and Development in Information Retrieval*, 2009, pp. 758–759, doi: 10.1145/1571941.1572114.
```
