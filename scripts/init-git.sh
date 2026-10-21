#!/usr/bin/env bash
# Khởi tạo git CỤC BỘ cho dự án (tầng 3, không có remote, không push).
# Dùng: ./scripts/init-git.sh            (chạy lại được: nếu đã có .git thì chỉ báo trạng thái)
set -euo pipefail
cd "$(dirname "$0")/.."
if [ -d .git ]; then
  echo "Đã có repo git:"; git status -sb | head -5; exit 0
fi
git init -b main
# danh tính chỉ đặt cho repo này nếu máy chưa cấu hình toàn cục
git config user.name >/dev/null || git config user.name "$(id -F 2>/dev/null || whoami)"
git config user.email >/dev/null || { echo "Đặt email: git config user.email <email>"; exit 1; }
git add .
echo "Sẽ commit $(git diff --cached --name-only | wc -l | tr -d ' ') file, $(git diff --cached --stat | tail -1)"
git commit -m "chore: khởi tạo repo theo harness tầng 3 (git cục bộ)"
echo "Xong. Muốn đưa lên GitHub sau này: tạo repo private rồi 'git remote add origin …' và 'git push -u origin main'."
