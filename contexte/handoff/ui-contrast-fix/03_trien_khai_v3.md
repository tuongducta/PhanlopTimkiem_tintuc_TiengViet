# 03 Triển khai v3 (ui-contrast-fix, vòng sửa 2)

## File Codex đã sửa
- src/system/app/streamlit_app.py (một rule CSS, dòng 305)

## AC đã làm
Đổi `.t2v-table .fl.path` sang `display:block; ... width:0; min-width:100%` để div không góp vào min-content của cột (hết tràn bảng 608/554px, cột FI và Điểm không bị ép), "…" hiện đúng.

## Diff (diff -u so với logs/streamlit_app.before_v3.py)
```diff
-.t2v-table .fl.path { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 420px; }
+.t2v-table .fl.path { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 0; min-width: 100%; } /* width: 0 tránh làm tăng min-content của cột */
```

## Kiểm
- py_compile: OK
- git status --porcelain: không đổi so với trước khi chạy Codex; không file ngoài phạm vi.
- Codex thoát 0.

## Cách chạy thử
Khởi động lại Streamlit (scripts/run-app.sh), mở trang kết quả tìm kiếm ở viewport hẹp, kiểm bảng không tràn và cột FI, Điểm không bị ép.

## Việc mở
Không. (Cần khởi động lại Streamlit để thấy CSS mới.)
