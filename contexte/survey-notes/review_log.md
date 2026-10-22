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

---

# GĐ12 — Nhật ký rà soát bản survey v3

**Ngày:** 22/10/2026 · **Bản rà soát:** `Survey_Trans2Vec_VN_News.md` v3 (build từ `livrables/survey/draft/`, 54 tài liệu, khoảng 24.300 từ)
**Cách làm:**
1. Agent `reviewer` đối chiếu từng con số ở các phần mới với `RESULTS.md`, `RESULTS_DB.md`, `he_thong_db.md`, `KE_HOACH_HE_THONG_DB.md` Mục 17, các file JSON kết quả và phiếu đọc K*.
2. Kiểm tra tự động: số thập phân, thuật ngữ cũ, mã K* sót, thứ tự bảng và hình, mọi tham chiếu "Mục / Bảng / Hình".
3. Xác minh lại ba nguồn mà agent dẫn: run TF-IDF dùng C = 10, độ trễ trong ứng dụng 50–170 ms, mức 1,5% của K29 là so với CARP.

**Khớp nguồn, không sửa:** E8 (Bảng 7.4), E9 (Bảng 9.9), Bảng 9.3–9.6 và 9.8, sáu mô hình (Bảng 9.4), BM25, dấu thanh, chỉ mục, bài trùng, số liệu 8 bài K*, các phép đếm (6 RQ, 7 nhánh, M1–M10, H1–H8, T1–T8, 19 công trình chính).

## Các lỗi đã sửa (24)

| # | Vị trí | Loại | Trước | Sau |
|---|---|---|---|---|
| 1 | Tóm tắt | Nói quá | "Chọn FI đóng hay FI ổn định không tốt hơn ngẫu nhiên" | FI đóng không có tác dụng vì gần như mọi FI đã đóng (E8); chỉ FI ổn định được so với ngẫu nhiên (E9) |
| 2 | 9.5 (i) | Sai số liệu | "+2,7 trên Snippets" (là FI − IT) | "+3,8" (JOI − IT, cùng đại lượng với Bảng 9.7) |
| 3 | 9.5 | Sai đường dẫn | `src/experiments/RESULTS.md` | `contexte/results/` |
| 4 | Bảng 8.1, 8.2 | Thiếu điều kiện | TF-IDF → LR 92,5% | ghi rõ C = 10 (run 7) |
| 5 | Tóm tắt, 1.5, 8.4, 8.6, 10.1 | Mâu thuẫn | "bốn mối đe dọa đo được" | "sáu" (T1, T2, T4, T5, T7, T8) |
| 6 | Bảng 8.4, T1 | Dẫn sai bằng chứng | 0,823 so với 0,766 (lệch do T2) | Snippets: transductive chênh inductive −0,5 đến +1,9 |
| 7 | 7.3 điểm 7 | Nói quá | "transductive có lợi" | "có thể có lợi"; mức chênh không nhất quán |
| 8 | Tóm tắt, 6.2, 9.5, 10.1 | Mâu thuẫn chi phí | "khoảng một phút" | "một đến hai phút"; thêm 98 s khi suy luận lại cả vector huấn luyện |
| 9 | 10.1 RQ4 | Thiếu điều kiện | "tìm kiếm dưới 20 ms" | p50 trong benchmark; 50–170 ms trong ứng dụng |
| 10 | 9.2 | Thiết kế lẫn hiện thực | M1 VnCoreNLP, M3 FP-Growth/LCM | thêm đoạn nêu 3 điểm khác của bản hiện thực |
| 11 | 8.1, 8.2, Phụ lục A | Nhãn không thống nhất | "BoW + OCFS" | "TF-IDF + OCFS" theo phiếu [1] |
| 12 | 9.5, A1 | So khác bộ phân loại | TF-IDF −1,2 so với JOI −2,5 | ghi rõ SVM và LR; thêm TRANS-IT −3,1 |
| 13 | 9.5, hạn chế | Sai mô tả | "Bảng 9.7 mới chạy một seed" | cột "suy luận lại" một seed; E9 3 seed cho +0,25 ± 0,11 |
| 14 | 7.1 | Đếm sai | "Ba nhận xét" | "Bốn nhận xét" |
| 15 | 1.4 | Thiếu | 3 tài liệu tìm kiếm không thuộc vòng nào | thêm câu nêu BM25, HNSW, RRF |
| 16 | Phụ lục A | Tên mục | "công trình nòng cốt" | "công trình chính (vòng 1 và vòng 3)" |
| 17 | Bảng 8.4 | Tham chiếu dễ nhầm | "Mục 7", "Mục 6"… | "Điểm 7", "Điểm 6"… (của Mục 7.3) |
| 18 | 7.3, T3 | Thiếu điểm giao thức | T3 trỏ tới điểm không có | thêm điểm 10 "chạy lại baseline trong cùng điều kiện" |
| 19 | 9.5 | Hình không số | `fig_macro_f1.png` | Hình 9.3 |
| 20 | 4.6, 6.1 | Gộp sai đối tượng so | "1,5% thời gian … so với GPT-3" | so với CARP; GPT-3 chỉ so accuracy |
| 21 | 6.3 | Thiếu thành phần | "+0,3 nhờ BERT, RoBERTa" | thêm gộp đồng xuất hiện |
| 22 | Bảng 7.3 | Thiếu nguồn | chỉ trích [li2022, minaee2021] | thêm [onan2023] cho số tài liệu R8, R52, 20NG |
| 23 | 8.2 | Khẳng định quá | "Chênh lệch 3,7 điểm này đến từ" | "có thể đến từ" |
| 24 | Phụ lục A, 4.7 | Thang đo | "74,63"; "98,75" | "0,7463"; "98,75%" |

## Ghi chú
- Ý kiến về thứ tự tác giả VNLP: `refs.tsv` đúng theo Crossref (Le, Do, Nguyen V.D., Nguyen T.D.). Phiếu K21 ghi sai và đã được sửa.
- `he_thong_db.md` đã đánh dấu "đã chèn" (cả 6 mục). Hai chi tiết nhỏ không ráp: Macro-F1 0,765 trên các bài trùng, cách kiểm FI đóng bằng SQL.
- Đoạn 2 của Tóm tắt đã tách câu dài.
- Chưa sửa (ngoài phạm vi ghi của Claude): `SPEC.md` (ô "Survey bản v3" còn chưa đánh dấu, còn ghi "chờ chốt Q2–Q5"); `CLAUDE.md` và `.claude/rules/livrables.md` (còn điều cấm sửa draft khi Q5 chưa chốt).
