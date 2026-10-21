# [K05] A Survey on Text Classification: From Traditional to Deep Learning

> **Vai trò:** R4 – **Khung tham chiếu** (taxonomy, dataset, độ đo, thách thức). **Không** dùng làm bằng chứng kết quả sơ cấp · Chương 1.4, 3.4, 4, 7, 10 · Liên quan ★★★★ (khung)

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | Q. Li, H. Peng, J. Li, C. Xia, R. Yang, L. Sun, P. S. Yu, and L. He, "A survey on text classification: From traditional to deep learning," *ACM Trans. Intell. Syst. Technol.*, vol. 13, no. 2, Art. no. 31, Apr. 2022, doi: 10.1145/3495162. |
| Đơn vị | Beihang Univ.; UIC; Univ. of Leeds; Lehigh Univ. |
| Phạm vi | Công trình từ 1961 đến 2021; 41 trang; hơn 300 tài liệu |
| File | `sources/papers/Paper_KDD_Data/5.pdf` |

## 2. Cấu trúc và nội dung
1. **Quy trình** (Fig. 1): tiền xử lý → biểu diễn (BoW, N-gram, TF-IDF, word2vec, GloVe) → bộ phân loại. Mô hình truyền thống phụ thuộc vào đặc trưng thủ công; DL học đặc trưng tự động.
2. **Taxonomy mô hình:**
   - Truyền thống: PGM (NB), KNN, SVM, DT, ensemble (RF, XGBoost, LightGBM).
   - DL (Table 1, kèm năm, venue, ứng dụng, dataset, link mã): ReNN, MLP, RNN, CNN, Attention, **pre-trained** (ELMo, GPT, BERT, XLNet, RoBERTa…), **GNN** (TextGCN, …), khác.
3. **Dataset** (Table 2) theo ứng dụng: SA, **News Classification** (AG News, 20NG, Sogou, R8/R52, …), Topic Labeling, QA, NLI, đa nhãn.
4. **Độ đo** (§3.2): đơn nhãn (Accuracy/ER, P, R, F1, **Micro/Macro-F1**, P@K, MRR…); đa nhãn (Hamming loss, …). Có so sánh ưu nhược điểm của từng độ đo.
5. **Kết quả định lượng** (Table 4): lấy từ bài gốc. Ví dụ: **Paragraph-Vec** SST-2 87,80 / IMDB 92,58 (chép từ Le & Mikolov 2014); TextGCN 20NG 86,34, MR 76,74; BERT-large SST-2 94,9. Tác giả khuyến nghị thử pre-trained trước.
6. **Thách thức** (§5):
   - *Dữ liệu*: zero/few-shot, tri thức ngoài, miền chuyên ngành, đa nhãn;
   - *Mô hình*: **biểu diễn văn bản** ("VSM đơn giản mà mất ngữ nghĩa; biểu diễn ngữ nghĩa thì quá tốn thời gian; cần biểu diễn ngữ nghĩa *hiệu quả*"), tích hợp mô hình, hiệu suất mô hình;
   - *Hiệu năng*: độ bền ngữ nghĩa (đối kháng), khả năng diễn giải.

## 3. Đánh giá phản biện
- **Điểm mạnh:** độ phủ rộng từ truyền thống tới DL; bảng dataset và độ đo đầy đủ; có thách thức theo 3 góc nhìn.
- **Hạn chế:**
  - Bảng kết quả tổng hợp từ **các bài gốc với giao thức khác nhau**, nên không so sánh trực tiếp được. Survey của nhóm phải nêu rõ điều này khi trích.
  - **Số liệu Paragraph Vector được chép lại mà không cảnh báo về tính tái lập.** Mesnil et al. (2014) đã không tái hiện được 92,58% trên IMDB (tài liệu ngoài kho, cần xác minh ở GĐ11). Đây đúng là kiểu vấn đề nhóm gặp lại với Trans2Vec ở E7.
  - Dừng ở năm 2021, chưa có LLM/embedding đóng băng (K29 lấp chỗ này).
  - **Không có mục nào về biểu diễn dựa trên mẫu phổ biến hay luật kết hợp** cho phân loại văn bản, dù đây là hướng KDD kinh điển (CBA, CMAR, Cheng 2007). Đây là **bằng chứng cho khoảng trống** mà survey nhắm tới.
  - Không có ngôn ngữ ít tài nguyên hay tiếng Việt.

## 4. Liên hệ với đề tài / Trans2Vec
- **Khung đối chiếu cho taxonomy v3:** các nhánh A–D, F, G của nhóm ánh xạ được sang taxonomy của K05. **Nhánh E (pattern-based embedding) không có tương ứng.** Nêu điều này ở Mục 1.4 và 4.1 của survey.
- **Thách thức "biểu diễn ngữ nghĩa hiệu quả về chi phí" và "khả năng diễn giải"** chính là hai điểm mạnh mà Trans2Vec nhắm tới (rẻ trên CPU; FI đọc được, xem Mục 2.4 RESULTS.md). Dùng làm lập luận động lực ở Chương 1.2.
- **"Tri thức ngoài" (§5.1):** FI là tri thức *nội tại* khai phá từ chính corpus, một lựa chọn thay thế khi không có knowledge graph tiếng Việt tốt.
- **Độ đo:** chuẩn hóa định nghĩa Micro/Macro-F1 và MRR/P@K cho Chương 3.4 (phân loại và tìm kiếm).

## 5. Ý dùng trong survey
- **Chương 1.4:** nêu K05 (và K06) là survey tổng quát tham chiếu, rồi xác định khoảng trống.
- **Chương 3.4:** định nghĩa độ đo.
- **Chương 4.1:** bảng ánh xạ taxonomy của nhóm với taxonomy K05.
- **Chương 7.1:** dataset tin tức quốc tế (AG News, 20NG, R8/R52, Sogou) làm bối cảnh cho dataset tiếng Việt.
- **Chương 10.2:** đối chiếu khoảng trống của nhóm với danh sách thách thức của K05.
