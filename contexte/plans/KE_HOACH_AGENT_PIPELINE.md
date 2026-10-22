# KẾ HOẠCH: pipeline nhiều agent có cổng duyệt

**Ngày lập:** 22/10/2026 · **Trạng thái:** ✅ duyệt 22/10 (Q-A1–Q-A7 theo đề xuất); đợt 1 dựng xong khung, chờ chạy thử (Mục 9).

**Thay đổi sau khi duyệt (22/10):** phần lập trình do **Codex CLI** làm. Agent `developer` không tự viết code mà soạn `codex_prompt.md`, chạy `codex exec -s workspace-write`, rồi kiểm diff và `py_compile`.

**Mục tiêu:** tách công việc cho 5 agent: kiến trúc, đặc tả, lập trình, review, kiểm thử. Agent này xong thì đến lượt agent kế. **Trước mỗi agent, phiên chính trình phiếu duyệt để anh/chị quyết định.**

---

## 1. Nguyên tắc thiết kế

| # | Nguyên tắc | Lý do |
|---|---|---|
| N1 | Phiên chính là **điều phối**; agent không tự gọi agent kế | Subagent của Claude Code không gọi được subagent khác. Cổng duyệt cũng phải nằm ở phiên chính |
| N2 | Bàn giao bằng file trong `contexte/handoff/<task>/` | Chạy lại một bước không cần lại cả hội thoại; anh/chị đọc và sửa được trước khi duyệt |
| N3 | Mỗi agent chỉ có đúng quyền cần dùng (`tools`, vùng ghi) | Reviewer không sửa file; architect và spec không đụng `src/` |
| N4 | Không bước nào tự chuyển sang bước sau | Dù bước trước báo "đạt", vẫn trình phiếu duyệt |
| N5 | Tester chạy tuần tự, không song song với tester khác | Dùng chung MariaDB và Manticore (`WORKTREE.md`) |
| N6 | Giữ nguyên luật hiện có | Không commit/push, không sửa `sources/`, xóa log kiểm thử, hỏi trước khi cài thư viện |

## 2. Luồng chạy

```
/pipeline <task> "<mô tả>"
  │
  ├─ Cổng 0: phiếu duyệt architect ──► anh/chị: Duyệt / Sửa / Bỏ qua bước / Dừng
  ├─ architect   → 01_kien_truc.md (+ ADR nếu có quyết định lớn)
  ├─ Cổng 1: tóm tắt 01 + phiếu duyệt spec-writer
  ├─ spec-writer → 02_dac_ta.md (tiêu chí nghiệm thu AC-1, AC-2…)
  ├─ Cổng 2: tóm tắt 02 + phiếu duyệt developer (danh sách file sẽ sửa, lệnh sẽ chạy)
  ├─ developer   → code trong src/ + 03_trien_khai.md
  ├─ Cổng 3: tóm tắt 03 + phiếu duyệt reviewer và tester (chạy song song)
  ├─ code-reviewer → 04_review.md      tester → 05_kiem_thu.md
  ├─ Cổng 4: tổng hợp
  │     • còn lỗi Nghiêm trọng/Lớn hoặc AC chưa đạt → đề xuất vòng sửa (quay lại developer, tối đa 2 vòng)
  │     • đạt hết → cập nhật PLAN.md, gửi câu commit gợi ý
  └─ Kết thúc
```

- Mỗi task có thể **bỏ bước**. Ví dụ sửa lỗi nhỏ: bỏ architect, bắt đầu từ spec-writer. Việc bỏ bước được chọn ở cổng 0.
- Trả lời "tiếp tục" ở một cổng nghĩa là duyệt đúng bước đó, không phải duyệt cả chuỗi.

### Mẫu phiếu duyệt (phiên chính trình trước mỗi agent)

