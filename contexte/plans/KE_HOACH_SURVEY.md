# KẾ HOẠCH THỰC HIỆN SURVEY

**Đề tài:** Hệ thống tìm kiếm & phân loại chuyên mục tin tức tiếng Việt với biểu diễn Trans2Vec
**Nguồn tài liệu hiện có:** `DocumentsSurvey/` (11 bài báo)
**Trạng thái:** v2 · GĐ2–GĐ7 ✅ (GĐ6: thực nghiệm VNTC-10, `experiments/RESULTS.md`, đã đưa vào survey Mục 9.5) · Thư mục: đã bổ sung 5/5 (08/10), riêng Đỗ Phúc 2006 còn thiếu trang cuối
**Ngày lập:** 07/10/2026

> **Thay đổi so với v1:** đã xác định "Tran2Vec" là **Trans2Vec** (Nguyen D., Nguyen T.D., Luo, Venkatesh — *Trans2Vec: Learning Transaction Embedding via Items and Frequent Itemsets*, PAKDD 2018, LNAI 10939, tr. 361–372), file `[13] Tran2Vec-nguyen2018.pdf`. Bỏ giả định Top2Vec. Top2Vec/BERTopic chuyển xuống vai trò phương pháp liên quan để so sánh.

### Danh mục tài liệu (đánh số theo năm công bố; số trong ngoặc vuông là tiền tố tên file trong `DocumentsSurvey/`)

| Số | Tên file | Tác giả đầu, năm | Venue |
|---|---|---|---|
| [1] | `[1] VN-TextClassification-Comparative-hoang2007.pdf` | Hoang V.C.D., 2007 | RIVF |
| [2] | `[2] VN-TextCategorization-Syllable-nguyen2009.pdf` | Nguyen G.S., 2009 | WI-IAT |
| [3] | `[3] VN-NewsClassification-KEBoW-NN-van2017.pdf` | Pham Van T., 2017 | IES |
| [4] | `[4] VNNews01-MultipleClassifier-duong2019.pdf` | Duong H.T., 2019 | KST |
| [5] | `[5] VN-KeywordsClassification-TextRank-huynh2020.pdf` | Huynh H.T., 2020 | IEEE RIVF |
| [6] | `[6] RoBERTa-VN-HateSpeech-pham2020.pdf` | Pham Q.H., 2020 | KSE |
| [7] | `[7] NN-FeatureExtraction-VN-TC-vinh2021.pdf` | To N.P. Vinh, 2021 | ISEE |
| [8] | `[8] WordVector-VN-Sentiment-huong2022.pdf` | Ho Huong T., 2022 | NICS |
| [9] | `[9] DataAugmentation-BERTology-VN-HSD-luu2024.pdf` | Luu S.T., 2024 | MTAP |
| [10] | `[10] PhoBERT-TopicClassification-Shopee-nguyen2025.pdf` | Nguyen T.D., 2025 | J. Marketing Analytics |
| [11], [12] | *(để trống, dành cho tài liệu bổ sung)* | | |
| [13] | `[13] Tran2Vec-nguyen2018.pdf` | Nguyen D., 2018 | PAKDD (**phương pháp lõi**) |

---

## 0. Trans2Vec là gì và vì sao hợp với đề tài

**Tóm tắt phương pháp:**
- Coi mỗi **transaction** là một *tập* item. Áp vào đề tài: **một bài báo là một transaction, các từ (sau khi tách từ) là các item**.
- Khai phá **tập phổ biến (Frequent Itemsets — FI)** với ngưỡng support tối thiểu δ. δ được chọn bằng **phương pháp elbow**, không cần nhãn.
- Học vector *d* = 128 chiều cho mỗi transaction theo mô hình **PV-DBOW** (Doc2Vec), có negative sampling:
  - **TRANS-IT:** học từ các item đơn lẻ (về bản chất là Doc2Vec PV-DBOW).
  - **TRANS-FI:** học từ các FI.
  - **Trans2Vec-IND:** học riêng hai vector trên rồi lấy trung bình.
  - **Trans2Vec-JOI:** học đồng thời trên tập "pattern" = item ∪ FI. Đây là biến thể tốt nhất.
