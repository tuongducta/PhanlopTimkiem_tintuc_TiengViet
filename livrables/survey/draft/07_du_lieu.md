## 7. Dữ liệu và giao thức đánh giá

### 7.1 Các tập dữ liệu

**Bảng 7.1.** Tập dữ liệu trong các công trình khảo sát

| Tập dữ liệu | Công trình | Miền / nguồn | #Tài liệu | #Lớp | Chia dữ liệu | Công khai |
|---|---|---|---|---|---|---|
| **VNTC Level 1** | [@hoang2007; @van2017; @hien2024] | Tin tức, 4 báo | 84.132 | 10 | 33.759 / 50.373 | ✅ |
| **VNTC Level 2** | [@hoang2007; @van2017; @hien2024] | Tin tức, chủ đề con | 26.451 | 27 | 14.375 / 12.076 | ✅ |
| VNNews-01 | [@duong2019] | Tin tức, >30 trang | 37.500 | 25 | 5-fold CV | Theo yêu cầu |
| Corpus của [@vinh2021] | [@vinh2021] | Tin tức, 5 trang | 68.363 | 30 | 48.363 / 10.000 / 10.000 | ❌ |
| D1 / D2 | [@nguyen2009] | Tin tức / thể loại | ~16.000 / 1.743 | 4 / 2 | 10% huấn luyện | ❌ |
| Corpus của [@huynh2020] | [@huynh2020] | Tin tức, 4 trang | 4.500 | 15 | 200 / 100 mỗi lớp | ❌ |
| Snippets | [@phan2008; @trans2vec] | Đoạn trích tìm kiếm web (tiếng Anh) | 12.340 | 8 | 10.060 / 2.280 | ✅ |
| Shopee reviews | [@nguyen2025] | Review thương mại điện tử, đa nhãn | 17.049 | 5 (+Khác) | 70 / 10 / 20 | ❌ |

Bốn nhận xét:
1. **Dữ liệu phân mảnh.** Có ít nhất sáu corpus tin tức tiếng Việt khác nhau, nhưng chỉ **VNTC** [@hoang2007] vừa công khai vừa đã có kết quả công bố để đối chiếu. VNTC được xây từ VnExpress, Tuổi Trẻ, Thanh Niên và Người Lao Động, sau đó được năm học viên cao học ngành ngôn ngữ học hiệu chỉnh thủ công.
2. **Độ khó chênh lệch lớn.** Corpus 4 chuyên mục cho độ chính xác khoảng 98% với *mọi* thuật toán [@nguyen2009], nên không còn đủ sức phân biệt các phương pháp. Ngược lại, VNNews-01 với 25 chuyên mục chồng lấn chỉ cho F1 0,749 với bộ phân loại tốt nhất [@duong2019].
3. **Sai lệch nhỏ trong mô tả dữ liệu.** Một công trình ghi 17.002 review ở phần tóm tắt nhưng 17.049 ở phần dữ liệu [@nguyen2025]. Những chi tiết như vậy làm giảm khả năng tái lập.
4. **VNTC có bài trùng.** Khi đưa VNTC-10 vào cơ sở dữ liệu và đánh chỉ mục theo mã băm nội dung, đề tài phát hiện 3.415 nhóm bài trùng y hệt, gồm 8.399 bài, tức 4.984 bản thừa. Có 2.522 nhóm nằm ở cả tập huấn luyện lẫn tập kiểm tra, nghĩa là **3.056 bài kiểm tra (6,1%) có bản sao trong tập huấn luyện**. Ngoài ra, 380 nhóm mang nhãn chuyên mục khác nhau, tức là nhiễu nhãn. Ảnh hưởng tới phân loại không đáng kể: bỏ 3.056 bài này thì Macro-F1 gần như không đổi (Trans2Vec-JOI 0,8498 so với 0,8488; TF-IDF 0,9063 so với 0,9065). Dù vậy, đây là rò rỉ giữa tập huấn luyện và tập kiểm tra mà các công trình dùng VNTC chưa đề cập. Với tìm kiếm, hệ thống phải khử trùng khi hiển thị kết quả.

