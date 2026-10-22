# 04_review · ui-contrast-fix

**Agent:** code-reviewer (phiên điều phối chép nguyên kết quả agent trả về) · **Ngày:** 22/10/2026 · **Vòng:** 1

## Phạm vi đã review
- Chỉ review 9 khối trong `logs/03_codex.diff`, đối chiếu với file hiện tại `src/system/app/streamlit_app.py` (dòng 93, 114–118, 248–249, 304, 315–316, 350, 822, 830). Không dùng `git diff`, vì file có sẵn thay đổi chưa commit từ trước task này.
- Cách kiểm: đọc `02_dac_ta.md`, `03_trien_khai.md` và file diff. Grep file hiện tại theo `64748B`, `summary`, các selector `.t2v-sec`, `.t2v-cfoot`, `.fl`, `.t2v-sc3`, `stBaseButton-primary`, `txt(`, `isinstance`. Đọc thêm ngữ cảnh dòng 630–669 và 790–835, cùng DDL `src/system/db/feed.sql` (`title NOT NULL`, `summary NULL`).
- Không chạy app, không đo tương phản bằng `contrast.py` (việc của tester). Không gọi skill `code-review`/`security-review` theo git diff, vì git diff lẫn thay đổi ngoài task. Phần thay đổi không chạm SQL hay dữ liệu đầu vào mới. `txt()` vẫn đi qua `e()` (html.escape) nên không mở thêm XSS.

## Phát hiện

| # | Mức | File:dòng | Phát hiện | Đề xuất sửa |
|---|---|---|---|---|
| 1 | Nhỏ | src/system/app/streamlit_app.py:350 | Comment của `txt` chỉ nói "Bỏ NaN". Hàm này còn được dùng để xử lý `None` (cột NULL toàn bộ) và `pd.NA`, nên comment chưa nói đủ lý do. | Có thể viết lại thành: `# summary NULL thành NaN/None/pd.NA; NaN truthy nên "or" không chặn được, str(NaN) ra "nan"`. Không bắt buộc. |
| 2 | Đề xuất | src/system/app/streamlit_app.py:116 | Hover giữ `brightness(1.1)`. Reviewer tự tính lại: nếu filter nhân trên sRGB thì ra `#0F809E`, chữ trắng ≈ 4,56:1. Nếu nhân trên giá trị tuyến tính thì ≈ 4,99:1. Cả hai cách đều đạt, nhưng cách sRGB chỉ dư khoảng 0,06 so với ngưỡng 4,5. Đây là số tính tay, chưa đo bằng `contrast.py`. | Tester đo thật cho AC-3. Muốn dư nhiều hơn thì hạ xuống `brightness(1.05)`. Không bắt buộc. |
| 3 | Đề xuất | src/system/app/streamlit_app.py:341, 822 | Khi không có mô tả, `<div class="t2v-nsum"></div>` vẫn được render rỗng, kèm `margin-top: 4px`. Đặc tả chấp nhận cách này. | Giữ nguyên. Chỉ ghi nhận cho tester khi soi ảnh AC-11. |
| 4 | Đề xuất | (quy trình) AC-12 | Cách kiểm AC-12 trong đặc tả là "`git diff --stat` chỉ có `streamlit_app.py`". Cách này không phân biệt được, vì repo đang có hàng chục file sửa sẵn từ trước. | Tester dùng `diff -u logs/streamlit_app.before.py src/system/app/streamlit_app.py`, kèm so `git status --porcelain` trước và sau, thay cho `git diff --stat`. |

Không có lỗi Nghiêm trọng hay Lớn.

