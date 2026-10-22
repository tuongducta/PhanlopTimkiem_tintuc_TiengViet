# Nhiệm vụ (vòng sửa 2, cuối): đổi đúng MỘT rule CSS
File duy nhất được sửa: src/system/app/streamlit_app.py. Không sửa file khác, không tạo file mới.

Thay rule CSS hiện tại (khoảng dòng 305):
`.t2v-table .fl.path { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 420px; }`
bằng:
`.t2v-table .fl.path { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 0; min-width: 100%; }`

Lý do: width:0 làm div không góp vào min-content của cột trong bảng auto layout (hết tràn bảng, cột FI và Điểm không bị ép); min-width:100% giãn bằng ô khi bố cục nên "…" hiện đúng.
Được thêm comment tiếng Việt ngắn giải thích vì sao width:0 (trong chuỗi CSS, dạng /* ... */ cuối dòng hoặc dòng trên).
Không đụng gì khác: không đổi table-layout, HTML, title, màu, cỡ chữ, comment khác.
Luật: không chạy schema.sql, sync_manticore.py, benchmark; không cài thư viện; không git commit; không sửa sources/.
Tự kiểm: .venv-exp/bin/python -m py_compile src/system/app/streamlit_app.py