### 7.2 Vấn đề giao thức đánh giá

**Bảng 7.2.** Giao thức đánh giá không thống nhất

| Khía cạnh | Biến thể trong tài liệu |
|---|---|
| Chia dữ liệu | Chia cố định [@hoang2007]; 10% huấn luyện, lặp 10 lần [@nguyen2009]; 5-fold [@duong2019]; 10-fold [@pham2020]; 70/30 [@huong2022]; không rõ [@van2017] |
| Độ đo | Accuracy trung bình theo lớp [@hoang2007; @van2017]; F-measure [@duong2019]; Macro-F1 [@pham2020; @luu2024; @trans2vec]; Hamming loss [@nguyen2025] |
| Độ lệch chuẩn | Hầu như không báo; [@trans2vec] nói "< 10⁻²" nhưng không đưa bảng |
| Mức fit tiền xử lý | Có trường hợp từ điển từ khóa được dựng trên toàn bộ corpus [@van2017] |
| Mô tả siêu tham số | Thiếu với embedding [@huong2022] và với mạng nơ-ron [@hien2024] |
| Học transductive | Mã công bố của [@trans2vec] học vector trên cả tập kiểm tra; TextGCN cũng đưa tài liệu kiểm tra vào đồ thị [@onan2023]. Bài báo không nêu điều này |
| Baseline chạy lại | Baseline lệch so với công bố gốc [@onan2023]; baseline không hội tụ [@liu2024] (Mục 8.4) |
| Bài trùng giữa các tập | 6,1% bài kiểm tra VNTC có bản sao trong tập huấn luyện (Mục 7.1) |

### 7.3 Đề xuất giao thức chuẩn

Để trả lời RQ5 theo hướng xây dựng, bài khảo sát đề xuất một giao thức tối thiểu cho các nghiên cứu phân loại và tìm kiếm tin tức tiếng Việt:
1. **Dữ liệu:** dùng VNTC (Level 1 và Level 2) với cách chia công bố, để đối chiếu được với [@hoang2007]. Bổ sung một corpus khó (≥ 25 chuyên mục) để tránh hiệu ứng trần.
2. **Không rò rỉ:** từ vựng, danh sách từ khóa, tập phổ biến, embedding và mọi tham số tiền xử lý **chỉ được fit trên tập huấn luyện**.
3. **Độ đo:** Macro-F1 là chính, accuracy là phụ. Báo **trung bình ± độ lệch chuẩn** qua ít nhất 5 lần chạy với hạt giống ngẫu nhiên khác nhau.
4. **Tìm kiếm:** Precision@k, MAP, nDCG@k [@jarvelin2002]. Coi các bài cùng chuyên mục là "liên quan" (nhãn thay thế), và nêu rõ hạn chế của cách làm này. Có thể tham khảo cách tổ chức tác vụ truy xuất và phân cụm của VN-MTEB [@vnmteb2026].
5. **Tái lập:** báo đầy đủ siêu tham số, phiên bản công cụ (bộ tách từ, thư viện), cấu hình phần cứng và thời gian chạy.
6. **Nhất quán giữa vector huấn luyện và kiểm tra** (bổ sung từ thực nghiệm ở Mục 9.5): với các mô hình phải suy luận vector cho tài liệu mới (Doc2Vec, Trans2Vec), vector của tập huấn luyện cũng phải được sinh bằng cùng quy trình suy luận. Nếu lấy trực tiếp vector học được trong mô hình, kết quả có thể lệch 7–8 điểm Macro-F1, và có thể xuất hiện những "cải thiện" giả.
7. **Khai báo chế độ học:** nêu rõ biểu diễn được học transductive hay inductive. Học transductive có thể có lợi cho chính phương pháp đó, vì mô hình đã thấy văn bản kiểm tra. Trên dữ liệu của đề tài, mức chênh không nhất quán (Snippets: từ −0,5 đến +1,9 điểm accuracy), nên càng phải khai báo.
8. **Khử trùng trước khi chia dữ liệu** theo mã băm nội dung, và báo số bài trùng giữa các tập.
9. **Đánh giá chỉ mục vector bằng recall so với tìm vét cạn.** Nhãn thay thế "cùng chuyên mục" quá thô cho việc này: trên VNTC, đổi chỉ mục làm recall@10 thay đổi từ 0,86 đến 1,00, nhưng nDCG@10 chỉ dao động trong khoảng 0,811–0,818 (Mục 9.5).
10. **Chạy lại baseline trong cùng điều kiện** thay vì chép số từ bài khác, và kiểm tra baseline có hội tụ không.

