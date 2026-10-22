# KẾ HOẠCH SURVEY v3: Tái cấu trúc quanh đề tài, bổ sung 8 bài trong `Paper_KDD_Data/`

**Đề tài:** Hệ thống tìm kiếm và phân loại chuyên mục tin tức tiếng Việt với biểu diễn Trans2Vec
**Ngày lập:** 18/10/2026 · **Trạng thái:** ✅ Q1 đã duyệt (18/10): tổ chức lại theo đường ống · ✅ GĐ8 xong (8 phiếu `contexte/survey-notes/K*.md`) · ✅ GĐ9 xong (22/10): `contexte/survey-notes/synthesis_v3.md` · ✅ Q2–Q5 chốt 22/10 (Mục 10): giữ mã K; không đổi tên PDF; chạy E8 + E9 bản sửa, bỏ E10; sửa thẳng `livrables/survey/draft/`.
**Quan hệ với bản cũ:** file này thay thế vai trò "kế hoạch đang dùng". `KE_HOACH_SURVEY.md` (v2) **giữ nguyên, không sửa**. Bản survey hiện tại (`livrables/survey/Survey_Trans2Vec_VN_News.docx`, build ngày 08/10) cũng giữ nguyên. Mọi thay đổi chỉ bắt đầu sau khi anh/chị duyệt bản này.

> **Liên kết (20/10):** hệ thống demo kết hợp môn *Hệ CSDL nâng cao* (MariaDB + Manticore Search) được lập kế hoạch riêng trong `KE_HOACH_HE_THONG_DB.md`. Hệ quả cho survey: RQ6 thêm baseline BM25 và hybrid; Chương 9 vẽ lại kiến trúc (xem Mục 6 của file đó).

> **Giả định và ghi chú khi đọc:**
> - `30.pdf` và `31.pdf` có **nội dung giống hệt nhau** (cùng bài Onan 2023, text trích ra trùng từng byte). Vì vậy thực tế có **8 bài mới**, không phải 9. Em đề nghị xóa một bản sau khi anh/chị xác nhận.
> - Em tạm đặt mã **K + tên file** (K05, K06, K21, K25, K26, K27, K29, K30) để không đụng hệ số [1]–[13] đang dùng. Cách đánh số chính thức nằm trong câu hỏi Q2 (Mục 8).
> - Em hiểu chỉ đạo "tập trung về đề tài, còn các bài survey để tham khảo và khảo sát" như sau: **trục của bài là hệ thống Trans2Vec cho tin tức tiếng Việt**. Hai bài survey lớn (K05, K06) chỉ đóng vai trò **khung tham chiếu**: mượn taxonomy, danh mục dataset/độ đo, cấu trúc trình bày và danh sách thách thức. Chúng **không** được đưa vào bảng so sánh kết quả như bằng chứng sơ cấp.

---

## 1. Định vị lại bài survey

**v2:** "Khảo sát tiến hóa biểu diễn văn bản tiếng Việt, rồi lập luận cho Trans2Vec". Phần tìm kiếm chỉ xuất hiện ở Chương 9.
**v3 (đề xuất):** "Khảo sát **các thành phần cần có để xây một hệ thống tìm kiếm và phân loại tin tức tiếng Việt dựa trên biểu diễn mẫu phổ biến (Trans2Vec)**". Mỗi chương trả lời một câu hỏi thiết kế của hệ thống:

```
 Tin tức thô ─► (1) Tiền xử lý TV ─► (2) Văn bản → transaction ─► (3) Khai phá FI ─► (4) Học embedding
                  [1][2][K21][K27]     [13][5][3]                   [K25][K26]+S..     [13][8]+PV-DBOW
                                                                                          │
                     ┌──────────────────────────────────────────────────────────────────────┤
                     ▼                                                                      ▼
             (5a) Phân loại chuyên mục                                     (5b) Tìm kiếm (query → vector → top-k)
             [1][4][7][K27][K29][K30]                                      [K06: PV trên WikiQA][K29][candidates]
                     └──────────────► (6) Dữ liệu và giao thức đánh giá ◄──────────────────────┘
                                         [1][4][K27][K05][K06][K30]
```

Lý do: khi tổ chức theo đường ống, mỗi bài được đặt đúng chỗ nó đóng góp. Hai bài FIM (K25, K26) trở thành cơ sở cho bước (3), bước mà v2 còn mỏng. Phần tìm kiếm trở thành câu hỏi nghiên cứu chính thức (RQ6) thay vì phụ lục cuối bài.

---

## 2. Vai trò của từng nhóm tài liệu

