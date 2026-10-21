"""E-DB1: tìm kiếm toàn văn — InnoDB FULLTEXT (MariaDB) so với Manticore BM25, cùng cột body_seg (đã tách từ pyvi).

Dựng chỉ mục (đo thời gian, kích thước) rồi chạy 1.000 truy vấn "doc" (50 từ) và 1.000 truy vấn "kw" (3 từ):
  innodb     ALTER TABLE article ADD FULLTEXT (body_seg); MATCH … AGAINST (… IN NATURAL LANGUAGE MODE)
             collation uca1400_vietnamese_as_ci (giữ dấu), innodb_ft_min_token_size=1, không stopword
  manticore  bảng `ft_only` chỉ có body_seg + thuộc tính split, charset giữ dấu; BM25 (k1=1,2, b=0,75)
Thông lượng: ngoài độ trễ tuần tự, đo QPS với 4 luồng (mỗi luồng một kết nối).

Chạy: .venv-exp/bin/python src/system/bench/edb1_fulltext.py
"""
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from common import Protocol, lat_stats, save, table, timed

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "pipeline"))
from config import connect_manticore, connect_mariadb  # noqa: E402
from sync_manticore import VI_CHARSET  # noqa: E402

THREADS = 4
MANTICORE_BM25 = "OPTION ranker=expr('10000*bm25a(1.2,0.75)'), idf='plain,tfidf_unnormalized', max_matches=1000"


def build_innodb(db):
    with db.cursor() as c:
        c.execute("SELECT COUNT(*) FROM information_schema.statistics WHERE table_schema = DATABASE()"
                  " AND table_name = 'article' AND index_name = 'ft_body_seg'")
        if c.fetchone()[0]:
            c.execute("ALTER TABLE article DROP INDEX ft_body_seg")
        t0 = time.time()
        c.execute("ALTER TABLE article ADD FULLTEXT ft_body_seg (body_seg)")
        build_s = time.time() - t0
        c.execute("SELECT SUM(allocated_size) FROM information_schema.innodb_sys_tablespaces"
                  " WHERE name LIKE 'trans2vec/fts\\_%%'")
        size = int(c.fetchone()[0] or 0)
    return {"build_s": build_s, "index_bytes": size}


def build_manticore(db, mc):
    with db.cursor() as c, mc.cursor() as m:
        m.execute("DROP TABLE IF EXISTS ft_only")
        m.execute(f"CREATE TABLE ft_only (body_seg text indexed, split string attribute) charset_table='{VI_CHARSET}'"
                  " min_word_len='1'")
        t0 = time.time()
        c.execute("SELECT id, body_seg, split FROM article ORDER BY id")
        while rows := c.fetchmany(1000):
            m.execute("INSERT INTO ft_only (id, body_seg, split) VALUES " +
                      ",".join(m.mogrify("(%s,%s,%s)", r) for r in rows))
        m.execute("FLUSH RAMCHUNK ft_only")
        m.execute("OPTIMIZE TABLE ft_only OPTION sync=1, cutoff=1")
        build_s = time.time() - t0
        m.execute("SHOW TABLE ft_only STATUS")
        st = dict(m.fetchall())
    return {"build_s": build_s, "index_bytes": int(st["disk_bytes"]), "ram_bytes": int(st["ram_bytes"])}


def innodb_search(c, terms):
    q = " ".join(terms)
    c.execute("SELECT id FROM article WHERE MATCH(body_seg) AGAINST (%s IN NATURAL LANGUAGE MODE) AND split = 'train'"
              " ORDER BY MATCH(body_seg) AGAINST (%s IN NATURAL LANGUAGE MODE) DESC LIMIT 100", (q, q))
    return [r[0] for r in c.fetchall()]


def manticore_search(m, terms):
    expr = "@body_seg (" + " | ".join(terms) + ")"
    m.execute(f"SELECT id FROM ft_only WHERE MATCH(%s) AND split = 'train' LIMIT 100 {MANTICORE_BM25}", (expr,))
    return [r[0] for r in m.fetchall()]


def throughput(connect, fn, queries):
    def worker(chunk):
        con = connect()
        with con.cursor() as c:
            for q in chunk:
                fn(c, q)
        con.close()

    chunks = [queries[i::THREADS] for i in range(THREADS)]
    t0 = time.perf_counter()
    with ThreadPoolExecutor(THREADS) as ex:
        list(ex.map(worker, chunks))
    return len(queries) / (time.perf_counter() - t0)


def main():
    db, mc = connect_mariadb(autocommit=True), connect_manticore()
    P = Protocol(db)
    builds = {"innodb": build_innodb(db), "manticore": build_manticore(db, mc)}
    print("dựng chỉ mục:", builds)
    engines = {"innodb": (connect_mariadb, innodb_search, db), "manticore": (connect_manticore, manticore_search, mc)}
    rows = []
    for kind in ["kw", "doc"]:
        Q = P.queries(kind)
        for name, (connect, fn, con) in engines.items():
            with con.cursor() as c:
                fn(c, Q[0])  # làm nóng
                ranked, lat = timed(lambda q: fn(c, q), Q)
            r = {"engine": name, "query": kind, **P.metrics(ranked), **lat_stats(lat),
                 f"qps_{THREADS}threads": throughput(connect, fn, Q), **builds[name]}
            rows.append(r)
            print(f"{name:<10} {kind:<4} nDCG@10={r['ndcg@10']:.4f} p50={r['p50_ms']:.1f}ms "
                  f"p95={r['p95_ms']:.1f}ms qps{THREADS}={r[f'qps_{THREADS}threads']:.0f}", flush=True)
    with db.cursor() as c:
        c.execute("SELECT @@innodb_ft_min_token_size, @@innodb_ft_enable_stopword, @@version")
        env = c.fetchone()
    save("edb1_fulltext", {"rows": rows, "env": {"innodb_ft_min_token_size": env[0], "innodb_ft_enable_stopword": env[1],
                                                  "mariadb": env[2], "threads": THREADS}})
    table(rows, ["engine", "query", "p@10", "map@100", "ndcg@10", "p50_ms", "p95_ms", f"qps_{THREADS}threads"])


if __name__ == "__main__":
    main()
