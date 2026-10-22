Đã sửa đúng các mục trong `src/system/app/streamlit_app.py`:

- Nút chính đổi màu đầu gradient từ `#06B6D4` sang `#0E7490`; giữ `brightness(1.1)` vì tương phản chữ trắng trên `#0F809E` đo được **4,56:1**.
- Bốn selector chữ phụ (`.t2v-sec`, `.t2v-cfoot`, `.t2v-table .fl`, `.t2v-sc3 small`) đổi sang cỡ `11px` và màu `#94A3B8`.
- Thêm `txt()` để chỉ nhận summary dạng chuỗi, dùng ở phần hiển thị và phân loại; không còn `summary or` trong file.
- Thêm chú thích ngắn giải thích cách bỏ qua NaN.

Kiểm tra: `.venv-exp/bin/python -m py_compile src/system/app/streamlit_app.py` chạy thành công.