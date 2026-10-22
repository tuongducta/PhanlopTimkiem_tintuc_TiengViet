## 5. Trans2Vec và mô thức biểu diễn dựa trên mẫu phổ biến

### 5.1 Ý tưởng

Trans2Vec [@trans2vec] giải bài toán nêu ở Mục 3.2. Đầu vào là dữ liệu transaction; mục tiêu là học hàm $f: D\to\mathbb{R}^d$ **không giám sát**, sao cho hai transaction giống nhau có vector gần nhau. Ý tưởng cốt lõi là **dùng FI như "từ" trong mô hình PV-DBOW**. FI mang thông tin đồng xuất hiện bậc cao mà item đơn lẻ không có. PV-DBOW nén thông tin đó vào một vector dày $d$ chiều, nhờ vậy loại bỏ cả vấn đề số chiều cao lẫn vấn đề vector thưa của biểu diễn FI nhị phân.

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

**Chọn tham số.** Số chiều $d=128$. Ngưỡng δ được chọn bằng **phương pháp elbow** trên đường cong "số FI theo δ" của tập huấn luyện, tức chọn điểm mà khi giảm δ thêm thì số FI bắt đầu tăng vọt. Cách chọn này không dùng nhãn [@trans2vec; @rousseau2015].

### 5.3 Kết quả gốc

Trans2Vec được đánh giá trên bốn tập dữ liệu:
- **Snippets:** đoạn trích kết quả tìm kiếm web, 8 lĩnh vực, 12.340 mẫu, tiếng Anh [@phan2008];
- **Cancer** (bệnh án), **Retail** (bán lẻ), **Food** (giỏ thực phẩm).

Vector được đưa vào SVM tuyến tính với C = 1 cố định, chạy lặp 10 lần trên cùng tập huấn luyện và tập kiểm tra (Bảng 5.1).

**Bảng 5.1.** Accuracy / Macro-F1 (%) của Trans2Vec và các baseline, trích từ [@trans2vec]

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
| Trans2Vec [@trans2vec] | Tập hợp (transaction) | Frequent itemset | Bài báo = tập từ |
| Sqn2Vec [@sqn2vec] | Chuỗi | Mẫu tuần tự có ràng buộc khoảng cách (gap) | Bài báo = **chuỗi** từ, **giữ được thứ tự** |
| Graph embedding qua đồ thị con phổ biến [@gefsg2018] | Đồ thị | Đồ thị con phổ biến | Kết hợp được với graph-of-words [@rousseau2015] |
| Con2Vec [@con2vec] | Transaction có biến mục tiêu | Contrast set | Phiên bản có định hướng nhãn |

Cũng theo hướng dùng mẫu cho văn bản, Rousseau và cộng sự biểu diễn văn bản bằng đồ thị từ (graph-of-words) và khai phá **đồ thị con phổ biến** làm đặc trưng, tức "n-gram khoảng cách xa" [@rousseau2015]. Wang và cộng sự giới hạn việc khai phá trên **thực thể có tên** để xử lý văn bản dài nhiều nhiễu [@wang2022]. Các công trình sớm hơn dùng tập từ phổ biến để **phân cụm văn bản** [@beil2002] và xây **cây chủ đề phân cấp** có nhãn diễn giải được [@fung2003].

Như vậy, dùng tập phổ biến cho văn bản không phải ý tưởng mới. Điểm mới của nhánh E2 là **dùng mẫu làm đơn vị học embedding**. Nhờ đó biểu diễn vừa dày, vừa không giám sát, vừa chuyển giao được giữa các tác vụ phân loại, phân cụm và tìm kiếm.

**Tương tác ký hiệu và tương tác tiềm ẩn.** Cả ba hướng E, F2, G đều xuất phát từ cùng một quan sát: tương tác giữa các đơn vị bổ sung thông tin cho biểu diễn bậc một. Chúng khác nhau ở *nơi* tương tác được mô hình hóa (Bảng 5.3).

**Bảng 5.3.** Ba cách đưa đồng xuất hiện vào biểu diễn

