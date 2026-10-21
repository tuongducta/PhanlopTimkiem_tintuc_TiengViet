## 8. So sánh tổng hợp và thảo luận

### 8.1 Kết quả theo nhóm có thể so sánh

Các kết quả được xếp vào những nhóm có cùng dữ liệu và giao thức tương đương. **Chỉ so sánh con số trong cùng một nhóm**; giữa các nhóm chỉ so sánh xu hướng.

**Bảng 8.1.** Kết quả theo nhóm

| Nhóm | Công trình | Biểu diễn → bộ phân loại | Kết quả | Độ tin cậy |
|---|---|---|---|---|
| **G1** VNTC 10 chuyên mục | [@hoang2007] | BoW + OCFS → SVM | 96,21% | Khá |
| | [@hoang2007] | N-gram âm tiết | 95,58% | Khá |
| | [@van2017] | KEBoW → MLP | 99,75% | ⚠️ Thấp (Mục 8.2) |
| **G2** Tin tức nhiều chuyên mục | [@duong2019] | TF-IDF → SVM-RBF (25 lớp) | F1 0,749 | Cao |
| | [@vinh2021] | TF-IDF → MLP-128 → SVM (30 lớp) | Accuracy ≈ 0,905 (tập validation) | Trung bình |
| **G3** Tin tức ít chuyên mục | [@nguyen2009] | Bigram âm tiết → SVM (4 lớp) | 98,6% | Trung bình |
| | [@huynh2020] | Từ khóa TextRank → Jaccard (15 lớp) | 95,40% | Thấp (không baseline) |
| **G4** Snippets (tiếng Anh) | [@trans2vec] | TF-IDF → SVM | 70,26% | Cao |
| | [@trans2vec] | Trans2Vec-JOI → SVM | 79,05% | Cao |
| | [@phan2008] | BoW + chủ đề ẩn LDA (Wikipedia) → MaxEnt | 82,18% | Cao (có dữ liệu ngoài) |
| **G5** Ngoài miền tin tức | [@nguyen2025] | PhoBERT → LR | Macro-F1 0,96 | Trung bình |
| | [@pham2020] | PhoBERT fine-tune | Macro-F1 0,7221 | Trung bình |

**Bảng 8.2.** Mức cải thiện khi đổi biểu diễn trong cùng nhóm

| Từ → sang | Nguồn | Δ |
|---|---|---|
| Unigram âm tiết → bigram âm tiết | [@nguyen2009] | +0,3–0,9 (dễ); +0,4–7,7 (khó) |
| TF-IDF → embedding item (PV-DBOW) | [@trans2vec] | +5,0 |
| Embedding item → embedding FI | [@trans2vec] | **+2,7** |
| TF-IDF → Trans2Vec-JOI | [@trans2vec] | +8,8 |
| BoW → BoW + chủ đề ẩn từ corpus ngoài | [@phan2008] | +16,4 |
| TF-IDF → PhoBERT | [@nguyen2025] | +7 Macro-F1 (so với BoW: +5) |

Bảng 8.2 cho thấy:
- **(i) Biểu diễn dày thắng TF-IDF khi được huấn luyện đúng cách**, và lợi thế càng rõ trên tác vụ khó.
- **(ii) FI mang thông tin riêng**, bổ sung cho embedding item.
- **(iii) Tri thức ngoài cho mức tăng lớn nhất.** Đây là trần trên mà mọi biểu diễn chỉ học từ dữ liệu nội tại, kể cả Trans2Vec, cần được đặt cạnh.

### 8.2 Độ khó corpus, rò rỉ dữ liệu và tính so sánh được

Trên cùng loại dữ liệu "tin tức tiếng Việt", kết quả báo cáo trải từ F1 0,749 [@duong2019] tới 99,75% [@van2017]. Khác biệt này chủ yếu đến từ ba nguồn:
1. **Số chuyên mục và mức chồng lấn:** 4–10 lớp tách bạch so với 25–30 lớp chồng lấn.
2. **Giao thức** (Bảng 7.2).
3. **Khả năng rò rỉ dữ liệu.** Con số 99,75% của [@van2017] cần được đọc thận trọng:
   - Từ điển từ khóa được dựng trên "toàn bộ tài liệu của corpus", nên có thể gồm cả tập kiểm tra.
   - Điểm từ khóa là một hàm thuần tần suất, không có thành phần IDF.
   - Bài không báo phương sai, và so sánh với [@hoang2007] qua hình chụp lại thay vì chạy lại baseline.

   Trên cùng VNTC, một kết quả hơn kết quả gốc gần 4 điểm (sai số giảm khoảng 15 lần) khi chỉ đổi cách chọn đặc trưng và bộ phân loại là điều khó xảy ra nếu không có rò rỉ.

### 8.3 Năm mâu thuẫn trong tài liệu

**Bảng 8.3.** Mâu thuẫn và cách giải thích