| Vai trò | Ý nghĩa | Tài liệu |
|---|---|---|
| **R0 – Lõi** | Phương pháp được khảo sát và đề xuất | [13] Trans2Vec |
| **R1 – Nền tảng KDD** | Cơ sở khai phá tập phổ biến cho bước (3) | **K25**, **K26**; S-Apriori/FP-Growth/LCM trong `supplementary.md` |
| **R2 – Bằng chứng tiếng Việt** | Kết quả và kinh nghiệm thực tế trên văn bản/tin tức TV | [1]–[5], [7], [8], [10], **K27**, **K21** |
| **R3 – Đối chứng hiện đại** | Trần trên và hướng cạnh tranh của Trans2Vec | [6], [9], [10] (PhoBERT), **K29** (LLM embedding), **K30** (đồ thị + BERT) |
| **R4 – Khung tham chiếu (survey)** | Mượn taxonomy, dataset, độ đo, thách thức; **không** dùng làm bằng chứng kết quả | **K05**, **K06** |

---

## 3. Phiếu đọc nhanh 8 bài mới (đánh giá dưới góc nhìn ML/KDD)

### 3.1 Bảng tổng hợp

| Mã | Bài báo | Venue | Nội dung chính | Số liệu then chốt | Vai trò | Liên quan |
|---|---|---|---|---|---|---|
| **K25** | Zhang H., Li H., Li Y., Teng G., Cao X., *Theoretical Properties of Closed Frequent Itemsets in Frequent Pattern Mining* | *Mathematics* (MDPI) 13(11):1709, 2025, doi:10.3390/math13111709 | Hệ thống hóa toán tử bao đóng; chứng minh tính chất của **CFI**; đề xuất **CICFI**: FI đóng kèm khoảng tin cậy của relative support (Wald / Wilson / Clopper–Pearson) | Thực nghiệm trên retail (88.162 giao dịch, 16.407 item, thưa) và mushroom (8.124 giao dịch, dày). Wilson cân bằng tốt nhất; Clopper–Pearson bảo thủ nhất | R1 | ★★★★★ |
| **K26** | Trasierras A.M., Luna J.M., Fournier-Viger P., Ventura S., *Data heterogeneity's impact on the performance of frequent itemset mining algorithms* | *Information Sciences* 678:120981, 2024, doi:10.1016/j.ins.2024.120981 | So sánh Apriori, Eclat, dEclat, FP-Growth, Relim, SaM, LCM v1–v3 trên 14 dataset; đề xuất **8 độ đo tính không đồng nhất** (density, similarity, item distribution, IT, IS, \|T\|, \|B\|, \|\|T\|\|) | Ngưỡng δ làm **thay đổi chính đặc trưng dữ liệu**: dataset thưa có thể thành dày. **LCMv3 và FP-Growth** thường tốt nhất. Các mở rộng (hypercube decomposition, k-items machine) quan trọng hơn bản thân thuật toán. Bùng nổ tổ hợp **vẫn chưa giải được** | R1 | ★★★★★ |
| **K27** | Hien N.T., Thoa B.T., Hoa L.N.H., *A study on deep learning for Vietnamese text classification* | *J. Military Science and Technology* 95:85–94, 2024, doi:10.54939/1859-1043.j.mst.95.2024.85-94 | BoW / TF-IDF (+SVD) → LR, DT, SVM, LSTM, CNN trên **VNTC** (cùng corpus với [1]); tách từ bằng vnTokenizer; danh sách khoảng 2.000 stopword | Level 1 (10 lớp): SVM+TF-IDF **93,60**, LSTM+BoW **94,52**. Level 2 (27 lớp): 89,35 / 89,43. Chỉ đo Accuracy | R2 | ★★★★★ |
| **K21** | Le N.M., Nguyen V.D., Do B.N., Nguyen T.D., *VNLP: An Open Source Framework for Vietnamese NLP* | SoICT 2013 (ACM) | Đường ống NLP TV trên GATE: vnTokenizer cải tiến, vnTagger, MaltParser, NER theo luật, coreference | Tách từ 2 triệu âm tiết trong 6 giây (bản gốc mất 234 giây). LAS 73%. NER F1 0,58 | R2 (tiền xử lý) | ★★★ |
| **K29** | Liu C., Zhang H., Zhao K., Ju X., Yang L., *LLMEmbed: Rethinking Lightweight LLM's Genuine Function in Text Classification* | ACL 2024 (Long), tr. 7994–8004 | **Đóng băng** LLaMA2-7B, lấy embedding trung bình ở 5 tầng cuối, ghép với BERT/RoBERTa và **co-occurrence pooling** (tích ngoài), rồi đưa vào bộ phân loại nhẹ | Accuracy trung bình 0,962 trên SST-2/MR/AGNews/R8/R52 (AGNews 0,958), ngang CARP+GPT-3 (0,952) nhưng chỉ tốn khoảng 1,5% thời gian và 1,8% điện năng | R3 | ★★★★ |
| **K30** (= 31) | Onan A., *Hierarchical graph-based text classification framework with contextual node embedding and BERT-based dynamic fusion* | *J. King Saud Univ. – CIS* 35:101610, 2023, doi:10.1016/j.jksuci.2023.101610 | 7 giai đoạn: đặc trưng ngôn ngữ (POS, dependency, NER, coref), đồ thị phân cấp có tri thức miền, GCN đa mức, DTW, attention, hợp nhất với BERT | Accuracy: 20NG 93,71; R8 98,75; R52 94,11; MR 89,30; Ohsumed 74,87 | R3 | ★★★ |
| **K05** | Li Q., Peng H., Li J., Xia C., Yang R., Sun L., Yu P.S., He L., *A Survey on Text Classification: From Traditional to Deep Learning* | *ACM TIST* 13(2), Art. 31, 2022, doi:10.1145/3495162 | Taxonomy truyền thống (PGM, KNN, SVM, DT, ensemble) → DL (ReNN, MLP, RNN, CNN, Attention, PLM, GNN); bảng dataset, độ đo đơn/đa nhãn, bảng kết quả; thách thức theo 3 góc: dữ liệu, mô hình, hiệu năng | Có Paragraph-Vec trong bảng kết quả; nêu thách thức "biểu diễn ngữ nghĩa *hiệu quả về chi phí*" và "tri thức ngoài" | R4 | ★★★★ (khung) |
| **K06** | Minaee S., Kalchbrenner N., Cambria E., Nikzad N., Chenaghlu M., Gao J., *Deep Learning–based Text Classification: A Comprehensive Review* | *ACM CSUR* 54(3), Art. 62, 2021, doi:10.1145/3439726 | Hơn 150 mô hình DL, hơn 40 dataset; **công thức 5 bước chọn mô hình** (chọn PLM → thích nghi miền → lớp đầu ra theo tác vụ → fine-tune → nén); mục riêng về dataset tin tức (AG News, 20NG, Sogou, Reuters) | AG News: fastText 92,50; XLNet 95,51. **Paragraph Vector trên WikiQA chỉ đạt MAP 0,511** so với BERT 0,813 | R4 | ★★★★ (khung) |

