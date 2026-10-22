# 04_review_v2 · ui-contrast-fix · vòng sửa 1

**Agent:** code-reviewer (phiên điều phối chép kết quả agent trả về) · **Ngày:** 22/10/2026 · **Phạm vi:** 3 khối trong `logs/03_codex_v2.diff`, đối chiếu với `src/system/app/streamlit_app.py` hiện tại (dòng 305, 351, 640). Không dùng `git diff` vì file đã có thay đổi chưa commit từ trước.

## Phát hiện

| # | Mức | File:dòng | Phát hiện | Đề xuất sửa |
|---|---|---|---|---|
| 1 | Lớn | `streamlit_app.py:305` (kèm 640, 648) | **Cách này hết xuống dòng bằng cách nới rộng cột, không phải bằng cách cắt chữ.** `.t2v-table` dùng `table-layout: auto` (dòng 286), nên độ rộng tối thiểu của cột lấy theo min-content contribution của nội dung. `div.fl.path` có `width: auto`, `nowrap`, `max-width: 420px` (giá trị px), nên contribution = min(độ rộng cả đường dẫn, 420px). `overflow: hidden` không giảm con số này: quy tắc hạ minimum về 0 chỉ áp cho flex/grid item, quy tắc coi phần trăm vòng là 0 chỉ áp cho giá trị phần trăm. Đường dẫn VNTC khoảng 45–55 ký tự, tức 300–360px ở 11px monospace, ngắn hơn 420px. Hệ quả: dấu "…" hầu như không hiện; cột "Bài viết" rộng ít nhất bằng cả đường dẫn cộng 28px padding. Phần thiếu lấy từ các cột khác. Nhãn chuyên mục là `nowrap`, cột FI ≥ 120px nên không co được. Nếu tổng min-content vượt bề rộng cột trái (`st.columns([7,5])`) thì: (a) bảng hiện thanh cuộn ngang (dòng 648), hoặc (b) chữ `BM25 #… · vec #…` ở cột Điểm xuống thêm dòng, lại vi phạm AC-8. | Chỉ sửa CSS dòng 305: `.t2v-table .fl.path { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 0; min-width: 100%; }`. `width: 0` làm contribution bằng 0; `min-width: 100%` được coi là 0 khi tính intrinsic size nhưng giãn bằng bề rộng ô khi bố cục, nên "…" hiện đúng ở mọi bề rộng. Bỏ `max-width: 420px`. Phương án thay thế kém hơn: `max-width:0` trên `<td>` (phụ thuộc trình duyệt); `table-layout: fixed` kèm `<colgroup>` (đổi bố cục chung của `.t2v-table`, class còn dùng ở dòng 685 và 752). |
| 2 | Nhỏ | `streamlit_app.py:305` | `420px` là số chọn tay, chưa có lý do (`03_trien_khai_v2` ghi "giá trị ước lượng"), không liên quan đến bề rộng thật của cột. | Áp #1 thì bỏ hẳn; nếu giữ thì thêm comment giải thích. |
| 3 | Đề xuất | `streamlit_app.py:640` | `title` chỉ hiện khi rê chuột; bàn phím và màn hình cảm ứng không xem được (WCAG 1.3.1, 2.1.1, tham khảo). Tác động thấp: chữ chỉ bị cắt ở mức hiển thị, trình đọc màn hình vẫn đọc đủ; đường dẫn đầy đủ của bài đang chọn có ở khung chi tiết (dòng 670). | Không bắt buộc. |
| 4 | đạt | `streamlit_app.py:640` | `title="{e(d["file"])}"`: `html.escape` mặc định `quote=True`, thoát cả `"` và `'`; không phá thuộc tính, không XSS. | — |
| 5 | đạt | `streamlit_app.py:644` | `.fl` ở cột Điểm vẫn là `class="fl"`, không bị `.fl.path` áp lên. Khung chi tiết dòng 670 dùng class `file`. `.t2v-table .fl` chung (dòng 304) giữ `11px`, `#94A3B8`. | — |
| 6 | đạt | `streamlit_app.py:351` | Comment của `txt` tiếng Việt, nêu đủ lý do (None/NaN/pd.NA; NaN truthy; `str(NaN)` ra "nan"), đúng `coding-style.md`. | — |

Luật dự án: không có mật khẩu, không có đường dẫn mới, không đụng RSS, không có số hiển thị mới, không chạm SQL.

## AC liên quan

| AC | Kết luận | Căn cứ |
|---|---|---|
| AC-6 | đạt | `.t2v-table .fl` dòng 304 không đổi; `.fl.path` chỉ thêm thuộc tính bố cục; ba selector còn lại không bị đụng. |
| AC-8 | để tester (có rủi ro, xem #1) | Tester kiểm ở 1440×900 trang Tìm kiếm: (1) bảng không có thanh cuộn ngang; (2) cột Điểm không xuống thêm dòng so với `shots/search-result.png`; (3) đường dẫn bị cắt thì có "…" và `title`. Nếu (1) hoặc (2) không đạt thì áp #1. |
| AC-9 | đạt | `txt` vẫn `isinstance(x, str)`; diff chỉ sửa comment. |
| AC-12 | để tester | `py_compile` OK theo developer; còn chạy 4 trang. |

**Kết luận:** code đúng và an toàn, nhưng `max-width: 420px` trong bảng auto layout làm nở cột thay vì cắt "…". Nên đổi sang `width: 0; min-width: 100%` (phát hiện #1, mức Lớn), hoặc đợi tester xác nhận bảng không tràn và cột Điểm không xuống dòng thêm.
