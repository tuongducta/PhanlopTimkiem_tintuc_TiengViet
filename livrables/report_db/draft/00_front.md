# Thiết kế và đánh giá hệ thống lưu trữ, tìm kiếm cho phân loại và tìm kiếm tin tức tiếng Việt trên MariaDB và Manticore Search

*Báo cáo môn Hệ cơ sở dữ liệu nâng cao, Chương trình Sau đại học, Trường Đại học Công nghệ TP.HCM (HUTECH)*

---

## Tóm tắt

Báo cáo trình bày phần cơ sở dữ liệu của một hệ thống phân loại chuyên mục và tìm kiếm tin tức tiếng Việt dùng biểu diễn Trans2Vec. Hệ thống tách hai vai trò. MariaDB 11.8 là nguồn dữ liệu gốc, lưu 84.132 bài báo của bộ VNTC-10, 4,15 triệu dòng transaction, các tập phổ biến, lịch sử huấn luyện mô hình, vector, dự đoán, kết quả đánh giá, nhật ký truy vấn và tin thu thập từ RSS. Manticore Search 29.9 là chỉ mục tìm kiếm phái sinh, dựng lại được hoàn toàn từ MariaDB, phục vụ BM25, tìm vector HNSW và hybrid. Lược đồ 16 bảng dùng collation tiếng Việt giữ dấu, mô hình hóa transaction và tập phổ biến dạng quan hệ nhiều–nhiều, lưu nguồn gốc của từng mô hình trong bảng `model_run` với siêu tham số dạng JSON, dùng kiểu `VECTOR(128)`, cột sinh để phát hiện bài trùng và phân vùng theo tháng cho bảng nhật ký.

Bốn thực nghiệm dùng chung giao thức 1.000 truy vấn trên kho 33.759 bài. Với tìm kiếm toàn văn, Manticore hơn InnoDB FULLTEXT cả về chất lượng (nDCG@10 cao hơn 0,06–0,14) lẫn tốc độ (nhanh hơn 7–19 lần). Với tìm kiếm vector, ở cùng tham số, chỉ mục MHNSW của MariaDB cho recall@10 cao hơn HNSW của Manticore (0,997 so với 0,940 ở M = 16, ef = 40), và độ trễ của cả hai dưới 1 ms. Hybrid RRF cho top-10 tốt nhất, lợi rõ nhất ở truy vấn ngắn, nhưng MAP@100 thấp hơn khi chỉ dùng vector. Giữ dấu tốt hơn gộp dấu với truy vấn có dấu, nhưng gần như hỏng với truy vấn không dấu; một trường gộp dấu đặt trong cùng bảng khắc phục được điều này (nDCG@10 0,394 lên 0,615).

Báo cáo cũng ghi lại các bài học thực tế: điều kiện để MariaDB dùng được chỉ mục vector; một phép JOIN trên biểu thức `MD5(body)` chạy hơn 5 phút, xuống còn 0,64 giây khi có cột sinh có chỉ mục; xung đột giữa khóa ngoại và phân vùng trong InnoDB; và cách nạp lô chạy tiếp được sau lỗi.

**Từ khóa:** MariaDB; Manticore Search; tìm kiếm toàn văn; BM25; tìm kiếm vector; HNSW; hybrid search; RRF; tiếng Việt; Trans2Vec.

---

## Mục lục

1. Giới thiệu
2. Kiến trúc hệ thống
3. Thiết kế cơ sở dữ liệu
4. Chỉ mục và tối ưu truy vấn
5. Nạp dữ liệu và giao dịch
6. Manticore Search: chỉ mục tìm kiếm phái sinh
7. Thực nghiệm
8. Ứng dụng
9. Thảo luận và hạn chế
10. Kết luận

Tài liệu tham khảo