### 3.2 Đánh giá phản biện và cách dùng trong survey

**K25 – Closed FI và khoảng tin cậy (bài quan trọng nhất trong 8 bài)**
- *Đóng góp cho đề tài:*
  1. CFI là biểu diễn **nén và không mất thông tin** của toàn bộ FI. Đây là lời giải có cơ sở lý thuyết cho hạn chế H2 của [13] (bùng nổ FI khi tài liệu dài). v2 mới chỉ nêu "closed/maximal" như một gợi ý chưa có trích dẫn sơ cấp.
  2. **CICFI** mở ra một tiêu chí chọn FI thay cho elbow của [13]: chỉ giữ FI có support *ổn định*, tức CI hẹp. Điều này gắn trực tiếp với câu hỏi tổng quát hóa: FI khai phá trên tập train có còn phổ biến trên test và trên query không?
- *Hạn chế:* thực nghiệm nhỏ (2 dataset), không có tác vụ hạ nguồn nào. Đây là bài lý thuyết trên MDPI, nên dùng làm **cơ sở định nghĩa/tính chất**, không dùng làm bằng chứng hiệu quả.
- *Nhận định chuyên môn:* đưa CFI vào "từ vựng" của PV-DBOW còn **giảm tính đa cộng tuyến giữa các token FI**. Lý do: nhiều FI con có cùng tập giao dịch (cùng lớp tương đương) sẽ bị gộp làm một. Đây là giả thuyết mới **H8** có thể kiểm chứng (Mục 6, E9).

**K26 – Tính không đồng nhất của dữ liệu và thuật toán FIM**
- *Đóng góp cho đề tài:*
  1. Cung cấp **bộ 8 độ đo để mô tả corpus dưới dạng CSDL giao dịch**, tức "hồ sơ dữ liệu" của bước (3). Survey có thể lập bảng đặt **Snippets** (nơi FI giúp +3,8 theo bài báo) cạnh **VNTC** (nơi FI chỉ giúp −0,3 đến +0,9 trong E6) theo density, similarity và độ dài giao dịch. Từ đó có **giả thuyết giải thích** cho phát hiện chính của GĐ6 (E6/E7) thay vì chỉ ghi nhận.
  2. Lý do có trích dẫn để **chọn LCM hoặc FP-Growth** cho hệ thống (mã gốc dùng `FIM_Trans.exe`, chỉ chạy trên Windows).
  3. Kết luận "bùng nổ tổ hợp chưa giải được, cần top-k hoặc tóm tắt mẫu" củng cố lập luận H2 của v2.
