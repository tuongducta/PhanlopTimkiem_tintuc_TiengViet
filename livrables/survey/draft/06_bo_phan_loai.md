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
| **LR** | TF-IDF [@duong2019; @huong2022; @hien2024]; PhoBERT [@nguyen2025] | Gần bằng SVM (F1 0,734 so với 0,749 [@duong2019]; accuracy 92,77% so với 93,60% [@hien2024]) nhưng **suy luận nhanh hơn hàng nghìn lần**; tốt nhất khi dùng trên vector PhoBERT [@nguyen2025] |
| NB | TF-IDF [@duong2019]; n-gram [@hoang2007]; âm tiết [@nguyen2009] | Rất nhanh; mạnh khi đã chọn đặc trưng tốt [@nguyen2009] |
| kNN | [@hoang2007; @nguyen2009; @duong2019; @huong2022] | Kém nhất (F1 0,500–0,626 [@duong2019]); **rất nhạy với đặc trưng nhiễu** [@nguyen2009] |
| RF / XGBoost | [@van2017; @duong2019; @huong2022; @nguyen2025] | Trung bình; RF huấn luyện chậm |
| MLP / fine-tune | [@van2017; @vinh2021; @pham2020; @luu2024; @nguyen2025] | Mạnh nhất khi có đủ nhãn; PhoBERT cần GPU |
| LSTM, CNN trên túi từ | [@hien2024] | Trên VNTC, LSTM hơn SVM 2,7–3,3 điểm accuracy với BoW, nhưng chỉ 0,08–0,15 điểm với TF-IDF (Mục 4.4) |
| Bộ phân loại nhẹ trên embedding đóng băng | [@liu2024] | Ngang cách dùng prompt CARP với GPT-3 về accuracy; thời gian chỉ khoảng 1,5% so với CARP |

Từ Bảng 6.1 có hai hệ quả cho hệ thống đề xuất:
1. **SVM tuyến tính** phù hợp làm bộ phân loại đánh giá, để so các biểu diễn một cách công bằng theo đúng thiết kế của [@trans2vec]. **LR** phù hợp làm bộ phân loại triển khai. Thực nghiệm của đề tài còn cho thấy, trên vector Trans2Vec, LR hơn SVM 0,6–0,7 điểm Macro-F1 ở mọi biến thể (Mục 9.5).
2. **kNN kém và nhạy nhiễu.** Tìm kiếm top-k theo cosine thực chất là một bài toán láng giềng gần nhất, nên **chất lượng tìm kiếm phụ thuộc trực tiếp vào độ "sạch" của biểu diễn**. Đây là lập luận ủng hộ biểu diễn dày, đã lọc nhiễu, thay cho vector TF-IDF thưa.

### 6.2 Chi phí tính toán

**Bảng 6.2.** Chi phí được báo cáo trong tài liệu

| Công trình | Thiết lập | Số liệu |
|---|---|---|
| [@duong2019] | 37.500 bài, 25 chuyên mục, CPU Xeon 3,2 GHz | NB: 0,3 s huấn luyện; LR: 77 s; SVM-RBF: 839 s huấn luyện / 291 s kiểm tra; OVO: 4.785 s kiểm tra |
| [@nguyen2009] | Unigram so với bigram âm tiết | Bigram chậm hơn 4,5–9,6 lần |
| [@huynh2020] | 4.500 bài | 2.155–9.279 s huấn luyện, tăng theo số từ khóa |
| [@nguyen2025] | 12.240 review | TF-IDF: 22 s trên CPU; PhoBERT: khoảng 4 phút mỗi epoch trên GPU T4 (khoảng 41 phút cho 10 epoch) |
| [@le2013vnlp] | Tách từ 2 triệu âm tiết | 6 s sau khi tối ưu (bản gốc 234 s) |
| [@trasierras2024] | Khai phá FI, 14 dataset | Chênh 4–6 bậc độ lớn giữa các thuật toán ở ngưỡng thấp; có lần chạy mất khoảng 140 giờ hoặc hết bộ nhớ |
| [@liu2024] | 5 benchmark, GPU A100 | Trung bình 1 giờ 41 phút và 0,38 kWh, so với 115 giờ và 20,93 kWh của cách dùng prompt |
| [@trans2vec] | — | **Không báo cáo** |

Thiếu số liệu chi phí cho Trans2Vec (H7) là một khoảng trống thực tế. Chi phí của Trans2Vec gồm hai phần:
- **Khai phá FI:** phụ thuộc mạnh vào δ và độ dài transaction (H2). Theo [@trasierras2024], chi phí này không phải hằng số mà là hàm của δ và hồ sơ dữ liệu.
- **Huấn luyện PV-DBOW:** tuyến tính theo tổng số mẫu.

Đề tài đã đo cả hai trên VNTC-10 (Mục 9.5). Với cấu hình chính, toàn bộ chạy trên CPU: khai phá FI 3 giây, huấn luyện 16 giây, suy luận vector cho 50.373 bài kiểm tra 42 giây. Nếu suy luận lại cả vector huấn luyện theo giao thức ở Mục 7.3, phần huấn luyện cộng suy luận mất khoảng 98 giây (Bảng 9.9). Hạ δ từ 0,535% xuống 0,2% làm số FI tăng 12 lần và thời gian huấn luyện cộng suy luận tăng gấp đôi. Trên trục chi phí, Trans2Vec nằm giữa TF-IDF và các mô hình cần GPU (PhoBERT tinh chỉnh, LLM đóng băng).

### 6.3 Trả lời RQ4

- SVM là chuẩn so sánh; LR là lựa chọn triển khai, và trên embedding còn tốt hơn SVM.
- Biểu diễn dày giúp các bộ phân loại đơn giản và nhanh (LR, tìm kiếm cosine) đạt hiệu năng cao. Biểu diễn thưa cần bộ phân loại mạnh hơn (SVM với hàm nhân) và đắt hơn.
- Nối nhiều embedding có lợi nhưng nhỏ: ghép thêm BERT, RoBERTa và gộp đồng xuất hiện vào LLaMA2 chỉ thêm khoảng 0,3 điểm [@liu2024]; nối ba vector Trans2Vec thêm 0,8 điểm Macro-F1 (Mục 9.5).
- Mức chi phí của PhoBERT và của LLM đóng băng chỉ hợp lý khi xử lý theo lô hoặc khi có GPU [@nguyen2025; @liu2024]. Trans2Vec là lựa chọn khi cần chạy trên CPU và cần giải thích được.
