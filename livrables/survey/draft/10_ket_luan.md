## 10. Kết luận và hướng phát triển

### 10.1 Tóm tắt trả lời các câu hỏi nghiên cứu

| RQ | Trả lời | Mức chắc chắn |
|---|---|---|
| **RQ1** | Thách thức chính là tách từ (nhập nhằng nghĩa), bảng mã và dấu thanh, và danh sách từ dừng chủ quan. Vai trò của tiền xử lý **đi theo đường cong chữ U**: giảm dần từ biểu diễn thưa tới Transformer, rồi trở lại thành cốt lõi với biểu diễn dựa trên mẫu. Tách từ rẻ [@le2013vnlp] và vẫn có ích trên tin tức (+1–3 điểm). Với tìm kiếm, dấu thanh cần hai dạng chỉ mục: giữ dấu cho truy vấn có dấu, gộp dấu cho truy vấn không dấu | Cao |
| **RQ2** | Biểu diễn thưa có chọn đặc trưng đủ cho tác vụ dễ; biểu diễn dày tạo khác biệt ở tác vụ khó; tri thức ngoài cho hiệu năng cao nhất với chi phí cao nhất. Trên VNTC-10, so sánh đối đầu của đề tài cho thứ tự: thưa ≥ dày có giám sát > embedding không giám sát ở phân loại, ngược lại ở tìm kiếm. Nhánh dựa trên mẫu, embedding đóng băng và đồ thị chưa có công trình tiếng Việt | Cao với VNTC; thấp với corpus khó |
| **RQ3** | Trên Snippets (tiếng Anh), FI làm giàu embedding thêm 2,7 điểm [@trans2vec]. **Thực nghiệm (Mục 9.5) không tái hiện được mức này trên VNTC-10:** khi đánh giá nhất quán, FI chỉ đóng góp −0,3 đến +0,9 điểm Macro-F1; hạ δ để có số FI gấp 12 lần cũng chỉ nâng lên +0,6. Trên chính Snippets, mức đóng góp là +0,7 khi chạy như mã gốc và +3,1 khi đánh giá inductive, nên FI có thể có ích thật với văn bản ngắn; hồ sơ dữ liệu không giải thích được khác biệt này. **Về loại FI:** FI đóng không tạo khác biệt vì gần như mọi FI trên tin tức đã đóng; chọn FI ổn định [@zhang2025] không hơn chọn ngẫu nhiên cùng số lượng. Giá trị của FI cho tin tức tiếng Việt nằm ở **tìm kiếm**, ở **diễn giải** chuyên mục, và ở **chi phí thấp** | Trung bình (một corpus tiếng Việt; E9 chạy 3 seed) |
| **RQ4** | SVM là chuẩn so sánh, LR là lựa chọn triển khai và tốt hơn SVM trên embedding. Nối nhiều embedding có lợi nhỏ (CAT +0,008). Toàn bộ đường ống Trans2Vec chạy trên CPU trong một đến hai phút. Tìm kiếm có p50 dưới 20 ms trong benchmark, và khoảng 50–170 ms trong ứng dụng (gồm khử trùng). Trans2Vec nằm giữa TF-IDF và các mô hình cần GPU (PhoBERT, LLM đóng băng) trên trục chi phí | Cao |
| **RQ5** | Chưa đủ chuẩn: dữ liệu phân mảnh, VNTC có bài trùng giữa các tập, giao thức không thống nhất. Có tám mối đe dọa đến tính hợp lệ, sáu mối được đề tài đo bằng số (Bảng 8.4). Bài đề xuất một giao thức tối thiểu (Mục 7.3) | Cao |
| **RQ6** | Một biểu diễn dùng chung được cho cả hai tác vụ (Trans2Vec-JOI), nhưng mô hình tốt nhất cho từng tác vụ khác nhau (CAT cho phân loại, JOI cho tìm kiếm). Embedding hơn biểu diễn thưa khoảng 0,07 nDCG@10; kết hợp với BM25 nhích thêm ở top-10, nhất là với truy vấn ngắn. Nhãn thay thế "cùng chuyên mục" chỉ cho **cận trên lạc quan**: nó quá thô để so chỉ mục, và Paragraph Vector yếu hẳn khi có nhãn liên quan thật [@minaee2021] | Trung bình |