### 7.4 Bối cảnh quốc tế và hồ sơ dữ liệu

**Bảng 7.3.** Các tập tin tức chuẩn quốc tế, theo hai bài tổng quan [@li2022; @minaee2021] và [@onan2023]

| Tập dữ liệu | Ngôn ngữ | #Tài liệu | #Lớp | Dùng trong |
|---|---|---|---|---|
| AG News | Anh | 127.600 (120.000 / 7.600) | 4 | [@minaee2021; @liu2024] |
| 20 Newsgroups | Anh | khoảng 18.800–20.000 | 20 | [@minaee2021; @onan2023] |
| Reuters R8 / R52 | Anh | 7.674 / 9.100 | 8 / 52 | [@li2022; @liu2024; @onan2023] |
| Sogou News | Trung | — | — | [@minaee2021] |

So với các tập này, VNTC-10 có quy mô tương đương (84.132 bài) nhưng ít được dùng làm benchmark chung, và chưa có bộ truy vấn có nhãn liên quan cho tìm kiếm.

**Hồ sơ dữ liệu giao dịch.** Khi coi mỗi bài là một transaction, có thể mô tả corpus bằng tám độ đo của [@trasierras2024] (Mục 3.2). Bảng 7.4 đặt Snippets, nơi [@trans2vec] báo FI có ích nhất, cạnh VNTC-10 theo cấu hình của đề tài. Số liệu do đề tài tính (thực nghiệm E8), chỉ trên tập huấn luyện.

**Bảng 7.4.** Hồ sơ giao dịch của Snippets và VNTC-10

| Corpus | δ | #Transaction | #Item | Độ dài TB | Density | Similarity (%) | FI dài ≥ 2 / bài | Bài không có FI dài ≥ 2 |
|---|---|---|---|---|---|---|---|---|
| Snippets | 0 | 10.060 | 20.302 | 13,0 | 6,4×10⁻⁴ | 1,56 | — | — |
| Snippets | 0,2% | 10.047 | 1.125 | 8,7 | 7,7×10⁻³ | 2,23 | 5,7 | 14% |
| VNTC-10, từ, k = 50 | 0 | 33.759 | 43.572 | 49,0 | 1,1×10⁻³ | 1,10 | — | — |
| VNTC-10, từ, k = 50 | 0,535% | 33.759 | 2.102 | 26,0 | 1,2×10⁻² | 1,88 | 12,0 | 14% |
| VNTC-10, từ, toàn văn | 0 | 33.759 | 43.777 | 138,0 | 3,2×10⁻³ | 6,82 | — | — |

*Ghi chú:* δ = 0,2% là ngưỡng tác giả [@trans2vec] chọn cho Snippets; δ = 0,535% là ngưỡng elbow của đề tài cho VNTC. Ở mỗi δ, item có độ hỗ trợ nhỏ hơn δ bị bỏ trước khi tính, như cách làm của [@trasierras2024]. Density và độ dài trung bình tính đúng như bài gốc; Similarity tính theo công thức in trong bài, chỉ dùng để so giữa các corpus ở đây.

Trước khi lọc, hai corpus cùng loại **thưa**, cùng bậc với tập Retail (density 6,3×10⁻⁴ [@trasierras2024]). Khác biệt rõ nhất là độ dài transaction: 13 so với 49 item, và 138 nếu không lọc top-k. Bảng cũng cho thấy kết luận của [@trasierras2024] đúng với văn bản: nâng δ làm hồ sơ đổi hẳn. Ý nghĩa của bảng này với vai trò của FI được phân tích ở Mục 9.5.
