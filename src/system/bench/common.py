"""Phần dùng chung cho benchmark GĐ-H6 (E-DB1, E-DB2, E-DB4, E-DB5).

Giao thức như GĐ6 (experiments/run_experiments.py): 100 bài test mỗi chuyên mục (rng seed 0) làm truy vấn,
kho = 33.759 bài train, "liên quan" = cùng chuyên mục (proxy). Hai loại truy vấn:
  doc  — 50 item tf·idf cao nhất của bài (transaction trong article_item)
  kw   — 3 item tf·idf cao nhất của bài (A6), tức article_item.rnk ≤ 3
"""
import json
import sys
import time
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np

BENCH = Path(__file__).resolve().parent
sys.path.insert(0, str(BENCH.parent))
sys.path.insert(0, str(BENCH.parent / "app"))
from config import connect_mariadb  # noqa: E402

RESULTS = BENCH / "results"
K, MAP_K = 10, 100


class Protocol:
    def __init__(self, db=None):
        db = db or connect_mariadb()
        with db.cursor() as c:
            c.execute("SELECT a.id, a.category_id, a.split, cat.code FROM article a"
                      " JOIN category cat ON cat.id = a.category_id ORDER BY a.id")
            arts = c.fetchall()
            self.cat_of = {i: cat for i, cat, _, _ in arts}
            self.n_in_cat = defaultdict(int)
            for _, cat, sp, _ in arts:
                self.n_in_cat[cat] += sp == "train"
            te = [(i, cat, code) for i, cat, sp, code in arts if sp == "test"]
            ycode = np.array([code for *_, code in te])
            rng = np.random.default_rng(0)
            q_idx = np.concatenate([rng.choice(np.where(ycode == l)[0], 100, replace=False) for l in sorted(set(ycode))])
            self.qids = [te[j][0] for j in q_idx]
            self.qcat = [te[j][1] for j in q_idx]
            self.train_ids = [i for i, _, sp, _ in arts if sp == "train"]
            c.execute("SELECT ai.article_id, i.token, ai.rnk FROM article_item ai JOIN item i ON i.id = ai.item_id"
                      " WHERE ai.article_id IN (" + ",".join(map(str, self.qids)) + ") ORDER BY ai.article_id, ai.rnk")
            self.doc, self.kw = defaultdict(list), defaultdict(list)
            for a, t, r in c.fetchall():
                self.doc[a].append(t)
                if r <= 3:
                    self.kw[a].append(t)

    def queries(self, kind):
        src = self.doc if kind == "doc" else self.kw
        return [src[q] for q in self.qids]

    def metrics(self, ranked, qcat=None):
        """P@10, MAP@100, nDCG@10 như t2v.retrieval, trên danh sách id đã xếp hạng (có thể ngắn hơn 100).
        qcat: chuyên mục của từng truy vấn khi chỉ đánh giá một tập con (mặc định: cả 1.000 truy vấn)."""
        disc = 1 / np.log2(np.arange(2, K + 2))
        out = defaultdict(list)
        for ids, c in zip(ranked, self.qcat if qcat is None else qcat):
            rel = np.array([self.cat_of[i] == c for i in list(ids)[:MAP_K]], dtype=float)
            n_rel = min(MAP_K, self.n_in_cat[c])
            prec = np.cumsum(rel) / np.arange(1, len(rel) + 1) if len(rel) else rel
            out["p@10"].append(rel[:K].sum() / K)
            out["map@100"].append((prec * rel).sum() / n_rel)
            out["ndcg@10"].append((rel[:K] * disc[:len(rel[:K])]).sum() / disc[:min(K, n_rel)].sum())
            out["empty"].append(len(rel) == 0)
        return {m: float(np.mean(v)) for m, v in out.items()}


def strip_accents(s):
    """Bỏ dấu tiếng Việt (người dùng gõ không dấu): NFD bỏ dấu kết hợp, đ → d."""
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    return unicodedata.normalize("NFC", "".join(ch for ch in s if unicodedata.category(ch) != "Mn"))


def timed(fn, items):
    """Chạy fn trên từng phần tử, trả (kết quả, độ trễ ms)."""
    res, lat = [], []
    for x in items:
        t0 = time.perf_counter()
        res.append(fn(x))
        lat.append((time.perf_counter() - t0) * 1000)
    return res, lat


def lat_stats(lat):
    lat = np.asarray(lat)
    return {"p50_ms": float(np.percentile(lat, 50)), "p95_ms": float(np.percentile(lat, 95)),
            "mean_ms": float(lat.mean()), "qps_1thread": float(1000 / lat.mean())}


def save(name, rows):
    RESULTS.mkdir(exist_ok=True)
    path = RESULTS / f"{name}.json"
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(f"→ {path.relative_to(BENCH.parent.parent)}")


def table(rows, cols):
    print(" | ".join(f"{c:>10}" if i else f"{c:<28}" for i, c in enumerate(cols)))
    for r in rows:
        print(" | ".join((f"{r.get(c, ''):>10.4f}" if isinstance(r.get(c), float) else f"{str(r.get(c, '')):>10}")
                         if i else f"{str(r.get(c, '')):<28}" for i, c in enumerate(cols)))
