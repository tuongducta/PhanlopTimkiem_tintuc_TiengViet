"""GĐ-H4: kiểm tra nhanh tìm kiếm trên Manticore theo giao thức của GĐ6 (truy vấn = bài test, kho = train,
liên quan = cùng chuyên mục; 100 truy vấn/chuyên mục). Đây là kiểm tra cài đặt, benchmark đầy đủ để GĐ-H6.

  bm25        top-50 item tf·idf của bài (transaction trong MariaDB) làm truy vấn OR, BM25 (k1=1.2, b=0.75)
  bm25+syl    như trên + khớp âm tiết trên body_syl (cấu hình (c) của E-DB5)
  knn         vector JOI của bài (article_vector) → HNSW Manticore; so với tìm vét cạn (numpy) để đo recall@10
  hybrid      RRF(bm25, knn), độ sâu 100

Chạy: .venv-exp/bin/python src/system/bench/smoke_search.py
"""
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))
from search import Searcher, rrf  # noqa: E402

K, MAP_K = 10, 100


def metrics(ranked, qcat, cat_of, n_in_cat):
    disc = 1 / np.log2(np.arange(2, K + 2))
    out = defaultdict(list)
    for ids, c in zip(ranked, qcat):
        rel = np.array([cat_of[i] == c for i in ids[:MAP_K]], dtype=float)
        n_rel = min(MAP_K, n_in_cat[c])
        prec = np.cumsum(rel) / np.arange(1, len(rel) + 1) if len(rel) else rel
        out["p@10"].append(rel[:K].sum() / K)
        out["map@100"].append((prec * rel).sum() / n_rel)
        out["ndcg@10"].append((rel[:K] * disc[:len(rel[:K])]).sum() / disc[:min(K, n_rel)].sum())
    return {m: float(np.mean(v)) for m, v in out.items()}


def main():
    s = Searcher()
    c = s.db.cursor()
    c.execute("SELECT id, category_id, split FROM article ORDER BY id")
    arts = c.fetchall()
    cat_of = {i: cat for i, cat, _ in arts}
    te = [(i, cat) for i, cat, sp in arts if sp == "test"]
    yte = np.array([cat for _, cat in te])
    n_in_cat = defaultdict(int)
    for _, cat, sp in arts:
        n_in_cat[cat] += sp == "train"
    rng = np.random.default_rng(0)  # như train_models.py / run_experiments.py (nhãn sắp theo mã chuyên mục)
    c.execute("SELECT id, code FROM category")
    code = dict(c.fetchall())
    ycode = np.array([code[x] for x in yte])
    q_idx = np.concatenate([rng.choice(np.where(ycode == l)[0], 100, replace=False) for l in sorted(set(ycode))])
    qids = [te[j][0] for j in q_idx]
    qcat = [te[j][1] for j in q_idx]

    c.execute("SELECT ai.article_id, i.token FROM article_item ai JOIN item i ON i.id = ai.item_id"
              " WHERE ai.article_id IN (" + ",".join(map(str, qids)) + ")")
    terms = defaultdict(list)
    for a, t in c.fetchall():
        terms[a].append(t)
    c.execute("SELECT v.article_id, v.vec, a.split FROM article_vector v JOIN article a ON a.id = v.article_id"
              " WHERE v.run_id = %s", (s.run_id,))
    vec, tr_ids, tr_vecs = {}, [], []
    for a, b, sp in c.fetchall():
        v = np.frombuffer(b, dtype="<f4")
        vec[a] = v
        if sp == "train":
            tr_ids.append(a)
            tr_vecs.append(v)
    tr_ids, Ztr = np.array(tr_ids), np.vstack(tr_vecs)

    ranked, lat = defaultdict(list), defaultdict(list)
    recall = []
    for q in qids:
        t0 = time.perf_counter()
        b = [i for i, _ in s.bm25(sorted(terms[q]), MAP_K, split="train")]
        t1 = time.perf_counter()
        bs = [i for i, _ in s.bm25(sorted(terms[q]), MAP_K, split="train", syllables=True)]
        t2 = time.perf_counter()
        kn = [i for i, _ in s.knn(vec[q], MAP_K, split="train")]
        t3 = time.perf_counter()
        hy = [i for i, _ in rrf(b, kn)][:MAP_K]
        for m, ids, dt in [("bm25", b, t1 - t0), ("bm25+syl", bs, t2 - t1), ("knn", kn, t3 - t2), ("hybrid", hy, t3 - t2 + t1 - t0)]:
            ranked[m].append(ids)
            lat[m].append(dt * 1000)
        exact = set(tr_ids[np.argsort(-(Ztr @ vec[q]))[:K]])
        recall.append(len(exact & set(kn[:K])) / K)
    ranked["knn-exact"] = [list(tr_ids[np.argsort(-(Ztr @ vec[q]))[:MAP_K]]) for q in qids]

    print(f"{len(qids)} truy vấn, kho train {len(tr_ids)} bài")
    print(f"{'chế độ':<11}{'P@10':>8}{'MAP@100':>9}{'nDCG@10':>9}{'p50 ms':>8}{'p95 ms':>8}")
    for m in ["bm25", "bm25+syl", "knn", "knn-exact", "hybrid"]:
        r = metrics(ranked[m], qcat, cat_of, n_in_cat)
        l = lat.get(m)
        lt = f"{np.percentile(l, 50):>8.1f}{np.percentile(l, 95):>8.1f}" if l else ""
        print(f"{m:<11}{r['p@10']:>8.4f}{r['map@100']:>9.4f}{r['ndcg@10']:>9.4f}{lt}")
    print(f"HNSW recall@10 so với vét cạn: {np.mean(recall):.4f}")

    # Truy vấn văn bản tự do (đi qua pyvi + infer_vector)
    for text in ["giá vàng tăng mạnh", "đội tuyển Việt Nam thắng trận"]:
        for mode in ["bm25", "knn", "hybrid"]:
            t0 = time.perf_counter()
            res = s.search(text, mode=mode, k=3)["hits"]
            dt = (time.perf_counter() - t0) * 1000
            d = s.details([r["id"] for r in res])
            print(f"[{mode:>6} {dt:5.0f} ms] {text!r}: " + " | ".join(f"{d[r['id']]['code']} {d[r['id']]['title'][:40]}" for r in res))


if __name__ == "__main__":
    main()
