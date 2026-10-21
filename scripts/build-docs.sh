#!/bin/zsh
# Build lại hai sản phẩm nộp từ nguồn draft/. Chạy từ bất kỳ đâu.
#   survey:    livrables/survey/draft/*.md  → Survey_Trans2Vec_VN_News.md/.docx
#   báo cáo:   livrables/report_db/draft/*.md → BaoCao_CSDL_Trans2Vec.md/.docx (vẽ lại hình trước)
set -e
cd "$(dirname "$0")/.."
python3 livrables/survey/draft/build.py
python3 livrables/survey/draft/docx/build_docx.py
.venv-exp/bin/python livrables/report_db/make_figures.py
python3 livrables/report_db/build.py
find livrables -name __pycache__ -type d -prune -exec rm -r {} +
