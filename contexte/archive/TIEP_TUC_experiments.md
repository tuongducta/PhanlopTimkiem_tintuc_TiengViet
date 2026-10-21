# GĐ6 — Trạng thái: ✅ HOÀN THÀNH (07/10/2026, ~23:45)

- **Kết quả đầy đủ:** `experiments/RESULTS.md`; bảng tự sinh ở `experiments/results/tables.md`.
- **Đã đưa vào survey:**
  - Mục 9.5 (Bảng 9.3–9.5, hình Macro-F1);
  - mục 6 của giao thức ở 7.3;
  - RQ3 ở 10.1 và hướng phát triển ở 10.3;
  - phần tóm tắt.
- **Đã tạo lại** `survey/Survey_Trans2Vec_VN_News.md` và `.docx`.
- **Đã chạy:**
  - E1–E4 (`run_experiments.py`);
  - E5z / E5 (`run_tuned.py`);
  - E6 (`run_consistent.py`, đánh giá nhất quán: kết quả chính cho Trans2Vec).

## Kết luận chính
1. Phân loại (Macro-F1): TF-IDF 0,907 (LR) > Trans2Vec-JOI 0,849 ≈ TRANS-IT 0,847. FI đóng góp −0,3 đến +0,9 điểm.
2. Tìm kiếm (nDCG@10): JOI 0,809 > IT 0,800 > LDA 0,765 > TF-IDF 0,740. Với truy vấn 3 từ khóa: 0,692 so với 0,634.
3. Bẫy đánh giá: vector train lấy từ `model.dv` + vector test sinh bằng `infer_vector` → lệch 7–8 điểm và "cải thiện nhờ FI" giả (+3,7 / +4,2).
4. Giả thuyết A1 (FI bù việc thiếu tách từ) không được xác nhận.

## Nếu muốn làm tiếp (tùy chọn)
- Chạy E6 với 3 seed: sửa `run_consistent.py` lặp seed 1..3.
- Thêm corpus khó, PhoBERT (cần GPU / PyTorch), Top2Vec, Sqn2Vec.
- Quét δ có hệ thống. Tìm cách đưa lại thông tin tần suất (H1).
