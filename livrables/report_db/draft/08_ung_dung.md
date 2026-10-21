## 8. Ứng dụng

Ứng dụng viết bằng Streamlit (`src/system/app/`), gồm bốn trang theo bản phác đã duyệt. Khi khởi động, ứng dụng nạp vào bộ nhớ 5 mô hình Doc2Vec, 7 bộ phân loại, bảng FI và từ điển idf (khoảng 2 giây). Mọi dữ liệu còn lại được đọc từ hai CSDL theo từng yêu cầu.

**Phân loại bài báo** (Hình 8.1). Ứng dụng so sánh sáu mô hình:
- mốc Trans2Vec gốc, chạy đúng mã của tác giả;
- bốn biến thể TRANS-IT, TRANS-FI, Trans2Vec-IND, Trans2Vec-JOI;
- mô hình cải tiến Trans2Vec-CAT, nối vector ba biến thể rồi đưa vào hồi quy logistic.

Danh sách mô hình và Macro-F1 không viết cứng trong mã. Ứng dụng đọc từ `model_run` và `eval_result`, lấy lần chạy mới nhất của mỗi loại. Vì vậy sau khi huấn luyện lại, mô hình mới tự hiện ra mà không phải sửa code. Trên 50.373 bài test, Macro-F1 lần lượt là:

| Mô hình | Macro-F1 |
|---|---|
| Mốc gốc | 0,823 |
| TRANS-IT | 0,847 |
| TRANS-FI | 0,826 |
| IND | 0,842 |
| JOI | 0,849 |
| CAT | **0,857** |

Phân loại một bài với cả sáu mô hình mất trung bình khoảng 10 ms. `classify_log` chỉ lưu hash SHA-256 của văn bản đầu vào, không lưu văn bản.

![Hình 8.1. Trang Phân loại: sáu thẻ mô hình với top-3 chuyên mục; phần dưới giải thích dự đoán bằng các FI khớp với bài.](figures/fig_ui_classify.png){width=62%}

**Tìm kiếm** (Hình 8.2):
- Người dùng chọn chế độ (BM25, vector, hybrid), lọc chuyên mục và số kết quả.
- Bảng kết quả hiện hạng của mỗi bài theo BM25 và theo vector, nên thấy được RRF gộp hai nguồn thế nào.
- Khung chi tiết lấy từ MariaDB phần đầu bài, các FI của bài (qua `article_itemset`) và tệp nguồn.

![Hình 8.2. Trang Tìm kiếm ở chế độ hybrid.](figures/fig_ui_search.png){width=62%}

**Dữ liệu và đánh giá:** trang hoàn toàn dựa trên SQL:
- kết quả từ `eval_result`;
- ma trận nhầm lẫn từ `v_confusion` (chọn được mô hình);
- `v_corpus_stats`, `v_category_fi`;
- thống kê nhật ký.

Kết quả được giữ trong bộ nhớ đệm 1 giờ.

**Tin mới nhất:**
- Trang hiển thị trạng thái ba nguồn RSS (từ `fetch_log`) và tin từ `v_latest_news`.
- Nút "Lấy tin ngay" gọi quy trình ở Mục 5.3, tối đa một lần mỗi 5 phút.
- Người dùng phân loại được từng tin hoặc cả loạt tin bằng mô hình CAT. Kết quả ghi vào `feed_item.pred_category`.
- RSS chỉ có tiêu đề và mô tả ngắn, nên phân phối dữ liệu khác bài VNTC. Cần lưu ý điều này khi đọc kết quả.

**Kiểm thử:**
- `streamlit.testing.v1.AppTest` đi qua cả bốn trang (phân loại, các chế độ tìm kiếm có lọc, ma trận nhầm lẫn, phân loại tin RSS), không có lỗi.
- Giao diện được chụp màn hình bằng Chrome headless để kiểm tra hiển thị.
- Dòng nhật ký do kiểm thử sinh ra đã được xóa, để số liệu nhật ký chỉ phản ánh lượt dùng thật.
