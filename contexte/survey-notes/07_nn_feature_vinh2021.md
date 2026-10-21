# [7] Feature Extraction Using Neural Networks for Vietnamese Text Classification

> **Vai trò:** Cầu nối từ biểu diễn thưa sang biểu diễn dày; **đối chứng trực tiếp nhất với Trans2Vec** (cùng 128 chiều + SVM) · Taxonomy **C** · Chương 4, 9

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | T. N. P. Vinh and H. H. Kha, "Feature extraction using neural networks for Vietnamese text classification," in *Proc. Int. Symp. Electrical and Electronics Engineering (ISEE)*, Ho Chi Minh City, Vietnam, 2021, pp. 120–124, doi: 10.1109/ISEE51682.2021.9418674. |
| Đơn vị | ĐH Bách khoa TP.HCM, ĐHQG TP.HCM |
| Ghi chú tên | Tên đầy đủ là **Tô Nguyễn Phước Vinh** (họ Tô). Tên file dùng "vinh2021" theo cách bài báo tự trích dẫn ("Vinh et al."). Cần thống nhất khi chọn chuẩn trích dẫn |
| File | `[7] NN-FeatureExtraction-VN-TC-vinh2021.pdf` |

## 2. Bài toán và động lực
- Vector TF-IDF có số chiều rất lớn. Các phương pháp **chọn đặc trưng** truyền thống (MI, IG, CHI, OR, DFS, OCFS) phức tạp mà hiệu quả hạn chế.
- **Đề xuất:** dùng mạng nơ-ron để **trích** đặc trưng dày, thay cho **chọn** đặc trưng.

## 3. Phương pháp
1. **Dữ liệu:** 68.363 bài từ dantri, thanhnien, vnexpress, doisongsuckhoe, qdnd; **30 chuyên mục**, mất cân bằng.
2. **Tiền xử lý:** bỏ số, ký tự đặc biệt, dấu câu; chuyển chữ thường; bỏ stopword.
3. **Token:** unigram + bigram (thay cho tách từ) để giảm nhập nhằng.
4. **TF-IDF:** $idf_t=\log\frac{N}{1+df_t}$; cắt còn **10.000 chiều** theo TF lớn nhất.
5. **Bộ trích đặc trưng:** MLP 2 lớp ẩn (n đơn vị, BatchNorm, ReLU hoặc tanh), softmax 30 lớp, cross-entropy + Frobenius regularization, Adam lr 3e-4, 30 epoch, batch 128. Huấn luyện xong thì **bỏ lớp output**, đầu ra của lớp ẩn cuối là đặc trưng n chiều.
6. **Phân loại:** SVM soft margin (OVO, OVR; kernel linear, poly, RBF). Xử lý mất cân bằng bằng **trọng số theo lớp** $K_c = M/(C\cdot M_c)$.
7. **Chia dữ liệu:** 48.363 train / 10.000 val / 10.000 test.

## 4. Kết quả
| n | ReLU val acc | tanh val acc |
|---|---|---|
| 512 | 0,9057 | 0,8890 |
| 256 | 0,9061 | 0,9019 |
| **128** (được chọn) | 0,9046 | 0,9056 |
| 96 | 0,9044 | 0,9073 |

- ReLU tốt hơn tanh. Chọn **n = 128, ReLU** để cân bằng hiệu năng và độ phức tạp.
- OVO và OVR cho kết quả gần như nhau.
- **So với CHI và OCFS** (cũng giảm về 128 chiều để so công bằng): phương pháp NN **vượt hoàn toàn** (Fig. 6; số liệu chi tiết chỉ có trong hình).

## 5. Hạn chế và phản biện
- Bộ trích đặc trưng **có giám sát** (huấn luyện bằng nhãn), nên embedding gắn với 30 chuyên mục và không chuyển sang tác vụ khác được. Đây chính là điểm [13] phê phán ở các phương pháp FI có giám sát.
- Số liệu so sánh cuối cùng chỉ có ở dạng hình; không báo F1 test dạng số.
- MLP + softmax đã là một bộ phân loại hoàn chỉnh, nên lợi ích của việc thêm SVM phía sau không được chứng minh tách bạch.
- Dataset không công khai.

## 6. Liên hệ với đề tài / Trans2Vec
- **Đối chứng công bằng nhất:** cùng **128 chiều**, cùng **SVM**, cùng tin tức tiếng Việt nhiều chuyên mục. Câu hỏi thực nghiệm then chốt: *embedding không giám sát (Trans2Vec) có đạt gần embedding có giám sát ([7]) không?* Nếu đạt, Trans2Vec có lợi thế dùng được cho cả **tìm kiếm** và tài liệu chưa gán nhãn.
- Unigram + bigram thay cho tách từ ứng với ý tưởng "FI 2 phần tử" của Trans2Vec, nhưng FI không cần liền kề.
- Trọng số lớp cho SVM nên được áp dụng trong thực nghiệm (tin tức mất cân bằng).
- Baseline OCFS/CHI @128 có thể tái hiện theo bài này.

## 7. Ý dùng trong survey
- Chương 4 (nhánh C), mốc chuyển "chọn đặc trưng" sang "học đặc trưng".
- Chương 9: baseline chính trong bảng thực nghiệm.
