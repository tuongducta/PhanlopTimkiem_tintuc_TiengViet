## 4. Tiến hóa của biểu diễn văn bản cho phân loại tiếng Việt

### 4.1 Khung phân loại

Các phương pháp được khảo sát được tổ chức thành sáu nhánh (Hình 4.1):

```
Biểu diễn văn bản tiếng Việt cho phân loại / tìm kiếm
├── A. Biểu diễn thưa
│   ├── A1. Theo âm tiết: bag-of-syllables, n-gram LM
│   └── A2. Theo từ: BoW, TF-IDF
├── B. Giảm chiều / chọn đặc trưng
│   ├── B1. Thống kê: IG, χ², MI, OR, GSS, OCFS
│   ├── B2. Lọc bằng từ điển
│   └── B3. Trích từ khóa: KeywordScore, TextRank
├── C. Biểu diễn dày học có giám sát (mạng nơ-ron trích đặc trưng)
├── D. Embedding không giám sát
│   ├── D1. Mức từ: Word2Vec, GloVe
│   ├── D2. Mức tài liệu: Doc2Vec (PV-DM / PV-DBOW)
│   └── D3. Mô hình chủ đề: LDA, Top2Vec, BERTopic
├── E. Biểu diễn dựa trên mẫu phổ biến            ← trọng tâm (Chương 5)
│   ├── E1. FI làm đặc trưng / cụm / luật
│   └── E2. FI làm đơn vị học embedding (Trans2Vec và họ phương pháp)
└── F. Mô hình ngôn ngữ tiền huấn luyện: PhoBERT, XLM-R, …
```
*Hình 4.1. Khung phân loại sáu nhánh.*

**Bảng 4.1.** Ma trận nhánh × công trình (● trọng tâm, ○ dùng làm baseline hoặc đề cập)

| Nhánh | [@hoang2007] | [@nguyen2009] | [@van2017] | [@duong2019] | [@huynh2020] | [@vinh2021] | [@huong2022] | [@nguyen2025] | [@pham2020; @luu2024] | [@trans2vec] |
|---|---|---|---|---|---|---|---|---|---|---|
| A1 | ● | ● | | | | ○ | | | | |
| A2 | ● | | ● | ● | | ● | ● | ● | | ○ |
| B1 | ● | ● | | | | ○ | | | | |
| B2 | | ● | | | | | | | | |
| B3 | | | ● | | ● | | | | | |
| C | | | ○ | | | ● | | | | |
| D1–D2 | | | | | | | ● | ● | | ○ |
| D3 | | | | | | | | ● | | |
| E1 | | | | | | | | | | ○ |
| E2 | | | | | | | | | | **●** |
| F | | | | | | | | ● | ● | |

*Các cột theo thứ tự: Hoang 2007, Nguyen 2009, Pham Van 2017, Duong 2019, Huynh 2020, Vinh 2021, Huong 2022, Nguyen 2025, Pham 2020 / Luu 2024, Trans2Vec 2018.*

Ô **E2 × tiếng Việt** trống hoàn toàn. Nhánh E1 có đúng một tiền lệ tiếng Việt: Đỗ Phúc dùng tập phổ biến và luật kết hợp để phân loại tóm tắt bài báo khoa học CNTT [@dophuc2006], không có thành phần embedding.

### 4.2 Nhánh A – Biểu diễn thưa

**A1 – Theo âm tiết.** Nguyen, Gao và Andreae biểu diễn văn bản ở mức hình thái: túi unigram âm tiết hoặc túi bigram âm tiết [@nguyen2009]. Trên tập 4 chủ đề, bigram vượt unigram với mọi thuật toán (98,1–98,6% so với 97,5–98,1%). Bigram còn có lợi rõ hơn trên tác vụ khó, tức phân loại theo thể loại *Tư liệu* hay *Phân tích*: kNN tăng từ 65,5 lên 73,2 điểm. Đổi lại, bigram chậm hơn 4,5–9,6 lần. Hoang và cộng sự xây **mô hình ngôn ngữ n-gram âm tiết** cho từng lớp và phân loại theo $c^*=\arg\max_c P(c)\prod_i P_c(w_i\mid w_{i-n+1}^{i-1})$, với làm trơn Good-Turing cho kết quả tốt nhất [@hoang2007]. Ưu điểm then chốt của nhánh A1 là **không cần tách từ**.

