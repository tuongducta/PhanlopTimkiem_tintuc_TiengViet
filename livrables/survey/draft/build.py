#!/usr/bin/env python3
"""Ghép các chương trong survey/draft/ thành một file survey hoàn chỉnh.

- Trích dẫn trong bản nháp viết dạng [@key] hoặc [@key1; @key2].
- Số thứ tự được gán theo lần xuất hiện đầu tiên (chuẩn IEEE).
- Danh mục tham khảo lấy từ refs.tsv, chỉ gồm tài liệu được trích dẫn.

Chạy:  python3 livrables/survey/draft/build.py
"""
import re
import sys
from pathlib import Path

DRAFT = Path(__file__).resolve().parent
OUT = DRAFT.parent / "Survey_Trans2Vec_VN_News.md"
CITE = re.compile(r"\[(@[\w-]+(?:\s*;\s*@[\w-]+)*)\]")


def load_refs():
    refs = {}
    for line in (DRAFT / "refs.tsv").read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        key, text = line.split("\t", 1)
        refs[key.strip()] = text.strip()
    return refs


def main():
    refs = load_refs()
    chapters = sorted(p for p in DRAFT.glob("[0-9][0-9]_*.md"))
    body = "\n\n".join(p.read_text(encoding="utf-8").rstrip() for p in chapters)

    order, missing = {}, set()

    def number(match):
        keys = [k.strip().lstrip("@") for k in match.group(1).split(";")]
        nums = []
        for k in keys:
            if k not in refs:
                missing.add(k)
                continue
            order.setdefault(k, len(order) + 1)
            nums.append(order[k])
        return "[" + ", ".join(str(n) for n in sorted(set(nums))) + "]"

    body = CITE.sub(number, body)
    if missing:
        sys.exit(f"Khóa trích dẫn không có trong refs.tsv: {sorted(missing)}")

    ref_lines = [f"[{n}] {refs[k]}" for k, n in sorted(order.items(), key=lambda kv: kv[1])]
    out = body + "\n\n## Tài liệu tham khảo\n\n" + "\n\n".join(ref_lines) + "\n"
    OUT.write_text(out, encoding="utf-8")

    unused = sorted(set(refs) - set(order))
    print(f"Đã ghi {OUT.name}: {len(chapters)} phần, {len(order)} tài liệu, {len(out.split())} từ.")
    if unused:
        print(f"Tài liệu trong refs.tsv chưa được trích dẫn: {unused}")


if __name__ == "__main__":
    main()
