# GĐ9 — Ma trận tổng hợp v3 (theo đường ống hệ thống)

**Đề tài:** Hệ thống tìm kiếm và phân loại chuyên mục tin tức tiếng Việt với biểu diễn Trans2Vec
**Ngày:** 22/10/2026 · **Kế hoạch:** `contexte/plans/KE_HOACH_SURVEY_v3.md` (Q1 đã duyệt: tổ chức theo đường ống; Q2–Q5 dùng mặc định)
**Quan hệ với bản cũ:** bổ sung cho `synthesis.md` (GĐ4, 07/10), không thay thế. Bảng nào của v2 còn đúng thì chỉ trỏ tới, không chép lại.

**Đầu vào:**
- Phiếu đọc [1]–[13], `supplementary.md` (S01–S27), 8 phiếu K* (GĐ8).
- Thực nghiệm của nhóm: `contexte/results/RESULTS.md` (E1–E7), `contexte/results/RESULTS_DB.md` (E-DB1, 2, 4, 5), `contexte/plans/KE_HOACH_HE_THONG_DB.md` Mục 17 (6 mô hình), `contexte/survey-notes/he_thong_db.md`.

**Quy ước:**
- Mã tài liệu giữ dạng K.. (mặc định Q2). Danh mục cuối bài vẫn đánh số tự động khi build.
- Số liệu của nhóm ghi kèm mã thực nghiệm: [E6], [E7], [E-DB4], [Mục 17]…
- Ký hiệu ma trận: ● trọng tâm · ○ baseline hoặc có đề cập · ✚ bằng chứng thực nghiệm của nhóm.
- Số liệu ghi theo độ đo của từng bài. Accuracy và Macro-F1 không trộn trong cùng một cột.

> **Giả định khi lập:**
> - Kế hoạch v3 ghi đích là `livrables/survey/synthesis_v3.md`. Sau đợt tái cấu trúc 21/10, `synthesis.md` đã chuyển sang `contexte/survey-notes/`, và `livrables/` chỉ nhận `draft/`, `figures/`. Vì vậy file này đặt ở `contexte/survey-notes/`.
> - Chưa chạy E8–E10 (Q4 chưa chốt). Chỗ nào cần E8–E10 thì ghi "chờ E8/E9/E10".

---

## 1. Dòng thời gian bổ sung (→ Chương 4)

Chỉ ghi các dòng mới. Các dòng còn lại xem `synthesis.md` §1.

| Năm | Khai phá mẫu (KDD) | Biểu diễn / NLP chung | Văn bản tiếng Việt |
|---|---|---|---|
| 2013 | | | **K21** VNLP: vnTokenizer tăng tốc, đường ống NLP mở |
| 2021 | | **K06** survey DL cho phân loại (hơn 150 mô hình) | |
| 2022 | | **K05** survey từ truyền thống đến DL | |
| 2023 | | **K30** đồ thị phân cấp + BERT (nhánh G) | |
| 2024 | **K26** hồ sơ dữ liệu và thuật toán FIM | **K29** LLMEmbed: embedding LLM đóng băng (nhánh F2) | **K27** LSTM/CNN trên VNTC |
| 2025 | **K25** closed FI, CICFI | | |
| 2026 | | | Hệ thống của nhóm: Trans2Vec + MariaDB + Manticore [Mục 17, E-DB*] |

**Đọc bảng:** sau năm 2018 vẫn **không có công trình nào nối hai dòng chảy** (khai phá mẫu và học biểu diễn) như Trans2Vec. Các bài KDD mới (K25, K26) cải thiện khâu khai phá nhưng không chạm tới tác vụ hạ nguồn. Các bài biểu diễn mới (K29, K30) đi theo hướng PLM và đồ thị. Khoảng trống của v2 vì vậy vẫn còn nguyên đến năm 2026.

---

## 2. Ma trận đường ống × tài liệu (bảng chính của v3, → Chương 1.3 và mọi chương)

Bước theo sơ đồ ở Mục 1 của kế hoạch v3: (1) tiền xử lý · (2) văn bản → transaction · (3) khai phá FI · (4) học embedding · (5a) phân loại · (5b) tìm kiếm · (6) dữ liệu và giao thức.

| Tài liệu | (1) | (2) | (3) | (4) | (5a) | (5b) | (6) | Vai trò |
|---|---|---|---|---|---|---|---|---|
| [1] Hoang 2007 | ● | | | ○ | ● | | ● VNTC | R2 |
| [2] Nguyen 2009 | ● | | | ○ | ● | | ○ | R2 |
| [3] KEBoW 2017 | ● | ● top-k | | ○ | ● | | ⚠️ rò rỉ | R2 |
| [4] VNNews-01 2019 | ○ | | | ○ | ● | | ● | R2 |
| [5] TextRank 2020 | ○ | ● từ khóa | | | ● | | | R2 |
| [6] PhoBERT HSD 2020 | ○ | | | ● | ● | | | R3 |
| [7] NN đặc trưng 2021 | ○ | | | ● | ● | | | R2 |
| [8] W2V vs TF-IDF 2022 | | | | ● | ● | | ⚠️ lỗi | R2 |
| [9] EDA + BERTology 2024 | ● | | | ● | ● | | | R3 |
| [10] PhoBERT + topic 2025 | ○ | | | ● | ● | | ○ | R2, R3 |
| **[13] Trans2Vec 2018** | ○ | **●** | **●** | **●** | **●** | | ○ | **R0** |
| **K21** VNLP 2013 | **●** | | | | | | | R2 |
| **K25** closed FI 2025 | | | **●** | | | | | R1 |
| **K26** FIM heterogeneity 2024 | | **●** hồ sơ | **●** | | | | | R1 |
| **K27** DL VNTC 2024 | ● | | | ○ SVD | **●** | | ● VNTC | R2 |
| **K29** LLMEmbed 2024 | | | | **●** | **●** | ○ | ○ | R3 |
| **K30** đồ thị + BERT 2023 | ● (POS, NER…) | | | ● | ● | | ⚠️ baseline | R3 |
| **K05** survey 2022 | ○ | | | ○ | ○ | ○ P@K, MRR | ● độ đo | R4 |
| **K06** survey 2021 | | | | ○ | ○ | ● PV trên WikiQA | ● dataset | R4 |
| **Nhóm (E1–E7, E-DB*)** | ✚ A1, E-DB5 | ✚ A2 | ✚ δ, A3 | ✚ E6 | ✚ E6, Mục 17 | ✚ E-DB1/2/4 | ✚ §3.1, bài trùng | — |

