# 00_dau_vao · ui-contrast-fix

**Nguồn:** design-review giao diện Streamlit ngày 22/10/2026 (skill `ux-ui-agent-skills:design-review`, desktop 1440×900). Tương phản đo bằng `contrast.py` của kit (`~/.claude/plugins/cache/ux-ui-agent-skills/ux-ui-agent-skills/2.10.0/scripts/contrast.py`).

File liên quan: `src/system/app/streamlit_app.py`.

| # | Mức | Vị trí | Phát hiện | Đề xuất của bản review |
|---|---|---|---|---|
| 1 | Nghiêm trọng | Nút chính "Phân loại ngay", "Lấy tin ngay": CSS `[data-testid="stBaseButton-primary"]` (dòng ~114) | Chữ trắng trên nền `#06B6D4` đạt **2,43:1**, dưới cả ngưỡng 3:1 | Gradient bắt đầu từ `#0E7490` (trắng/`#0E7490` = 5,36:1), hoặc giữ cyan và đổi chữ sang `#07090E` (11,02:1) |
| 2 | Lớn | Chữ phụ màu `#64748B`: `.t2v-sec` (nhãn "CHỨC NĂNG CHÍNH"), `.t2v-cfoot`, `.t2v-table .fl` (đường dẫn tệp), `.t2v-sc3 small` | `#64748B` trên `#07090E` = **4,18:1**, trên `#0C0F17` = **4,03:1**, dưới 4,5:1; chữ lại chỉ 10–11px | Đổi sang `#94A3B8` (trên `#07090E` = 7,77:1); nâng cỡ chữ tối thiểu lên 11–12px |
| 3 | Lớn | Trang "Tin mới nhất", `page_news()` (dòng ~821) | Tin không có mô tả hiện chữ **"nan"**. `r.summary or ""` không bắt được NaN của pandas (NaN là truthy) | `r.summary if isinstance(r.summary, str) else ""` |

**Ràng buộc:**
- Giữ bố cục theo `sources/template_demo/`.
- Không đổi các màu `#475569` dùng làm dấu phân cách (chỉ trang trí).
- `#64748B` còn dùng cho icon và chấm trạng thái (`.dot.off`): đó là thành phần đồ họa, ngưỡng 3:1, đang đạt, không bắt buộc đổi.
