# GĐ4 — Ma trận tổng hợp (Synthesis)

**Đề tài:** Hệ thống tìm kiếm & phân loại chuyên mục tin tức tiếng Việt với biểu diễn Trans2Vec
**Đầu vào:** 11 phiếu đọc `notes/01..13_*.md` và 27 tài liệu bổ sung `notes/supplementary.md` (mã S01–S27)
**Ngày:** 07/10/2026
**Mục đích:** gom chứng cứ theo từng trục để viết survey (GĐ5). Mỗi bảng ghi rõ nó phục vụ chương nào.

---

## 1. Dòng thời gian (→ Chương 4, hình timeline)

| Năm | Khai phá mẫu (KDD) | Biểu diễn / NLP chung | Văn bản tiếng Việt |
|---|---|---|---|
| 1994 | Apriori (S05) | | |
| 1998 | CBA, luật kết hợp phân lớp (S14) | | |
| 2000 | FP-Growth (S06) | | |
| 2002 | FI cho phân cụm văn bản (S09); CHARM closed itemsets (S07) | | |
| 2003 | FIHC: cây chủ đề từ FI (S10) | | |
| 2006 | | | **FI + luật kết hợp phân loại văn bản tiếng Việt (S12)** |
| 2007 | FI phân biệt, có giám sát (S13) | | **[1]** BoW + chọn đặc trưng / N-gram âm tiết; corpus VNTC |
| 2008 | | Chủ đề ẩn LDA cho văn bản ngắn (S18) | |
| 2009 | | | **[2]** Bag-of-syllables |
| 2013–14 | | Word2Vec + negative sampling (S16); Paragraph Vector (S15) | |
| 2015 | Đồ thị con phổ biến trên graph-of-words (S04) | | |
| 2016 | | Đánh giá thực nghiệm Doc2Vec (S17) | |
| 2017 | Tổng quan itemset mining (S08) | | **[3]** KEBoW + NN |
| 2018 | **[13] Trans2Vec**; Sqn2Vec (S01); đồ thị con phổ biến → embedding (S02) | | VnCoreNLP (S24) |
| 2019 | | Sentence-BERT (S21) | **[4]** VNNews-01 |
| 2020 | | Top2Vec (S19); DPR (S22) | **[5]** TextRank; **[6]** PhoBERT HSD; PhoBERT (S23) |
| 2021 | Con2Vec (S03) | | **[7]** NN trích đặc trưng |
| 2022 | FI thực thể cho văn bản dài (S11) | BERTopic (S20) | **[8]** TF-IDF vs embedding |
| 2024 | | | **[9]** EDA + BERTology |
| 2025 | | | **[10]** PhoBERT + topic model |
| 2026 | | | VN-MTEB (S26) |

**Đọc bảng:** hai dòng chảy *khai phá mẫu* (cột 1) và *học biểu diễn* (cột 2) hội tụ ở **Trans2Vec (2018)**. Dòng chảy *văn bản tiếng Việt* (cột 3) đi từ sparse (2007–2017) sang embedding và Transformer (2020–2025), nhưng **chưa từng đi qua điểm hội tụ đó**. Đây chính là khoảng trống của đề tài.

---

## 2. Ma trận taxonomy × tài liệu (→ Chương 4, 5)

Ký hiệu: ● trọng tâm của bài · ○ dùng làm baseline hoặc đề cập.

| Nhánh | [1] | [2] | [3] | [4] | [5] | [6] | [7] | [8] | [9] | [10] | [13] | Tài liệu bổ sung |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **A1** Âm tiết / n-gram | ● | ● | | | | | ○ uni+bi | | | | | |
| **A2** BoW / TF-IDF theo từ | ● | | ● | ● | | | ● | ● | | ● | ○ | |
| **B1** Chọn đặc trưng thống kê | ● | ● | | | | | ○ | | | | | S13 |
| **B2** Lọc từ điển | | ● | | | | | | | | | | |
| **B3** Từ khóa | | | ● | | ● | | | | | | | |
| **C** NN trích đặc trưng (có giám sát) | | | ○ | | | | ● | | | | | |
| **D1** Word2Vec / GloVe | | | | | | | | ● | | ● | | S16 |
| **D2** Doc2Vec | | | | | | | | ● | | | ○ TRANS-IT | S15, S17 |
| **D3** Topic model | | | | | | | | | | ● | | S18, S19, S20 |
| **E1** FI làm đặc trưng / cụm | | | | | | | | | | | ○ FI-BIN/SUP | S09, S10, S12, S04, S11 |
| **E2** FI làm đơn vị embedding | | | | | | | | | | | **●** | S01, S02, S03 |
| **F** Transformer pretrained | | | | | | ● | | | ● | ● | | S21, S23 |

