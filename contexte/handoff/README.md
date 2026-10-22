# contexte/handoff/ — Bàn giao giữa các agent

Mỗi task chạy bằng `/pipeline` có một thư mục `<task>/` (chữ thường, gạch nối, ví dụ `ui-contrast-fix`).

| File | Agent ghi | Agent sau đọc |
|---|---|---|
| `01_kien_truc.md` | architect | spec-writer, developer |
| `02_dac_ta.md` | spec-writer | developer, code-reviewer, tester |
| `codex_prompt.md`, `codex_last.md` | developer (prompt gửi Codex, câu trả lời cuối của Codex) | code-reviewer |
| `03_trien_khai.md` | developer | code-reviewer, tester |
| `04_review.md` | phiên điều phối (chép kết quả code-reviewer) | developer (vòng sửa) |
| `05_kiem_thu.md`, `shots/` | tester | developer (vòng sửa) |
| `00_dau_vao.md` | phiên điều phối (đầu vào có sẵn, ví dụ bản review) | mọi agent |
| `log.md` | phiên điều phối: một dòng mỗi sự kiện | anh/chị |
| `logs/<NN>_<agent>.md` | phiên điều phối: phiếu duyệt, lời gọi, kết quả trả về, file thay đổi, thời gian | anh/chị |
| `logs/<NN>_<agent>.transcript.jsonl` | bản chép transcript gốc của agent (không commit) | anh/chị |
| `logs/03_codex_events.jsonl`, `03_codex_stderr.log` | developer: sự kiện của Codex CLI (không commit) | anh/chị |

- Mẫu chung: `_template.md`.
- Vòng sửa thứ n ghi thêm hậu tố, ví dụ `03_trien_khai_v2.md`, không ghi đè bản trước.
- Kế hoạch tổng: `contexte/plans/KE_HOACH_AGENT_PIPELINE.md`.
