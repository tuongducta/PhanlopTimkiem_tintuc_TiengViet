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
- Chuẩn hóa Unicode và vị trí dấu thanh; loại thẻ HTML và ký tự ngoài bảng chữ cái [@nguyen2009].
- Tách từ bằng VnCoreNLP [@vncorenlp2018]. Đây là cấu hình có thể đổi: phương án đối chứng giữ nguyên âm tiết, để kiểm chứng giả thuyết "FI ≈ từ ghép" (Mục 5.5).
- Bỏ từ dừng bằng một danh sách công bố kèm theo nghiên cứu, để tăng khả năng tái lập.

**M2 – Lọc item** (giải H2). Mỗi bài báo chỉ giữ **k item đại diện**. Ba phương án sẽ được so sánh:
- (a) top-k theo TF-IDF, với IDF tính trên tập huấn luyện;
- (b) top-k theo TextRank [@mihalcea2004; @huynh2020];
- (c) chỉ giữ thực thể có tên và danh từ riêng [@wang2022].

Giá trị khởi điểm k = 50 dựa trên điểm bão hòa quan sát được trong [@huynh2020].

**M3 – Khai phá FI.**
- Dùng **FP-Growth** [@han2000] cho tập phổ biến thường, hoặc thuật toán khai phá **tập phổ biến đóng** [@zaki2002], trên tập huấn luyện.
- Giới hạn độ dài itemset ≤ 3.
- Chọn δ bằng phương pháp elbow [@trans2vec; @rousseau2015].
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

**M7 – Tìm kiếm ngữ nghĩa.**
- Lưu vector của toàn bộ kho bài vào một chỉ mục vector và tìm top-k theo cosine.
- Có thể lọc trước theo chuyên mục dự đoán của truy vấn để giảm nhiễu và chi phí.
- Hỗ trợ hai kiểu truy vấn: **từ khóa** ("lãi suất căn hộ") và **bài tương tự** (truyền vào một bài báo).

### 9.3 Thiết kế thực nghiệm

**Bảng 9.1.** Ma trận thực nghiệm đề xuất

| Hạng mục | Nội dung |
|---|---|
| Dữ liệu | VNTC Level 1 (10 lớp) và Level 2 (27 lớp) [@hoang2007]; một corpus khó ≥ 25 chuyên mục tự thu thập theo cách của [@duong2019] |
| Baseline thưa | BoW, TF-IDF → SVM / LR [@duong2019]; TF-IDF + OCFS / χ² ở 128 chiều [@hoang2007; @vinh2021] |
| Baseline FI | FI-BIN, FI-SUP [@trans2vec] |
| Baseline dày | TRANS-IT (≡ Doc2Vec PV-DBOW), PV-DM [@le2014]; MLP-128 có giám sát [@vinh2021]; Top2Vec [@angelov2020] |
| Trần trên | PhoBERT fine-tune và PhoBERT/SBERT làm bộ mã hóa cho tìm kiếm [@phobert2020; @reimers2019] |
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
| A3 | FI thường, FI đóng, chỉ thực thể | FI đóng giữ hiệu năng với số FI nhỏ hơn nhiều |
| A4 | d ∈ {64, 128, 256} | Tồn tại d tối ưu ở mức trung bình, không tăng đơn điệu [@trans2vec] |
| A5 | JOI so với JOI + TF-IDF so với JOI khởi tạo bằng vector tiền huấn luyện | Bổ sung tần suất hoặc tri thức ngoài cải thiện thêm, nhất là trên corpus khó |
| A6 | Truy vấn có FI và không có FI | Truy vấn chứa FI cho nDCG cao hơn; khoảng chênh đo được giá trị của FI cho tìm kiếm |

### 9.4 Kết quả kỳ vọng và tiêu chí thành công

Dựa trên bằng chứng ở Chương 8, kỳ vọng hợp lý là Trans2Vec-JOI:
- **(i)** vượt TF-IDF và Doc2Vec trên corpus khó;
- **(ii)** tiến gần mức của MLP-128 có giám sát [@vinh2021] mà không dùng nhãn khi học biểu diễn;
- **(iii)** thấp hơn PhoBERT, nhưng với chi phí nhỏ hơn nhiều và không cần GPU;
- **(iv)** cho kết quả tìm kiếm tốt hơn TF-IDF cosine.