- Hoàn toàn **không giám sát**. Vector học xong được đưa vào **SVM tuyến tính (C = 1)** để phân loại.
- **Kết quả** trên 4 bộ dữ liệu (Snippets, Cancer, Retail, Food): JOI > IND > TRANS-FI > TRANS-IT > TF-IDF/BOW/FI-BIN/FI-SUP. Accuracy hơn BOW 4–19% và hơn TF-IDF 2–13%. Trên **Snippets** (đoạn trích kết quả tìm kiếm web, 8 chuyên mục, dạng văn bản): AC 79,05 / F1 78,31, so với TF-IDF 70,26 / 69,52.

**Vì sao hợp với đề tài:**
1. **Gắn trực tiếp với môn "Tri thức dữ liệu" (KDD).** Phương pháp kết hợp khai phá luật kết hợp/tập phổ biến (Apriori, FP-Growth) với học biểu diễn (embedding).
2. **Một vector dùng cho hai việc.** Phân loại: vector → SVM/LR. Tìm kiếm: query → suy luận vector → cosine top-k.
3. **Hợp với đặc thù tiếng Việt.** FI tự nắm được **cụm từ đồng xuất hiện**, ví dụ {chứng_khoán, cổ_phiếu, sàn}. Nếu chạy trên âm tiết, FI còn có thể **khôi phục từ ghép** như {chứng, khoán}. Đây là hướng bỏ qua bước tách từ, giống lập luận n-gram của [1]/[2].
4. **Có khoảng trống rõ ràng.** Chưa có công bố nào áp dụng Trans2Vec cho văn bản tiếng Việt hoặc cho tin tức dài.

---

## 1. Mục tiêu và câu hỏi nghiên cứu (RQ)

**Mục tiêu survey:** hệ thống hóa sự tiến hóa của **biểu diễn văn bản** cho phân loại văn bản tiếng Việt, từ BoW/n-gram đến embedding. Từ đó lập luận rằng **biểu diễn kết hợp tập phổ biến + embedding (Trans2Vec)** là một lựa chọn có cơ sở cho hệ thống *tìm kiếm + phân loại chuyên mục* tin tức tiếng Việt.

| RQ | Câu hỏi | Bài trả lời chính |
|---|---|---|
| RQ1 | Tiếng Việt đặt ra thách thức tiền xử lý nào (tách từ, dấu thanh, mã hóa, stopword), và chúng ảnh hưởng tới kết quả ra sao? | [1], [2], [3], [9] |
| RQ2 | Các họ biểu diễn văn bản (sparse → chọn đặc trưng/từ khóa → dense học từ NN → embedding không giám sát → contextual) so sánh với nhau thế nào trên tiếng Việt? | [1], [2], [5], [7], [8], [10] |
| RQ3 | **Tri thức đồng xuất hiện (FI / từ khóa) có làm giàu được embedding tài liệu không? Trans2Vec cần điều chỉnh gì để dùng cho tin tức tiếng Việt?** | **[13]**, [3], [5], [2] |
| RQ4 | Bộ phân loại nào phù hợp với từng loại biểu diễn, và chi phí tính toán đổi lại được gì? | [1], [4], [7], [10], [13] |
| RQ5 | Dataset và giao thức đánh giá hiện có có đủ chuẩn để so sánh công bằng không? | Tất cả |

---

## 2. Review và đánh giá nhanh 11 bài báo

### 2.1 Bảng tổng hợp