- *Hạn chế:* chỉ đo **tốc độ** (số itemset/giây), không đánh giá chất lượng mẫu cho tác vụ hạ nguồn. Không có dataset văn bản (Retail và Kosarak là dữ liệu bán lẻ và clickstream).

**K27 – Học sâu cho phân loại văn bản TV (VNTC, 2024)**
- *Đóng góp cho đề tài:* đây là **baseline VNTC mới nhất** trong kho tài liệu, rất có giá trị khi đặt cạnh [1] (2007) và E1–E6 của nhóm.
  - SVM+TF-IDF đạt 93,60% ở K27, thấp hơn 96,21% ở [1] trên *cùng corpus*. Đây là thêm bằng chứng cho luận điểm "giao thức và tiền xử lý chi phối kết quả" (Mục 8.2 của survey).
  - Kết quả này nhất quán với TF-IDF Macro-F1 0,907 trong thực nghiệm của nhóm.
- *Phản biện (cần nêu trong survey):*
  1. Đầu vào của LSTM/CNN là **vector BoW/TF-IDF(+SVD)**, không phải chuỗi từ. Vì vậy mô hình gọi là "LSTM" không thực sự mô hình hóa thứ tự từ, và kết luận "DL tốt hơn" chưa thuyết phục. Mức chênh cũng chỉ +0,1 đến +2,7 điểm.
  2. Chỉ dùng Accuracy trên dữ liệu mất cân bằng, không báo độ lệch chuẩn.
  3. Số lượng Level 2 (14.375/12.076) khác với mô tả của [1]. Cần ghi chú khi so sánh.
- *Vị trí trong taxonomy:* nhánh C (dense có giám sát) và A2 (thưa).

**K21 – VNLP (2013)**
- *Đóng góp:* là nguồn trích dẫn cho **vnTokenizer**, công cụ tách từ mà [3] và K27 dùng. Cung cấp số liệu tốc độ tách từ (yếu tố chi phí của bước 1) và cho thấy các công cụ NLP sâu cho tiếng Việt yếu ở thời điểm đó (NER F1 0,58, LAS 73%).
- *Cách dùng:*
  - Chương 2 (tiền xử lý).
  - Làm **lập luận phản bác K30**: các khung cần POS, dependency, NER, coref sẽ bị **lan truyền lỗi** khi chuyển sang tiếng Việt.
  - Làm lập luận ủng hộ Trans2Vec: chỉ cần tách từ, hoặc thậm chí chỉ cần âm tiết.
- *Hạn chế:* đã cũ, bị VnCoreNLP, underthesea, pyvi thay thế. Chỉ dùng ở vai trò lịch sử và số liệu.

**K29 – LLMEmbed**
- *Đóng góp cho đề tài:*
  1. Hiện thân hiện đại của đúng mô thức Trans2Vec: **embedding không fine-tune + bộ phân loại tuyến tính/nhẹ**. Đây là **đối chứng có cùng "hình dạng pipeline"**, nên công bằng hơn so sánh với PhoBERT fine-tune.
  2. **Co-occurrence pooling** (tích ngoài) là tương tác bậc cao ở *không gian tiềm ẩn*, trong khi FI của Trans2Vec là tương tác bậc cao ở *không gian ký hiệu*. Đây là một trục so sánh khái niệm đáng viết (Mục 5.4 của survey: họ "mẫu + embedding").
  3. Có bảng chi phí (thời gian, kWh, $), bổ sung cho RQ4.
- *Phản biện:*
  - Cần GPU A100.
  - Chỉ thử trên tiếng Anh.
  - Baseline RoBERTa đạt 42,17% trên R52, cho thấy huấn luyện baseline có vấn đề.
  - Không báo độ lệch chuẩn.
  - Tác giả **tự thừa nhận yếu với văn bản dài**, mà tin tức tiếng Việt lại dài, nên không thể giả định kết quả chuyển sang được.
- *Hàm ý cho hệ thống:* biến thể khả thi trên CPU là embedding câu tiếng Việt đóng băng (BGE-M3, multilingual-e5, SimCSE-PhoBERT; xem `candidates.md`) kết hợp LR. Đây vừa là baseline cho phân loại, vừa là baseline cho tìm kiếm.

