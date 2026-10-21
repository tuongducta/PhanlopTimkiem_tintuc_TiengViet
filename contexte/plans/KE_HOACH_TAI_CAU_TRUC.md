# KẾ HOẠCH: dọn file thừa và tái cấu trúc theo mẫu "Harness 3 Tầng"

**Ngày lập:** 21/10/2026 · **Trạng thái:** ✅ đã duyệt và làm xong 21/10 (kết quả ở Mục 6).

**Quyết định của anh/chị:**
- **Q-R1:** tầng 2.
- **Q-R2:** không chọn mục nào ở 2b, nên **giữ nguyên** `.venv/`, các file `.rar`, cả 4 repo tham khảo và các bảng phụ trong CSDL. Chỉ xóa nhóm 2a.
- **Q-R3:** chuyển `system/` và `experiments/` vào **`src/`**.

**Mẫu tham chiếu:**
- Ảnh `harness-project_template_demo.png`.
- Bộ khung `../../harness-project_template.zip` (42 file).

**Mẫu gồm ba tầng:**

| Tầng | Nội dung |
|---|---|
| 1. Nền tảng | `CLAUDE.md`, `MAP.md`, `contexte/` (AI học được gì), `livrables/` (AI tạo ra gì) |
| 2. Harness đầy đủ | Thêm `CLAUDE.local.md`, `AGENTS.md`, `SPEC.md`, `PLAN.md`, `.mcp.json`, `.worktreeinclude`, `.claude/` (settings, rules, skills, agents, agent-memory, workflows, output-styles), `sources/` (tài liệu thô), `scripts/`, `docs/`, `.github/workflows/`, `.env.example`, `.gitignore`, `README.md` |
| 3. Đồng bộ | Thêm `WORKTREE.md`, `scripts/init-git.sh`, `docs/sync-guide.md`, Git và repo GitHub riêng tư |

---

## 1. Kiểm kê hiện trạng (dung lượng)

| Mục | Dung lượng | Dùng ở đâu |
|---|---|---|
| `.venv-exp/` (Python 3.11) | 771 MB | **Đang dùng**: thực nghiệm, pipeline, Streamlit |
| `data/vntc/` | 745 MB | `raw/` (526 MB) và `processed/` (99 MB) đang dùng; hai file `.rar` (121 MB) là bản nén gốc, đã giải nén |
| `.venv/` (Python 3.14) | 482 MB | **Không script nào dùng**: không chạy được gensim, chỉ có jupyter và matplotlib |
| `sourceGitSurvey/` | 389 MB | `Trans2Vec/` (55 MB) đang dùng (mốc gốc, E7). `GE-FSG/` (249 MB), `Sqn2Vec/` (13 MB), `UIT-ViON-Dataset/` (73 MB): không mã nguồn nào dùng; chỉ được nhắc trong ghi chú |
| `system/` | 237 MB | Đang dùng; `models/` khoảng 230 MB |
| `DocumentsSurvey/` | 50 MB | PDF tài liệu, được các phiếu đọc trỏ tới |
| `report_db/`, `survey/`, `experiments/` | 4,5 MB | Đang dùng |
| `.idea/`, `.junie/` | 156 KB | Cấu hình IDE; `.junie/plans/` rỗng |

---

## 2. Xóa file thừa

### 2a. Xóa ngay sau khi duyệt (rác tự sinh hoặc bản chạy dở, không ai tham chiếu)

| Mục | Lý do |
|---|---|
| Mọi thư mục `__pycache__/` (`system/`, `experiments/`) | Python tự sinh lại |
| Mọi `.DS_Store` | macOS tự sinh |
| `experiments/results_elbow_loglog_partial/` | Bản chạy dở ngày 07/10, đã thay bằng `results/` |
| `experiments/results_quick/` | Kết quả chế độ `--quick`, chạy thử ngày 18/10; không tài liệu nào dùng số liệu này |
| `report_db/reference.docx` | Mẫu Word mà `build.py` dựng lại mỗi lần chạy |
| `.junie/` | Thư mục rỗng của plugin IDE |
| `system/bench/results/edb4_hybrid_before_p1.json` | **Giữ lại**: là số liệu tham chiếu ở Mục 20 |

