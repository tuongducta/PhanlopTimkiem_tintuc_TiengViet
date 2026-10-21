"""GĐ-H1: kiểm tra kết nối và cú pháp trên bản cài thật (MariaDB 11.8 Vector, Manticore KNN, charset tiếng Việt).

Chạy: .venv-exp/bin/python src/system/bench/check_setup.py
Chỉ tạo bảng tạm có tiền tố _chk_ và xóa sau khi kiểm tra.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import connect_manticore, connect_mariadb  # noqa: E402

# Giữ nguyên chữ có dấu (chỉ hạ chữ thường) + '_' để giữ token pyvi như giá_vàng.
# U+1EA0..U+1EF9/2: khối Latin mở rộng tiếng Việt, hoa/thường xen kẽ.
VI_CHARSET = (
    "0..9, A..Z->a..z, _, a..z, "
    "U+00C0..U+00DE->U+00E0..U+00FE, U+00E0..U+00FF, "
    "U+0102->U+0103, U+0103, U+0110->U+0111, U+0111, U+0128->U+0129, U+0129, "
    "U+0168->U+0169, U+0169, U+01A0->U+01A1, U+01A1, U+01AF->U+01B0, U+01B0, "
    "U+1EA0..U+1EF9/2"
)

VECS = {1: [1, 0, 0, 0], 2: [0.9, 0.1, 0, 0], 3: [0, 1, 0, 0], 4: [0, 0, 1, 0]}
QUERY = [1, 0.05, 0, 0]


def check_mariadb():
    print("== MariaDB")
    con = connect_mariadb(autocommit=True)
    with con.cursor() as c:
        c.execute("SELECT VERSION()")
        print("version:", c.fetchone()[0])
        c.execute("DROP TABLE IF EXISTS _chk_vec")
        c.execute(
            "CREATE TABLE _chk_vec (id INT PRIMARY KEY, v VECTOR(4) NOT NULL,"
            " VECTOR INDEX (v) M=8 DISTANCE=cosine) ENGINE=InnoDB"
        )
        c.executemany(
            "INSERT INTO _chk_vec VALUES (%s, VEC_FromText(%s))",
            [(i, str(v)) for i, v in VECS.items()],
        )
        q = ("SELECT id, VEC_DISTANCE_COSINE(v, VEC_FromText(%s)) d FROM _chk_vec"
             " ORDER BY d LIMIT 2")
        c.execute(q, (str(QUERY),))
        print("knn top-2:", c.fetchall())
        c.execute("EXPLAIN " + q, (str(QUERY),))
        plan = c.fetchall()
        print("explain:", plan)
        print("dùng VECTOR INDEX:", any("v" == (r[5] or "") or "v" == (r[6] or "") for r in plan))
        c.execute("DROP TABLE _chk_vec")

        c.execute("DROP TABLE IF EXISTS _chk_ft")
        c.execute("CREATE TABLE _chk_ft (id INT PRIMARY KEY, body TEXT, FULLTEXT (body)) ENGINE=InnoDB")
        c.executemany("INSERT INTO _chk_ft VALUES (%s,%s)",
                      [(1, "giá_vàng tăng mạnh"), (2, "bán bàn ghế"), (3, "bạn bè")])
        for w in ("giá_vàng", "bàn"):
            c.execute("SELECT id FROM _chk_ft WHERE MATCH(body) AGAINST (%s IN BOOLEAN MODE)", (w,))
            print(f"InnoDB FULLTEXT '{w}':", [r[0] for r in c.fetchall()])
        c.execute("DROP TABLE _chk_ft")
    con.close()


def check_manticore():
    print("== Manticore")
    con = connect_manticore()
    with con.cursor() as c:
        c.execute("SHOW STATUS LIKE 'version'")
        print("version:", c.fetchone()[1])
        docs = [(1, "bàn ghế gỗ"), (2, "bán nhà giá rẻ"), (3, "bạn bè"), (4, "giá_vàng tăng")]
        for name, charset in (("_chk_default", None), ("_chk_vi", VI_CHARSET)):
            c.execute(f"DROP TABLE IF EXISTS {name}")
            opt = f" charset_table='{charset}'" if charset else ""
            c.execute(
                f"CREATE TABLE {name} (title text, category_id uint,"
                " vec float_vector knn_type='hnsw' knn_dims='4' hnsw_similarity='COSINE')" + opt
            )
            for i, t in docs:
                vec = "(" + ",".join(map(str, VECS[i])) + ")"
                c.execute(f"INSERT INTO {name} (id, title, category_id, vec) VALUES (%s,%s,%s,{vec})",
                          (i, t, i % 2))
            print(f"[{name}]")
            for w in ("bàn", "ban", "giá_vàng", "vàng"):
                c.execute(f"SELECT id FROM {name} WHERE MATCH(%s)", (w,))
                print(f"  MATCH '{w}':", [r[0] for r in c.fetchall()])
            c.execute(f"CALL KEYWORDS(%s, '{name}')", ("Bàn BÁN Đường ƯỚC giá_vàng",))
            print("  keywords:", [r[2] for r in c.fetchall()])
        qv = "(" + ",".join(map(str, QUERY)) + ")"
        c.execute(f"SELECT id, knn_dist() FROM _chk_vi WHERE knn(vec, 2, {qv})")
        print("knn top-2:", c.fetchall())
        c.execute(f"SELECT id, knn_dist() FROM _chk_vi WHERE knn(vec, 3, {qv}) AND category_id=1")
        print("knn + lọc category_id=1:", c.fetchall())
        c.execute("SELECT id, WEIGHT() FROM _chk_vi WHERE MATCH('giá') OPTION ranker=bm25")
        print("bm25:", c.fetchall())
        for name in ("_chk_default", "_chk_vi"):
            c.execute(f"DROP TABLE {name}")
    con.close()


if __name__ == "__main__":
    check_mariadb()
    check_manticore()
    print("OK")
