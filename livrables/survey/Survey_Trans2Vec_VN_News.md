# Biểu diễn văn bản dựa trên mẫu phổ biến cho hệ thống tìm kiếm và phân loại chuyên mục tin tức tiếng Việt: Khảo sát và đề xuất hướng tiếp cận Trans2Vec

*Bài khảo sát — Môn Tri thức dữ liệu, Chương trình Sau đại học, Trường Đại học Công nghệ TP.HCM (HUTECH)*

---

## Tóm tắt

Phân loại chuyên mục tin tức tiếng Việt đã được nghiên cứu gần hai thập kỷ, với các cách biểu diễn văn bản đi từ túi từ (bag-of-words) và n-gram âm tiết, qua chọn đặc trưng thống kê và trích từ khóa, tới embedding học bằng mạng nơ-ron và mô hình ngôn ngữ tiền huấn luyện như PhoBERT. Song song với dòng nghiên cứu đó, cộng đồng khai phá dữ liệu đã phát triển hướng *học biểu diễn dựa trên mẫu phổ biến*. Đại diện tiêu biểu là Trans2Vec: phương pháp kết hợp tập phổ biến (frequent itemsets) với mô hình Paragraph Vector để học vector cho dữ liệu dạng tập hợp mà không cần nhãn.

Bài khảo sát này hệ thống hóa 11 công trình chính và 27 tài liệu bổ sung theo một khung phân loại sáu nhánh biểu diễn. Bài phân tích kết quả theo các nhóm có thể so sánh được, chỉ ra năm mâu thuẫn trong tài liệu, và đánh giá phản biện Trans2Vec qua bảy hạn chế khi áp dụng cho tin tức tiếng Việt. Kết quả khảo sát cho thấy ba điểm. (i) Độ khó của corpus và giao thức đánh giá chi phối kết quả nhiều hơn thuật toán: kết quả báo cáo trên cùng loại dữ liệu dao động từ F1 0,749 đến accuracy 99,75%. (ii) Vai trò của tiền xử lý tiếng Việt giảm dần qua các thế hệ biểu diễn nhưng trở lại thành yếu tố cốt lõi với biểu diễn dựa trên mẫu. (iii) Hướng học embedding từ tập phổ biến chưa từng được áp dụng cho văn bản tiếng Việt, cho văn bản dài như tin tức, hay cho bài toán tìm kiếm.

Từ đó, bài đề xuất kiến trúc một hệ thống dùng chung một biểu diễn Trans2Vec cho cả phân loại chuyên mục và tìm kiếm ngữ nghĩa, kèm giao thức đánh giá chuẩn hóa trên corpus công khai VNTC. Thực nghiệm sơ bộ trên toàn bộ VNTC-10 (33.759 bài huấn luyện, 50.373 bài kiểm tra) cho thấy: Trans2Vec chưa vượt TF-IDF ở phân loại (Macro-F1 0,849 so với 0,907), và tập phổ biến chỉ đóng góp −0,3 đến +0,9 điểm. Ngược lại, ở tìm kiếm, Trans2Vec là biểu diễn không giám sát tốt nhất (nDCG@10 0,809 so với 0,740 của TF-IDF), đồng thời cho phần giải thích chuyên mục dễ đọc với chi phí dưới một phút trên CPU. Thực nghiệm cũng phát hiện một cái bẫy đánh giá: vector huấn luyện và vector kiểm tra không được sinh cùng quy trình có thể làm sai lệch kết quả tới 8 điểm và tạo ra những cải thiện giả.

**Từ khóa:** phân loại văn bản tiếng Việt; tin tức; tập phổ biến; Trans2Vec; Paragraph Vector; học biểu diễn; tìm kiếm ngữ nghĩa; khai phá tri thức.

---

## Mục lục

1. Giới thiệu
2. Đặc thù xử lý văn bản tiếng Việt
3. Kiến thức nền tảng
4. Tiến hóa của biểu diễn văn bản cho phân loại tiếng Việt
5. Trans2Vec và mô thức biểu diễn dựa trên mẫu phổ biến
6. Bộ phân loại và đánh đổi hiệu năng – chi phí
7. Dữ liệu và giao thức đánh giá
8. So sánh tổng hợp và thảo luận
9. Đề xuất hệ thống tìm kiếm và phân loại chuyên mục dựa trên Trans2Vec
10. Kết luận và hướng phát triển

Phụ lục A: Bảng tóm tắt công trình · Phụ lục B: Thuật ngữ Việt – Anh · Tài liệu tham khảo

## 1. Giới thiệu

### 1.1 Bối cảnh

Báo điện tử là một trong những nguồn văn bản tiếng Việt lớn và tăng nhanh nhất. Mỗi ngày, hàng chục trang tin như VnExpress, Tuổi Trẻ, Thanh Niên, Dân trí xuất bản hàng nghìn bài, và mỗi bài được biên tập viên xếp vào một chuyên mục: Thời sự, Kinh doanh, Thể thao, Sức khỏe, v.v. Hai nhu cầu xử lý cơ bản nảy sinh từ khối dữ liệu này:
- **Phân loại chuyên mục tự động:** gán chuyên mục cho bài mới, cho bài từ nguồn chưa được phân loại, hoặc thống nhất hệ thống chuyên mục khác nhau giữa các trang.
- **Tìm kiếm:** truy xuất những bài *liên quan về nội dung* tới một truy vấn hay một bài đang đọc, vượt ra ngoài việc khớp từ khóa chính xác.

Về hình thức, phân loại văn bản là bài toán học một ánh xạ từ tập tài liệu vào tập chuyên mục định trước [1, 2]. Chất lượng của mọi bộ phân loại, cũng như mọi hệ thống tìm kiếm dựa trên độ tương đồng, phụ thuộc trước hết vào **cách biểu diễn văn bản thành vector**. Với tiếng Việt, câu hỏi biểu diễn càng khó hơn: ranh giới từ không trùng với khoảng trắng, và phần lớn từ có nghĩa được ghép từ hai âm tiết trở lên [3, 4].

### 1.2 Động lực: điểm giao giữa khai phá mẫu và học biểu diễn

Nghiên cứu phân loại văn bản tiếng Việt đã trải qua ba thế hệ biểu diễn:
1. **Biểu diễn thưa và chọn đặc trưng:** túi từ và TF-IDF [2], n-gram âm tiết, các tiêu chí chọn đặc trưng như Information Gain, χ² hay OCFS [3, 4], và các phương pháp trích từ khóa [5, 6].
2. **Biểu diễn dày học từ dữ liệu:** mạng nơ-ron trích đặc trưng [7] và embedding tĩnh Word2Vec, GloVe, Doc2Vec [8].
3. **Mô hình ngôn ngữ tiền huấn luyện:** họ BERT, đặc biệt PhoBERT [9, 10, 11, 12].

Ở một nhánh khác, cộng đồng khai phá dữ liệu (KDD) từ lâu đã biểu diễn dữ liệu dạng tập hợp bằng **tập phổ biến** (frequent itemsets): những tổ hợp phần tử cùng xuất hiện với tần suất vượt một ngưỡng [13, 14]. Tập phổ biến đã được dùng cho phân cụm và phân loại văn bản [15, 16, 17], kể cả văn bản tiếng Việt [18]. Tuy nhiên, cách dùng này gặp hai trở ngại cố hữu: số chiều rất lớn và vector rất thưa.

Năm 2018, Nguyen và cộng sự đề xuất **Trans2Vec** [19]: coi mỗi tập phổ biến như một "từ" và học vector cho mỗi transaction bằng mô hình Paragraph Vector [20]. Kết quả là một biểu diễn **dày, ít chiều, không cần nhãn**, nhưng vẫn mang tri thức đồng xuất hiện bậc cao của tập phổ biến. Áp vào văn bản, mỗi bài báo là một transaction và mỗi từ là một item. Khi đó tập phổ biến chính là các cụm từ hay đi cùng nhau, chẳng hạn {chứng_khoán, cổ_phiếu, sàn} cho chuyên mục Kinh doanh. Với tiếng Việt, có thêm một điểm đáng chú ý: nếu item là âm tiết, các tập phổ biến hai phần tử có khả năng tự "khôi phục" từ ghép, ví dụ {chứng, khoán}. Nhờ vậy hệ thống phần nào bớt phụ thuộc vào bộ tách từ.

Dù vậy, cho tới nay chưa có công trình nào đưa hướng tiếp cận này vào văn bản tiếng Việt, và cũng chưa có công trình nào dùng nó cho bài toán tìm kiếm. Bài khảo sát này nhằm lấp khoảng trống đó ở mức tổng quan và đề xuất.

### 1.3 Câu hỏi nghiên cứu

Bài khảo sát được tổ chức quanh năm câu hỏi nghiên cứu (RQ):

| RQ | Câu hỏi |
|---|---|
| **RQ1** | Tiếng Việt đặt ra những thách thức tiền xử lý nào (tách từ, dấu thanh, bảng mã, từ dừng), và tầm quan trọng của chúng thay đổi thế nào theo từng họ biểu diễn? |
| **RQ2** | Các họ biểu diễn văn bản (thưa, chọn đặc trưng, từ khóa, dày có giám sát, embedding tĩnh, Transformer) so sánh với nhau ra sao trên tiếng Việt? |
| **RQ3** | Tri thức đồng xuất hiện dưới dạng tập phổ biến có làm giàu được embedding tài liệu không, và Trans2Vec cần điều chỉnh gì để áp dụng cho tin tức tiếng Việt? |
| **RQ4** | Bộ phân loại nào phù hợp với từng loại biểu diễn, và chi phí tính toán đổi lại được gì? |
| **RQ5** | Các tập dữ liệu và giao thức đánh giá hiện có có đủ chuẩn để so sánh công bằng giữa các nghiên cứu không? |

### 1.4 Phương pháp khảo sát

Tài liệu được thu thập theo hai vòng:
- **Vòng 1:** 11 công trình nòng cốt do người thực hiện tuyển chọn. Gồm 10 nghiên cứu phân loại văn bản tiếng Việt giai đoạn 2007–2025 và bài gốc Trans2Vec. Mỗi công trình được đọc toàn văn và lập phiếu đọc theo mẫu thống nhất: bài toán, phương pháp, dữ liệu, kết quả, hạn chế, liên hệ với Trans2Vec.
- **Vòng 2:** 27 tài liệu bổ sung, tìm theo bốn hướng:
  - các công trình cùng mô thức với Trans2Vec;
  - nền tảng khai phá tập phổ biến;
  - tập phổ biến cho văn bản;
  - tài nguyên và benchmark tiếng Việt.

  Mọi tài liệu bổ sung đều được xác minh thông tin thư mục qua nguồn chính thức (ACL Anthology, DBLP, kho của nhà xuất bản hoặc của trường).

Kết quả được tổng hợp vào các ma trận đối chiếu (khung phân loại × tài liệu, dataset, kết quả theo nhóm so sánh được, tiền xử lý × biểu diễn). Các ma trận này là xương sống của các Chương 4–8. Ba công trình về phát hiện ngôn từ thù ghét và phân tích cảm xúc [8, 10, 11] nằm ngoài miền tin tức. Chúng được giữ lại vì chứa bằng chứng về biểu diễn và tiền xử lý tiếng Việt có thể chuyển giao, nhưng không đưa vào so sánh trực tiếp với kết quả trên tin tức.

### 1.5 Đóng góp

Bài khảo sát có ba đóng góp:
1. **Hệ thống hóa** các phương pháp biểu diễn văn bản cho phân loại tiếng Việt theo khung sáu nhánh, và lần đầu đặt **mô thức biểu diễn dựa trên mẫu phổ biến** (pattern-based embedding) vào bức tranh đó.
2. **Phân tích phản biện** Trans2Vec qua bảy hạn chế khi áp dụng cho tin tức tiếng Việt. Mỗi hạn chế đi kèm giải pháp có cơ sở tài liệu và cách kiểm chứng.
3. **Đề xuất** kiến trúc hệ thống dùng một biểu diễn chung cho phân loại và tìm kiếm, cùng **giao thức đánh giá chuẩn hóa** khắc phục các vấn đề về tính so sánh được, rò rỉ dữ liệu và khả năng tái lập đã phát hiện trong tài liệu.

### 1.6 Cấu trúc bài

- Chương 2: đặc thù tiếng Việt.
- Chương 3: nền tảng khai phá tập phổ biến và học biểu diễn phân tán.
- Chương 4: tiến hóa của biểu diễn văn bản tiếng Việt.
- Chương 5: phân tích sâu Trans2Vec và họ phương pháp của nó.
- Chương 6: bộ phân loại và chi phí.
- Chương 7: dữ liệu và giao thức đánh giá.
- Chương 8: so sánh tổng hợp và các mâu thuẫn.
- Chương 9: đề xuất hệ thống.
- Chương 10: kết luận.

## 2. Đặc thù xử lý văn bản tiếng Việt

### 2.1 Âm tiết, từ và bài toán tách từ