**Nhận xét:**
- Ô **E2 × tiếng Việt** trống hoàn toàn.
- Nhánh E1 có một tiền lệ tiếng Việt duy nhất (S12, 2006), bằng luật kết hợp, không có embedding.
- Chỉ [10] phủ đồng thời D và F, nên đó là bài có bảng so sánh "nhiều biểu diễn" đầy đủ nhất trên tiếng Việt.

---

## 3. Bảng dataset (→ Chương 7)

| Dataset | Bài dùng | Miền / nguồn | Ngôn ngữ | #Tài liệu | #Lớp | Chia dữ liệu | Công khai | Độ khó (ước lượng) |
|---|---|---|---|---|---|---|---|---|
| **VNTC Level 1** | [1], [3], S25 | Tin tức (4 báo) | vi | 84.132 | 10 | 33.759 / 50.373 (gốc); 67.305 / 8.413 / 8.414 (bản chia lại cố định do cộng đồng tạo) | ✅ GitHub | Thấp–TB |
| **VNTC Level 2** | [1], [3] | Tin tức, chủ đề con | vi | 26.451 | 27 | 14.375 / 12.076 | ✅ | TB |
| VNNews-01 | [4] | Tin tức (>30 trang) | vi | 37.500 | 25 | 5-fold CV | ⚠️ theo yêu cầu | **Cao** |
| Corpus của [7] | [7] | Tin tức (5 trang) | vi | 68.363 | 30 | 48.363 / 10k / 10k | ❌ | Cao |
| D1 / D2 của [2] | [2] | Tin tức / thể loại | vi | ~16k / 1.743 | 4 / 2 | 10% train | ❌ | Thấp / Cao |
| Corpus của [5] | [5] | Tin tức (4 trang) | vi | 4.500 | 15 | 200 / 100 mỗi lớp | ❌ | Thấp |
| VLSP 2019 HSD | [6] | Bình luận Facebook | vi | 25.431 | 3 | 10-fold | ✅ | Cao, mất cân bằng |
| ViHSD / UIT-ViCTSD | [9] | Bình luận FB, YT / VnExpress | vi | 33.400 / 10.000 | 3 / 2 | chuẩn | ✅ | Cao, mất cân bằng |
| Food comments | [8] | Bình luận ẩm thực | vi | 30k / 10k | 2 | 70:30 | ❌ | Thấp, cân bằng |
| Shopee reviews | [10] | Review TMĐT, đa nhãn | vi | 17.049 (*tóm tắt bài ghi 17.002*) | 5 (+Other) | 70 / 10 / 20 | ❌ | TB |
| **Snippets** | [13], S18 | Đoạn trích kết quả tìm kiếm web | en | 12.340 | 8 | 10.060 / 2.280 | ✅ | TB |
| Cancer / Retail / Food | [13] | Transaction (y tế, bán lẻ) | — | 15k / 3k / 4k | 3 / 2 / 2 | 80 / 20 | một phần | — |

**Nhận xét:**
- Chỉ **VNTC** vừa là tin tức tiếng Việt, vừa công khai, vừa đã có kết quả công bố ([1], [3]). Đây là **benchmark chính** cho thực nghiệm.
- Muốn có benchmark khó (≥ 25 chuyên mục, chồng lấn), phải xin VNNews-01 hoặc **tự crawl**. Phương pháp crawl có sẵn trong [4] và [10].
- Lỗi nhỏ phát hiện được: [10] tự mâu thuẫn về số review (17.002 ở tóm tắt so với 17.049 ở phần dữ liệu).

---

## 4. Bảng kết quả theo nhóm *có thể so sánh* (→ Chương 8)

> **Nguyên tắc:** chỉ so sánh trong cùng nhóm (cùng dataset và giao thức gần nhau). Giữa các nhóm chỉ so *xu hướng*, không so con số.

