## 2. Đặc thù xử lý văn bản tiếng Việt

### 2.1 Âm tiết, từ và bài toán tách từ

Tiếng Việt là ngôn ngữ đơn lập. Đơn vị viết cách nhau bằng khoảng trắng là **âm tiết** (Hoang và cộng sự gọi là *morpho-syllable* [@hoang2007]), chứ không phải từ. Một âm tiết có thể là một từ, một hình vị, hoặc không mang nghĩa độc lập. Nguyen và cộng sự ghi nhận **hơn 80% từ tiếng Việt có hai âm tiết** [@nguyen2009]. Vì vậy việc xác định ranh giới từ, tức **tách từ** (word segmentation), là bước tiền xử lý đặc thù, và cách tách khác nhau có thể dẫn tới nghĩa khác nhau. Ba ví dụ kinh điển trong các công trình được khảo sát:

| Câu | Cách tách 1 | Cách tách 2 | Hệ quả với phân loại | Nguồn |
|---|---|---|---|---|
| "Một luật gia cầm cự với tình hình hiện nay" | luật_gia / cầm_cự → *Chính trị – Xã hội* | gia_cầm → *Sức khỏe (cúm gia cầm)* | Đổi chuyên mục | [@hoang2007] |
| "học sinh ra từ hành" | học / sinh_ra / từ / hành | học_sinh / ra / từ / hành | Cả hai cách đều gồm các từ có thật | [@nguyen2009] |
| "Bảo lãnh bằng chứng khoán" | bảo_lãnh / bằng / chứng_khoán → *Tài chính* | bảo_lãnh / bằng_chứng / khoán → lệch nghĩa, nghiêng về *Pháp luật* | Từ khóa sai, phân loại sai | [@van2017; @hien2024] |

Các công trình xử lý vấn đề này theo hai hướng:
- **Dùng bộ tách từ:** MaxEnt [@hoang2007], vnTokenizer [@van2017; @hien2024; @le2013vnlp], pyvi [@huong2022; @luu2024], VnCoreNLP/RDRSegmenter [@vncorenlp2018; @pham2020]. Rủi ro là lỗi tách từ lan truyền sang các bước sau. Pham Van và Ta Minh xếp sự phụ thuộc vào thư viện tách từ vào danh sách hạn chế chính [@van2017].
- **Tránh tách từ:** làm việc trực tiếp với âm tiết, qua bag-of-syllables [@nguyen2009], mô hình ngôn ngữ n-gram âm tiết [@hoang2007], hoặc tổ hợp unigram + bigram [@vinh2021]. Hoang và cộng sự cho thấy mô hình n-gram âm tiết đạt độ chính xác ngang SVM trên túi từ (95,58% so với 96,21%) mà không cần tách từ hay chọn đặc trưng [@hoang2007].

Bài toán ranh giới từ không riêng tiếng Việt. Sogou News, một benchmark tin tức tiếng Trung, cũng là văn bản không có ranh giới từ tường minh [@minaee2021]. Tiếng Việt khác ở chỗ khoảng trắng vẫn tách *âm tiết*, nên luôn có một mức biểu diễn dùng được mà không cần bộ tách từ.

**Chi phí và độ tin cậy của công cụ.** Tách từ không phải nút thắt về tốc độ: bộ công cụ VNLP tách 2 triệu âm tiết trong 6 giây sau khi tối ưu, so với 234 giây của bản vnTokenizer gốc [@le2013vnlp]. Các công cụ sâu hơn thì còn yếu. Trong cùng bộ công cụ, nhận diện thực thể theo luật chỉ đạt F1 0,58, và phân tích phụ thuộc đạt khoảng 70% [@le2013vnlp]. Vì vậy, phương pháp nào cần nhiều tầng phân tích ngôn ngữ (từ loại, phụ thuộc, thực thể) sẽ chịu lan truyền lỗi lớn khi chuyển sang tiếng Việt (Mục 4.7).

**Bằng chứng từ thực nghiệm của đề tài.** Trên VNTC-10, bỏ tách từ làm mọi biểu diễn mất 1–3 điểm Macro-F1 (thực nghiệm A1, Mục 9.5). Nói cách khác, với tin tức tiếng Việt, tách từ vẫn có ích, dù không bắt buộc.

### 2.2 Bảng mã, dấu thanh và biến thể chính tả

Văn bản tiếng Việt điện tử từng tồn tại ở nhiều bảng mã (TELEX, VNI, TCVN3, VIQR, Unicode). Vị trí dấu thanh cũng không thống nhất (ví dụ "hoà" và "hòa"), và có biến thể chính tả như "thời kỳ" và "thời kì". Nếu không chuẩn hóa, cùng một từ sẽ thành nhiều đặc trưng khác nhau. Các công trình sớm đều xây bước chuẩn hóa riêng [@hoang2007; @nguyen2009]. Ngày nay chuẩn hóa Unicode vẫn được dùng như bước đầu tiên, kể cả trong các hệ thống dựa trên Transformer [@pham2020].