| Mã | Bài báo (năm, venue) | Tác vụ / Dữ liệu | Biểu diễn | Bộ phân loại | Kết quả chính | Mức liên quan |
|---|---|---|---|---|---|---|
| **[13]** | **Nguyen D. et al., *Trans2Vec: Learning Transaction Embedding via Items and Frequent Itemsets* (2018, PAKDD)** | 4 bộ transaction: Snippets (12.340, 8 lớp, *văn bản*), Cancer, Retail, Food | **Item + Frequent Itemset → PV-DBOW embedding (d = 128)**, δ chọn bằng elbow | SVM tuyến tính, C = 1 | JOI tốt nhất trên cả 4 bộ; Snippets: AC 79,05 so với TF-IDF 70,26 | ★★★★★ **(phương pháp lõi)** |
| **[1]** | Hoang V.C.D. et al., *A Comparative Study on Vietnamese Text Classification Methods* (2007, RIVF) | Tin tức 4 báo. Level 1: 10 chủ đề (33.759 train / 50.373 test). Level 2: 27 chủ đề | BoW + TF-IDF + chọn đặc trưng (MI, IG, CHI, GSS, OR, **OCFS**); n-gram LM theo âm tiết | SVM, kNN, NB trên n-gram | SVM ≈ 96,21%, N-gram ≈ 95,58%; OCFS tốt nhất | ★★★★★ (corpus nền tảng, sau này được biết tới là **VNTC**) |
| **[2]** | Nguyen G.S., Gao, Andreae, *Text Categorization for Vietnamese Documents* (2009, WI-IAT) | D1: 4 chủ đề (~16k); D2: 1.743 bài, 2 lớp theo thể loại | Bag-of-syllables uni/bigram, lọc bằng từ điển, InfoGain | NB, kNN, SVM (4 kernel) | Bigram > unigram (98,6%); D2 ~89,8%; IG giảm 300K → ~1K đặc trưng | ★★★★ |
| **[3]** | Pham Van T., Ta Minh T., *Vietnamese News Classification based on BoW with Keywords Extraction and NN* (2017, IES) | Corpus của [1] | **KEBoW** (KeywordScore, top-10), vnTokenizer | SVM, RF, SVC, MLP 6 lớp | NN 99,75% (10 chủ đề), 99,69% (27 chủ đề) | ★★★★ |
| **[4]** | Duong H.T., Hoang V.T., *A survey on the multiple classifier for new benchmark dataset of Vietnamese news classification* (2019, KST) | **VNNews-01**: 37.500 bài, 25 chuyên mục | TF-IDF (có tách từ) | kNN, NB, LR, CART, RF, SVM, OVO, OVA | SVM-RBF F1 = **0,749**; kNN 0,50; có đo thời gian | ★★★★★ (benchmark khó) |
| **[5]** | Huynh H.T. et al., *Automatic Keywords-based Classification of Vietnamese Texts* (~2019–2020, IEEE; cần xác minh venue) | 4.500 bài, 15 chủ đề | Từ khóa **TextRank** | Đối sánh **Jaccard** có trọng số | 10 từ khóa: 75,27%; toàn bộ: 95,40% | ★★★★ (lọc item trước khi khai phá FI) |
| **[6]** | Pham Q.H. et al., *From Universal Language Model to Downstream Task: Improving RoBERTa-Based Vietnamese HSD* (2020, KSE) | VLSP 2019 HSD | PhoBERT + tiếp tục MLM trên dữ liệu miền | FC head; đóng băng tầng, LR theo khối, label smoothing | Macro-F1 0,7221 | ★★ (trần trên để tham chiếu) |
| **[7]** | Vinh T.N.P., Kha H.H., *Feature Extraction Using Neural Networks for Vietnamese Text Classification* (2021, ISEE) | 68.363 bài, 30 chuyên mục | Uni+bigram → TF-IDF 10k → **MLP trích đặc trưng 128 chiều** | SVM (OVO/OVR) | Vượt CHI và OCFS ở cùng 128 chiều; ~90,6% | ★★★★★ (đối chứng trực tiếp: cũng 128 chiều + SVM) |
| **[8]** | Huong T.H. et al., *Sentiment Analysis based on word vector representation for short comments in Vietnamese* (2022, NICS) | Cảm xúc (30k & 10k, 2 lớp) | TF-IDF, Word2Vec, GloVe, **Doc2Vec** | LR, NB, 1-NN, RF, SVM | TF-IDF ~86,8%; **W2V/Doc2Vec ≈ 50%** | ★★★★ (Trans2Vec xây trên PV-DBOW) |
| **[9]** | Luu S.T. et al., *Data augmentation … BERTology models for Vietnamese HSD* (2024, MTAP) | ViHSD, UIT-ViCTSD | mBERT, XLM-R, PhoBERT, … | Fine-tune, EDA, Focal loss | Tiền xử lý không giúp BERTology; tách từ vẫn giúp PhoBERT (~+2 F1) | ★★ |
| **[10]** | Nguyen T.D. et al., *Topic classification of Vietnamese product reviews in e-commerce using PhoBERT* (2025, J. Marketing Analytics) | 17.002 review Shopee, 5 chủ đề, đa nhãn | LDA/Top2Vec/BERTopic; BoW, TF-IDF, W2V, PhoBERT | LR, SVM, XGB, NB + BR/CC | PhoBERT + LR F1 0,96; có bảng chi phí tính toán | ★★★ |

