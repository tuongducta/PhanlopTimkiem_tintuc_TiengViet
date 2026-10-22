# 02_dac_ta · ui-contrast-fix

**Agent:** spec-writer · **Ngày:** 22/10/2026 · **Vòng:** 1

## Đầu vào
- File đã đọc: `contexte/handoff/ui-contrast-fix/00_dau_vao.md`, `contexte/handoff/_template.md`, `src/system/app/streamlit_app.py` (dòng 40–345 CSS, 780–834 trang RSS; chỉ đọc), `src/system/db/feed.sql` (cột `summary TEXT NULL`), `src/system/pipeline/fetch_news.py` (dòng 95: `summary=clean_text(desc) or None`), phần usage của `contrast.py`. Không có `01_kien_truc.md` (task không qua architect).
- Phạm vi được duyệt (từ phiếu duyệt): đúng 3 lỗi #1–#3 của design-review 22/10. Chốt màu, liệt kê selector và dòng cần đổi, viết AC kiểm được. Lỗi #4–#12 và bố cục template nằm ngoài phạm vi.

## Quyết định / Nội dung chính

### Lỗi 1: tương phản chữ của nút chính (mức Nghiêm trọng)

**Hiện trạng:** dòng 114 có `[data-testid="stBaseButton-primary"] { background: linear-gradient(90deg, #06B6D4, #4F46E5 60%, #4338CA); color: #fff; … }`. Theo bản review, chữ trắng trên `#06B6D4` chỉ đạt 2,43:1. Có hai nút dùng kiểu này: "Phân loại ngay" (dòng 480) và "Lấy tin ngay" (dòng 797).

**Chốt phương án A:** đổi điểm đầu gradient từ `#06B6D4` sang `#0E7490` (cyan-700) và giữ chữ trắng.

| | Phương án A (chọn) | Phương án B (loại) |
|---|---|---|
| Thay đổi | Điểm đầu gradient `#06B6D4` → `#0E7490` | Giữ gradient, chữ đổi sang `#07090E` |
| Số đo trong bản review | trắng/`#0E7490` = 5,36:1 | `#07090E`/`#06B6D4` = 11,02:1 |
| Phần còn lại của gradient | Trắng trên `#4F46E5` và `#4338CA` vốn đã cao, chữ trắng đọc tốt trên cả dải | Chữ tối trên `#4F46E5` và `#4338CA` (phần indigo chiếm 40–100% bề ngang) sẽ thấp. Ước tính tay khoảng 3:1, chưa đo, nhiều khả năng dưới 4,5:1 |
| Cảm giác template | Vẫn đi từ cyan sang indigo. Bóng đổ `rgba(6,182,212,…)` giữ nguyên nên ánh cyan vẫn còn | Chữ đen trên nút tím lệch hẳn khỏi template |

Lý do chọn A: chỉ A giữ được tương phản trên toàn dải gradient, vì chữ nằm giữa nút, nơi gradient đã chuyển sang indigo. A cũng chỉ đổi đúng một mã màu.

**Đổi cụ thể (developer):**
1. Dòng 114: trong `linear-gradient(90deg, #06B6D4, #4F46E5 60%, #4338CA)` chỉ thay `#06B6D4` → `#0E7490`. Giữ nguyên các điểm dừng `#4F46E5 60%` và `#4338CA`, `color: #fff`, viền, bo góc, `box-shadow`.
2. Dòng 116 (`:hover`) dùng `filter: brightness(1.1)`, làm nền điểm đầu sáng lên. Ước tính tay `#0E7490 × 1,1` còn khoảng 4,5:1 với chữ trắng, sát ngưỡng và **chưa đo**. Developer đo màu hover thực tế (lấy bằng DevTools hoặc tính `#0E7490 × 1,1` ≈ `#0F809E`) bằng `contrast.py`. Nếu < 4,5:1 thì hạ xuống `brightness(1.05)`. Không đổi gì khác ở hover.
3. Dòng 118 (`:disabled`, `opacity: .45`): giữ nguyên. Theo WCAG 1.4.3, điều khiển bị vô hiệu không phải đạt ngưỡng tương phản.

**Các trạng thái của nút chính sau khi sửa:**

| Trạng thái | Yêu cầu |
|---|---|
| default | Chữ trắng ≥ 4,5:1 với cả 3 điểm màu `#0E7490`, `#4F46E5`, `#4338CA` |
| hover | Chữ trắng ≥ 4,5:1 với điểm đầu sau khi áp `brightness` |
| focus (bàn phím) | Không đổi CSS. Viền focus mặc định của Streamlit vẫn phải hiện (kiểm bằng ảnh chụp khi nhấn Tab) |
| active / loading (`st.spinner`) | Không đổi |
| disabled | Không đổi (`opacity .45`, ngoài ngưỡng WCAG) |

