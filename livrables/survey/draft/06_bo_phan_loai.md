## 6. Bộ phân loại và đánh đổi hiệu năng – chi phí

### 6.1 Các bộ phân loại trong tài liệu

Duong và Hoang tổng quan lý thuyết các bộ phân loại thường dùng [@duong2019]:
- k láng giềng gần nhất (kNN);
- Naive Bayes, dạng Multinomial và Bernoulli, có làm trơn Laplace;
- hồi quy logistic (LR);
- cây quyết định ID3, C4.5, CART;
- rừng ngẫu nhiên (RF);
- SVM với lề cứng, lề mềm và hàm nhân;
- các chiến lược mở rộng bộ phân loại nhị phân thành đa lớp: một-đấu-một (OVO) và một-đấu-tất-cả (OVA).

Bảng 6.1 tổng hợp các tổ hợp bộ phân loại × biểu diễn đã được kiểm chứng trong tài liệu.

**Bảng 6.1.** Bộ phân loại × biểu diễn đã được kiểm chứng

| Bộ phân loại | Biểu diễn đã thử | Nhận xét tổng hợp |
|---|---|---|
| **SVM** | TF-IDF [@hoang2007; @duong2019; @huong2022]; âm tiết [@nguyen2009]; MLP-128 [@vinh2021]; Trans2Vec [@trans2vec] | Gần như luôn tốt nhất hoặc nhì với biểu diễn thưa. Thường được dùng làm **bộ phân loại chuẩn để so biểu diễn**: [@trans2vec] cố định C = 1 |
| **LR** | TF-IDF [@duong2019; @huong2022]; PhoBERT [@nguyen2025] | Gần bằng SVM (F1 0,734 so với 0,749 [@duong2019]) nhưng **suy luận nhanh hơn hàng nghìn lần**; tốt nhất khi dùng trên vector PhoBERT [@nguyen2025] |
| NB | TF-IDF [@duong2019]; n-gram [@hoang2007]; âm tiết [@nguyen2009] | Rất nhanh; mạnh khi đã chọn đặc trưng tốt [@nguyen2009] |
| kNN | [@hoang2007; @nguyen2009; @duong2019; @huong2022] | Kém nhất (F1 0,500–0,626 [@duong2019]); **rất nhạy với đặc trưng nhiễu** [@nguyen2009] |
| RF / XGBoost | [@van2017; @duong2019; @huong2022; @nguyen2025] | Trung bình; RF huấn luyện chậm |
| MLP / fine-tune | [@van2017; @vinh2021; @pham2020; @luu2024; @nguyen2025] | Mạnh nhất khi có đủ nhãn; PhoBERT cần GPU |

Từ Bảng 6.1 có hai hệ quả cho hệ thống đề xuất:
1. **SVM tuyến tính** phù hợp làm bộ phân loại đánh giá, để so các biểu diễn một cách công bằng theo đúng thiết kế của [@trans2vec]. **LR** phù hợp làm bộ phân loại triển khai.
2. **kNN kém và nhạy nhiễu.** Tìm kiếm top-k theo cosine thực chất là một bài toán láng giềng gần nhất, nên **chất lượng tìm kiếm phụ thuộc trực tiếp vào độ "sạch" của biểu diễn**. Đây là lập luận ủng hộ biểu diễn dày, đã lọc nhiễu, thay cho vector TF-IDF thưa.

### 6.2 Chi phí tính toán

**Bảng 6.2.** Chi phí được báo cáo trong tài liệu

| Công trình | Thiết lập | Số liệu |
|---|---|---|
| [@duong2019] | 37.500 bài, 25 chuyên mục, CPU Xeon 3,2 GHz | NB: 0,3 s huấn luyện; LR: 77 s; SVM-RBF: 839 s huấn luyện / 291 s kiểm tra; OVO: 4.785 s kiểm tra |
| [@nguyen2009] | Unigram so với bigram âm tiết | Bigram chậm hơn 4,5–9,6 lần |
| [@huynh2020] | 4.500 bài | 2.155–9.279 s huấn luyện, tăng theo số từ khóa |
| [@nguyen2025] | 12.240 review | TF-IDF: 22 s trên CPU; PhoBERT: khoảng 4 phút mỗi epoch trên GPU T4 (khoảng 41 phút cho 10 epoch) |
| [@trans2vec] | — | **Không báo cáo** |

Thiếu số liệu chi phí cho Trans2Vec (H7) là một khoảng trống thực tế. Chi phí của Trans2Vec gồm hai phần:
- **Khai phá FI:** phụ thuộc mạnh vào δ và độ dài transaction (H2).
- **Huấn luyện PV-DBOW:** tuyến tính theo tổng số mẫu.

Cả hai cần được đo trong thực nghiệm. Về định tính, Trans2Vec nằm giữa TF-IDF và PhoBERT trên trục chi phí, và không cần GPU.

### 6.3 Trả lời RQ4

- SVM là chuẩn so sánh; LR là lựa chọn triển khai.
- Biểu diễn dày giúp các bộ phân loại đơn giản và nhanh (LR, tìm kiếm cosine) đạt hiệu năng cao. Biểu diễn thưa cần bộ phân loại mạnh hơn (SVM với hàm nhân) và đắt hơn.
- Mức chi phí của PhoBERT chỉ hợp lý khi xử lý theo lô hoặc khi có GPU [@nguyen2025].