**Nhận xét:**
1. **Bước (5b) tìm kiếm gần như không có tài liệu sơ cấp.** Chỉ K06 có một con số bên ngoài (PV trên WikiQA), còn lại là thực nghiệm của nhóm. Đây là khoảng trống lớn nhất về tài liệu của RQ6. Các ứng viên trong `candidates.md` (PACLIC 2024, Do & Nguyen 2021) nên được cân nhắc ở GĐ11.
2. **Bước (2) và (3) trước đây chỉ có [13] và S05–S08.** K25 và K26 lấp đúng chỗ này, nên bước (3) giờ có cơ sở KDD hiện đại.
3. **Cột (6) có nhiều cảnh báo (⚠️) nhất.** Giao thức là điểm yếu chung, đúng như luận điểm Chương 8 của v2.

---

## 3. Ma trận taxonomy v3 × tài liệu (→ Chương 4, 5)

Mở rộng `synthesis.md` §2 theo taxonomy ở Mục 5 của kế hoạch v3. Cột "K05/K06" cho biết nhánh đó có trong taxonomy của hai survey lớn hay không.

| Nhánh | Tài liệu [1]–[13] | Tài liệu mới | Bổ sung S.. | Có trong K05/K06? | Thực nghiệm nhóm | Ô trống tiếng Việt |
|---|---|---|---|---|---|---|
| **A** Thưa: âm tiết, BoW/TF-IDF | [1] ● [2] ● [3] ● [4] ● [7] ● [8] ● [10] ● | K27 ● | | Có | ✚ TF-IDF 0,907 MF1 | Không |
| **B** Chọn/giảm chiều | [1] ● [2] ● [3] ● [5] ● | K27 ○ (SVD) | S13 | Có (một phần) | ✚ χ² 0,754 | Không |
| **C** Dense có giám sát | [3] ○ [7] ● | K27 ● (LSTM/CNN) | | Có | ✚ MLP-128 0,902 | Không |
| **D** Embedding không giám sát | [8] ● [10] ● [13] ○ | | S15–S20 | Có (doc2vec trong K06) | ✚ TRANS-IT, LDA | Không |
| **E1** FI làm đặc trưng | [13] ○ | | S09–S12, S04 | **Không** | ✚ FI-BIN 0,824 | Chỉ S12 (2006) |
| **E2** Trans2Vec IND/JOI | **[13] ●** | | S01–S03 | **Không** | ✚ E6, E7, Mục 17 | **Chỉ có nhóm** |
| **E3** Mẫu nén/ổn định (mới) | | **K25 ●, K26 ●** | S07, S08 | **Không** | ✚ A3 (xem §5.2: chưa kiểm chứng được) | **Trống** |
| **F1** PLM fine-tune | [6] ● [9] ● [10] ● | | S21, S23 | Có | — (không có GPU) | Không |
| **F2** Embedding đóng băng + bộ phân loại nhẹ (mới) | | **K29 ●** | S26 | Không (dừng 2021–2022) | chờ E10 | **Trống** |
| **G** Đồ thị (mới) | | **K30 ●**; K05, K06 ○ | S02, S04 | Có (GNN) | — | **Trống** |

**Nhận xét:**
- **Nhánh E (E1–E3) không có trong taxonomy của K05 và K06.** Hai survey lớn nhất trong kho đều bỏ qua biểu diễn dựa trên mẫu phổ biến. Đây là bằng chứng có trích dẫn cho khoảng trống mà v2 mới chỉ khẳng định.
- **E3, F2, G đều trống ở tiếng Việt.** Trong ba ô này, chỉ E3 nằm trong phạm vi đề tài. F2 là đối chứng (E10). G không phù hợp với tiếng Việt vì phụ thuộc công cụ NLP sâu (xem §4, K21 × K30).
- Ở nhánh C, **K27 cùng loại với [7]**: cả hai là mạng dựng trên vector TF-IDF/BoW. "LSTM" của K27 không mô hình hóa thứ tự từ.

---

## 4. Bước (1): tiền xử lý tiếng Việt (→ Chương 2, RQ1)

Bổ sung cho `synthesis.md` §5 (bảng tiền xử lý × họ biểu diễn vẫn dùng được).