Đề tài được coi là thành công nếu (i), (iv) và giả thuyết A1 được xác nhận. Ngay cả khi kết quả âm tính, một so sánh có kiểm soát theo giao thức Mục 7.3 vẫn có giá trị, vì hiện chưa có bảng so sánh như vậy cho tin tức tiếng Việt (Mục 8.5).

### 9.5 Kết quả thực nghiệm sơ bộ trên VNTC-10

Thiết kế ở các Mục 9.1–9.3 đã được hiện thực và chạy trên toàn bộ VNTC-10 [@hoang2007]: 33.759 bài huấn luyện, 50.373 bài kiểm tra, 10 chủ đề. Mã nguồn, dữ liệu dẫn xuất và báo cáo chi tiết nằm trong thư mục `experiments/` (tệp `RESULTS.md`).

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
| MLP-128 có giám sát [@vinh2021] | 0,902 | — |
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
- **(i) Không đạt.** Trans2Vec-JOI không vượt TF-IDF (0,849 so với 0,907 với LR) và chỉ ngang Doc2Vec (TRANS-IT 0,847). Trên VNTC, đóng góp của FI cho phân loại nằm trong khoảng −0,3 đến +0,9 điểm (Bảng 9.5), thấp hơn nhiều mức +2,7 trên Snippets [@trans2vec]. Kết quả này phù hợp với hạn chế H1: biểu diễn dạng tập hợp bỏ mất tần suất từ, mà tần suất mang thông tin chuyên mục trong văn bản dài.
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
- TRANS-IT đạt 75,29%, khớp với 75,23% của [@trans2vec], tức cách cài đặt là chính xác.
- Trans2Vec-JOI chỉ đạt 75,99% so với 79,05% công bố. Phần đóng góp của FI là +0,7 điểm, không phải +3,8.

Như vậy, việc FI đóng góp ít không phải đặc thù của tiếng Việt: nó cũng xảy ra trên chính dữ liệu của bài gốc.

Mã nguồn công bố còn khác bài báo ở bốn điểm:
1. vector được học **transductive**: Doc2Vec học trên cả tài liệu kiểm tra, không dùng nhãn;
2. 50 epoch, không được nêu trong bài;
3. có tùy chọn tinh chỉnh C;
4. một lỗi `if/else` khiến tập huấn luyện Snippets thực tế là 9.872 thay vì 10.060 bài.

**Bảng 9.6.** Tái hiện trên Snippets (accuracy %, 3 seed)

| Phương pháp | Bài báo [@trans2vec] | Tái hiện, transductive như mã gốc | Inductive như Mục 9.5 |
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

Thực nghiệm cũng tái hiện được kiểu lỗi đã nghi ở [@huong2022] (Mục 8.3): khi huấn luyện quá ít (5 epoch trên mẫu 3.000 bài), vector gần như không rời giá trị khởi tạo và độ chính xác rơi về mức đoán ngẫu nhiên. Ngoài ra, cách hiện thực phương pháp elbow ảnh hưởng mạnh tới kết quả. Chuẩn hóa trên thang log-log chọn δ = 2,16%, khiến 82% bài kiểm tra không còn FI nào dài ≥ 2. Chuẩn hóa tuyến tính, đúng như cách đọc hình trong [@trans2vec], chọn δ = 0,535%.

**Giá trị diễn giải.** Dù không cải thiện độ chính xác phân loại, FI cho phần giải thích chuyên mục dễ đọc (mô-đun M6). Ví dụ:
- Kinh doanh: {doanh_nghiệp, thị_trường}, {tỷ, usd}.
- Thế giới: {bush, tổng_thống}, {baghdad, iraq}.
- Thể thao: {chung_kết, đội}.
- Vi tính: {e, mail}. pyvi tách sai "email" thành hai token, và FI đã tự ghép lại.

*Hạn chế của thực nghiệm:* mới dùng một corpus (VNTC-10, giai đoạn 2003–2006, 10 chủ đề khá tách bạch); kết quả "suy luận lại" mới chạy một seed; "liên quan" trong tìm kiếm là nhãn thay thế; chưa có PhoBERT, Top2Vec, Sqn2Vec.
