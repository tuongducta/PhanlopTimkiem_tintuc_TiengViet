# WORKTREE.md — Luật chạy song song (git cục bộ, không có remote)

- Mỗi phiên Claude chạy song song dùng 1 git worktree và 1 nhánh riêng:
  ```bash
  git worktree add ../TriThucDuLieu_BaiTap2-<task> -b task/<task>
  ```
- Worktree mới chỉ có file được git theo dõi. Những gì bị `.gitignore` phải tự đưa sang:
  - File cấu hình liệt kê trong `.worktreeinclude`: chép sang.
  - Dữ liệu lớn: tạo liên kết, không chép.
    ```bash
    ln -s "$PWD/sources/data" ../TriThucDuLieu_BaiTap2-<task>/sources/data
    ln -s "$PWD/sources/papers" ../TriThucDuLieu_BaiTap2-<task>/sources/papers
    ln -s "$PWD/sources/repos" ../TriThucDuLieu_BaiTap2-<task>/sources/repos
    ln -s "$PWD/src/system/models" ../TriThucDuLieu_BaiTap2-<task>/src/system/models
    ln -s "$PWD/.venv-exp" ../TriThucDuLieu_BaiTap2-<task>/.venv-exp
    ```
- Mỗi phiên chỉ sửa thư mục hoặc file được giao; ghi rõ cạnh task trong `PLAN.md`.
- Hai phiên không cùng sửa `PLAN.md`. Chỉ phiên chính cập nhật, sau khi merge.
- **Dùng chung một CSDL:** mọi worktree trỏ tới cùng MariaDB và Manticore trong Docker. Phiên song song không được chạy `schema.sql`, `sync_manticore.py` hay benchmark ghi bảng, vì sẽ đè dữ liệu của phiên khác.
- Xong việc:
  ```bash
  git -C ../TriThucDuLieu_BaiTap2-<task> commit
  git merge task/<task>              # ở worktree chính, nhánh main
  git worktree remove ../TriThucDuLieu_BaiTap2-<task>
  git branch -d task/<task>
  ```