| Vấn đề | Bằng chứng tài liệu | Bằng chứng của nhóm | Hàm ý cho hệ thống |
|---|---|---|---|
| Nhập nhằng tách từ | "luật gia cầm cự" [1]; "học sinh ra" [2]; **"bảo lãnh bằng chứng khoán"** [3], K27 | {e, mail}: FI tự ghép lại từ bị pyvi tách sai [RESULTS §2.4]; nhưng chỉ 13,5% cặp âm tiết phổ biến trùng một từ | FI bù lỗi tách từ **có xảy ra nhưng hiếm**; chưa đủ để bỏ tách từ |
| Có cần tách từ? | Không cần [1], [2]; có cần [3], [9] | **A1:** không tách từ mất 1–3 điểm ở mọi biểu diễn; FI chỉ bù +0,9 [E6] | Giữ tách từ (pyvi) |
| Chi phí tách từ | **K21:** 2 triệu âm tiết trong 6 giây, khoảng 440 bài/giây | Nạp 84.132 bài trong 99 giây (gồm cả ghi CSDL) [GĐ-H2] | Tách từ **không phải nút thắt** |
| Công cụ NLP sâu | **K21:** NER F1 0,58; dependency khoảng 70% (bảng của bài có LAS > UAS, nghi đảo số) | — | Phương pháp cần POS/NER/coref (**K30**) sẽ bị lan truyền lỗi khi chuyển sang tiếng Việt |
| Dấu thanh trong tìm kiếm | (chưa có tài liệu) | **E-DB5:** giữ dấu tốt hơn gộp dấu với truy vấn có dấu (0,653 so với 0,621); truy vấn không dấu trên chỉ mục giữ dấu chỉ còn 0,394, 9% rỗng; nhánh gộp dấu riêng đạt 0,615 | Cần **hai nhánh** chỉ mục. Đây là phát hiện riêng của nhóm, chưa có trong tài liệu khảo sát |
| Ranh giới từ (bối cảnh quốc tế) | **K06:** Sogou News (tiếng Trung) | — | Tiếng Việt khác ở chỗ khoảng trắng tách âm tiết, không tách từ |

**Kết luận bước (1):** tiền xử lý tiếng Việt quan trọng ở **hai chỗ** mà tài liệu cũ ít nói tới: (a) chọn item cho FI (stopword, top-k) và (b) dấu thanh trong tìm kiếm. Tách từ thì rẻ và vẫn có ích.

---

## 5. Bước (2)–(3): văn bản → transaction và khai phá FI (→ Chương 3.2, 5.6, RQ3)

### 5.1 Nền tảng KDD mới

| Câu hỏi thiết kế | K25 | K26 | Mã gốc [13] | Nhóm |
|---|---|---|---|---|
| Khai phá loại FI nào? | **Closed FI**: nén, không mất thông tin support; mỗi lớp tương đương có một đại diện | Chỉ xét FI đầy đủ | FI đầy đủ | FI độ dài ≤ 3; mọi FI đều đóng ở cấu hình chính (§5.2) |
| Chọn δ thế nào? | **CICFI**: giữ FI có cận dưới CI Wilson của rsup ≥ θ | δ **làm đổi đặc trưng dữ liệu**; phải quét và báo kèm hồ sơ dữ liệu | Elbow trên đồ thị số FI | Elbow tuyến tính cho δ = 0,535%; cả 4 cấu hình chọn cùng δ nên elbow kém nhạy [RESULTS §3.2] |
| Thuật toán nào? | (lọc sau khi có CFI) | **LCMv3, FP-Growth** thường tốt nhất; các mở rộng quan trọng hơn bản thân thuật toán | `FIM_Trans.exe` (chỉ Windows) | Đếm cặp bằng XᵀX thưa + bộ ba kiểu Apriori; 3 giây |
| Chặn bùng nổ thế nào? | CFI giảm số FI | Bùng nổ **chưa giải được**; cần top-k hoặc tóm tắt mẫu | — | **A2:** k = 100 cho 30.866 FI (gấp 9 lần k = 50), chi phí gấp khoảng 4,7 lần, không cải thiện |
| Mô tả corpus dạng giao dịch | — | 8 độ đo: density, similarity, ID, IT, IS, \|T\|, \|B\|, \|\|T\|\| | — | **chờ E8** |

### 5.2 Đính chính quan trọng: K25 chưa được kiểm chứng trên dữ liệu của nhóm

Phiếu K25 (§6) và kế hoạch v3 (§7, dòng E9) đều viết rằng ablation A3 (chỉ FI đóng: 0,770 so với 0,766) "khớp với dự đoán của K25" và rằng "phần closed FI của E9 đã có". **Hai nhận định này không còn đúng.** GĐ-H3 phát hiện rằng ở cấu hình chính (k = 50, δ = 0,535%, support tối thiểu 181 bài, FI dài tối đa 3), **mọi FI đều là FI đóng**. Phát hiện được kiểm tra bằng hai cách độc lập (`he_thong_db.md` §4). Hệ quả:
- A3 so sánh hai tập FI giống hệt nhau. Chênh 0,004 là dao động ngẫu nhiên.
- K25 **chưa được kiểm chứng**, cũng chưa bị bác bỏ. Muốn kiểm chứng phải hạ δ hoặc tăng độ dài FI tối đa, để có FI không đóng.
- Giả thuyết H8 (FI cùng lớp tương đương gây đa cộng tuyến) vì vậy cũng **không phát sinh ở cấu hình hiện tại**.

→ Việc cần làm: sửa phiếu K25 §6, kế hoạch v3 §7 và RESULTS.md mục H2 (đã ghi ở GĐ11). Viết lại E9 thành "hạ δ để có FI không đóng, rồi so sánh all/closed/CICFI".

### 5.3 Hồ sơ dữ liệu giao dịch: Snippets so với VNTC (giả thuyết cho E8)

