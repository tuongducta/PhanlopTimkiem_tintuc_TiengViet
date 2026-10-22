## 9. Đề xuất hệ thống tìm kiếm và phân loại chuyên mục dựa trên Trans2Vec

Chương này chuyển các kết luận của khảo sát thành một kiến trúc cụ thể và một thiết kế thực nghiệm kiểm chứng được. Mỗi quyết định thiết kế được gắn với hạn chế (H1–H8, Bảng 5.4) hoặc bằng chứng mà nó dựa vào.

**Vì sao không chọn mô hình tiền huấn luyện làm lõi.** Minaee và cộng sự đưa ra công thức năm bước để chọn mô hình phân loại văn bản: chọn mô hình tiền huấn luyện, thích nghi miền, thiết kế lớp đầu ra, tinh chỉnh, rồi nén mô hình vì mô hình tiền huấn luyện tốn kém khi phục vụ [@minaee2021]. Với tiếng Việt, bước 1 và 4 dẫn tới PhoBERT tinh chỉnh, một trần trên cần GPU. Bước 5 cho thấy chi phí phục vụ là vấn đề thật ngay cả với các nhóm có nhiều tài nguyên. Hệ thống đề xuất vì vậy đi theo hướng khác: một biểu diễn rẻ, chạy trên CPU, diễn giải được, dùng chung cho cả hai tác vụ. PhoBERT và embedding đóng băng (nhánh F2) được giữ làm trần trên trong thiết kế thực nghiệm.

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

Kiến trúc trên đã được hiện thực thành một hệ thống chạy được, gồm hai hệ lưu trữ với vai trò tách biệt (Hình 9.2):
- **MariaDB 11.8** là nguồn dữ liệu gốc: bài báo, transaction (4,15 triệu dòng), tập phổ biến, các lần huấn luyện, vector `VECTOR(128)`, dự đoán, kết quả đánh giá và nhật ký truy vấn.
- **Manticore Search** là chỉ mục phái sinh, dựng lại được hoàn toàn từ MariaDB trong khoảng 100 giây. Manticore phục vụ đồng thời BM25 [@robertson2009] và tìm vector bằng HNSW [@malkov2020] trên cùng một bảng, kèm lọc theo chuyên mục.

Mô-đun M7 vì vậy có ba chế độ: từ khóa (BM25), vector (Trans2Vec-JOI) và kết hợp, gộp hai danh sách bằng Reciprocal Rank Fusion [@cormack2009]. Thiết kế lưu trữ, chỉ mục và các phép đo hiệu năng được trình bày trong báo cáo riêng của môn Hệ cơ sở dữ liệu nâng cao.

![Hệ thống đã hiện thực: MariaDB là nguồn gốc, Manticore là chỉ mục phái sinh, Streamlit là giao diện.](figures/fig_arch.png)

*Hình 9.2. Hệ thống đã hiện thực.*

### 9.2 Các mô-đun

Mục này mô tả thiết kế. Bản hiện thực (Mục 9.5) khác thiết kế ở ba điểm: tách từ bằng pyvi thay vì VnCoreNLP; khai phá FI bằng mã tự viết (đếm cặp bằng nhân ma trận thưa, bộ ba kiểu Apriori), đủ nhanh vì FI chỉ dài tới 3; và mô-đun M2 mới chạy phương án (a).

**M1 – Tiền xử lý** (Mục 2.4, Bảng 2.1).
- Chuẩn hóa Unicode và vị trí dấu thanh; loại thẻ HTML và ký tự ngoài bảng chữ cái [@nguyen2009].
- Tách từ bằng VnCoreNLP [@vncorenlp2018]. Đây là cấu hình có thể đổi: phương án đối chứng giữ nguyên âm tiết, để kiểm chứng giả thuyết "FI ≈ từ ghép" (Mục 5.5).
- Bỏ từ dừng bằng một danh sách công bố kèm theo nghiên cứu, để tăng khả năng tái lập.

**M2 – Lọc item** (giải H2). Mỗi bài báo chỉ giữ **k item đại diện**. Ba phương án sẽ được so sánh:
- (a) top-k theo TF-IDF, với IDF tính trên tập huấn luyện;
- (b) top-k theo TextRank [@mihalcea2004; @huynh2020];
- (c) chỉ giữ thực thể có tên và danh từ riêng [@wang2022].