### 10.2 Khoảng trống nghiên cứu

Phân loại tin tức tiếng Việt đã đi qua ba thế hệ biểu diễn: thưa [@hoang2007; @hien2024], dày có giám sát [@vinh2021; @hien2024] và mô hình tiền huấn luyện [@pham2020; @luu2024; @nguyen2025]. Khai phá tập phổ biến đã có cơ sở lý thuyết và thuật toán hiện đại [@zhang2025; @trasierras2024], nhưng các công trình này dừng ở tốc độ và tính chất, không chạm tới tác vụ hạ nguồn. Tập phổ biến đã được dùng cho văn bản, kể cả tiếng Việt, nhưng chỉ dưới dạng đặc trưng thưa hoặc luật [@dophuc2006; @beil2002; @fung2003]. Hai bài tổng quan lớn về phân loại văn bản không có nhánh nào cho biểu diễn dựa trên mẫu phổ biến [@li2022; @minaee2021].

Vì vậy, hướng **học embedding từ mẫu phổ biến**, gồm Trans2Vec và họ phương pháp của nó [@trans2vec; @sqn2vec; @gefsg2018], **chưa được đánh giá trên văn bản tiếng Việt, trên văn bản dài như tin tức, và cho tìm kiếm**. Thực nghiệm của đề tài là bước đầu lấp khoảng trống này. Kết quả cho thấy lợi ích của tập phổ biến phụ thuộc mạnh vào dữ liệu và vào giao thức đánh giá; khi đánh giá đúng, lợi ích trên văn bản tiếng Việt dài thấp hơn nhiều so với mức công bố trên văn bản ngắn tiếng Anh.

### 10.3 Hướng phát triển

1. **Tìm lời giải cho câu hỏi M7:** vì sao FI giúp văn bản ngắn tiếng Anh mà không giúp tin tức tiếng Việt. Kiểm chứng rẻ nhất là chạy cùng giao thức trên một tập văn bản ngắn tiếng Việt, ví dụ tiêu đề tin tức.
2. **Mở rộng thực nghiệm ở Mục 9.5:** chạy nhiều seed cho mọi bảng; thêm một corpus khó (≥ 25 chuyên mục), PhoBERT, Top2Vec và một baseline embedding câu đóng băng theo mô thức của [@liu2024]; tìm cách đưa lại thông tin tần suất vào Trans2Vec (H1), vì phép ghép thẳng với TF-IDF chưa hiệu quả.
3. **Xây tập truy vấn có nhãn liên quan do người gán** cho tin tức tiếng Việt, để đánh giá tìm kiếm không còn phụ thuộc nhãn thay thế.
4. **Mở rộng sang mẫu tuần tự** với Sqn2Vec [@sqn2vec], để giữ thứ tự từ, và sang **đồ thị từ** [@rousseau2015; @gefsg2018].
5. **Kết hợp tri thức ngoài:** khởi tạo vector item từ embedding tiền huấn luyện, hoặc dùng FI làm tín hiệu bổ sung cho bộ mã hóa PhoBERT.
6. **Phân loại phân cấp:** tận dụng cấu trúc chuyên mục cha – con (VNTC Level 1 – Level 2) và cây chủ đề từ FI [@fung2003].
7. **Xây dựng một benchmark tin tức tiếng Việt công khai, khó, có giao thức chuẩn**, đã khử trùng, cho cả phân loại lẫn tìm kiếm, theo tinh thần của VN-MTEB [@vnmteb2026] nhưng trên dữ liệu gốc tiếng Việt thay vì dữ liệu dịch.

---

## Phụ lục A. Bảng tóm tắt các công trình chính (vòng 1 và vòng 3)

