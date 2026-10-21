# Đồng bộ 3 bước (git cục bộ)

Remote `origin` = GitHub riêng tư `tuongducta/PhanlopTimkiem_tintuc_TiengViet`. Chỉ push khi người dùng yêu cầu. Trước khi push, kiểm tra không có `.env` và không có PDF có bản quyền.

1. **Đầu phiên:** chạy `git status`. Phải sạch; nếu còn thay đổi dở thì commit hoặc `git stash` trước.
2. **Làm và commit nhỏ** (người dùng tự commit; Claude chỉ gợi ý câu commit): mỗi bước trong `PLAN.md` là một commit, tiền tố `feat:`, `fix:`, `docs:`, `chore:`, `data:`. Ví dụ:
   - `docs(report_db): rút gọn chương 7 còn 30 trang`
   - `feat(search): nhánh gộp dấu cho truy vấn không dấu`
3. **Gộp:** phiên song song làm trên worktree và nhánh riêng (xem `WORKTREE.md`). Xong thì `git merge task/<task>` vào `main`.

**Không đưa vào git** (đã có trong `.gitignore`): `.env`, `CLAUDE.local.md`, `.venv*`, `sources/data|papers|repos`, `src/system/models/`. Những thứ này sao lưu riêng; mô hình sinh lại được bằng `train_models.py` và `train_variants.py`.

**Đẩy lên:** `git push -u origin main` (lần đầu), sau đó `git push`.
