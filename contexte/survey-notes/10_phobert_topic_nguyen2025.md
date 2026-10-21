# [10] Topic Classification of Vietnamese Product Reviews in E-commerce using PhoBERT

> **Vai trò:** So sánh **đầy đủ nhất** các họ biểu diễn (BoW, TF-IDF, Word2Vec, PhoBERT) và topic model (LDA, **Top2Vec**, BERTopic) trên tiếng Việt; có bảng chi phí · Taxonomy **D1, D3, F** · Chương 4, 6, 9

## 1. Thông tin thư mục
| | |
|---|---|
| **APA/IEEE** | T. D. Nguyen, D. M. Nguyen, H. M. Nguyen, and T. Q. G. Nguyen, "Topic classification of Vietnamese product reviews in e-commerce using PhoBERT," *Journal of Marketing Analytics*, vol. 13, pp. 371–385, 2025, doi: 10.1057/s41270-025-00402-w. |
| Loại | Tạp chí Springer Nature (thiên về marketing), 15 trang |
| File | `[10] PhoBERT-TopicClassification-Shopee-nguyen2025.pdf` |

## 2. Bài toán
- Phân loại chủ đề review sản phẩm Shopee để doanh nghiệp xác định vấn đề của khách hàng.
- **Đa nhãn**, 5 chủ đề: Product Quality, Customer Service, Price, Shipping, Packaging (+ Other).

## 3. Quy trình hai pha
**Pha 1 — topic modeling không giám sát:**
- Crawl hơn 500.000 review (10/2023) bằng Selenium, Requests, BeautifulSoup; lấy mẫu còn 17.049 (rating lệch về 5 sao, 41%).
- So sánh **LDA (Gensim), Top2Vec, BERTopic** bằng **C_v coherence** và **topic diversity**, với 10–20 chủ đề.
- **Kết quả:** LDA và BERTopic có coherence ~0,48, diversity > 0,8. **Top2Vec kém hơn.**
- Topic model không đủ tốt để dùng trực tiếp. Chúng chỉ được dùng để **định nghĩa nhãn** cho pha 2.

**Pha 2 — phân loại có giám sát:**
- **Gán nhãn tay** (nhị phân cho từng chủ đề), kiểm tra chéo giữa các thành viên, **active learning**: dùng mô hình baseline để tìm nhãn nghi sai.
- Chia 70 / 10 / 20 (train / val / test).
- Biểu diễn: BoW, TF-IDF, Word2Vec (Skip-gram, CBOW), **PhoBERT-base-v2**. Tiền xử lý bằng VnCoreNLP.
- Bộ phân loại: LR, SVM, XGBoost, NB; xử lý đa nhãn bằng **Binary Relevance (BR)** hoặc **Classifier Chain (CC)**.

## 4. Kết quả (Table 4, trích)
| Biểu diễn | Tốt nhất | Hamming ↓ | Macro-F1 | Micro-F1 |
|---|---|---|---|---|
| BoW | CC-XGB | 0,049 | 0,89 | 0,92 |
| TF-IDF | CC-XGB | 0,050 | 0,89 | 0,92 |
| Word2Vec Skip-gram | CC-XGB | 0,071 | 0,83 | 0,88 |
| Word2Vec CBOW | CC-XGB | 0,066 | 0,84 | 0,89 |
| PhoBERT + NN (fine-tune) | — | 0,032 | 0,94 | 0,95 |
| **PhoBERT + BR-LR** | — | **0,022** | **0,96** | **0,96** |

**Chi phí (Table 5, Colab):**
| Biểu diễn | Phần cứng | Train (12.240 review) | Inference (3.041 review) |
|---|---|---|---|
| BoW | CPU | 24,1 s | 6,17 s |
| TF-IDF | CPU | 21,9 s | 5,77 s |
| Skip-gram | CPU | 71,2 s | 4,65 s |
| CBOW | CPU | 21,4 s | 3,15 s |
| PhoBERT | GPU T4 | 4 phút 7 giây mỗi epoch (~41 phút cho 10 epoch) | 37 s |

- **Kết luận của tác giả:** hệ thống thời gian thực nên chọn mô hình đơn giản; xử lý theo lô thì chọn PhoBERT.

## 5. Hạn chế và phản biện
- Venue thiên về marketing; phần NLP mô tả ở mức ứng dụng.
- Nhãn được gán bởi chính nhóm tác giả, không báo chỉ số đồng thuận (kappa).
- Word2Vec kém BoW. Có thể do review ngắn, hoặc do gộp vector bằng trung bình (không mô tả).
- **Top2Vec chỉ được đánh giá bằng coherence**, không thử như một biểu diễn cho phân loại. Kết luận "Top2Vec kém" chỉ áp dụng cho chất lượng chủ đề, trên văn bản ngắn.
- Không báo phương sai.

## 6. Liên hệ với đề tài / Trans2Vec
- **Bảng so sánh mẫu mực** để mô phỏng trong Chương 9: cùng tập test, nhiều biểu diễn × nhiều bộ phân loại, kèm chi phí.
- **Thứ tự rút ra:** PhoBERT > BoW ≈ TF-IDF > Word2Vec. Trans2Vec nên được chen vào bảng này để xem nó đứng ở đâu, kỳ vọng giữa TF-IDF và PhoBERT, với chi phí CPU.
- **"Embedding tĩnh kém TF-IDF trên văn bản ngắn"** xuất hiện ở cả [8] và [10]. Tin tức dài là bối cảnh thuận lợi hơn cho Doc2Vec và Trans2Vec, và cần được kiểm chứng.
- **Pha 1 (topic model) gợi ý:** C_v coherence và topic diversity có thể đánh giá **FI/cụm từ khai phá được** của Trans2Vec như những "chủ đề" diễn giải được.
- **Bảng chi phí** là mẫu để đo H7 của [13].
- Active learning để làm sạch nhãn hữu ích nếu tự crawl corpus.

## 7. Ý dùng trong survey
- Chương 4 (nhánh D3: LDA, Top2Vec, BERTopic; nhánh F).
- Chương 6 (bảng chi phí).
- Chương 7 (C_v, diversity, Hamming loss).
- Chương 9 (khung bảng thực nghiệm).
