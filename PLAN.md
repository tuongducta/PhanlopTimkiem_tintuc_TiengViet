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
- [x] Bước 09, phân tích lỗi (23/10): Accuracy/P/R/F1 cho 7 mô hình, F1 từng chuyên mục, cặp nhầm, nhiễu nhãn, độ tin cậy. Xem `RESULTS.md` Mục 8. Đã đưa lên giao diện (trang Dữ liệu và đánh giá: P/R/F1, ma trận nhầm lẫn có số, P/R/F1 theo chuyên mục) và slide 9 của `Trans2Vec_TrinhBay.pptx`; chưa đưa vào survey hay báo cáo.
- [x] Slide kết quả thực nghiệm (7 mô hình, Macro-F1 và nDCG@10, chi phí chạy) thêm thành slide 8 của `livrables/survey/Trans2Vec_TrinhBay_final_v2.pptx`, có ghi chú và câu hỏi dự kiến; `Trans2Vec_TrinhBay_final.pptx` giữ nguyên (01/11).

## Hệ thống và báo cáo CSDL (môn Hệ CSDL nâng cao)
- [x] GĐ-H1–GĐ-H6: Docker, lược đồ, nạp dữ liệu, mô hình, Manticore, Streamlit, benchmark (20/10). Xem `KE_HOACH_HE_THONG_DB.md`.
- [x] Mục 17: 6 mô hình phân loại, mốc Trans2Vec gốc, mô hình cải tiến CAT (21/10).
- [x] Mục 18: giao diện theo bản phác (21/10).
- [x] GĐ-H7: báo cáo `livrables/report_db/` (30 trang) và đoạn chèn survey (21/10).
- [x] Mục 20: P1 (nhánh gộp dấu cho truy vấn không dấu), P2 (dùng recall@10 khi so sánh chỉ mục) (21/10).
- [x] Slide `CSDL_TrinhBay.pptx` viết lại theo dàn ý mới, 15 slide, dựng bằng `livrables/report_db/make_slides.py`; thêm E-DB7 (PostgreSQL), E-DB8 (Elasticsearch), xem `RESULTS_DB.md`, `KE_HOACH_SLIDE_CSDL_V2.md`. Bản cũ ở `contexte/archive/` (01/11). Chưa đưa vào báo cáo.
- [x] Mục 21: giao diện tối theo template `sources/template_demo/` (22/10). Ảnh trong báo cáo cập nhật 25/10: Hình 8.1–8.3 (thêm trang Dữ liệu và đánh giá), bảng Acc/P/R/F1, bộ lọc tin RSS; báo cáo 30 trang.
- [x] Trang Phân loại: bấm một dòng trong "So sánh 6 mô hình" để đổi mục "Vì sao … chọn …" theo mô hình đó (01/11). Hình `fig_ui_classify.png` trong báo cáo chưa chụp lại theo giao diện này.

## Tổ chức dự án
- [x] Dọn file thừa và tái cấu trúc theo mẫu Harness tầng 2 (21/10). Xem `KE_HOACH_TAI_CAU_TRUC.md`.
- [x] Tầng 3, git cục bộ: `WORKTREE.md`, `scripts/init-git.sh`, `docs/sync-guide.md`, commit đầu tiên (21/10).
- [x] Đổi tên PDF trong `sources/papers/` theo `STT_Năm_[SURVEY_]TênNgắn.pdf`, đánh dấu 4 bài survey (25/10). Thêm 32 bài tải truy cập mở (35–66, mã D-xx). Xem `KE_HOACH_DOI_TEN_PAPERS.md`, `contexte/survey-notes/papers_index.md`.
- [ ] Bảng màu giao diện (`ui-theme-tokens`): B1 xong (gom biến, 26/10); B2 đã áp nhưng dừng khi chưa đạt (bảng Sáng lỗi, progress S1). Xem `KE_HOACH_THEME.md` Mục 5.
- [ ] Pipeline nhiều agent có cổng duyệt (kiến trúc → đặc tả → lập trình bằng Codex → review + kiểm thử). Đợt 1 xong (22/10): khung đã dựng, chạy thử `/pipeline ui-contrast-fix` đạt 13/13 AC sau 2 vòng sửa (Mục 10). Đợt 2 (hook log, thông báo, worktree, agent-memory) chưa làm. Xem `KE_HOACH_AGENT_PIPELINE.md` Mục 9.
- [ ] (Tùy chọn) Đưa lên GitHub private: chỉ làm khi anh/chị yêu cầu.
