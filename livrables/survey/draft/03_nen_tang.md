## 3. Kiến thức nền tảng

### 3.1 Bài toán phân loại và tìm kiếm văn bản

Cho tập tài liệu $D=\{d_1,\dots,d_N\}$ và tập chuyên mục $C=\{c_1,\dots,c_k\}$. **Phân loại văn bản** là học hàm $F: D\times C\to\{\text{đúng},\text{sai}\}$, với $F(d_i,c_j)=\text{đúng}$ nếu $d_i$ thuộc $c_j$ [@duong2019; @sebastiani2002]. Có ba trường hợp:
- **nhị phân:** $k=2$;
- **đa lớp:** $k>2$, mỗi tài liệu thuộc đúng một lớp. Đây là trường hợp phân loại chuyên mục tin tức;
- **đa nhãn:** một tài liệu có thể thuộc nhiều lớp [@nguyen2025].

Quy trình chuẩn gồm năm bước: tiền xử lý, biểu diễn, giảm chiều, huấn luyện bộ phân loại, đánh giá [@duong2019; @van2017].

**Tìm kiếm ngữ nghĩa** được hiểu ở đây là một bài toán xếp hạng. Cho một truy vấn $q$, là một chuỗi từ khóa hoặc một tài liệu, ta xếp hạng các tài liệu trong $D$ theo độ tương đồng $\text{sim}(\phi(q),\phi(d))$, với $\phi$ là hàm biểu diễn. Khi $\phi$ cho ra vector dày, $\text{sim}$ thường là cosine và bài toán trở thành tìm láng giềng gần nhất. Đây là nguyên lý của dense retrieval [@karpukhin2020; @reimers2019]. Điểm then chốt cho đề tài: **nếu cùng một $\phi$ dùng được cho cả phân loại và tìm kiếm, hệ thống chỉ cần học và lưu một biểu diễn duy nhất.**

### 3.2 Khai phá tập phổ biến

Cho tập item $I=\{i_1,\dots,i_M\}$ và cơ sở dữ liệu transaction $D=\{T_1,\dots,T_N\}$ với $T_i\subseteq I$. **Độ hỗ trợ** (support) của itemset $X\subseteq I$ là

$$\text{sup}(X)=\frac{|\{T_i\in D : X\subseteq T_i\}|}{|D|}.$$

$X$ là **tập phổ biến** (frequent itemset, FI) nếu $\text{sup}(X)\ge\delta$, với $\delta\in[0,1]$ là ngưỡng hỗ trợ tối thiểu [@agrawal1994; @fournier2017]. Tính chất **đóng xuống** (anti-monotone) là nền tảng của mọi thuật toán khai phá: mọi tập con của một tập phổ biến cũng phổ biến.

Ba thuật toán chính liên quan tới đề tài:
- **Apriori** [@agrawal1994]: sinh ứng viên theo từng mức độ dài và tỉa nhờ tính đóng xuống. Đơn giản nhưng phải quét dữ liệu nhiều lần.
- **FP-Growth** [@han2000]: nén cơ sở dữ liệu vào cấu trúc cây FP-tree và khai phá đệ quy, **không sinh ứng viên**. Thường nhanh hơn Apriori nhiều bậc trên dữ liệu dày. Đây là thuật toán được đề xuất cho hệ thống ở Chương 9.
- **Tập phổ biến đóng** (closed itemsets), ví dụ thuật toán CHARM [@zaki2002]: chỉ giữ các FI không có tập cha nào cùng độ hỗ trợ. Đây là biểu diễn nén *không mất thông tin* của toàn bộ tập FI. Như Mục 5.6 sẽ phân tích, nó là công cụ chính để chống bùng nổ số FI khi transaction dài.

**Ví dụ.** Với δ = 0,6 trên năm transaction {a,b,c}, {b,c,d}, {a,d}, {b,c,d,e}, {a,c,d}, ta thu được sáu FI: {a}, {b}, {c}, {d}, {b,c}, {c,d}. Mỗi transaction có thể được viết lại thành tập các FI mà nó chứa [@trans2vec].

**Biểu diễn bằng FI và vấn đề của nó.** Cách cổ điển là biểu diễn mỗi transaction bằng vector nhị phân $f(T)=[x_1,\dots,x_F]$, với $x_i=1$ nếu $X_i\subseteq T$. Cách này gặp hai vấn đề [@trans2vec]:
1. **Số chiều rất lớn:** số FI có thể vượt $10^5$ khi δ < 5%.
2. **Rất thưa.**

