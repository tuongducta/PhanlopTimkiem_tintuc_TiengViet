# Log · Bước 1/3 · spec-writer · ui-contrast-fix

| Trường | Giá trị |
|---|---|
| Bắt đầu | 22/10/2026 16:26 (khoảng; log chi tiết bổ sung sau khi agent đã chạy) |
| Kết thúc | 22/10/2026 16:37 (thông báo hoàn tất) |
| Thời lượng agent | 134 giây, 12 lần gọi tool, khoảng 70.000 token |
| Trạng thái | xong |
| Người duyệt | anh/chị, chọn "Duyệt" tại cổng 1 |
| Transcript gốc | `02_spec-writer.transcript.jsonl` (chép khi agent xong) |

## Phiếu duyệt
```
Task:        ui-contrast-fix
Đầu vào:     contexte/handoff/ui-contrast-fix/00_dau_vao.md, src/system/app/streamlit_app.py (chỉ đọc)
Sẽ làm:      viết đặc tả + AC đánh số cho 3 lỗi; chốt phương án màu và danh sách file được sửa
Sẽ sửa file: chỉ tạo contexte/handoff/ui-contrast-fix/02_dac_ta.md
Sẽ chạy:     không chạy lệnh
Không làm:   sửa src/, đổi bố cục template, các lỗi #4–#12
Rủi ro:      thấp (chỉ ghi tài liệu)
```

## Lời gọi gửi agent
Viết đặc tả và AC-1… cho đúng 3 lỗi trong `00_dau_vao.md` (tương phản chữ nút chính; màu và cỡ chữ phụ `#64748B`; chữ "nan" ở tin RSS). Chốt phương án màu kèm lý do, giữ gradient cyan→indigo của template. Liệt kê chính xác selector và dòng cần đổi, phân biệt chữ với icon/chấm/viền. Mỗi AC phải kiểm được bằng `contrast.py`, cỡ chữ, ảnh chụp hoặc dữ liệu. Nêu danh sách file được phép sửa. Chỉ ghi `02_dac_ta.md`, không chạy lệnh, không sửa `src/`.

## Kết quả agent trả về (tóm tắt nguyên ý)
- 13 AC. Agent không chạy lệnh. Số tương phản lấy từ `00_dau_vao.md`; tương phản ở trạng thái hover chỉ là ước tính tay (khoảng 4,5:1, chưa đo).
- Lỗi 1: phương án A, điểm đầu gradient dòng 114 đổi `#06B6D4` thành `#0E7490`, chữ giữ trắng. Không chọn B vì chữ tối trên vùng indigo ước tính chỉ khoảng 3:1. Hover `brightness(1.1)` dòng 116: nếu đo dưới 4,5:1 thì hạ xuống 1.05 (AC-3).
- Lỗi 2: 6 chỗ dùng `#64748B`. 4 chỗ là chữ (`.t2v-sec` dòng 93, `.t2v-cfoot` 249, `.t2v-table .fl` 304, `.t2v-sc3 small` 315) đổi sang `#94A3B8`, cỡ tối thiểu 11px. 2 chỗ đồ họa (icon thanh bên dòng 75, `.dot.off` 148) giữ nguyên.
- Lỗi 3: `isinstance(x, str)` ở dòng 821 và dòng 829 (`classify_news`; chữ "nan" lọt vào văn bản đưa đi phân loại và vào `classify_log`). Dòng 829 do agent tự thêm vào phạm vi.
- Ngoài phạm vi, ghi vào việc mở: dòng 815 `if r.published_at` không bắt được `NaT`.
- File được phép sửa: chỉ `src/system/app/streamlit_app.py`.

## File thay đổi (git status so với trước khi chạy)
- Mới: `contexte/handoff/ui-contrast-fix/02_dac_ta.md`.
- Không có thay đổi nào khác do agent. `.gitignore` và các file log do phiên điều phối sửa.
- Ghi chú: mốc trước khi chạy chỉ chụp 40 dòng đầu của `git status`, nên phải so tay. Từ bước sau chụp đầy đủ.