Giá trị khởi điểm k = 50 dựa trên điểm bão hòa quan sát được trong [@huynh2020].

**M3 – Khai phá FI.**
- Dùng **FP-Growth** [@han2000] hoặc **LCM**, hai họ thuật toán thường nhanh nhất theo [@trasierras2024], trên tập huấn luyện. Mã gốc của [@trans2vec] dùng một công cụ chỉ chạy trên Windows, nên không dùng lại được.
- Giới hạn độ dài itemset ≤ 3.
- Chọn δ bằng phương pháp elbow [@trans2vec; @rousseau2015], và **báo δ kèm hồ sơ dữ liệu**, vì hồ sơ đổi theo δ [@trasierras2024].
- Không cần bước lọc FI đóng hay lọc theo khoảng tin cậy: trên tin tức, gần như mọi FI đã đóng, và lọc theo khoảng tin cậy không tốt hơn chọn ngẫu nhiên cùng số lượng (Mục 9.5).
- Kết quả gồm danh sách FI kèm độ hỗ trợ, đánh chỉ mục để khớp nhanh với bài mới.

**M4 – Học Trans2Vec-JOI** [@trans2vec].
- Huấn luyện PV-DBOW trên tập mẫu (item ∪ FI) của mỗi bài, d = 128, có negative sampling.
- Siêu tham số khởi điểm theo khuyến nghị của [@lau2016].
- Biến thể mở rộng (giải H1 và H3):
  - (i) nối thêm vector TF-IDF đã giảm chiều;
  - (ii) khởi tạo vector item từ embedding tiền huấn luyện [@lau2016];
  - (iii) thay FI bằng mẫu tuần tự theo Sqn2Vec [@sqn2vec].

**M5 – Suy luận vector** (giải H5).
- Với bài mới hoặc truy vấn $q$, cố định mọi vector item và FI rồi tối ưu riêng $f(q)$ vài vòng gradient [@le2014].
- Nếu $q$ không chứa FI nào (thường gặp với truy vấn 2–3 từ), suy luận chỉ trên phần item.
- Nếu $q$ chứa item ngoài từ vựng, có thể mở rộng truy vấn bằng các từ gần nghĩa trong không gian vector item.

**M6 – Phân loại chuyên mục.**
- LR để triển khai; SVM tuyến tính để so sánh công bằng giữa các biểu diễn (Mục 6.3).
- Xử lý mất cân bằng bằng trọng số lớp [@vinh2021].
- **Giải thích:** với mỗi chuyên mục $c$, lấy các FI có tích vô hướng lớn nhất với tâm (centroid) vector bài báo của $c$ làm "từ khóa chuyên mục". Cách này dùng được vì PV-DBOW học vector bài báo và vector mẫu qua chính tích vô hướng đó. Với mỗi bài, liệt kê các FI của bài thuộc nhóm đó.

**M7 – Tìm kiếm.**
- Ba chế độ: **từ khóa** (BM25 trên văn bản đã tách từ), **vector** (suy luận vector Trans2Vec-JOI cho truy vấn, rồi tìm top-k trên chỉ mục HNSW), và **kết hợp** (gộp hai danh sách bằng RRF, $k=60$, lấy 100 bài mỗi nhánh).
- **Xử lý dấu thanh:** chỉ mục giữ hai dạng văn bản, giữ dấu và đã gộp dấu. Truy vấn có dấu dùng dạng giữ dấu. Truy vấn gõ không dấu dùng dạng gộp dấu cho BM25; ở chế độ kết hợp, nhánh vector bị bỏ vì vector suy luận từ chữ không dấu kéo kết quả lạc đề.
- **Khử trùng** theo mã băm nội dung trước khi hiển thị, vì VNTC có bài trùng (Mục 7.1).
- Có thể lọc theo chuyên mục. Hỗ trợ hai kiểu truy vấn: **từ khóa** ("lãi suất căn hộ") và **bài tương tự** (truyền vào một bài báo).

### 9.3 Thiết kế thực nghiệm

**Bảng 9.1.** Ma trận thực nghiệm đề xuất

