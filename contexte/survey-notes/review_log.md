# GĐ7 — Nhật ký rà soát bản survey

**Ngày:** 07/10/2026 · **Bản rà soát:** `Survey_Trans2Vec_VN_News.md`, bản nháp 1 → bản nháp 2
**Cách làm:**
1. Đọc toàn văn.
2. Đối chiếu từng con số với phiếu đọc (`notes/`) và bảng gốc trong PDF.
3. Kiểm tra từng trích dẫn có đúng công trình được nói tới không.
4. Kiểm tra tự động mọi tham chiếu "Mục / Bảng / Hình / Chương".

## 1. Các lỗi đã sửa (13)

| # | Vị trí | Loại | Trước | Sau |
|---|---|---|---|---|
| 1 | Tóm tắt (i) | Diễn đạt | "độ chính xác … từ F1 0,749 đến 99,75%" (trộn hai độ đo) | "kết quả … dao động từ F1 0,749 đến accuracy 99,75%" |
| 2 | 1.2, ý 1 | **Trích dẫn sai đối tượng** | Duong & Hoang 2019 được trích cho "chọn đặc trưng IG, χ², OCFS", trong khi bài này chỉ dùng TF-IDF | Tách ra: TF-IDF → Duong 2019; chọn đặc trưng → Hoang 2007, Nguyen 2009 |
| 3 | 2.2 | Khẳng định quá mức | "chuẩn hóa Unicode là bước bắt buộc trước mọi biểu diễn" (dựa trên 1 nguồn) | "vẫn được dùng như bước đầu tiên, kể cả với Transformer" |
| 4 | 3.1 | Diễn đạt | "bài toán ngược với phân loại về dữ liệu đầu vào" (khó hiểu) | "một bài toán xếp hạng" |
| 5 | 3.3 | Thuật ngữ | "Biểu diễn không phải là một hàm đóng" | "không có công thức dạng đóng (closed-form) để tính vector cho tài liệu mới" |
| 6 | 4.3 (B2) | **Số liệu** | "giảm từ vựng 3–10 lần" | "6–10 lần (30.000 → 5.000; 300.000 → 30.000)", đúng theo Bảng 4 của Nguyen 2009 |
| 7 | Bảng 4.1 | Trình bày | Tiêu đề cột chỉ có số [n] (không biết cột nào là bài nào) | Thêm tên tác giả + năm |
| 8 | 5.2, công thức $O_1$ | **Công thức** | Dấu "+" trước tổng mẫu âm (chép theo bản PDF bị mất ngoặc) | Dấu "−", nhất quán với hàm mất mát negative sampling ở 3.3 (cũng sửa trong phiếu [13]) |
| 9 | 5.5, ý 4 | Khẳng định chưa kiểm chứng | "Toàn bộ quy trình chạy trên CPU" | "Về nguyên tắc chạy được trên CPU … chi phí thực tế cần được đo (H7)" |
| 10 | Bảng 8.1, Vinh 2021 | Thiếu độ đo | "≈ 0,905 (validation)" | "Accuracy ≈ 0,905 (tập validation)" |
| 11 | 8.2 | Lập luận | "khi chỉ đổi cách chọn đặc trưng" | "khi chỉ đổi cách chọn đặc trưng **và bộ phân loại**" (Pham Van 2017 cũng đổi sang MLP) |
| 12 | Bảng 8.3, M4 | Diễn đạt | "Accuracy ~99% hay ~75%?" (Duong 2019 báo F1, không phải accuracy) | "Kết quả ~99% hay ~0,75?" |
| 13 | 9.2, M6 | Lập luận kỹ thuật | "FI có vector gần tâm chuyên mục" (chưa nói vì sao so được) | "FI có tích vô hướng lớn nhất với tâm … vì PV-DBOW học hai loại vector qua chính tích vô hướng đó" |

Sửa trong GĐ5, trước khi rà soát:
- Số liệu Word2Vec / BoW / PhoBERT của Nguyen 2025 (thống nhất lấy Macro-F1 tốt nhất mỗi biểu diễn).
- "Chung tác giả liên hệ" → "chung tác giả Ta Minh Thanh".

## 2. Đã kiểm tra, không có lỗi

- **Tham chiếu chéo:** 100% "Mục x.y / Bảng x.y / Hình x.y / Chương n" trỏ tới mục có thật (kiểm tra tự động).
- **Trích dẫn:** 43/43 khóa có trong `refs.tsv`; không còn khóa `[@…]` sót; mọi tài liệu trong danh mục đều được trích dẫn ít nhất một lần.
- **Số liệu Bảng 5.1** (Trans2Vec): khớp 32/32 ô với Table 2 của bài gốc.
- **Các hiệu số trong Bảng 8.2:** +5,0; +2,7; +8,8; +16,4; +1,2 (JOI so với TRANS-FI) được tính lại và khớp.
- **"Sai số giảm khoảng 15 lần"** (8.2): 3,79% → 0,25%, khớp.
- **Số liệu dataset (Bảng 7.1):** VNTC 84.132 = 33.759 + 50.373; Level 2 26.451 = 14.375 + 12.076; khớp.

## 3. Điểm còn mở (cần anh/chị lưu ý hoặc bổ sung)

| Mức | Nội dung | Đề xuất |
|---|---|---|
| ✅ | Huynh 2020: **IEEE RIVF 2020**, tr. 1–3, doi 10.1109/RIVF48685.2020.9140761 (Crossref; bản mở rộng: ASTESJ 5(6):363–369, 2020) | Đã bổ sung (08/10) |
| ✅ | Nguyen 2009 (WI-IAT): tr. **466–469** (Crossref) | Đã bổ sung (08/10) |
| ✅ | Beil 2002: tr. 436–442, doi 10.1145/775047.775110 · Fung 2003: tr. 59–70, doi 10.1137/1.9781611972733.6 (Crossref) | Đã bổ sung (08/10) |
| ✅ | Con2Vec: Knowledge-Based Systems 229, 107382, **tháng 10/2021**, doi 10.1016/j.knosys.2021.107382; tác giả D. Nguyen, W. Luo, B. Vo, L. T. T. Nguyen, W. Pedrycz (Crossref). Đã sửa câu "cùng nhóm tác giả (Deakin)" ở 5.4 và 8.4 | Đã bổ sung (08/10) |
| ◐ | Đỗ Phúc 2006: bổ sung tiêu đề gốc tiếng Việt + tên tạp chí đầy đủ + **trang bắt đầu 23** (theo bản PDF trên VJOL, qua công cụ tìm kiếm). **Trang kết thúc chưa xác minh**: máy chủ VJOL từ chối kết nối ngày 08/10 | Mở https://vjol.info.vn/JSTD/article/view/28928, xem PDF, thêm trang cuối vào `refs.tsv` (khóa `dophuc2006`) |
| ℹ️ | Vài số liệu của Hoang 2007 (bản scan) và Vinh 2021 chỉ có trong hình | Bài đã chỉ trích các con số có trong phần văn bản; nêu ở 8.4 |
| ℹ️ | Họ tên tác giả Việt trong danh mục (Vinh/To, Huong/Ho) | Thống nhất theo quy định trình bày của khoa |
| ℹ️ | Độ dài ~13.800 từ (~25–30 trang A4) | Nếu bị giới hạn trang: rút gọn Phụ lục A và Bảng 6.1 trước |
