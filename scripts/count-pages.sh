#!/bin/zsh
# Đếm số trang A4 của một .docx bằng cách xuất PDF qua Microsoft Word (cập nhật mục lục trước).
# Mặc định: báo cáo CSDL. PDF chỉ ghi vào thư mục tạm, không lưu vào dự án.
#   scripts/count-pages.sh [đường-dẫn.docx]
set -e
cd "$(dirname "$0")/.."
SRC="${1:-livrables/report_db/BaoCao_CSDL_Trans2Vec.docx}"
N="$(basename "$SRC" .docx)"
W="$HOME/Library/Containers/com.microsoft.Word/Data"   # thư mục Word luôn có quyền ghi
cp "$SRC" "${W:?}/${N:?}.docx"
# bỏ cờ "cập nhật field khi mở" để hộp thoại không chặn AppleScript
python3 -c "import sys; sys.path.insert(0, 'livrables/survey/draft/docx'); import build_docx; from pathlib import Path; build_docx.strip_update_fields(Path('$W/$N.docx'))"
rm -f "${W:?}/${N:?}.pdf"
osascript <<OSA
with timeout of 300 seconds
tell application "Microsoft Word"
	open POSIX file "$W/$N.docx"
	set t to 0
	repeat while (count of documents) = 0 and t < 30
		delay 1
		set t to t + 1
	end repeat
	set d to active document
	update (table of contents 1 of d)
	save as d file name "$W/$N.pdf" file format format PDF
	close d saving no
end tell
end timeout
OSA
PAGES=$(osascript -l JavaScript -e "ObjC.import('PDFKit'); \$.PDFDocument.alloc.initWithURL(\$.NSURL.fileURLWithPath('$W/$N.pdf')).pageCount")
mkdir -p "${TMPDIR:-/tmp}/count-pages" && mv "${W:?}/${N:?}.pdf" "${TMPDIR:-/tmp}/count-pages/" && rm -f "${W:?}/${N:?}.docx"
find livrables -name __pycache__ -type d -prune -exec rm -r {} +
echo "$SRC: $PAGES trang (PDF ở ${TMPDIR:-/tmp}/count-pages/$N.pdf)"
