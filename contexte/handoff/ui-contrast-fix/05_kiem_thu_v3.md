# 05_kiem_thu_v3 · ui-contrast-fix (vòng sửa 2)
**Agent:** tester · 22/10/2026 · Kết quả: **4/4 AC kiểm lại đạt** (AC-6, AC-8, AC-12, AC-13). Bảng không còn tràn.

Môi trường: t2v-mariadb, t2v-manticore healthy; check_setup.py OK; py_compile streamlit_app.py PYC_OK. Không khởi động lại Streamlit. Mốc trước: search_log MAX=9 COUNT=2; classify_log MAX=56 COUNT=39.

| AC | Cách kiểm | Kết quả | Bằng chứng |
|---|---|---|---|
| AC-6 | getComputedStyle | Đạt | `.t2v-sec`, `.t2v-cfoot` (2), `.t2v-table .fl`, `.t2v-sc3 small` đều rgb(148,163,184), 11px |
| AC-8 (a) `.fl.path` 1 dòng, "…", title | đo 10 phần tử | Đạt | white-space nowrap, text-overflow ellipsis, cao 14px (1 dòng), rộng 166px; scrollWidth > clientWidth ở 10/10 (đường dẫn 39-41 ký tự bị cắt "…", ảnh xác nhận); title = đường dẫn đầy đủ 10/10 |
| AC-8 (b) `.t2v-sc3 small`, `.t2v-sec`, `.t2v-cfoot` không xuống dòng | đo chiều cao | Đạt | small 14px, sec 14px, cfoot 41px (white-space normal, như vòng 1 và v2) |
| AC-8 (c) bảng không tràn | bảng vs wrapper | Đạt | bảng 553,7 = wrapper 553,7; tableScroll=false; docOverflow=false (v2: 608/554 tràn) |
| AC-8 (d) cột không bị ép | đo th | Đạt | FI 120 (= vòng 1), Điểm 89,4 (vòng 1 84,9), Bài viết 193,7 (vòng 1 198,2) |
| AC-8 (e) `.fl` cột Điểm | scrollWidth, chiều cao | Đạt | 0/10 bị cắt; "BM25 #8 · vec #19" cao 28px = 2 dòng (giống vòng 1: 28-42px; v2 42-56px). Điểm số hiển thị đủ trong vùng nhìn thấy |
| AC-12 | py_compile; mở 4 trang | Đạt | PYC_OK; 4 trang không Traceback/Exception, pageerror rỗng |
| AC-13 | dọn log | Đạt | xem dưới |

## Số đo cột (px, 1440x900, "giá vàng tăng mạnh", Hybrid, Top 10)
Vòng 1 và v2 lấy từ 05_kiem_thu_v2.md. Cột "R1 sim v3" là mô phỏng vòng 1 ngay trên bản v3 (CSS tạm), chỉ để đối chiếu.

| Cột | Vòng 1 (mô phỏng) | v2 | v3 (thật) |
|---|---|---|---|
| # | 44,4 | 44,4 | 44,4 |
| Bài viết | 198,2 | 298,6 | 193,7 |
| Chuyên mục | 104,2 | 104,2 | 104,2 |
| FI trong bài | 120,0 | 88,0 | 120,0 |
| Điểm | 84,9 | 71,2 | 89,4 |
| Tổng bảng / wrapper | 553,7 / 553,7 | 608,4 / 553,7 (tràn) | 553,7 / 553,7 (không tràn) |
| Cao 3 hàng đầu | 142,2 / 141,4 / 124,6 | 93 / 106,2 / 106,2 | 145 / 128,2 / 128,2 |
| Dòng `.fl` cột Điểm | 2-3 (28-42px) | 3-4 (42-56px) | 2 (28px) |

Ghi chú: hàng v3 cao hơn v2 vì cột Bài viết hẹp lại (tiêu đề và snippet xuống dòng nhiều hơn); tương đương vòng 1. Mô phỏng vòng 1 chạy lại trên v3 cho 159 / 142,2 / 142,2, cùng cỡ với vòng 1 gốc, cột y hệt v3, nên bố cục đã trở về như vòng 1, chỉ khác tệp nguồn được cắt 1 dòng.

## Dọn log
Phát sinh: search_log 1 dòng, classify_log 1 dòng (id > mốc). Đã xóa; sau dọn search_log MAX=9 COUNT=2, classify_log MAX=56 COUNT=39 (bằng mốc). Không bấm "Lấy tin ngay", "Phân loại N tin", "Phân loại lại".

## Ảnh (shots/)
v3-search-result.png (xem: bảng vừa khít, 4 cột đủ, tệp nguồn có "…", điểm số đủ), v3-classify-result.png, v3-search-result-r1sim.png. Script: v3check.cjs (sao từ v2check.cjs).
