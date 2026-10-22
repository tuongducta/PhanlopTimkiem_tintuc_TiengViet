# Nhiệm vụ: vòng sửa 1 (v2) cho ui-contrast-fix
File DUY NHẤT được sửa: src/system/app/streamlit_app.py. Không sửa file khác, không tạo file mới.

## Việc 1 (AC-8): đường dẫn tệp không xuống dòng
Trong page_search (khoảng dòng 639) có `<div class="fl">{e(d["file"])}</div>` ở cột "Bài viết".
- Đổi thành `<div class="fl path" title="{e(d["file"])}">{e(d["file"])}</div>`.
- Thêm CSS ngay sau rule `.t2v-table .fl` (dòng ~304):
  `.t2v-table .fl.path { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 420px; }`
  (display:block đã có sẵn vì là div; max-width để cột không phình làm bảng tràn).
- GIỮ 11px và #94A3B8. KHÔNG đổi rule `.t2v-table .fl` chung. KHÔNG đụng `<div class="fl">BM25 #… · vec #…</div>` ở cột Điểm.

## Việc 2: viết lại comment của `txt` (dòng ~350)
Thay comment cuối dòng bằng:
`# summary NULL ra None/NaN/pd.NA; NaN truthy nên "or" không chặn được và str(NaN) thành "nan"`
Giữ nguyên biểu thức lambda.

## Luật
Không làm gì khác (màu, cỡ, hover, bố cục, CSDL). Comment tiếng Việt giải thích vì sao. Không chạy schema.sql, sync_manticore.py, benchmark; không cài thư viện; không git commit; không sửa sources/.
Tự kiểm: .venv-exp/bin/python -m py_compile src/system/app/streamlit_app.py
