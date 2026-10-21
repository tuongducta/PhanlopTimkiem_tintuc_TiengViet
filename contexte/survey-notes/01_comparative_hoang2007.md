# [1] A Comparative Study on Vietnamese Text Classification Methods

> **Vai trò:** Bài nền tảng; nguồn corpus tin tức tiếng Việt chuẩn (sau này được biết tới là **VNTC**) · Taxonomy **A1, A2, B1** · Chương 2, 4, 7

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | V. C. D. Hoang, D. Dinh, N. L. Nguyen, and H. Q. Ngo, "A comparative study on Vietnamese text classification methods," in *Proc. IEEE Int. Conf. Research, Innovation and Vision for the Future (RIVF)*, Hanoi, Vietnam, 2007, pp. 267–273. |
| Đơn vị | ĐH KHTN và ĐH CNTT, ĐHQG TP.HCM |
| File | `[1] VN-TextClassification-Comparative-hoang2007.pdf` (bản scan có lớp OCR, nhiều hình bị lỗi chữ) |

## 2. Bài toán và động lực
- Năm 2007, nghiên cứu phân loại văn bản tiếng Việt còn ít; thường dùng **tập dữ liệu nhỏ (50–100 file mỗi chủ đề) và không công khai**, nên không có "gold standard" để so sánh.
- Khác biệt cốt lõi so với tiếng Anh: **ranh giới từ không phải khoảng trắng** (đơn vị là "morpho-syllable"). Ví dụ "Một luật gia cầm cự với tình hình hiện nay": tách "luật_gia cầm_cự" thì thuộc *Chính trị–Xã hội*, tách "gia_cầm" thì thuộc *Sức khỏe (cúm gia cầm)*.

## 3. Đóng góp chính
1. **Xây dựng corpus lớn** từ 4 báo (VnExpress, Tuổi Trẻ, Thanh Niên, Người Lao Động); tiền xử lý tự động bằng Teleport, sau đó **5 học viên cao học ngôn ngữ học hiệu chỉnh tay**.
   - **Level 1:** 10 chủ đề, 33.759 train / 50.373 test.
   - **Level 2:** 27 chủ đề con, 14.375 train / 12.076 test.
2. **So sánh 2 hướng:**
   - **BoW:** tách từ (MaxEnt, Dien & Thuy 2006) → bỏ stopword (~900 từ) → TF-IDF → **chọn đặc trưng** (MI, IG, CHI, GSS, OR, **OCFS**) → SVM (LIBSVM, linear, C = 1, 10) / kNN.
   - **N-gram LM theo âm tiết:** chuẩn hóa dấu thanh và biến thể chữ (hoà/hòa, kỳ/kì) → n-gram LM cho từng lớp (n = 2, 3, 4) → $c^* = \arg\max_c P(c)\prod_i P_c(w_i\mid w_{i-n+1}^{i-1})$. Thử các phép làm trơn Good-Turing, Linear, Witten-Bell, Absolute.

## 4. Kết quả
| Thực nghiệm | Kết quả |
|---|---|
| Chọn đặc trưng (2.500 term) | **OCFS tốt nhất** trong 6 phương pháp (F1 ≈ 0,945 Level 2) |
| Số term | Càng nhiều term càng chính xác nhưng chậm hơn; chọn 2.500 |
| N-gram | Level 1: n = 4 tốt nhất (dữ liệu lớn nên 4-gram đủ thống kê); **Good-Turing tốt nhất** |
| So sánh tổng thể | **SVM-Multi ≈ 96,21%**, **N-gram ≈ 95,58%**; > 95% trung bình; ~79 phút cho ~14.000 tài liệu |
| Kết luận | N-gram "đáng ưa hơn": nhanh hơn, **không cần tách từ, không cần chọn đặc trưng**, F1 tương đương |

## 5. Hạn chế và phản biện
- Bản PDF scan, nhiều số trong hình khó đọc. Khi trích số liệu nên dùng các con số trong phần kết luận (96,21% / 95,58%).
- "Accuracy" là trung bình theo lớp; chưa rõ macro hay micro.
- Lỗi còn lại: do bộ tách từ, và do **tài liệu nhập nhằng giữa nhiều chủ đề**. Tác giả đề xuất thêm ngữ nghĩa (LSI).
- Chỉ dùng SVM tuyến tính; không báo phương sai.

## 6. Liên hệ với đề tài / Trans2Vec
- **Corpus VNTC** là ứng viên số 1 cho thực nghiệm, vì so được với [1] và [3].
- **Lập luận "tránh tách từ"** của N-gram là tiền đề cho giả thuyết **Trans2Vec trên âm tiết**.
- Chọn đặc trưng (B1) giải bài toán số chiều cao bằng cách *chọn*. Trans2Vec giải bằng cách *học embedding*. Đây là trục so sánh trong Chương 4.
- OCFS và CHI ở 128 chiều là baseline đã được [7] dùng lại, nên có thể tái sử dụng.

## 7. Ý dùng trong survey
- Ví dụ nhập nhằng tách từ (Chương 2).
- Bảng corpus (Chương 7).
- Mốc khởi đầu dòng thời gian (Chương 4).
