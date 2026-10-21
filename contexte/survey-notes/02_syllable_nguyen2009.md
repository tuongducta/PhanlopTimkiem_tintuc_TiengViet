# [2] Text Categorization for Vietnamese Documents

> **Vai trò:** Biểu diễn mức âm tiết (bag-of-syllables); chọn đặc trưng bằng từ điển và InfoGain · Taxonomy **A1, B1, B2** · Chương 2, 4

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | G.-S. Nguyen, X. Gao, and P. Andreae, "Text categorization for Vietnamese documents," in *Proc. IEEE/WIC/ACM Int. Joint Conf. Web Intelligence and Intelligent Agent Technology (WI-IAT)*, Milan, Italy, 2009, pp. 462–465 (*số trang cần xác minh; bản PDF có hai dãy số 462–464 và 466–468*), doi: 10.1109/WI-IAT.2009.327. |
| Đơn vị | Victoria University of Wellington, New Zealand |
| File | `[2] VN-TextCategorization-Syllable-nguyen2009.pdf` (4 trang) |

## 2. Bài toán và động lực
- BoW chuẩn của tiếng Anh khó áp dụng vì từ tiếng Việt gồm nhiều âm tiết và **tách từ không tầm thường**. Ví dụ "học sinh ra từ hành" có thể tách "học | sinh ra | từ | hành" hoặc "học sinh | ra | từ | hành".
- Thay vì tách từ, phân tích văn bản ở **mức hình thái (âm tiết)**.

## 3. Phương pháp
- **Biểu diễn:** *bag of syllables* (unigram) và *bag of syllable pairs* (bigram). Lý do chọn bigram: **hơn 80% từ tiếng Việt có 2 âm tiết**.
- **Tiền xử lý:** chuyển mọi bảng mã (TELEX, VNI, TCVN3, VIQR) sang UTF-8; **chuẩn hóa vị trí dấu thanh**; loại token ngoài bảng chữ cái tiếng Việt.
- **Giảm chiều:** (a) **lọc bằng từ điển** (~30.000 từ), chỉ giữ gram là từ hoặc một phần của từ; (b) **InfoGain** giữ top-M.
- **Bộ phân loại:** NB, kNN (k = 32), SVM với 4 kernel (Linear, Poly d = 3, Gaussian c = 16, Sigmoid). Tham số tối ưu trên 5% validation.
- **Giao thức:** **chỉ 10% dữ liệu làm train**, phần còn lại test; lặp 10 lần và lấy trung bình accuracy.

## 4. Dữ liệu và kết quả
- **D1:** 4 chủ đề (Xã hội, Khoa học, Kinh tế, Thể thao), ~4.000 bài mỗi chủ đề.
- **D2:** 1.743 bài, phân loại theo **thể loại** (Tư liệu: 918, Phân tích: 825). Khoảng 15% bài khó ngay cả với chuyên gia.

| Thực nghiệm | Kết quả chính |
|---|---|
| Unigram vs bigram (D1) | Bigram tốt hơn với mọi thuật toán (98,1–98,6% so với 97,5–98,1%) nhưng **chậm hơn 4–10 lần** |
| Độ khó (bigram) | D1 ~98,5%; **D2: PSVM 89,8%, kNN 73,2%** (giảm ≥ 9%) |
| Lọc từ điển (D2) | Unigram 30K → 5K, bigram 300K → 30K. **kNN tăng mạnh** (65,5 → 74,3; 73,2 → 78,4); SVM giảm nhẹ |
| InfoGain (D2, bigram) | M = 1.000: kNN 81,5%, NB 84,9%; **300K → 100 term vẫn giữ ~72%** |

## 5. Hạn chế và phản biện
- Train chỉ 10%: thiết lập lạ, khó so với các bài khác.
- D1 chỉ 4 lớp rất tách biệt nên accuracy ~98% gần như bão hòa. Thông tin hữu ích nằm ở D2.
- Không có thống kê ý nghĩa; bài ngắn (4 trang).

## 6. Liên hệ với đề tài / Trans2Vec
- **"> 80% từ có 2 âm tiết"** là lập luận định lượng cho giả thuyết: FI 2-phần-tử trên âm tiết sẽ tự nắm được từ ghép.
- **kNN rất nhạy với đặc trưng nhiễu.** Vì tìm kiếm dựa trên láng giềng gần nhất (cosine top-k) cũng là một dạng kNN, **chất lượng embedding quyết định chất lượng tìm kiếm**. Đây là lập luận ủng hộ embedding dày thay cho vector thưa.
- **Lọc bằng từ điển** là phương án thay thế để giảm số item trước khi khai phá FI (giải H2 của [13]).
- **Khác biệt chủ đề với thể loại (D2)** cho thấy độ khó phụ thuộc định nghĩa nhãn. Đây là chất liệu cho Chương 7.

## 7. Ý dùng trong survey
- Ví dụ "học sinh ra từ hành" (Chương 2).
- Bảng unigram vs bigram và thời gian (Chương 4, đánh đổi chi phí).
- Lập luận kNN nhạy nhiễu (Chương 6 và 9, tìm kiếm).
