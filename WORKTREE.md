# WORKTREE.md — Luật chạy song song (git worktree; chỉ phiên chính push)

- Mỗi phiên Claude chạy song song dùng 1 git worktree và 1 nhánh riêng. Tên thư mục worktree phải có đuôi `.nosync`, vì `~/Documents` đang được iCloud đồng bộ:
  ```bash
  git worktree add ../TriThucDuLieu_BaiTap2-<task>.nosync -b task/<task>
  ```
- Worktree mới chỉ có file được git theo dõi. Những gì bị `.gitignore` phải tự đưa sang:
  - File cấu hình liệt kê trong `.worktreeinclude`: chép sang.
  - Dữ liệu lớn: tạo liên kết, không chép.
    ```bash
    ln -s "$PWD/sources/data" ../TriThucDuLieu_BaiTap2-<task>.nosync/sources/data
    ln -s "$PWD/sources/papers" ../TriThucDuLieu_BaiTap2-<task>.nosync/sources/papers
    ln -s "$PWD/sources/repos" ../TriThucDuLieu_BaiTap2-<task>.nosync/sources/repos
    ln -s "$PWD/src/system/models" ../TriThucDuLieu_BaiTap2-<task>.nosync/src/system/models
    ln -s "$PWD/.venv-exp" ../TriThucDuLieu_BaiTap2-<task>.nosync/.venv-exp
    ```
- Mỗi phiên chỉ sửa thư mục hoặc file được giao; ghi rõ cạnh task trong `PLAN.md`.
- Hai phiên không cùng sửa `PLAN.md`. Chỉ phiên chính cập nhật, sau khi merge.
- **Dùng chung một CSDL:** mọi worktree trỏ tới cùng MariaDB và Manticore trong Docker. Phiên song song không được chạy `schema.sql`, `sync_manticore.py` hay benchmark ghi bảng, vì sẽ đè dữ liệu của phiên khác.
- Xong việc (**người dùng tự commit và merge**; Claude chỉ gợi ý lệnh):
  ```bash
  git -C ../TriThucDuLieu_BaiTap2-<task>.nosync commit
  git merge task/<task>              # ở worktree chính, nhánh main
  git worktree remove ../TriThucDuLieu_BaiTap2-<task>.nosync
  git branch -d task/<task>
  ```
