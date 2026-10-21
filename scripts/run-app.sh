#!/bin/zsh
# Chạy ứng dụng Streamlit từ thư mục gốc (để đọc .streamlit/config.toml). Cần MariaDB và Manticore đang chạy.
set -e
cd "$(dirname "$0")/.."
exec .venv-exp/bin/streamlit run src/system/app/streamlit_app.py \
  --server.headless true --server.port "${PORT:-8501}" --server.address 127.0.0.1
