#!/usr/bin/env python3
"""Ghép báo cáo môn Hệ CSDL nâng cao từ report_db/draft/ thành .md rồi xuất .docx.

- Trích dẫn viết dạng [@key] hoặc [@key1; @key2]; số thứ tự theo lần xuất hiện đầu tiên (IEEE);
  danh mục lấy từ draft/refs.tsv, chỉ gồm tài liệu được trích dẫn (như survey/draft/build.py).
- Định dạng Word dùng lại mẫu của survey (survey/draft/docx/build_docx.py): Times New Roman 13, A4,
  lề trái 3 cm, Heading 1 sang trang mới. Không sửa gì trong survey/.

Chạy (từ thư mục gốc dự án):  python3 livrables/report_db/build.py
Hình: chạy trước  .venv-exp/bin/python livrables/report_db/make_figures.py
"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DRAFT = HERE / "draft"
OUT_MD = HERE / "BaoCao_CSDL_Trans2Vec.md"
OUT_DOCX = HERE / "BaoCao_CSDL_Trans2Vec.docx"
REF_DOCX = HERE / "reference.docx"
CITE = re.compile(r"\[(@[\w-]+(?:\s*;\s*@[\w-]+)*)\]")

spec = importlib.util.spec_from_file_location("survey_docx", HERE.parent / "survey/draft/docx/build_docx.py")
survey_docx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(survey_docx)


def load_refs():
    refs = {}
    for line in (DRAFT / "refs.tsv").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            key, text = line.split("\t", 1)
            refs[key.strip()] = text.strip()
    return refs


def build_md():
    refs = load_refs()
    chapters = sorted(DRAFT.glob("[0-9][0-9]_*.md"))
    body = "\n\n".join(p.read_text(encoding="utf-8").rstrip() for p in chapters)
    order, missing = {}, set()

    def number(m):
        nums = []
        for k in (k.strip().lstrip("@") for k in m.group(1).split(";")):
            if k not in refs:
                missing.add(k)
                continue
            nums.append(order.setdefault(k, len(order) + 1))
        return "[" + ", ".join(str(n) for n in sorted(set(nums))) + "]"

    body = CITE.sub(number, body)
    if missing:
        sys.exit(f"Khóa trích dẫn không có trong refs.tsv: {sorted(missing)}")
    ref_lines = [f"[{n}] {refs[k]}" for k, n in sorted(order.items(), key=lambda kv: kv[1])]
    out = body + "\n\n## Tài liệu tham khảo\n\n" + "\n\n".join(ref_lines) + "\n"
    OUT_MD.write_text(out, encoding="utf-8")
    unused = sorted(set(refs) - set(order))
    print(f"Đã ghi {OUT_MD.name}: {len(chapters)} phần, {len(order)} tài liệu, {len(out.split())} từ.")
    if unused:
        print(f"Tài liệu trong refs.tsv chưa được trích dẫn: {unused}")
    return out


def docx_markdown(text):
    """Tiêu đề, dòng phụ, tóm tắt → metadata; bỏ mục lục viết tay (Word tự sinh); từ chương 1 trở đi là thân bài."""
    title = re.search(r"^# (.+)$", text, re.M).group(1).strip()
    subtitle = re.search(r"^\*(Báo cáo.+)\*$", text, re.M).group(1).strip()
    abstract = re.search(r"^## Tóm tắt\s*\n(.*?)\n---", text, re.S | re.M).group(1).strip()
    body = survey_docx.size_table_columns(text[re.search(r"^## 1\. ", text, re.M).start():])

    def q(v):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"') + '"'

    abstract_yaml = "\n".join("  " + l if l else "" for l in abstract.splitlines())
    return ("---\n" f"title: {q(title)}\n" f"subtitle: {q(subtitle)}\n" "lang: vi-VN\n"
            'toc-title: "Mục lục"\n' 'abstract-title: "Tóm tắt"\n' f"abstract: |\n{abstract_yaml}\n" "---\n\n" + body)


def build_docx(text):
    survey_docx.REF = REF_DOCX  # mẫu định dạng dựng lại vào report_db/, không ghi đè mẫu của survey
    survey_docx.make_reference()
    md = HERE / "_report_for_docx.md"
    md.write_text(docx_markdown(text), encoding="utf-8")
    subprocess.run([
        "pandoc", str(md),
        "-f", "markdown-subscript-superscript-fancy_lists+lists_without_preceding_blankline",
        "-o", str(OUT_DOCX), "--reference-doc", str(REF_DOCX),
        "--shift-heading-level-by=-1", "--toc", "--toc-depth=1",
        "--resource-path", str(HERE),  # ảnh trong report_db/figures/
    ], check=True)
    md.unlink()
    print(f"Đã ghi {OUT_DOCX.name} ({OUT_DOCX.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build_docx(build_md())