| Công trình | Năm | Dữ liệu | Biểu diễn | Bộ phân loại | Kết quả chính | Nhánh |
|---|---|---|---|---|---|---|
| Hoang và cs. [@hoang2007] | 2007 | VNTC 10 / 27 lớp | TF-IDF + OCFS; n-gram âm tiết | SVM; NB-LM | 96,21% / 95,58% | A1, A2, B1 |
| Nguyen và cs. [@nguyen2009] | 2009 | 4 lớp; 2 lớp thể loại | Bag-of-syllables; IG; từ điển | NB, kNN, SVM | 98,6%; 89,8% | A1, B1, B2 |
| Pham Van & Ta Minh [@van2017] | 2017 | VNTC | KEBoW | MLP 6 lớp | 99,75% (nghi rò rỉ) | B3 |
| Duong & Hoang [@duong2019] | 2019 | VNNews-01, 25 lớp | TF-IDF | 8 bộ phân loại | F1 0,749 | A2 |
| Huynh và cs. [@huynh2020] | 2020 | 15 lớp | Từ khóa TextRank | Jaccard | 95,40% | B3 |
| Pham và cs. [@pham2020] | 2020 | VLSP HSD | PhoBERT | Fine-tune | Macro-F1 0,7221 | F |
| Vinh & Kha [@vinh2021] | 2021 | 30 lớp | MLP-128 | SVM | > χ², OCFS | C |
| Huong và cs. [@huong2022] | 2022 | Cảm xúc | TF-IDF, W2V, GloVe, D2V | 5 bộ phân loại | TF-IDF 86,8% | D1, D2 |
| Luu và cs. [@luu2024] | 2024 | ViHSD, UIT-ViCTSD | 7 mô hình BERT | Fine-tune + EDA | Macro-F1 0,7463 | F |
| Nguyen và cs. [@nguyen2025] | 2025 | Shopee, đa nhãn | BoW … PhoBERT; LDA, Top2Vec, BERTopic | LR, SVM, XGB | Macro-F1 0,96 | D, F |
| Nguyen và cs. [@trans2vec] | 2018 | Snippets + 3 tập | Trans2Vec | SVM | 79,05% (Snippets) | E2 |
| Le và cs. [@le2013vnlp] | 2013 | 2 triệu âm tiết; 140 bài | Bộ công cụ NLP tiếng Việt | — | Tách từ 6 s; NER F1 0,58 | Tiền xử lý |
| Hien và cs. [@hien2024] | 2024 | VNTC 10 / 27 lớp | BoW, TF-IDF (+SVD) | LR, DT, SVM, LSTM, CNN | 94,52% / 89,43% | A2, B1, C |
| Liu và cs. [@liu2024] | 2024 | 5 tập tiếng Anh | Embedding LLaMA2 đóng băng | Bộ phân loại nhẹ | Accuracy TB 0,962 | F2 |
| Onan [@onan2023] | 2023 | 8 tập tiếng Anh | Đồ thị phân cấp + BERT | FC | 98,75% (R8) | G |
| Zhang và cs. [@zhang2025] | 2025 | retail, mushroom | Tập phổ biến đóng, CICFI | — | Lý thuyết | E3 |
| Trasierras và cs. [@trasierras2024] | 2024 | 14 tập transaction | 9 thuật toán khai phá FI | — | LCM, FP-Growth nhanh nhất | E3 |
| Li và cs. [@li2022]; Minaee và cs. [@minaee2021] | 2022; 2021 | Tổng quan | Khung phân loại, dataset, độ đo | — | Khung tham chiếu | — |

## Phụ lục B. Thuật ngữ Việt – Anh

| Tiếng Việt | Tiếng Anh |
|---|---|
| Tập phổ biến | Frequent itemset (FI) |
| Tập phổ biến đóng | Closed itemset |
| Lớp tương đương | Equivalence class |
| Khoảng tin cậy | Confidence interval |
| Hồ sơ dữ liệu | Data heterogeneity profile |
| Học transductive / inductive | Transductive / inductive learning |
| Tìm kiếm kết hợp | Hybrid search |
| Chỉ mục vector xấp xỉ | Approximate nearest neighbor (ANN) index |
| Gộp dấu | Diacritic folding |
| Mối đe dọa đến tính hợp lệ | Threat to validity |
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