### 2.2 Đánh giá phản biện riêng về Trans2Vec ([13])

**Điểm mạnh:**
- Ý tưởng gọn: thêm FI vào "từ vựng" của PV-DBOW, nên tri thức đồng xuất hiện bậc cao được đưa vào embedding.
- Không giám sát. Chọn δ bằng elbow, không dùng nhãn, nên không rò rỉ nhãn.
- Có ablation rõ ràng: IT, FI, IND, JOI. Cùng tập train/test cho mọi phương pháp, lặp 10 lần.

**Hạn chế (cần đưa vào survey):**
1. **Transaction là *tập*, nên mất tần suất từ và thứ tự từ.** Tin tức dài, TF mang thông tin, nên đây là điểm phải đánh giá thực nghiệm.
2. **Độ dài transaction trong bài rất ngắn** (trung bình 6–27 item). Một bài báo tiếng Việt có hàng trăm từ, nên số FI tăng tổ hợp khi δ nhỏ. **Cần chiến lược giới hạn:** chỉ giữ top-k từ theo TF-IDF/TextRank mỗi bài (nối với [3]/[5]); dùng closed/maximal itemsets; giới hạn độ dài itemset 2–3; hoặc chia transaction theo câu/đoạn.
3. **Baseline yếu và đã cũ:** không có LDA, Doc2Vec PV-DM, fastText, BERT; không tối ưu C của SVM; không báo độ lệch chuẩn ("< 10⁻²").
4. **Mức cải thiện nhỏ trên một số bộ**: Cancer ~50% cho mọi phương pháp. Hiệu quả chủ yếu thể hiện ở Snippets và Food.
5. **Suy luận cho tài liệu mới hoặc query** (cần cho tìm kiếm) không được mô tả. PV-DBOW cần một bước *infer* bằng gradient cho tài liệu mới; query ngắn có thể không chứa FI nào, khi đó vector FI là vector 0, như bài đã tự thừa nhận.
6. **Chưa có thực nghiệm clustering hay retrieval**, chỉ có phân loại. Phần "tìm kiếm" của đề tài là **đóng góp mới**.

**Liên hệ với các bài tiếng Việt:**
- **[8] cho Doc2Vec ≈ 50%**, trong khi [13] cho TRANS-IT (bản chất là PV-DBOW) chạy tốt trên Snippets, vốn là văn bản ngắn. Điều này củng cố nhận định rằng kết quả của [8] nhiều khả năng do lỗi cài đặt hoặc thiếu dữ liệu, không phải giới hạn của PV-DBOW. Survey nên nêu đối chiếu này.
- **[7]** cũng tạo vector 128 chiều rồi đưa vào SVM, nên là **đối chứng công bằng nhất** (cùng số chiều, cùng bộ phân loại). Khác biệt: [7] có giám sát, Trans2Vec không giám sát.
- **[1]/[2]:** n-gram âm tiết tránh được tách từ. Trans2Vec trên âm tiết, với FI đóng vai "n-gram không cần liền kề", là giả thuyết đáng kiểm chứng.
- **[3]/[5]:** trích từ khóa có thể dùng làm **bước lọc item** trước khi khai phá FI, giải quyết hạn chế #2.