Tiếng Việt là ngôn ngữ đơn lập. Đơn vị viết cách nhau bằng khoảng trắng là **âm tiết** (Hoang và cộng sự gọi là *morpho-syllable* [3]), chứ không phải từ. Một âm tiết có thể là một từ, một hình vị, hoặc không mang nghĩa độc lập. Nguyen và cộng sự ghi nhận **hơn 80% từ tiếng Việt có hai âm tiết** [4]. Vì vậy việc xác định ranh giới từ, tức **tách từ** (word segmentation), là bước tiền xử lý đặc thù, và cách tách khác nhau có thể dẫn tới nghĩa khác nhau. Ba ví dụ kinh điển trong các công trình được khảo sát:

| Câu | Cách tách 1 | Cách tách 2 | Hệ quả với phân loại | Nguồn |
|---|---|---|---|---|
| "Một luật gia cầm cự với tình hình hiện nay" | luật_gia / cầm_cự → *Chính trị – Xã hội* | gia_cầm → *Sức khỏe (cúm gia cầm)* | Đổi chuyên mục | [3] |
| "học sinh ra từ hành" | học / sinh_ra / từ / hành | học_sinh / ra / từ / hành | Cả hai cách đều gồm các từ có thật | [4] |
| "Bảo lãnh bằng chứng khoán" | bảo_lãnh / bằng / chứng_khoán → *Tài chính* | bảo_lãnh / bằng_chứng / khoán → vô nghĩa | Từ khóa sai, phân loại sai | [5] |

Các công trình xử lý vấn đề này theo hai hướng:
- **Dùng bộ tách từ:** MaxEnt [3], vnTokenizer [5], pyvi [8, 11], VnCoreNLP/RDRSegmenter [10, 21]. Rủi ro là lỗi tách từ lan truyền sang các bước sau. Pham Van và Ta Minh xếp sự phụ thuộc vào thư viện tách từ vào danh sách hạn chế chính [5].
- **Tránh tách từ:** làm việc trực tiếp với âm tiết, qua bag-of-syllables [4], mô hình ngôn ngữ n-gram âm tiết [3], hoặc tổ hợp unigram + bigram [7]. Hoang và cộng sự cho thấy mô hình n-gram âm tiết đạt độ chính xác ngang SVM trên túi từ (95,58% so với 96,21%) mà không cần tách từ hay chọn đặc trưng [3].

### 2.2 Bảng mã, dấu thanh và biến thể chính tả

Văn bản tiếng Việt điện tử từng tồn tại ở nhiều bảng mã (TELEX, VNI, TCVN3, VIQR, Unicode). Vị trí dấu thanh cũng không thống nhất (ví dụ "hoà" và "hòa"), và có biến thể chính tả như "thời kỳ" và "thời kì". Nếu không chuẩn hóa, cùng một từ sẽ thành nhiều đặc trưng khác nhau. Các công trình sớm đều xây bước chuẩn hóa riêng [3, 4]. Ngày nay chuẩn hóa Unicode vẫn được dùng như bước đầu tiên, kể cả trong các hệ thống dựa trên Transformer [10].

### 2.3 Từ dừng và từ vựng

Danh sách từ dừng tiếng Việt thường được **xây thủ công** và thiếu chuẩn chung: khoảng 900 từ trong [3], khoảng 2.000 từ trong [5]. Tính chủ quan của danh sách được chính các tác giả nêu là một nguồn sai số [5]. Một hướng khác là lọc từ vựng bằng từ điển, chỉ giữ các gram ứng với từ có thật. Cách này giảm từ vựng bigram từ 300.000 xuống 30.000 và đặc biệt có lợi cho kNN, vốn nhạy với đặc trưng nhiễu [4].

### 2.4 Tầm quan trọng của tiền xử lý thay đổi theo họ biểu diễn

Một quan sát xuyên suốt của khảo sát này: tiền xử lý **không có vai trò cố định**, mà phụ thuộc vào cách biểu diễn được dùng (Bảng 2.1).
- **Với mô hình Transformer:** Luu và cộng sự cho thấy các bước tiền xử lý truyền thống (bỏ từ dừng, chuyển chữ thường, bỏ emoji, hashtag, URL) **không cải thiện, thậm chí làm giảm** hiệu năng [11]. Ngoại lệ duy nhất là tách từ bằng VnCoreNLP cho PhoBERT, giúp tăng khoảng 2 điểm Macro-F1, vì PhoBERT được tiền huấn luyện trên văn bản đã tách từ theo cách này [9, 11].
- **Với biểu diễn dựa trên tập hợp và mẫu** (từ khóa, Trans2Vec): tiền xử lý quyết định *những item nào tồn tại*, và do đó những tập phổ biến nào được khai phá. Vai trò của nó vì vậy là cốt lõi.

**Bảng 2.1.** Vai trò của tiền xử lý theo họ biểu diễn (tổng hợp từ các công trình khảo sát)

| Bước | Âm tiết / n-gram | TF-IDF + chọn đặc trưng | Từ khóa | Embedding tĩnh | **Trans2Vec** | PhoBERT / BERT |
|---|---|---|---|---|---|---|
| Chuẩn hóa mã, dấu | Cần | Cần | Cần | Cần | **Cần** | Cần |
| Tách từ | Không cần [3, 4] | Cần | Cần; lỗi lan truyền [5] | Cần [8] | **Tùy chọn, cần thực nghiệm** | Cần cho PhoBERT [11] |
| Bỏ từ dừng | Có ích | Có ích | Rất quan trọng | Có ích | **Rất quan trọng** | Vô ích hoặc có hại [11] |
| Lọc từ vựng / top-k | — | Giúp kNN [4] | Bản chất phương pháp | — | **Bắt buộc** (Mục 5.6) | — |

Bảng 2.1 cho thấy một **đường cong chữ U**. Vai trò của tri thức ngôn ngữ tiếng Việt giảm dần từ biểu diễn thưa đến Transformer, rồi tăng trở lại với biểu diễn dựa trên mẫu. Đây là luận điểm đầu tiên trả lời RQ1. Nó cũng là lý do Chương 9 đặt tiền xử lý thành một mô-đun có thể cấu hình, kèm thực nghiệm loại trừ (ablation).

## 3. Kiến thức nền tảng

### 3.1 Bài toán phân loại và tìm kiếm văn bản

Cho tập tài liệu $D=\{d_1,\dots,d_N\}$ và tập chuyên mục $C=\{c_1,\dots,c_k\}$. **Phân loại văn bản** là học hàm $F: D\times C\to\{\text{đúng},\text{sai}\}$, với $F(d_i,c_j)=\text{đúng}$ nếu $d_i$ thuộc $c_j$ [1, 2]. Có ba trường hợp:
- **nhị phân:** $k=2$;
- **đa lớp:** $k>2$, mỗi tài liệu thuộc đúng một lớp. Đây là trường hợp phân loại chuyên mục tin tức;
- **đa nhãn:** một tài liệu có thể thuộc nhiều lớp [12].

Quy trình chuẩn gồm năm bước: tiền xử lý, biểu diễn, giảm chiều, huấn luyện bộ phân loại, đánh giá [2, 5].

**Tìm kiếm ngữ nghĩa** được hiểu ở đây là một bài toán xếp hạng. Cho một truy vấn $q$, là một chuỗi từ khóa hoặc một tài liệu, ta xếp hạng các tài liệu trong $D$ theo độ tương đồng $\text{sim}(\phi(q),\phi(d))$, với $\phi$ là hàm biểu diễn. Khi $\phi$ cho ra vector dày, $\text{sim}$ thường là cosine và bài toán trở thành tìm láng giềng gần nhất. Đây là nguyên lý của dense retrieval [22, 23]. Điểm then chốt cho đề tài: **nếu cùng một $\phi$ dùng được cho cả phân loại và tìm kiếm, hệ thống chỉ cần học và lưu một biểu diễn duy nhất.**

### 3.2 Khai phá tập phổ biến

Cho tập item $I=\{i_1,\dots,i_M\}$ và cơ sở dữ liệu transaction $D=\{T_1,\dots,T_N\}$ với $T_i\subseteq I$. **Độ hỗ trợ** (support) của itemset $X\subseteq I$ là

$$\text{sup}(X)=\frac{|\{T_i\in D : X\subseteq T_i\}|}{|D|}.$$

$X$ là **tập phổ biến** (frequent itemset, FI) nếu $\text{sup}(X)\ge\delta$, với $\delta\in[0,1]$ là ngưỡng hỗ trợ tối thiểu [13, 24]. Tính chất **đóng xuống** (anti-monotone) là nền tảng của mọi thuật toán khai phá: mọi tập con của một tập phổ biến cũng phổ biến.

Ba thuật toán chính liên quan tới đề tài:
- **Apriori** [13]: sinh ứng viên theo từng mức độ dài và tỉa nhờ tính đóng xuống. Đơn giản nhưng phải quét dữ liệu nhiều lần.
- **FP-Growth** [14]: nén cơ sở dữ liệu vào cấu trúc cây FP-tree và khai phá đệ quy, **không sinh ứng viên**. Thường nhanh hơn Apriori nhiều bậc trên dữ liệu dày. Đây là thuật toán được đề xuất cho hệ thống ở Chương 9.
- **Tập phổ biến đóng** (closed itemsets), ví dụ thuật toán CHARM [25]: chỉ giữ các FI không có tập cha nào cùng độ hỗ trợ. Đây là biểu diễn nén *không mất thông tin* của toàn bộ tập FI. Như Mục 5.6 sẽ phân tích, nó là công cụ chính để chống bùng nổ số FI khi transaction dài.

**Ví dụ.** Với δ = 0,6 trên năm transaction {a,b,c}, {b,c,d}, {a,d}, {b,c,d,e}, {a,c,d}, ta thu được sáu FI: {a}, {b}, {c}, {d}, {b,c}, {c,d}. Mỗi transaction có thể được viết lại thành tập các FI mà nó chứa [19].

**Biểu diễn bằng FI và vấn đề của nó.** Cách cổ điển là biểu diễn mỗi transaction bằng vector nhị phân $f(T)=[x_1,\dots,x_F]$, với $x_i=1$ nếu $X_i\subseteq T$. Cách này gặp hai vấn đề [19]:
1. **Số chiều rất lớn:** số FI có thể vượt $10^5$ khi δ < 5%.
2. **Rất thưa.**

Các giải pháp đi trước chọn **FI phân biệt** theo information gain hoặc độ chênh support giữa các lớp [17], hoặc xây **bộ phân lớp dựa trên luật kết hợp** [26]. Cả hai đều cần nhãn. Hệ quả là biểu diễn gắn với một tác vụ duy nhất và không chuyển sang phân cụm hay tìm kiếm được.

### 3.3 Học biểu diễn phân tán

**Word2Vec** [27] học vector cho từ bằng cách dự đoán từ ngữ cảnh. Mô hình Skip-gram dự đoán các từ xung quanh từ trung tâm; mô hình CBOW làm ngược lại. Hàm softmax trên toàn bộ từ vựng quá tốn kém, nên được xấp xỉ bằng **negative sampling**. Với cặp (đơn vị mục tiêu $u$, ngữ cảnh $c$) và $K$ mẫu âm $u_n$ rút từ phân phối nhiễu $P$, hàm mục tiêu là:

$$\mathcal{L}=-\log\sigma\big(\mathbf{v}_u\cdot\mathbf{h}_c\big)-\sum_{n=1}^{K}\mathbb{E}_{u_n\sim P}\log\sigma\big(-\mathbf{v}_{u_n}\cdot\mathbf{h}_c\big),$$

với $\sigma$ là hàm sigmoid.

**Paragraph Vector** (Doc2Vec) [20] mở rộng ý tưởng cho tài liệu: mỗi tài liệu có thêm một vector riêng $\mathbf{f}(d)$. Mô hình có hai biến thể:
- **PV-DM** (Distributed Memory): ghép vector tài liệu với vector các từ ngữ cảnh để dự đoán từ tiếp theo.
- **PV-DBOW** (Distributed Bag-of-Words): chỉ dùng $\mathbf{f}(d)$ để dự đoán các từ *có trong* tài liệu, bỏ qua thứ tự. Đây chính là công thức trên với $\mathbf{h}_c=\mathbf{f}(d)$ và $u$ là một từ thuộc $d$.

**PV-DBOW là lõi của Trans2Vec**, nên ba tính chất của nó cần được ghi nhận:
1. **Mô hình coi tài liệu như một *tập* đơn vị.** Vì vậy nó áp dụng được nguyên dạng cho dữ liệu transaction, và các đơn vị không nhất thiết phải là từ.
2. **Vector của tài liệu mới phải được *suy luận*** bằng cách giữ cố định vector đơn vị và tối ưu riêng $\mathbf{f}(d_{\text{mới}})$ vài vòng gradient. Nói cách khác, không có công thức dạng đóng (closed-form) để tính vector cho tài liệu mới.
3. **Hiệu năng nhạy với cấu hình** (số chiều, số epoch, kích thước cửa sổ, tần suất tối thiểu) và với lượng dữ liệu. Lau và Baldwin cho thấy Doc2Vec, và đặc biệt PV-DBOW, cho kết quả vững khi được cấu hình đúng và huấn luyện trên đủ dữ liệu. Họ cũng đưa ra bộ siêu tham số khuyến nghị [28]. Tính chất này giúp giải thích một mâu thuẫn quan trọng trong tài liệu tiếng Việt (Mục 8.3).

