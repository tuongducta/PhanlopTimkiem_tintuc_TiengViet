# 05_kiem_thu_v2 · ui-contrast-fix (vòng sửa 1)
**Agent:** tester · 22/10/2026 · Kết quả: **AC-6, AC-12, AC-13 đạt; AC-8 KHÔNG đạt (hồi quy: bảng tràn ngang, cột Điểm bị che)**. 3/4 AC kiểm lại đạt.

Môi trường: t2v-mariadb, t2v-manticore healthy; check_setup.py OK; py_compile PYC_OK. Không khởi động lại Streamlit.
Mốc trước: search_log MAX=9 COUNT=2; classify_log MAX=56 COUNT=39.

| AC | Cách kiểm | Kết quả | Bằng chứng |
|---|---|---|---|
| AC-6 | getComputedStyle | Đạt | `.t2v-sec`, `.t2v-cfoot` (2 phần tử), `.t2v-table .fl`, `.t2v-sc3 small` đều rgb(148,163,184), 11px |
| AC-8 (a) đường dẫn 1 dòng, title | đo 10 `.fl.path` | Đạt về chữ | white-space nowrap, text-overflow ellipsis, cao 14px (1 dòng), title = đường dẫn đầy đủ (10/10). Chưa thấy cắt "…" vì đường dẫn (39-41 ký tự) vừa 271px; max-width 420px không phát huy |
| AC-8 (b) `.t2v-sc3 small`, `.t2v-sec`, `.t2v-cfoot` không xuống dòng | đo chiều cao | Đạt | small 14px; sec 14px; cfoot 41px (2 phần tử, white-space normal, giống vòng 1) |
| AC-8 (c) bảng không tràn ngang | đo bảng và wrapper | **Không đạt** | bảng 608px trong wrapper 554px (overflow-x: auto, scrollWidth 608 > clientWidth 554). Cột Điểm kết thúc ở x=989 > mép wrapper 935: điểm số (0,0251...) và dòng "BM25 #… · vec #…" bị che, phải cuộn ngang mới thấy. Ảnh `v2-search-result.png` xác nhận cột Điểm bị cắt ở mép phải. Vòng 1: bảng vừa khít (554/554), không cuộn |
| AC-8 (d) cột khác không bị ép hẹp | đo th | **Không đạt** | xem bảng số đo; FI trong bài hẹp 120 -> 88, Điểm 84,9 -> 71,2, Bài viết rộng 198 -> 299 |
| AC-8 (e) `.fl` cột Điểm không bị cắt | scrollWidth | Đạt về cắt chữ, kém về bố cục | không có ellipsis, nhưng xuống 3-4 dòng (cao 42-56px, vòng 1: 28-42px) và cả cột nằm ngoài vùng nhìn thấy |
| AC-12 | py_compile; mở 4 trang | Đạt | PYC_OK; 4 trang không Traceback/Exception, pageerror rỗng |
| AC-13 | xóa log | Đạt | xem dưới |

## Số đo cột (px, viewport 1440x900, truy vấn "giá vàng tăng mạnh", Hybrid, Top 10)
Vòng 1 mô phỏng bằng CSS tạm ghi đè `.fl.path` về normal/none/none/none (không sửa code); chiều cao hàng 3 của số đo vòng 1 ghi trong 05_kiem_thu.md khác truy vấn nên không dùng so sánh trực tiếp; ảnh gốc `search-result.png` khớp với mô phỏng (bảng khít, 4 cột đủ).

| Cột | Vòng 1 (mô phỏng) | v2 (thật) | Đổi |
|---|---|---|---|
| # | 44,4 | 44,4 | 0 |
| Bài viết | 198,2 | 298,6 | +100 |
| Chuyên mục | 104,2 | 104,2 | 0 |
| FI trong bài | 120,0 | 88,0 | -32 |
| Điểm | 84,9 | 71,2 | -13,7 |
| Tổng bảng | 553,7 (= wrapper) | 608,4 (wrapper 553,7) | +54,7 tràn |
| Chiều cao 3 hàng đầu | 142,2 / 141,4 / 124,6 | 93 / 106,2 / 106,2 | thấp hơn |

Nguyên nhân: `nowrap` làm min-content của cột Bài viết bằng độ dài đường dẫn (~271px), trình duyệt (table-layout auto) lấy phần rộng đó từ FI và Điểm, rồi bảng vượt wrapper. `max-width` trên div không giới hạn cột.

## Gợi ý sửa (cho developer; tester không sửa code)
Đặt `.t2v-table { table-layout: fixed; width: 100% }` với độ rộng cột cố định (hoặc `td:first-child` có `max-width`/`width` cùng `overflow:hidden`), hoặc cho `.fl.path` `display:block; width:0; min-width:100%` để không đóng góp min-content. Khi đó ellipsis mới hoạt động và cột Điểm giữ ~85px.

## Dọn log
search_log: xóa 2 dòng (id > 9); sau dọn MAX=9 COUNT=2. classify_log: xóa 1 dòng (id > 56); sau dọn MAX=56 COUNT=39. Bằng mốc ban đầu. Không bấm nút ghi CSDL ngoài "Phân loại ngay" (một lượt phân loại thử, đã dọn log; tin không bị ghi).

## Ảnh (shots/)
v2-search-result.png, v2-search-result-r1sim.png (mô phỏng vòng 1), v2-classify-result.png. Script: v2check.cjs, ov.cjs.