### Lỗi 2: chữ phụ màu `#64748B` quá mờ và quá nhỏ (mức Lớn)

**Kết quả Grep `#64748B` trong `streamlit_app.py` (6 chỗ), phân loại:**

| Dòng | Selector | Loại | Xử lý |
|---|---|---|---|
| 75 | `[data-testid="stSidebar"] label[data-testid="stRadioOption"] [data-testid="stIconMaterial"]` | Icon menu (đồ họa, ngưỡng 3:1) | **Giữ nguyên** |
| 93 | `.t2v-sec` (nhãn "CHỨC NĂNG CHÍNH", dòng 843) | Chữ, 10px, nền thanh bên ≈ `#0C0F17` | **Đổi** |
| 148 | `.dot.off` | Chấm trạng thái (đồ họa) | **Giữ nguyên** |
| 249 | `.t2v-cfoot` (chân thẻ, dòng 529, 536, 719, 751) | Chữ, 11px | **Đổi màu**, cỡ giữ 11px |
| 304 | `.t2v-table .fl` (đường dẫn tệp, hạng BM25/vec, dòng 638, 642) | Chữ, 10px | **Đổi** |
| 315 | `.t2v-sc3 small` (dòng 666) | Chữ, 10px | **Đổi** |

**Chốt:** màu chữ phụ là `#94A3B8`, cỡ tối thiểu **11px**.
- Chọn `#94A3B8` vì giao diện đã dùng màu này cho mọi chữ phụ khác (`.t2v-sub`, `.t2v-mono`, `.t2v-ch p`…), nên không thêm màu mới. Bản review đo được 7,77:1 trên `#07090E`.
- Chọn 11px thay vì 12px để giữ mật độ nhãn mono như template (template dùng 10–11px cho loại nhãn này) và tránh `.t2v-table .fl` hay `.t2v-sc3` bị xuống dòng.

**Đổi cụ thể (developer):**
| Dòng | Trước | Sau |
|---|---|---|
| 93 | `font: 600 10px 'JetBrains Mono', monospace; color: #64748B;` | `font: 600 11px 'JetBrains Mono', monospace; color: #94A3B8;` |
| 249 | `font: 11px 'JetBrains Mono', monospace; color: #64748B;` | `font: 11px 'JetBrains Mono', monospace; color: #94A3B8;` |
| 304 | `font: 10px 'JetBrains Mono', monospace; color: #64748B;` | `font: 11px 'JetBrains Mono', monospace; color: #94A3B8;` |
| 315 | `font: 10px 'JetBrains Mono', monospace; color: #64748B;` | `font: 11px 'JetBrains Mono', monospace; color: #94A3B8;` |

Giữ nguyên `.t2v-sc3 .on small { color: #67E8F9 }` (dòng 316) và mọi chỗ dùng `#475569` (dấu phân cách `.sep`, `.t2v-bar i.lo`, `.t2v-kpi .vl small`). Các chữ 10px khác không dùng `#64748B` (`.t2v-k`, `.t2v-tag`, `.t2v-table th`, `.t2v-sc3 span`, inline style dòng 639…) nằm ngoài phạm vi lỗi #2. Không đổi.

### Lỗi 3: hiện chữ "nan" ở tin RSS không có mô tả (mức Lớn)

**Nguyên nhân:** `feed_item.summary` là `NULL` khi RSS không có mô tả. Pandas đọc giá trị này thành `NaN` (kiểu float). `NaN` là truthy nên `r.summary or ""` trả lại `NaN`, và `html.escape(str(NaN))` cho ra chữ `nan`.

**Chỗ bị lỗi (2 chỗ, cùng nguyên nhân):**
| Dòng | Code hiện tại | Hậu quả |
|---|---|---|
| 821 | `f'<div class="t2v-nsum">{e(r.summary or "")}</div>'` | Hiện chữ "nan" trên thẻ tin |
| 829 | `clf.predict(f"{r.title}\n{r.summary or ''}", log=True)` | Đưa chữ "nan" vào văn bản phân loại và vào `classify_log` |

Dòng 829 không có trong danh sách của bản review, nhưng có cùng nguyên nhân với lỗi #3 và nằm ngay trong `classify_news()` mà trang RSS gọi. Đặc tả gộp vào để sửa dứt điểm.

