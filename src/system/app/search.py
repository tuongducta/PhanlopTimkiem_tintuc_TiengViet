"""Tìm kiếm 3 chế độ trên Manticore (GĐ-H4): BM25, KNN (Trans2Vec-JOI), hybrid RRF. Dùng chung cho app/ và bench/.

    s = Searcher()
    s.search("giá vàng tăng mạnh", mode="hybrid", k=10, category_id=4)
      → [{"id", "score", "rank", "bm25_rank", "knn_rank", ...}, ...]; chi tiết bài: s.details(ids)

Truy vấn được xử lý giống tài liệu: NFC → pyvi → chữ thường → bỏ token không phải chữ. Văn bản dài
(> K từ khác nhau) chỉ giữ top-K item theo tf·idf như transaction của Trans2Vec.
Khử trùng (mặc định bật): VNTC có 4.984 bài trùng y hệt nội dung, nên chỉ giữ bài đầu tiên của mỗi body_md5.
Truy vấn gõ không dấu (P1): BM25 chạy trên title_fold/body_fold (âm tiết đã gộp dấu) thay cho trường giữ dấu.
"""
import json
import pickle
import re
import sys
import threading
import time
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
from pyvi import ViTokenizer

ROOT = Path(__file__).resolve().parents[3]  # gốc dự án (mã ở src/system/<gói>/)
sys.path.insert(0, str(ROOT / "src/system"))
sys.path.insert(0, str(ROOT / "src/experiments"))
import t2v  # noqa: E402
from config import connect_manticore, connect_mariadb  # noqa: E402
from vi_text import fold, is_unaccented  # noqa: E402

WORD = re.compile(r"[^\W\d_]+(?:_[^\W\d_]+)*")
SYL = re.compile(r"[^\W\d_]+")
MODELS = ROOT / "src/system/models"
K_ITEMS = 50
RRF_K = 60
BM25 = "OPTION ranker=expr('10000*bm25a(1.2,0.75)'), idf='plain,tfidf_unnormalized', max_matches={n}"


def rrf(*ranked_lists, k=RRF_K):
    """Reciprocal Rank Fusion (Cormack et al. 2009): score = Σ 1 / (k + rank)."""
    score = Counter()
    for ids in ranked_lists:
        for r, i in enumerate(ids, 1):
            score[i] += 1.0 / (k + r)
    return score.most_common()


def segment(text):
    text = unicodedata.normalize("NFC", text)
    return [w for w in (t.lower() for t in ViTokenizer.tokenize(text).split()) if WORD.fullmatch(w)]


def embed_with(model, T, fis, mode):
    """Vector L2-chuẩn hóa của một transaction theo mode của t2v.pattern_tokens; kèm FI khớp."""
    F = t2v.match_fi([T], fis)[0]
    toks = [t for t in t2v.pattern_tokens([T], [F], mode)[0] if t in model.wv.key_to_index]
    if not toks:
        return None, F
    v = model.infer_vector(toks, epochs=20)
    return v / (np.linalg.norm(v) or 1.0), F


