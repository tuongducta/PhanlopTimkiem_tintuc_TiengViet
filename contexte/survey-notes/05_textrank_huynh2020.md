# [5] Automatic Keywords-based Classification of Vietnamese Texts

> **Vai trò:** Phân loại chỉ dựa trên **tập từ khóa** (TextRank + Jaccard), về bản chất là biểu diễn văn bản như một **tập item** · Taxonomy **B3** · Chương 4, 5.5

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | H. T. Huynh, N. Duong-Trung, X. S. Ha, N. Q. T. Tang, H. X. Huynh, and D. Q. Truong, "Automatic keywords-based classification of Vietnamese texts," in *Proc. 2020 RIVF Int. Conf. Computing and Communication Technologies (RIVF)*, 2020, pp. 1–3, doi: 10.1109/RIVF48685.2020.9140761. *(Đã xác minh qua Crossref, 08/10/2026. Bài mời; bản mở rộng: "Vietnamese text classification with TextRank and Jaccard similarity coefficient," ASTESJ, vol. 5, no. 6, pp. 363–369, 2020, doi: 10.25046/aj050644.)* |
| Đơn vị | ĐH Cần Thơ, ĐH FPT Cần Thơ, NTUST (Đài Loan) |
| File | `[5] VN-KeywordsClassification-TextRank-huynh2020.pdf` (3 trang) |

## 2. Động lực
- Con người phân loại tài liệu bằng cách **lướt các từ quan trọng**, không đọc toàn văn. Vì vậy chỉ cần trích từ khóa đại diện là đủ để xác định chủ đề.
- Tác giả cho rằng đây là lần đầu phân loại văn bản tiếng Việt bằng từ khóa đại diện.

## 3. Phương pháp
1. **Trích từ khóa bằng TextRank** (Mihalcea & Tarau, 2004): đồ thị đồng xuất hiện từ trong cửa sổ N; điểm đỉnh $S(V_i) = (1-d) + d\sum_{j\in In(V_i)} \frac{1}{|Out(V_j)|}S(V_j)$, d = 0,85; lấy top-T.
2. **Mỗi chủ đề** có một bộ từ khóa đại diện, xây từ dữ liệu train.
3. **Phân loại:** so khớp từ khóa của văn bản mới với bộ từ khóa của từng chủ đề bằng **Jaccard có trọng số theo thứ hạng (top-weighted)**: $JD(R_i,R_j)=\frac{1}{T}\sum_{d=1}^{T}\frac{|R_{i,d}\cap R_{j,d}|}{|R_{i,d}\cup R_{j,d}|}$.

## 4. Dữ liệu và kết quả
- 15 chủ đề (âm nhạc, ẩm thực, du lịch, …) từ vnexpress, dantri, tuoitre, yahoo; thu thập bằng Teleport Pro. **200 train + 100 test mỗi chủ đề**, tổng 4.500 file.

| # từ khóa | Accuracy (%) | Train (s) | Test (s) |
|---|---|---|---|
| 10 | 75,27 | 2.155 | 1.111 |
| 20 | 85,87 | 2.162 | 1.114 |
| 30 | 88,53 | 2.178 | 1.116 |
| 50 | 90,07 | 2.199 | 1.120 |
| 70 | 90,07 | 2.307 | 1.125 |
| tất cả | **95,40** | 9.279 | 1.362 |

## 5. Hạn chế và phản biện
- Dataset nhỏ, cân bằng hoàn hảo, 15 chủ đề tách biệt.
- **Không có baseline** (không so với TF-IDF + SVM). Không báo P/R/F1 dù có định nghĩa.
- Không nói rõ có tách từ hay không.
- Bài 3 trang; chưa xác định được venue.
- Khi dùng tất cả từ khóa (95,4%), phương pháp tiến gần BoW, nên lợi ích của "chỉ dùng từ khóa" không rõ ràng ngoài việc tiết kiệm.

## 6. Liên hệ với đề tài / Trans2Vec
- **Văn bản biểu diễn như một *tập* từ khóa và đo tương đồng bằng Jaccard (phép toán tập hợp)** chính là góc nhìn "văn bản = transaction" của [13]. [5] là **cầu nối khái niệm** giữa phân loại văn bản tiếng Việt và Trans2Vec.
- **Đường cong "số từ khóa → accuracy" bão hòa ở ~50** là gợi ý định lượng cho tham số **top-k item mỗi transaction** (giải H2 của [13]). Nên thử k ∈ {20, 50, 100}.
- TextRank (có tính đồ thị đồng xuất hiện) là ứng viên thay KeywordScore của [3] cho bước lọc item.
- Jaccard top-k là baseline **tìm kiếm** đơn giản trên tập từ khóa, để so với cosine trên embedding Trans2Vec.

## 7. Ý dùng trong survey
- Chương 4 (B3).
- Chương 5.5: lập luận "văn bản = tập item" và chọn k.
- Chương 9: baseline tìm kiếm.