| | Trans2Vec [@trans2vec] | TextGCN và biến thể [@onan2023] | LLMEmbed [@liu2024] |
|---|---|---|---|
| Đơn vị tương tác | Tập từ cùng xuất hiện trong bài | Cặp từ, cặp từ – tài liệu | Cặp chiều của vector ẩn |
| Bậc | Cao (tới độ dài FI) | Hai | Hai |
| Cách có | Đếm tường minh, lọc theo δ | Trọng số cạnh (PMI) | Tích ngoài $\phi\phi^\top$ |
| Đọc được? | Có, FI là cụm từ | Một phần | Không |
| Cần gì | CPU, không nhãn | GPU, công cụ ngôn ngữ | GPU, mô hình 7 tỉ tham số |

Trans2Vec là cách duy nhất trong ba cách cho ra tương tác **đọc được** và chạy được trên CPU. Đổi lại, nó chỉ nhìn thấy tương tác ở mức ký hiệu, nên không nắm được từ đồng nghĩa hay các từ khác mặt chữ mà cùng nghĩa.

### 5.5 Vì sao phù hợp với tin tức tiếng Việt

1. **Cụm đồng xuất hiện mang tính chuyên mục.** Chuyên mục tin tức thường được nhận diện qua tổ hợp từ hơn là từ đơn lẻ. Ví dụ "lãi suất" xuất hiện ở cả Kinh doanh lẫn Bất động sản, nhưng {lãi_suất, căn_hộ, dự_án} thì chỉ thuộc Bất động sản. FI nắm được những tổ hợp này một cách tường minh. Snippets, tập mà Trans2Vec thắng rõ nhất, cũng là bài toán phân loại lĩnh vực của văn bản.
2. **Giảm phụ thuộc vào tách từ.** Hơn 80% từ tiếng Việt có hai âm tiết [@nguyen2009], nên nếu chọn item là âm tiết, FI hai phần tử có thể đóng vai từ ghép. Khác với n-gram [@hoang2007], FI không đòi hỏi các phần tử đứng liền nhau. Đây là một **giả thuyết cần kiểm chứng**, chưa phải kết luận.
3. **Không giám sát.** Biểu diễn học được trên toàn bộ kho bài, kể cả bài chưa có chuyên mục, và dùng được ngay cho tìm kiếm cũng như phân cụm. Điều này khác với đặc trưng gắn nhãn của [@vinh2021].
4. **Diễn giải được và chi phí thấp.** FI là các cụm từ đọc được, nên có thể dùng để giải thích vì sao một bài được xếp vào một chuyên mục. Về nguyên tắc, toàn bộ quy trình (FP-Growth và PV-DBOW) chạy được trên CPU, khác với yêu cầu GPU của PhoBERT [@nguyen2025]. Chi phí thực tế vẫn cần được đo (H7, Mục 5.6).

### 5.6 Phân tích phản biện: tám hạn chế khi áp dụng cho tin tức

**Bảng 5.4.** Hạn chế của Trans2Vec, hệ quả với tin tức tiếng Việt và hướng giải quyết có cơ sở tài liệu