| Nhóm | Bài | Thiết lập | Biểu diễn → bộ phân loại tốt nhất | Kết quả | Độ tin cậy |
|---|---|---|---|---|---|
| **G1** VNTC-10 | [1] | Chia cố định, acc TB lớp | BoW + OCFS → SVM | **96,21%** | Khá (bản scan, không có std) |
| | [1] | như trên | N-gram âm tiết → NB | 95,58% | Khá |
| | [3] | Chia không rõ | KEBoW → MLP | 99,75% | ⚠️ **Thấp, nghi rò rỉ** |
| **G1b** VNTC-27 | [3] | Chia không rõ | KEBoW → MLP | 99,69% | ⚠️ Thấp |
| **G2** Tin tức nhiều lớp | [4] | 25 lớp, 5-fold, F1 | TF-IDF → SVM-RBF | **F1 0,749** | Cao |
| | [7] | 30 lớp, holdout | TF-IDF → MLP-128 → SVM | val acc ~0,905 | TB (chỉ val, so sánh qua hình) |
| **G3** Tin tức ít lớp | [2] | 4 lớp, 10% train | Bigram âm tiết → PSVM | 98,6% | TB |
| | [2] | 2 lớp theo thể loại | Bigram → PSVM | 89,8% | TB |
| | [5] | 15 lớp | Từ khóa TextRank → Jaccard | 95,4% | Thấp (không có baseline) |
| **G4** Snippets (en) | [13] | Chia cố định, 10 lần | TF-IDF → SVM | 70,26% | Cao |
| | [13] | như trên | **Trans2Vec-JOI → SVM** | **79,05%** (F1 78,31) | Cao |
| | S18 | như trên | BoW → MaxEnt | 65,75% | Cao |
| | S18 | như trên | BoW + LDA (Wikipedia) → MaxEnt | **82,18%** | Cao (*có dữ liệu ngoài*) |
| **G5** Ngoài miền tin tức | [6] | VLSP HSD, 10-fold | PhoBERT fine-tune | MF1 0,7221 | TB (CV so với leaderboard) |
| | [9] | UIT-ViCTSD | PhoBERT + EDA | MF1 74,63 | Cao |
| | [8] | Cảm xúc 2 lớp | TF-IDF → SVM | 86,8% | ⚠️ embedding ~50% |
| | [10] | Shopee đa nhãn | PhoBERT → BR-LR | MF1 0,96 | TB |

### 4.1 Mức cải thiện nhờ đổi biểu diễn, trong cùng nhóm (bằng chứng cho RQ2, RQ3)

| Từ → sang | Bài | Δ | Ghi chú |
|---|---|---|---|
| Unigram âm tiết → bigram âm tiết | [2] D1 / D2 | +0,3–0,9 / +0,4–7,7 điểm | Lợi nhiều hơn ở tác vụ khó |
| CHI / OCFS @128 → MLP @128 | [7] | dương (chỉ có hình) | Có giám sát |
| TF-IDF → TRANS-IT (PV-DBOW) | [13] Snippets | **+5,0** | Không giám sát |
| TRANS-IT → TRANS-FI | [13] Snippets | **+2,7** | **Giá trị riêng của FI** |
| TF-IDF → Trans2Vec-JOI | [13] Snippets | **+8,8** | |
| BoW → BoW + LDA ngoài | S18 Snippets | +16,4 | Có tri thức ngoài |
| TF-IDF → PhoBERT | [10] | +7 MF1 | Có tri thức ngoài (pretrain) |
| TF-IDF → Word2Vec | [8] / [10] | −32 / −1 MF1 (so với BoW: −3) | [8] nhiều khả năng lỗi; [10] gần ngang (lấy Macro-F1 tốt nhất mỗi biểu diễn: BoW 0,91, TF-IDF 0,89, W2V 0,88, PhoBERT 0,96) |

**Kết luận rút ra:**
1. **Biểu diễn dày thắng TF-IDF khi được huấn luyện đúng cách**, rõ nhất ở tác vụ khó hoặc văn bản ngắn ([13], [10]).
2. **FI có đóng góp riêng** ngoài embedding item: +2,7 điểm trong [13]. Đây là bằng chứng định lượng duy nhất hiện có cho RQ3.
3. **Tri thức ngoài** (LDA trên Wikipedia, pretrain PhoBERT) mang lại mức tăng lớn nhất (S18, [10]). Đây là trần trên mà Trans2Vec thuần (chỉ học từ dữ liệu trong bộ) cần được đặt cạnh.
4. **Độ khó corpus** chi phối kết quả: cùng là tin tức tiếng Việt, kết quả trải từ 0,749 ([4]) tới 99%+ ([3]).