| Hạng mục | Nội dung |
|---|---|
| Dữ liệu | VNTC Level 1 (10 lớp) và Level 2 (27 lớp) [@hoang2007]; một corpus khó ≥ 25 chuyên mục tự thu thập theo cách của [@duong2019] |
| Baseline thưa | BoW, TF-IDF → SVM / LR [@duong2019]; TF-IDF + OCFS / χ² ở 128 chiều [@hoang2007; @vinh2021] |
| Baseline FI | FI-BIN, FI-SUP [@trans2vec] |
| Baseline dày | TRANS-IT (≡ Doc2Vec PV-DBOW), PV-DM [@le2014]; MLP-128 có giám sát [@vinh2021]; Top2Vec [@angelov2020] |
| Trần trên | PhoBERT fine-tune và PhoBERT/SBERT làm bộ mã hóa cho tìm kiếm [@phobert2020; @reimers2019]; embedding câu đóng băng + LR theo mô thức của [@liu2024] |
| Tìm kiếm từ khóa | BM25 [@robertson2009]; kết hợp BM25 với vector bằng RRF [@cormack2009] |
| Phương pháp chính | TRANS-FI, Trans2Vec-IND, Trans2Vec-JOI và các biến thể ở M4 |
| Độ đo phân loại | Macro-F1 (chính), accuracy; trung bình ± độ lệch chuẩn qua 5 hạt giống |
| Độ đo tìm kiếm | Precision@10, MAP, nDCG@10 [@jarvelin2002]; tài liệu liên quan = cùng chuyên mục (nhãn thay thế) |
| Độ đo phân cụm / diễn giải | NMI, ARI giữa cụm K-means trên f(T) và nhãn chuyên mục; đánh giá định tính FI chuyên mục |
| Chi phí | Số FI theo δ và k; thời gian FP-Growth, huấn luyện PV-DBOW, suy luận một truy vấn; bộ nhớ chỉ mục |

**Bảng 9.2.** Các thực nghiệm loại trừ (ablation) và giả thuyết

| Mã | Biến thay đổi | Giả thuyết |
|---|---|---|
| A1 | Từ (tách từ) so với âm tiết | Với âm tiết, FI bù đắp phần lớn việc thiếu tách từ: khoảng cách Macro-F1 giữa hai cấu hình **nhỏ hơn** ở Trans2Vec so với ở TF-IDF |
| A2 | k ∈ {20, 50, 100, toàn bộ} | Hiệu năng bão hòa quanh k ≈ 50, còn chi phí khai phá FI tăng vọt khi k lớn |
| A3 | FI thường, FI đóng, FI ổn định (CICFI), chỉ thực thể | FI đóng hoặc FI ổn định giữ hiệu năng với số FI nhỏ hơn [@zhang2025] |
| A4 | d ∈ {64, 128, 256} | Tồn tại d tối ưu ở mức trung bình, không tăng đơn điệu [@trans2vec] |
| A5 | JOI so với JOI + TF-IDF so với JOI khởi tạo bằng vector tiền huấn luyện | Bổ sung tần suất hoặc tri thức ngoài cải thiện thêm, nhất là trên corpus khó |
| A6 | Truy vấn có FI và không có FI | Truy vấn chứa FI cho nDCG cao hơn; khoảng chênh đo được giá trị của FI cho tìm kiếm |

### 9.4 Kết quả kỳ vọng và tiêu chí thành công

Dựa trên bằng chứng ở Chương 8, kỳ vọng hợp lý là Trans2Vec-JOI:
- **(i)** vượt TF-IDF và Doc2Vec trên corpus khó;
- **(ii)** tiến gần mức của MLP-128 có giám sát [@vinh2021] mà không dùng nhãn khi học biểu diễn;
- **(iii)** thấp hơn PhoBERT, nhưng với chi phí nhỏ hơn nhiều và không cần GPU;
- **(iv)** cho kết quả tìm kiếm tốt hơn TF-IDF cosine.

Đề tài được coi là thành công nếu (i), (iv) và giả thuyết A1 được xác nhận. Ngay cả khi kết quả âm tính, một so sánh có kiểm soát theo giao thức Mục 7.3 vẫn có giá trị, vì hiện chưa có bảng so sánh như vậy cho tin tức tiếng Việt (Mục 8.6).

