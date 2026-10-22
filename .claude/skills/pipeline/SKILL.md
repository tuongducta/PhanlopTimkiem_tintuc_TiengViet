---
name: pipeline
description: Điều phối pipeline nhiều agent (architect → spec-writer → developer/Codex → code-reviewer ∥ tester) cho một task, có phiếu duyệt trước mỗi agent. Dùng khi người dùng gõ /pipeline <task> "<mô tả>" hoặc yêu cầu chạy task qua các agent.
---
Bạn là **phiên điều phối**. Bạn không tự làm việc của các agent; bạn trình phiếu duyệt, gọi agent, tóm tắt kết quả. Kế hoạch gốc: `contexte/plans/KE_HOACH_AGENT_PIPELINE.md`.

## 0. Khởi tạo
1. Tên task: chữ thường, gạch nối. Tạo `contexte/handoff/<task>/` và `log.md` (nếu đã có thì đọc để chạy tiếp từ bước dở).
2. Đọc `SPEC.md`, `PLAN.md` để biết bối cảnh.
3. Đầu vào chỉ có trong hội thoại (bản review, yêu cầu dài) thì ghi ra `contexte/handoff/<task>/00_dau_vao.md` để agent đọc được.
4. **Cổng 0:** hỏi bằng AskUserQuestion chọn các bước sẽ chạy (mặc định cả 5; sửa lỗi nhỏ thì đề xuất bỏ architect).

**Trước mỗi lượt developer:** file sẽ sửa đã có thay đổi chưa commit thì chép ra `logs/<tên>.before[_vN].<đuôi>`, và dặn developer, reviewer, tester so bằng `diff -u` với bản này, không dùng `git diff`. Sau lượt developer, lưu `logs/03_codex[_vN].diff`.

**Vòng sửa:** đưa phát hiện của reviewer vào phiếu developer; con số tự ước lượng (độ rộng, ngưỡng) phải nêu rõ trong phiếu là "chưa kiểm". Tester ghi số đo bố cục ngay từ vòng đầu để có mốc so.

## 1. Vòng lặp cho mỗi bước
Trước **mỗi** agent, trình phiếu duyệt rồi hỏi bằng AskUserQuestion (lựa chọn: Duyệt · Sửa phạm vi · Bỏ qua bước · Dừng):

```
── Phiếu duyệt · Bước <i>/<n> · <agent> ──
Task:        <task>
Đầu vào:     <file handoff sẽ đọc>
Sẽ làm:      <1–3 dòng>
Sẽ sửa file: <danh sách; "không" nếu chỉ đọc>
Sẽ chạy:     <lệnh; với developer: codex exec … -s workspace-write>
Không làm:   <ngoài phạm vi>
Rủi ro:      <thấp/trung bình/cao + lý do>
```

- "Sửa phạm vi": nhận chỉnh sửa của người dùng, trình lại phiếu.
- "Dừng": ghi `log.md`, cập nhật PLAN.md, kết thúc.
- Duyệt rồi mới gọi Agent tool với `subagent_type` tương ứng. Lời gọi phải nêu: tên task, đường dẫn thư mục handoff, danh sách file được phép sửa (đúng như phiếu).
- Agent xong: đọc file đầu ra, tóm tắt 3–5 dòng cho người dùng, ghi một dòng vào `log.md` (`giờ · bước · agent · kết quả`). **Không tự sang bước kế**; quay lại đầu vòng với phiếu của bước sau.

## 1b. Log từng lần chạy agent (bắt buộc)
Mỗi lần gọi agent có một file `contexte/handoff/<task>/logs/<NN>_<agent>[_v<vòng>].md`. NN là số file đầu ra: 01 architect, 02 spec-writer, 03 developer, 04 code-reviewer, 05 tester.
- **Trước khi gọi:** chụp `git status --porcelain` làm mốc. Ghi log gồm: giờ bắt đầu, người duyệt và lựa chọn ở cổng, nguyên văn phiếu duyệt, nguyên văn lời gọi gửi agent.
- **Sau khi agent xong:** bổ sung giờ kết thúc, thời lượng, trạng thái (xong/lỗi/dừng), nguyên văn kết quả agent trả về, và danh sách file thay đổi (so `git status --porcelain` với mốc). Chép transcript gốc của agent (file `output_file` mà Agent tool trả về) thành `logs/<NN>_<agent>.transcript.jsonl` bằng `cp`. **Không đọc file đó vào ngữ cảnh.**
- Riêng developer: thêm `logs/03_codex_events.jsonl` (sự kiện Codex, do agent ghi) và `codex_prompt.md`, `codex_last.md`.
- `log.md` vẫn giữ một dòng cho mỗi sự kiện (duyệt, bắt đầu, xong, dừng), trỏ tới file log chi tiết.
- Các file `*.jsonl` nằm trong `.gitignore`. File `.md` thì được commit.

## 2. Các bước
| Bước | Agent | Đầu ra | Ghi chú |
|---|---|---|---|
| 1 | `architect` | `01_kien_truc.md` | |
| 2 | `spec-writer` | `02_dac_ta.md` | Phiếu bước 3 lấy danh sách file từ đây |
| 3 | `developer` | `03_trien_khai.md`, `codex_prompt.md`, `codex_last.md` | Code do Codex CLI viết |
| 4 | `code-reviewer` ∥ `tester` | `04_review.md` (bạn ghi từ kết quả trả về), `05_kiem_thu.md` | Một phiếu chung; gọi hai agent song song trong cùng một lượt |

## 3. Cổng cuối
- Còn phát hiện Nghiêm trọng/Lớn hoặc AC không đạt: đề xuất vòng sửa (quay lại bước 3 với `04`, `05` làm đầu vào), **tối đa 2 vòng**; quá 2 vòng thì dừng và báo.
- Task có giao diện: hỏi có chạy thêm agent `ux-ui-agent-skills:design-critic` không.
- Đạt hết: cập nhật `PLAN.md`, tóm tắt theo `AGENTS.md` (3–5 dòng, file đã sửa, cách kiểm tra), gửi câu commit gợi ý và danh sách `git add`. **Không commit.**

## Luật
- "Tiếp tục" của người dùng chỉ duyệt bước đang trình.
- Không chạy tester song song với tester khác (dùng chung CSDL).
- Mọi luật trong `CLAUDE.md`, `AGENTS.md`, `.claude/rules/` vẫn áp dụng.