**Embedding ngữ cảnh.** BERT [29] và các biến thể như PhoBERT [9] tạo vector *phụ thuộc ngữ cảnh* bằng kiến trúc Transformer tiền huấn luyện trên corpus lớn. Để tìm kiếm, vector câu hoặc tài liệu thường được lấy bằng Sentence-BERT [23] hoặc bằng cách gộp đầu ra của các tầng cuối [10].

### 3.4 Độ đo đánh giá

- **Phân loại:** Accuracy; Precision, Recall, F1 theo trung bình macro hoặc micro. Với dữ liệu mất cân bằng, **Macro-F1** được khuyến nghị vì nó coi các lớp ngang nhau, trong khi accuracy thiên về lớp đa số [11]. Với bài toán đa nhãn có thêm Hamming loss [12].
- **Tìm kiếm:** Precision@k, Mean Average Precision (MAP), và nDCG@k [30].
- **Chủ đề / phân cụm:** độ gắn kết chủ đề $C_v$ và độ đa dạng chủ đề [12]; NMI và ARI khi so cụm với nhãn.

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

| Nhánh | [3] | [4] | [5] | [2] | [6] | [7] | [8] | [12] | [10, 11] | [19] |
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

Ô **E2 × tiếng Việt** trống hoàn toàn. Nhánh E1 có đúng một tiền lệ tiếng Việt: Đỗ Phúc dùng tập phổ biến và luật kết hợp để phân loại tóm tắt bài báo khoa học CNTT [18], không có thành phần embedding.

### 4.2 Nhánh A – Biểu diễn thưa

**A1 – Theo âm tiết.** Nguyen, Gao và Andreae biểu diễn văn bản ở mức hình thái: túi unigram âm tiết hoặc túi bigram âm tiết [4]. Trên tập 4 chủ đề, bigram vượt unigram với mọi thuật toán (98,1–98,6% so với 97,5–98,1%). Bigram còn có lợi rõ hơn trên tác vụ khó, tức phân loại theo thể loại *Tư liệu* hay *Phân tích*: kNN tăng từ 65,5 lên 73,2 điểm. Đổi lại, bigram chậm hơn 4,5–9,6 lần. Hoang và cộng sự xây **mô hình ngôn ngữ n-gram âm tiết** cho từng lớp và phân loại theo $c^*=\arg\max_c P(c)\prod_i P_c(w_i\mid w_{i-n+1}^{i-1})$, với làm trơn Good-Turing cho kết quả tốt nhất [3]. Ưu điểm then chốt của nhánh A1 là **không cần tách từ**.

**A2 – Theo từ.** Túi từ có trọng số TF-IDF, kết hợp SVM, là baseline mạnh và bền nhất trong toàn bộ tài liệu khảo sát [2, 3, 8]. Kết quả này nhất quán với các nghiên cứu kinh điển trên tiếng Anh [31]. Điểm yếu cố hữu của nó là số chiều lớn (hàng chục đến hàng trăm nghìn) và không nắm được quan hệ ngữ nghĩa giữa các từ.

### 4.3 Nhánh B – Giảm chiều và chọn đặc trưng

**B1 – Chọn đặc trưng thống kê.** Hoang và cộng sự so sánh sáu tiêu chí MI, IG, χ², GSS, OR và OCFS (Optimal Orthogonal Centroid Feature Selection) trên 2.500 term. OCFS cho kết quả tốt nhất [3]. Nguyen và cộng sự cho thấy chỉ dùng **Information Gain** đã giảm từ vựng từ 300.000 xuống khoảng 1.000 term mà độ chính xác của NB và kNN *tăng* [4]. Kết quả này phù hợp với nghiên cứu kinh điển của Yang và Pedersen [32].

**B2 – Lọc bằng từ điển.** Chỉ giữ gram ứng với từ có thật trong một từ điển khoảng 30.000 từ. Cách này giảm từ vựng 6–10 lần (unigram: 30.000 → 5.000; bigram: 300.000 → 30.000), cải thiện kNN rõ rệt và chỉ làm giảm nhẹ hiệu năng của SVM [4].

**B3 – Trích từ khóa.** Pham Van và Ta Minh chọn 10 từ khóa mỗi bài theo một điểm tần suất chuẩn hóa (KeywordScore), dựng từ điển từ khóa và biểu diễn túi từ trên đó (KEBoW). Kết hợp với mạng nơ-ron sáu lớp, họ báo cáo 99,75% [5]. Mục 8.2 sẽ thảo luận độ tin cậy của con số này. Huynh và cộng sự đi xa hơn: biểu diễn mỗi văn bản *chỉ* bằng **tập từ khóa** trích bởi TextRank [33], rồi phân loại bằng độ tương đồng **Jaccard** có trọng số với tập từ khóa đại diện của từng chủ đề [6]. Độ chính xác tăng từ 75,27% với 10 từ khóa lên khoảng 90% với 50 từ khóa, sau đó bão hòa. Dùng toàn bộ từ khóa thì đạt 95,40%. Đáng chú ý, cách nhìn "**văn bản là một tập từ khóa, đo tương đồng bằng phép toán tập hợp**" chính là góc nhìn transaction mà Trans2Vec khai thác (Chương 5).

### 4.4 Nhánh C – Biểu diễn dày học có giám sát

Vinh và Kha thay bước *chọn* đặc trưng bằng bước *học* đặc trưng [7]:
- Vector TF-IDF 10.000 chiều (unigram + bigram) đi qua một mạng hai lớp ẩn, huấn luyện với nhãn của 30 chuyên mục.
- Sau khi huấn luyện, lớp đầu ra bị bỏ đi và đầu ra **128 chiều** của lớp ẩn cuối trở thành đặc trưng cho SVM.
- Ở cùng 128 chiều, đặc trưng học được vượt χ² và OCFS.

Công trình này là mắt xích chuyển tiếp từ biểu diễn thưa sang biểu diễn dày trong tài liệu tiếng Việt. Nó cũng là **đối chứng trực tiếp nhất với Trans2Vec**: cùng 128 chiều, cùng SVM, cùng miền tin tức nhiều chuyên mục. Khác biệt căn bản nằm ở chỗ đặc trưng của Vinh và Kha **gắn với nhãn**, nên không dùng được cho tài liệu chưa gán nhãn, cho phân cụm hay cho tìm kiếm.

### 4.5 Nhánh D – Embedding không giám sát

**D1–D2.** Huong và cộng sự so sánh TF-IDF, Word2Vec, GloVe và Doc2Vec trên hai tập bình luận cảm xúc. TF-IDF thắng tuyệt đối; Word2Vec và Doc2Vec chỉ đạt khoảng 50% [8]. Nguyen và cộng sự cũng ghi nhận Word2Vec kém túi từ một chút trên review Shopee (Macro-F1 tốt nhất 0,88 so với 0,91) [12]. Hai kết quả này mâu thuẫn với kết quả của PV-DBOW trên dữ liệu Snippets [19]. Mục 8.3 sẽ phân tích mâu thuẫn này.

**D3 – Mô hình chủ đề.** Các mô hình chủ đề dùng được cho cả gán nhãn chủ đề lẫn tìm kiếm:
- **LDA** [34]: mô hình xác suất.
- **Top2Vec** [35]: embedding chung cho tài liệu và từ, tự xác định số chủ đề, có sẵn chức năng tìm kiếm ngữ nghĩa.
- **BERTopic** [36]: embedding Transformer kết hợp c-TF-IDF.

Trên review Shopee tiếng Việt, LDA và BERTopic đạt độ gắn kết khoảng 0,48 và độ đa dạng trên 0,8, còn **Top2Vec kém hơn**. Không mô hình nào đủ tốt để dùng trực tiếp làm nhãn, nên các tác giả phải gán nhãn thủ công [12]. Trên dữ liệu tiếng Anh, Phan và cộng sự cho thấy chủ đề ẩn học từ một corpus ngoài lớn (Wikipedia) nâng độ chính xác phân loại văn bản ngắn từ 65,75% lên 82,18% [37]. Đây là bằng chứng rõ cho giá trị của **tri thức ngoài**.

### 4.6 Nhánh F – Mô hình ngôn ngữ tiền huấn luyện

PhoBERT là mô hình RoBERTa đơn ngữ tiếng Việt. Dữ liệu tiền huấn luyện khoảng 20 GB, trong đó khoảng 19 GB là **tin tức** [9]. Điều này khiến PhoBERT đặc biệt hợp với miền tin tức. Các công trình được khảo sát cho thấy:
- Fine-tune có chiến lược (huấn luyện thêm MLM trên dữ liệu miền, đóng băng rồi mở dần các tầng, learning rate theo khối, label smoothing) đạt Macro-F1 0,7221 trên VLSP 2019 HSD. Đặc trưng từ 4–6 khối cuối tốt nhất [10].
- Các phương pháp tăng cường dữ liệu và hàm mất mát cho dữ liệu mất cân bằng chỉ cải thiện 1–2 điểm [11].
- Trên review Shopee, PhoBERT kết hợp hồi quy logistic đạt Macro-F1 0,96, vượt mọi biểu diễn khác ít nhất 5 điểm. Đổi lại, nó cần GPU và khoảng 41 phút huấn luyện, so với khoảng 22 giây của TF-IDF trên CPU [12].

### 4.7 Nhận xét chung

Ba xu hướng rút ra từ chương này:
1. **Từ chọn sang học:** đặc trưng ngày càng được *học* thay vì *chọn* (B → C → D → F).
2. **Từ thưa sang dày:** chiều biểu diễn giảm từ $10^4$–$10^5$ xuống $10^2$–$10^3$.
3. **Từ dữ liệu nội tại sang tri thức ngoài:** từ chỉ học trên corpus đích sang tận dụng corpus ngoài (LDA trên Wikipedia, tiền huấn luyện PhoBERT).

Nhánh E nằm ở một vị trí đặc biệt. Nó *học* biểu diễn dày như C, D, F, nhưng đơn vị học là **mẫu do khai phá dữ liệu phát hiện**, nên giữ được tính diễn giải của nhánh B. Đồng thời nó **không giám sát** như D. Chương 5 phân tích nhánh này.

## 5. Trans2Vec và mô thức biểu diễn dựa trên mẫu phổ biến

### 5.1 Ý tưởng

Trans2Vec [19] giải bài toán nêu ở Mục 3.2. Đầu vào là dữ liệu transaction; mục tiêu là học hàm $f: D\to\mathbb{R}^d$ **không giám sát**, sao cho hai transaction giống nhau có vector gần nhau. Ý tưởng cốt lõi là **dùng FI như "từ" trong mô hình PV-DBOW**. FI mang thông tin đồng xuất hiện bậc cao mà item đơn lẻ không có. PV-DBOW nén thông tin đó vào một vector dày $d$ chiều, nhờ vậy loại bỏ cả vấn đề số chiều cao lẫn vấn đề vector thưa của biểu diễn FI nhị phân.

**Ánh xạ sang văn bản tin tức** (đề xuất của bài khảo sát):

| Khái niệm Trans2Vec | Văn bản tin tức tiếng Việt |
|---|---|
| Item $i$ | Từ (sau tách từ), hoặc âm tiết |
| Transaction $T$ | Tập các từ phân biệt của một bài báo |
| Frequent itemset $X$ | Cụm từ thường xuất hiện cùng nhau trong các bài, ví dụ {chứng_khoán, cổ_phiếu}, {đội_tuyển, HLV, vòng_loại} |
| Vector transaction $f(T)$ | Vector bài báo, dùng cho phân loại **và** tìm kiếm |

### 5.2 Bốn biến thể

**(1) TRANS-IT: học từ item.** Áp dụng PV-DBOW, coi item là từ. Hàm mục tiêu với negative sampling:

$$O_1=-\log\sigma\big(g(i_j)\cdot f(T_t)\big)-\sum_{n=1}^{K}\mathbb{E}_{i_n\sim P(i)}\log\sigma\big(-g(i_n)\cdot f(T_t)\big),$$

với $g(\cdot)$ là vector item, $f(T_t)$ là vector transaction, và $i_n$ là các item âm không thuộc $T_t$. Biến thể này về bản chất **chính là Doc2Vec PV-DBOW**.

**(2) TRANS-FI: học từ tập phổ biến.** Thay item bằng các FI chứa trong $T_t$, với vector $h(X_j)$. Hàm mục tiêu $O_2$ có cùng dạng. Biến thể này có một điểm yếu: transaction không chứa FI nào sẽ nhận vector 0.

