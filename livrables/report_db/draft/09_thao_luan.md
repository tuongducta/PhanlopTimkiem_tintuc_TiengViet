## 9. Thảo luận và hạn chế

### 9.1 Proxy độ liên quan

Chương 7 coi một bài là "liên quan" nếu cùng chuyên mục với truy vấn. Proxy này cho phép đánh giá tự động, nhưng có ba hệ quả:
- **Đánh giá sai truy vấn ngắn.** Với "giá vàng tăng", mọi bài Kinh doanh đều tính là đúng, kể cả bài không nói gì về vàng. Ngược lại, một bài Thế giới về giá vàng quốc tế lại bị tính là sai.
- **Kém nhạy với chỉ mục ANN.** Recall đổi từ 0,86 đến 1,0 mà nDCG chỉ dao động 0,007 (E-DB2).
- **Ưu ái biểu diễn theo chủ đề.** Vector Trans2Vec gom bài theo chủ đề nên hưởng lợi hơn BM25. Một phần khoảng cách ở E-DB4 có thể đến từ proxy.

Cần một tập truy vấn có nhãn liên quan do người gán, dù chỉ khoảng 50 truy vấn. Báo cáo chưa làm được việc này.

### 9.2 Nhất quán giữa hai hệ

Hiện Manticore được **dựng lại toàn bộ** sau mỗi lần nạp hoặc huấn luyện. Sau khoảng 100 giây, Manticore phản ánh chính xác MariaDB, và bước kiểm tra số lượng bảo đảm không thiếu tài liệu. Kho VNTC là tĩnh nên cách này đủ dùng.

Khi dữ liệu thay đổi liên tục, ví dụ đưa tin RSS vào kho tìm kiếm, cần đồng bộ tăng dần. Cách "ghi kép" (ứng dụng ghi MariaDB rồi ghi Manticore) có lỗ hổng kinh điển [@kleppmann2017]: tiến trình chết giữa hai lần ghi làm hai hệ lệch nhau mà không ai biết, và hai luồng ghi song song có thể đến hai hệ theo thứ tự khác nhau.

Phương án phù hợp là **mẫu outbox**:
1. Trong **cùng giao dịch** ghi `feed_item`, ứng dụng (hoặc một trigger) ghi thêm một dòng vào bảng `sync_outbox(id, entity, entity_id, op)`.
2. Một tiến trình nền đọc outbox theo thứ tự `id`, áp lên Manticore bằng `REPLACE` hoặc `DELETE` (đều idempotent), rồi đánh dấu đã xử lý. Cột `feed_item.indexed_at` đã có sẵn cho việc này.
3. Nếu tiến trình nền chết, nó chỉ việc đọc tiếp từ dòng chưa xử lý; áp lại một thay đổi hai lần không gây sai.

Kết quả là **nhất quán cuối cùng**: Manticore có thể chậm vài giây nhưng không mất thay đổi nào. Phương án mạnh hơn là đọc binlog của MariaDB (change data capture). Cách đó không cần sửa ứng dụng nhưng thêm một thành phần phải vận hành.

### 9.3 Những gì chưa làm và các giới hạn khác

| Hạng mục | Hướng làm |
|---|---|
| E-DB3: khai phá FI trong DBMS | Đếm support bằng self-join trên `article_item` theo hướng SETM [@houtsma1995] hoặc các phương án tích hợp của Sarawagi và cộng sự [@sarawagi1998]; so với Python |
| E-DB6: ghi kép có lỗi | Kiểm chứng mẫu outbox ở Mục 9.2 |
| Nguyên tử ở mức lần chạy | Cột `status` cho `model_run` (Mục 5.1) |

**Các giới hạn khác:**
- **Môi trường và quy mô:** một máy, Docker trên macOS, 84 nghìn tài liệu nằm gọn trong bộ nhớ. Các so sánh tương đối vẫn có giá trị vì cùng điều kiện, nhưng kết luận "quét toàn bảng cũng đủ nhanh" không còn đúng khi kho lên hàng triệu bài.
- **Bài trùng của VNTC:** ảnh hưởng tới Macro-F1 không đáng kể (JOI 0,8498 so với 0,8488 khi bỏ các bài trùng), nhưng kết quả tìm kiếm bắt buộc phải khử trùng khi hiển thị.
- **Bảo mật:** mật khẩu chỉ dành cho máy cá nhân, cổng chỉ mở trên 127.0.0.1, và ứng dụng dùng một tài khoản có quyền ghi mọi bảng. Khi triển khai thật, nên tách tài khoản chỉ đọc cho trang tra cứu và tài khoản chỉ được `INSERT` vào bảng nhật ký.