class Searcher:
    def __init__(self, table="news", run_id=None):
        from gensim.models.doc2vec import Doc2Vec

        self.table = table
        self.lock = threading.Lock()  # Streamlit chạy mỗi phiên một luồng; hai kết nối pymysql dùng chung
        self.db = connect_mariadb(autocommit=True)
        self.mc = connect_manticore()
        with self.db.cursor() as c:
            if run_id is None:
                c.execute("SELECT MAX(id) FROM model_run WHERE kind = 'trans2vec-joi'")
                run_id = c.fetchone()[0]
            c.execute("SELECT parent_id, JSON_VALUE(params, '$.model_file') FROM model_run WHERE id = %s", (run_id,))
            self.fim_run, model_file = c.fetchone()
            c.execute("SELECT token, idf, is_stop FROM item")
            rows = c.fetchall()
        self.run_id = run_id
        self.idf = {t: f for t, f, _ in rows if f is not None}
        self.stop = {t for t, _, s in rows if s}
        self.fold_stop = {fold(t) for t in self.stop if "_" not in t}
        self.model = Doc2Vec.load(str(MODELS / model_file))
        with open(MODELS / f"run{self.fim_run}_fim.pkl", "rb") as f:
            self.fis = pickle.load(f)["fis"]

    # ------------------------------------------------------------ xử lý truy vấn
    segment = staticmethod(segment)

    def transaction(self, words):
        """Top-K item theo tf·idf (như t2v.transactions)."""
        tf = Counter(t for t in words if t in self.idf)
        return frozenset(sorted(tf, key=lambda t: (-tf[t] * self.idf[t], t))[:K_ITEMS])

    def query_terms(self, words):
        """Từ dùng cho BM25: bỏ từ dừng; văn bản dài thì chỉ giữ transaction."""
        uniq = list(dict.fromkeys(w for w in words if w not in self.stop))
        return uniq if len(uniq) <= K_ITEMS else sorted(self.transaction(words))

    def embed(self, words=None, transaction=None):
        T = transaction if transaction is not None else self.transaction(words)
        return embed_with(self.model, T, self.fis, "joi")

    # ------------------------------------------------------------ truy vấn Manticore
    def _where(self, category_id, split):
        w = ""
        if category_id is not None:
            w += f" AND category_id={int(category_id)}"
        if split is not None:
            w += f" AND split={self.mc.escape(split)}"
        return w

    def bm25(self, terms, k=10, category_id=None, split=None, fields="title_seg,body_seg", syllables=False):
        if not terms:
            return []
        if syllables:  # cấu hình (c): khớp thêm theo âm tiết trên body_syl
            syl = list(dict.fromkeys(s for t in terms for s in t.split("_") if SYL.fullmatch(s)))
            expr = f"(@({fields}) ({' | '.join(terms)})) | (@body_syl ({' | '.join(syl)}))"
        else:
            expr = f"@({fields}) ({' | '.join(terms)})"
        sql = (f"SELECT id, WEIGHT() FROM {self.table} WHERE MATCH({self.mc.escape(expr)})"
               f"{self._where(category_id, split)} LIMIT {int(k)} " + BM25.format(n=max(1000, k)))
        with self.lock, self.mc.cursor() as m:
            m.execute(sql)
            return [(i, float(w)) for i, w in m.fetchall()]

    def bm25_fold(self, terms, k=10, category_id=None, split=None):
        """BM25 trên trường gộp dấu. Term có '_' (từ ghép pyvi đã bỏ dấu) khớp dạng cụm âm tiết."""
        terms = [fold(t) for t in terms]
        terms = list(dict.fromkeys(t for t in terms if t and t not in self.fold_stop))[:K_ITEMS]
        if not terms:
            return []
        parts = [f'"{t.replace("_", " ")}"' if "_" in t else t for t in terms]
        expr = f"@(title_fold,body_fold) ({' | '.join(parts)})"
        sql = (f"SELECT id, WEIGHT() FROM {self.table} WHERE MATCH({self.mc.escape(expr)})"
               f"{self._where(category_id, split)} LIMIT {int(k)} " + BM25.format(n=max(1000, k)))
        with self.lock, self.mc.cursor() as m:
            m.execute(sql)
            return [(i, float(w)) for i, w in m.fetchall()]

    def knn(self, vec, k=10, category_id=None, split=None, ef=None):
        if vec is None:
            return []
        ef = ef or max(4 * k, 200)
        v = "(" + ",".join(f"{x:.6g}" for x in vec) + ")"
        # có bộ lọc thì xin nhiều ứng viên hơn để bù phần bị lọc
        kk = k if category_id is None and split is None else max(k, 4 * k)
        sql = (f"SELECT id, knn_dist() FROM {self.table} WHERE knn(vec, {kk}, {v}, {{ef={ef}}})"
               f"{self._where(category_id, split)} LIMIT {int(k)}")
        with self.lock, self.mc.cursor() as m:
            m.execute(sql)
            return [(i, 1.0 - float(d)) for i, d in m.fetchall()]  # cosine similarity

    def _dedupe(self, ids):
        if not ids:
            return set()
        with self.lock, self.db.cursor() as c:
            c.execute("SELECT id, body_md5 FROM article WHERE id IN (" + ",".join(map(str, map(int, ids))) + ")")
            h = dict(c.fetchall())
        seen, keep = set(), set()
        for i in ids:
            if h.get(i) not in seen:
                seen.add(h.get(i))
                keep.add(i)
        return keep

    def search(self, text, mode="hybrid", k=10, category_id=None, split=None, depth=100, syllables=False,
               dedupe=True, log=False):
        t0 = time.perf_counter()
        words = self.segment(text)
        n = depth if (mode == "hybrid" or dedupe) else k
        folded = is_unaccented(text)
        if mode == "knn":
            lex = []
        elif folded:  # gõ không dấu: token pyvi không khớp trường giữ dấu, nên tìm theo âm tiết đã gộp dấu
            lex = self.bm25_fold(SYL.findall(fold(text)), n, category_id, split)
        else:
            lex = self.bm25(self.query_terms(words), n, category_id, split, syllables=syllables)
        # vector suy luận từ chữ không dấu kéo kết quả lạc đề (1.000 truy vấn kw không dấu: hybrid 0,473 so với
        # BM25 gộp dấu 0,534 nDCG@10), nên hybrid bỏ nhánh vector khi truy vấn không dấu; chế độ knn vẫn chạy
        use_vec = mode == "knn" or (mode == "hybrid" and not folded)
        vec, fi = self.embed(words) if use_vec else (None, [])
        sem = self.knn(vec, n, category_id, split) if use_vec else []
        lex_rank = {i: r for r, (i, _) in enumerate(lex, 1)}
        sem_rank = {i: r for r, (i, _) in enumerate(sem, 1)}
        if mode == "bm25":
            fused = lex
        elif mode == "knn":
            fused = sem
        else:
            fused = rrf([i for i, _ in lex], [i for i, _ in sem])
        if dedupe:
            keep = self._dedupe([i for i, _ in fused])
            fused = [(i, s) for i, s in fused if i in keep]
        fused = fused[:k]
        bm, kn = dict(lex), dict(sem)
        hits = [{"id": i, "score": s, "rank": r, "bm25": bm.get(i), "bm25_rank": lex_rank.get(i),
                 "knn": kn.get(i), "knn_rank": sem_rank.get(i)} for r, (i, s) in enumerate(fused, 1)]
        ms = (time.perf_counter() - t0) * 1000
        if log:
            with self.lock, self.db.cursor() as c:
                c.execute("INSERT INTO search_log (query, mode, category_id, latency_ms, result_ids) VALUES (%s,%s,%s,%s,%s)",
                          (text[:1024], mode, category_id, ms, json.dumps([h["id"] for h in hits])))
        return {"hits": hits, "words": words, "query_fi": [f for f in fi if len(f) > 1], "ms": ms, "folded": folded}

    def details(self, ids):
        """Tiêu đề, chuyên mục, đoạn đầu, tệp nguồn và FI (độ dài ≥ 2) của các bài."""
        if not ids:
            return {}
        idl = ",".join(map(str, map(int, ids)))
        with self.lock, self.db.cursor() as c:
            c.execute(
                "SELECT a.id, a.title, cat.code, cat.name, LEFT(a.body, 400), a.source_file, a.split FROM article a"
                " JOIN category cat ON cat.id = a.category_id WHERE a.id IN (" + idl + ")")
            out = {r[0]: {"title": r[1], "code": r[2], "category": r[3], "snippet": r[4], "file": r[5],
                          "split": r[6], "fi": []} for r in c.fetchall()}
            c.execute("SELECT ais.article_id, s.label FROM article_itemset ais JOIN itemset s ON s.id = ais.itemset_id"
                      f" WHERE s.run_id = %s AND s.size >= 2 AND ais.article_id IN ({idl}) ORDER BY s.support DESC",
                      (self.fim_run,))
            for aid, label in c.fetchall():
                out[aid]["fi"].append(label.replace(t2v.FI_SEP, " + "))
        return out
