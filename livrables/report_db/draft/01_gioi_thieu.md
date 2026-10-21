## 1. Giới thiệu

### 1.1 Bối cảnh

Báo cáo này đi cùng bài khảo sát môn Tri thức dữ liệu về biểu diễn Trans2Vec cho tin tức tiếng Việt [@survey]. Trans2Vec coi mỗi bài báo là một *transaction* (tập các từ đặc trưng), khai phá các *tập phổ biến* (frequent itemsets, FI), rồi học vector cho bài bằng mô hình Paragraph Vector [@trans2vec; @le2014].

Thực nghiệm của bài khảo sát chạy trên tệp và bộ nhớ của Python. Cách làm đó đủ cho nghiên cứu nhưng chưa phải một hệ thống dùng được: không có chỗ lưu và so sánh các lần huấn luyện, không tìm kiếm trực tuyến được, không ghi lại truy vấn, và không nhận được tin mới.

Phần CSDL của đề tài trả lời câu hỏi: **lưu trữ và truy vấn dữ liệu của một hệ thống phân loại và tìm kiếm tin tức tiếng Việt thế nào cho đúng và đủ nhanh**. Hệ thống phải xử lý cùng lúc dữ liệu quan hệ có ràng buộc toàn vẹn, dữ liệu bán cấu trúc (siêu tham số, phân phối xác suất), vector dày 128 chiều, và văn bản cần tìm kiếm toàn văn bằng một ngôn ngữ có dấu thanh và từ ghép nhiều âm tiết.

### 1.2 Mục tiêu và phạm vi

1. Thiết kế lược đồ quan hệ cho toàn bộ vòng đời dữ liệu, từ văn bản gốc tới nhật ký, kèm lý do của từng lựa chọn.
2. Chọn và cấu hình chỉ mục (B+tree, toàn văn, vector, phân vùng), kiểm chứng bằng `EXPLAIN` và số đo.
3. Kết hợp MariaDB với engine tìm kiếm chuyên dụng Manticore Search, và chỉ rõ hệ nào giữ dữ liệu gốc.
4. Đo đạc để trả lời bốn câu hỏi:
   - nên dùng InnoDB FULLTEXT hay Manticore để tìm kiếm toàn văn;
   - nên dùng chỉ mục vector của MariaDB hay của Manticore;
   - hybrid có hơn từng thành phần không;
   - nên giữ hay gộp dấu khi đánh chỉ mục.
5. Xây ứng dụng minh họa chạy trên dữ liệu thật.

Các mô hình học máy và cách đánh giá chúng thuộc phạm vi bài khảo sát; báo cáo này chỉ dùng lại kết quả khi cần. Mọi số liệu đo trên một máy macOS. MariaDB và Manticore chạy trong Docker (VM 7,6 GB RAM); client là Python 3.11. Báo cáo không xét replication, phân tán và phân quyền nhiều người dùng.

Mã nguồn nằm trong `src/system/`: lược đồ ở `db/`, nạp dữ liệu và huấn luyện ở `pipeline/`, ứng dụng ở `app/`, thực nghiệm ở `bench/`.