**(3) Trans2Vec-IND (individual).** Học riêng $f_1(T)$ từ item và $f_2(T)$ từ FI, rồi lấy trung bình $f(T)=\tfrac{1}{2}(f_1(T)+f_2(T))$. Cách này đơn giản nhưng không mô hình hóa quan hệ giữa item và FI.

**(4) Trans2Vec-JOI (joint).** Gộp item và FI thành một tập **mẫu** (pattern) $p_j\in I(T_t)\cup F(T_t)$ và học một vector duy nhất:

$$O=-\sum_{p_j\in I(T_t)\cup F(T_t)}\log\Pr(p_j\mid T_t),$$

cũng được xấp xỉ bằng negative sampling. Sau khi huấn luyện, hai transaction có vector gần nhau khi chúng chia sẻ nhiều item **và** nhiều FI.

**Chọn tham số.** Số chiều $d=128$. Ngưỡng δ được chọn bằng **phương pháp elbow** trên đường cong "số FI theo δ" của tập huấn luyện, tức chọn điểm mà khi giảm δ thêm thì số FI bắt đầu tăng vọt. Cách chọn này không dùng nhãn [19, 38].

### 5.3 Kết quả gốc

Trans2Vec được đánh giá trên bốn tập dữ liệu:
- **Snippets:** đoạn trích kết quả tìm kiếm web, 8 lĩnh vực, 12.340 mẫu, tiếng Anh [37];
- **Cancer** (bệnh án), **Retail** (bán lẻ), **Food** (giỏ thực phẩm).

Vector được đưa vào SVM tuyến tính với C = 1 cố định, chạy lặp 10 lần trên cùng tập huấn luyện và tập kiểm tra (Bảng 5.1).

**Bảng 5.1.** Accuracy / Macro-F1 (%) của Trans2Vec và các baseline, trích từ [19]

| Phương pháp | Snippets | Cancer | Retail | Food |
|---|---|---|---|---|
| BOW | 66,32 / 65,83 | 48,57 / 48,57 | 77,33 / 77,31 | 63,12 / 63,12 |
| TF-IDF | 70,26 / 69,52 | 49,43 / 49,43 | 81,67 / 81,56 | 64,50 / 64,49 |
| FI-BIN | 64,52 / 63,96 | 48,52 / 48,44 | 77,67 / 77,62 | 61,75 / 61,74 |
| FI-SUP | 37,94 / 32,19 | 47,30 / 46,54 | 80,33 / 79,20 | 71,00 / 70,03 |
| TRANS-IT | 75,23 / 74,79 | 49,35 / 49,32 | 81,17 / 81,07 | 65,95 / 65,81 |
| TRANS-FI | 77,88 / 77,41 | 50,03 / 49,92 | 82,07 / 81,90 | 69,14 / 68,95 |
| Trans2Vec-IND | 78,80 / 77,92 | 50,10 / 50,02 | 82,23 / 82,12 | 69,22 / 69,12 |
| **Trans2Vec-JOI** | **79,05 / 78,31** | **50,34 / 50,28** | **83,43 / 83,36** | **72,51 / 72,47** |

*Ghi chú:* khi tái hiện bằng dữ liệu và mã nguồn chính thức, TRANS-IT khớp (75,29%) nhưng JOI chỉ đạt 75,99%; xem Mục 9.5.

Bốn quan sát quan trọng cho bài khảo sát:
- **(a) Embedding học từ item thắng TF-IDF:** +5,0 điểm trên Snippets, một tập *văn bản ngắn*.
- **(b) FI có đóng góp riêng:** TRANS-FI hơn TRANS-IT 2,7 điểm trên Snippets, và TRANS-FI luôn hơn TRANS-IT trên cả bốn tập. Đây là **bằng chứng định lượng duy nhất** trong tài liệu khảo sát cho RQ3.
- **(c) Học chung item và FI tốt hơn học riêng:** JOI > IND trên cả bốn tập.
- **(d) δ chọn bằng elbow luôn cho độ chính xác tốt nhất trong các giá trị thử.** Riêng số chiều $d$: độ chính xác tăng rồi giảm trên Snippets và Food, khác với xu hướng "càng nhiều chiều càng tốt" thường thấy ở embedding tài liệu.

### 5.4 Họ phương pháp "mẫu + embedding"

Trans2Vec không đứng riêng lẻ. Tác giả chính Dang Nguyen và các cộng sự (chủ yếu tại Đại học Deakin) đã áp dụng một **mô thức chung**, gồm khai phá mẫu phổ biến, coi mẫu như từ, rồi học embedding kiểu PV-DBOW, cho nhiều kiểu dữ liệu khác nhau (Bảng 5.2).

**Bảng 5.2.** Mô thức biểu diễn dựa trên mẫu phổ biến

| Phương pháp | Kiểu dữ liệu | Loại mẫu | Ý nghĩa với văn bản |
|---|---|---|---|
| Trans2Vec [19] | Tập hợp (transaction) | Frequent itemset | Bài báo = tập từ |
| Sqn2Vec [39] | Chuỗi | Mẫu tuần tự có ràng buộc khoảng cách (gap) | Bài báo = **chuỗi** từ, **giữ được thứ tự** |
| Graph embedding qua đồ thị con phổ biến [40] | Đồ thị | Đồ thị con phổ biến | Kết hợp được với graph-of-words [38] |
| Con2Vec [41] | Transaction có biến mục tiêu | Contrast set | Phiên bản có định hướng nhãn |

Cũng theo hướng dùng mẫu cho văn bản, Rousseau và cộng sự biểu diễn văn bản bằng đồ thị từ (graph-of-words) và khai phá **đồ thị con phổ biến** làm đặc trưng, tức "n-gram khoảng cách xa" [38]. Wang và cộng sự giới hạn việc khai phá trên **thực thể có tên** để xử lý văn bản dài nhiều nhiễu [42]. Các công trình sớm hơn dùng tập từ phổ biến để **phân cụm văn bản** [15] và xây **cây chủ đề phân cấp** có nhãn diễn giải được [16].

Như vậy, dùng tập phổ biến cho văn bản không phải ý tưởng mới. Điểm mới của nhánh E2 là **dùng mẫu làm đơn vị học embedding**. Nhờ đó biểu diễn vừa dày, vừa không giám sát, vừa chuyển giao được giữa các tác vụ phân loại, phân cụm và tìm kiếm.

### 5.5 Vì sao phù hợp với tin tức tiếng Việt

1. **Cụm đồng xuất hiện mang tính chuyên mục.** Chuyên mục tin tức thường được nhận diện qua tổ hợp từ hơn là từ đơn lẻ. Ví dụ "lãi suất" xuất hiện ở cả Kinh doanh lẫn Bất động sản, nhưng {lãi_suất, căn_hộ, dự_án} thì chỉ thuộc Bất động sản. FI nắm được những tổ hợp này một cách tường minh. Snippets, tập mà Trans2Vec thắng rõ nhất, cũng là bài toán phân loại lĩnh vực của văn bản.
2. **Giảm phụ thuộc vào tách từ.** Hơn 80% từ tiếng Việt có hai âm tiết [4], nên nếu chọn item là âm tiết, FI hai phần tử có thể đóng vai từ ghép. Khác với n-gram [3], FI không đòi hỏi các phần tử đứng liền nhau. Đây là một **giả thuyết cần kiểm chứng**, chưa phải kết luận.
3. **Không giám sát.** Biểu diễn học được trên toàn bộ kho bài, kể cả bài chưa có chuyên mục, và dùng được ngay cho tìm kiếm cũng như phân cụm. Điều này khác với đặc trưng gắn nhãn của [7].
4. **Diễn giải được và chi phí thấp.** FI là các cụm từ đọc được, nên có thể dùng để giải thích vì sao một bài được xếp vào một chuyên mục. Về nguyên tắc, toàn bộ quy trình (FP-Growth và PV-DBOW) chạy được trên CPU, khác với yêu cầu GPU của PhoBERT [12]. Chi phí thực tế vẫn cần được đo (H7, Mục 5.6).

### 5.6 Phân tích phản biện: bảy hạn chế khi áp dụng cho tin tức

**Bảng 5.3.** Hạn chế của Trans2Vec, hệ quả với tin tức tiếng Việt và hướng giải quyết có cơ sở tài liệu

| # | Hạn chế | Hệ quả với tin tức tiếng Việt | Hướng giải quyết |
|---|---|---|---|
| **H1** | Transaction là *tập*, nên mất tần suất và thứ tự từ | Tin tức dài; tần suất từ mang thông tin chuyên mục | Sqn2Vec [39]; nối thêm TF-IDF; khai phá FI trên cửa sổ câu |
| **H2** | Transaction trong thực nghiệm gốc rất ngắn (trung bình 6–27 item) | Bài báo có hàng trăm từ, nên số FI **bùng nổ tổ hợp** khi δ nhỏ | Giữ top-k từ mỗi bài theo TF-IDF hoặc TextRank (k ≈ 50 [6]); dùng tập phổ biến đóng [24, 25]; item là thực thể có tên [21, 42]; giới hạn độ dài itemset ≤ 3 |
| **H3** | Baseline yếu: không có LDA, PV-DM hay BERT; SVM không tinh chỉnh; không báo độ lệch chuẩn | Không biết Trans2Vec đứng ở đâu so với các phương pháp hiện đại | So sánh thêm với [7], LDA [34], Top2Vec [35], PhoBERT [9] |
| **H4** | Hiệu quả phụ thuộc dữ liệu (Cancer: mọi phương pháp ≈ 50%) | Cần đánh giá trên cả corpus dễ và corpus khó | VNTC-10 và VNTC-27 / corpus ≥ 25 chuyên mục [2, 3] |
| **H5** | Không mô tả cách suy luận vector cho transaction mới | Chức năng tìm kiếm cần vector cho **truy vấn**. Truy vấn ngắn có thể không chứa FI nào | Suy luận PV-DBOW [20, 28]; dự phòng chỉ dùng phần item; mở rộng truy vấn |
| **H6** | Chỉ đánh giá phân loại | Phần tìm kiếm và phân cụm chưa được kiểm chứng | Đo Precision@k, nDCG [30], NMI/ARI; dùng FI làm nhãn chủ đề diễn giải được [16] |
| **H7** | Không báo chi phí tính toán | Không đánh giá được tính khả thi khi triển khai | Đo thời gian khai phá FI theo δ và thời gian huấn luyện, theo mẫu của [2, 12] |

Hạn chế H3 cần được nhấn mạnh. Trên **chính tập Snippets**, Phan và cộng sự đạt **82,18%** khi bổ sung chủ đề ẩn học từ Wikipedia [37], cao hơn mức 79,05% của Trans2Vec-JOI. Bài Trans2Vec không so sánh với kết quả này. Hai con số không cùng điều kiện, vì một bên dùng dữ liệu ngoài và bộ phân loại MaxEnt. Dù vậy, so sánh này cho thấy **tri thức ngoài vẫn vượt embedding chỉ học từ dữ liệu nội tại**. Đó là lý do Chương 9 đề xuất thử nghiệm khởi tạo Trans2Vec bằng vector từ tiền huấn luyện, theo khuyến nghị của [28].

### 5.7 Trả lời RQ3

Tài liệu hiện có cho phép trả lời RQ3 ở mức **thận trọng**:
- **FI có làm giàu embedding.** Trên Snippets, FI giúp tăng 2,7 điểm so với embedding chỉ từ item, và JOI tăng thêm 1,2 điểm [19].
- **Bằng chứng còn mỏng.** Nó đến từ *một* công trình, trên dữ liệu *tiếng Anh*, với transaction *ngắn*.
- **Muốn áp dụng cho tin tức tiếng Việt, cần ít nhất:**
  1. một chiến lược chặn bùng nổ FI (H2);
  2. một cơ chế suy luận vector cho truy vấn (H5);
  3. một giao thức đánh giá có đối chứng hiện đại (H3, H6).

Kiểm chứng ba điều kiện này trên tiếng Việt chính là đóng góp mà đề tài hướng tới. Mục 9.5 trình bày kết quả thực nghiệm sơ bộ theo hướng này.

## 6. Bộ phân loại và đánh đổi hiệu năng – chi phí

### 6.1 Các bộ phân loại trong tài liệu

Duong và Hoang tổng quan lý thuyết các bộ phân loại thường dùng [2]:
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
| **SVM** | TF-IDF [2, 3, 8]; âm tiết [4]; MLP-128 [7]; Trans2Vec [19] | Gần như luôn tốt nhất hoặc nhì với biểu diễn thưa. Thường được dùng làm **bộ phân loại chuẩn để so biểu diễn**: [19] cố định C = 1 |
| **LR** | TF-IDF [2, 8]; PhoBERT [12] | Gần bằng SVM (F1 0,734 so với 0,749 [2]) nhưng **suy luận nhanh hơn hàng nghìn lần**; tốt nhất khi dùng trên vector PhoBERT [12] |
| NB | TF-IDF [2]; n-gram [3]; âm tiết [4] | Rất nhanh; mạnh khi đã chọn đặc trưng tốt [4] |
| kNN | [2, 3, 4, 8] | Kém nhất (F1 0,500–0,626 [2]); **rất nhạy với đặc trưng nhiễu** [4] |
| RF / XGBoost | [2, 5, 8, 12] | Trung bình; RF huấn luyện chậm |
| MLP / fine-tune | [5, 7, 10, 11, 12] | Mạnh nhất khi có đủ nhãn; PhoBERT cần GPU |

