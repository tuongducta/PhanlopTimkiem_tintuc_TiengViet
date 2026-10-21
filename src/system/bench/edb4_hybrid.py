"""E-DB4: hybrid BM25 + vector (RRF) có tốt hơn từng thành phần không? Bảng Manticore `news` (charset giữ dấu).

Truy vấn: "kw" (3 từ khóa, A6) và "doc" (50 từ) của giao thức GĐ6; kho = train; không khử trùng (giữ giao thức).
  bm25    MATCH @(title_seg, body_seg) (t1 | t2 | …), BM25 k1=1,2, b=0,75
  knn     infer_vector(item ∪ FI≥2 của truy vấn) → HNSW, ef=400
  hybrid  RRF(bm25 top-100, knn top-100), k=60; độ nhạy: k ∈ {10, 60, 200}, độ sâu ∈ {20, 100}
Truy vấn kw được tách theo "có/không chứa FI độ dài ≥ 2" như Bảng 3 của RESULTS.md (GĐ6: TF-IDF 0,634, JOI 0,692).
Lọc chuyên mục: chỉ đo độ trễ (khi lọc, mọi kết quả đều "liên quan" theo proxy cùng chuyên mục, nên không đo chất lượng).

Chạy: .venv-exp/bin/python src/system/bench/edb4_hybrid.py
"""
import time

import numpy as np

from common import Protocol, lat_stats, save, table
from search import Searcher, rrf


def main():
    s = Searcher()
    P = Protocol(s.db)
    rows = []
    for kind in ["kw", "doc"]:
        Q = P.queries(kind)
        lex, sem, has_fi = [], [], []
        lat = {"bm25": [], "knn": [], "infer": []}
        for terms in Q:
            t0 = time.perf_counter()
            lex.append([i for i, _ in s.bm25(terms, 100, split="train")])
            t1 = time.perf_counter()
            v, F = s.embed(transaction=frozenset(terms))
            t2 = time.perf_counter()
            sem.append([i for i, _ in s.knn(v, 100, split="train", ef=400)])
            t3 = time.perf_counter()
            has_fi.append(any(len(f) > 1 for f in F))
            lat["bm25"].append((t1 - t0) * 1000)
            lat["infer"].append((t2 - t1) * 1000)
            lat["knn"].append((t3 - t2) * 1000)
        has_fi = np.array(has_fi)
        variants = {"bm25": lex, "knn": sem}
        for k in [10, 60, 200]:
            for depth in [20, 100]:
                variants[f"hybrid k={k} d={depth}"] = [[i for i, _ in rrf(a[:depth], b[:depth], k=k)][:100]
                                                       for a, b in zip(lex, sem)]
        for name, ranked in variants.items():
            for subset, mask in [("tất cả", np.ones(len(Q), bool)), ("có FI", has_fi), ("không FI", ~has_fi)]:
                if kind == "doc" and subset != "tất cả" or not mask.any():
                    continue
                sub = [r for r, m in zip(ranked, mask) if m]
                qcat = [c for c, m in zip(P.qcat, mask) if m]
                r = {"query": kind, "subset": subset, "n": int(mask.sum()), "method": name, **P.metrics(sub, qcat)}
                if subset == "tất cả":
                    if name == "bm25":
                        r.update(lat_stats(lat["bm25"]))
                    elif name == "knn":
                        r.update(lat_stats(np.add(lat["knn"], lat["infer"])), knn_only_p50_ms=float(np.percentile(lat["knn"], 50)))
                    elif name == "hybrid k=60 d=100":
                        r.update(lat_stats(np.add(np.add(lat["bm25"], lat["knn"]), lat["infer"])))
                rows.append(r)
        print(f"[{kind}] xong; {has_fi.sum()} truy vấn có FI", flush=True)

    # độ trễ khi có lọc chuyên mục (truy vấn kw)
    flt = {}
    for mode in ["bm25", "knn", "hybrid"]:
        lat = []
        for terms, cat in zip(P.queries("kw"), P.qcat):
            t0 = time.perf_counter()
            s.search(" ".join(terms).replace("_", " "), mode=mode, k=10, category_id=cat, dedupe=False)
            lat.append((time.perf_counter() - t0) * 1000)
        flt[mode] = lat_stats(lat)
    print("lọc chuyên mục (search() đầy đủ, gồm pyvi):", {m: round(v["p50_ms"], 1) for m, v in flt.items()})
    save("edb4_hybrid", {"rows": rows, "filtered_latency": flt})
    table(rows, ["query", "subset", "method", "n", "p@10", "map@100", "ndcg@10", "p50_ms"])


if __name__ == "__main__":
    main()