### 2.3 Đánh giá phản biện chung (giữ từ v1)

1. **Kết quả giữa các bài không so sánh trực tiếp được** (khác corpus, cách chia dữ liệu, độ đo). Các bài báo trên 95% ([1]/[2]/[3]/[5]) nằm cạnh F1 0,749 của [4]. Độ khó của corpus chi phối kết quả nhiều hơn thuật toán.
2. **[3] (99,75%) có nguy cơ rò rỉ dữ liệu**: từ điển từ khóa được xây "in all documents of our corpus".
3. **Tách từ là "con dao hai lưỡi"**: n-gram âm tiết ([1]/[2]) so với tách từ ([3], [9], PhoBERT).
4. **Xu hướng biểu diễn:** sparse thủ công → chọn/trích đặc trưng → embedding → contextual. Trans2Vec nằm ở **giao điểm giữa khai phá mẫu (KDD cổ điển) và embedding**, một vị trí chưa bài tiếng Việt nào khai thác.
5. **Bài lệch miền ([6], [8], [9])** chỉ dùng ở vai trò "kỹ thuật chuyển giao được" hoặc tham chiếu, không đưa vào bảng so sánh kết quả tin tức.

---

## 3. Khung phân loại (taxonomy) đề xuất

```
Biểu diễn văn bản tiếng Việt cho phân loại / tìm kiếm
├── A. Biểu diễn thưa
│   ├── A1. Theo âm tiết: bag-of-syllables, n-gram LM .............. [1], [2]
│   └── A2. Theo từ: BoW, TF-IDF .................................... [1], [4], [7]
├── B. Giảm chiều / chọn đặc trưng
│   ├── B1. Thống kê: IG, CHI, MI, OR, GSS, OCFS .................... [1], [2]
│   ├── B2. Lọc bằng từ điển ........................................ [2]
│   └── B3. Trích từ khóa: KeywordScore, TextRank ................... [3], [5]
├── C. Biểu diễn dày học có giám sát (NN feature extractor) ......... [7]
├── D. Embedding không giám sát
│   ├── D1. Word-level: Word2Vec, GloVe ............................. [8], [10]
│   ├── D2. Document-level: Doc2Vec (PV-DM / PV-DBOW) ............... [8], ([13]: TRANS-IT)
│   └── D3. Topic-embedding: LDA, Top2Vec, BERTopic ................. [10]
├── E. ★ Embedding làm giàu bằng mẫu phổ biến (pattern-based) ← TRỌNG TÂM
│   ├── E1. FI làm đặc trưng trực tiếp: FI-BIN, FI-SUP .............. [13] (baseline)
│   └── E2. Trans2Vec: IND / JOI (item + FI → PV-DBOW) .............. [13]
└── F. Embedding ngữ cảnh pretrained: PhoBERT, XLM-R, … ............. [6], [9], [10]

Trục phụ: bộ phân loại · tiền xử lý tiếng Việt · độ đo · chi phí tính toán
```

---

## 4. Tài liệu cần bổ sung