| # | Mâu thuẫn | Bên A | Bên B | Giải thích đề xuất |
|---|---|---|---|---|
| **M1** | Embedding tĩnh hay TF-IDF? | TF-IDF thắng: Word2Vec/Doc2Vec ≈ 50% [@huong2022]; Word2Vec < BoW (Macro-F1 0,88 so với 0,91) [@nguyen2025] | PV-DBOW hơn TF-IDF 5 điểm [@trans2vec] | Xem phân tích bên dưới |
| **M2** | Có cần tách từ? | Không: n-gram âm tiết ≈ BoW theo từ [@hoang2007]; bigram [@nguyen2009; @vinh2021] | Có: lỗi tách từ gây phân loại sai [@van2017]; PhoBERT +2 F1 [@luu2024] | Phụ thuộc họ biểu diễn (Bảng 2.1); với Trans2Vec là câu hỏi mở |
| **M3** | Top2Vec tốt hay kém? | Kém về độ gắn kết trên review ngắn [@nguyen2025] | Tốt hơn LDA theo tác giả [@angelov2020] | Phụ thuộc độ dài văn bản và kích thước corpus |
| **M4** | Kết quả ~99% hay ~0,75? | [@van2017; @nguyen2009] | [@duong2019] | Độ khó corpus, giao thức, rò rỉ (Mục 8.2) |
| **M5** | Trans2Vec có phải tốt nhất trên Snippets? | Tốt nhất trong các baseline của bài [@trans2vec] | 82,18% > 79,05% [@phan2008] | [@trans2vec] chỉ so với baseline không giám sát và không dùng dữ liệu ngoài |

**Phân tích M1.** Mâu thuẫn này đáng phân tích kỹ vì nó ảnh hưởng trực tiếp đến tính khả thi của Trans2Vec (vốn xây trên PV-DBOW).
- **Kết quả của [@huong2022] khó chấp nhận về mặt lý thuyết.** Word2Vec và Doc2Vec chỉ đạt khoảng 50% trên tập nhị phân *cân bằng*, với **cả năm** bộ phân loại, kể cả 1-NN. Một biểu diễn mang dù chỉ một chút thông tin thì 1-NN cũng phải vượt mức đoán ngẫu nhiên. Kết quả đúng bằng 50% vì vậy gợi ý lỗi cài đặt hơn là giới hạn của phương pháp: vector suy biến sau khi gộp, lệch thứ tự giữa vector và nhãn, hoặc vector chưa được huấn luyện. Bài cũng không công bố siêu tham số nên không thể tái lập.
- **Bằng chứng đối lập:** PV-DBOW thắng TF-IDF trên văn bản ngắn [@trans2vec]; Word2Vec (CBOW) vẫn đạt Macro-F1 tới 0,88 trên review Shopee, gần bằng TF-IDF (0,89) [@nguyen2025]; Doc2Vec vững khi được cấu hình đúng [@lau2016].
- **Kết luận cho đề tài:** không nên coi [@huong2022] là bằng chứng rằng Doc2Vec không dùng được cho tiếng Việt. Ngược lại, cần kiểm tra cẩn thận để tránh những lỗi tương tự: chuẩn và phương sai của vector, thử kNN nhanh, báo đủ siêu tham số.

### 8.4 Các mối đe dọa đến tính hợp lệ của khảo sát

- **Tuyển chọn tài liệu.** Vòng 1 do người thực hiện chọn. Vòng 2 bổ sung có hệ thống nhưng không phải tổng quan hệ thống đầy đủ theo PRISMA.
- **Tính độc lập.** Một số công trình chung nhóm tác giả: [@van2017] và [@pham2020] chung tác giả Ta Minh Thanh; [@duong2019] và [@huong2022] chung nhóm Đại học Mở TP.HCM. Toàn bộ họ phương pháp ở Bảng 5.2 có chung tác giả chính (Dang Nguyen, Wei Luo).
- **Trích số liệu.** Một số số liệu chỉ có trong hình (bản quét của [@hoang2007]; so sánh trong [@vinh2021]), nên chỉ được trích ở mức đã nêu trong văn bản của bài.
- **Bằng chứng cho RQ3** đến từ một công trình duy nhất trên dữ liệu tiếng Anh.

### 8.5 Trả lời RQ2 và RQ5

**RQ2.**
- Biểu diễn thưa có chọn đặc trưng đã đủ cho tác vụ dễ (trên 95%).
- Biểu diễn dày tạo khác biệt ở tác vụ khó.
- Tri thức ngoài (PhoBERT, chủ đề từ corpus lớn) cho hiệu năng cao nhất nhưng đắt nhất.
- Thiếu một bảng so sánh đối đầu đủ các họ biểu diễn trên **cùng một corpus tin tức tiếng Việt công khai**. Chính khoảng trống này khiến không thể xếp hạng dứt khoát.

**RQ5.** Dữ liệu và giao thức hiện tại *chưa đủ chuẩn*:
- dữ liệu phân mảnh, phần lớn không công khai;
- giao thức và độ đo không thống nhất;
- có dấu hiệu rò rỉ dữ liệu và lỗi tái lập.

Giao thức ở Mục 7.3 là đề xuất khắc phục.