---

## 5. Tiền xử lý × họ biểu diễn (→ Chương 2; bảng đề xuất mới)

| Bước | A1 Âm tiết | A2 / B TF-IDF, chọn đặc trưng | B3 Từ khóa | D Embedding tĩnh | **E Trans2Vec** | F PhoBERT / BERT |
|---|---|---|---|---|---|---|
| Chuẩn hóa mã, dấu thanh | Cần [1], [2] | Cần | Cần | Cần | **Cần** | Cần (Unicode) |
| Tách từ | **Không cần** [1], [2] | Cần [1] | Cần; lỗi lan truyền [3] | Cần [8] | **Tùy chọn, cần ablation** (giả thuyết âm tiết + FI ≈ từ ghép, vì > 80% từ có 2 âm tiết [2]) | **PhoBERT cần VnCoreNLP (+2 F1)** [9]; mô hình khác không cần |
| Bỏ stopword | Có ích | Có ích [1] | Rất quan trọng [3] | Có ích | **Rất quan trọng: quyết định item và FI** | **Vô ích hoặc có hại** [9] |
| Lọc từ điển / top-k | — | Giúp kNN [2] | Bản chất của phương pháp [3], [5] | — | **Bắt buộc để chặn bùng nổ FI (H2)**: top-k ≈ 50 [5], closed FI (S07), thực thể (S11) | — |

**Luận điểm cho survey:** tiền xử lý **giảm vai trò** dần theo tiến hóa từ A tới F, **nhưng quay lại thành yếu tố cốt lõi ở nhánh E**. Vì vậy, với Trans2Vec, tri thức ngôn ngữ tiếng Việt (tách từ, stopword, NER) không phải là bước phụ.

---

## 6. Bộ phân loại × biểu diễn, kèm chi phí (→ Chương 6)

### 6.1 Tổ hợp đã được kiểm chứng
| Bộ phân loại | Biểu diễn đã thử (bài) | Nhận xét tổng hợp |
|---|---|---|
| **SVM** | TF-IDF [1], [4], [8]; âm tiết [2]; MLP-128 [7]; KEBoW [3]; Trans2Vec [13] | Gần như luôn tốt nhất hoặc nhì với biểu diễn thưa; **là bộ phân loại chuẩn để so biểu diễn** ([13] cố định C = 1) |
| **LR** | TF-IDF [4], [8]; PhoBERT [10] | Gần bằng SVM ([4]: 0,734 so với 0,749), **suy luận nhanh hơn hàng nghìn lần**; tốt nhất trên PhoBERT [10] |
| NB | TF-IDF [4], [8]; n-gram [1]; âm tiết [2] | Rất nhanh; tốt khi đã chọn đặc trưng mạnh [2] |
| kNN | [1], [2], [4], [8] | **Kém nhất, nhạy với đặc trưng nhiễu** [2], [4]. Hệ quả: tìm kiếm top-k cần embedding sạch |
| RF / XGB | [3], [4], [8], [10] | Trung bình, huấn luyện chậm (RF-100: 408 s [4]) |
| MLP / fine-tune | [3], [7], [6], [9], [10] | Mạnh nhất khi có nhãn; cần GPU (PhoBERT) |

### 6.2 Chi phí đã được báo
| Bài | Thiết lập | Số liệu |
|---|---|---|
| [4] | 37,5k bài, CPU Xeon | NB 0,3 s; LR 77 s; SVM-RBF 839 s train / 291 s test; OVO test 4.785 s |
| [2] | D1, unigram so với bigram | Bigram chậm hơn 4,5–9,6 lần |
| [5] | 4,5k bài | 2.155–9.279 s train (tăng theo số từ khóa) |
| [10] | 12k review, Colab | TF-IDF 22 s CPU; PhoBERT ~41 phút GPU T4 (10 epoch) |
| [13] | — | **Không báo** (H7), cần tự đo: thời gian FP-Growth theo δ và thời gian huấn luyện PV-DBOW |

---

## 7. Mâu thuẫn trong tài liệu và cách giải thích (→ Chương 8)