### 2b. Xóa nếu anh/chị đồng ý (lớn; không mã nguồn nào dùng, nhưng là bản gốc)

| Mục | Tiết kiệm | Rủi ro |
|---|---|---|
| `.venv/` (Python 3.14) | 482 MB | Nếu anh/chị dùng nó cho notebook riêng thì sẽ mất; tạo lại được bằng pip |
| `data/vntc/Train_Full.rar`, `Test_Full.rar` | 121 MB | Bản nén gốc của VNTC; tải lại được, thư mục `raw/` đã giải nén đủ |
| `sourceGitSurvey/GE-FSG/` | 249 MB | Repo tham khảo, có trên GitHub |
| `sourceGitSurvey/Sqn2Vec/` | 13 MB | Như trên. Survey trích dẫn bài báo, không dùng mã |
| `sourceGitSurvey/UIT-ViON-Dataset/` | 73 MB | Chỉ nhắc trong `survey/notes/candidates.md` |

Tổng phần 2b: khoảng 940 MB.

### 2c. Giữ nguyên

- `system/models/`: mọi tệp đều gắn với một dòng `model_run`, kể cả TF-IDF (run 6/7) cho trang Dữ liệu.
- Log `experiments/*_stdout.log` và `system/**/*.log`: bằng chứng của các lần chạy, nhỏ.
- `.idea/`: cấu hình IntelliJ của anh/chị; sẽ được đưa vào `.gitignore`.
- **Trong CSDL**, không phải file: các bảng phụ thực nghiệm `vec_m6`, `vec_m16` (MariaDB) và `ft_only`, `vec_m6`, `vec_m16`, `news_fold` (Manticore). Chỉ xóa nếu anh/chị muốn; E-DB1, 2, 5 sẽ tự dựng lại khi chạy.

---

## 3. Cấu trúc đích (đề xuất theo tầng 2)

```
TriThucDuLieu_BaiTap2/
├── CLAUDE.md            # vai trò, quy tắc làm việc (tiếng Việt, kế hoạch trước khi làm, các điều cấm)
├── CLAUDE.local.md      # sở thích cá nhân (xưng hô...) — không đưa lên git
├── AGENTS.md            # quy tắc chung cho mọi agent: thư mục nào được sửa, lệnh build/test
├── MAP.md               # bản đồ dự án: cái gì ở đâu (thay TIEP_TUC.md đã cũ)
├── SPEC.md              # mục tiêu: 2 môn, 2 sản phẩm nộp, tiêu chí (giới hạn 25–30 trang...)
├── PLAN.md              # lộ trình và trạng thái, trỏ tới các kế hoạch chi tiết
├── README.md            # cài đặt, chạy Docker, Streamlit, build tài liệu
├── .mcp.json  .worktreeinclude  .env.example  .gitignore
├── .claude/
│   ├── settings.json  settings.local.json
│   ├── rules/           # vd. survey-draft.md: chỉ sửa draft rồi build; system-code.md
│   ├── skills/          # vd. build-docs/SKILL.md (build survey + báo cáo + đếm trang)
│   ├── agents/          # vd. reviewer.md (rà số liệu và trích dẫn)
│   ├── agent-memory/  workflows/  output-styles/
├── contexte/            # AI học được gì
│   ├── plans/           # KE_HOACH_SURVEY.md, KE_HOACH_SURVEY_v3.md, KE_HOACH_HE_THONG_DB.md, KE_HOACH_TAI_CAU_TRUC.md
│   ├── results/         # RESULTS.md (thực nghiệm), RESULTS_DB.md (CSDL)
│   └── survey-notes/    # survey/notes/, synthesis.md, review_log.md
├── sources/             # tài liệu thô, chỉ đọc
│   ├── papers/          # ← DocumentsSurvey/
│   ├── repos/           # ← sourceGitSurvey/ (cả 4 repo, vì Q-R2 không xóa)
│   └── data/vntc/       # ← data/vntc/
├── livrables/           # AI tạo ra gì: sản phẩm nộp và nguồn dựng chúng
│   ├── survey/          # ← survey/ (draft/, figures/, .md, .docx)
│   └── report_db/       # ← report_db/ (draft/, figures/, .md, .docx)
├── src/
│   ├── system/          # mã nguồn hệ thống MariaDB + Manticore (Q-R3)
│   └── experiments/     # mã thực nghiệm Trans2Vec (Q-R3)
├── scripts/             # lệnh tiện ích: build-docs.sh, run-app.sh, count-pages.sh
├── docs/                # harness-project_template_demo.png, hướng dẫn
└── .github/workflows/   # check.yml: kiểm tra cú pháp Python, build tài liệu
```