```
── Phiếu duyệt · Bước 3/5 · developer ──
Task:        ui-contrast-fix
Đầu vào:     contexte/handoff/ui-contrast-fix/02_dac_ta.md (AC-1…AC-4)
Sẽ làm:      sửa màu nút chính, màu chữ phụ, lỗi "nan" ở tin RSS
Sẽ sửa file: src/system/app/streamlit_app.py
Sẽ chạy:     py_compile; khởi động lại Streamlit
Không làm:   đổi bố cục, đụng CSDL
Rủi ro:      thấp, hoàn tác được bằng git
→ Duyệt / Sửa phạm vi / Bỏ qua bước / Dừng
```

Phiên chính hỏi bằng câu hỏi lựa chọn (AskUserQuestion) để anh/chị bấm chọn, không phải gõ.

## 3. Năm agent

| Agent (file) | Việc | `tools` | Được ghi | Skill dùng | `model` |
|---|---|---|---|---|---|
| `architect` (mới) | Chọn hướng, ranh giới module, ảnh hưởng tới DDL và benchmark | Read, Grep, Glob, Write, Skill | `contexte/handoff/`, `contexte/decisions/` | `codebase-design`, `archify`, `decision-records` | opus |
| `spec-writer` (mới) | Đặc tả chức năng, tiêu chí nghiệm thu, đặc tả UI và câu chữ | Read, Grep, Glob, Write, Skill | `contexte/handoff/`, `livrables/*/draft/` (chỉ khi task là tài liệu) | `design-screen`/`design-component` (chỉ phần đặc tả), `ux-writing`, `build-docs` | opus |
| `developer` (mới) | Viết code đúng đặc tả, không mở rộng phạm vi | Read, Grep, Glob, Edit, Write, Bash, Skill | `src/`, `contexte/handoff/` | `design-code`, `codebase-design`, `simplify` | sonnet |
| `code-reviewer` (mới) | Rà code và đối chiếu với AC; không sửa file | Read, Grep, Glob, Bash (chỉ `git diff`), Skill | `contexte/handoff/` (chỉ file 04) | `code-review`, `security-review`, `design-review`, `a11y-audit` | opus |
| `tester` (mới) | Chạy kiểm thử theo từng AC, chụp màn hình, dọn log | Read, Grep, Glob, Bash, Write, Skill | `contexte/handoff/` | `run`, `design-qa`, `a11y-audit` | sonnet |
| `reviewer` (giữ nguyên) | Rà `livrables/` so với SPEC và số liệu | Read, Grep, Glob | — | — | — |

Ngoài ra dùng agent `ux-ui-agent-skills:design-critic` ở cổng 4, chỉ khi task có giao diện.

**Cần xác minh ở bước 0 (Claude Code 2.1.308):**
- Frontmatter của subagent có nhận trường `skills:` để nạp sẵn skill không. Nếu không, ghi tên skill trong phần hướng dẫn của agent để agent tự gọi bằng `Skill`.
- Trường `tools` có giới hạn được theo mẫu lệnh, ví dụ `Bash(git diff:*)`, không. Nếu không, đặt giới hạn trong `settings.json` và trong lời dặn của agent.
- Trường `memory:` có dùng được với `.claude/agent-memory/` không.

### Khung chung của mỗi file agent (ví dụ `developer.md`)

```markdown
---
name: developer
description: Viết code theo contexte/handoff/<task>/02_dac_ta.md. Chỉ gọi khi phiếu duyệt bước developer đã được duyệt.
tools: Read, Grep, Glob, Edit, Write, Bash, Skill
model: sonnet
---
Bạn là lập trình viên của dự án. Đọc CLAUDE.md, AGENTS.md, .claude/rules/*.md trước.
Đầu vào: 01_kien_truc.md (nếu có), 02_dac_ta.md của task.
1. Chỉ sửa các file đã nêu trong phiếu duyệt. Cần sửa thêm thì dừng và ghi vào mục "Việc mở".
2. Chạy py_compile cho file đã sửa. Sửa search.py/classify.py thì ghi rõ cần khởi động lại Streamlit.
3. Không chạy schema.sql, sync_manticore.py, benchmark. Không commit.
Đầu ra: 03_trien_khai.md theo contexte/handoff/_template.md (file đã sửa, AC nào đã làm, cách chạy thử, việc mở).
Không tự gọi agent khác.
```