### 9.5 Kết quả thực nghiệm trên VNTC-10

Thiết kế ở các Mục 9.1–9.3 đã được hiện thực và chạy trên toàn bộ VNTC-10 [@hoang2007]: 33.759 bài huấn luyện, 50.373 bài kiểm tra, 10 chủ đề. Mã nguồn nằm trong `src/experiments/` và `src/system/`; báo cáo chi tiết nằm trong `contexte/results/` (tệp `RESULTS.md` và `RESULTS_DB.md`).

**Cấu hình chính:**
- Tách từ bằng pyvi; từ dừng xác định theo dữ liệu (token xuất hiện trong hơn 30% bài huấn luyện).
- Giữ k = 50 item có tf·idf cao nhất mỗi bài.
- Khai phá itemset độ dài ≤ 3 với δ = 0,535% (chọn bằng elbow).
- PV-DBOW (gensim), d = 128, 20 epoch; vector của cả tập huấn luyện lẫn tập kiểm tra đều sinh bằng suy luận.
- Phân loại bằng SVM tuyến tính và hồi quy logistic với C = 1, trên vector chuẩn hóa L2.

Bài báo trung bình dài 488 âm tiết, xác nhận hạn chế H2: phải lọc item trước khi khai phá FI. Với k = 50 thu được 3.586 FI; mỗi bài chứa trung bình 38 FI, trong đó 12 FI dài ≥ 2.

#### Phân loại chuyên mục

**Bảng 9.3.** Phân loại chuyên mục trên tập kiểm tra VNTC-10 (Macro-F1)

| Biểu diễn | SVM C = 1 | LR C = 1 |
|---|---|---|
| TF-IDF toàn văn | **0,903** | **0,907** |
| MLP-128 có giám sát [@vinh2021] | 0,902 | — |
| TF-IDF trên 50 item mỗi bài | 0,889 | — |
| LDA-100 | 0,827 | — |
| FI-BIN | 0,824 | — |
| TRANS-IT (≡ Doc2Vec PV-DBOW) | 0,841 | 0,847 |
| TRANS-FI | 0,820 | 0,826 |
| **Trans2Vec-JOI** | **0,842** | **0,849** |
| Trans2Vec-JOI, vector huấn luyện lấy từ mô hình (3 seed) | 0,766 | 0,814 |

![Macro-F1 của các biểu diễn (SVM C = 1).](figures/fig_macro_f1.png)

*Hình 9.3. Macro-F1 của các biểu diễn (SVM C = 1).*

Trên hệ thống, đề tài huấn luyện thêm một mốc là **mã gốc của tác giả** và một mô hình cải tiến (Bảng 9.4).

**Bảng 9.4.** Sáu mô hình Trans2Vec trên hệ thống (50.373 bài kiểm tra; LR C = 1 trừ dòng đầu)

| Mô hình | Macro-F1 | Accuracy | nDCG@10 tìm kiếm |
|---|---|---|---|
| Trans2Vec gốc: mã tác giả, transductive, LinearSVC | 0,823 | 0,852 | 0,762 |
| TRANS-IT | 0,847 | 0,874 | 0,804 |
| TRANS-FI | 0,826 | 0,854 | 0,776 |
| Trans2Vec-IND (trung bình IT và FI) | 0,842 | 0,870 | 0,793 |
| Trans2Vec-JOI | 0,849 | 0,875 | **0,816** |
| **Trans2Vec-CAT** (nối IT ‖ FI ‖ JOI) | **0,857** | **0,882** | 0,807 |