**K30 – Đồ thị phân cấp + BERT (Onan 2023)**
- *Đóng góp:* đại diện cho nhánh **GNN/đồ thị**, nhánh mà taxonomy v2 chưa có. TextGCN, TextING, HyperGAT được liệt kê đầy đủ. Đáng chú ý: TextGCN cũng là phương pháp **transductive** giống mã gốc Trans2Vec, nên có thể dùng để thảo luận bẫy đánh giá đã phát hiện ở E6.
- *Phản biện (mạnh):*
  1. Số liệu baseline **thấp bất thường so với công bố gốc**. Ví dụ TextGCN R8 = 86,07, trong khi Yao et al. 2019 báo 97,07; BERT R8 = 91,06, trong khi các tài liệu thường báo khoảng 98. Nghĩa là mức "vượt trội" có thể do **baseline yếu**. Đây là ví dụ điển hình cho Mục 8.2–8.4 (tính so sánh được, mối đe dọa đến tính hợp lệ).
  2. Pipeline 7 giai đoạn, không có mã nguồn, không báo chi phí.
  3. Phụ thuộc mạnh vào công cụ ngôn ngữ, nên khó chuyển sang tiếng Việt (xem K21).
- *Cách dùng:* chỉ dùng ở vai trò nhánh liên quan và ví dụ phản biện. **Không** đưa vào bảng kết quả tin tức.

**K05, K06 – Hai bài survey tham chiếu**
- *Dùng cho:*
  1. Kiểm tra độ phủ của taxonomy v2: bổ sung các nhánh RNN/CNN, GNN, LLM.
  2. Chuẩn hóa danh mục **dataset tin tức quốc tế** (AG News, 20NG, Sogou, Reuters R8/R52) để đặt dataset tiếng Việt vào bối cảnh. *Sogou News* là tiền lệ "tin tức ngôn ngữ không phân tách từ bằng khoảng trắng", gần với bài toán tách từ tiếng Việt.
  3. Chuẩn hóa định nghĩa độ đo đơn/đa nhãn (Mục 3.4 của survey).
  4. **Công thức 5 bước chọn mô hình của K06**, dùng làm khung lập luận cho chương đề xuất hệ thống: vì sao chọn Trans2Vec làm lõi và PhoBERT/LLM embedding làm trần trên.
  5. Danh sách thách thức (K05 Mục 5, K06 Mục 6) dùng để đối chiếu với các khoảng trống ở Mục 10.2 của survey.
- *Số liệu đáng trích:* K06 Bảng 4: **Paragraph Vector chỉ đạt MAP 0,511 trên WikiQA**, so với BERT 0,813. Đây là bằng chứng bên ngoài rằng embedding kiểu PV-DBOW yếu ở bài toán *khớp truy vấn và tài liệu*. Phát hiện này phải được đặt cạnh kết quả nDCG@10 của nhóm (JOI 0,809 > TF-IDF 0,740) và thảo luận vì sao khác nhau. Lý do: nhóm dùng *proxy cùng chuyên mục*, không phải nhãn liên quan thật. Đây là một điểm phản biện mới mà v2 chưa có.
- *Giới hạn:* cả hai bài dừng ở năm 2021–2022, chưa có LLM. K29 lấp chỗ này. Không bài nào nhắc tới biểu diễn dựa trên mẫu phổ biến. Đây là **bằng chứng cho khoảng trống** mà survey nhắm tới: hướng "pattern-based embedding" vắng mặt trong cả hai survey lớn.

---

## 4. Câu hỏi nghiên cứu v3

| RQ | Câu hỏi (gắn với bước của hệ thống) | Bài trả lời chính (bài mới **đậm**) |
|---|---|---|
| RQ1 | Tiền xử lý tiếng Việt (tách từ, chuẩn hóa, stopword) ảnh hưởng thế nào và tốn bao nhiêu chi phí? *(bước 1)* | [1], [2], [3], [9], **K21**, **K27** |
| RQ2 | Các họ biểu diễn so sánh với nhau thế nào trên tin tức tiếng Việt? *(bước 4)* | [1], [2], [5], [7], [8], [10], **K27**; khung: **K05**, **K06** |
| RQ3 | Tri thức đồng xuất hiện (FI) có làm giàu embedding không, và **nên khai phá loại FI nào** (all / closed / ổn định) với thuật toán nào? *(bước 2–4)* | **[13]**, **K25**, **K26**, [3], [5] |
| RQ4 | Bộ phân loại nào hợp với loại biểu diễn nào, và chi phí đổi lại được gì? *(bước 5a)* | [1], [4], [7], [10], [13], **K27**, **K29** |
| RQ5 | Dataset và giao thức hiện có có cho phép so sánh công bằng không? *(bước 6)* | Tất cả; ví dụ phản biện: **K27** (VNTC lệch [1]), **K30** (baseline yếu), **K29** (RoBERTa R52) |
| **RQ6 (mới)** | **Biểu diễn nào phục vụ được *đồng thời* phân loại và tìm kiếm, và đánh giá phần tìm kiếm thế nào cho đúng?** *(bước 5b)* | [13], **K06** (PV trên WikiQA), **K29**, `candidates.md` (benchmark truy hồi TV) |

