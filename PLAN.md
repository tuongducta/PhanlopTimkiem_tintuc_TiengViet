# PLAN.md — Các bước làm

Chi tiết từng giai đoạn ở `contexte/plans/`.

## Survey (môn Tri thức dữ liệu)
- [x] GĐ1–GĐ7: kế hoạch, phiếu đọc, tổng hợp, viết survey, thực nghiệm E1–E7, rà soát, xuất Word (08/10). Xem `KE_HOACH_SURVEY.md`.
- [x] GĐ8 (v3): phiếu đọc K* (18/10). Xem `KE_HOACH_SURVEY_v3.md`.
- [x] GĐ9: ma trận tổng hợp v3 (22/10). Xem `contexte/survey-notes/synthesis_v3.md`; §15 liệt kê việc cần xử lý ở GĐ11.
- [x] Q2–Q5 chốt (22/10): xem Mục 10 của `KE_HOACH_SURVEY_v3.md`.
- [x] GĐ10: E8, E9 xong (22/10). Xem `RESULTS.md` Mục 7.
- [x] GĐ11: viết lại theo đường ống, ráp `he_thong_db.md`, E8/E9, 11 tài liệu mới (22/10). Bản build: 54 tài liệu, khoảng 24.000 từ.
- [x] GĐ12: rà soát (22/10), sửa 24 lỗi. Xem `contexte/survey-notes/review_log.md`.

## Hệ thống và báo cáo CSDL (môn Hệ CSDL nâng cao)
- [x] GĐ-H1–GĐ-H6: Docker, lược đồ, nạp dữ liệu, mô hình, Manticore, Streamlit, benchmark (20/10). Xem `KE_HOACH_HE_THONG_DB.md`.
- [x] Mục 17: 6 mô hình phân loại, mốc Trans2Vec gốc, mô hình cải tiến CAT (21/10).
- [x] Mục 18: giao diện theo bản phác (21/10).
- [x] GĐ-H7: báo cáo `livrables/report_db/` (30 trang) và đoạn chèn survey (21/10).
- [x] Mục 20: P1 (nhánh gộp dấu cho truy vấn không dấu), P2 (dùng recall@10 khi so sánh chỉ mục) (21/10).
- [x] Mục 21: giao diện tối theo template `sources/template_demo/` (22/10). Ảnh trong báo cáo giữ bản cũ.

## Tổ chức dự án
- [x] Dọn file thừa và tái cấu trúc theo mẫu Harness tầng 2 (21/10). Xem `KE_HOACH_TAI_CAU_TRUC.md`.
- [x] Tầng 3, git cục bộ: `WORKTREE.md`, `scripts/init-git.sh`, `docs/sync-guide.md`, commit đầu tiên (21/10).
- [ ] Pipeline nhiều agent có cổng duyệt (kiến trúc → đặc tả → lập trình bằng Codex → review + kiểm thử). Đợt 1 xong (22/10): khung đã dựng, chạy thử `/pipeline ui-contrast-fix` đạt 13/13 AC sau 2 vòng sửa (Mục 10). Đợt 2 (hook log, thông báo, worktree, agent-memory) chưa làm. Xem `KE_HOACH_AGENT_PIPELINE.md` Mục 9.
- [ ] (Tùy chọn) Đưa lên GitHub private: chỉ làm khi anh/chị yêu cầu.