Các giải pháp đi trước chọn **FI phân biệt** theo information gain hoặc độ chênh support giữa các lớp [@cheng2007], hoặc xây **bộ phân lớp dựa trên luật kết hợp** [@liu1998]. Cả hai đều cần nhãn. Hệ quả là biểu diễn gắn với một tác vụ duy nhất và không chuyển sang phân cụm hay tìm kiếm được.

### 3.3 Học biểu diễn phân tán

**Word2Vec** [@mikolov2013] học vector cho từ bằng cách dự đoán từ ngữ cảnh. Mô hình Skip-gram dự đoán các từ xung quanh từ trung tâm; mô hình CBOW làm ngược lại. Hàm softmax trên toàn bộ từ vựng quá tốn kém, nên được xấp xỉ bằng **negative sampling**. Với cặp (đơn vị mục tiêu $u$, ngữ cảnh $c$) và $K$ mẫu âm $u_n$ rút từ phân phối nhiễu $P$, hàm mục tiêu là:

$$\mathcal{L}=-\log\sigma\big(\mathbf{v}_u\cdot\mathbf{h}_c\big)-\sum_{n=1}^{K}\mathbb{E}_{u_n\sim P}\log\sigma\big(-\mathbf{v}_{u_n}\cdot\mathbf{h}_c\big),$$

với $\sigma$ là hàm sigmoid.

**Paragraph Vector** (Doc2Vec) [@le2014] mở rộng ý tưởng cho tài liệu: mỗi tài liệu có thêm một vector riêng $\mathbf{f}(d)$. Mô hình có hai biến thể:
- **PV-DM** (Distributed Memory): ghép vector tài liệu với vector các từ ngữ cảnh để dự đoán từ tiếp theo.
- **PV-DBOW** (Distributed Bag-of-Words): chỉ dùng $\mathbf{f}(d)$ để dự đoán các từ *có trong* tài liệu, bỏ qua thứ tự. Đây chính là công thức trên với $\mathbf{h}_c=\mathbf{f}(d)$ và $u$ là một từ thuộc $d$.

**PV-DBOW là lõi của Trans2Vec**, nên ba tính chất của nó cần được ghi nhận:
1. **Mô hình coi tài liệu như một *tập* đơn vị.** Vì vậy nó áp dụng được nguyên dạng cho dữ liệu transaction, và các đơn vị không nhất thiết phải là từ.
2. **Vector của tài liệu mới phải được *suy luận*** bằng cách giữ cố định vector đơn vị và tối ưu riêng $\mathbf{f}(d_{\text{mới}})$ vài vòng gradient. Nói cách khác, không có công thức dạng đóng (closed-form) để tính vector cho tài liệu mới.
3. **Hiệu năng nhạy với cấu hình** (số chiều, số epoch, kích thước cửa sổ, tần suất tối thiểu) và với lượng dữ liệu. Lau và Baldwin cho thấy Doc2Vec, và đặc biệt PV-DBOW, cho kết quả vững khi được cấu hình đúng và huấn luyện trên đủ dữ liệu. Họ cũng đưa ra bộ siêu tham số khuyến nghị [@lau2016]. Tính chất này giúp giải thích một mâu thuẫn quan trọng trong tài liệu tiếng Việt (Mục 8.3).

**Embedding ngữ cảnh.** BERT [@devlin2019] và các biến thể như PhoBERT [@phobert2020] tạo vector *phụ thuộc ngữ cảnh* bằng kiến trúc Transformer tiền huấn luyện trên corpus lớn. Để tìm kiếm, vector câu hoặc tài liệu thường được lấy bằng Sentence-BERT [@reimers2019] hoặc bằng cách gộp đầu ra của các tầng cuối [@pham2020].

### 3.4 Độ đo đánh giá

- **Phân loại:** Accuracy; Precision, Recall, F1 theo trung bình macro hoặc micro. Với dữ liệu mất cân bằng, **Macro-F1** được khuyến nghị vì nó coi các lớp ngang nhau, trong khi accuracy thiên về lớp đa số [@luu2024]. Với bài toán đa nhãn có thêm Hamming loss [@nguyen2025].
- **Tìm kiếm:** Precision@k, Mean Average Precision (MAP), và nDCG@k [@jarvelin2002].
- **Chủ đề / phân cụm:** độ gắn kết chủ đề $C_v$ và độ đa dạng chủ đề [@nguyen2025]; NMI và ARI khi so cụm với nhãn.