Bốn agent còn lại dùng cùng khung, khác ở đầu vào, vùng ghi, các bước và tên file đầu ra.

## 4. Các file thêm mới hoặc sửa

### Đợt 1: dựng khung và chạy thử

| # | File | Thay đổi |
|---|---|---|
| 1.1 | `.claude/agents/architect.md`, `spec-writer.md`, `developer.md`, `code-reviewer.md`, `tester.md` | Tạo mới theo Mục 3 |
| 1.2 | `.claude/skills/pipeline/SKILL.md` | Skill `/pipeline <task> "<mô tả>"`: tạo thư mục handoff, chọn bước, trình phiếu duyệt, gọi agent, tóm tắt, vòng sửa tối đa 2 lần, cập nhật PLAN.md |
| 1.3 | `contexte/handoff/_template.md` | Mẫu chung: Đầu vào · Quyết định · Đầu ra · Tiêu chí (AC) · Việc mở cho bước sau · Cách kiểm tra |
| 1.4 | `contexte/handoff/README.md` | Quy ước đặt tên: `<task>/01_kien_truc.md` … `05_kiem_thu.md`, `log.md` |
| 1.5 | `AGENTS.md` | Thêm mục "Hợp đồng bàn giao": agent đọc gì, ghi gì, được sửa ở đâu; agent không tự gọi agent khác |
| 1.6 | `CLAUDE.md` | Thêm vào "Quy tắc làm việc": khi chạy pipeline thì trình phiếu duyệt trước mỗi agent; "tiếp tục" chỉ duyệt bước đang trình |
| 1.7 | `.claude/workflows/release.md` | Thêm bước 0: task có sửa code thì chạy `/pipeline` trước, sau đó mới tới build và giao nộp |
| 1.8 | `.claude/settings.json` | Thêm quyền `Edit(./.claude/agents/**)`, `Edit(./.claude/skills/**)`. Thêm quyền Bash cho tester: `.venv-exp/bin/python -m py_compile:*`, `check_setup.py`, `scripts/run-app.sh` |
| 1.9 | `MAP.md` | Thêm dòng cho `contexte/handoff/`, `contexte/decisions/`, các agent mới |
| 1.10 | `PLAN.md` | Thêm mục "Tổ chức dự án → Pipeline agent", mỗi task một dòng trạng thái 5 bước |

**Chạy thử đợt 1** bằng task nhỏ `ui-contrast-fix`, tức lỗi #1–#3 của lần design-review ngày 22/10:
1. Nút chính chữ trắng trên cyan, tương phản 2,43:1.
2. Chữ phụ `#64748B`, tương phản 4,03–4,18:1.
3. Tin RSS không có mô tả hiện chữ "nan".

Bỏ bước architect. Chạy spec → developer → review + test. Đo xem phiếu duyệt có đủ thông tin không, và file bàn giao có quá dài không.

### Đợt 2: tự động hóa thêm (chỉ làm khi đợt 1 ổn)

| # | File | Thay đổi |
|---|---|---|
| 2.1 | `.claude/settings.json` | Hook `SubagentStop`: ghi một dòng (giờ, agent, task, kết quả) vào `contexte/handoff/<task>/log.md` |
| 2.2 | `.claude/settings.json` | Thông báo đẩy khi một agent xong và đang chờ duyệt |
| 2.3 | `WORKTREE.md`, `.claude/agents/developer.md` | Cho developer chạy trong worktree riêng (`isolation: worktree`) với các task lớn |
| 2.4 | `.claude/agent-memory/<agent>/` | Mỗi agent ghi lỗi hay gặp, quy ước đã chốt |

## 5. Ranh giới không tự động hóa