- **Mốc "Trans2Vec gốc"** chạy đúng quy trình trong mã công bố: Doc2Vec học transductive trên toàn bộ bài, 50 epoch, vector lấy từ mô hình, LinearSVC mặc định. Chỉ hai điểm phải đổi: dùng cùng bộ 3.586 FI, vì công cụ khai phá FI của tác giả chỉ chạy trên Windows; và đổi tên tham số sang gensim 4. Mốc đạt 0,823, cao hơn bản inductive lấy vector từ mô hình ở Bảng 9.3 (0,766), vì khi học transductive, vector huấn luyện và kiểm tra cùng phân phối.
- **Mô hình CAT** được chọn giữa hai ứng viên (nối vector và stacking) bằng kiểm định chéo 3 phần **trên tập huấn luyện** (0,873 so với 0,866), không nhìn tập kiểm tra. CAT hơn JOI 0,008 Macro-F1. Mức tăng nhỏ nhưng nhất quán với nhận định rằng mỗi biến thể nhìn bài báo từ một góc khác nhau.
- Ở tìm kiếm thì CAT kém JOI (0,807 so với 0,816), nên tìm kiếm vẫn dùng JOI. **Mô hình tốt nhất cho hai tác vụ không trùng nhau.** Khoảng cách với TF-IDF (0,907) vẫn còn khoảng 0,05.

#### Tìm kiếm

**Bảng 9.5.** Tìm kiếm theo cosine (nDCG@10): 1.000 truy vấn, kho 33.759 bài, "liên quan" = cùng chủ đề

| Biểu diễn | Truy vấn là bài báo | Truy vấn 3 từ khóa |
|---|---|---|
| TF-IDF toàn văn | 0,740 | 0,634 |
| LDA-100 | 0,765 | — |
| TRANS-IT | 0,800 | — |
| **Trans2Vec-JOI** | **0,809** | **0,692** |

Trên hệ thống, cùng giao thức được chạy lại với BM25 và tìm kiếm kết hợp (Bảng 9.6). JOI trên hệ thống là một lần huấn luyện khác, nên đạt 0,816 thay vì 0,809.

**Bảng 9.6.** Tìm kiếm trên Manticore (nDCG@10)

| Phương pháp | Truy vấn là bài báo | 3 từ khóa | 3 từ khóa, có FI (n = 56) | 3 từ khóa, không FI (n = 944) |
|---|---|---|---|---|
| BM25 ($k_1$ = 1,2; b = 0,75) | 0,749 | 0,653 | 0,769 | 0,646 |
| Trans2Vec-JOI (HNSW) | 0,816 | 0,690 | 0,863 | 0,679 |
| **Kết hợp RRF (k = 60)** | **0,819** | **0,704** | **0,870** | **0,694** |

Ba nhận xét cho RQ6:
1. **BM25 không đổi kết luận của Bảng 9.5.** BM25 ngang TF-IDF cosine (0,749 so với 0,740 với truy vấn là bài báo), và Trans2Vec-JOI vẫn hơn biểu diễn thưa khoảng 0,07.
2. **Tìm kiếm kết hợp chỉ có ích rõ với truy vấn ngắn:** +0,014 so với vector và +0,051 so với BM25. Với truy vấn là bài báo, nó ngang vector (+0,003). Đổi lại, MAP@100 của nó thấp hơn vector (0,525 so với 0,596 với truy vấn ngắn), nên nó hợp cho trang top-10 hơn là cho thu hồi sâu.
3. **Truy vấn ngắn có chứa FI dễ hơn hẳn**, và ở nhóm này vector hơn BM25 khoảng 0,09. Quan sát này ủng hộ vai trò của FI trong tìm kiếm, nhưng n = 56 nên mới chỉ là gợi ý.

**Về đánh giá chỉ mục vector.** Khi đổi chỉ mục HNSW (tham số M và ef khác nhau), recall@10 so với tìm vét cạn thay đổi từ 0,86 đến 1,00, trong khi nDCG@10 theo nhãn thay thế "cùng chủ đề" chỉ dao động trong khoảng 0,811–0,818. Nhãn thay thế không đủ nhạy để so sánh chỉ mục; phải dùng recall so với vét cạn. Đây là thêm một lý do cần tập truy vấn có nhãn liên quan do người gán (Mục 8.4, T8). Độ trễ của chỉ mục dưới 1 ms; nút thắt là bước suy luận vector cho truy vấn (3–5 ms).

**Về dấu thanh** (Mục 2.2). Truy vấn gõ tự do không dấu, đi qua toàn bộ quy trình tìm kiếm, đạt nDCG@10 0,399 trước khi có nhánh gộp dấu và 0,534 sau. Nếu chế độ kết hợp vẫn giữ nhánh vector với truy vấn không dấu, kết quả chỉ còn 0,473, nên nhánh vector bị bỏ trong trường hợp này.

