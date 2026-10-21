# Phiếu đọc (Reading Cards) — GĐ2

Mỗi phiếu có cấu trúc thống nhất: **Thông tin thư mục (IEEE) → Bài toán → Phương pháp → Dữ liệu & kết quả → Hạn chế/phản biện → Liên hệ với Trans2Vec → Ý dùng trong survey.**

| Số | Phiếu | Nhánh taxonomy | Liên quan | Một dòng tóm tắt |
|---|---|---|---|---|
| [13] | [13_trans2vec_nguyen2018.md](13_trans2vec_nguyen2018.md) | E | ★★★★★ lõi | Item + Frequent Itemset → PV-DBOW, không giám sát; JOI tốt nhất; hạn chế H1–H7 |
| [1] | [01_comparative_hoang2007.md](01_comparative_hoang2007.md) | A1, A2, B1 | ★★★★★ | Corpus VNTC 10/27 chủ đề; SVM 96,21% ≈ N-gram âm tiết 95,58%; OCFS tốt nhất |
| [2] | [02_syllable_nguyen2009.md](02_syllable_nguyen2009.md) | A1, B1, B2 | ★★★★ | Bag-of-syllables; bigram > unigram; >80% từ có 2 âm tiết; kNN nhạy nhiễu |
| [3] | [03_kebow_van2017.md](03_kebow_van2017.md) | B3 | ★★★★ | Top-10 từ khóa + MLP: 99,75%, **nghi rò rỉ dữ liệu** |
| [4] | [04_vnnews01_duong2019.md](04_vnnews01_duong2019.md) | A2 + bộ phân loại | ★★★★★ | VNNews-01 (25 lớp): SVM F1 chỉ 0,749; bảng thời gian |
| [5] | [05_textrank_huynh2020.md](05_textrank_huynh2020.md) | B3 | ★★★★ | Văn bản = tập từ khóa (TextRank) + Jaccard; bão hòa ở ~50 từ khóa |
| [6] | [06_roberta_hsd_pham2020.md](06_roberta_hsd_pham2020.md) | F | ★★ | PhoBERT + MLM miền + freeze/LR theo khối + label smoothing: F1 0,7221 |
| [7] | [07_nn_feature_vinh2021.md](07_nn_feature_vinh2021.md) | C | ★★★★★ | MLP trích 128 chiều + SVM > CHI/OCFS; **đối chứng trực tiếp nhất** |
| [8] | [08_wordvector_huong2022.md](08_wordvector_huong2022.md) | D1, D2 | ★★★★ | TF-IDF thắng; W2V/Doc2Vec ≈ 50%, **nhiều khả năng lỗi cài đặt** |
| [9] | [09_eda_bertology_luu2024.md](09_eda_bertology_luu2024.md) | F + tiền xử lý | ★★ | Tiền xử lý không giúp BERT (trừ tách từ cho PhoBERT); EDA + fastText |
| [10] | [10_phobert_topic_nguyen2025.md](10_phobert_topic_nguyen2025.md) | D1, D3, F | ★★★ | PhoBERT + LR F1 0,96; Top2Vec coherence kém; bảng chi phí |

**Tài liệu bổ sung (GĐ3):** [supplementary.md](supplementary.md), gồm 27 tài liệu S01–S27 đã xác minh, chia 7 nhóm.

## Các mạch xuyên suốt rút ra từ phiếu đọc (đầu vào cho GĐ4)

1. **Tính so sánh được:** cùng là "tin tức tiếng Việt" nhưng kết quả dao động từ 0,749 ([4]) đến 99,75% ([3]). Độ khó corpus và giao thức đánh giá chi phối kết quả.
2. **Tách từ:** tránh tách từ bằng âm tiết/n-gram ([1], [2], [7]) đối lập với bắt buộc tách từ ([3], [6], [9] cho PhoBERT). Từ đây có giả thuyết Trans2Vec trên âm tiết.
3. **Văn bản như một tập hợp:** [5] (Jaccard trên tập từ khóa), [3] (top-k từ khóa) dẫn tới [13] (transaction + FI).
4. **Embedding tĩnh và TF-IDF:** [8], [10] cho thấy TF-IDF thắng trên văn bản ngắn; [13] cho thấy PV-DBOW thắng trên Snippets. Cần kiểm chứng trên tin tức dài.
5. **Có giám sát và không giám sát:** [7] (có giám sát, 128 chiều) so với [13] (không giám sát, 128 chiều).
6. **Chi phí:** [4], [10] có bảng thời gian; [13] không có (H7).
7. **Rò rỉ và tái lập:** [3] (từ điển trên toàn corpus), [8] (thiếu siêu tham số).

