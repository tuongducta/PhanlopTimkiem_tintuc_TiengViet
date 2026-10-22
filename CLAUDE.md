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
10. **Pipeline nhiều agent** (`/pipeline <task> "<mô tả>"`): architect → spec-writer → developer (Codex CLI viết code) → code-reviewer ∥ tester. Trước **mỗi** agent phải trình phiếu duyệt và chờ người dùng chọn; "tiếp tục" chỉ duyệt bước đang trình. Bàn giao qua `contexte/handoff/<task>/`. Xem `contexte/plans/KE_HOACH_AGENT_PIPELINE.md`.

## Điều cấm và lưu ý đã thống nhất
- Không sửa nội dung `contexte/plans/KE_HOACH_SURVEY.md` (bản v2).
- `livrables/survey/draft/` là nguồn của survey v3 (Q5 chốt 22/10: sửa thẳng draft, bản v2 nằm trong git). Sửa xong phải build lại và kiểm tra tham chiếu chéo.
- Hỏi trước khi cài thư viện. Không đề xuất cài `pypdf`; đọc PDF bằng PDFKit qua `osascript`.
- Không xóa phần RSS (`src/system/db/feed.sql`, `pipeline/fetch_news.py`, các bảng `news_source`, `feed_item`, `fetch_log`).
- Giao diện Streamlit (nền tối) bám template tham khảo `sources/template_demo/` (chỉ đọc, không sửa). Chỉ lấy bố cục, không lấy số liệu mẫu. Chụp màn hình kiểm tra trước khi báo xong.
- Báo cáo môn CSDL giới hạn **25–30 trang** A4. Đếm trang bằng `scripts/count-pages.sh`.
- Kiểm thử xong phải xóa các dòng `search_log`, `classify_log` do kiểm thử sinh ra.