Từ Bảng 6.1 có hai hệ quả cho hệ thống đề xuất:
1. **SVM tuyến tính** phù hợp làm bộ phân loại đánh giá, để so các biểu diễn một cách công bằng theo đúng thiết kế của [19]. **LR** phù hợp làm bộ phân loại triển khai.
2. **kNN kém và nhạy nhiễu.** Tìm kiếm top-k theo cosine thực chất là một bài toán láng giềng gần nhất, nên **chất lượng tìm kiếm phụ thuộc trực tiếp vào độ "sạch" của biểu diễn**. Đây là lập luận ủng hộ biểu diễn dày, đã lọc nhiễu, thay cho vector TF-IDF thưa.

### 6.2 Chi phí tính toán

**Bảng 6.2.** Chi phí được báo cáo trong tài liệu

| Công trình | Thiết lập | Số liệu |
|---|---|---|
| [2] | 37.500 bài, 25 chuyên mục, CPU Xeon 3,2 GHz | NB: 0,3 s huấn luyện; LR: 77 s; SVM-RBF: 839 s huấn luyện / 291 s kiểm tra; OVO: 4.785 s kiểm tra |
| [4] | Unigram so với bigram âm tiết | Bigram chậm hơn 4,5–9,6 lần |
| [6] | 4.500 bài | 2.155–9.279 s huấn luyện, tăng theo số từ khóa |
| [12] | 12.240 review | TF-IDF: 22 s trên CPU; PhoBERT: khoảng 4 phút mỗi epoch trên GPU T4 (khoảng 41 phút cho 10 epoch) |
| [19] | — | **Không báo cáo** |

Thiếu số liệu chi phí cho Trans2Vec (H7) là một khoảng trống thực tế. Chi phí của Trans2Vec gồm hai phần:
- **Khai phá FI:** phụ thuộc mạnh vào δ và độ dài transaction (H2).
- **Huấn luyện PV-DBOW:** tuyến tính theo tổng số mẫu.

Cả hai cần được đo trong thực nghiệm. Về định tính, Trans2Vec nằm giữa TF-IDF và PhoBERT trên trục chi phí, và không cần GPU.

### 6.3 Trả lời RQ4

- SVM là chuẩn so sánh; LR là lựa chọn triển khai.
- Biểu diễn dày giúp các bộ phân loại đơn giản và nhanh (LR, tìm kiếm cosine) đạt hiệu năng cao. Biểu diễn thưa cần bộ phân loại mạnh hơn (SVM với hàm nhân) và đắt hơn.
- Mức chi phí của PhoBERT chỉ hợp lý khi xử lý theo lô hoặc khi có GPU [12].

## 7. Dữ liệu và giao thức đánh giá

### 7.1 Các tập dữ liệu

**Bảng 7.1.** Tập dữ liệu trong các công trình khảo sát

| Tập dữ liệu | Công trình | Miền / nguồn | #Tài liệu | #Lớp | Chia dữ liệu | Công khai |
|---|---|---|---|---|---|---|
| **VNTC Level 1** | [3, 5] | Tin tức, 4 báo | 84.132 | 10 | 33.759 / 50.373 | ✅ |
| **VNTC Level 2** | [3, 5] | Tin tức, chủ đề con | 26.451 | 27 | 14.375 / 12.076 | ✅ |
| VNNews-01 | [2] | Tin tức, >30 trang | 37.500 | 25 | 5-fold CV | Theo yêu cầu |
| Corpus của [7] | [7] | Tin tức, 5 trang | 68.363 | 30 | 48.363 / 10.000 / 10.000 | ❌ |
| D1 / D2 | [4] | Tin tức / thể loại | ~16.000 / 1.743 | 4 / 2 | 10% huấn luyện | ❌ |
| Corpus của [6] | [6] | Tin tức, 4 trang | 4.500 | 15 | 200 / 100 mỗi lớp | ❌ |
| Snippets | [19, 37] | Đoạn trích tìm kiếm web (tiếng Anh) | 12.340 | 8 | 10.060 / 2.280 | ✅ |
| Shopee reviews | [12] | Review thương mại điện tử, đa nhãn | 17.049 | 5 (+Khác) | 70 / 10 / 20 | ❌ |

Ba nhận xét:
1. **Dữ liệu phân mảnh.** Có ít nhất sáu corpus tin tức tiếng Việt khác nhau, nhưng chỉ **VNTC** [3] vừa công khai vừa đã có kết quả công bố để đối chiếu. VNTC được xây từ VnExpress, Tuổi Trẻ, Thanh Niên và Người Lao Động, sau đó được năm học viên cao học ngành ngôn ngữ học hiệu chỉnh thủ công.
2. **Độ khó chênh lệch lớn.** Corpus 4 chuyên mục cho độ chính xác khoảng 98% với *mọi* thuật toán [4], nên không còn đủ sức phân biệt các phương pháp. Ngược lại, VNNews-01 với 25 chuyên mục chồng lấn chỉ cho F1 0,749 với bộ phân loại tốt nhất [2].
3. **Sai lệch nhỏ trong mô tả dữ liệu.** Một công trình ghi 17.002 review ở phần tóm tắt nhưng 17.049 ở phần dữ liệu [12]. Những chi tiết như vậy làm giảm khả năng tái lập.

### 7.2 Vấn đề giao thức đánh giá

**Bảng 7.2.** Giao thức đánh giá không thống nhất

| Khía cạnh | Biến thể trong tài liệu |
|---|---|
| Chia dữ liệu | Chia cố định [3]; 10% huấn luyện, lặp 10 lần [4]; 5-fold [2]; 10-fold [10]; 70/30 [8]; không rõ [5] |
| Độ đo | Accuracy trung bình theo lớp [3, 5]; F-measure [2]; Macro-F1 [10, 11, 19]; Hamming loss [12] |
| Độ lệch chuẩn | Hầu như không báo; [19] nói "< 10⁻²" nhưng không đưa bảng |
| Mức fit tiền xử lý | Có trường hợp từ điển từ khóa được dựng trên toàn bộ corpus [5] |
| Mô tả siêu tham số | Thiếu với embedding [8] |

### 7.3 Đề xuất giao thức chuẩn

Để trả lời RQ5 theo hướng xây dựng, bài khảo sát đề xuất một giao thức tối thiểu cho các nghiên cứu phân loại và tìm kiếm tin tức tiếng Việt:
1. **Dữ liệu:** dùng VNTC (Level 1 và Level 2) với cách chia công bố, để đối chiếu được với [3]. Bổ sung một corpus khó (≥ 25 chuyên mục) để tránh hiệu ứng trần.
2. **Không rò rỉ:** từ vựng, danh sách từ khóa, tập phổ biến, embedding và mọi tham số tiền xử lý **chỉ được fit trên tập huấn luyện**.
3. **Độ đo:** Macro-F1 là chính, accuracy là phụ. Báo **trung bình ± độ lệch chuẩn** qua ít nhất 5 lần chạy với hạt giống ngẫu nhiên khác nhau.
4. **Tìm kiếm:** Precision@k, MAP, nDCG@k [30]. Coi các bài cùng chuyên mục là "liên quan" (nhãn thay thế), và nêu rõ hạn chế của cách làm này. Có thể tham khảo cách tổ chức tác vụ truy xuất và phân cụm của VN-MTEB [43].
5. **Tái lập:** báo đầy đủ siêu tham số, phiên bản công cụ (bộ tách từ, thư viện), cấu hình phần cứng và thời gian chạy.
6. **Nhất quán giữa vector huấn luyện và kiểm tra** (bổ sung từ thực nghiệm ở Mục 9.5): với các mô hình phải suy luận vector cho tài liệu mới (Doc2Vec, Trans2Vec), vector của tập huấn luyện cũng phải được sinh bằng cùng quy trình suy luận. Nếu lấy trực tiếp vector học được trong mô hình, kết quả có thể lệch 7–8 điểm Macro-F1, và có thể xuất hiện những "cải thiện" giả.

## 8. So sánh tổng hợp và thảo luận

### 8.1 Kết quả theo nhóm có thể so sánh

Các kết quả được xếp vào những nhóm có cùng dữ liệu và giao thức tương đương. **Chỉ so sánh con số trong cùng một nhóm**; giữa các nhóm chỉ so sánh xu hướng.

**Bảng 8.1.** Kết quả theo nhóm

| Nhóm | Công trình | Biểu diễn → bộ phân loại | Kết quả | Độ tin cậy |
|---|---|---|---|---|
| **G1** VNTC 10 chuyên mục | [3] | BoW + OCFS → SVM | 96,21% | Khá |
| | [3] | N-gram âm tiết | 95,58% | Khá |
| | [5] | KEBoW → MLP | 99,75% | ⚠️ Thấp (Mục 8.2) |
| **G2** Tin tức nhiều chuyên mục | [2] | TF-IDF → SVM-RBF (25 lớp) | F1 0,749 | Cao |
| | [7] | TF-IDF → MLP-128 → SVM (30 lớp) | Accuracy ≈ 0,905 (tập validation) | Trung bình |
| **G3** Tin tức ít chuyên mục | [4] | Bigram âm tiết → SVM (4 lớp) | 98,6% | Trung bình |
| | [6] | Từ khóa TextRank → Jaccard (15 lớp) | 95,40% | Thấp (không baseline) |
| **G4** Snippets (tiếng Anh) | [19] | TF-IDF → SVM | 70,26% | Cao |
| | [19] | Trans2Vec-JOI → SVM | 79,05% | Cao |
| | [37] | BoW + chủ đề ẩn LDA (Wikipedia) → MaxEnt | 82,18% | Cao (có dữ liệu ngoài) |
| **G5** Ngoài miền tin tức | [12] | PhoBERT → LR | Macro-F1 0,96 | Trung bình |
| | [10] | PhoBERT fine-tune | Macro-F1 0,7221 | Trung bình |

**Bảng 8.2.** Mức cải thiện khi đổi biểu diễn trong cùng nhóm

| Từ → sang | Nguồn | Δ |
|---|---|---|
| Unigram âm tiết → bigram âm tiết | [4] | +0,3–0,9 (dễ); +0,4–7,7 (khó) |
| TF-IDF → embedding item (PV-DBOW) | [19] | +5,0 |
| Embedding item → embedding FI | [19] | **+2,7** |
| TF-IDF → Trans2Vec-JOI | [19] | +8,8 |
| BoW → BoW + chủ đề ẩn từ corpus ngoài | [37] | +16,4 |
| TF-IDF → PhoBERT | [12] | +7 Macro-F1 (so với BoW: +5) |

Bảng 8.2 cho thấy:
- **(i) Biểu diễn dày thắng TF-IDF khi được huấn luyện đúng cách**, và lợi thế càng rõ trên tác vụ khó.
- **(ii) FI mang thông tin riêng**, bổ sung cho embedding item.
- **(iii) Tri thức ngoài cho mức tăng lớn nhất.** Đây là trần trên mà mọi biểu diễn chỉ học từ dữ liệu nội tại, kể cả Trans2Vec, cần được đặt cạnh.

### 8.2 Độ khó corpus, rò rỉ dữ liệu và tính so sánh được

Trên cùng loại dữ liệu "tin tức tiếng Việt", kết quả báo cáo trải từ F1 0,749 [2] tới 99,75% [5]. Khác biệt này chủ yếu đến từ ba nguồn:
1. **Số chuyên mục và mức chồng lấn:** 4–10 lớp tách bạch so với 25–30 lớp chồng lấn.
2. **Giao thức** (Bảng 7.2).
3. **Khả năng rò rỉ dữ liệu.** Con số 99,75% của [5] cần được đọc thận trọng:
   - Từ điển từ khóa được dựng trên "toàn bộ tài liệu của corpus", nên có thể gồm cả tập kiểm tra.
   - Điểm từ khóa là một hàm thuần tần suất, không có thành phần IDF.
   - Bài không báo phương sai, và so sánh với [3] qua hình chụp lại thay vì chạy lại baseline.

   Trên cùng VNTC, một kết quả hơn kết quả gốc gần 4 điểm (sai số giảm khoảng 15 lần) khi chỉ đổi cách chọn đặc trưng và bộ phân loại là điều khó xảy ra nếu không có rò rỉ.

### 8.3 Năm mâu thuẫn trong tài liệu

**Bảng 8.3.** Mâu thuẫn và cách giải thích