**A2 – Theo từ.** Túi từ có trọng số TF-IDF, kết hợp SVM, là baseline mạnh và bền nhất trong toàn bộ tài liệu khảo sát [@hoang2007; @duong2019; @huong2022]. Kết quả này nhất quán với các nghiên cứu kinh điển trên tiếng Anh [@joachims1998]. Điểm yếu cố hữu của nó là số chiều lớn (hàng chục đến hàng trăm nghìn) và không nắm được quan hệ ngữ nghĩa giữa các từ.

### 4.3 Nhánh B – Giảm chiều và chọn đặc trưng

**B1 – Chọn đặc trưng thống kê.** Hoang và cộng sự so sánh sáu tiêu chí MI, IG, χ², GSS, OR và OCFS (Optimal Orthogonal Centroid Feature Selection) trên 2.500 term. OCFS cho kết quả tốt nhất [@hoang2007]. Nguyen và cộng sự cho thấy chỉ dùng **Information Gain** đã giảm từ vựng từ 300.000 xuống khoảng 1.000 term mà độ chính xác của NB và kNN *tăng* [@nguyen2009]. Kết quả này phù hợp với nghiên cứu kinh điển của Yang và Pedersen [@yang1997].

**B2 – Lọc bằng từ điển.** Chỉ giữ gram ứng với từ có thật trong một từ điển khoảng 30.000 từ. Cách này giảm từ vựng 6–10 lần (unigram: 30.000 → 5.000; bigram: 300.000 → 30.000), cải thiện kNN rõ rệt và chỉ làm giảm nhẹ hiệu năng của SVM [@nguyen2009].

**B3 – Trích từ khóa.** Pham Van và Ta Minh chọn 10 từ khóa mỗi bài theo một điểm tần suất chuẩn hóa (KeywordScore), dựng từ điển từ khóa và biểu diễn túi từ trên đó (KEBoW). Kết hợp với mạng nơ-ron sáu lớp, họ báo cáo 99,75% [@van2017]. Mục 8.2 sẽ thảo luận độ tin cậy của con số này. Huynh và cộng sự đi xa hơn: biểu diễn mỗi văn bản *chỉ* bằng **tập từ khóa** trích bởi TextRank [@mihalcea2004], rồi phân loại bằng độ tương đồng **Jaccard** có trọng số với tập từ khóa đại diện của từng chủ đề [@huynh2020]. Độ chính xác tăng từ 75,27% với 10 từ khóa lên khoảng 90% với 50 từ khóa, sau đó bão hòa. Dùng toàn bộ từ khóa thì đạt 95,40%. Đáng chú ý, cách nhìn "**văn bản là một tập từ khóa, đo tương đồng bằng phép toán tập hợp**" chính là góc nhìn transaction mà Trans2Vec khai thác (Chương 5).

### 4.4 Nhánh C – Biểu diễn dày học có giám sát

Vinh và Kha thay bước *chọn* đặc trưng bằng bước *học* đặc trưng [@vinh2021]:
- Vector TF-IDF 10.000 chiều (unigram + bigram) đi qua một mạng hai lớp ẩn, huấn luyện với nhãn của 30 chuyên mục.
- Sau khi huấn luyện, lớp đầu ra bị bỏ đi và đầu ra **128 chiều** của lớp ẩn cuối trở thành đặc trưng cho SVM.
- Ở cùng 128 chiều, đặc trưng học được vượt χ² và OCFS.

Công trình này là mắt xích chuyển tiếp từ biểu diễn thưa sang biểu diễn dày trong tài liệu tiếng Việt. Nó cũng là **đối chứng trực tiếp nhất với Trans2Vec**: cùng 128 chiều, cùng SVM, cùng miền tin tức nhiều chuyên mục. Khác biệt căn bản nằm ở chỗ đặc trưng của Vinh và Kha **gắn với nhãn**, nên không dùng được cho tài liệu chưa gán nhãn, cho phân cụm hay cho tìm kiếm.