## Bổ sung GĐ8 (18/10/2026): 8 bài trong `sources/papers/Paper_KDD_Data/`

Mã tạm **K + tên file**, theo kế hoạch `KE_HOACH_SURVEY_v3.md`. Vai trò: R1 nền tảng KDD · R2 bằng chứng tiếng Việt · R3 đối chứng hiện đại · R4 khung tham chiếu (survey). `30.pdf` trùng `31.pdf`.

| Mã | Phiếu | Bước đường ống | Vai trò | Nhánh | Liên quan | Một dòng tóm tắt |
|---|---|---|---|---|---|---|
| K25 | [K25_closedfi_zhang2025.md](K25_closedfi_zhang2025.md) | (3) FIM | R1 | E3 | ★★★★★ | CFI nén không mất thông tin; CICFI lọc FI theo khoảng tin cậy; giải thích lý thuyết cho ablation A3 |
| K26 | [K26_fim_heterogeneity_trasierras2024.md](K26_fim_heterogeneity_trasierras2024.md) | (3) FIM | R1 | E3 | ★★★★★ | 8 độ đo hồ sơ dữ liệu giao dịch; δ làm đổi đặc trưng dữ liệu; LCM/FP-Growth tốt nhất; bùng nổ chưa giải được |
| K27 | [K27_dl_vntc_hien2024.md](K27_dl_vntc_hien2024.md) | (5a) phân loại | R2 | A2, B, C | ★★★★★ | VNTC 2024: SVM+TF-IDF 93,60 (< 96,21 của [1]); "LSTM" chạy trên vector túi từ |
| K21 | [K21_vnlp_le2013.md](K21_vnlp_le2013.md) | (1) tiền xử lý | R2 | – | ★★★ | vnTokenizer tăng tốc (~440 bài/s); NER F1 0,58, nên công cụ NLP sâu cho tiếng Việt còn yếu |
| K29 | [K29_llmembed_liu2024.md](K29_llmembed_liu2024.md) | (4), (5a/b) | R3 | F2 | ★★★★ | LLaMA2 đóng băng + bộ phân loại nhẹ: 0,962, chi phí ~1,5%; co-occurrence pooling song song với FI |
| K30 | [K30_hiergraph_onan2023.md](K30_hiergraph_onan2023.md) | (5a) | R3 | G | ★★★ | Đồ thị phân cấp + BERT; baseline lệch công bố gốc (TextGCN chênh tới 11 điểm) |
| K05 | [K05_survey_li2022.md](K05_survey_li2022.md) | khung | R4 | – | ★★★★ | Taxonomy truyền thống → DL, dataset, độ đo, thách thức; không có pattern-based (khoảng trống) |
| K06 | [K06_survey_minaee2021.md](K06_survey_minaee2021.md) | khung | R4 | – | ★★★★ | 150 mô hình DL, dataset tin tức, công thức 5 bước; PV trên WikiQA chỉ đạt MAP 0,511 |

### Mạch xuyên suốt mới (đầu vào cho GĐ9)
8. **FIM có cơ sở:** K25 (loại FI nào: closed/ổn định) và K26 (thuật toán nào, hồ sơ dữ liệu ra sao) lấp phần mỏng nhất của đường ống ở v2. A3 và A2 của GĐ6 đã có bằng chứng thực nghiệm khớp với cả hai.
9. **Tương tác bậc cao: ký hiệu và tiềm ẩn:** FI ([13]) so với co-occurrence pooling (K29) và cạnh PMI (TextGCN, K30).
10. **Baseline và tái lập:** K30 (TextGCN lệch nhau giữa các nguồn), K29 (RoBERTa R52 = tỉ lệ lớp đa số), K27 (VNTC lệch [1] 2,6 điểm), K05 (chép số Paragraph Vector không cảnh báo), cộng với E7 của nhóm.
11. **Tìm kiếm cần đánh giá thật:** K06 (PV MAP 0,511 trên WikiQA) so với proxy "cùng chuyên mục" của nhóm, dẫn tới RQ6.
12. **Khoảng trống được xác nhận:** cả K05 và K06 đều không có nhánh pattern-based embedding.