| # | Mâu thuẫn | Bên A | Bên B | Giải thích đề xuất |
|---|---|---|---|---|
| **M1** | Embedding tĩnh hay TF-IDF? | TF-IDF thắng: Word2Vec/Doc2Vec ≈ 50% [8]; Word2Vec < BoW (Macro-F1 0,88 so với 0,91) [12] | PV-DBOW hơn TF-IDF 5 điểm [19] | Xem phân tích bên dưới |
| **M2** | Có cần tách từ? | Không: n-gram âm tiết ≈ BoW theo từ [3]; bigram [4, 7] | Có: lỗi tách từ gây phân loại sai [5]; PhoBERT +2 F1 [11] | Phụ thuộc họ biểu diễn (Bảng 2.1); với Trans2Vec là câu hỏi mở |
| **M3** | Top2Vec tốt hay kém? | Kém về độ gắn kết trên review ngắn [12] | Tốt hơn LDA theo tác giả [35] | Phụ thuộc độ dài văn bản và kích thước corpus |
| **M4** | Kết quả ~99% hay ~0,75? | [4, 5] | [2] | Độ khó corpus, giao thức, rò rỉ (Mục 8.2) |
| **M5** | Trans2Vec có phải tốt nhất trên Snippets? | Tốt nhất trong các baseline của bài [19] | 82,18% > 79,05% [37] | [19] chỉ so với baseline không giám sát và không dùng dữ liệu ngoài |

**Phân tích M1.** Mâu thuẫn này đáng phân tích kỹ vì nó ảnh hưởng trực tiếp đến tính khả thi của Trans2Vec (vốn xây trên PV-DBOW).
- **Kết quả của [8] khó chấp nhận về mặt lý thuyết.** Word2Vec và Doc2Vec chỉ đạt khoảng 50% trên tập nhị phân *cân bằng*, với **cả năm** bộ phân loại, kể cả 1-NN. Một biểu diễn mang dù chỉ một chút thông tin thì 1-NN cũng phải vượt mức đoán ngẫu nhiên. Kết quả đúng bằng 50% vì vậy gợi ý lỗi cài đặt hơn là giới hạn của phương pháp: vector suy biến sau khi gộp, lệch thứ tự giữa vector và nhãn, hoặc vector chưa được huấn luyện. Bài cũng không công bố siêu tham số nên không thể tái lập.
- **Bằng chứng đối lập:** PV-DBOW thắng TF-IDF trên văn bản ngắn [19]; Word2Vec (CBOW) vẫn đạt Macro-F1 tới 0,88 trên review Shopee, gần bằng TF-IDF (0,89) [12]; Doc2Vec vững khi được cấu hình đúng [28].
- **Kết luận cho đề tài:** không nên coi [8] là bằng chứng rằng Doc2Vec không dùng được cho tiếng Việt. Ngược lại, cần kiểm tra cẩn thận để tránh những lỗi tương tự: chuẩn và phương sai của vector, thử kNN nhanh, báo đủ siêu tham số.

### 8.4 Các mối đe dọa đến tính hợp lệ của khảo sát

- **Tuyển chọn tài liệu.** Vòng 1 do người thực hiện chọn. Vòng 2 bổ sung có hệ thống nhưng không phải tổng quan hệ thống đầy đủ theo PRISMA.
- **Tính độc lập.** Một số công trình chung nhóm tác giả: [5] và [10] chung tác giả Ta Minh Thanh; [2] và [8] chung nhóm Đại học Mở TP.HCM. Toàn bộ họ phương pháp ở Bảng 5.2 có chung tác giả chính (Dang Nguyen, Wei Luo).
- **Trích số liệu.** Một số số liệu chỉ có trong hình (bản quét của [3]; so sánh trong [7]), nên chỉ được trích ở mức đã nêu trong văn bản của bài.
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

## 9. Đề xuất hệ thống tìm kiếm và phân loại chuyên mục dựa trên Trans2Vec

Chương này chuyển các kết luận của khảo sát thành một kiến trúc cụ thể và một thiết kế thực nghiệm kiểm chứng được. Mỗi quyết định thiết kế được gắn với hạn chế (H1–H7, Bảng 5.3) hoặc bằng chứng mà nó dựa vào.

### 9.1 Kiến trúc tổng thể

```
                        ┌─────────────── PHA HUẤN LUYỆN (offline, trên tập train) ───────────────┐
[Thu thập tin tức] → [M1 Tiền xử lý] → [M2 Lọc item] → [M3 Khai phá FI] → [M4 Học Trans2Vec-JOI]
                        │                                                       │
                        │                                    vector bài báo f(T) ∈ R^128
                        │                                    + vector item g(·), vector FI h(·)
                        └───────────────────────────────────────────────────────┬───────────────┘
                                                                                ▼
                              ┌──────────────── PHA PHỤC VỤ (online) ─────────────────┐
     Bài mới / truy vấn  →  [M1] → [M2] → [khớp item + FI] → [M5 Suy luận vector]
                                                                    │
                              ┌─────────────────────────────────────┴──────────────┐
                              ▼                                                    ▼
                   [M6 Phân loại chuyên mục]                          [M7 Tìm kiếm ngữ nghĩa]
                   LR / SVM trên f(T)                                 cosine top-k trên chỉ mục vector
                   + giải thích bằng FI đặc trưng                     (tùy chọn: lọc theo chuyên mục)
```
*Hình 9.1. Kiến trúc hệ thống đề xuất.*

### 9.2 Các mô-đun

**M1 – Tiền xử lý** (Mục 2.4, Bảng 2.1).
- Chuẩn hóa Unicode và vị trí dấu thanh; loại thẻ HTML và ký tự ngoài bảng chữ cái [4].
- Tách từ bằng VnCoreNLP [21]. Đây là cấu hình có thể đổi: phương án đối chứng giữ nguyên âm tiết, để kiểm chứng giả thuyết "FI ≈ từ ghép" (Mục 5.5).
- Bỏ từ dừng bằng một danh sách công bố kèm theo nghiên cứu, để tăng khả năng tái lập.

**M2 – Lọc item** (giải H2). Mỗi bài báo chỉ giữ **k item đại diện**. Ba phương án sẽ được so sánh:
- (a) top-k theo TF-IDF, với IDF tính trên tập huấn luyện;
- (b) top-k theo TextRank [6, 33];
- (c) chỉ giữ thực thể có tên và danh từ riêng [42].

Giá trị khởi điểm k = 50 dựa trên điểm bão hòa quan sát được trong [6].

**M3 – Khai phá FI.**
- Dùng **FP-Growth** [14] cho tập phổ biến thường, hoặc thuật toán khai phá **tập phổ biến đóng** [25], trên tập huấn luyện.
- Giới hạn độ dài itemset ≤ 3.
- Chọn δ bằng phương pháp elbow [19, 38].
- Kết quả gồm danh sách FI kèm độ hỗ trợ, đánh chỉ mục để khớp nhanh với bài mới.

**M4 – Học Trans2Vec-JOI** [19].
- Huấn luyện PV-DBOW trên tập mẫu (item ∪ FI) của mỗi bài, d = 128, có negative sampling.
- Siêu tham số khởi điểm theo khuyến nghị của [28].
- Biến thể mở rộng (giải H1 và H3):
  - (i) nối thêm vector TF-IDF đã giảm chiều;
  - (ii) khởi tạo vector item từ embedding tiền huấn luyện [28];
  - (iii) thay FI bằng mẫu tuần tự theo Sqn2Vec [39].

**M5 – Suy luận vector** (giải H5).
- Với bài mới hoặc truy vấn $q$, cố định mọi vector item và FI rồi tối ưu riêng $f(q)$ vài vòng gradient [20].
- Nếu $q$ không chứa FI nào (thường gặp với truy vấn 2–3 từ), suy luận chỉ trên phần item.
- Nếu $q$ chứa item ngoài từ vựng, có thể mở rộng truy vấn bằng các từ gần nghĩa trong không gian vector item.

**M6 – Phân loại chuyên mục.**
- LR để triển khai; SVM tuyến tính để so sánh công bằng giữa các biểu diễn (Mục 6.3).
- Xử lý mất cân bằng bằng trọng số lớp [7].
- **Giải thích:** với mỗi chuyên mục $c$, lấy các FI có tích vô hướng lớn nhất với tâm (centroid) vector bài báo của $c$ làm "từ khóa chuyên mục". Cách này dùng được vì PV-DBOW học vector bài báo và vector mẫu qua chính tích vô hướng đó. Với mỗi bài, liệt kê các FI của bài thuộc nhóm đó.

**M7 – Tìm kiếm ngữ nghĩa.**
- Lưu vector của toàn bộ kho bài vào một chỉ mục vector và tìm top-k theo cosine.
- Có thể lọc trước theo chuyên mục dự đoán của truy vấn để giảm nhiễu và chi phí.
- Hỗ trợ hai kiểu truy vấn: **từ khóa** ("lãi suất căn hộ") và **bài tương tự** (truyền vào một bài báo).

### 9.3 Thiết kế thực nghiệm

**Bảng 9.1.** Ma trận thực nghiệm đề xuất

| Hạng mục | Nội dung |
|---|---|
| Dữ liệu | VNTC Level 1 (10 lớp) và Level 2 (27 lớp) [3]; một corpus khó ≥ 25 chuyên mục tự thu thập theo cách của [2] |
| Baseline thưa | BoW, TF-IDF → SVM / LR [2]; TF-IDF + OCFS / χ² ở 128 chiều [3, 7] |
| Baseline FI | FI-BIN, FI-SUP [19] |
| Baseline dày | TRANS-IT (≡ Doc2Vec PV-DBOW), PV-DM [20]; MLP-128 có giám sát [7]; Top2Vec [35] |
| Trần trên | PhoBERT fine-tune và PhoBERT/SBERT làm bộ mã hóa cho tìm kiếm [9, 23] |
| Phương pháp chính | TRANS-FI, Trans2Vec-IND, Trans2Vec-JOI và các biến thể ở M4 |
| Độ đo phân loại | Macro-F1 (chính), accuracy; trung bình ± độ lệch chuẩn qua 5 hạt giống |
| Độ đo tìm kiếm | Precision@10, MAP, nDCG@10 [30]; tài liệu liên quan = cùng chuyên mục (nhãn thay thế) |
| Độ đo phân cụm / diễn giải | NMI, ARI giữa cụm K-means trên f(T) và nhãn chuyên mục; đánh giá định tính FI chuyên mục |
| Chi phí | Số FI theo δ và k; thời gian FP-Growth, huấn luyện PV-DBOW, suy luận một truy vấn; bộ nhớ chỉ mục |

**Bảng 9.2.** Các thực nghiệm loại trừ (ablation) và giả thuyết

| Mã | Biến thay đổi | Giả thuyết |
|---|---|---|
| A1 | Từ (tách từ) so với âm tiết | Với âm tiết, FI bù đắp phần lớn việc thiếu tách từ: khoảng cách Macro-F1 giữa hai cấu hình **nhỏ hơn** ở Trans2Vec so với ở TF-IDF |
| A2 | k ∈ {20, 50, 100, toàn bộ} | Hiệu năng bão hòa quanh k ≈ 50, còn chi phí khai phá FI tăng vọt khi k lớn |
| A3 | FI thường, FI đóng, chỉ thực thể | FI đóng giữ hiệu năng với số FI nhỏ hơn nhiều |
| A4 | d ∈ {64, 128, 256} | Tồn tại d tối ưu ở mức trung bình, không tăng đơn điệu [19] |
| A5 | JOI so với JOI + TF-IDF so với JOI khởi tạo bằng vector tiền huấn luyện | Bổ sung tần suất hoặc tri thức ngoài cải thiện thêm, nhất là trên corpus khó |
| A6 | Truy vấn có FI và không có FI | Truy vấn chứa FI cho nDCG cao hơn; khoảng chênh đo được giá trị của FI cho tìm kiếm |

### 9.4 Kết quả kỳ vọng và tiêu chí thành công

Dựa trên bằng chứng ở Chương 8, kỳ vọng hợp lý là Trans2Vec-JOI:
- **(i)** vượt TF-IDF và Doc2Vec trên corpus khó;
- **(ii)** tiến gần mức của MLP-128 có giám sát [7] mà không dùng nhãn khi học biểu diễn;
- **(iii)** thấp hơn PhoBERT, nhưng với chi phí nhỏ hơn nhiều và không cần GPU;
- **(iv)** cho kết quả tìm kiếm tốt hơn TF-IDF cosine.

Đề tài được coi là thành công nếu (i), (iv) và giả thuyết A1 được xác nhận. Ngay cả khi kết quả âm tính, một so sánh có kiểm soát theo giao thức Mục 7.3 vẫn có giá trị, vì hiện chưa có bảng so sánh như vậy cho tin tức tiếng Việt (Mục 8.5).

### 9.5 Kết quả thực nghiệm sơ bộ trên VNTC-10

Thiết kế ở các Mục 9.1–9.3 đã được hiện thực và chạy trên toàn bộ VNTC-10 [3]: 33.759 bài huấn luyện, 50.373 bài kiểm tra, 10 chủ đề. Mã nguồn, dữ liệu dẫn xuất và báo cáo chi tiết nằm trong thư mục `experiments/` (tệp `RESULTS.md`).