| # | Hạn chế | Hệ quả với tin tức tiếng Việt | Hướng giải quyết |
|---|---|---|---|
| **H1** | Transaction là *tập*, nên mất tần suất và thứ tự từ | Tin tức dài; tần suất từ mang thông tin chuyên mục | Sqn2Vec [@sqn2vec]; nối thêm TF-IDF; khai phá FI trên cửa sổ câu |
| **H2** | Transaction trong thực nghiệm gốc rất ngắn (trung bình 6–27 item) | Bài báo có hàng trăm từ, nên số FI **bùng nổ tổ hợp** khi δ nhỏ | Giữ top-k từ mỗi bài theo TF-IDF hoặc TextRank (k ≈ 50 [@huynh2020]); dùng tập phổ biến đóng [@zaki2002; @zhang2025]; item là thực thể có tên [@wang2022; @vncorenlp2018]; giới hạn độ dài itemset ≤ 3. Bùng nổ tổ hợp vẫn là bài toán mở của khai phá FI, nên hậu xử lý kiểu top-k là cần thiết [@trasierras2024] |
| **H3** | Baseline yếu: không có LDA, PV-DM hay BERT; SVM không tinh chỉnh; không báo độ lệch chuẩn | Không biết Trans2Vec đứng ở đâu so với các phương pháp hiện đại | So sánh thêm với [@vinh2021], LDA [@blei2003], Top2Vec [@angelov2020], PhoBERT [@phobert2020] |
| **H4** | Hiệu quả phụ thuộc dữ liệu (Cancer: mọi phương pháp ≈ 50%) | Cần đánh giá trên cả corpus dễ và corpus khó | VNTC-10 và VNTC-27 / corpus ≥ 25 chuyên mục [@hoang2007; @duong2019]; mô tả corpus bằng hồ sơ dữ liệu giao dịch [@trasierras2024] |
| **H5** | Không mô tả cách suy luận vector cho transaction mới | Chức năng tìm kiếm cần vector cho **truy vấn**. Truy vấn ngắn có thể không chứa FI nào | Suy luận PV-DBOW [@le2014; @lau2016]; dự phòng chỉ dùng phần item; mở rộng truy vấn |
| **H6** | Chỉ đánh giá phân loại | Phần tìm kiếm và phân cụm chưa được kiểm chứng | Đo Precision@k, nDCG [@jarvelin2002], NMI/ARI; dùng FI làm nhãn chủ đề diễn giải được [@fung2003] |
| **H7** | Không báo chi phí tính toán | Không đánh giá được tính khả thi khi triển khai | Đo thời gian khai phá FI theo δ và thời gian huấn luyện, theo mẫu của [@duong2019; @nguyen2025] |
| **H8** | Các FI cùng lớp tương đương (cùng tập transaction) đều được đưa vào làm token riêng | Trong PV-DBOW, các token này có ngữ cảnh trùng hoàn toàn, làm tăng từ vựng mà không thêm tín hiệu | Chỉ giữ FI đóng, đại diện duy nhất của mỗi lớp [@zhang2025] |

Hạn chế H8 do bài khảo sát nêu ra, dựa trên tính chất lớp tương đương của [@zhang2025]. Thực nghiệm E8 (Mục 9.5) cho thấy H8 ít xảy ra với tin tức: sau khi lọc top-k, FI không đóng chỉ chiếm 0–0,17% trên VNTC và tối đa 3,4% trên Snippets.

Hạn chế H3 cần được nhấn mạnh. Trên **chính tập Snippets**, Phan và cộng sự đạt **82,18%** khi bổ sung chủ đề ẩn học từ Wikipedia [@phan2008], cao hơn mức 79,05% của Trans2Vec-JOI. Bài Trans2Vec không so sánh với kết quả này. Hai con số không cùng điều kiện, vì một bên dùng dữ liệu ngoài và bộ phân loại MaxEnt. Dù vậy, so sánh này cho thấy **tri thức ngoài vẫn vượt embedding chỉ học từ dữ liệu nội tại**. Đó là lý do Chương 9 đề xuất thử nghiệm khởi tạo Trans2Vec bằng vector từ tiền huấn luyện, theo khuyến nghị của [@lau2016].

### 5.7 Trả lời RQ3

Tài liệu hiện có cho phép trả lời RQ3 ở mức **thận trọng**:
- **FI có làm giàu embedding.** Trên Snippets, FI giúp tăng 2,7 điểm so với embedding chỉ từ item, và JOI tăng thêm 1,2 điểm [@trans2vec].
- **Bằng chứng còn mỏng.** Nó đến từ *một* công trình, trên dữ liệu *tiếng Anh*, với transaction *ngắn*.
- **Về loại FI nên khai phá**, tài liệu khai phá dữ liệu gợi ý hai hướng: dùng FI đóng để bỏ phần dư thừa [@zhang2025], và chọn δ cùng thuật toán theo hồ sơ dữ liệu [@trasierras2024]. Cả hai chưa từng được kiểm chứng trên một tác vụ hạ nguồn.
- **Muốn áp dụng cho tin tức tiếng Việt, cần ít nhất:**
  1. một chiến lược chặn bùng nổ FI (H2);
  2. một cơ chế suy luận vector cho truy vấn (H5);
  3. một giao thức đánh giá có đối chứng hiện đại (H3, H6).

Kiểm chứng các điều kiện này trên tiếng Việt chính là đóng góp mà đề tài hướng tới. Mục 9.5 trình bày kết quả thực nghiệm, và Mục 10.1 tổng hợp câu trả lời cuối cùng cho RQ3.