**Chốt:** dùng cách kiểm tra mà bản review đề xuất, `isinstance(x, str)`. Để không lặp code, developer có thể khai báo một hàm nhỏ cạnh các tiện ích HTML (khoảng dòng 349–352), ví dụ `txt = lambda x: x if isinstance(x, str) else ""`, rồi dùng tại dòng 821 và 829. Có thể viết `isinstance` trực tiếp ở hai chỗ; cả hai cách đều đạt.
- Trạng thái rỗng: tin không có mô tả **không hiện khối mô tả có chữ**. `<div class="t2v-nsum"></div>` rỗng là chấp nhận được vì không chiếm chiều cao đáng kể, hoặc bỏ hẳn div khi rỗng. Không thêm câu kiểu "Không có mô tả" (giữ bố cục template, không đổi nội dung chữ).
- Văn bản phân loại khi không có mô tả là `f"{title}\n"`, không chứa `nan`.

### Danh sách file được phép sửa
- `src/system/app/streamlit_app.py`: **file duy nhất**. Không cần sửa DDL, pipeline hay file khác. `fetch_news.py` ghi `None` đúng; lỗi chỉ nằm ở tầng hiển thị.

### Ngoài phạm vi
- Bố cục và cấu trúc theo `sources/template_demo/`: không thêm, bớt hay di chuyển khối nào.
- Lỗi #4–#12 của bản design-review 22/10.
- Màu `#475569` dùng cho dấu phân cách; icon menu (dòng 75) và `.dot.off` (dòng 148).
- Các chữ 10px khác không dùng `#64748B`; chữ trên nút phụ (`stBaseButton-secondary`), pills, segmented control.
- Lỗi tiềm ẩn ở dòng 815 (`if r.published_at` với `NaT`): ghi nhận ở mục "Việc mở", không sửa trong task này.

## Tiêu chí nghiệm thu (AC)
`CONTRAST` = `python3 ~/.claude/plugins/cache/ux-ui-agent-skills/ux-ui-agent-skills/2.10.0/scripts/contrast.py`. Cú pháp: `CONTRAST "#fg" "#bg"`.