**Dấu thanh trong tìm kiếm.** Các công trình khảo sát chỉ bàn dấu thanh ở góc độ phân loại. Với tìm kiếm, vấn đề khác hẳn, vì người dùng có thể gõ không dấu. Thực nghiệm của đề tài trên chỉ mục BM25 (Mục 9.5) cho thấy hai mặt của cùng một lựa chọn:
- **Giữ dấu** tốt hơn khi truy vấn có dấu: nDCG@10 0,653 so với 0,621 khi gộp dấu. Lý do là gộp dấu dồn "bàn", "bán", "bản", "ban" thành một token; token đó khớp khoảng 63% số bài của kho.
- **Gộp dấu** là bắt buộc khi truy vấn không dấu. Trên chỉ mục giữ dấu, truy vấn không dấu chỉ còn nDCG@10 0,394, và 9% truy vấn không có kết quả nào.

Hệ thống vì vậy giữ cả hai dạng và chọn theo truy vấn. Chi tiết ở Mục 9.2.

### 2.3 Từ dừng và từ vựng

Danh sách từ dừng tiếng Việt thường được **xây thủ công** và thiếu chuẩn chung: khoảng 900 từ trong [@hoang2007], khoảng 2.000 từ trong [@van2017; @hien2024]. Tính chủ quan của danh sách được chính các tác giả nêu là một nguồn sai số [@van2017]. Một hướng khác là lọc từ vựng bằng từ điển, chỉ giữ các gram ứng với từ có thật. Cách này giảm từ vựng bigram từ 300.000 xuống 30.000 và đặc biệt có lợi cho kNN, vốn nhạy với đặc trưng nhiễu [@nguyen2009].

### 2.4 Tầm quan trọng của tiền xử lý thay đổi theo họ biểu diễn

Một quan sát xuyên suốt của khảo sát này: tiền xử lý **không có vai trò cố định**, mà phụ thuộc vào cách biểu diễn được dùng (Bảng 2.1).
- **Với mô hình Transformer:** Luu và cộng sự cho thấy các bước tiền xử lý truyền thống (bỏ từ dừng, chuyển chữ thường, bỏ emoji, hashtag, URL) **không cải thiện, thậm chí làm giảm** hiệu năng [@luu2024]. Ngoại lệ duy nhất là tách từ bằng VnCoreNLP cho PhoBERT, giúp tăng khoảng 2 điểm Macro-F1, vì PhoBERT được tiền huấn luyện trên văn bản đã tách từ theo cách này [@luu2024; @phobert2020].
- **Với biểu diễn dựa trên tập hợp và mẫu** (từ khóa, Trans2Vec): tiền xử lý quyết định *những item nào tồn tại*, và do đó những tập phổ biến nào được khai phá. Vai trò của nó vì vậy là cốt lõi.

**Bảng 2.1.** Vai trò của tiền xử lý theo họ biểu diễn (tổng hợp từ các công trình khảo sát)

| Bước | Âm tiết / n-gram | TF-IDF + chọn đặc trưng | Từ khóa | Embedding tĩnh | **Trans2Vec** | PhoBERT / BERT |
|---|---|---|---|---|---|---|
| Chuẩn hóa mã, dấu | Cần | Cần | Cần | Cần | **Cần** | Cần |
| Tách từ | Không cần [@hoang2007; @nguyen2009] | Cần | Cần; lỗi lan truyền [@van2017] | Cần [@huong2022] | **Tùy chọn, cần thực nghiệm** | Cần cho PhoBERT [@luu2024] |
| Bỏ từ dừng | Có ích | Có ích | Rất quan trọng | Có ích | **Rất quan trọng** | Vô ích hoặc có hại [@luu2024] |
| Lọc từ vựng / top-k | — | Giúp kNN [@nguyen2009] | Bản chất phương pháp | — | **Bắt buộc** (Mục 5.6) | — |

Bảng 2.1 cho thấy một **đường cong chữ U**. Vai trò của tri thức ngôn ngữ tiếng Việt giảm dần từ biểu diễn thưa đến Transformer, rồi tăng trở lại với biểu diễn dựa trên mẫu. Đây là luận điểm đầu tiên trả lời RQ1. Nó cũng là lý do Chương 9 đặt tiền xử lý thành một mô-đun có thể cấu hình, kèm thực nghiệm loại trừ (ablation).
