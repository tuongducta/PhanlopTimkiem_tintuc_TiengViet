"""A6 (GĐ-H4): dựng lại bảng Manticore từ MariaDB (MariaDB là nguồn gốc; Manticore xóa/nạp lại được bất kỳ lúc nào).

Chạy:
  .venv-exp/bin/python src/system/pipeline/sync_manticore.py                    # bảng `news`, charset giữ dấu
  .venv-exp/bin/python src/system/pipeline/sync_manticore.py --table news_fold --charset non_cjk   # biến thể E-DB5 (a)
Vector lấy từ lần chạy trans2vec-joi mới nhất (hoặc --run).
"""
import argparse
import re
import sys
import time
from pathlib import Path

import numpy as np
from pyvi import ViTokenizer

ROOT = Path(__file__).resolve().parents[3]  # gốc dự án (mã ở src/system/<gói>/)
sys.path.insert(0, str(ROOT / "src/system"))
from config import connect_manticore, connect_mariadb  # noqa: E402
from vi_text import fold  # noqa: E402

DDL = ROOT / "src/system/db/manticore.sql"
WORD = re.compile(r"[^\W\d_]+(?:_[^\W\d_]+)*")  # như experiments/prepare.py
# Giữ nguyên chữ có dấu (chỉ hạ chữ thường) + '_' để giữ token pyvi; đã kiểm tra trong bench/check_setup.py
VI_CHARSET = (
    "0..9, A..Z->a..z, _, a..z, "
    "U+00C0..U+00DE->U+00E0..U+00FE, U+00E0..U+00FF, "
    "U+0102->U+0103, U+0103, U+0110->U+0111, U+0111, U+0128->U+0129, U+0129, "
    "U+0168->U+0169, U+0169, U+01A0->U+01A1, U+01A1, U+01AF->U+01B0, U+01B0, "
    "U+1EA0..U+1EF9/2"
)
BATCH = 500


def segment(text):
    return " ".join(w for w in (t.lower() for t in ViTokenizer.tokenize(text).split()) if WORD.fullmatch(w))


def ddl(table, charset):
    sql = DDL.read_text(encoding="utf-8")
    sql = "\n".join(l for l in sql.splitlines() if not l.lstrip().startswith("--"))
    return sql.replace("{table}", table).replace("{charset_table}", charset).strip().rstrip(";")


def latest_run(c, kind):
    c.execute("SELECT MAX(id) FROM model_run WHERE kind = %s", (kind,))
    return c.fetchone()[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", default="news")
    ap.add_argument("--charset", default="vi", help="'vi' (giữ dấu) hoặc một charset_table của Manticore, vd. non_cjk")
    ap.add_argument("--run", type=int, help="model_run.id của vector (mặc định: trans2vec-joi mới nhất)")
    args = ap.parse_args()
    charset = VI_CHARSET if args.charset == "vi" else args.charset

    t0 = time.time()
    db = connect_mariadb()
    mc = connect_manticore()
    with db.cursor() as c, mc.cursor() as m:
        run = args.run or latest_run(c, "trans2vec-joi")
        m.execute(f"DROP TABLE IF EXISTS {args.table}")
        m.execute(ddl(args.table, charset))
        c.execute("SELECT COUNT(*) FROM article")
        total = c.fetchone()[0]
        c.execute(
            "SELECT a.id, a.title, a.body_seg, a.body_syl, a.category_id, a.split, v.vec"
            " FROM article a JOIN article_vector v ON v.article_id = a.id AND v.run_id = %s ORDER BY a.id", (run,))
        n = 0
        while rows := c.fetchmany(BATCH):
            values = []
            for aid, title, seg, syl, cat, split, vec in rows:
                v = np.frombuffer(vec, dtype="<f4")
                vtxt = "(" + ",".join(f"{x:.6g}" for x in v) + ")"
                values.append(m.mogrify("(%s,%s,%s,%s,%s,%s,%s,%s,%s,", (aid, title, segment(title), seg, syl,
                                                                     fold(title), fold(syl), cat, split)) + vtxt + ")")
            m.execute("REPLACE INTO " + args.table + " (id, title, title_seg, body_seg, body_syl, title_fold, body_fold,"
                      " category_id, split, vec) VALUES " + ",".join(values))
            n += len(rows)
            if n % 10000 < BATCH:
                print(f"  {n}/{total} ({time.time() - t0:.0f}s)", flush=True)
        m.execute(f"FLUSH RAMCHUNK {args.table}")
        m.execute(f"SELECT COUNT(*) FROM {args.table}")
        cnt = m.fetchone()[0]
        m.execute(f"SHOW TABLE {args.table} STATUS")
        status = dict(m.fetchall())
    db.close()
    mc.close()
    print(f"XONG: {args.table} ({args.charset}), vector run {run}: {cnt}/{total} tài liệu, "
          f"disk_bytes={status.get('disk_bytes')}, ram_bytes={status.get('ram_bytes')}, {time.time() - t0:.0f}s")
    if cnt != total:
        sys.exit("Số tài liệu Manticore khác MariaDB")


if __name__ == "__main__":
    main()