**Cấu hình chính:**
- Tách từ bằng pyvi; từ dừng xác định theo dữ liệu (token xuất hiện trong hơn 30% bài huấn luyện).
- Giữ k = 50 item có tf·idf cao nhất mỗi bài.
- Khai phá itemset độ dài ≤ 3 với δ = 0,535% (chọn bằng elbow).
- PV-DBOW (gensim), d = 128, 20 epoch.
- Phân loại bằng SVM tuyến tính và hồi quy logistic với C = 1, trên vector chuẩn hóa L2.

Bài báo trung bình dài 488 âm tiết, xác nhận hạn chế H2: phải lọc item trước khi khai phá FI. Với k = 50 thu được 3.586 FI, trung bình 38 FI mỗi bài.

**Bảng 9.3.** Phân loại chuyên mục trên tập kiểm tra VNTC-10 (Macro-F1)

| Biểu diễn | SVM C = 1 | LR C = 1 |
|---|---|---|
| TF-IDF toàn văn | **0,903** | **0,907** |
| MLP-128 có giám sát [7] | 0,902 | — |
| TF-IDF trên 50 item mỗi bài | 0,889 | — |
| LDA-100 | 0,827 | — |
| FI-BIN | 0,824 | — |
| TRANS-IT (≡ Doc2Vec PV-DBOW) | 0,841 | 0,847 |
| TRANS-FI | 0,820 | 0,826 |
| **Trans2Vec-JOI** | **0,842** | **0,849** |
| Trans2Vec-JOI, vector huấn luyện lấy từ mô hình (3 seed) | 0,766 | 0,814 |

![Macro-F1 của các biểu diễn (SVM C = 1).](figures/fig_macro_f1.png)

**Bảng 9.4.** Tìm kiếm ngữ nghĩa (nDCG@10): 1.000 truy vấn, kho 33.759 bài, "liên quan" = cùng chủ đề

| Biểu diễn | Truy vấn là bài báo | Truy vấn 3 từ khóa |
|---|---|---|
| TF-IDF toàn văn | 0,740 | 0,634 |
| LDA-100 | 0,765 | — |
| TRANS-IT | 0,800 | — |
| **Trans2Vec-JOI** | **0,809** | **0,692** |

Đối chiếu với các kỳ vọng ở Mục 9.4:
- **(i) Không đạt.** Trans2Vec-JOI không vượt TF-IDF (0,849 so với 0,907 với LR) và chỉ ngang Doc2Vec (TRANS-IT 0,847). Trên VNTC, đóng góp của FI cho phân loại nằm trong khoảng −0,3 đến +0,9 điểm (Bảng 9.5), thấp hơn nhiều mức +2,7 trên Snippets [19]. Kết quả này phù hợp với hạn chế H1: biểu diễn dạng tập hợp bỏ mất tần suất từ, mà tần suất mang thông tin chuyên mục trong văn bản dài.
- **(ii) Không đạt.** Trans2Vec còn cách MLP-128 có giám sát khoảng 5 điểm. Đây là cái giá của việc học biểu diễn không dùng nhãn.
- **(iii) Chưa đo PhoBERT** (không có GPU). Riêng về chi phí, Trans2Vec rất rẻ: khai phá FI 3 giây, huấn luyện 16 giây, suy luận 50.373 bài 42 giây, toàn bộ trên CPU.
- **(iv) Đạt.** Ở bài toán tìm kiếm, Trans2Vec-JOI tốt nhất trong các biểu diễn không giám sát, hơn TF-IDF 7 điểm nDCG@10 với truy vấn là bài báo và gần 6 điểm với truy vấn 3 từ khóa. Phần lớn lợi thế này đến từ việc dùng vector dày, vì 94% truy vấn ngắn không chứa FI nào.
- **Giả thuyết A1 không được xác nhận.** Bỏ tách từ làm TF-IDF giảm 1,2 điểm nhưng làm Trans2Vec-JOI giảm 2,5 điểm (0,824 so với 0,849). FI không bù được việc thiếu tách từ. Chỉ 13,5% cặp âm tiết phổ biến trùng với một từ ghép của pyvi.

**Bảng 9.5.** Đóng góp của FI: Macro-F1(JOI) − Macro-F1(TRANS-IT)

| Cấu hình | FI / bài | Vector huấn luyện lấy từ mô hình | Vector huấn luyện suy luận lại |
|---|---|---|---|
| Từ, k = 50 | 38 | −0,5 | +0,1 |
| Từ, k = 100 | 282 | +3,7 | −0,3 |
| Âm tiết, k = 50 | 96 | +4,2 | +0,9 |

**Kiểm chứng cài đặt trên Snippets.** Để chắc rằng kết quả trên VNTC không do lỗi cài đặt, Trans2Vec được chạy lại trên Snippets bằng dữ liệu và tập phổ biến do chính tác giả công bố cùng mã nguồn (github.com/nphdang/Trans2Vec), với cấu hình của mã gốc (50 epoch, SVM C = 1). Kết quả (Bảng 9.6):
- TRANS-IT đạt 75,29%, khớp với 75,23% của [19], tức cách cài đặt là chính xác.
- Trans2Vec-JOI chỉ đạt 75,99% so với 79,05% công bố. Phần đóng góp của FI là +0,7 điểm, không phải +3,8.

Như vậy, việc FI đóng góp ít không phải đặc thù của tiếng Việt: nó cũng xảy ra trên chính dữ liệu của bài gốc.

Mã nguồn công bố còn khác bài báo ở bốn điểm:
1. vector được học **transductive**: Doc2Vec học trên cả tài liệu kiểm tra, không dùng nhãn;
2. 50 epoch, không được nêu trong bài;
3. có tùy chọn tinh chỉnh C;
4. một lỗi `if/else` khiến tập huấn luyện Snippets thực tế là 9.872 thay vì 10.060 bài.

**Bảng 9.6.** Tái hiện trên Snippets (accuracy %, 3 seed)

| Phương pháp | Bài báo [19] | Tái hiện, transductive như mã gốc | Inductive như Mục 9.5 |
|---|---|---|---|
| TRANS-IT | 75,23 | 75,29 | 73,44 |
| TRANS-FI | 77,88 | 75,23 | 74,84 |
| Trans2Vec-JOI | 79,05 | 75,99 | 76,51 |
| JOI − IT | +3,8 | +0,7 | +3,1 |

**Phát hiện về phương pháp đánh giá.** Cột giữa của Bảng 9.5 cho thấy một cái bẫy đánh giá cần đưa vào giao thức (Mục 7.3):
- Nếu vector huấn luyện lấy trực tiếp từ mô hình PV-DBOW còn vector kiểm tra được *suy luận*, hai tập vector có phân phối khác nhau.
- Hệ quả thứ nhất: Trans2Vec bị đánh giá thấp 7–8 điểm (0,766 so với 0,842).
- Hệ quả thứ hai: chọn C bằng cross-validation trên tập huấn luyện bị sai lệch, luôn chọn C lớn mà điểm kiểm tra lại giảm.
- Hệ quả thứ ba, nghiêm trọng nhất: xuất hiện những "cải thiện nhờ FI" giả, tới +3,7 và +4,2 điểm, rồi biến mất khi vector huấn luyện được suy luận bằng cùng quy trình như vector kiểm tra.

Thực nghiệm cũng tái hiện được kiểu lỗi đã nghi ở [8] (Mục 8.3): khi huấn luyện quá ít (5 epoch trên mẫu 3.000 bài), vector gần như không rời giá trị khởi tạo và độ chính xác rơi về mức đoán ngẫu nhiên. Ngoài ra, cách hiện thực phương pháp elbow ảnh hưởng mạnh tới kết quả. Chuẩn hóa trên thang log-log chọn δ = 2,16%, khiến 82% bài kiểm tra không còn FI nào dài ≥ 2. Chuẩn hóa tuyến tính, đúng như cách đọc hình trong [19], chọn δ = 0,535%.

**Giá trị diễn giải.** Dù không cải thiện độ chính xác phân loại, FI cho phần giải thích chuyên mục dễ đọc (mô-đun M6). Ví dụ:
- Kinh doanh: {doanh_nghiệp, thị_trường}, {tỷ, usd}.
- Thế giới: {bush, tổng_thống}, {baghdad, iraq}.
- Thể thao: {chung_kết, đội}.
- Vi tính: {e, mail}. pyvi tách sai "email" thành hai token, và FI đã tự ghép lại.

*Hạn chế của thực nghiệm:* mới dùng một corpus (VNTC-10, giai đoạn 2003–2006, 10 chủ đề khá tách bạch); kết quả "suy luận lại" mới chạy một seed; "liên quan" trong tìm kiếm là nhãn thay thế; chưa có PhoBERT, Top2Vec, Sqn2Vec.

## 10. Kết luận và hướng phát triển

### 10.1 Tóm tắt trả lời các câu hỏi nghiên cứu

| RQ | Trả lời | Mức chắc chắn |
|---|---|---|
| **RQ1** | Thách thức chính là tách từ (nhập nhằng nghĩa), bảng mã và dấu thanh, và danh sách từ dừng chủ quan. Vai trò của tiền xử lý **đi theo đường cong chữ U**: giảm dần từ biểu diễn thưa tới Transformer, rồi trở lại thành cốt lõi với biểu diễn dựa trên mẫu | Cao |
| **RQ2** | Biểu diễn thưa có chọn đặc trưng đủ cho tác vụ dễ; biểu diễn dày tạo khác biệt ở tác vụ khó; tri thức ngoài cho hiệu năng cao nhất với chi phí cao nhất. Chưa có so sánh đối đầu trên một corpus tin tức tiếng Việt công khai | Trung bình – Cao |
| **RQ3** | Trên Snippets (tiếng Anh), FI làm giàu embedding thêm 2,7 điểm [19]. **Thực nghiệm sơ bộ (Mục 9.5) không tái hiện được mức này, cả trên VNTC-10 lẫn trên chính Snippets với dữ liệu và mã nguồn của tác giả (+0,7 điểm):** khi đánh giá nhất quán, FI chỉ đóng góp −0,3 đến +0,9 điểm Macro-F1, và Trans2Vec (0,849) vẫn kém TF-IDF (0,907). Giá trị của FI cho tin tức tiếng Việt nằm ở **tìm kiếm** (biểu diễn không giám sát tốt nhất, hơn TF-IDF 7 điểm nDCG@10), ở **diễn giải** chuyên mục, và ở **chi phí thấp** (dưới 1 phút trên CPU) | Trung bình (một corpus, một seed cho bản đánh giá nhất quán) |
| **RQ4** | SVM là chuẩn so sánh, LR là lựa chọn triển khai. Tìm kiếm top-k cần biểu diễn dày và sạch vì kNN nhạy với nhiễu. Trans2Vec nằm giữa TF-IDF và PhoBERT trên trục chi phí | Cao |
| **RQ5** | Chưa đủ chuẩn: dữ liệu phân mảnh, giao thức không thống nhất, có dấu hiệu rò rỉ và lỗi tái lập. Bài đề xuất một giao thức tối thiểu (Mục 7.3) | Cao |

### 10.2 Khoảng trống nghiên cứu

Phân loại chuyên mục tin tức tiếng Việt đã được nghiên cứu qua ba thế hệ biểu diễn. Khai phá tập phổ biến đã được dùng cho văn bản, kể cả tiếng Việt, nhưng chỉ dưới dạng đặc trưng thưa hoặc luật [15, 16, 18]. Hướng **học embedding từ mẫu phổ biến**, gồm Trans2Vec và họ phương pháp của nó [19, 39, 40], **chưa được áp dụng cho văn bản tiếng Việt, chưa được kiểm chứng trên văn bản dài như tin tức, và chưa được dùng cho tìm kiếm**.

### 10.3 Hướng phát triển

1. **Mở rộng thực nghiệm ở Mục 9.5:** chạy nhiều seed cho bản đánh giá nhất quán; thêm một corpus khó (≥ 25 chuyên mục), PhoBERT và Top2Vec; quét δ có hệ thống thay vì chỉ dùng elbow; tìm cách đưa lại thông tin tần suất vào Trans2Vec (H1), vì phép ghép thẳng với TF-IDF chưa hiệu quả.
2. **Mở rộng sang mẫu tuần tự** với Sqn2Vec [39], để giữ thứ tự từ, và sang **đồ thị từ** [38, 40].
3. **Kết hợp tri thức ngoài:** khởi tạo vector item từ embedding tiền huấn luyện, hoặc dùng FI làm tín hiệu bổ sung cho bộ mã hóa PhoBERT.
4. **Phân loại phân cấp:** tận dụng cấu trúc chuyên mục cha – con (VNTC Level 1 – Level 2) và cây chủ đề từ FI [16].
5. **Xây dựng một benchmark tin tức tiếng Việt công khai, khó, có giao thức chuẩn**, cho cả phân loại lẫn tìm kiếm, theo tinh thần của VN-MTEB [43] nhưng trên dữ liệu gốc tiếng Việt thay vì dữ liệu dịch.

