# [K27] A study on deep learning for Vietnamese text classification

> **Vai trò:** R2 – Bằng chứng tiếng Việt cho **bước (5a) phân loại**; baseline VNTC mới nhất · Taxonomy **A2, B (SVD), C** · Chương 2, 4, 6, 8 · Liên quan ★★★★★

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | N. T. Hien, B. T. Thoa, and L. N. H. Hoa, "A study on deep learning for Vietnamese text classification," *J. Military Science and Technology*, no. 95, pp. 85–94, May 2024, doi: 10.54939/1859-1043.j.mst.95.2024.85-94. |
| Đơn vị | Học viện Kỹ thuật Quân sự (Lê Quý Đôn); Bộ Công an |
| Tên tiếng Việt | "Nghiên cứu kỹ thuật học sâu cho bài toán phân lớp dữ liệu tiếng Việt" |
| File | `sources/papers/Paper_KDD_Data/27.pdf` |

## 2. Bài toán và động lực
- Nghiên cứu phân loại văn bản tiếng Việt trước đó chủ yếu dùng ML cổ điển trên dữ liệu nhỏ. Nhóm tác giả muốn đánh giá LSTM/CNN trên corpus lớn.
- Nêu ví dụ nhập nhằng tách từ: "bảo lãnh bằng chứng khoán" có thể tách thành `bảo_lãnh bằng_chứng khoán` (nghiêng về pháp luật) hoặc `bảo_lãnh bằng chứng_khoán` (nghiêng về tài chính).

## 3. Phương pháp
1. **Tiền xử lý:** tách từ bằng **vnTokenizer** (qua VNLP, xem [K21]); bỏ khoảng 2.000 stopword.
2. **Biểu diễn:** BoW; TF-IDF, sau đó **SVD** để giảm chiều.
3. **Bộ phân loại:**
   - ML: LR, DT (tham số mặc định), SVC với C = 1;
   - DL: CNN (1 tầng tích chập → MaxPooling → Flatten → Dense); LSTM (1 tầng → Dense → Dropout); Adam.
   - **Đầu vào của mạng là vector đặc trưng sau bước chọn/giảm chiều**, không phải chuỗi từ.
4. **Độ đo:** chỉ Accuracy.

## 4. Dữ liệu và kết quả
**Dữ liệu:** VNTC của [1] (VnExpress, Tuổi Trẻ, Thanh Niên, Người Lao Động).
- Level 1: 10 chủ đề, **33.759 train / 50.373 test**, trùng với cách chia trong GĐ6.
- Level 2: 27 chủ đề, 14.375 train / 12.076 test.

| Biểu diễn | Level | LR | DT | SVM | LSTM | CNN |
|---|---|---|---|---|---|---|
| BoW | 1 | 92,29 | 78,31 | 91,85 | **94,52** | 93,75 |
| BoW | 2 | 87,79 | 68,13 | 86,08 | **89,35** | 88,22 |
| TF-IDF | 1 | 92,77 | 83,60 | 93,60 | **93,75** | 93,59 |
| TF-IDF | 2 | 88,20 | 73,82 | 89,35 | **89,43** | 88,33 |

Kết luận của tác giả: DL tốt hơn ML, đặc biệt trên Level 1 vốn có các chủ đề dễ nhầm lẫn. Tác giả tự nêu hạn chế: biểu diễn còn đơn giản, corpus có nhập nhằng giữa chủ đề, tách từ bị giới hạn bởi thư viện bên thứ ba.

## 5. Hạn chế và phản biện
1. **"LSTM" không mô hình hóa thứ tự từ.** Đầu vào là một vector BoW/TF-IDF(+SVD) duy nhất, nên LSTM và CNN thực chất là bộ phân loại phi tuyến trên đặc trưng túi từ. Kết luận "DL tốt hơn" vì vậy không phải bằng chứng về giá trị của mô hình chuỗi.
2. **Mức chênh nhỏ:** với TF-IDF, LSTM chỉ hơn SVM 0,15 (L1) và 0,08 (L2) điểm. Không có độ lệch chuẩn hay kiểm định, nên chênh lệch nằm trong vùng nhiễu.
3. **SVM+TF-IDF đạt 93,60%, thấp hơn 96,21% của [1] trên cùng corpus và cùng cách chia.** Khác biệt do tiền xử lý, số chiều SVD, kernel, C… không được phân tích.
4. **Chỉ báo Accuracy** trên dữ liệu mất cân bằng. Bảng 1 (thống kê Level 1) trong PDF bị lỗi trình bày (dòng tổng trùng dòng 1).
5. Số lượng ở Level 2 khác với số liệu thường được trích dẫn từ [1]. Cần ghi chú khi so sánh.
6. Không công bố mã nguồn và siêu tham số mạng (số đơn vị, số epoch, số chiều SVD).

## 6. Liên hệ với đề tài / Trans2Vec
- **Cùng corpus, cùng cách chia Level 1 với GĐ6 (E1–E6).** Vì vậy K27 là điểm đối chiếu trực tiếp và mới nhất. TF-IDF+SVM của nhóm (Macro-F1 0,907) nằm cùng vùng với Accuracy 93,60% của K27. Khi so sánh cần nêu rõ khác độ đo: Accuracy cao hơn Macro-F1 trên dữ liệu mất cân bằng.
- **Bằng chứng cho luận điểm "giao thức chi phối kết quả"** (Mục 8.2 survey): [1] 96,21%, K27 93,60%, nhóm 0,907 Macro-F1, đều trên VNTC.
- Ví dụ "bằng chứng khoán" minh họa tốt cho đề xuất của Trans2Vec: FI trên **âm tiết** như {chứng, khoán} có thể khôi phục từ ghép mà không cần tách từ (ablation A1 của GĐ6: không tách từ mất 1–3 điểm).
- Đối chứng với [7]: [7] dùng MLP trích 128 chiều rồi SVM; K27 dùng SVD rồi mạng nông. Cả hai đều là **dense có giám sát dựng trên TF-IDF**, cùng nhánh C.

## 7. Ý dùng trong survey
- **Chương 2:** ví dụ nhập nhằng tách từ.
- **Chương 4 (nhánh C):** đại diện 2024 cho LSTM/CNN trên tiếng Việt, kèm phản biện về đầu vào.
- **Chương 6 và 8.1:** đưa vào bảng kết quả VNTC (cột Accuracy, ghi chú khác độ đo).
- **Chương 8.2–8.3:** ví dụ cùng corpus mà lệch 2,6 điểm giữa hai công trình.