| Nhóm | Tài liệu gợi ý (sẽ xác minh trước khi trích dẫn) | Lý do |
|---|---|---|
| Nền tảng của Trans2Vec | Le & Mikolov (2014) *Paragraph Vector*; Mikolov et al. (2013) *Word2Vec, negative sampling* | Mô hình lõi PV-DBOW |
| Khai phá tập phổ biến | Agrawal & Srikant (1994) *Apriori*; Han et al. (2000) *FP-Growth*; Fournier-Viger et al. (2017) *survey itemset mining*; closed/maximal itemsets | Bước khai phá FI, giới hạn bùng nổ FI |
| FI cho phân loại | Cheng et al. (2007) *Discriminative frequent pattern analysis*; Liu et al. (1998) *CBA*; Li et al. (2001) *CMAR* | Các hướng FI-based đi trước mà [13] so sánh |
| Chọn δ | Rousseau et al. (2015) *Text categorization as graph classification* (elbow) | Cơ sở chọn tham số |
| Dataset Snippets | Phan X.H., Nguyen L.M., Horiguchi (2008) *hidden topics*, WWW | Bộ văn bản duy nhất trong [13] |
| Hậu Trans2Vec | Các công trình tiếp nối hoặc trích dẫn Trans2Vec (sẽ tìm qua Google Scholar) | Kiểm tra trạng thái mới nhất của hướng này |
| Đối chứng hiện đại | Nguyen & Nguyen (2020) *PhoBERT*; Reimers & Gurevych (2019) *Sentence-BERT*; Angelov (2020) *Top2Vec* | Trần trên / phương pháp liên quan |
| Tìm kiếm ngữ nghĩa | Dense retrieval / semantic search (ví dụ DPR) | Hiện chưa có bài nào về "tìm kiếm" |
| Công cụ tiếng Việt | VnCoreNLP, pyvi, underthesea | Tách từ |
| Dataset tin tức | VNTC (corpus [1]), VNNews-01 ([4]) | Benchmark thực nghiệm |

---

## 5. Cấu trúc survey dự kiến (outline)

1. **Giới thiệu.** Bối cảnh; bài toán phân loại chuyên mục + tìm kiếm; đóng góp; RQ1–RQ5.
2. **Đặc thù xử lý tiếng Việt** (RQ1).
3. **Nền tảng.** Định nghĩa bài toán phân loại văn bản; **khai phá tập phổ biến** (support, Apriori/FP-Growth); **học biểu diễn** (Word2Vec, Doc2Vec PV-DBOW, negative sampling).
4. **Tiến hóa của biểu diễn văn bản tiếng Việt** (RQ2). Các nhánh A → D, F, mỗi nhánh gồm nguyên lý, bài tiêu biểu, ưu nhược điểm.
5. **Trans2Vec: biểu diễn làm giàu bằng mẫu phổ biến** (RQ3, chương lõi).
   - 5.1 Mô hình hóa văn bản thành transaction.
   - 5.2 TRANS-IT, TRANS-FI, IND, JOI: công thức (Eq. 3, 5, 8 của [13]).
   - 5.3 Chọn δ bằng elbow; độ nhạy theo δ và d.
   - 5.4 Kết quả gốc và đánh giá phản biện (Mục 2.2).
   - 5.5 Thách thức khi áp dụng cho tin tức tiếng Việt và hướng điều chỉnh.
6. **Bộ phân loại và đánh đổi hiệu năng/chi phí** (RQ4).
7. **Dataset và giao thức đánh giá** (RQ5).
8. **Bảng so sánh tổng hợp và thảo luận.**
9. **Đề xuất hệ thống tìm kiếm + phân loại chuyên mục dựa trên Trans2Vec** (Mục 6) và khoảng trống nghiên cứu.
10. **Kết luận và hướng phát triển.**
11. **Tài liệu tham khảo.**

---

## 6. Flow nghiên cứu đề xuất cho hệ thống

```
[Crawl tin tức theo chuyên mục] → [Chuẩn hóa Unicode NFC, dấu thanh, loại HTML]
   → [Tách từ: VnCoreNLP / pyvi]  (nhánh ablation: giữ nguyên âm tiết)
   → [Bỏ stopword] → [Lọc item: top-k theo TF-IDF hoặc TextRank mỗi bài]
   → [Mỗi bài = 1 transaction (tập từ)]
   → [Khai phá FI bằng FP-Growth trên TẬP TRAIN; δ chọn bằng elbow; độ dài itemset ≤ 3]
   → [Trans2Vec-JOI: PV-DBOW trên pattern = item ∪ FI, d = 128, negative sampling]
         ├── (1) PHÂN LOẠI: doc vector → SVM tuyến tính / LR → chuyên mục
         └── (2) TÌM KIẾM: query → tách từ → khớp item + FI → infer vector
                  → cosine top-k (có thể lọc theo chuyên mục dự đoán)
```

