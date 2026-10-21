#!/bin/zsh
# Mở survey .docx bằng Microsoft Word: cập nhật mục lục (số trang), lưu lại, và xuất PDF.
# File được xử lý trong thư mục sandbox của Word (Word luôn có quyền ở đó, không hỏi quyền truy cập),
# sau đó chép .docx đã cập nhật và .pdf về thư mục survey/.
#
# Chạy sau build_docx.py:   zsh livrables/survey/draft/docx/export_pdf.sh
set -e
SURVEY="$(cd "$(dirname "$0")/../.." && pwd)"
NAME="Survey_Trans2Vec_VN_News"
W="$HOME/Library/Containers/com.microsoft.Word/Data"

cp "$SURVEY/$NAME.docx" "$W/$NAME.docx"
# Bỏ dấu "cập nhật field khi mở" trên bản sao, tránh hộp thoại chặn AppleScript
python3 -c "import sys; sys.path.insert(0, '$(dirname "$0")'); import build_docx; from pathlib import Path; build_docx.strip_update_fields(Path('$W/$NAME.docx'))"
rm -f "$W/$NAME.pdf"

osascript <<EOF
with timeout of 180 seconds
tell application "Microsoft Word"
	open POSIX file "$W/$NAME.docx"
	set t to 0
	repeat while (count of documents) = 0 and t < 30
		delay 1
		set t to t + 1
	end repeat
	if (count of documents) = 0 then error "Word không mở được tài liệu (kiểm tra hộp thoại đang mở trong Word)"
	set d to active document
	update (table of contents 1 of d)
	save d
	save as d file name "$W/$NAME.pdf" file format format PDF
	close d saving no
end tell
end timeout
EOF

cp "$W/$NAME.docx" "$SURVEY/$NAME.docx"
cp "$W/$NAME.pdf" "$SURVEY/$NAME.pdf"
echo "Đã cập nhật mục lục và xuất: survey/$NAME.docx, survey/$NAME.pdf"
