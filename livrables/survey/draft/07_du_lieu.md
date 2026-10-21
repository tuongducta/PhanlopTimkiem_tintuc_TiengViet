## 7. Dữ liệu và giao thức đánh giá

### 7.1 Các tập dữ liệu

**Bảng 7.1.** Tập dữ liệu trong các công trình khảo sát

| Tập dữ liệu | Công trình | Miền / nguồn | #Tài liệu | #Lớp | Chia dữ liệu | Công khai |
|---|---|---|---|---|---|---|
| **VNTC Level 1** | [@hoang2007; @van2017] | Tin tức, 4 báo | 84.132 | 10 | 33.759 / 50.373 | ✅ |
| **VNTC Level 2** | [@hoang2007; @van2017] | Tin tức, chủ đề con | 26.451 | 27 | 14.375 / 12.076 | ✅ |
| VNNews-01 | [@duong2019] | Tin tức, >30 trang | 37.500 | 25 | 5-fold CV | Theo yêu cầu |
| Corpus của [@vinh2021] | [@vinh2021] | Tin tức, 5 trang | 68.363 | 30 | 48.363 / 10.000 / 10.000 | ❌ |
| D1 / D2 | [@nguyen2009] | Tin tức / thể loại | ~16.000 / 1.743 | 4 / 2 | 10% huấn luyện | ❌ |
| Corpus của [@huynh2020] | [@huynh2020] | Tin tức, 4 trang | 4.500 | 15 | 200 / 100 mỗi lớp | ❌ |
| Snippets | [@phan2008; @trans2vec] | Đoạn trích tìm kiếm web (tiếng Anh) | 12.340 | 8 | 10.060 / 2.280 | ✅ |
| Shopee reviews | [@nguyen2025] | Review thương mại điện tử, đa nhãn | 17.049 | 5 (+Khác) | 70 / 10 / 20 | ❌ |

Ba nhận xét:
1. **Dữ liệu phân mảnh.** Có ít nhất sáu corpus tin tức tiếng Việt khác nhau, nhưng chỉ **VNTC** [@hoang2007] vừa công khai vừa đã có kết quả công bố để đối chiếu. VNTC được xây từ VnExpress, Tuổi Trẻ, Thanh Niên và Người Lao Động, sau đó được năm học viên cao học ngành ngôn ngữ học hiệu chỉnh thủ công.
2. **Độ khó chênh lệch lớn.** Corpus 4 chuyên mục cho độ chính xác khoảng 98% với *mọi* thuật toán [@nguyen2009], nên không còn đủ sức phân biệt các phương pháp. Ngược lại, VNNews-01 với 25 chuyên mục chồng lấn chỉ cho F1 0,749 với bộ phân loại tốt nhất [@duong2019].
3. **Sai lệch nhỏ trong mô tả dữ liệu.** Một công trình ghi 17.002 review ở phần tóm tắt nhưng 17.049 ở phần dữ liệu [@nguyen2025]. Những chi tiết như vậy làm giảm khả năng tái lập.

### 7.2 Vấn đề giao thức đánh giá

**Bảng 7.2.** Giao thức đánh giá không thống nhất

| Khía cạnh | Biến thể trong tài liệu |
|---|---|
| Chia dữ liệu | Chia cố định [@hoang2007]; 10% huấn luyện, lặp 10 lần [@nguyen2009]; 5-fold [@duong2019]; 10-fold [@pham2020]; 70/30 [@huong2022]; không rõ [@van2017] |
| Độ đo | Accuracy trung bình theo lớp [@hoang2007; @van2017]; F-measure [@duong2019]; Macro-F1 [@pham2020; @luu2024; @trans2vec]; Hamming loss [@nguyen2025] |
| Độ lệch chuẩn | Hầu như không báo; [@trans2vec] nói "< 10⁻²" nhưng không đưa bảng |
| Mức fit tiền xử lý | Có trường hợp từ điển từ khóa được dựng trên toàn bộ corpus [@van2017] |
| Mô tả siêu tham số | Thiếu với embedding [@huong2022] |

### 7.3 Đề xuất giao thức chuẩn

Để trả lời RQ5 theo hướng xây dựng, bài khảo sát đề xuất một giao thức tối thiểu cho các nghiên cứu phân loại và tìm kiếm tin tức tiếng Việt:
1. **Dữ liệu:** dùng VNTC (Level 1 và Level 2) với cách chia công bố, để đối chiếu được với [@hoang2007]. Bổ sung một corpus khó (≥ 25 chuyên mục) để tránh hiệu ứng trần.
2. **Không rò rỉ:** từ vựng, danh sách từ khóa, tập phổ biến, embedding và mọi tham số tiền xử lý **chỉ được fit trên tập huấn luyện**.
3. **Độ đo:** Macro-F1 là chính, accuracy là phụ. Báo **trung bình ± độ lệch chuẩn** qua ít nhất 5 lần chạy với hạt giống ngẫu nhiên khác nhau.
4. **Tìm kiếm:** Precision@k, MAP, nDCG@k [@jarvelin2002]. Coi các bài cùng chuyên mục là "liên quan" (nhãn thay thế), và nêu rõ hạn chế của cách làm này. Có thể tham khảo cách tổ chức tác vụ truy xuất và phân cụm của VN-MTEB [@vnmteb2026].
5. **Tái lập:** báo đầy đủ siêu tham số, phiên bản công cụ (bộ tách từ, thư viện), cấu hình phần cứng và thời gian chạy.
6. **Nhất quán giữa vector huấn luyện và kiểm tra** (bổ sung từ thực nghiệm ở Mục 9.5): với các mô hình phải suy luận vector cho tài liệu mới (Doc2Vec, Trans2Vec), vector của tập huấn luyện cũng phải được sinh bằng cùng quy trình suy luận. Nếu lấy trực tiếp vector học được trong mô hình, kết quả có thể lệch 7–8 điểm Macro-F1, và có thể xuất hiện những "cải thiện" giả.