| Đại lượng | Snippets [13] | VNTC-10 (nhóm) | Nguồn |
|---|---|---|---|
| Số giao dịch train | 10.060 | 33.759 | [13]; RESULTS §1 |
| Độ dài giao dịch | khoảng 13 item | 50 item (top-k), bài gốc dài trung bình 488 âm tiết | K26 phiếu §6; RESULTS §1 |
| Density | khoảng 5,5×10⁻⁴ (ước tính, cỡ Retail) | chờ E8 | K26 phiếu §6 |
| Đóng góp của FI (JOI − IT), đánh giá nhất quán | **+3,07** (inductive, 3 seed) / +0,70 (transductive) | **+0,1** (từ, k = 50) / +0,9 (âm tiết) | [E7]; [E6] |

**Điểm mới khi đặt hai cột cạnh nhau:** trên Snippets, đánh giá inductive cho FI đóng góp +3,07, gần mức +3,82 của bài báo. Trên VNTC, cùng cách đánh giá chỉ cho +0,1. Như vậy kết luận "FI không giúp" của nhóm **chưa chắc phổ quát**: có thể FI chỉ giúp khi giao dịch ngắn và thưa, tức văn bản ngắn. Đây đúng là dạng giải thích theo hồ sơ dữ liệu mà K26 gợi ý. Cần E8 (tính 8 độ đo) và nên thử thêm trên văn bản ngắn tiếng Việt (UIT-ViON, 260.000 tiêu đề, `candidates.md`).

> **Cập nhật sau E8 (22/10, `RESULTS.md` Mục 7.1):** giả thuyết "thưa so với dày" **không được ủng hộ**. Hai corpus cùng thưa (density 6,4×10⁻⁴ so với 1,1×10⁻³), Sim % gần nhau, tỉ lệ bài không có FI dài ≥ 2 bằng nhau (14%). Khác biệt rõ nhất chỉ là độ dài giao dịch (13 so với 49 item), nhưng tăng tỉ trọng FI trong VNTC cũng không làm FI có ích hơn. Câu hỏi "vì sao FI giúp Snippets" vẫn mở; ứng viên kiểm chứng rẻ nhất là văn bản ngắn tiếng Việt.

---

## 6. Bước (4)–(5a): biểu diễn và phân loại (→ Chương 4, 6, 8, RQ2, RQ4)

### 6.1 Bảng kết quả trên VNTC-10 (cùng corpus, cùng cách chia 33.759 / 50.373)

| Nguồn | Biểu diễn → bộ phân loại | Accuracy | Macro-F1 | Ghi chú |
|---|---|---|---|---|
| [1] 2007 | BoW + OCFS → SVM | 96,21% | — | Accuracy trung bình theo lớp; bản scan, không có std |
| [1] 2007 | N-gram âm tiết → NB | 95,58% | — | |
| **K27** 2024 | BoW → "LSTM" | 94,52% | — | Đầu vào là vector BoW, không phải chuỗi |
| **K27** 2024 | TF-IDF → SVM (C = 1) | 93,60% | — | |
| **K27** 2024 | TF-IDF → LR | 92,77% | — | |
| Nhóm [E6] | TF-IDF toàn văn → LR | 0,925 | **0,907** | Mạnh nhất trong các phương pháp của nhóm |
| Nhóm [E1] | MLP-128 có giám sát → SVM | — | 0,902 | Theo [7] |
| Nhóm [Mục 17] | **Trans2Vec-CAT** (IT ‖ FI ‖ JOI) → LR | 0,882 | **0,857** | Mô hình cải tiến; chọn bằng CV trên train |
| Nhóm [E6] | Trans2Vec-JOI → LR | 0,875 | 0,849 | |
| Nhóm [E6] | TRANS-IT → LR | 0,874 | 0,847 | ≡ PV-DBOW |
| Nhóm [Mục 17] | Trans2Vec gốc (mã tác giả, transductive) → LinearSVC | 0,852 | 0,823 | Mốc |
| Nhóm [E1] | LDA-100 → SVM | — | 0,827 | |

**Nhận xét:**
1. **Cùng TF-IDF + bộ phân loại tuyến tính mà Accuracy trải từ 92,5% (nhóm) đến 96,21% ([1]).** Chênh tới 3,7 điểm trên cùng corpus và cùng cách chia. Đây là bằng chứng mạnh nhất cho luận điểm "tiền xử lý và giao thức chi phối kết quả" (Chương 8.2). Khác biệt chưa được bài nào phân tích.
2. **Kết luận "DL tốt hơn ML" của K27 không đứng vững:** với TF-IDF, LSTM chỉ hơn SVM 0,15 điểm, không có std; mạng lại không nhận chuỗi từ.
3. **Trans2Vec vẫn kém TF-IDF khoảng 0,05 Macro-F1**, kể cả với CAT. Hạn chế H1 (mất tần suất) được xác nhận.

### 6.2 Snippets (tiếng Anh, bối cảnh gốc của [13])

| Phương pháp | Bài báo [13] | Nhóm, transductive [E7] | Nhóm, inductive [E7] |
|---|---|---|---|
| TF-IDF → SVM | 70,26 | — | — |
| TRANS-IT | 75,23 | **75,29 ± 0,66** | 73,44 ± 0,60 |
| Trans2Vec-JOI | 79,05 | 75,99 ± 0,43 | 76,51 ± 0,14 |
| BoW + LDA Wikipedia → MaxEnt (S18) | 82,18 | — | — |

TRANS-IT tái hiện đúng, nên cài đặt của nhóm là chính xác. JOI thì không đạt con số công bố (thiếu 2,5–3,1 điểm).