| # | Mâu thuẫn | Phía A | Phía B | Giải thích đề xuất |
|---|---|---|---|---|
| M1 | Embedding tĩnh và TF-IDF | TF-IDF thắng: [8] (W2V/D2V ≈ 50%), [10] (W2V < BoW) | PV-DBOW thắng TF-IDF +5: [13] trên Snippets | Kết quả 50% của [8] trái với lý thuyết (1-NN cũng ≈ 50%), nên nhiều khả năng lỗi cài đặt. S17 cho thấy Doc2Vec tốt khi đủ dữ liệu và cấu hình đúng. [10] dùng văn bản rất ngắn và vector trung bình |
| M2 | Có cần tách từ? | Không: N-gram âm tiết ≈ BoW theo từ [1]; bigram [2], [7] | Có: lỗi tách từ gây phân loại sai [3]; PhoBERT +2 F1 [9] | Tùy họ biểu diễn (Bảng 5). Với Trans2Vec là **câu hỏi thực nghiệm mở**, cần ablation |
| M3 | Top2Vec tốt hay kém? | Kém về coherence trên review ngắn [10] | Tác giả Top2Vec cho rằng tốt hơn LDA (S19) | Phụ thuộc độ dài văn bản và kích thước corpus; tin tức dài thuận lợi hơn |
| M4 | Accuracy ~99% hay ~75%? | [3] 99,75%, [2] 98,6% | [4] F1 0,749 | Số lớp, độ chồng lấn, giao thức, và khả năng rò rỉ ([3]) |
| M5 | Trans2Vec có phải SOTA trên Snippets? | [13]: tốt nhất trong các baseline của bài | S18 đạt 82,18% > 79,05% | [13] chỉ so với baseline không giám sát và không dùng dữ liệu ngoài |

---

## 8. Hạn chế của Trans2Vec × giải pháp × tài liệu (→ Chương 5.5, 9)

| Hạn chế | Giải pháp đề xuất | Cơ sở tài liệu | Cách kiểm chứng (GĐ6) |
|---|---|---|---|
| **H1** Mất thứ tự, tần suất | (a) Sqn2Vec (mẫu tuần tự có gap); (b) nối thêm TF-IDF; (c) FI trên cửa sổ câu | S01; [1] (n-gram giữ thứ tự cục bộ) | Ablation JOI so với JOI + TF-IDF so với Sqn2Vec |
| **H2** Bùng nổ FI với bài dài | Top-k từ (TF-IDF / TextRank, k ≈ 50); closed / maximal FI; item = thực thể có tên; giới hạn \|X\| ≤ 3; k-core | [3], [5], S07, S08, S11, S04 | Số FI và thời gian theo δ, k; accuracy theo k |
| **H3** Baseline yếu | Thêm Doc2Vec PV-DM, LDA + MaxEnt, Top2Vec, MLP-128 [7], PhoBERT | S18, S19, [7], S23 | Bảng thực nghiệm chính |
| **H4** Hiệu quả phụ thuộc dữ liệu | Thử cả benchmark dễ (VNTC-10) và khó (VNTC-27 / tự crawl ≥ 25 lớp) | [1], [4] | So Δ giữa hai mức độ khó |
| **H5** Không có suy luận cho tài liệu mới hoặc query | `infer_vector` của PV-DBOW; query không có FI thì chỉ dùng phần item; mở rộng query bằng fastText | S15, S17, [9] (fastText cc.vi) | Đo P@k, nDCG khi có và không có FI trong query |
| **H6** Chỉ đánh giá phân loại | Thêm đánh giá **tìm kiếm** (P@k, MAP, nDCG) và **phân cụm** (NMI, ARI); FI làm nhãn chủ đề diễn giải được (C_v) | S10, S26, [10] | Bảng tìm kiếm và phân cụm |
| **H7** Không báo chi phí | Đo theo mẫu [4], [10] | [4], [10] | Bảng chi phí |

---

## 9. Trả lời sơ bộ các câu hỏi nghiên cứu (khung kết luận cho GĐ5)

