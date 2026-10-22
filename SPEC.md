# SPEC.md — Muốn đạt gì

## Mục tiêu
- **Môn Tri thức dữ liệu:** bài khảo sát về biểu diễn văn bản dựa trên tập phổ biến (Trans2Vec) cho phân loại và tìm kiếm tin tức tiếng Việt. Bài khảo sát có thực nghiệm trên VNTC-10 và đề xuất hệ thống.
- **Môn Hệ cơ sở dữ liệu nâng cao:** hiện thực hệ thống trên MariaDB 11.8 (nguồn dữ liệu gốc) và Manticore Search 29.9 (chỉ mục phái sinh), đo đạc E-DB1, 2, 4, 5, và viết báo cáo riêng.

## Phạm vi
- **Trong phạm vi:**
  - Corpus VNTC-10 (84.132 bài).
  - Trans2Vec: mốc gốc, 4 biến thể, mô hình cải tiến CAT.
  - Tìm kiếm BM25, vector và hybrid; xử lý dấu tiếng Việt.
  - Ứng dụng Streamlit 4 trang.
  - Thu thập RSS 3 báo.
- **Ngoài phạm vi:**
  - Replication, phân tán, phân quyền nhiều người dùng.
  - E-DB3 (khai phá FI bằng SQL) và E-DB6 (ghi kép có lỗi).
  - PhoBERT, vì không có GPU.

## Sản phẩm nộp
| Sản phẩm | File |
|---|---|
| Bài khảo sát | `livrables/survey/Survey_Trans2Vec_VN_News.docx` |
| Báo cáo CSDL | `livrables/report_db/BaoCao_CSDL_Trans2Vec.docx` |
| Hệ thống demo | `src/system/` (chạy bằng `scripts/run-app.sh`) |

## Tiêu chí hoàn thành
- [x] Survey bản v2 build được (Times New Roman 13, A4, mục lục tự động).
- [x] Survey bản v3: ráp phiếu đọc K* và các đoạn chèn ở `contexte/survey-notes/he_thong_db.md`; đã rà soát (GĐ12, 22/10, xem `contexte/survey-notes/review_log.md`).
- [x] Báo cáo CSDL: 10 chương, trong giới hạn **25–30 trang** (hiện 30).
- [x] Mọi số liệu trong tài liệu lấy từ kết quả chạy thật và tái lập được bằng script trong `src/`.
- [x] Ứng dụng chạy được trên dữ liệu thật; kiểm thử AppTest đạt cả 4 trang.
