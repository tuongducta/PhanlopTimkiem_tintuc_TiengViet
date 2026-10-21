# [3] Vietnamese News Classification based on BoW with Keywords Extraction and Neural Network

> **Vai trò:** Trích từ khóa để giảm không gian đặc trưng; MLP làm bộ phân loại; có triển khai thực tế · Taxonomy **B3** · Chương 4, 8 (phản biện)

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | T. Pham Van and T. Ta Minh, "Vietnamese news classification based on BoW with keywords extraction and neural network," in *Proc. 21st Asia Pacific Symp. Intelligent and Evolutionary Systems (IES)*, Hanoi, Vietnam, 2017, pp. 43–48. |
| Đơn vị | Framgia Inc. R&D (nay là Sun\*); HV Kỹ thuật Quân sự |
| File | `[3] VN-NewsClassification-KEBoW-NN-van2017.pdf` |

## 2. Bài toán và động lực
- Phân loại tin tức tiếng Việt; dùng lại **corpus của [1]** (10 và 27 chủ đề).
- Ví dụ nhập nhằng: "Bảo_lãnh bằng chứng_khoán" (*bảo lãnh bằng cổ phiếu*) so với "Bảo_lãnh bằng_chứng khoán" (vô nghĩa). Tách từ sai dẫn tới từ khóa sai, rồi tới phân loại sai.

## 3. Phương pháp — KEBoW
1. **Tách từ:** vnTokenizer.
2. **Bỏ stopword:** danh sách ~2.000 từ, thu thập thủ công.
3. **Trích từ khóa:** chọn top-10 từ khóa mỗi bài theo $\text{KeywordScore}(k_i) = 1{,}5 \cdot |k_i| / |W|$, với $|k_i|$ là tần suất từ khóa và $|W|$ là số từ khóa duy nhất.
4. **Từ điển từ khóa** xây "in all documents of our corpus"; biểu diễn BoW trên từ điển này.
5. **Bộ phân loại:** SVM đa lớp (Crammer–Singer), SVC, Random Forest, **MLP 6 lớp ẩn, tanh, SGD**.

## 4. Kết quả (Table I, accuracy)
| | SVM | RF | SVC | **NN** |
|---|---|---|---|---|
| 10 chủ đề | 0,9652 | 0,9921 | 0,9922 | **0,9975** |
| 27 chủ đề | 0,9780 | 0,9925 | 0,9965 | **0,9969** |

- Tác giả khẳng định tốt hơn [1] trên cùng dataset. Kết quả được **ứng dụng thực tế** để tự gán chuyên mục bài viết trên Viblo.

## 5. Hạn chế và phản biện (quan trọng)
- **Nguy cơ rò rỉ dữ liệu:** từ điển từ khóa xây trên **toàn bộ corpus**, nhiều khả năng gồm cả tập test. Không mô tả rõ train/test split cho bước trích từ khóa.
- 99,75% trên 10 chủ đề, có nhiều chủ đề chồng lấn (Chính trị–Xã hội, Pháp luật, Thế giới), là con số **khó tin** khi đặt cạnh [4] (F1 0,749 trên 25 lớp) và [7] (~90% trên 30 lớp).
- Không báo phương sai và cấu hình MLP chi tiết. So sánh với [1] qua **hình chụp lại** (Fig. 10), không chạy lại baseline.
- Công thức KeywordScore là hàm đơn điệu của tần suất (thực chất là TF đã chuẩn hóa), không có thành phần IDF, nên **dễ chọn phải từ phổ biến**.
- Tác giả tự nêu: danh sách stopword chủ quan; corpus có nhập nhằng chủ đề; phụ thuộc thư viện tách từ.

## 6. Liên hệ với đề tài / Trans2Vec
- **Ý tưởng "top-k từ khóa mỗi bài" là cách giải H2 của [13]:** giới hạn mỗi transaction còn k item trước khi khai phá FI. Nên dùng TF-IDF hoặc TextRank thay cho KeywordScore để có IDF.
- **Bài học thiết kế thực nghiệm:** mọi bước fit (từ điển, FI, embedding) **chỉ được làm trên tập train**. Đưa vào mục "Kiểm soát rò rỉ".
- Bằng chứng ứng dụng: phân loại chuyên mục tự động trên nền tảng thật (Viblo).

## 7. Ý dùng trong survey
- Ví dụ "Bảo lãnh bằng chứng khoán" (Chương 2).
- Ví dụ điển hình cho **mục phản biện về tính so sánh được và rò rỉ dữ liệu** (Chương 8).
