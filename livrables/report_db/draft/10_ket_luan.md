## 10. Kết luận

Báo cáo đã trình bày phần cơ sở dữ liệu của một hệ thống phân loại và tìm kiếm tin tức tiếng Việt, từ thiết kế lược đồ tới vận hành thực tế trên 84.132 bài báo.

**Về thiết kế:**
- Hệ thống tách rõ hai vai: MariaDB giữ dữ liệu gốc có ràng buộc toàn vẹn, Manticore là chỉ mục tìm kiếm dựng lại được bất kỳ lúc nào.
- Lược đồ 16 bảng mô hình hóa đủ vòng đời dữ liệu học máy:
  - transaction và tập phổ biến dạng quan hệ nhiều–nhiều;
  - lịch sử lần chạy có quan hệ cha–con và siêu tham số dạng JSON;
  - vector với kiểu `VECTOR(128)` có kiểm tra số chiều;
  - dự đoán kèm phân phối xác suất;
  - nhật ký phân vùng theo tháng.
- Các quyết định quan trọng đều xuất phát từ kiểm tra trên bản cài thật, không từ giả định:
  - chọn collation giữ dấu sau khi thấy `'bàn' = 'bán'` dưới collation mặc định;
  - bỏ phân vùng `article_item` vì xung đột với khóa ngoại;
  - không đặt chỉ mục vector lên bảng nhiều lần chạy vì chỉ mục không lọc được;
  - thêm cột sinh `body_md5` sau khi một phép JOIN trên biểu thức chạy hơn 5 phút.

**Về thực nghiệm**, bốn kết luận chính:
1. Với tìm kiếm toàn văn tiếng Việt, engine chuyên dụng vượt chỉ mục toàn văn của InnoDB cả về chất lượng lẫn tốc độ.
2. Chỉ mục vector của MariaDB 11.8 cạnh tranh tốt, thậm chí cho recall cao hơn Manticore ở cùng tham số. Ở quy mô này, thời gian suy luận của mô hình mới là nút cổ chai, không phải chỉ mục.
3. Hybrid RRF cho top-10 tốt nhất, nhất là với truy vấn ngắn, nhưng đánh đổi chất lượng ở phần đuôi danh sách.
4. Giữ dấu là cấu hình đúng cho tiếng Việt có dấu. Với người dùng gõ không dấu, hệ thống tự chuyển sang trường gộp dấu, nâng nDCG@10 từ 0,394 lên 0,615.

**Hướng tiếp theo:**
- Đồng bộ tăng dần bằng mẫu outbox để đưa tin RSS vào kho tìm kiếm.
- Bổ sung tập truy vấn có nhãn liên quan do người gán.
- Hoàn thành thực nghiệm khai phá tập phổ biến ngay trong DBMS (E-DB3), để trả lời câu hỏi bao giờ nên đưa thuật toán khai phá dữ liệu vào trong hệ quản trị.