**Vì sao giữ `system/` và `experiments/` ở gốc:**
- Mẫu không có thư mục mã nguồn.
- Đưa vào `src/` sẽ phải sửa mọi `ROOT = parents[...]` và đường dẫn tới mô hình, kèm rủi ro hỏng app đang chạy, mà không có lợi ích chức năng.
- `MAP.md` sẽ mô tả rõ hai thư mục này.

**Chỗ phải sửa đường dẫn khi di chuyển:**

| Di chuyển | File phải sửa |
|---|---|
| `data/` → `sources/data/` | `experiments/prepare.py`, `run_experiments.py`, `system/pipeline/load_articles.py` |
| `sourceGitSurvey/Trans2Vec` → `sources/repos/Trans2Vec` | `experiments/replicate_snippets.py`; chú thích trong `system/pipeline/train_variants.py` |
| `report_db/` → `livrables/report_db/` | `make_figures.py` (`parents[1]` → `parents[2]`); `build.py` vẫn đúng vì `survey/` nằm cùng cấp |
| `survey/` → `livrables/survey/` | Không phải sửa: `build.py` và `build_docx.py` dùng đường dẫn tương đối với chính chúng |
| `RESULTS*.md`, các `KE_HOACH*.md` | Liên kết văn bản trong README, MAP, bộ nhớ |

Đường dẫn dạng chữ trong các tài liệu (ví dụ "`DocumentsSurvey/...`" trong phiếu đọc) sẽ được thay bằng tìm-thay có kiểm tra. **Riêng `KE_HOACH_SURVEY.md`** anh/chị từng dặn không sửa, nên em chỉ di chuyển file này, không sửa nội dung.

**Kiểm tra sau khi chuyển:**
- Chạy lại `python3 -m py_compile` toàn bộ code.
- Kiểm thử AppTest qua 4 trang.
- Build survey và báo cáo (báo cáo phải vẫn 30 trang).
- Chạy `check_setup.py`.
- Khởi động lại Streamlit.

---

## 4. Tầng 3 (Git và GitHub)

**Đề xuất:** làm tầng 2 trước. Tầng 3 cần anh/chị quyết riêng vì đẩy dữ liệu ra ngoài máy.
- `git init` cục bộ. `.gitignore` loại `.venv*`, `sources/data/`, `system/models/`, `.env`, `CLAUDE.local.md`, `.idea/`.
- PDF trong `sources/papers/` có thể vướng bản quyền nếu đưa lên repo, kể cả repo riêng tư; đề xuất cũng loại khỏi git.
- Tạo repo GitHub riêng tư và push chỉ làm khi anh/chị xác nhận tài khoản và tên repo.

---

## 5. Cần anh/chị duyệt

- **Q-R1:** áp dụng tầng nào: 2 (đề xuất), hay 3 (thêm git, và GitHub nếu có)?
- **Q-R2:** những mục nào ở 2b được xóa?
- **Q-R3:** đồng ý giữ `system/` và `experiments/` ở gốc (đề xuất), hay chuyển vào `src/`?

---

## 6. Kết quả (21/10/2026)

**Đã xóa** (nhóm 2a):
- 6 thư mục `__pycache__/`;
- 2 file `.DS_Store`;
- `experiments/results_elbow_loglog_partial/`, `experiments/results_quick/`;
- `report_db/reference.docx` (build tự sinh lại);
- `.junie/` (thư mục rỗng).

Nhóm 2b giữ nguyên theo Q-R2.

**Đã di chuyển:** theo Mục 3. Ánh xạ cũ → mới:

| Cũ | Mới |
|---|---|
| `system/`, `experiments/` | `src/` |
| `data/` | `sources/data/` |
| `DocumentsSurvey/` | `sources/papers/` |
| `sourceGitSurvey/` | `sources/repos/` |
| `survey/`, `report_db/` | `livrables/` |
| `survey/notes/`, `synthesis.md`, `review_log.md` | `contexte/survey-notes/` |
| `KE_HOACH_*.md` | `contexte/plans/` |
| `RESULTS*.md` | `contexte/results/` |
| `TIEP_TUC*.md` | `contexte/archive/` |
| Ảnh mẫu | `docs/` |

