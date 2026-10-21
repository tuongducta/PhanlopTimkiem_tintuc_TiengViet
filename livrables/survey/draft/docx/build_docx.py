#!/usr/bin/env python3
"""Xuất survey ra Word (.docx) bằng pandoc.

1. Dựng reference.docx (mẫu định dạng) từ mẫu mặc định của pandoc:
   Times New Roman 13pt, A4, lề trái 3 cm / còn lại 2 cm, số trang ở chân trang,
   bảng có viền + hàng tiêu đề tô nền, mỗi chương (Heading 1) sang trang mới.
2. Tách tiêu đề / tóm tắt của bản Markdown thành metadata, bỏ mục lục viết tay
   (thay bằng mục lục tự động của Word), hạ cấp heading (## → Heading 1).
3. Gọi pandoc → survey/Survey_Trans2Vec_VN_News.docx

Chạy (sau khi đã chạy build.py):  python3 livrables/survey/draft/docx/build_docx.py
"""
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SURVEY = HERE.parent.parent
SRC_MD = SURVEY / "Survey_Trans2Vec_VN_News.md"
OUT = SURVEY / "Survey_Trans2Vec_VN_News.docx"
REF = HERE / "reference.docx"

FONT = "Times New Roman"
TNR = f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:eastAsia="{FONT}" w:cs="{FONT}" />'
HEAD_COLOR = "1F3864"


def style_block(xml, sid):
    m = re.search(r'<w:style [^>]*w:styleId="%s">.*?</w:style>' % sid, xml, re.S)
    if not m:
        raise SystemExit(f"Không tìm thấy style {sid}")
    return m


def patch_style(xml, sid, fn):
    m = style_block(xml, sid)
    return xml[: m.start()] + fn(m.group(0)) + xml[m.end():]


def set_rpr(block, size=None, bold=False, color=None, font=TNR):
    """Thay toàn bộ <w:rPr> của style bằng phiên bản mới."""
    parts = [font] if font else []
    if bold:
        parts.append("<w:b /><w:bCs />")
    if color:
        parts.append(f'<w:color w:val="{color}" />')
    if size:
        parts.append(f'<w:sz w:val="{size}" /><w:szCs w:val="{size}" />')
    rpr = "<w:rPr>" + "".join(parts) + "</w:rPr>"
    block = re.sub(r"<w:rPr>.*?</w:rPr>", "", block, flags=re.S)
    return block.replace("</w:style>", rpr + "</w:style>")


def set_ppr(block, inner):
    block = re.sub(r"<w:pPr>.*?</w:pPr>", "", block, flags=re.S)
    # pPr phải đứng trước rPr trong style
    if "<w:rPr>" in block:
        return block.replace("<w:rPr>", f"<w:pPr>{inner}</w:pPr><w:rPr>", 1)
    return block.replace("</w:style>", f"<w:pPr>{inner}</w:pPr></w:style>")


