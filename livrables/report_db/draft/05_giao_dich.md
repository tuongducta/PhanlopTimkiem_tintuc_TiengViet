## 5. Nạp dữ liệu và giao dịch

### 5.1 Nạp lô dữ liệu gốc và kết quả huấn luyện

**Nạp bài báo.** `load_articles.py` nạp 84.132 bài theo lô 1.000 bài. Mỗi lô là **một giao dịch** gồm hai lệnh `executemany`: một cho `article`, một cho khoảng 49.000 dòng `article_item`. Kích thước lô là một đánh đổi:
- Lô quá nhỏ: mỗi `COMMIT` buộc ghi redo log xuống đĩa.
- Lô quá lớn: giữ nhiều undo log, và một lỗi giữa chừng làm mất nhiều việc.

Toàn bộ dữ liệu nạp xong trong **99 giây**. Ba biện pháp bảo đảm đúng đắn:
- Script từ chối chạy nếu `article` đã có dữ liệu, để tránh nạp hai lần.
- Transaction tự tính được so khớp với thư viện thực nghiệm bằng `assert` trên 500 bài đầu.
- Sau khi nạp, script chạy `ANALYZE TABLE` để bộ tối ưu có thống kê mới.

**Ghi kết quả huấn luyện.** Mỗi bộ phân loại được ghi theo trình tự:
1. `INSERT model_run`.
2. Huấn luyện.
3. `INSERT eval_result`.
4. `INSERT prediction` 50.373 dòng theo lô 20.000.
5. `UPDATE model_run SET metrics`.

Các bước 3, 4, 5 commit riêng. Mô hình (khoảng 130 MB) lưu thành tệp ngoài CSDL, đặt tên theo id lần chạy; đường dẫn ghi trong `params`. Mô hình chỉ được đọc trọn khi ứng dụng khởi động, nên lưu tệp hợp lý hơn lưu BLOB.

Cách chia giao dịch này **chưa nguyên tử ở mức lần chạy**. Nếu tiến trình chết giữa bước 3 và 4, CSDL sẽ có lần chạy có đánh giá nhưng thiếu dự đoán. Có hai cách sửa:
- gói cả 5 bước trong một giao dịch;
- thêm cột `status ENUM('running','done','failed')` và chỉ đọc lần chạy `done`.

Cách thứ hai hợp hơn khi huấn luyện lâu, vì không giữ giao dịch mở nhiều phút.

### 5.2 Lỗi và chạy tiếp: trường hợp lần chạy 14

Khi thêm mô hình Trans2Vec-CAT, lần chạy đầu bị lỗi theo trình tự sau:
1. Script tạo `model_run` id 14, rồi ghi vector CAT vào `article_vector`.
2. Vector CAT có 384 chiều nên MariaDB từ chối, báo lỗi 1292: cột là `VECTOR(128)`.
3. Ngoại lệ làm script dừng. Giao dịch đang mở bị **rollback**: dòng `model_run` 14 và phần vector đã chèn đều biến mất.

Có hai quan sát:
1. **Kiểu `VECTOR(n)` là một ràng buộc thật.** Dữ liệu sai chiều bị chặn ngay ở CSDL, không lọt vào làm hỏng các phép tính khoảng cách về sau.
2. **`AUTO_INCREMENT` không bị rollback**, nên lần chạy kế tiếp nhận id 15. Đây là hành vi có chủ đích: bộ đếm tự tăng không bị khóa tới cuối giao dịch, để các giao dịch song song không phải chờ nhau. Khóa tự tăng chỉ bảo đảm duy nhất, không bảo đảm liên tục.

Sau sự cố, `train_variants.py` được sửa để **chạy tiếp được**. Mỗi bước kiểm tra trong `model_run` xem lần chạy loại đó đã có chưa; nếu có thì nạp lại mô hình đã lưu thay vì huấn luyện lại. Đây là idempotency ở mức ứng dụng, dựa trên chính dữ liệu trong CSDL.

### 5.3 Thu thập RSS: một báo, một giao dịch

`fetch_news.py` xử lý mỗi báo trong **một giao dịch riêng**:
1. Gửi yêu cầu HTTP có điều kiện (`If-None-Match`, `If-Modified-Since`).
2. `INSERT IGNORE` từng tin. Số dòng ảnh hưởng cho biết tin nào thật sự mới.
3. Cập nhật `etag` của nguồn.
4. Ghi `fetch_log`.
5. `COMMIT`.

Nếu một báo lỗi, giao dịch của báo đó rollback rồi ghi một dòng `fetch_log` báo lỗi; các báo khác không bị ảnh hưởng. ETag phải được cập nhật **cùng giao dịch** với tin đã lưu. Nếu tách riêng, có thể ETag mới được lưu còn tin thì không, và lần sau máy chủ trả 304 khiến tin bị mất vĩnh viễn. Lần chạy đầu thu được 49, 50 và 60 tin từ ba báo (116–338 ms). Chạy lại ngay chỉ có 1 tin mới thật, không trùng.

### 5.4 Ghi trực tuyến và mức cô lập

Kết nối chính của ứng dụng đặt `autocommit=True`. Mỗi lệnh ghi nhật ký có hiệu lực ngay và độc lập với các thao tác khác. Nút "Lấy tin ngay" dùng kết nối riêng, vì cần giao dịch tường minh như Mục 5.3.

`autocommit` còn quan trọng vì một lý do ít được để ý:
- Mức cô lập mặc định của InnoDB là `REPEATABLE READ`: mọi `SELECT` trong một giao dịch đọc cùng một ảnh chụp, tạo ở lần đọc đầu tiên.
- Ứng dụng web giữ kết nối suốt vòng đời tiến trình. Nếu không autocommit, giao dịch đầu tiên không bao giờ kết thúc, và ứng dụng sẽ **không bao giờ thấy** tin RSS hay kết quả huấn luyện mới.
- Với autocommit, mỗi `SELECT` là một giao dịch riêng nên luôn đọc dữ liệu đã commit mới nhất.

Streamlit chạy mỗi phiên trong một luồng, còn kết nối `pymysql` không an toàn khi dùng từ nhiều luồng. Vì vậy các truy vấn đi qua một `threading.Lock` chung. Khi có nhiều người dùng, nên thay bằng connection pool.
