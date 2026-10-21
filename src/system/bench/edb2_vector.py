"""E-DB2: tìm kiếm vector — MariaDB VECTOR INDEX (MHNSW) so với Manticore HNSW, đối chiếu tìm vét cạn.

Kho: 33.759 vector Trans2Vec-JOI của bài train (article_vector, L2-chuẩn hóa, 128 chiều).
Truy vấn: 1.000 vector bài test của giao thức GĐ6. Chân lý: top-k cosine chính xác (numpy).
  mariadb-M{m}    bảng vec_m{m}: VECTOR INDEX … M=m DISTANCE=cosine; quét @@mhnsw_ef_search
  manticore-M{m}  bảng vec_m{m}: float_vector HNSW hnsw_m=m, ef_construction=200; quét {ef=…}
  mariadb-scan    cùng dữ liệu, KHÔNG có chỉ mục (quét toàn bảng), 100 truy vấn
Độ đo: recall@10 so với vét cạn, nDCG@10 (LIMIT 10); MAP@100 ở LIMIT 100; độ trễ; thời gian dựng; dung lượng.

Chạy: .venv-exp/bin/python src/system/bench/edb2_vector.py
"""
import time

import numpy as np

from common import Protocol, lat_stats, save, table, timed
from config import connect_manticore, connect_mariadb

MS = [6, 16]
EFS = [10, 20, 40, 100, 200]


def load_vectors(c, run, ids):
    c.execute("SELECT article_id, vec FROM article_vector WHERE run_id = %s AND article_id IN (" +
              ",".join(map(str, ids)) + ")", (run,))
    d = {a: np.frombuffer(b, dtype="<f4") for a, b in c.fetchall()}
    return np.vstack([d[i] for i in ids])


def mariadb_build(c, name, m, run, index=True):
    c.execute(f"DROP TABLE IF EXISTS {name}")
    idx = f", VECTOR INDEX (v) M={m} DISTANCE=cosine" if index else ""
    c.execute(f"CREATE TABLE {name} (id INT UNSIGNED PRIMARY KEY, v VECTOR(128) NOT NULL{idx}) ENGINE=InnoDB")
    t0 = time.time()
    c.execute(f"INSERT INTO {name} SELECT v.article_id, v.vec FROM article_vector v JOIN article a ON a.id = v.article_id"
              " WHERE v.run_id = %s AND a.split = 'train' ORDER BY v.article_id", (run,))
    build_s = time.time() - t0
    c.execute("SELECT SUM(allocated_size) FROM information_schema.innodb_sys_tablespaces WHERE name LIKE %s",
              (f"trans2vec/{name}%",))
    return {"build_s": build_s, "index_bytes": int(c.fetchone()[0] or 0)}


def manticore_build(m, name, M, ids, Z):
    m.execute(f"DROP TABLE IF EXISTS {name}")
    m.execute(f"CREATE TABLE {name} (vec float_vector knn_type='hnsw' knn_dims='128' hnsw_similarity='COSINE'"
              f" hnsw_m='{M}' hnsw_ef_construction='200')")
    t0 = time.time()
    for i in range(0, len(ids), 500):
        m.execute(f"INSERT INTO {name} (id, vec) VALUES " + ",".join(
            f"({a},(" + ",".join(f"{x:.6g}" for x in z) + "))" for a, z in zip(ids[i:i + 500], Z[i:i + 500])))
    m.execute(f"FLUSH RAMCHUNK {name}")
    m.execute(f"OPTIMIZE TABLE {name} OPTION sync=1, cutoff=1")
    build_s = time.time() - t0
    m.execute(f"SHOW TABLE {name} STATUS")
    st = dict(m.fetchall())
    return {"build_s": build_s, "index_bytes": int(st["disk_bytes"]), "ram_bytes": int(st["ram_bytes"])}


