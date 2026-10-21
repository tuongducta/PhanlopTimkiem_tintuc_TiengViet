## 10. Kết luận và hướng phát triển

### 10.1 Tóm tắt trả lời các câu hỏi nghiên cứu

| RQ | Trả lời | Mức chắc chắn |
|---|---|---|
| **RQ1** | Thách thức chính là tách từ (nhập nhằng nghĩa), bảng mã và dấu thanh, và danh sách từ dừng chủ quan. Vai trò của tiền xử lý **đi theo đường cong chữ U**: giảm dần từ biểu diễn thưa tới Transformer, rồi trở lại thành cốt lõi với biểu diễn dựa trên mẫu | Cao |
| **RQ2** | Biểu diễn thưa có chọn đặc trưng đủ cho tác vụ dễ; biểu diễn dày tạo khác biệt ở tác vụ khó; tri thức ngoài cho hiệu năng cao nhất với chi phí cao nhất. Chưa có so sánh đối đầu trên một corpus tin tức tiếng Việt công khai | Trung bình – Cao |
| **RQ3** | Trên Snippets (tiếng Anh), FI làm giàu embedding thêm 2,7 điểm [@trans2vec]. **Thực nghiệm sơ bộ (Mục 9.5) không tái hiện được mức này, cả trên VNTC-10 lẫn trên chính Snippets với dữ liệu và mã nguồn của tác giả (+0,7 điểm):** khi đánh giá nhất quán, FI chỉ đóng góp −0,3 đến +0,9 điểm Macro-F1, và Trans2Vec (0,849) vẫn kém TF-IDF (0,907). Giá trị của FI cho tin tức tiếng Việt nằm ở **tìm kiếm** (biểu diễn không giám sát tốt nhất, hơn TF-IDF 7 điểm nDCG@10), ở **diễn giải** chuyên mục, và ở **chi phí thấp** (dưới 1 phút trên CPU) | Trung bình (một corpus, một seed cho bản đánh giá nhất quán) |
| **RQ4** | SVM là chuẩn so sánh, LR là lựa chọn triển khai. Tìm kiếm top-k cần biểu diễn dày và sạch vì kNN nhạy với nhiễu. Trans2Vec nằm giữa TF-IDF và PhoBERT trên trục chi phí | Cao |
| **RQ5** | Chưa đủ chuẩn: dữ liệu phân mảnh, giao thức không thống nhất, có dấu hiệu rò rỉ và lỗi tái lập. Bài đề xuất một giao thức tối thiểu (Mục 7.3) | Cao |

### 10.2 Khoảng trống nghiên cứu

Phân loại chuyên mục tin tức tiếng Việt đã được nghiên cứu qua ba thế hệ biểu diễn. Khai phá tập phổ biến đã được dùng cho văn bản, kể cả tiếng Việt, nhưng chỉ dưới dạng đặc trưng thưa hoặc luật [@dophuc2006; @beil2002; @fung2003]. Hướng **học embedding từ mẫu phổ biến**, gồm Trans2Vec và họ phương pháp của nó [@trans2vec; @sqn2vec; @gefsg2018], **chưa được áp dụng cho văn bản tiếng Việt, chưa được kiểm chứng trên văn bản dài như tin tức, và chưa được dùng cho tìm kiếm**.

### 10.3 Hướng phát triển