---

## 5. Taxonomy v3 (bổ sung vào khung v2)

```
Biểu diễn văn bản cho phân loại và tìm kiếm tin tức tiếng Việt
├── A. Thưa: âm tiết [1][2] · từ, BoW/TF-IDF [1][4][7][K27]
├── B. Chọn/giảm chiều: thống kê [1][2] · từ khóa [3][5] · SVD [K27]
├── C. Dense có giám sát: MLP [7] · LSTM/CNN [K27]  (khung: K05 §2.2, K06 §2.1–2.3)
├── D. Embedding không giám sát: Word2Vec/GloVe [8][10] · Doc2Vec [8] · topic [10]
├── E. ★ Embedding làm giàu bằng mẫu phổ biến ← TRỌNG TÂM
│   ├── E1. FI làm đặc trưng trực tiếp: FI-BIN/FI-SUP [13]
│   ├── E2. Trans2Vec IND/JOI [13]
│   └── E3. (mới, đề xuất) Mẫu nén/ổn định: closed FI, CICFI [K25]; chọn thuật toán theo hồ sơ dữ liệu [K26]
├── F. Ngữ cảnh tiền huấn luyện
│   ├── F1. Fine-tune: PhoBERT, XLM-R [6][9][10]
│   └── F2. (mới) Embedding đóng băng từ LLM/PLM + bộ phân loại nhẹ [K29]
└── G. (mới) Đồ thị: TextGCN và các biến thể; đồ thị phân cấp + BERT [K30]  (khung: K05 §2.2.7, K06 §2.7)
```

---

## 6. Thay đổi dự kiến theo chương (`livrables/survey/draft/`)

| Chương | Thay đổi | Bài mới dùng |
|---|---|---|
| 1. Giới thiệu | Viết lại 1.2–1.3 theo đường ống hệ thống; thêm RQ6. Ở 1.4 (phương pháp khảo sát), nêu rõ K05/K06 là khung tham chiếu, và nêu khoảng trống: hai survey lớn không đề cập pattern-based embedding | K05, K06 |
| 2. Tiếng Việt | Thêm vnTokenizer/VNLP (tốc độ, giới hạn công cụ sâu); thêm ví dụ nhập nhằng "bảo lãnh bằng chứng khoán" của K27 | K21, K27 |
| 3. Nền tảng | **Mở rộng 3.2:** toán tử bao đóng, closed FI, lớp tương đương (K25); họ thuật toán Apriori, Eclat, FP-Growth, LCM và 8 độ đo hồ sơ dữ liệu (K26). Chuẩn hóa 3.4 (độ đo) theo K05 | K25, K26, K05 |
| 4. Tiến hóa biểu diễn | Thêm C (LSTM/CNN), F2, G theo taxonomy v3 | K27, K29, K30 |
| 5. Trans2Vec (lõi) | Thêm 5.4b "mẫu ký hiệu và tương tác tiềm ẩn" (FI và co-occurrence pooling). 5.6: H2 có lời giải CFI có trích dẫn; thêm H8 (đa cộng tuyến giữa token FI). 5.7: trả lời RQ3 có thêm "loại FI và thuật toán" | K25, K26, K29 |
| 6. Bộ phân loại và chi phí | Thêm chi phí FIM (K26), chi phí LLM embedding (K29), số liệu VNTC 2024 (K27) | K26, K27, K29 |
| 7. Dữ liệu và giao thức | Bảng dataset tin tức quốc tế (từ K05/K06) đặt cạnh dataset tiếng Việt; thêm **hồ sơ giao dịch** (density, similarity) của Snippets và VNTC | K05, K06, K26 |
| 8. Thảo luận | 8.2–8.4: thêm ví dụ VNTC lệch giữa [1] và K27, baseline yếu của K30; thảo luận PV MAP 0,511 so với nDCG của nhóm | K27, K30, K06 |
| 9. Đề xuất hệ thống | Mô-đun FIM: chọn LCM/FP-Growth, closed FI, lọc theo CI. Thêm baseline embedding đóng băng. Lập luận theo công thức 5 bước của K06 | K25, K26, K29, K06 |
| 10. Kết luận | Cập nhật khoảng trống và hướng phát triển; trả lời RQ6 | tất cả |

Ước tính: thêm khoảng **2.500–3.500 từ** (từ ~15.200 lên ~18.000) và **8 tài liệu tham khảo** (từ 43 lên 51).

