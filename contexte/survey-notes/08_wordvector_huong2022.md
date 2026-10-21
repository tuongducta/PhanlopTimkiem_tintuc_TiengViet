# [8] Sentiment Analysis based on Word Vector Representation for Short Comments in Vietnamese Language

> **Vai trò:** So sánh TF-IDF, Word2Vec, GloVe, **Doc2Vec** trên tiếng Việt (bài lệch miền: cảm xúc) · Taxonomy **D1, D2** · Chương 4, 8 (phản biện)

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | T. H. Huong, D. T. C. Lai, K. Tran-Trung, and V. T. Hoang, "Sentiment analysis based on word vector representation for short comments in Vietnamese language," in *Proc. 9th NAFOSTED Conf. Information and Computer Science (NICS)*, Ho Chi Minh City, Vietnam, 2022, pp. 165–169, doi: 10.1109/NICS56915.2022.10013426. |
| Đơn vị | ĐH Mở TP.HCM (cùng nhóm Vinh Truong Hoang với [4]); Universiti Brunei Darussalam |
| Ghi chú tên | Tác giả đầu ghi "Thien Ho Huong" (thứ tự kiểu phương Tây). Họ cần xác minh khi trích dẫn |
| File | `[8] WordVector-VN-Sentiment-huong2022.pdf` |

## 2. Bài toán
- Phân loại cảm xúc (tích cực/tiêu cực) bình luận ẩm thực tiếng Việt.
- Hai dataset từ streetcodevn.com: **Dataset 1** 15.000 + 15.000 bình luận (~2,96 triệu từ); **Dataset 2** 5.000 + 5.000 (~1 triệu từ). Đều **cân bằng hoàn toàn**.

## 3. Phương pháp
- **Tiền xử lý:** bỏ URL, email, hashtag, @user, số, ký tự lặp; xử lý emoticon; tách từ bằng **pyvi**; bỏ stopword.
- **Biểu diễn:** TF-IDF; Word2Vec (CBOW/Skip-gram); GloVe; **Doc2Vec (PV-DM / PV-DBOW)**. Bài mô tả lý thuyết từng phương pháp nhưng **không nêu số chiều, cửa sổ, số epoch, cách gộp vector từ thành vector câu, hay embedding tự huấn luyện hay pretrained**.
- **Bộ phân loại:** LR, NB, 1-NN, RF, SVM. Chia 70:30; đo accuracy.

## 4. Kết quả (accuracy %)
| Biểu diễn | LR | NB | 1-NN | RF | SVM | TB (DS1) | TB (DS2) |
|---|---|---|---|---|---|---|---|
| **TF-IDF** | 86,77 | 83,37 | 68,66 | 84,89 | **86,80** | **82,09** | **81,44** |
| GloVe | 68,26 | 49,68 | 61,92 | 68,68 | 69,04 | 63,51 | 61,16 |
| Word2Vec | 49,86 | 49,68 | 50,57 | 49,84 | 49,88 | 50,00 | 49,97 |
| Doc2Vec | 49,73 | 49,78 | 50,41 | 48,71 | 49,87 | 49,70 | 49,48 |

- **Giải thích của tác giả:** bình luận ngắn, viết lỏng lẻo, nên biểu diễn "cục bộ" (TF-IDF) tốt hơn biểu diễn "toàn cục" (embedding). Kết quả sẽ cải thiện nếu có corpus lớn hơn để huấn luyện embedding.

## 5. Phản biện (quan trọng cho đề tài)
- **Word2Vec và Doc2Vec ≈ 50% trên dữ liệu nhị phân cân bằng, tức đúng bằng mức đoán ngẫu nhiên, với *mọi* bộ phân loại kể cả RF và 1-NN.** Một biểu diễn có chứa thông tin dù yếu thì ít nhất 1-NN cũng phải vượt 50%. Gần như chắc chắn đây là **lỗi cài đặt**: vector rỗng hoặc hằng sau khi gộp, sai lệch thứ tự giữa vector và nhãn, hoặc dùng vector chưa huấn luyện. Đây không phải giới hạn của phương pháp.
- **Bằng chứng đối chiếu:**
  - Trong [13], TRANS-IT (PV-DBOW, tức Doc2Vec) đạt **75,23%** trên Snippets, văn bản *ngắn* 8 lớp, hơn TF-IDF 5 điểm.
  - Trong [10], Word2Vec trên review Shopee (cũng ngắn) đạt Micro-F1 0,84–0,89, tức hoạt động bình thường.
- Thiếu mô tả siêu tham số nên không tái lập được. Không có thống kê ý nghĩa.

## 6. Liên hệ với đề tài / Trans2Vec
- Trans2Vec xây trên PV-DBOW. Nếu chỉ đọc [8], người đọc dễ kết luận sai rằng "Doc2Vec không dùng được cho tiếng Việt". **Survey cần chủ động giải thích** bằng đối chiếu với [13] và [10].
- **Bài học thực nghiệm:**
  1. Kiểm tra vector embedding không suy biến (norm, phương sai).
  2. Kiểm tra sơ bộ bằng kNN.
  3. Báo đầy đủ siêu tham số (d, window, epoch, min_count, negative).
- Kết quả TF-IDF mạnh nhắc rằng **TF-IDF + SVM/LR là baseline bắt buộc**.

## 7. Ý dùng trong survey
- Chương 4 (nhánh D): định nghĩa TF-IDF, Word2Vec, GloVe, Doc2Vec (Eq. 1–4).
- Chương 8: ví dụ điển hình về **kết quả âm tính khó tin** và tầm quan trọng của khả năng tái lập.