| RQ | Trả lời sơ bộ từ tài liệu | Mức chắc chắn | Còn mở |
|---|---|---|---|
| **RQ1** Thách thức tiền xử lý tiếng Việt | Tách từ (nhập nhằng: "luật gia cầm cự" [1], "học sinh ra" [2], "bảo lãnh bằng chứng khoán" [3]); bảng mã và dấu thanh [2]; stopword chủ quan [3]. **Tầm quan trọng phụ thuộc họ biểu diễn** (Bảng 5) | Cao | Ảnh hưởng lên Trans2Vec |
| **RQ2** So sánh các họ biểu diễn | Sparse + chọn đặc trưng đủ tốt cho tác vụ dễ (> 95%). Biểu diễn dày (C, D2, E, F) tạo khác biệt ở tác vụ khó. Tri thức ngoài (F) mạnh nhất nhưng đắt (Bảng 4.1) | TB–Cao | Thiếu bảng đối đầu trên cùng corpus tin tức VN |
| **RQ3** FI có làm giàu embedding? Trans2Vec cần gì cho tin tức VN | **Có**, +2,7 điểm so với embedding item ([13]). Cần giải H2 (bùng nổ FI) và H5 (query) trước khi dùng cho tin tức | **Thấp–TB**: bằng chứng duy nhất là [13], dữ liệu tiếng Anh, transaction ngắn | **Toàn bộ trên tiếng Việt**, chính là đóng góp của đề tài |
| **RQ4** Bộ phân loại và chi phí | SVM là chuẩn so sánh; LR là lựa chọn triển khai (gần bằng SVM, nhanh hơn nhiều); kNN kém nên tìm kiếm cần embedding sạch | Cao | Chi phí khai phá FI trên tin tức |
| **RQ5** Dataset và giao thức | Phân mảnh: 6 corpus tin tức VN, chỉ VNTC công khai; giao thức và độ đo không thống nhất; có rủi ro rò rỉ ([3]) và lỗi tái lập ([8]). **Đề xuất giao thức chuẩn:** VNTC với split cố định, Macro-F1 ± std, fit mọi thứ chỉ trên train | Cao | — |

---

## 10. Phát biểu khoảng trống nghiên cứu (bản chốt, → Chương 1, 9)

> Phân loại chuyên mục tin tức tiếng Việt đã được nghiên cứu theo ba thế hệ biểu diễn: thưa và chọn đặc trưng ([1], [2], [3], [4], [5]), dày học có giám sát hoặc embedding tĩnh ([7], [8]), và Transformer pretrained ([6], [9], [10]). Song song, khai phá tập phổ biến đã được dùng cho văn bản, kể cả tiếng Việt, nhưng chỉ làm đặc trưng hoặc luật (S09, S10, S12).
>
> **Hướng *học embedding từ tập phổ biến* (Trans2Vec [13] và họ phương pháp S01–S03) chưa được áp dụng cho văn bản tiếng Việt, chưa được thử trên văn bản dài như tin tức, và chưa được dùng cho tìm kiếm.**
>
> Hướng này đặc biệt phù hợp với tiếng Việt, vì tập phổ biến có tiềm năng nắm bắt *từ ghép và cụm đồng xuất hiện* mà không cần bộ tách từ hoàn hảo. Nó cũng phù hợp với một hệ thống thực tế, vì không giám sát, chạy trên CPU, và cho ra một vector dùng chung cho phân loại và tìm kiếm.

**Ba đóng góp mà survey sẽ đề xuất:**
1. Hệ thống hóa ba thế hệ biểu diễn và mô thức pattern-based embedding cho tiếng Việt.
2. Phân tích hạn chế H1–H7 của Trans2Vec khi áp dụng cho tin tức, kèm giải pháp có cơ sở tài liệu (Bảng 8).
3. Đề xuất kiến trúc tìm kiếm và phân loại cùng giao thức đánh giá chuẩn hóa (Bảng 9, RQ5).

---

## 11. Ánh xạ bảng → chương survey (cho GĐ5)

| Chương | Dùng bảng / mục |
|---|---|
| 1. Giới thiệu | §10 |
| 2. Đặc thù tiếng Việt | §5, RQ1 (§9) |
| 3. Nền tảng (FI, PV-DBOW) | S05–S08, S15–S16; phiếu [13] §3 |
| 4. Tiến hóa biểu diễn | §1, §2 |
| 5. Trans2Vec | phiếu [13]; §4 nhóm G4; §8 |
| 6. Bộ phân loại và chi phí | §6 |
| 7. Dataset và giao thức | §3; RQ5 |
| 8. So sánh và thảo luận | §4, §4.1, §7 |
| 9. Đề xuất hệ thống | §8, §10; Mục 6 của kế hoạch |
| 10. Kết luận | §9 |