**Đã sửa đường dẫn:**
- **Code:** `load_articles.py`, `sync_manticore.py`, `train_models.py`, `search.py` (gốc dự án là `parents[3]`, thư mục mã `src/system`, `src/experiments`); `prepare.py`, `run_experiments.py`, `replicate_snippets.py` (`parents[2]`, `sources/...`); `livrables/report_db/make_figures.py`. Lệnh chạy trong docstring của 28 file được sửa theo.
- **Tài liệu:** 125 chỗ trong `contexte/` và `src/system/README.md`. Không sửa: `KE_HOACH_SURVEY.md` (bị cấm); bản nháp và bản build của survey (chờ Q5); `contexte/archive/`; Mục 1–5 của file này.
- **Báo cáo CSDL:** đường dẫn `src/system/...` trong draft; build lại vẫn **30 trang**.
- **Bộ nhớ của Claude:** đường dẫn trong các file nhớ, thêm `project-structure-harness.md`.

**File harness mới:**
- `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, `MAP.md`, `SPEC.md`, `PLAN.md`, `README.md`;
- `.mcp.json`, `.worktreeinclude`, `.env.example`, `.gitignore` (viết lại cho Python, loại dữ liệu lớn và PDF);
- `.claude/`: `settings.json`; `rules/` (coding-style, livrables, system-db); `skills/build-docs`; `agents/reviewer`; `agent-memory/`; `workflows/release`; `output-styles/concise-vi`. File `settings.local.json` cũ giữ nguyên;
- `scripts/`: `build-docs.sh`, `run-app.sh`, `count-pages.sh`;
- `.github/workflows/check.yml`: chặn commit `.env`, kiểm tra cú pháp Python.

**Kiểm tra:**
- `py_compile` toàn bộ code đạt.
- `check_setup.py` đạt.
- AppTest 4 trang đạt.
- `docker compose -f src/system/docker-compose.yml ps` nhận đúng hai container đang chạy.
- Build survey ra `.md` giống hệt bản cũ.
- `scripts/build-docs.sh` và `scripts/count-pages.sh` chạy được; báo cáo 30 trang.
- `scripts/run-app.sh` chạy được; ảnh chụp trang Dữ liệu hiển thị đầy đủ.
- Dòng nhật ký do kiểm thử sinh ra đã xóa.

**Chưa làm hoặc lưu ý:**
- `.idea/` (IntelliJ) có thể còn trỏ tới thư mục cũ; IDE thường tự cập nhật khi mở lại.
- Bản nháp survey vẫn nhắc `experiments/RESULTS.md` dạng chữ; sẽ sửa khi làm GĐ11 (chờ Q5).
- Tầng 3: xem Mục 7.

---

## 7. Tầng 3, chỉ git cục bộ (21/10/2026, người dùng yêu cầu)

**File mới:**
- `WORKTREE.md`: luật chạy song song. Bổ sung so với mẫu: tạo liên kết tới dữ liệu và mô hình nằm ngoài git; cảnh báo các phiên dùng chung một CSDL.
- `scripts/init-git.sh`: chỉ khởi tạo cục bộ. Bỏ phần `gh repo create` và push của mẫu; chạy lại được.
- `docs/sync-guide.md`: quy ước commit và gộp nhánh khi chưa có remote.

**Repo:**
- `git init -b main`. Danh tính đặt riêng cho repo (`user.name` "Tạ Tường" lấy từ tài khoản macOS, `user.email` của người dùng); không đổi cấu hình toàn máy.
- Commit đầu `3b93759`: 172 file, 5,8 MB, thư mục `.git` 5,3 MB.
- Trước khi commit đã kiểm tra: không có `.env`, `.venv*`, `sources/data|papers|repos`, `src/system/models/`, `CLAUDE.local.md`, `.idea/`. Chỉ có mật khẩu mặc định cho máy cá nhân trong `docker-compose.yml`, đã ghi rõ trong README.
- Chưa có remote, chưa push.