#### Đối chiếu với kỳ vọng ở Mục 9.4

- **(i) Không đạt.** Trans2Vec-JOI không vượt TF-IDF (0,849 so với 0,907 với LR) và chỉ ngang Doc2Vec (TRANS-IT 0,847). Mô hình cải tiến CAT thu hẹp khoảng cách được 0,008. Trên VNTC, đóng góp của FI cho phân loại (JOI − IT) nằm trong khoảng −0,3 đến +0,9 điểm (Bảng 9.7), thấp hơn nhiều mức +3,8 trên Snippets [@trans2vec]. Kết quả này phù hợp với hạn chế H1: biểu diễn dạng tập hợp bỏ mất tần suất từ, mà tần suất mang thông tin chuyên mục trong văn bản dài.
- **(ii) Không đạt.** Trans2Vec còn cách MLP-128 có giám sát khoảng 5 điểm. Đây là cái giá của việc học biểu diễn không dùng nhãn.
- **(iii) Chưa đo PhoBERT** (không có GPU). Riêng về chi phí, Trans2Vec rất rẻ: khai phá FI 3 giây, huấn luyện 16 giây, suy luận 50.373 bài kiểm tra 42 giây, toàn bộ trên CPU. Nếu suy luận lại cả vector huấn luyện, phần huấn luyện cộng suy luận mất khoảng 98 giây.
- **(iv) Đạt.** Ở bài toán tìm kiếm, Trans2Vec-JOI tốt nhất trong các biểu diễn không giám sát, hơn TF-IDF và BM25 khoảng 0,07 nDCG@10 với truy vấn là bài báo và khoảng 0,04–0,06 với truy vấn 3 từ khóa. Phần lớn lợi thế này đến từ việc dùng vector dày, vì 94% truy vấn ngắn không chứa FI nào. Kết hợp với BM25 nhích thêm một chút ở top-10.
- **Giả thuyết A1 không được xác nhận.** Bỏ tách từ làm TF-IDF giảm 1,2 điểm (SVM: 0,891 so với 0,903), còn TRANS-IT và Trans2Vec-JOI giảm 3,1 và 2,5 điểm (LR: 0,816 so với 0,847; 0,824 so với 0,849). FI không bù được việc thiếu tách từ. Chỉ 13,5% cặp âm tiết phổ biến trùng với một từ ghép của pyvi.

#### Vai trò của tập phổ biến

**Bảng 9.7.** Đóng góp của FI: Macro-F1(JOI) − Macro-F1(TRANS-IT)

| Cấu hình | FI / bài | Vector huấn luyện lấy từ mô hình | Vector huấn luyện suy luận lại |
|---|---|---|---|
| Từ, k = 50 | 38 | −0,5 | +0,1 |
| Từ, k = 100 | 282 | +3,7 | −0,3 |
| Âm tiết, k = 50 | 96 | +4,2 | +0,9 |

**Kiểm chứng cài đặt trên Snippets.** Để chắc rằng kết quả trên VNTC không do lỗi cài đặt, Trans2Vec được chạy lại trên Snippets bằng dữ liệu và tập phổ biến do chính tác giả công bố cùng mã nguồn (github.com/nphdang/Trans2Vec), với cấu hình của mã gốc (50 epoch, SVM C = 1). Kết quả (Bảng 9.8):
- TRANS-IT đạt 75,29%, khớp với 75,23% của [@trans2vec], tức cách cài đặt là chính xác.
- Trans2Vec-JOI chỉ đạt 75,99% so với 79,05% công bố. Phần đóng góp của FI là +0,7 điểm, không phải +3,8.

Như vậy, việc FI đóng góp ít không phải đặc thù của tiếng Việt: nó cũng xảy ra trên chính dữ liệu của bài gốc khi chạy như mã công bố.

Mã nguồn công bố còn khác bài báo ở bốn điểm:
1. vector được học **transductive**: Doc2Vec học trên cả tài liệu kiểm tra, không dùng nhãn;
2. 50 epoch, không được nêu trong bài;
3. có tùy chọn tinh chỉnh C;
4. một lỗi `if/else` khiến tập huấn luyện Snippets thực tế là 9.872 thay vì 10.060 bài.

