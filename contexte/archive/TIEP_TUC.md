# Ghi chú để tiếp tục dự án

*Cập nhật: 08/10/2026*

**Đề tài:** Hệ thống tìm kiếm & phân loại chuyên mục tin tức tiếng Việt với biểu diễn Trans2Vec
**Trạng thái:** ✅ Hoàn thành GĐ1–GĐ7: kế hoạch → phiếu đọc → tài liệu bổ sung → tổng hợp → viết survey → thực nghiệm → rà soát → xuất Word.

## Sản phẩm chính

| File | Nội dung |
|---|---|
| `survey/Survey_Trans2Vec_VN_News.docx` | **Bản nộp** (Word). Khi mở, bấm **Yes** để Word cập nhật mục lục |
| `survey/Survey_Trans2Vec_VN_News.md` | Cùng nội dung, dạng Markdown (~15.200 từ, 43 tài liệu tham khảo) |
| `experiments/RESULTS.md` | Báo cáo thực nghiệm trên VNTC-10 |
| `KE_HOACH_SURVEY.md` | Kế hoạch và danh mục tài liệu |
| `survey/review_log.md` | Nhật ký rà soát và tình trạng danh mục tham khảo |
| `survey/notes/`, `survey/synthesis.md` | Phiếu đọc 11 bài, 27 tài liệu bổ sung, ma trận tổng hợp |

## Sửa nội dung survey
1. Sửa file chương trong `survey/draft/` (`00_front.md` … `10_ket_luan.md`). Trích dẫn viết dạng `[@key]`; danh mục ở `survey/draft/refs.tsv`.
2. Chạy lại:
   ```
   python3 survey/draft/build.py && python3 survey/draft/docx/build_docx.py
   ```
   Không sửa trực tiếp `Survey_Trans2Vec_VN_News.md/.docx`, vì lần build sau sẽ ghi đè.
3. (Tùy chọn) Xuất PDF: đóng Word rồi chạy `zsh survey/draft/docx/export_pdf.sh`.

## Chạy lại thực nghiệm
Dùng môi trường `.venv-exp` (Python 3.11). Xem mục "Tái lập" trong `experiments/RESULTS.md`. Toàn bộ mất khoảng 1 giờ trên CPU.

## Cập nhật 08/10
- Đã clone 4 repo vào `sourceGitSurvey/`: Trans2Vec, Sqn2Vec, GE-FSG, UIT-ViON-Dataset.
- E7 (tái hiện trên Snippets bằng mã nguồn gốc): TRANS-IT khớp bài báo, nhưng phần đóng góp của FI không tái hiện được (+0,7 so với +3,8). Đã đưa vào survey Mục 9.5.
- Ứng viên tài liệu mới: `survey/notes/candidates.md`.

## Việc còn mở (tùy chọn)
- [ ] Trang cuối bài Đỗ Phúc 2006. Xem PDF tại https://vjol.info.vn/JSTD/article/view/28928, rồi sửa dòng `dophuc2006` trong `refs.tsv` (hiện chỉ có "p. 23").
- [ ] Chốt chuẩn trình bày của khoa: IEEE hay APA, giới hạn số trang. Hiện dùng IEEE, đánh số theo thứ tự xuất hiện.
- [ ] Mở rộng thực nghiệm: E6 nhiều seed; corpus khó (IEEE Access 2026) hoặc UIT-ViON (đã có trong `sourceGitSurvey/`); Sqn2Vec (đã có mã); PhoBERT (cần GPU).
- [ ] Đọc và đưa vào survey các tài liệu trong `survey/notes/candidates.md` (Chen 2004: FI + tần suất; Chau 2026; UIT-ViON).
