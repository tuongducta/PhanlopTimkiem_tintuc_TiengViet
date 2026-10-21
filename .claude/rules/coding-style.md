# Quy tắc code
- Tên biến và hàm tiếng Anh; comment và docstring tiếng Việt, giải thích *vì sao* chứ không lặp lại code.
- Không hard-code mật khẩu: đọc từ biến môi trường (xem `src/system/config.py`).
- Đường dẫn tính từ vị trí file (`Path(__file__).resolve().parents[...]`), không phụ thuộc thư mục đang đứng.
- Script chạy lâu phải in tiến độ và chạy tiếp được sau lỗi (xem `train_variants.py`).
