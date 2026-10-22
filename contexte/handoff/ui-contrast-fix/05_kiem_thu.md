# 05_kiem_thu · ui-contrast-fix
**Agent:** tester · **Ngày:** 22/10/2026 · Kết quả: **12/13 đạt, 1 đạt một phần (AC-8)**

Môi trường: t2v-mariadb, t2v-manticore healthy; check_setup.py OK; py_compile PYC_OK. Streamlit không khởi động lại (tải lại trang, script nạp lại; computed style trong trình duyệt đã khớp CSS mới).
Mốc trước kiểm thử: search_log MAX(id)=9, COUNT=2; classify_log MAX(id)=56, COUNT=39.

| AC | Cách kiểm | Kết quả | Bằng chứng |
|---|---|---|---|
| AC-1 | grep dòng 114 | Đạt | `linear-gradient(90deg, #0E7490, #4F46E5 60%, #4338CA)`; computed style trình duyệt: `rgb(14,116,144), rgb(79,70,229) 60%, rgb(67,56,202)`, chữ `rgb(255,255,255)` |
| AC-2 | contrast.py | Đạt | trắng/#0E7490 = 5,36:1; /#4F46E5 = 6,29:1; /#4338CA = 7,90:1 |
| AC-3 | brightness(1.1): #0E7490 -> (15,128,158) = #0F809E; đo lại | Đạt | trắng/#0F809E = 4,56:1 (khớp số Codex); computed filter hover = `brightness(1.1)`; ảnh `classify-btn-hover.png` |
| AC-4 | Ảnh 1440x900, focus bằng phím | Đạt | `classify-result.png`, `classify-btn-focus.png` (viền cyan box-shadow 3,2px, :focus-visible = true), `classify-btn-hover.png`. Nút "Phân loại ngay" gradient cyan đậm sang indigo, chữ trắng rõ. Nút "Lấy tin ngay" không chụp (không bấm/không ghi RSS), dùng cùng selector primary nên cùng CSS; trang tin xem `news-full.png` |
| AC-5 | grep -i 64748B | Đạt | đúng 2 dòng: 75 (icon `stIconMaterial`), 148 (`.dot.off`) |
| AC-6 | grep + computed style | Đạt | `.t2v-sec` dòng 93, `.t2v-cfoot` 249, `.fl` 304, `.sc3 small` 315 đều `#94A3B8`, 11px; computed: sec/cfoot/fl/small = rgb(148,163,184) 11px |
| AC-7 | contrast.py | Đạt | #94A3B8 trên #07090E 7,77; #0C0F17 7,47; #1E1B4B 6,24 (đều ≥ 4,5) |
| AC-8 | Ảnh + đo chiều cao | **Đạt một phần** | Chữ đọc rõ trên mọi ảnh (`classify-result.png`, `search-result.png`, `data-eval.png`). NHƯNG khi đo chiều cao với 10px (chèn CSS tạm, không sửa code): `.fl` hàng 2-3 cao 26px -> 42px (11px), tức đường dẫn tệp xuống thêm 1 dòng ở khoảng 2/3 hàng đầu (hàng 3: 157 -> 173px). `.sc3 small` không xuống dòng (14px một dòng). Sidebar `.t2v-sec` và `.t2v-cfoot` không xuống dòng. Vi phạm nhẹ vế "không xuống dòng mới" của AC; không ảnh hưởng đọc/bố cục lớn |
| AC-9 | grep | Đạt | `summary or` = 0 dòng; `txt(r.summary)` ở dòng 822 và 830 |
| AC-10 | Python .venv-exp | Đạt | `None->''`, `nan->''`, `<NA>->''`, `'abc'->'abc'` |
| AC-11 | SQL + DOM | Đạt | v_latest_news có 1 tin summary NULL/rỗng, nằm trong 30 tin đầu; DOM: 30 `.t2v-nsum`, 1 rỗng, `/\bnan\b/i` trên body.innerText = false; thẻ tin: `news-null-summary-card.png` ("Những tấm lòng vàng 22.10.2026", không có chữ nan) |
| AC-12 | py_compile, 4 trang | Đạt | PYC_OK; mở đủ 4 trang, không Traceback/Exception, không pageerror; `git status` không file mới ngoài phạm vi từ task (streamlit_app.py đã sửa từ trước nên không đối chiếu diff) |
| AC-13 | Đếm log | Đạt | xem dưới |

## Dọn log
Đã xóa: search_log 2 dòng (id > 9), classify_log 1 dòng (id > 56). Sau dọn: search_log MAX=9 COUNT=2; classify_log MAX=56 COUNT=39 (bằng mốc ban đầu). Không bấm "Lấy tin ngay", "Phân loại N tin", "Phân loại lại" (feed_item không bị ghi).

## Ảnh (contexte/handoff/ui-contrast-fix/shots/)
classify-empty.png, classify-result.png, classify-btn-hover.png, classify-btn-focus.png, search-result.png, data-eval.png, news-full.png, news-null-summary-card.png. Script: shoot_ui.cjs, check2.cjs, check3.cjs.

## Ghi chú
- AC-8: gợi ý cho developer nếu muốn đạt chặt: cho `.t2v-table .fl` `word-break: break-all` hoặc giữ 10px cho `.fl` (vẫn đổi màu `#94A3B8` đủ tương phản). Không thuộc quyền tester sửa.