---

## 7. Thực nghiệm bổ sung (tùy chọn, chạy trên CPU)

| Mã | Nội dung | Kiểm chứng | Chi phí ước tính |
|---|---|---|---|
| **E8** | Tính 8 độ đo hồ sơ dữ liệu của K26 cho Snippets và VNTC-10 (dạng transaction), ở nhiều mức δ | Giả thuyết: FI giúp trên Snippets mà không giúp trên VNTC là do khác density/similarity và độ dài giao dịch | Thấp (vài phút) |
| **E9** | ~~closed FI thay cho all FI~~ (**đã có**: ablation A3 của GĐ6, 0,770 so với 0,766). Còn lại: chỉ giữ FI có CI Wilson hẹp (K25), ước lượng theo chuyên mục; đánh giá cả Macro-F1 lẫn nDCG | H2, H8: ít token FI hơn mà Macro-F1/nDCG không giảm, hoặc tăng | Trung bình (~30–60 phút, tái dùng pipeline E6) |
| **E10** | Baseline embedding câu đóng băng (BGE-M3 hoặc multilingual-e5) + LR cho phân loại, cosine cho tìm kiếm | RQ6 và trần trên theo mô thức K29 | Cao (tải mô hình khoảng 1–2 GB, suy luận CPU trên ~84k bài có thể mất vài giờ; có thể lấy mẫu con) |

> **Đính chính (22/10):** dòng E9 ở trên viết "closed FI đã có (A3)" là **sai**. Ở cấu hình chính mọi FI đều đóng (phát hiện GĐ-H3), nên A3 không kiểm chứng gì. Thiết kế E9 mới ở Mục 10.3.

Cả ba đều chạy trong `.venv-exp`, kết quả ghi thêm vào `contexte/results/RESULTS.md` (mục mới, không sửa số liệu E1–E7).

---

## 8. Câu hỏi cần anh/chị quyết định

1. **Q1 – Hướng tái cấu trúc:** duyệt định vị v3 (tổ chức survey theo đường ống hệ thống, thêm RQ6 về tìm kiếm)? Hay chỉ **bổ sung** 8 bài vào khung v2, giữ nguyên cấu trúc chương?
2. **Q2 – Đánh số tài liệu:** dùng mã K.. như trên, hay đánh lại [11]–[18]? Gợi ý: điền [11] = K27 và [12] = K26 vào hai chỗ trống, còn lại [14]–[19]. Danh mục tham khảo cuối bài vẫn đánh số tự động theo thứ tự xuất hiện, nên lựa chọn này chỉ ảnh hưởng tên file và phiếu đọc.
3. **Q3 – Tên file:** đổi tên PDF trong `Paper_KDD_Data/` theo quy ước `[n] TenNgan-tacgiaNam.pdf` như `sources/papers/`, và xóa bản trùng `31.pdf`? (Em sẽ chưa làm gì cho tới khi anh/chị đồng ý.)
4. **Q4 – Thực nghiệm:** chạy E8, E9, E10, hay không chạy?
5. **Q5 – Bản survey:** sửa trực tiếp `livrables/survey/draft/` rồi build ra bản mới (em sẽ **sao lưu** bản .md/.docx hiện tại thành `..._v2_20261008`), hay dựng nhánh nháp riêng `livrables/survey/draft_v3/`?

---

## 9. Lộ trình (sau khi duyệt)

| Giai đoạn | Công việc | Sản phẩm |
|---|---|---|
| GĐ8 ✅ | Phiếu đọc chi tiết 8 bài theo mẫu sẵn có | `contexte/survey-notes/K25_…md` … (8 file mới) + cập nhật `notes/README.md` |
| GĐ9 ✅ | Ma trận tổng hợp v3 (taxonomy v3 × bài, RQ6) | `contexte/survey-notes/synthesis_v3.md` (file mới, giữ `synthesis.md`; đặt ở `contexte/` theo cấu trúc 21/10) |
| GĐ10 | E8, E9 bản sửa (Mục 10) | script mới trong `src/experiments/` + mục mới trong `RESULTS.md` |
| GĐ11 ✅ (22/10) | Sửa các chương theo Mục 6; thêm 8 mục K* + 3 mục tìm kiếm (BM25, HNSW, RRF) vào `refs.tsv`, xác minh Crossref | bản survey v3 (.md/.docx), bản v2 đã sao lưu |
| GĐ12 ✅ (22/10) | Rà soát: số liệu, tham chiếu chéo, trích dẫn | `contexte/survey-notes/review_log.md` (24 lỗi đã sửa) |

---

## 10. Quyết định ngày 22/10 và thiết kế GĐ10

