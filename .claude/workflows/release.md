# Workflow: hoàn thiện và giao nộp
1. Chạy skill `build-docs` (build, kiểm tra trích dẫn, đếm trang).
2. Chạy agent `reviewer` trên `livrables/`.
3. Sửa các điểm chưa đạt trong `draft/`, rồi build lại.
4. Kiểm thử ứng dụng: AppTest 4 trang, chụp màn hình; xóa nhật ký do kiểm thử sinh ra.
5. Cập nhật `PLAN.md` và `SPEC.md`.
