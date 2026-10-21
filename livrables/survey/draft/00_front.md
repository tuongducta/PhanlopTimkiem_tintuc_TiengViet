# Biểu diễn văn bản dựa trên mẫu phổ biến cho hệ thống tìm kiếm và phân loại chuyên mục tin tức tiếng Việt: Khảo sát và đề xuất hướng tiếp cận Trans2Vec

*Bài khảo sát — Môn Tri thức dữ liệu, Chương trình Sau đại học, Trường Đại học Công nghệ TP.HCM (HUTECH)*

---

## Tóm tắt

Phân loại chuyên mục tin tức tiếng Việt đã được nghiên cứu gần hai thập kỷ, với các cách biểu diễn văn bản đi từ túi từ (bag-of-words) và n-gram âm tiết, qua chọn đặc trưng thống kê và trích từ khóa, tới embedding học bằng mạng nơ-ron và mô hình ngôn ngữ tiền huấn luyện như PhoBERT. Song song với dòng nghiên cứu đó, cộng đồng khai phá dữ liệu đã phát triển hướng *học biểu diễn dựa trên mẫu phổ biến*. Đại diện tiêu biểu là Trans2Vec: phương pháp kết hợp tập phổ biến (frequent itemsets) với mô hình Paragraph Vector để học vector cho dữ liệu dạng tập hợp mà không cần nhãn.

Bài khảo sát này hệ thống hóa 11 công trình chính và 27 tài liệu bổ sung theo một khung phân loại sáu nhánh biểu diễn. Bài phân tích kết quả theo các nhóm có thể so sánh được, chỉ ra năm mâu thuẫn trong tài liệu, và đánh giá phản biện Trans2Vec qua bảy hạn chế khi áp dụng cho tin tức tiếng Việt. Kết quả khảo sát cho thấy ba điểm. (i) Độ khó của corpus và giao thức đánh giá chi phối kết quả nhiều hơn thuật toán: kết quả báo cáo trên cùng loại dữ liệu dao động từ F1 0,749 đến accuracy 99,75%. (ii) Vai trò của tiền xử lý tiếng Việt giảm dần qua các thế hệ biểu diễn nhưng trở lại thành yếu tố cốt lõi với biểu diễn dựa trên mẫu. (iii) Hướng học embedding từ tập phổ biến chưa từng được áp dụng cho văn bản tiếng Việt, cho văn bản dài như tin tức, hay cho bài toán tìm kiếm.

Từ đó, bài đề xuất kiến trúc một hệ thống dùng chung một biểu diễn Trans2Vec cho cả phân loại chuyên mục và tìm kiếm ngữ nghĩa, kèm giao thức đánh giá chuẩn hóa trên corpus công khai VNTC. Thực nghiệm sơ bộ trên toàn bộ VNTC-10 (33.759 bài huấn luyện, 50.373 bài kiểm tra) cho thấy: Trans2Vec chưa vượt TF-IDF ở phân loại (Macro-F1 0,849 so với 0,907), và tập phổ biến chỉ đóng góp −0,3 đến +0,9 điểm. Ngược lại, ở tìm kiếm, Trans2Vec là biểu diễn không giám sát tốt nhất (nDCG@10 0,809 so với 0,740 của TF-IDF), đồng thời cho phần giải thích chuyên mục dễ đọc với chi phí dưới một phút trên CPU. Thực nghiệm cũng phát hiện một cái bẫy đánh giá: vector huấn luyện và vector kiểm tra không được sinh cùng quy trình có thể làm sai lệch kết quả tới 8 điểm và tạo ra những cải thiện giả.

**Từ khóa:** phân loại văn bản tiếng Việt; tin tức; tập phổ biến; Trans2Vec; Paragraph Vector; học biểu diễn; tìm kiếm ngữ nghĩa; khai phá tri thức.

---

## Mục lục

1. Giới thiệu
2. Đặc thù xử lý văn bản tiếng Việt
3. Kiến thức nền tảng
4. Tiến hóa của biểu diễn văn bản cho phân loại tiếng Việt
5. Trans2Vec và mô thức biểu diễn dựa trên mẫu phổ biến
6. Bộ phân loại và đánh đổi hiệu năng – chi phí
7. Dữ liệu và giao thức đánh giá
8. So sánh tổng hợp và thảo luận
9. Đề xuất hệ thống tìm kiếm và phân loại chuyên mục dựa trên Trans2Vec
10. Kết luận và hướng phát triển

Phụ lục A: Bảng tóm tắt công trình · Phụ lục B: Thuật ngữ Việt – Anh · Tài liệu tham khảo