1. **Mở rộng thực nghiệm ở Mục 9.5:** chạy nhiều seed cho bản đánh giá nhất quán; thêm một corpus khó (≥ 25 chuyên mục), PhoBERT và Top2Vec; quét δ có hệ thống thay vì chỉ dùng elbow; tìm cách đưa lại thông tin tần suất vào Trans2Vec (H1), vì phép ghép thẳng với TF-IDF chưa hiệu quả.
2. **Mở rộng sang mẫu tuần tự** với Sqn2Vec [@sqn2vec], để giữ thứ tự từ, và sang **đồ thị từ** [@rousseau2015; @gefsg2018].
3. **Kết hợp tri thức ngoài:** khởi tạo vector item từ embedding tiền huấn luyện, hoặc dùng FI làm tín hiệu bổ sung cho bộ mã hóa PhoBERT.
4. **Phân loại phân cấp:** tận dụng cấu trúc chuyên mục cha – con (VNTC Level 1 – Level 2) và cây chủ đề từ FI [@fung2003].
5. **Xây dựng một benchmark tin tức tiếng Việt công khai, khó, có giao thức chuẩn**, cho cả phân loại lẫn tìm kiếm, theo tinh thần của VN-MTEB [@vnmteb2026] nhưng trên dữ liệu gốc tiếng Việt thay vì dữ liệu dịch.

---

## Phụ lục A. Bảng tóm tắt các công trình nòng cốt

| Công trình | Năm | Dữ liệu | Biểu diễn | Bộ phân loại | Kết quả chính | Nhánh |
|---|---|---|---|---|---|---|
| Hoang và cs. [@hoang2007] | 2007 | VNTC 10 / 27 lớp | BoW + OCFS; n-gram âm tiết | SVM; NB-LM | 96,21% / 95,58% | A1, A2, B1 |
| Nguyen và cs. [@nguyen2009] | 2009 | 4 lớp; 2 lớp thể loại | Bag-of-syllables; IG; từ điển | NB, kNN, SVM | 98,6%; 89,8% | A1, B1, B2 |
| Pham Van & Ta Minh [@van2017] | 2017 | VNTC | KEBoW | MLP 6 lớp | 99,75% (nghi rò rỉ) | B3 |
| Duong & Hoang [@duong2019] | 2019 | VNNews-01, 25 lớp | TF-IDF | 8 bộ phân loại | F1 0,749 | A2 |
| Huynh và cs. [@huynh2020] | 2020 | 15 lớp | Từ khóa TextRank | Jaccard | 95,40% | B3 |
| Pham và cs. [@pham2020] | 2020 | VLSP HSD | PhoBERT | Fine-tune | Macro-F1 0,7221 | F |
| Vinh & Kha [@vinh2021] | 2021 | 30 lớp | MLP-128 | SVM | > χ², OCFS | C |
| Huong và cs. [@huong2022] | 2022 | Cảm xúc | TF-IDF, W2V, GloVe, D2V | 5 bộ phân loại | TF-IDF 86,8% | D1, D2 |
| Luu và cs. [@luu2024] | 2024 | ViHSD, UIT-ViCTSD | 7 mô hình BERT | Fine-tune + EDA | Macro-F1 74,63 | F |
| Nguyen và cs. [@nguyen2025] | 2025 | Shopee, đa nhãn | BoW … PhoBERT; LDA, Top2Vec, BERTopic | LR, SVM, XGB | Macro-F1 0,96 | D, F |
| Nguyen và cs. [@trans2vec] | 2018 | Snippets + 3 tập | Trans2Vec | SVM | 79,05% (Snippets) | E2 |

## Phụ lục B. Thuật ngữ Việt – Anh

| Tiếng Việt | Tiếng Anh |
|---|---|
| Tập phổ biến | Frequent itemset (FI) |
| Tập phổ biến đóng | Closed itemset |
| Độ hỗ trợ | Support |
| Ngưỡng hỗ trợ tối thiểu | Minimum support threshold (δ) |
| Mẫu tuần tự | Sequential pattern |
| Học biểu diễn | Representation learning |
| Vector nhúng | Embedding |
| Lấy mẫu âm | Negative sampling |
| Túi từ | Bag-of-words (BoW) |
| Tách từ | Word segmentation |
| Từ dừng | Stop word |
| Chọn đặc trưng | Feature selection |
| Trích đặc trưng | Feature extraction |
| Mô hình chủ đề | Topic model |
| Tìm kiếm ngữ nghĩa | Semantic search |
| Rò rỉ dữ liệu | Data leakage |
| Thực nghiệm loại trừ | Ablation study |