### 6.3 Đối chứng quốc tế (không so sánh trực tiếp với VNTC)

| Nguồn | Dataset tin tức | Kết quả | Cách dùng trong survey |
|---|---|---|---|
| K06 | AG News | fastText 92,50; XLNet 95,51 | Bối cảnh Chương 7.1 |
| K29 | AG News | LLMEmbed 0,958; RoBERTa-large đóng băng 0,944 | Mô thức F2; RoBERTa trên R52 = 0,422, đúng bằng tỉ lệ lớp lớn nhất (baseline không hội tụ) |
| K30 | R8 / 20NG | 98,75 / 93,71 | Chỉ dùng làm ví dụ phản biện: baseline TextGCN lệch công bố gốc tới 11 điểm |

### 6.4 Bộ phân loại × biểu diễn (bổ sung `synthesis.md` §6.1)

| Kết hợp | Bằng chứng mới |
|---|---|
| LR trên embedding | Nhóm: LR hơn SVM 0,6–0,7 điểm trên mọi biến thể Trans2Vec [E6]; K29 cũng chỉ dùng đầu phân loại nhẹ |
| Nối nhiều embedding | CAT hơn JOI 0,008 [Mục 17]; K29: nối thêm BERT/RoBERTa chỉ thêm khoảng 0,3 điểm. **Hai nguồn độc lập cùng cho thấy nối vector có lợi nhưng nhỏ** |
| Ghép embedding với TF-IDF | A5: 0,867 < TF-IDF 0,903, do hai khối lệch thang đo [E4] |

---

## 7. Bước (5b): tìm kiếm (→ Chương 9.5, RQ6, mới)

### 7.1 Truy vấn là bài báo (1.000 truy vấn, kho 33.759 bài, liên quan = cùng chuyên mục)

| Phương pháp | nDCG@10 | MAP@100 | Nguồn |
|---|---|---|---|
| InnoDB FULLTEXT | 0,597 | 0,436 | [E-DB1] |
| TF-IDF cosine | 0,740 | 0,565 | [E2] |
| BM25 (Manticore) | 0,749 | 0,558 | [E-DB4] |
| LDA-100 | 0,765 | 0,603 | [E2] |
| Trans2Vec gốc (mã tác giả) | 0,762 | — | [Mục 17] |
| TRANS-IT | 0,800 | 0,671 | [E2] |
| Trans2Vec-CAT | 0,807 | — | [Mục 17] |
| Trans2Vec-JOI | 0,809 (GĐ6) / 0,816 (hệ thống) | 0,686 / 0,682 | [E2]; [E-DB4] |
| **Hybrid RRF (k = 60, d = 100)** | **0,819** | 0,639 | [E-DB4] |

*Hai con số của JOI đến từ hai lần huấn luyện khác nhau (`src/experiments/` và `train_models.py`). Khi viết survey phải ghi rõ dùng số nào.*

### 7.2 Truy vấn 3 từ khóa (nDCG@10)

| Phương pháp | Tất cả (1.000) | Có FI (56) | Không FI (944) | Nguồn |
|---|---|---|---|---|
| TF-IDF | 0,634 | 0,805 | 0,624 | [E3, A6] |
| BM25 | 0,653 | 0,769 | 0,646 | [E-DB4] |
| JOI (kNN) | 0,690 | 0,863 | 0,679 | [E-DB4] |
| **Hybrid** | **0,704** | **0,870** | **0,694** | [E-DB4] |

### 7.3 Tổng hợp cho RQ6

| Câu hỏi con | Trả lời | Bằng chứng | Độ chắc chắn |
|---|---|---|---|
| Một biểu diễn có phục vụ được cả hai tác vụ? | **Được, nhưng mô hình tốt nhất khác nhau:** CAT tốt nhất cho phân loại, JOI tốt nhất cho tìm kiếm | [Mục 17] | TB |
| Embedding có hơn biểu diễn thưa ở tìm kiếm? | Có, khoảng +0,07 nDCG@10 với cả truy vấn dài lẫn ngắn | [E2], [E-DB4] | TB, vì proxy liên quan |
| FI có giúp tìm kiếm? | Có xu hướng: JOI > IT (0,809 so với 0,800); truy vấn chứa FI dễ hơn hẳn | [E2], [E-DB4] | **Thấp**: chênh nhỏ, n = 56 |
| Hybrid có đáng dùng? | Có cho trang top-10, nhất là truy vấn ngắn (+0,014 so với kNN). Không hợp cho thu hồi sâu (MAP thấp hơn) | [E-DB4] | TB |
| Đánh giá thế nào cho đúng? | Proxy "cùng chuyên mục" **quá dễ và quá thô**: (a) PV chỉ đạt MAP 0,511 trên WikiQA, so với BERT 0,813, khi liên quan là khớp câu hỏi – câu trả lời thật (**K06**); (b) proxy không phân biệt được chỉ mục có recall 0,86 với recall 1,00 (nDCG chỉ dao động 0,811–0,818) | K06; [E-DB2] | **Cao** |

**Kết luận RQ6:** kết quả tìm kiếm của nhóm là **cận trên lạc quan**. Survey cần nêu rõ rằng chưa có tập truy vấn tiếng Việt có nhãn liên quan do người gán cho tin tức. Đây là khoảng trống của giao thức, không chỉ của đề tài.

---

## 8. Bước (6): dữ liệu và giao thức (→ Chương 7, 8.4, RQ5)

### 8.1 Bảng dataset bổ sung (thêm vào `synthesis.md` §3)