def main():
    db, mc = connect_mariadb(autocommit=True), connect_manticore()
    P = Protocol(db)
    c, m = db.cursor(), mc.cursor()
    c.execute("SELECT MAX(id) FROM model_run WHERE kind = 'trans2vec-joi'")
    run = c.fetchone()[0]
    tr = np.array(P.train_ids)
    Ztr, Zq = load_vectors(c, run, P.train_ids), load_vectors(c, run, P.qids)
    t0 = time.perf_counter()
    S = Zq @ Ztr.T
    exact = tr[np.argsort(-S, axis=1)[:, :100]]
    numpy_ms = (time.perf_counter() - t0) * 1000 / len(Zq)
    truth10 = [set(e[:10]) for e in exact]
    rows = [{"engine": "numpy-exact", "M": "", "ef": "", **P.metrics(exact), "recall@10": 1.0,
             "map@100_at100": P.metrics(exact)["map@100"], "mean_ms": numpy_ms}]
    print(f"numpy vét cạn: nDCG@10={rows[0]['ndcg@10']:.4f}, {numpy_ms:.2f} ms/truy vấn (ma trận)", flush=True)

    def run_cfg(engine, M, ef, fn10, fn100, build):
        res10, lat = timed(fn10, list(Zq))
        res100, _ = timed(fn100, list(Zq))
        r = {"engine": engine, "M": M, "ef": ef, **P.metrics(res10),
             "recall@10": float(np.mean([len(t & set(x)) / 10 for t, x in zip(truth10, res10)])),
             "map@100_at100": P.metrics(res100)["map@100"], **lat_stats(lat), **build}
        rows.append(r)
        print(f"{engine:<14} M={M:<3} ef={ef:<4} recall@10={r['recall@10']:.4f} nDCG@10={r['ndcg@10']:.4f} "
              f"p50={r['p50_ms']:.2f}ms p95={r['p95_ms']:.2f}ms", flush=True)

    for M in MS:
        b = mariadb_build(c, f"vec_m{M}", M, run)
        print(f"mariadb vec_m{M}: {b}", flush=True)
        sql = f"SELECT id FROM vec_m{M} ORDER BY VEC_DISTANCE_COSINE(v, %s) LIMIT {{n}}"
        for ef in EFS:
            c.execute(f"SET SESSION mhnsw_ef_search = {ef}")
            f = lambda n: (lambda z: (c.execute(sql.format(n=n), (z.astype('<f4').tobytes(),)), [x[0] for x in c.fetchall()])[1])
            f(10)(Zq[0])  # làm nóng bộ đệm chỉ mục
            run_cfg("mariadb", M, ef, f(10), f(100), b)
        c.execute(f"EXPLAIN " + sql.format(n=10), (Zq[0].astype('<f4').tobytes(),))
        print("  EXPLAIN:", c.fetchall(), flush=True)

        b = manticore_build(m, f"vec_m{M}", M, P.train_ids, Ztr)
        print(f"manticore vec_m{M}: {b}", flush=True)
        for ef in EFS:
            def g(n, ef=ef):
                def q(z):
                    m.execute(f"SELECT id FROM vec_m{M} WHERE knn(vec, {n}, (" + ",".join(f"{x:.6g}" for x in z) +
                              f"), {{ef={max(ef, n)}}}) LIMIT {n}")
                    return [x[0] for x in m.fetchall()]
                return q
            g(10)(Zq[0])
            run_cfg("manticore", M, ef, g(10), g(100), b)

    b = mariadb_build(c, "vec_flat", 0, run, index=False)
    sub = list(Zq[:100])
    q = lambda z: (c.execute("SELECT id FROM vec_flat ORDER BY VEC_DISTANCE_COSINE(v, %s) LIMIT 10",
                             (z.astype('<f4').tobytes(),)), [x[0] for x in c.fetchall()])[1]
    res, lat = timed(q, sub)
    rows.append({"engine": "mariadb-scan", "M": "", "ef": "", "n_queries": 100,
                 "recall@10": float(np.mean([len(t & set(x)) / 10 for t, x in zip(truth10[:100], res)])),
                 **lat_stats(lat), **b})
    print(f"mariadb-scan: recall@10={rows[-1]['recall@10']:.4f} p50={rows[-1]['p50_ms']:.1f}ms", flush=True)
    c.execute("DROP TABLE vec_flat")
    save("edb2_vector", {"rows": rows, "n_train": len(tr), "n_queries": len(Zq), "run_id": run})
    table(rows, ["engine", "M", "ef", "recall@10", "ndcg@10", "map@100_at100", "p50_ms", "p95_ms", "build_s", "index_bytes"])


if __name__ == "__main__":
    main()