**Bảng 9.8.** Tái hiện trên Snippets (accuracy %, 3 seed)

| Phương pháp | Bài báo [@trans2vec] | Tái hiện, transductive như mã gốc | Inductive như Mục 9.5 |
|---|---|---|---|
| TRANS-IT | 75,23 | 75,29 | 73,44 |
| TRANS-FI | 77,88 | 75,23 | 74,84 |
| Trans2Vec-JOI | 79,05 | 75,99 | 76,51 |
| JOI − IT | +3,8 | +0,7 | +3,1 |

**Phát hiện về phương pháp đánh giá.** Cột giữa của Bảng 9.7 cho thấy một cái bẫy đánh giá cần đưa vào giao thức (Mục 7.3):
- Nếu vector huấn luyện lấy trực tiếp từ mô hình PV-DBOW còn vector kiểm tra được *suy luận*, hai tập vector có phân phối khác nhau.
- Hệ quả thứ nhất: Trans2Vec bị đánh giá thấp 7–8 điểm (0,766 so với 0,842).
- Hệ quả thứ hai: chọn C bằng cross-validation trên tập huấn luyện bị sai lệch, luôn chọn C lớn mà điểm kiểm tra lại giảm.
- Hệ quả thứ ba, nghiêm trọng nhất: xuất hiện những "cải thiện nhờ FI" giả, tới +3,7 và +4,2 điểm, rồi biến mất khi vector huấn luyện được suy luận bằng cùng quy trình như vector kiểm tra.

Thực nghiệm cũng tái hiện được kiểu lỗi đã nghi ở [@huong2022] (Mục 8.3): khi huấn luyện quá ít (5 epoch trên mẫu 3.000 bài), vector gần như không rời giá trị khởi tạo và độ chính xác rơi về mức đoán ngẫu nhiên. Ngoài ra, cách hiện thực phương pháp elbow ảnh hưởng mạnh tới kết quả. Chuẩn hóa trên thang log-log chọn δ = 2,16%, khiến 82% bài kiểm tra không còn FI nào dài ≥ 2. Chuẩn hóa tuyến tính, đúng như cách đọc hình trong [@trans2vec], chọn δ = 0,535%.

#### Loại tập phổ biến và hồ sơ dữ liệu

Hai thực nghiệm bổ sung kiểm chứng gợi ý của tài liệu khai phá dữ liệu (Mục 3.2) về *loại* FI nên dùng.

**E8: hồ sơ dữ liệu** (Bảng 7.4). Ba kết quả:
1. **Hồ sơ dữ liệu không giải thích được vì sao FI giúp Snippets mà không giúp VNTC.** Hai corpus cùng thưa, độ giống nhau giữa các transaction gần nhau, và tỉ lệ bài không có FI dài ≥ 2 bằng nhau (14%). Khác biệt rõ nhất là độ dài transaction, nên tỉ trọng FI trong token của JOI khác nhau: khoảng 30% với Snippets, khoảng 20% với VNTC k = 50. Nhưng trong chính VNTC, khi tỉ trọng này tăng lên khoảng 54% (âm tiết) và 72% (k = 100), đóng góp của FI vẫn chỉ +0,9 và −0,3 (Bảng 9.7). Lượng FI vì thế cũng không phải lời giải.
2. **FI không đóng rất hiếm trong văn bản.** Tỉ lệ cao nhất là 3,4% (Snippets, δ = 0,2%). Trên VNTC từ k = 50, tỉ lệ này là 0,17% ở δ = 0,2% và bằng 0 ở mọi δ ≥ 0,535%. Các FI không đóng hầu hết là cụm cố định: {games, đội} luôn đi cùng "sea", {a, milan} luôn đi cùng "serie", {wiki, …} luôn đi cùng "wikipedia". Một tập và tập cha của nó chỉ cùng độ hỗ trợ khi các item *luôn* đi cùng nhau, điều mà văn bản tự nhiên hiếm khi có.
3. **Bùng nổ FI đo được theo δ:** VNTC từ k = 100 ở δ = 0,2% sinh 284.384 FI, trung bình 941 FI dài ≥ 2 mỗi bài.