| Dataset | Bài dùng | Ngôn ngữ | #Tài liệu | #Lớp | Ghi chú |
|---|---|---|---|---|---|
| VNTC Level 1 | [1], [3], **K27**, nhóm | vi | 84.132 | 10 | **Có 3.056 bài test (6,1%) trùng y hệt bài train; 380 nhóm trùng mang nhãn khác nhau** [GĐ-H2] |
| VNTC Level 2 | [1], [3], **K27** | vi | 26.451 | 27 | Số lượng ở K27 khác số thường trích từ [1] |
| UIT-ViON | (`candidates.md`) | vi | 260.000 tiêu đề | 13 | Ứng viên văn bản ngắn, chia cố định |
| AG News | **K06**, **K29** | en | 127.600 | 4 | Tin tức chuẩn quốc tế |
| 20 Newsgroups | **K06**, **K30** | en | khoảng 18.800–20.000 | 20 | |
| Reuters R8 / R52 | **K05**, **K29**, **K30** | en | 7.674 / 9.100 | 8 / 52 | Mất cân bằng mạnh (R52: lớp *earn* chiếm 42% tập test) |
| Sogou News | **K06** | zh | — | — | Tin tức ở ngôn ngữ không có ranh giới từ |

### 8.2 Các mối đe dọa đến tính hợp lệ (bảng mới, → Chương 8.4)

| # | Mối đe dọa | Ví dụ trong tài liệu | Ví dụ của nhóm | Đề xuất giao thức |
|---|---|---|---|---|
| T1 | **Học transductive** (mô hình thấy văn bản test) | TextGCN (K30); mã gốc Trans2Vec | Mốc transductive 0,823 so với inductive dùng `model.dv` 0,766 [Mục 17] | Báo rõ chế độ; ưu tiên inductive |
| T2 | **Vector train và test sinh bằng hai quy trình khác nhau** | (ngầm định trong [13]) | Lệch 7–8 điểm; tạo "cải thiện nhờ FI" giả (+3,7; +4,1) [E6] | Sinh vector train và test bằng cùng `infer_vector` |
| T3 | **Baseline yếu hoặc lệch công bố gốc** | K30 (TextGCN, BERT); K29 (RoBERTa R52 = 0,422) | — | Chạy lại baseline trong cùng điều kiện |
| T4 | **Cùng corpus mà lệch nhau, không giải thích** | [1] 96,21% so với K27 93,60% | Nhóm 92,5% (Accuracy) | Công bố mã tiền xử lý |
| T5 | **Rò rỉ train–test qua bài trùng** | [3] (nghi) | 6,1% bài test VNTC có bản sao trong train | Khử trùng theo hash trước khi chia |
| T6 | **Chỉ báo Accuracy, không std** | K27, K29, K30 | E6 mới 1 seed | Macro-F1 ± std, nhiều seed |
| T7 | **Số liệu chép lại không kiểm tra tái lập** | K05 chép PV IMDB 92,58 (Mesnil 2014 không tái hiện được; cần xác minh) | JOI Snippets: 76,0 so với 79,05 công bố [E7] | Tái hiện trước khi so sánh |
| T8 | **Proxy liên quan cho tìm kiếm** | K06 (WikiQA cho thấy PV yếu khi có nhãn thật) | nDCG không nhạy với recall chỉ mục [E-DB2] | Tập truy vấn có nhãn thủ công; recall so với vét cạn khi so chỉ mục |

**Nhận xét:** 8 mối đe dọa, trong đó T1, T2, T5, T8 được nhóm **đo được bằng số**. Đây là đóng góp phương pháp luận của survey, độc lập với việc Trans2Vec thắng hay thua.

---

## 9. Chi phí (→ Chương 6, RQ4)

| Bước | Nguồn | Thiết lập | Chi phí |
|---|---|---|---|
| (1) Tách từ | K21 | 2 triệu âm tiết | 6 giây (bản gốc 234 giây) |
| (3) Khai phá FI | K26 | 14 dataset, ngưỡng thấp | Chênh 4–6 bậc độ lớn giữa các thuật toán; Eclat khoảng 140 giờ trên BMSPOS |
| (3) Khai phá FI | Nhóm [E4] | VNTC, k = 50 / k = 100 | 3 giây / 14 giây |
| (4) Huấn luyện + suy luận | Nhóm [E4] | JOI, k = 50, CPU | 16 giây + 42 giây (50.373 bài) |
| (4) Huấn luyện 6 biến thể | Nhóm [GĐ-H3] | 7 model_run | 234 giây |
| (4)+(5a) Fine-tune PLM | [10] | 12.000 review, GPU T4 | khoảng 41 phút |
| (4)+(5a) LLM đóng băng | **K29** | 5 benchmark, GPU A100 | trung bình 1 giờ 41 phút; 0,38 kWh (so với CARP 115 giờ, 20,93 kWh) |
| (5b) Tìm kiếm | Nhóm [E-DB2, E-DB4] | 33.759 vector | HNSW dưới 1 ms; infer_vector 3–5 ms; hybrid p50 7–18 ms |
| (5b) Full-text | Nhóm [E-DB1] | truy vấn dài | Manticore 11 ms so với InnoDB 213 ms (p50) |

**Kết luận RQ4:** toàn bộ đường ống Trans2Vec chạy trên CPU trong vài phút, tìm kiếm dưới 20 ms. Đánh đổi là "rẻ, diễn giải được, kém TF-IDF 0,05" so với "đắt, cần GPU, chưa rõ hiệu quả trên tin tức tiếng Việt dài" (K29 tự nhận yếu với văn bản dài). **Nút thắt của hệ thống nằm ở infer_vector, không nằm ở CSDL** [E-DB2].