def make_reference():
    tmp = Path(tempfile.mkdtemp())
    default = tmp / "default.docx"
    with open(default, "wb") as f:
        subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"], stdout=f, check=True)
    with zipfile.ZipFile(default) as z:
        files = {n: z.read(n) for n in z.namelist()}

    s = files["word/styles.xml"].decode("utf-8")
    # Phông và cỡ chữ mặc định
    s = re.sub(r"(<w:rPrDefault>\s*<w:rPr>)\s*<w:rFonts[^>]*/>", r"\1" + TNR, s, flags=re.S)
    s = re.sub(r'(<w:rPrDefault>.*?)<w:sz w:val="24" />\s*<w:szCs w:val="24" />',
               r'\1<w:sz w:val="26" /><w:szCs w:val="26" />', s, flags=re.S)
    s = s.replace('w:val="en-US" w:eastAsia="zh-CN"', 'w:val="vi-VN" w:eastAsia="vi-VN"')

    # Đoạn văn: căn đều, giãn dòng 1,3
    s = patch_style(s, "BodyText", lambda b: set_ppr(
        b, '<w:spacing w:before="0" w:after="120" w:line="312" w:lineRule="auto" /><w:jc w:val="both" />'))
    s = patch_style(s, "Compact", lambda b: set_ppr(
        b, '<w:spacing w:before="20" w:after="20" w:line="264" w:lineRule="auto" />'))

    # Tiêu đề
    s = patch_style(s, "Title", lambda b: set_rpr(b, 34, True, HEAD_COLOR))
    s = patch_style(s, "Subtitle", lambda b: set_rpr(b, 26, False, "404040"))
    s = patch_style(s, "Heading1", lambda b: set_rpr(set_ppr(
        b, '<w:keepNext /><w:keepLines /><w:pageBreakBefore />'
           '<w:spacing w:before="0" w:after="240" /><w:outlineLvl w:val="0" />'), 32, True, HEAD_COLOR))
    s = patch_style(s, "Heading2", lambda b: set_rpr(set_ppr(
        b, '<w:keepNext /><w:keepLines /><w:spacing w:before="240" w:after="120" />'
           '<w:outlineLvl w:val="1" />'), 28, True, HEAD_COLOR))
    s = patch_style(s, "Heading3", lambda b: set_rpr(set_ppr(
        b, '<w:keepNext /><w:keepLines /><w:spacing w:before="200" w:after="80" />'
           '<w:outlineLvl w:val="2" />'), 26, True, HEAD_COLOR))
    s = patch_style(s, "TOCHeading", lambda b: set_rpr(b, 32, True, HEAD_COLOR))
    s = patch_style(s, "AbstractTitle", lambda b: set_rpr(b, 28, True, HEAD_COLOR))
    s = patch_style(s, "Abstract", lambda b: set_ppr(
        b, '<w:spacing w:before="0" w:after="120" w:line="312" w:lineRule="auto" /><w:jc w:val="both" />'))

    # Mã / sơ đồ ASCII: Consolas 8pt
    consolas = '<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas" />'
    s = patch_style(s, "VerbatimChar", lambda b: set_rpr(b, 16, False, None, consolas))
    s = s.replace("</w:styles>",
        '<w:style w:type="paragraph" w:customStyle="1" w:styleId="SourceCode">'
        '<w:name w:val="Source Code" /><w:basedOn w:val="Normal" /><w:link w:val="VerbatimChar" />'
        '<w:pPr><w:wordWrap w:val="off" /><w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto" />'
        '<w:shd w:val="clear" w:color="auto" w:fill="F5F5F5" /></w:pPr>'
        f'<w:rPr>{consolas}<w:sz w:val="16" /><w:szCs w:val="16" /></w:rPr></w:style></w:styles>')

    # Bảng: viền mảnh, hàng đầu tô nền, chữ 11pt
    border = '<w:{0} w:val="single" w:sz="4" w:space="0" w:color="8C8C8C" />'
    borders = "".join(border.format(e) for e in ["top", "left", "bottom", "right", "insideH", "insideV"])
    s = patch_style(s, "Table", lambda b: (
        b.replace('<w:tblInd w:w="0" w:type="dxa" />',
                  f'<w:tblInd w:w="0" w:type="dxa" /><w:tblBorders>{borders}</w:tblBorders>')
         .replace('<w:top w:w="0" w:type="dxa" />', '<w:top w:w="30" w:type="dxa" />')
         .replace('<w:bottom w:w="0" w:type="dxa" />', '<w:bottom w:w="30" w:type="dxa" />')
         .replace('</w:tblPr>', '</w:tblPr><w:rPr><w:sz w:val="22" /><w:szCs w:val="22" /></w:rPr>')
         .replace('<w:tblStylePr w:type="firstRow">',
                  '<w:tblStylePr w:type="firstRow"><w:rPr><w:b /><w:bCs /></w:rPr>')
         .replace('<w:vAlign w:val="bottom"/>',
                  '<w:shd w:val="clear" w:color="auto" w:fill="D9E2F3" /><w:vAlign w:val="bottom"/>')))
    files["word/styles.xml"] = s.encode("utf-8")

    # Khổ giấy A4, lề, chân trang có số trang
    d = files["word/document.xml"].decode("utf-8")
    if "xmlns:r=" not in d:
        d = d.replace("<w:document ", '<w:document xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" ', 1)
    d = re.sub(r"<w:sectPr>.*?</w:sectPr>",
               '<w:sectPr><w:footerReference w:type="default" r:id="rIdFooter1" />'
               '<w:footnotePr><w:numRestart w:val="eachSect" /></w:footnotePr>'
               '<w:pgSz w:w="11906" w:h="16838" />'
               '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1701" '
               'w:header="567" w:footer="567" w:gutter="0" /></w:sectPr>', d, flags=re.S)
    files["word/document.xml"] = d.encode("utf-8")
    files["word/footer1.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:p><w:pPr><w:jc w:val="center" /></w:pPr>'
        '<w:r><w:fldChar w:fldCharType="begin" /></w:r>'
        '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate" /></w:r><w:r><w:t>1</w:t></w:r>'
        '<w:r><w:fldChar w:fldCharType="end" /></w:r></w:p></w:ftr>').encode("utf-8")
    rels = files["word/_rels/document.xml.rels"].decode("utf-8")
    rels = rels.replace("</Relationships>",
        '<Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" '
        'Id="rIdFooter1" Target="footer1.xml" /></Relationships>')
    files["word/_rels/document.xml.rels"] = rels.encode("utf-8")
    ct = files["[Content_Types].xml"].decode("utf-8")
    ct = ct.replace("</Types>",
        '<Override PartName="/word/footer1.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml" /></Types>')
    files["[Content_Types].xml"] = ct.encode("utf-8")

    with zipfile.ZipFile(REF, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    shutil.rmtree(tmp)


def size_table_columns(text):
    """Đặt độ rộng tương đối cho cột của mỗi bảng pipe theo độ dài nội dung.

    Pandoc chia cột theo tỉ lệ số dấu '-' ở dòng phân cách (khi bảng rộng),
    nên ta viết lại dòng đó: cột chữ dài được nhiều '-' hơn, có chặn trên/dưới.
    """
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|(\s*:?-+:?\s*\|)+\s*$", lines[i + 1]):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            rows = [r.strip().strip("|").split("|") for k, r in enumerate(lines[i:j]) if k != 1]
            ncol = len(rows[0])
            weights = []
            for c in range(ncol):
                cells = [re.sub(r"[*$\\]", "", r[c]).strip() for r in rows if c < len(r)]
                longest = max((len(x) for x in cells), default=1)
                avg = sum(len(x) for x in cells) / max(len(cells), 1)
                longest_word = max((len(w) for x in cells for w in x.split()), default=1)
                weights.append(max(6, round(1.5 * longest_word) + 2, min(45, round(0.5 * longest + 0.5 * avg))))
            out.append(lines[i])
            out.append("|" + "|".join("-" * w for w in weights) + "|")
            out.extend(lines[i + 2:j])
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out)


