---
name: build-docs
description: Build lại survey và báo cáo CSDL từ draft/, kiểm tra trích dẫn và số trang báo cáo (25–30).
---
1. Chạy `scripts/build-docs.sh`. Nếu báo "Khóa trích dẫn không có trong refs.tsv" thì sửa `refs.tsv` hoặc draft, không bỏ qua.
2. Chạy `scripts/count-pages.sh`. Báo cáo CSDL phải nằm trong khoảng 25–30 trang; nếu vượt thì rút gọn draft rồi build lại.
3. Xem các hình mới bằng công cụ đọc ảnh trước khi báo xong.
4. Báo lại: số từ, số tài liệu tham khảo, số trang, file đã đổi.
