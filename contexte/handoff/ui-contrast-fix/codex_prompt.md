# Nhiệm vụ: sửa 3 lỗi tương phản/hiển thị trong Streamlit UI

Chỉ được sửa DUY NHẤT file: `src/system/app/streamlit_app.py`. Không sửa file khác, không tạo file mới.
File này đã có nhiều thay đổi chưa commit từ trước: KHÔNG đụng các dòng không liên quan, không format lại, không đổi bố cục. Chỉ sửa đúng các dòng dưới đây.

## Lỗi 1: nút chính (`[data-testid="stBaseButton-primary"]`, dòng ~114)
- Trong `linear-gradient(90deg, #06B6D4, #4F46E5 60%, #4338CA)` chỉ thay `#06B6D4` -> `#0E7490`. Giữ nguyên điểm dừng, `color:#fff`, viền, bo góc, box-shadow.
- Dòng hover (~116) dùng `filter: brightness(1.1)`: đo `#0E7490` x1,1 ≈ `#0F809E` với chữ trắng bằng
  `python3 ~/.claude/plugins/cache/ux-ui-agent-skills/ux-ui-agent-skills/2.10.0/scripts/contrast.py "#FFFFFF" "#0F809E"`.
  Nếu < 4,5 thì đổi thành `brightness(1.05)`; nếu >= 4,5 giữ nguyên. Nói rõ kết quả đo trong câu trả lời cuối.
- Giữ nguyên `:disabled`.

## Lỗi 2: chữ phụ `#64748B` (đổi 4 chỗ, giữ nguyên 2 chỗ đồ họa là icon thanh bên dòng ~75 và `.dot.off` dòng ~148)
| Selector (dòng ~) | Sau khi sửa |
|---|---|
| `.t2v-sec` (93) | `font: 600 11px 'JetBrains Mono', monospace; color: #94A3B8;` |
| `.t2v-cfoot` (249) | `font: 11px 'JetBrains Mono', monospace; color: #94A3B8;` |
| `.t2v-table .fl` (304) | `font: 11px 'JetBrains Mono', monospace; color: #94A3B8;` |
| `.t2v-sc3 small` (315) | `font: 11px 'JetBrains Mono', monospace; color: #94A3B8;` |
Chỉ đổi cỡ chữ và màu; giữ nguyên các thuộc tính khác của từng rule. Không đổi `#475569`, `.t2v-sc3 .on small`.

## Lỗi 3: chữ "nan" khi `feed_item.summary` NULL (pandas cho NaN, truthy)
- Dòng ~821: `{e(r.summary or "")}` -> chỉ nhận summary khi là `str`, ngược lại `""`.
- Dòng ~829: `{r.summary or ''}` trong `clf.predict(...)` -> tương tự.
- Có thể thêm hàm nhỏ cạnh các tiện ích HTML (~dòng 349-352), ví dụ `txt = lambda x: x if isinstance(x, str) else ""`, rồi dùng ở hai chỗ; hoặc viết isinstance trực tiếp. Sau sửa không còn chuỗi `summary or` nào trong file. Không thêm câu "Không có mô tả". KHÔNG sửa dòng ~815 (`if r.published_at`, NaT).

## Luật
- Comment tiếng Việt, giải thích vì sao (ngắn).
- Không chạy schema.sql, sync_manticore.py, benchmark; không cài thư viện; không git commit; không sửa `sources/`; không khởi động lại app.
- Tự kiểm: `.venv-exp/bin/python -m py_compile src/system/app/streamlit_app.py`
- Cuối cùng tóm tắt các dòng đã đổi.