def make_markdown():
    text = SRC_MD.read_text(encoding="utf-8")
    title = re.search(r"^# (.+)$", text, re.M).group(1).strip()
    subtitle = re.search(r"^\*(Bài khảo sát.+)\*$", text, re.M).group(1).strip()
    abstract = re.search(r"^## Tóm tắt\s*\n(.*?)\n---", text, re.S | re.M).group(1).strip()
    body = text[re.search(r"^## 1\. ", text, re.M).start():]

    def yaml_str(v):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'

    body = size_table_columns(body)
    abstract_yaml = "\n".join("  " + line if line else "" for line in abstract.splitlines())
    meta = (
        "---\n"
        f"title: {yaml_str(title)}\n"
        f"subtitle: {yaml_str(subtitle)}\n"
        "lang: vi-VN\n"
        'toc-title: "Mục lục"\n'
        'abstract-title: "Tóm tắt"\n'
        f"abstract: |\n{abstract_yaml}\n"
        "---\n\n"
    )
    return meta + body


def strip_update_fields(path):
    """Bỏ các dấu buộc Word cập nhật field khi mở (w:dirty trên field mục lục, updateFields).

    Cờ này khiến Word hỏi "update the fields?" khi mở file. Mở tay thì nên giữ (bấm Yes
    để mục lục có số trang), nhưng hộp thoại chặn thao tác tự động bằng AppleScript,
    nên chỉ export_pdf.sh gọi hàm này trên bản sao nó xử lý.
    """
    with zipfile.ZipFile(path) as z:
        files = {n: z.read(n) for n in z.namelist()}
    s = files["word/settings.xml"].decode("utf-8")
    files["word/settings.xml"] = re.sub(r"<w:updateFields[^>]*/>", "", s).encode("utf-8")
    # pandoc đánh dấu field mục lục là "dirty" — chính dấu này làm Word hỏi khi mở
    d = files["word/document.xml"].decode("utf-8")
    files["word/document.xml"] = d.replace(' w:dirty="true"', "").encode("utf-8")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)


def main():
    make_reference()
    md = HERE / "_survey_for_docx.md"
    md.write_text(make_markdown(), encoding="utf-8")
    subprocess.run([
        "pandoc", str(md),
        "-f", "markdown-subscript-superscript-fancy_lists+lists_without_preceding_blankline",
        "-o", str(OUT),
        "--reference-doc", str(REF),
        "--shift-heading-level-by=-1",
        "--toc", "--toc-depth=2",
        "--resource-path", str(SURVEY),  # ảnh trong survey/figures/
    ], check=True)
    md.unlink()
    print(f"Đã ghi {OUT.relative_to(SURVEY.parent)} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