- Không commit, push hay merge. Kết thúc pipeline chỉ gửi câu commit gợi ý.
- Không chạy `schema.sql`, `sync_manticore.py`, benchmark ghi bảng khi phiếu duyệt không ghi rõ.
- Không cài thư viện mới. Cần cài thì dừng và hỏi.
- Không sửa `sources/`, `contexte/plans/KE_HOACH_SURVEY.md`, file đã build trong `livrables/`.
- Tester xóa các dòng `search_log` và `classify_log` do mình sinh ra: ghi `MAX(id)` trước khi test, xóa `id >` mốc đó sau khi test.

## 6. Kiểm tra sau khi làm

| Việc | Cách kiểm tra |
|---|---|
| Agent mới được nhận | `/agents` liệt kê đủ 5 agent mới, đúng `tools` và `model` |
| Skill pipeline | `/pipeline` có trong danh sách skill; chạy thử dừng đúng ở cổng 0 |
| Quyền | Reviewer thử ghi file thì bị từ chối; developer không sửa được `sources/` |
| Chạy thử | Task `ui-contrast-fix` đủ 5 file handoff, chụp màn hình trước và sau, log kiểm thử đã xóa |

## 7. Ước lượng

- Đợt 1: khoảng 12 file mới hoặc sửa, cộng một lần chạy thử.
- Đợt 2: khoảng 4 thay đổi, làm sau.

## 8. Câu hỏi cần anh/chị chốt

| # | Câu hỏi | Đề xuất |
|---|---|---|
| Q-A1 | Tên agent tiếng Anh (`architect`, `spec-writer`…) hay tiếng Việt? | Tiếng Anh, khớp quy ước đặt tên trong code; mô tả và nội dung viết tiếng Việt |
| Q-A2 | Agent review code là file mới `code-reviewer`, hay mở rộng `reviewer` hiện có? | File mới; giữ `reviewer` cho `livrables/` vì hai việc khác nhau |
| Q-A3 | Số vòng sửa tối đa khi review hoặc test chưa đạt? | 2 vòng; quá 2 vòng thì dừng, báo anh/chị |
| Q-A4 | Phiếu duyệt hỏi bằng câu hỏi bấm chọn hay chỉ in ra rồi chờ gõ "tiếp tục"? | Bấm chọn, nhanh hơn và ít nhầm hơn |
| Q-A5 | Cho reviewer và tester chạy song song ở cổng 3? | Có; reviewer chỉ đọc nên không va chạm |
| Q-A6 | Có dùng task `ui-contrast-fix` để chạy thử đợt 1 không? | Có; task nhỏ, đủ 4 bước, kết quả kiểm chứng được bằng ảnh chụp |
| Q-A7 | Làm luôn đợt 2 hay đợi đợt 1 chạy ổn? | Đợi đợt 1 |

## 9. Kết quả đợt 1 (22/10)

**Bước 0, xác minh Claude Code 2.1.308:**
- Frontmatter agent nhận: `tools`, `disallowedTools`, `model`, `effort`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, `initialPrompt`, `memory`, `background`, `omitClaudeMd`, `isolation`. Nguồn: danh sách trường trong binary.
- **Không** dùng `skills:` để nạp sẵn, vì nạp sẵn đưa toàn bộ nội dung skill vào ngữ cảnh agent. Agent gọi skill bằng tool `Skill` khi cần.
- Giới hạn Bash theo mẫu lệnh đặt trong lời dặn của agent. Agent chỉ đọc được chặn bằng `disallowedTools: Edit, Write`.
- Codex CLI 0.158.0 ở `/opt/homebrew/bin/codex`, đã đăng nhập (ChatGPT), model mặc định `gpt-6-luna`.

**Đã làm:**