*Đính chính:* ở cấu hình chính mọi FI đều đã đóng. Thực nghiệm loại trừ A3 trước đây (chỉ dùng FI đóng: 0,770 so với 0,766) vì vậy so sánh hai tập FI giống hệt nhau; chênh lệch là dao động ngẫu nhiên, không phải tác dụng của FI đóng.

**E9: loại FI.** Hạ δ xuống 0,2% để có nhiều FI hơn và có FI sát ngưỡng, rồi so các cách chọn FI cùng số lượng (Bảng 9.9). Biến thể FI đóng bị bỏ vì kết quả 2 ở trên. Giao thức như cấu hình chính, 3 seed, LR C = 1.

**Bảng 9.9.** Loại FI trong Trans2Vec-JOI (VNTC-10, trung bình ± độ lệch chuẩn qua 3 seed; Δ so với TRANS-IT cùng seed)

| Biến thể | FI dài ≥ 2 | Macro-F1 | Δ Macro-F1 | Δ nDCG@10 | Thời gian |
|---|---|---|---|---|---|
| TRANS-IT (không FI) | 0 | 0,8473 ± 0,0001 | — | — | 98 s |
| JOI, mọi FI, δ = 0,535% | 1.484 | 0,8498 ± 0,0010 | +0,0025 | +0,0018 | 98 s |
| **JOI, mọi FI, δ = 0,2%** | 17.349 | **0,8535 ± 0,0007** | **+0,0062** | +0,0074 | 194 s |
| JOI, FI ổn định toàn cục (CICFI) | 10.374 | 0,8526 ± 0,0013 | +0,0053 | +0,0054 | 147 s |
| JOI, FI ổn định theo chuyên mục (dùng nhãn) | 10.374 | 0,8534 ± 0,0002 | +0,0061 | +0,0085 | 138 s |
| JOI, FI chọn ngẫu nhiên cùng số lượng | 10.374 | 0,8533 ± 0,0006 | +0,0059 | +0,0089 | 114 s |

- **Hạ δ giúp, nhưng rất ít.** Số FI tăng 12 lần làm đóng góp của FI tăng từ +0,0025 lên +0,0062 Macro-F1. Mức tăng nhất quán qua 3 seed nên là thật, nhưng chỉ khoảng 0,6 điểm, đổi lại thời gian gấp đôi.
- **Tiêu chí chọn FI không quan trọng.** Ở cùng 10.374 FI, chọn theo độ hỗ trợ (CICFI toàn cục, tương đương nâng δ lên 0,249%), theo độ ổn định trong chuyên mục, hay chọn ngẫu nhiên đều cho kết quả ngang nhau trong vùng nhiễu. **CICFI [@zhang2025] không đem lại gì hơn chọn ngẫu nhiên.** Tín hiệu đến từ việc *có thêm* token đồng xuất hiện, không đến từ việc chọn *đúng* FI.
- **Khuyến nghị cho hệ thống:** giữ mọi FI, chọn δ theo ngân sách tính toán, không cần bước lọc FI đóng hay lọc theo khoảng tin cậy.

#### Giá trị diễn giải

Dù không cải thiện nhiều độ chính xác phân loại, FI cho phần giải thích chuyên mục dễ đọc (mô-đun M6). Ví dụ:
- Kinh doanh: {doanh_nghiệp, thị_trường}, {tỷ, usd}.
- Thế giới: {bush, tổng_thống}, {baghdad, iraq}.
- Thể thao: {chung_kết, đội}.
- Vi tính: {e, mail}. pyvi tách sai "email" thành hai token, và FI đã tự ghép lại.

*Hạn chế của thực nghiệm:*
- mới dùng một corpus (VNTC-10, giai đoạn 2003–2006, 10 chủ đề khá tách bạch);
- cột "suy luận lại" của Bảng 9.7 mới chạy một seed (+0,1 ở k = 50); E9 chạy lại cấu hình này với 3 seed và được +0,25 ± 0,11 điểm (Bảng 9.9);
- "liên quan" trong tìm kiếm là nhãn thay thế;
- chưa có PhoBERT, embedding đóng băng, Top2Vec, Sqn2Vec.
