# Workflow: hoàn thiện và giao nộp
0. Task còn sửa code: chạy `/pipeline <task>` cho xong (đủ phiếu duyệt, review và test đạt) rồi mới sang bước 1.
1. Chạy skill `build-docs` (build, kiểm tra trích dẫn, đếm trang).
2. Chạy agent `reviewer` trên `livrables/`.
3. Sửa các điểm chưa đạt trong `draft/`, rồi build lại.
4. Kiểm thử ứng dụng: AppTest 4 trang, chụp màn hình; xóa nhật ký do kiểm thử sinh ra.
5. Cập nhật `PLAN.md` và `SPEC.md`.
6. Gửi người dùng câu commit gợi ý. Không tự commit hay push.