| AC | Mô tả | Cách kiểm | Trạng thái |
|---|---|---|---|
| AC-1 | Điểm đầu gradient của nút chính là `#0E7490`, không còn `#06B6D4` trong selector `stBaseButton-primary`. Các điểm dừng `#4F46E5 60%`, `#4338CA` giữ nguyên | Grep `stBaseButton-primary.*linear-gradient\(90deg, #0E7490, #4F46E5 60%, #4338CA\)` khớp 1 dòng | chưa làm |
| AC-2 | Chữ trắng của nút chính đạt **≥ 4,5:1** với cả ba điểm màu nền ở trạng thái default | Chạy `CONTRAST "#FFFFFF" "#0E7490"`, `CONTRAST "#FFFFFF" "#4F46E5"`, `CONTRAST "#FFFFFF" "#4338CA"`. Cả 3 kết quả ≥ 4,5 (dán output thật vào 03/04) | chưa làm |
| AC-3 | Ở trạng thái hover, chữ trắng vẫn đạt **≥ 4,5:1** với điểm đầu gradient sau khi áp `filter: brightness(…)` | Tính màu sau filter (nhân từng kênh RGB của `#0E7490` với hệ số brightness, làm tròn), chạy `CONTRAST "#FFFFFF" "<màu đó>"` ≥ 4,5. Nếu không đạt thì hạ brightness rồi đo lại | chưa làm |
| AC-4 | Nút "Phân loại ngay" và "Lấy tin ngay" hiển thị đúng gradient mới, chữ trắng rõ. Viền focus vẫn hiện khi nhấn Tab | Ảnh chụp 1440×900 trang "Phân loại bài báo" và trang tin RSS (trạng thái thường và trạng thái focus bằng Tab) | chưa làm |
| AC-5 | `#64748B` chỉ còn ở 2 chỗ đồ họa: dòng icon thanh bên (`stIconMaterial`) và `.dot.off`. Không còn ở `.t2v-sec`, `.t2v-cfoot`, `.t2v-table .fl`, `.t2v-sc3 small` | Grep `-i "#64748B"` trong `streamlit_app.py` ra đúng 2 dòng, cả hai thuộc 2 selector trên | chưa làm |
| AC-6 | Bốn selector `.t2v-sec`, `.t2v-cfoot`, `.t2v-table .fl`, `.t2v-sc3 small` dùng `color: #94A3B8` và cỡ chữ **≥ 11px** | Grep từng selector, đọc giá trị `color` và cỡ trong `font:` (không còn `10px` ở 4 selector này) | chưa làm |
| AC-7 | Chữ phụ `#94A3B8` đạt **≥ 4,5:1** trên mọi nền nó nằm lên | Chạy `CONTRAST "#94A3B8" "#07090E"`, `CONTRAST "#94A3B8" "#0C0F17"`, `CONTRAST "#94A3B8" "#1E1B4B"` (nền hàng chọn hoặc nổi bật, trường hợp xấu nhất). Cả 3 kết quả ≥ 4,5 | chưa làm |
| AC-8 | Nhãn "CHỨC NĂNG CHÍNH", chân thẻ, đường dẫn tệp trong bảng kết quả tìm kiếm và ô `.t2v-sc3` đọc rõ. Không có chữ nào bị xuống dòng mới so với trước khi sửa | Ảnh chụp trước và sau ở 1440×900: thanh bên, trang "Phân loại bài báo" (chân thẻ), trang "Tìm kiếm nâng cao" sau một truy vấn (bảng `.fl`, `.t2v-sc3`), trang "Dữ liệu và đánh giá" (chân thẻ) | chưa làm |
| AC-9 | Không còn `r.summary or` ở đâu trong file. Cả dòng hiển thị (≈821) và dòng phân loại (≈829) đều chỉ nhận `summary` khi là `str` | Grep `summary or` ra 0 dòng. Grep `isinstance(.*summary` (hoặc lời gọi hàm trợ giúp với `r.summary`) ra 2 chỗ | chưa làm |
| AC-10 | Hàm hoặc biểu thức xử lý `summary` trả về `""` cho `None`, `float('nan')`, `pd.NA`, và trả nguyên chuỗi cho `"abc"` | Kiểm bằng một đoạn Python ngắn trong `.venv-exp` gọi đúng biểu thức hoặc hàm đã viết với 4 đầu vào trên. Dán output vào 04 | chưa làm |
| AC-11 | Trang tin RSS không hiện chữ "nan" ở tin có `summary` NULL | (a) SQL `SELECT COUNT(*) FROM v_latest_news WHERE summary IS NULL` để biết có tin như vậy không. (b) Nếu có trong 30 tin đầu: chụp ảnh thẻ tin đó, không có chữ "nan". Nếu không có: ghi rõ "không có dữ liệu NULL trong 30 tin", dựa vào AC-10 và ghi kết quả SQL thật vào 04. (c) Tìm chữ `nan` trên trang (Ctrl+F hoặc DOM) ra 0 kết quả trong `.t2v-nsum` | chưa làm |
| AC-12 | Không hỏng chức năng: file biên dịch được, ứng dụng chạy đủ 4 trang, bố cục giữ theo template | `.venv-exp/bin/python -m py_compile src/system/app/streamlit_app.py` không lỗi. Khởi động lại Streamlit (`scripts/run-app.sh`), mở 4 trang không có traceback. `git diff --stat` chỉ có `src/system/app/streamlit_app.py` (ngoài `contexte/handoff/`) | chưa làm |
| AC-13 | Dọn dữ liệu kiểm thử: xóa các dòng `classify_log`, `search_log` sinh ra khi kiểm thử | Đếm số dòng 2 bảng trước và sau khi kiểm thử. Sau khi dọn, số dòng bằng số trước kiểm thử (ghi số thật vào 04) | chưa làm |

**Tổng: 13 AC.**

## Đầu ra
- File đã tạo hoặc sửa: `contexte/handoff/ui-contrast-fix/02_dac_ta.md` (file này). Không sửa `src/`.

## Việc mở cho bước sau
- Developer: sửa đúng các dòng 114 (có thể cả 116), 93, 249, 304, 315, 821, 829 (thêm hàm trợ giúp nếu dùng) trong `src/system/app/streamlit_app.py`. Số dòng có thể lệch vài dòng nếu có thêm hàm trợ giúp.
- AC-3: con số hover hiện chỉ là ước tính tay (khoảng 4,5:1), **chưa đo**. Cần đo thật, không chép số ước tính vào tài liệu.
- Tester: phải khởi động lại Streamlit trước khi chụp (AGENTS.md: `st.cache_resource`). Bấm "Phân loại bài này" khi kiểm AC-11 sẽ ghi `classify_log` và `feed_item.pred_category`, nhớ dọn theo AC-13. Nếu không cần thì không bấm.
- Ghi nhận ngoài phạm vi: dòng 815 `if r.published_at` không bắt được `NaT` (cũng truthy). Nên mở task riêng nếu gặp tin không có ngày đăng.

## Cách kiểm tra
- Spec-writer chỉ đọc mã (Read, Grep). Không chạy lệnh và không đo tương phản. Mọi tỉ lệ tương phản trong file này lấy nguyên từ `00_dau_vao.md`, trừ những chỗ ghi rõ "ước tính tay, chưa đo".