---

## 10. Mâu thuẫn mới và cách giải thích (bổ sung `synthesis.md` §7)

| # | Mâu thuẫn | Phía A | Phía B | Giải thích đề xuất |
|---|---|---|---|---|
| M6 | TF-IDF + SVM trên VNTC | [1]: 96,21% | K27: 93,60%; nhóm: 92,5% | Tiền xử lý (stopword, tách từ), cách tính Accuracy ([1] lấy trung bình theo lớp), C, kernel. Không bài nào công bố đủ để tái lập |
| M7 | FI đóng góp bao nhiêu? | [13]: +3,82 (Snippets) | Nhóm: +0,70 (Snippets, transductive); +0,1 (VNTC) | **Hồ sơ dữ liệu** (giao dịch ngắn, thưa so với dài, dày; chờ E8) cộng với **độ dao động** ([13] không báo std). Inductive trên Snippets cho +3,07 nên hiệu ứng có thể có thật trên văn bản ngắn |
| M8 | PV có tốt cho tìm kiếm? | K06: MAP 0,511 trên WikiQA, rất xa BERT | Nhóm: JOI hơn TF-IDF 0,07 nDCG@10 | Khác **định nghĩa liên quan**: khớp câu trả lời (khó) so với cùng chuyên mục (dễ). Không mâu thuẫn thật |
| M9 | TextGCN đạt bao nhiêu? | K05, K06: 20NG 86,34; MR 76,74 | K30: 20NG 79,52; MR 80,18; R8 86,07 (bản gốc 97,07) | Baseline chạy lại không cẩn thận trong K30 |
| M10 | Học sâu có hơn ML trên VNTC? | K27: có | K27 (chính số liệu của bài): chỉ +0,15 điểm với TF-IDF, mạng không nhận chuỗi | Kết luận vượt quá bằng chứng |
| M11 | Closed FI có giúp? | K25: nén, bỏ dư thừa | Nhóm A3: 0,770 so với 0,766 | **Không phải mâu thuẫn**: ở cấu hình của nhóm mọi FI đã đóng, nên A3 không kiểm chứng gì (§5.2) |

---

## 11. Hạn chế H1–H8 × bằng chứng (cập nhật `synthesis.md` §8)

| Hạn chế | Trạng thái sau thực nghiệm | Tài liệu mới | Việc còn lại |
|---|---|---|---|
| **H1** Mất thứ tự, tần suất | **Xác nhận:** TF-IDF 0,907 > CAT 0,857 > JOI 0,849 | Chen 2004 (`candidates.md`, FI + tần suất) | Thử FI có trọng số tần suất |
| **H2** Bùng nổ FI | **Xác nhận:** k = 100 gấp 9 lần số FI, không lợi | **K26** (bùng nổ chưa giải được), **K25** (CFI) | Báo cáo quét δ kèm hồ sơ dữ liệu |
| **H3** Baseline yếu trong [13] | **Xác nhận:** TF-IDF mạnh hơn mọi biến thể trên VNTC | K29 (trần F2), K27 (baseline VNTC mới) | E10 |
| **H4** Hiệu quả phụ thuộc dữ liệu | **Có dấu hiệu:** FI +3,07 trên Snippets so với +0,1 trên VNTC | **K26** (độ đo hồ sơ dữ liệu) | **E8**; thử văn bản ngắn tiếng Việt (UIT-ViON) |
| **H5** Không có suy luận cho truy vấn | **Đã giải:** infer_vector chạy được với truy vấn 3 từ; 3–5 ms | — | Truy vấn không dấu: nhánh vector kéo kết quả lạc đề (0,473), nên hybrid bỏ nhánh này |
| **H6** Chỉ đánh giá phân loại | **Đã giải một phần:** có tìm kiếm (BM25, kNN, hybrid) | K06 (giới hạn của proxy) | Tập truy vấn có nhãn thủ công |
| **H7** Không báo chi phí | **Đã giải:** §9 | K21, K26, K29 | — |
| **H8** (mới) Đa cộng tuyến giữa FI cùng lớp tương đương | **Không phát sinh** ở cấu hình hiện tại (mọi FI đóng) | **K25** | Chỉ kiểm chứng được khi hạ δ (E9 bản sửa) |

---

## 12. Trả lời sơ bộ RQ1–RQ6 (khung kết luận cho GĐ11)

| RQ | Trả lời sơ bộ | Mức chắc chắn | Còn mở |
|---|---|---|---|
| **RQ1** Tiền xử lý | Tách từ rẻ (K21) và có ích (A1: +1–3 điểm). Với Trans2Vec, chọn item (stopword, top-k) quyết định FI. Với tìm kiếm, dấu thanh cần hai nhánh chỉ mục (E-DB5) | Cao | Ảnh hưởng của bộ tách từ khác (VnCoreNLP so với pyvi) |
| **RQ2** So sánh các họ biểu diễn | Trên VNTC: thưa ≥ dense có giám sát > embedding không giám sát (§6.1). Embedding thắng ở tìm kiếm (§7). Nhánh E, F2, G vắng mặt ở tiếng Việt (§3) | Cao với VNTC; thấp với corpus khó | Corpus khó (≥ 25 lớp), PLM |
| **RQ3** FI làm giàu embedding? Loại FI nào? | Phân loại: gần như không trên VNTC (−0,3 đến +0,9); có thể có trên văn bản ngắn (Snippets inductive +3,07). Tìm kiếm: xu hướng dương nhỏ. Loại FI: **chưa trả lời được**, vì ở cấu hình hiện tại mọi FI đều đóng | TB với VNTC; **thấp** với loại FI | E8, E9 (bản sửa) |
| **RQ4** Bộ phân loại và chi phí | LR tốt hơn SVM trên embedding. Nối vector có lợi nhỏ (CAT +0,008; K29 +0,3). Toàn bộ đường ống chạy trên CPU trong vài phút | Cao | So chi phí với F2 (E10) |
| **RQ5** Dataset và giao thức | 8 mối đe dọa T1–T8, trong đó 4 mối đo được bằng số trên dữ liệu của nhóm (§8.2) | Cao | — |
| **RQ6** Một biểu diễn cho cả hai tác vụ; đánh giá tìm kiếm | Một embedding dùng chung được (JOI), nhưng mô hình tốt nhất cho từng tác vụ khác nhau. Hybrid tốt cho top-10. Proxy "cùng chuyên mục" là cận trên lạc quan | TB | Nhãn liên quan thủ công; baseline embedding câu (E10) |