---

## Phụ lục A. Bảng tóm tắt các công trình nòng cốt

| Công trình | Năm | Dữ liệu | Biểu diễn | Bộ phân loại | Kết quả chính | Nhánh |
|---|---|---|---|---|---|---|
| Hoang và cs. [3] | 2007 | VNTC 10 / 27 lớp | BoW + OCFS; n-gram âm tiết | SVM; NB-LM | 96,21% / 95,58% | A1, A2, B1 |
| Nguyen và cs. [4] | 2009 | 4 lớp; 2 lớp thể loại | Bag-of-syllables; IG; từ điển | NB, kNN, SVM | 98,6%; 89,8% | A1, B1, B2 |
| Pham Van & Ta Minh [5] | 2017 | VNTC | KEBoW | MLP 6 lớp | 99,75% (nghi rò rỉ) | B3 |
| Duong & Hoang [2] | 2019 | VNNews-01, 25 lớp | TF-IDF | 8 bộ phân loại | F1 0,749 | A2 |
| Huynh và cs. [6] | 2020 | 15 lớp | Từ khóa TextRank | Jaccard | 95,40% | B3 |
| Pham và cs. [10] | 2020 | VLSP HSD | PhoBERT | Fine-tune | Macro-F1 0,7221 | F |
| Vinh & Kha [7] | 2021 | 30 lớp | MLP-128 | SVM | > χ², OCFS | C |
| Huong và cs. [8] | 2022 | Cảm xúc | TF-IDF, W2V, GloVe, D2V | 5 bộ phân loại | TF-IDF 86,8% | D1, D2 |
| Luu và cs. [11] | 2024 | ViHSD, UIT-ViCTSD | 7 mô hình BERT | Fine-tune + EDA | Macro-F1 74,63 | F |
| Nguyen và cs. [12] | 2025 | Shopee, đa nhãn | BoW … PhoBERT; LDA, Top2Vec, BERTopic | LR, SVM, XGB | Macro-F1 0,96 | D, F |
| Nguyen và cs. [19] | 2018 | Snippets + 3 tập | Trans2Vec | SVM | 79,05% (Snippets) | E2 |

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

## Tài liệu tham khảo

[1] F. Sebastiani, "Machine learning in automated text categorization," *ACM Computing Surveys*, vol. 34, no. 1, pp. 1–47, 2002.

[2] H.-T. Duong and V. T. Hoang, "A survey on the multiple classifier for new benchmark dataset of Vietnamese news classification," in *Proc. 11th Int. Conf. Knowledge and Smart Technology (KST)*, 2019, pp. 23–28.

[3] V. C. D. Hoang, D. Dinh, N. L. Nguyen, and H. Q. Ngo, "A comparative study on Vietnamese text classification methods," in *Proc. IEEE Int. Conf. Research, Innovation and Vision for the Future (RIVF)*, 2007, pp. 267–273.

[4] G.-S. Nguyen, X. Gao, and P. Andreae, "Text categorization for Vietnamese documents," in *Proc. IEEE/WIC/ACM Int. Joint Conf. Web Intelligence and Intelligent Agent Technology (WI-IAT)*, 2009, pp. 466–469, doi: 10.1109/WI-IAT.2009.327.

[5] T. Pham Van and T. Ta Minh, "Vietnamese news classification based on BoW with keywords extraction and neural network," in *Proc. 21st Asia Pacific Symp. Intelligent and Evolutionary Systems (IES)*, 2017, pp. 43–48.

[6] H. T. Huynh, N. Duong-Trung, X. S. Ha, N. Q. T. Tang, H. X. Huynh, and D. Q. Truong, "Automatic keywords-based classification of Vietnamese texts," in *Proc. 2020 RIVF Int. Conf. Computing and Communication Technologies (RIVF)*, 2020, pp. 1–3, doi: 10.1109/RIVF48685.2020.9140761.

[7] T. N. P. Vinh and H. H. Kha, "Feature extraction using neural networks for Vietnamese text classification," in *Proc. Int. Symp. Electrical and Electronics Engineering (ISEE)*, 2021, pp. 120–124, doi: 10.1109/ISEE51682.2021.9418674.

[8] T. H. Huong, D. T. C. Lai, K. Tran-Trung, and V. T. Hoang, "Sentiment analysis based on word vector representation for short comments in Vietnamese language," in *Proc. 9th NAFOSTED Conf. Information and Computer Science (NICS)*, 2022, pp. 165–169, doi: 10.1109/NICS56915.2022.10013426.

[9] D. Q. Nguyen and A. T. Nguyen, "PhoBERT: Pre-trained language models for Vietnamese," in *Findings of the Association for Computational Linguistics: EMNLP 2020*, 2020, pp. 1037–1042.

[10] Q. H. Pham, V. A. Nguyen, L. B. Doan, N. N. Tran, and T. M. Thanh, "From universal language model to downstream task: Improving RoBERTa-based Vietnamese hate speech detection," in *Proc. 12th Int. Conf. Knowledge and Systems Engineering (KSE)*, 2020, pp. 37–42.

[11] S. T. Luu, K. V. Nguyen, and N. L.-T. Nguyen, "An approach of data augmentation to improve the performance of BERTology models for Vietnamese hate speech detection," *Multimedia Tools and Applications*, vol. 83, pp. 56763–56783, 2024, doi: 10.1007/s11042-023-16968-5.

[12] T. D. Nguyen, D. M. Nguyen, H. M. Nguyen, and T. Q. G. Nguyen, "Topic classification of Vietnamese product reviews in e-commerce using PhoBERT," *J. Marketing Analytics*, vol. 13, pp. 371–385, 2025, doi: 10.1057/s41270-025-00402-w.

[13] R. Agrawal and R. Srikant, "Fast algorithms for mining association rules in large databases," in *Proc. 20th Int. Conf. Very Large Data Bases (VLDB)*, 1994, pp. 487–499.

[14] J. Han, J. Pei, and Y. Yin, "Mining frequent patterns without candidate generation," in *Proc. ACM SIGMOD Int. Conf. Management of Data*, 2000, pp. 1–12, doi: 10.1145/342009.335372.

[15] F. Beil, M. Ester, and X. Xu, "Frequent term-based text clustering," in *Proc. 8th ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining*, 2002, pp. 436–442, doi: 10.1145/775047.775110.

[16] B. C. M. Fung, K. Wang, and M. Ester, "Hierarchical document clustering using frequent itemsets," in *Proc. SIAM Int. Conf. Data Mining (SDM)*, 2003, pp. 59–70, doi: 10.1137/1.9781611972733.6.

[17] H. Cheng, X. Yan, J. Han, and C.-W. Hsu, "Discriminative frequent pattern analysis for effective classification," in *Proc. IEEE 23rd Int. Conf. Data Engineering (ICDE)*, 2007, pp. 716–725.

[18] Đỗ Phúc, "Nghiên cứu ứng dụng tập phổ biến và luật kết hợp vào bài toán phân loại văn bản tiếng Việt có xem xét ngữ nghĩa [Research on application of frequent sets and association rules to semantic Vietnamese document classification]," *Tạp chí Phát triển Khoa học và Công nghệ (ĐHQG-HCM)*, vol. 9, no. 2, p. 23, 2006.

[19] D. Nguyen, T. D. Nguyen, W. Luo, and S. Venkatesh, "Trans2Vec: Learning transaction embedding via items and frequent itemsets," in *Advances in Knowledge Discovery and Data Mining (PAKDD 2018)*, LNAI vol. 10939, Springer, 2018, pp. 361–372, doi: 10.1007/978-3-319-93040-4_29.

[20] Q. Le and T. Mikolov, "Distributed representations of sentences and documents," in *Proc. 31st Int. Conf. Machine Learning (ICML)*, 2014, pp. 1188–1196.

[21] T. Vu, D. Q. Nguyen, D. Q. Nguyen, M. Dras, and M. Johnson, "VnCoreNLP: A Vietnamese natural language processing toolkit," in *Proc. NAACL-HLT 2018: Demonstrations*, 2018, pp. 56–60.

[22] V. Karpukhin *et al.*, "Dense passage retrieval for open-domain question answering," in *Proc. EMNLP*, 2020, pp. 6769–6781, doi: 10.18653/v1/2020.emnlp-main.550.

[23] N. Reimers and I. Gurevych, "Sentence-BERT: Sentence embeddings using Siamese BERT-networks," in *Proc. EMNLP-IJCNLP*, 2019, pp. 3982–3992, doi: 10.18653/v1/D19-1410.

[24] P. Fournier-Viger, J. C.-W. Lin, B. Vo, T. T. Chi, J. Zhang, and H. B. Le, "A survey of itemset mining," *WIREs Data Mining and Knowledge Discovery*, vol. 7, no. 4, e1207, 2017.

[25] M. J. Zaki and C.-J. Hsiao, "CHARM: An efficient algorithm for closed itemset mining," in *Proc. SIAM Int. Conf. Data Mining (SDM)*, 2002, pp. 457–473.

[26] B. Liu, W. Hsu, and Y. Ma, "Integrating classification and association rule mining," in *Proc. 4th Int. Conf. Knowledge Discovery and Data Mining (KDD)*, 1998, pp. 80–86.

[27] T. Mikolov, I. Sutskever, K. Chen, G. S. Corrado, and J. Dean, "Distributed representations of words and phrases and their compositionality," in *Advances in Neural Information Processing Systems (NIPS)*, 2013, pp. 3111–3119.

[28] J. H. Lau and T. Baldwin, "An empirical evaluation of doc2vec with practical insights into document embedding generation," in *Proc. 1st Workshop on Representation Learning for NLP*, 2016, pp. 78–86.

[29] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, "BERT: Pre-training of deep bidirectional transformers for language understanding," in *Proc. NAACL-HLT*, 2019, pp. 4171–4186.

[30] K. Järvelin and J. Kekäläinen, "Cumulated gain-based evaluation of IR techniques," *ACM Trans. Information Systems*, vol. 20, no. 4, pp. 422–446, 2002.

[31] T. Joachims, "Text categorization with support vector machines: Learning with many relevant features," in *Proc. 10th European Conf. Machine Learning (ECML)*, LNCS vol. 1398, 1998, pp. 137–142.

[32] Y. Yang and J. O. Pedersen, "A comparative study on feature selection in text categorization," in *Proc. 14th Int. Conf. Machine Learning (ICML)*, 1997, pp. 412–420.

[33] R. Mihalcea and P. Tarau, "TextRank: Bringing order into texts," in *Proc. Conf. Empirical Methods in Natural Language Processing (EMNLP)*, 2004, pp. 404–411.

[34] D. M. Blei, A. Y. Ng, and M. I. Jordan, "Latent Dirichlet allocation," *J. Machine Learning Research*, vol. 3, pp. 993–1022, 2003.

[35] D. Angelov, "Top2Vec: Distributed representations of topics," arXiv:2008.09470, 2020.

[36] M. Grootendorst, "BERTopic: Neural topic modeling with a class-based TF-IDF procedure," arXiv:2203.05794, 2022.

[37] X.-H. Phan, L.-M. Nguyen, and S. Horiguchi, "Learning to classify short and sparse text & web with hidden topics from large-scale data collections," in *Proc. 17th Int. Conf. World Wide Web (WWW)*, 2008, pp. 91–100, doi: 10.1145/1367497.1367510.

[38] F. Rousseau, E. Kiagias, and M. Vazirgiannis, "Text categorization as a graph classification problem," in *Proc. 53rd Annu. Meeting of the ACL and 7th IJCNLP*, 2015, pp. 1702–1712.

[39] D. Nguyen, W. Luo, T. D. Nguyen, S. Venkatesh, and D. Phung, "Sqn2Vec: Learning sequence representation via sequential patterns with a gap constraint," in *Proc. ECML PKDD 2018*, LNCS vol. 11052, Springer, 2018, pp. 569–584, doi: 10.1007/978-3-030-10928-8_34.

[40] D. Nguyen, W. Luo, T. D. Nguyen, S. Venkatesh, and D. Phung, "Learning graph representation via frequent subgraphs," in *Proc. SIAM Int. Conf. Data Mining (SDM)*, 2018, pp. 306–314.

[41] D. Nguyen, W. Luo, B. Vo, L. T. T. Nguyen, and W. Pedrycz, "Con2Vec: Learning embedding representations for contrast sets," *Knowledge-Based Systems*, vol. 229, Art. no. 107382, Oct. 2021, doi: 10.1016/j.knosys.2021.107382.

[42] B. Wang, R. Qi, J. Gao, J. Zhang, X. Yuan, and W. Ke, "Mining the frequent patterns of named entities for long document classification," *Applied Sciences*, vol. 12, no. 5, Art. no. 2544, 2022, doi: 10.3390/app12052544.

[43] L. Pham, T. Luu, T. Vo, M. Nguyen, and V. Hoang, "VN-MTEB: Vietnamese massive text embedding benchmark," in *Findings of the Association for Computational Linguistics: EACL 2026*, 2026, arXiv:2507.21500.