**Thiết kế thực nghiệm (nếu đề tài cần phần thực nghiệm):**

| Hạng mục | Nội dung |
|---|---|
| Dataset | VNTC (10 / 27 chủ đề) để so được với [1]/[3]; VNNews-01 hoặc corpus tự crawl (khó, giống [4]/[7]) |
| Baseline (theo [13]) | BOW, TF-IDF, FI-BIN, FI-SUP, TRANS-IT (= Doc2Vec PV-DBOW), TRANS-FI, Trans2Vec-IND, Trans2Vec-JOI |
| Baseline tiếng Việt bổ sung | TF-IDF + OCFS/CHI ([1]); MLP-128 + SVM ([7]); PhoBERT (trần trên, [10]) |
| Độ đo phân loại | Accuracy, **Macro-F1**; báo mean ± std qua nhiều lần chạy (khắc phục hạn chế #3 của [13]) |
| Độ đo tìm kiếm | Precision@k, MAP, nDCG@k, coi tài liệu cùng chuyên mục là "liên quan" (proxy) |
| Ablation | Từ và âm tiết; top-k item (k = 20/50/100/toàn bộ); δ; d ∈ {64, 128, 256}; độ dài itemset tối đa; closed và all FI |
| Chi phí | Số FI theo δ, thời gian khai phá FI, thời gian huấn luyện/suy luận, bộ nhớ |
| Kiểm soát rò rỉ | FI, vocabulary, embedding chỉ fit trên train; δ chọn không dùng nhãn |

---

## 7. Lộ trình thực hiện

| Giai đoạn | Công việc | Sản phẩm |
|---|---|---|
| **GĐ1** – Chốt phạm vi | Duyệt kế hoạch v2; chọn có/không thực nghiệm; ngôn ngữ trình bày, chuẩn trích dẫn | Kế hoạch đã duyệt |
| **GĐ2** – Phiếu đọc chi tiết | Mỗi bài 1 reading card: vấn đề, phương pháp, dữ liệu, kết quả, hạn chế, liên hệ với Trans2Vec. **Bắt đầu từ [13]** | ✅ `survey/notes/` (11 phiếu + README mục lục) |
| **GĐ3** – Bổ sung tài liệu | Tìm và xác minh các bài ở Mục 4, ưu tiên nhóm FI mining và các công trình hậu Trans2Vec | ✅ `survey/notes/supplementary.md` |
| **GĐ4** – Ma trận tổng hợp | Bảng taxonomy × bài, bảng dataset, bảng kết quả kèm chú thích tính so sánh được | ✅ `survey/synthesis.md` |
| **GĐ5** – Viết survey | Theo outline Mục 5; hình pipeline, sơ đồ taxonomy, sơ đồ Trans2Vec-IND/JOI | ✅ `survey/Survey_Trans2Vec_VN_News.md` (bản nháp 1; nguồn trong `survey/draft/`) (xuất .docx/.pdf nếu cần) |
| **GĐ6** – (Tùy chọn) Thực nghiệm | Notebook theo Mục 6 | ✅ `experiments/` (script + RESULTS.md) |
| **GĐ7** – Rà soát | Kiểm tra nhất quán số liệu, trích dẫn, lập luận | ✅ bản nháp 2 + `survey/review_log.md` |

---

## 8. Câu hỏi cần anh/chị quyết định

1. Sản phẩm cuối chỉ là **bài survey**, hay **survey + thực nghiệm Trans2Vec trên tin tức tiếng Việt** (GĐ6)?
2. Số **[11]** và **[12]** đang để trống (Trans2Vec giữ số [13] như anh/chị đặt). Anh/chị định thêm 2 bài nữa, hay muốn đổi Trans2Vec thành [11] cho liền mạch?
3. Ngôn ngữ trình bày: tiếng Việt toàn bộ hay kèm thuật ngữ tiếng Anh? Chuẩn trích dẫn: IEEE hay APA?
4. Định dạng nộp: Markdown, Word (.docx) hay LaTeX?
5. Có giới hạn số trang hoặc số tài liệu tham khảo không?