### 10.1 Quyết định (anh/chị trả lời "theo đề xuất")

| Câu | Quyết định | Lý do |
|---|---|---|
| Q2 | Giữ mã K.. | Danh mục cuối bài tự đánh số; không phải đổi tên 8 phiếu |
| Q3 | Không đổi tên PDF trong `Paper_KDD_Data/`; `31.pdf` để anh/chị tự xử lý | `sources/` chỉ đọc |
| Q4 | Chạy **E8** và **E9 bản sửa**; **bỏ E10** | E10 cần cài torch và chạy nhiều giờ |
| Q5 | Sửa thẳng `livrables/survey/draft/` | Script build đọc sẵn thư mục này; bản v2 nằm trong git (anh/chị commit/tag trước khi GĐ11 bắt đầu) |

### 10.2 E8 — Hồ sơ dữ liệu giao dịch (K26)

- **Script:** `src/experiments/run_e8_profile.py` → `src/experiments/results/e8_profile.json`.
- **Dữ liệu (chỉ tập train):**
  - Snippets: 10.060 dòng đầu của `snippets.txt` (dữ liệu tác giả [13]); mỗi đoạn là một giao dịch.
  - VNTC-10: từ k = 20, 50, 100; âm tiết k = 50; từ không lọc top-k.
- **Mức δ:** không lọc, 0,2% (δ của tác giả trên Snippets), 0,535% (δ của nhóm trên VNTC), 1%, 2%. Theo K26, ở mỗi δ bỏ các item có support < δ rồi mới tính độ đo.
- **Độ đo:** 8 độ đo của K26 (Eq. 1–12). Density, IT, |T|, |B|, ||T|| khớp Bảng 3 của K26 (đã thử bằng phép tính trên Chess, Mushrooms, Retail). Similarity, ID và IS được cài theo công thức in trong bài, nhưng công thức này không tái tạo được số trong Bảng 3. Vì vậy ba độ đo này chỉ dùng để so giữa các corpus của nhóm. Similarity báo hai dạng: số item chung trung bình (Eq. 3) và tỉ lệ % so với độ dài giao dịch.
- **Thống kê FI kèm theo** (FI dài ≤ 3, cùng hàm `t2v.mine_fi`): số FI, số FI theo độ dài, FI dài ≥ 2 trung bình mỗi bài, tỉ lệ bài không có FI dài ≥ 2, **tỉ lệ FI không đóng**. Riêng cấu hình không lọc top-k thì bỏ phần FI, vì quá nặng.
- **Đối chiếu:** đặt hồ sơ cạnh mức JOI − IT đã đo khi đánh giá nhất quán: Snippets inductive +3,07; VNTC từ k = 50 +0,1; k = 100 −0,3; âm tiết +0,9. Chỉ có 4 điểm nên chỉ mô tả, không tính tương quan.

### 10.3 E9 bản sửa — Loại FI: all, closed, ổn định

- **Bước A (nằm trong E8):** đo tỉ lệ FI không đóng theo δ. Nếu tỉ lệ này vẫn gần 0 ở mọi δ, kết luận rằng với giao dịch văn bản đã lọc top-k, closed FI không tạo khác biệt. Đây cũng là một kết quả, và khi đó bỏ nhánh closed của bước B.
- **Bước B:** VNTC từ k = 50, δ thấp nhất mà khai phá còn chạy được. Các biến thể JOI:
  1. all FI;
  2. closed FI (chỉ khi bước A cho tỉ lệ không đóng ≥ 5%);
  3. **CICFI toàn cục:** giữ FI có cận dưới Wilson 95% ≥ δ. Với một N chung, bộ lọc này tương đương nâng δ, nên so với đối chứng "nâng δ để còn đúng số FI đó";
  4. **CICFI theo chuyên mục:** giữ FI có cận dưới Wilson ≥ δ trong ít nhất một chuyên mục (N = số bài train của chuyên mục). Biến thể này dùng nhãn train, tương tự FI phân biệt (S13), nên phải ghi rõ là *có giám sát*;
  5. đối chứng ngẫu nhiên: lấy ngẫu nhiên đúng bằng số FI của biến thể 4.
- **Giao thức:** như E6: vector train và test đều sinh bằng `infer_vector`, LR C = 1, **3 seed** (chênh 0,005 là trong vùng nhiễu nếu chỉ có 1 seed). Đo Macro-F1 và nDCG@10 (1.000 truy vấn bài báo).
- **Script:** `src/experiments/run_e9_fi_types.py` → `results/e9_fi_types.json`. Chạy nền, ghi kết quả sau từng biến thể để chạy tiếp được nếu bị ngắt.
- **Ước tính:** 30–60 phút.

