# CLAUDE.md — Bộ não dự án

@AGENTS.md
@MAP.md

## Bạn là ai
- Trợ lý nghiên cứu và kỹ thuật cho đề tài *Hệ thống tìm kiếm và phân loại chuyên mục tin tức tiếng Việt với biểu diễn Trans2Vec*. Đề tài dùng cho hai môn sau đại học ở HUTECH: **Tri thức dữ liệu** (bài khảo sát) và **Hệ cơ sở dữ liệu nâng cao** (hệ thống MariaDB + Manticore, báo cáo riêng).
- Trả lời bằng tiếng Việt. Thuật ngữ kỹ thuật giữ tiếng Anh khi cần.

## Quy tắc làm việc
1. Đọc `SPEC.md` (mục tiêu) và `PLAN.md` (trạng thái) trước khi bắt đầu một task.
2. **Lên kế hoạch trước khi làm:** với bước lớn hoặc thay đổi khó hoàn tác, ghi kế hoạch ra `contexte/plans/*.md` và chờ duyệt. Câu "tiếp tục …" nghĩa là đồng ý đi tiếp theo lộ trình.
3. `sources/` chỉ đọc: tài liệu thô, dữ liệu VNTC, repo tham khảo. Không sửa, không xóa.
4. Kiến thức, kế hoạch, kết quả thực nghiệm ghi vào `contexte/`. Sản phẩm nộp chỉ tạo trong `livrables/`. Mã nguồn ở `src/`. Không tạo file rác ở thư mục gốc; file tạm để trong scratchpad.
5. **Không sửa trực tiếp file đã build** (`livrables/**/*.md`, `.docx` cùng tên thư mục). Sửa `draft/` rồi build lại (xem `scripts/build-docs.sh`).
6. Không đọc hay ghi `.env`, không in mật khẩu ra màn hình.
7. Việc chạy lâu (huấn luyện, benchmark, dựng chỉ mục, xuất PDF) chạy nền.
8. Xong mỗi bước thì cập nhật `PLAN.md` và kế hoạch chi tiết tương ứng.
9. **Git: KHÔNG tự commit, push, amend, rebase, merge hay tag.** Người dùng tự làm mọi thao tác này. Claude chỉ hỏi trước và gửi sẵn câu commit kèm danh sách file nên `git add` (quy ước ở `docs/sync-guide.md`). `git status` và `git diff` thì được. Remote `origin` = GitHub riêng tư `tuongducta/PhanlopTimkiem_tintuc_TiengViet`. Email commit của repo: tuongduc.ta@gmail.com.

## Điều cấm và lưu ý đã thống nhất
- Không sửa nội dung `contexte/plans/KE_HOACH_SURVEY.md` (bản v2).
- Chưa sửa `livrables/survey/draft/` khi Q5 của `KE_HOACH_SURVEY_v3.md` chưa chốt. Đoạn cần chèn soạn sẵn ở `contexte/survey-notes/he_thong_db.md`.
- Hỏi trước khi cài thư viện. Không đề xuất cài `pypdf`; đọc PDF bằng PDFKit qua `osascript`.
- Không xóa phần RSS (`src/system/db/feed.sql`, `pipeline/fetch_news.py`, các bảng `news_source`, `feed_item`, `fetch_log`).
- Giao diện Streamlit bám bản phác https://claude.ai/artifact/MvVm7icEkfFGJfjm3Jj2eU. Chụp màn hình kiểm tra trước khi báo xong.
- Báo cáo môn CSDL giới hạn **25–30 trang** A4. Đếm trang bằng `scripts/count-pages.sh`.
- Kiểm thử xong phải xóa các dòng `search_log`, `classify_log` do kiểm thử sinh ra.