### 4.5 Nhánh D – Embedding không giám sát

**D1–D2.** Huong và cộng sự so sánh TF-IDF, Word2Vec, GloVe và Doc2Vec trên hai tập bình luận cảm xúc. TF-IDF thắng tuyệt đối; Word2Vec và Doc2Vec chỉ đạt khoảng 50% [@huong2022]. Nguyen và cộng sự cũng ghi nhận Word2Vec kém túi từ một chút trên review Shopee (Macro-F1 tốt nhất 0,88 so với 0,91) [@nguyen2025]. Hai kết quả này mâu thuẫn với kết quả của PV-DBOW trên dữ liệu Snippets [@trans2vec]. Mục 8.3 sẽ phân tích mâu thuẫn này.

**D3 – Mô hình chủ đề.** Các mô hình chủ đề dùng được cho cả gán nhãn chủ đề lẫn tìm kiếm:
- **LDA** [@blei2003]: mô hình xác suất.
- **Top2Vec** [@angelov2020]: embedding chung cho tài liệu và từ, tự xác định số chủ đề, có sẵn chức năng tìm kiếm ngữ nghĩa.
- **BERTopic** [@grootendorst2022]: embedding Transformer kết hợp c-TF-IDF.

Trên review Shopee tiếng Việt, LDA và BERTopic đạt độ gắn kết khoảng 0,48 và độ đa dạng trên 0,8, còn **Top2Vec kém hơn**. Không mô hình nào đủ tốt để dùng trực tiếp làm nhãn, nên các tác giả phải gán nhãn thủ công [@nguyen2025]. Trên dữ liệu tiếng Anh, Phan và cộng sự cho thấy chủ đề ẩn học từ một corpus ngoài lớn (Wikipedia) nâng độ chính xác phân loại văn bản ngắn từ 65,75% lên 82,18% [@phan2008]. Đây là bằng chứng rõ cho giá trị của **tri thức ngoài**.

### 4.6 Nhánh F – Mô hình ngôn ngữ tiền huấn luyện

PhoBERT là mô hình RoBERTa đơn ngữ tiếng Việt. Dữ liệu tiền huấn luyện khoảng 20 GB, trong đó khoảng 19 GB là **tin tức** [@phobert2020]. Điều này khiến PhoBERT đặc biệt hợp với miền tin tức. Các công trình được khảo sát cho thấy:
- Fine-tune có chiến lược (huấn luyện thêm MLM trên dữ liệu miền, đóng băng rồi mở dần các tầng, learning rate theo khối, label smoothing) đạt Macro-F1 0,7221 trên VLSP 2019 HSD. Đặc trưng từ 4–6 khối cuối tốt nhất [@pham2020].
- Các phương pháp tăng cường dữ liệu và hàm mất mát cho dữ liệu mất cân bằng chỉ cải thiện 1–2 điểm [@luu2024].
- Trên review Shopee, PhoBERT kết hợp hồi quy logistic đạt Macro-F1 0,96, vượt mọi biểu diễn khác ít nhất 5 điểm. Đổi lại, nó cần GPU và khoảng 41 phút huấn luyện, so với khoảng 22 giây của TF-IDF trên CPU [@nguyen2025].

### 4.7 Nhận xét chung

Ba xu hướng rút ra từ chương này:
1. **Từ chọn sang học:** đặc trưng ngày càng được *học* thay vì *chọn* (B → C → D → F).
2. **Từ thưa sang dày:** chiều biểu diễn giảm từ $10^4$–$10^5$ xuống $10^2$–$10^3$.
3. **Từ dữ liệu nội tại sang tri thức ngoài:** từ chỉ học trên corpus đích sang tận dụng corpus ngoài (LDA trên Wikipedia, tiền huấn luyện PhoBERT).

Nhánh E nằm ở một vị trí đặc biệt. Nó *học* biểu diễn dày như C, D, F, nhưng đơn vị học là **mẫu do khai phá dữ liệu phát hiện**, nên giữ được tính diễn giải của nhánh B. Đồng thời nó **không giám sát** như D. Chương 5 phân tích nhánh này.