---

## 13. Phát biểu khoảng trống v3 (thay `synthesis.md` §10 khi viết GĐ11)

> Phân loại tin tức tiếng Việt đã đi qua ba thế hệ biểu diễn: thưa ([1]–[5], K27), dày có giám sát ([7], K27) và Transformer ([6], [9], [10]). Khai phá tập phổ biến đã có cơ sở lý thuyết và thuật toán hiện đại (K25, K26), nhưng các công trình này dừng ở tốc độ và tính chất, không chạm tới tác vụ hạ nguồn. Hai survey lớn về phân loại văn bản (K05, K06) **không có nhánh nào cho biểu diễn dựa trên mẫu phổ biến**.
>
> **Vì vậy hướng học embedding từ tập phổ biến (Trans2Vec [13]) chưa được đánh giá trên văn bản tiếng Việt, trên văn bản dài như tin tức, và cho tìm kiếm.** Thực nghiệm của đề tài lấp khoảng trống này. Kết quả cho thấy lợi ích của FI phụ thuộc mạnh vào dữ liệu và vào giao thức đánh giá; khi đánh giá đúng, kết quả trên văn bản tiếng Việt dài thấp hơn nhiều so với mức công bố trên văn bản ngắn tiếng Anh.

**Ba đóng góp (chỉnh so với v2):**
1. Hệ thống hóa các thành phần của một hệ thống tìm kiếm và phân loại tin tức tiếng Việt **theo đường ống**, đặt nhánh pattern-based embedding (E1–E3) cạnh các nhánh mà K05, K06 đã phủ.
2. **Đánh giá thực nghiệm có kiểm soát giao thức**: tái hiện [13], đo 4 mối đe dọa đến tính hợp lệ (T1, T2, T5, T8), và chỉ ra rằng đóng góp của FI bị thổi phồng khi giao thức không nhất quán.
3. Kiến trúc chạy được (MariaDB + Manticore) với ba chế độ tìm kiếm, cùng phân tích dấu thanh cho tìm kiếm tiếng Việt.

---

## 14. Ánh xạ → chương survey v3 (cho GĐ11)

| Chương | Mục dùng trong file này | Tài liệu mới chính |
|---|---|---|
| 1. Giới thiệu | §2, §13; RQ6 | K05, K06 |
| 2. Tiếng Việt | §4 | K21, K27 |
| 3. Nền tảng | §5.1 | K25, K26, K05 (độ đo) |
| 4. Tiến hóa biểu diễn | §1, §3 | K27, K29, K30 |
| 5. Trans2Vec | §5.2, §5.3, §11 | K25, K26, K29 |
| 6. Bộ phân loại và chi phí | §6.4, §9 | K26, K27, K29 |
| 7. Dữ liệu và giao thức | §8.1 | K05, K06, K26 |
| 8. Thảo luận | §6.1, §8.2, §10 | K27, K30, K06 |
| 9. Đề xuất hệ thống | §7, `he_thong_db.md` | K25, K26, K29, K06 |
| 10. Kết luận | §12, §13 | tất cả |

---

## 15. Việc cần xử lý trước hoặc trong GĐ11

| # | Việc | File | Ghi chú |
|---|---|---|---|
| 1 | Sửa nhận định "A3 khớp K25" và "closed FI của E9 đã có" | `K25_closedfi_zhang2025.md` §6, `KE_HOACH_SURVEY_v3.md` §7, `RESULTS.md` mục H2 | Theo §5.2. Kế hoạch v3 chỉ nên **thêm ghi chú đính chính**, không viết lại |
| 2 | Viết lại E9: hạ δ để có FI không đóng, so all / closed / CICFI | `KE_HOACH_SURVEY_v3.md` §7 | Cần anh/chị duyệt khi chốt Q4 |
| 3 | Xác minh qua Crossref: số trang/DOI của K21, DOI của K29, số tập của K30, bài Mesnil 2014 (T7) | `refs.tsv` | Trước khi thêm vào survey |
| 4 | Thống nhất dùng nDCG@10 của JOI: 0,809 (GĐ6) hay 0,816 (hệ thống) | — | Đề xuất: Chương 9.5 dùng 0,809 cho bảng biểu diễn, 0,816 cho bảng Manticore, và ghi chú hai lần huấn luyện |
| 5 | Cân nhắc thêm tài liệu sơ cấp cho bước (5b) | `candidates.md` (PACLIC 2024, Do & Nguyen 2021) | Bước này hiện thiếu tài liệu nhất (§2) |