Các điểm đã kiểm theo yêu cầu của phiên điều phối:
- **`txt()` với `pd.NA`, `None`, `NaN`:** `isinstance(x, str)` trả False với cả ba nên ra `""`. `np.str_` là lớp con của `str` nên vẫn giữ nguyên chuỗi. Không ném lỗi, vì không gọi `bool(pd.NA)`.
- **Chỗ khác còn dùng summary hoặc NaN:** chỉ còn 2 chỗ dùng `r.summary` (822, 830), cả hai đã qua `txt`. Không còn `summary or`. `r.title` là `NOT NULL` trong DDL nên an toàn. `pred_category` (817) đã có `isinstance` từ trước. Dòng 816 (`published_at` với `NaT`) nằm ngoài phạm vi, đặc tả đã ghi nhận.
- **Selector trùng hoặc bị rule sau ghi đè:** không có rule nào sau dòng 93, 249, 304, 315 ghi đè `.t2v-sec`, `.t2v-cfoot`, `.t2v-table .fl`, `.t2v-sc3 small`. `.fl` chỉ được định nghĩa ở dòng 304. Không có rule `tr.sel .fl`.
- **`.t2v-sc3 .on small` còn ghi đè màu không:** còn. Dòng 316 có specificity (0,2,1), cao hơn (0,1,1) của dòng 315 và đứng sau, nên ô `.on` vẫn dùng `#67E8F9`. Đúng như đặc tả yêu cầu giữ nguyên.
- **Shorthand `font` có làm mất weight không:**
  - `.t2v-sec` vẫn giữ `600`.
  - `.t2v-cfoot`, `.fl`, `.t2v-sc3 small` trước và sau đều là shorthand không có weight. Weight và line-height về `normal` giống hệt trước, nên không có thay đổi nào ngoài ý muốn.
- **Tương phản dải gradient:** reviewer ước tính tay màu ở giữa dải `#0E7490`→`#4F46E5`, chữ trắng khoảng 6:1, không thấp hơn hai đầu. Tester vẫn đo 3 điểm theo AC-2.
- **Luật dự án:**
  - Không có mật khẩu, không có đường dẫn mới.
  - Phần RSS (`fetch_news`, `feed_item`) không bị xóa, chỉ đổi cách đọc `summary`.
  - Comment bằng tiếng Việt và có giải thích lý do.
  - Định dạng số (`vn`, `num`) không đổi.
  - Chỉ một file bị sửa.

## Tiêu chí nghiệm thu

| AC | Kết luận | Căn cứ |
|---|---|---|
| AC-1 | đạt | Dòng 114: `linear-gradient(90deg, #0E7490, #4F46E5 60%, #4338CA)`. Selector `stBaseButton-primary` không còn `#06B6D4`. Dòng 220 vẫn còn `#06B6D4` nhưng thuộc selector khác. |
| AC-2 | để tester | Cần chạy `contrast.py` cho 3 điểm màu. Bản review gốc ghi trắng/`#0E7490` = 5,36:1. |
| AC-3 | để tester | `brightness(1.1)` được giữ. Codex báo 4,56:1, reviewer tính tay cũng khớp (xem phát hiện #2). Cần đo thật. |
| AC-4 | để tester | Cần ảnh chụp, gồm cả trạng thái focus khi nhấn Tab. CSS focus không bị đổi. |
| AC-5 | đạt | Grep `64748B` ra đúng 2 dòng: 75 (`stIconMaterial`) và 148 (`.dot.off`). |
| AC-6 | đạt | Dòng 93, 249, 304, 315 đều là `11px` và `color: #94A3B8`. Không còn `10px` ở 4 selector này. |
| AC-7 | để tester | Cần chạy `contrast.py` trên `#07090E`, `#0C0F17`, `#1E1B4B`. |
| AC-8 | để tester | Cần ảnh trước và sau để kiểm xuống dòng. Cỡ chữ tăng 1px ở `.t2v-sec`, `.fl`, `.t2v-sc3 small`. |
| AC-9 | đạt | Grep `summary or` ra 0 dòng. `txt(r.summary)` có ở 2 chỗ (822, 830). `txt` dùng `isinstance(x, str)` (350). |
| AC-10 | đạt về logic, để tester chạy xác nhận | Với `isinstance(x, str)`: `None`, `float('nan')`, `pd.NA` cho ra `""`, còn `"abc"` cho ra `"abc"`. Đặc tả yêu cầu dán output thật từ `.venv-exp`. |
| AC-11 | để tester | Cần SQL đếm NULL và soi DOM tìm `.t2v-nsum`. |
| AC-12 | để tester | Developer báo `py_compile` OK. Còn phải chạy 4 trang. Cách kiểm "git diff --stat" cần thay bằng diff với file before (xem phát hiện #4). |
| AC-13 | để tester | Cần đếm `classify_log` và `search_log` trước và sau kiểm thử. |

**Kết luận chung:** phần code đạt cả 5 AC kiểm được bằng đọc code (1, 5, 6, 9, 10). Không có lỗi Nghiêm trọng hay Lớn, chỉ có 1 lỗi Nhỏ (comment) và 3 đề xuất. Các AC 2–4, 7, 8, 10–13 chờ tester đo và chụp ảnh.