| Hạng mục | File | Ghi chú |
|---|---|---|
| 1.1 | `.claude/agents/architect.md`, `spec-writer.md`, `developer.md`, `code-reviewer.md`, `tester.md` | `developer` điều khiển Codex; `code-reviewer` không ghi file, phiên điều phối ghi `04_review.md` |
| 1.2 | `.claude/skills/pipeline/SKILL.md` | Skill `/pipeline` đã được nhận ngay trong phiên |
| 1.3–1.4 | `contexte/handoff/_template.md`, `README.md` | |
| 1.5 | `AGENTS.md` | Mục "Hợp đồng bàn giao", áp dụng cả cho Codex vì Codex tự đọc AGENTS.md |
| 1.6 | `CLAUDE.md` | Quy tắc số 10 |
| 1.7 | `.claude/workflows/release.md` | Bước 0 |
| 1.8 | `.claude/settings.json` | Thêm quyền Edit cho `.claude/agents/**`, `.claude/skills/**`; Bash: `run-app.sh`, `git status:*`, `git log:*`, `docker ps:*`, `py_compile`. **Không** cho `codex exec` tự chạy, mỗi lần chạy vẫn hỏi |
| 1.9–1.10 | `MAP.md`, `PLAN.md` | |

**Chưa làm được:** thêm `deny` cho `codex exec --dangerously-bypass-approvals-and-sandbox` / `--yolo` vào `settings.json`. Bộ phân loại an toàn của chế độ auto đã chặn lệnh sửa này. Lời dặn trong `developer.md` đã cấm hai cờ đó; anh/chị có thể tự thêm dòng `deny` nếu muốn chặn cứng.

**Còn lại của đợt 1:** chạy thử `/pipeline ui-contrast-fix` (bỏ architect). Các agent mới có thể chỉ được nạp sau khi khởi động lại phiên Claude Code.

## 10. Chạy thử `/pipeline ui-contrast-fix` (22/10, 16:25–17:45)

**Kết quả:** 13/13 AC đạt sau vòng đầu và 2 vòng sửa (đúng giới hạn). Chi tiết ở `contexte/handoff/ui-contrast-fix/log.md` và `logs/`.

| Lượt | Agent (thời lượng) | Kết quả chính |
|---|---|---|
| 1 | spec-writer (134 giây) | 13 AC; phương án A cho nút chính; tự thêm dòng 829 (`classify_news`) vào phạm vi |
| 1 | developer/Codex (98 giây) | 9 khối, đúng phạm vi, py_compile OK |
| 1 | code-reviewer (73 giây) ∥ tester (503 giây) | 0 lỗi Lớn; 12/13 AC; AC-8 một phần (đường dẫn tệp 11px xuống dòng) |
| Sửa 1 | developer/Codex (131 giây) | `.fl.path` nowrap + `max-width: 420px` |
| Sửa 1 | code-reviewer (574 giây) ∥ tester (872 giây) | Cả hai độc lập kết luận hồi quy: bảng tràn 608/554px |
| Sửa 2 | developer/Codex (40 giây) | `width: 0; min-width: 100%` (đề xuất của reviewer) |
| Sửa 2 | tester (148 giây), bỏ reviewer | AC-8 đạt; bề rộng cột về như vòng 1 |

**Bài học (đã đưa vào `.claude/skills/pipeline/SKILL.md`):**
1. Đầu vào chỉ nằm trong hội thoại (ví dụ bản design-review) thì phiên điều phối ghi ra `00_dau_vao.md` trước khi gọi agent đầu tiên.
2. File cần sửa đã có thay đổi chưa commit thì `git diff` không tách được phần của agent. Chụp `logs/<file>.before[_vN].py` trước mỗi lượt developer, so bằng `diff -u`.
3. Tester phải ghi số đo bố cục (bề rộng cột, chiều cao hàng) ngay từ vòng đầu, để có mốc so cho các vòng sửa.
4. Phiếu developer ở vòng sửa nên được reviewer soát trước khi giao Codex. Ở vòng sửa 1, `max-width: 420px` là con số Codex tự ước lượng. Rủi ro này đã được nêu nhưng vẫn mất một vòng.
5. Ảnh chụp `shots/` khá nặng (14 MB/task). Transcript `*.jsonl` đã nằm trong `.gitignore`.
