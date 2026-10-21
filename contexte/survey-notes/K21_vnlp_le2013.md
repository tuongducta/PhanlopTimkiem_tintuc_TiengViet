# [K21] VNLP: An Open Source Framework for Vietnamese Natural Language Processing

> **Vai trò:** R2 – Công cụ cho **bước (1) tiền xử lý tiếng Việt**; nguồn trích dẫn của vnTokenizer · Chương 2, 4 (phản biện nhánh G) · Liên quan ★★★

## 1. Thông tin thư mục
| | |
|---|---|
| **IEEE** | N. M. Le, V. D. Nguyen, B. N. Do, and T. D. Nguyen, "VNLP: An open source framework for Vietnamese natural language processing," in *Proc. 4th Symp. Information and Communication Technology (SoICT)*, Da Nang, Vietnam, Dec. 2013. *(Số trang và DOI cần tra Crossref ở GĐ11.)* |
| Đơn vị | Univ. of Trento; ePi Technologies; Univ. of Groningen |
| File | `sources/papers/Paper_KDD_Data/21.pdf` |

## 2. Bài toán và động lực
- Tính đến năm 2013, NLP tiếng Việt **thiếu một đường ống mã nguồn mở hoàn chỉnh**. Người nghiên cứu phải tự ghép các công cụ rời rạc trước khi làm được tác vụ chính.
- Mục tiêu: một bộ công cụ sẵn dùng cho sản xuất, đặt ưu tiên vào **đơn giản, tốc độ, ổn định** hơn là độ chính xác tối đa.

## 3. Phương pháp (các thành phần)
| Tác vụ | Lựa chọn | Ghi chú |
|---|---|---|
| Tách từ | **vnTokenizer** (Le H.P. et al. 2008: maximal matching + đồ thị, độ chính xác từ khoảng 97%), được tăng tốc | Đọc XML bằng SAX; tokenizer sinh bằng ANTLR; automaton có chuyển trạng thái mặc định giảm độ phức tạp từ $O(w_{max}s^2)$ xuống $O(w_{max}s)$; hỗ trợ unigram/bigram |
| POS | vnTagger (MaxEnt) | |
| Phân tích cú pháp | MaltParser (2-planar, LIBLINEAR) trên VietTreebank chuyển sang dependency | |
| NER | Luật (gazetteer + JAPE) | |
| Đồng tham chiếu | Luật (17 luật orthomatcher + đại từ) | |
| Tích hợp | Plugin GATE, dòng lệnh, giấy phép GPL | |

## 4. Kết quả
- **Tốc độ tách từ trên 2 triệu âm tiết:** vnTokenizer gốc 234 giây; Dong Du 44 giây; **bản sửa 6 giây (unigram) / 11 giây (bigram)**, tức khoảng 0,3 triệu âm tiết/giây, khoảng 440 bài/giây.
- Dependency parsing: LAS 73%, UAS 69% (theo bài; LAS > UAS là bất thường, xem Mục 5).
- NER trên 140 bài đánh giá điện thoại: **F1 tổng 0,58** (Location chỉ 0,28). Độ đồng thuận giữa người gán nhãn là 0,89.
- Công bố corpus NER và cảm xúc.

## 5. Hạn chế và phản biện
- Bảng 2 báo **LAS (73%) > UAS (69%)**, điều không thể xảy ra theo định nghĩa (LAS ≤ UAS). Nhiều khả năng hai số bị đảo. Khi trích chỉ nên nêu "khoảng 70%".
- Không đánh giá lại độ chính xác tách từ sau khi tối ưu, mà chỉ đo tốc độ.
- NER theo luật trên corpus nhỏ (140 bài), một miền (điện thoại).
- Đã lỗi thời: hiện nay là VnCoreNLP (2018), underthesea, pyvi, PhoNLP. Liên kết bitbucket có thể không còn hoạt động.

## 6. Liên hệ với đề tài / Trans2Vec
- **Bước (1) của đường ống:** tách từ là bước nền. Lỗi ở bước này truyền thẳng sang mọi bước sau ("if it mistakes a word, there is no chance for a subsequent step to get right"). Đây chính là động lực cho nhánh **âm tiết + FI** của Trans2Vec (FI khôi phục từ ghép) và ablation A1 của GĐ6.
- **Chi phí:** tốc độ khoảng 440 bài/giây cho thấy tách từ **không phải nút thắt** của hệ thống. Bước tốn kém nằm ở FIM và huấn luyện embedding. Số liệu này dùng được cho RQ1 và RQ4.
- **Phản biện nhánh G (K30):** khung của Onan cần POS, dependency, NER, coref. Với tiếng Việt, các thành phần này (theo K21) chỉ đạt F1 NER 0,58 và khoảng 70% với dependency. Chuyển K30 sang tiếng Việt vì thế sẽ chịu **lan truyền lỗi** lớn. Trans2Vec chỉ cần tách từ, thậm chí chỉ cần âm tiết.
- [3] và [K27] dùng vnTokenizer; [K21] là nguồn trích dẫn chung cho công cụ này.

## 7. Ý dùng trong survey
- **Chương 2.1:** lịch sử công cụ tách từ (vnTokenizer → VnCoreNLP/pyvi), kèm số liệu tốc độ.
- **Chương 4 (nhánh G) và 8:** lập luận về lan truyền lỗi khi phụ thuộc công cụ NLP sâu cho tiếng Việt.
