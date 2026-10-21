"""GĐ-H2: kiểm tra dữ liệu đã nạp — số dòng, toàn vẹn, kích thước bảng, kế hoạch truy vấn đếm support.

Chạy: .venv-exp/bin/python src/system/bench/check_load.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import connect_mariadb  # noqa: E402

CHECKS = [
    ("số bài theo tập", "SELECT split, COUNT(*) FROM article GROUP BY split"),
    ("item / item dùng được / từ dừng",
     "SELECT COUNT(*), SUM(idf IS NOT NULL), SUM(is_stop) FROM item"),
    ("dòng transaction / bài có transaction / TB item mỗi bài",
     "SELECT COUNT(*), COUNT(DISTINCT article_id), ROUND(COUNT(*) / COUNT(DISTINCT article_id), 2) FROM article_item"),
    ("bài có ít hơn 50 item", "SELECT COUNT(*) FROM (SELECT article_id FROM article_item GROUP BY article_id HAVING COUNT(*) < 50) t"),
    ("transaction chứa từ dừng (phải = 0)",
     "SELECT COUNT(*) FROM article_item ai JOIN item i ON i.id = ai.item_id WHERE i.idf IS NULL"),
    ("tiêu đề rỗng", "SELECT COUNT(*) FROM article WHERE title = ''"),
    ("giữ dấu ở kết nối: 'bàn' = 'bán'? (phải = 0)", "SELECT 'bàn' = 'bán'"),
    ("giữ dấu ở cột: item 'bàn' khớp được token nào (phải chỉ 'bàn')",
     "SELECT token FROM item WHERE token COLLATE utf8mb4_uca1400_vietnamese_as_ci = 'bàn'"),
    ("collation cột body_seg",
     "SELECT collation_name FROM information_schema.columns WHERE table_schema = DATABASE()"
     " AND table_name = 'article' AND column_name = 'body_seg'"),
]

SUPPORT_SQL = """
SELECT i.token, COUNT(*) AS support
FROM article_item ai JOIN item i ON i.id = ai.item_id
JOIN article a ON a.id = ai.article_id AND a.split = 'train'
GROUP BY ai.item_id ORDER BY support DESC LIMIT 10"""


def main():
    con = connect_mariadb()
    with con.cursor() as c:
        for name, sql in CHECKS:
            c.execute(sql)
            print(f"{name}: {c.fetchall()}")
        c.execute("SELECT * FROM v_corpus_stats ORDER BY code, split")
        print("v_corpus_stats:")
        for r in c.fetchall():
            print("  ", r)
        c.execute(
            "SELECT table_name, table_rows, ROUND(data_length/1048576), ROUND(index_length/1048576)"
            " FROM information_schema.tables WHERE table_schema = DATABASE()"
            " AND table_name IN ('article','item','article_item') ORDER BY table_name")
        print("kích thước (bảng, dòng ước lượng, data MB, index MB):", c.fetchall())
        t0 = time.time()
        c.execute(SUPPORT_SQL)
        print(f"top-10 item theo support train ({time.time() - t0:.2f}s):", c.fetchall())
        c.execute("EXPLAIN " + SUPPORT_SQL)
        print("EXPLAIN:")
        for r in c.fetchall():
            print("  ", r)
    con.close()


if __name__ == "__main__":
    main()
