"""Phân loại trực tuyến: mốc Trans2Vec gốc, 4 biến thể (TRANS-IT, TRANS-FI, Trans2Vec-IND, Trans2Vec-JOI)
và mô hình cải tiến (Trans2Vec-CAT hoặc -STACK) — huấn luyện ở train_models.py và train_variants.py.

    clf = Classifier(searcher)          # dùng chung từ vựng, FI và mô hình JOI với Searcher
    clf.predict("…nội dung bài…")       → {"models": [...], "items": [...], "fi": [...], "ms": ...}
"""
import hashlib
import pickle
import time
from collections import Counter

import numpy as np

from search import MODELS, embed_with
import t2v  # noqa: E402  (search.py đã thêm experiments/ vào sys.path)

FI_PREFIX = "fi:"  # như pipeline/train_variants.py: FI là token riêng trong đầu vào Items-FIs của mã gốc


def orig_tokens(T, F):
    return sorted(T) + [FI_PREFIX + t2v.fi_token(f) for f in sorted(F, key=lambda f: (len(f), f))]


def l2(v):
    return v / (np.linalg.norm(v) or 1.0)


class Classifier:
    # (kind, tên hiển thị, ghi chú); mô hình cải tiến là kind nào có trong CSDL (cat hoặc stack)
    KINDS = [("trans2vec-orig", "Trans2Vec gốc (mốc)",
              "Mã tác giả · transductive · LinearSVC"),
             ("trans-it", "TRANS-IT", "PV-DBOW trên item"),
             ("trans-fi", "TRANS-FI", "PV-DBOW trên FI"),
             ("trans2vec-ind", "Trans2Vec-IND", "Trung bình vector IT và FI"),
             ("trans2vec-joi", "Trans2Vec-JOI", "PV-DBOW trên item ∪ FI"),
             ("trans2vec-cat", "Trans2Vec-CAT (cải tiến)", "Nối vector IT ‖ FI ‖ JOI → LR"),
             ("trans2vec-stack", "Trans2Vec-STACK (cải tiến)", "LR meta trên xác suất của IT, FI, IND, JOI")]
    VARIANTS = ["trans-it", "trans-fi", "trans2vec-ind", "trans2vec-joi"]

    def __init__(self, searcher):
        from gensim.models.doc2vec import Doc2Vec

        self.s = searcher
        self.models = []
        with self.s.lock, self.s.db.cursor() as c:
            c.execute("SELECT code, name FROM category")
            self.cat_name = dict(c.fetchall())
            c.execute("SELECT code, id FROM category")
            self.cat_id = dict(c.fetchall())
            for kind, name, note in self.KINDS:
                c.execute("SELECT MAX(id) FROM model_run WHERE kind = %s", (kind,))
                emb = c.fetchone()[0]
                if emb is None:
                    continue
                c.execute("SELECT l.id, l.kind, JSON_VALUE(e.params, '$.model_file'), ev.value FROM model_run l"
                          " JOIN model_run e ON e.id = l.parent_id"
                          " JOIN eval_result ev ON ev.run_id = l.id AND ev.metric = 'macro_f1'"
                          " WHERE l.kind IN ('lr', 'svm') AND l.parent_id = %s ORDER BY l.id DESC LIMIT 1", (emb,))
                run, clf_kind, model_file, f1 = c.fetchone()
                with open(MODELS / f"run{run}_{clf_kind}.pkl", "rb") as f:
                    clf = pickle.load(f)
                rep = None
                if emb == self.s.run_id:
                    rep = self.s.model
                elif model_file:
                    rep = Doc2Vec.load(str(MODELS / model_file))
                self.models.append({"kind": kind, "name": name, "note": note, "run": run, "rep": rep, "clf": clf,
                                    "f1": f1, "improved": kind in ("trans2vec-cat", "trans2vec-stack")})
        self.by_kind = {m["kind"]: m for m in self.models}

    def _vectors(self, T):
        """Vector (đã chuẩn hóa) của IT, FI, JOI cho transaction T; None nếu không có token nào trong từ vựng."""
        V, F = {}, []
        for kind, mode in [("trans-it", "it"), ("trans-fi", "fi"), ("trans2vec-joi", "joi")]:
            if kind in self.by_kind:
                V[kind], F = embed_with(self.by_kind[kind]["rep"], T, self.s.fis, mode)
        return V, F

    def predict(self, text, log=False):
        t0 = time.perf_counter()
        words = self.s.segment(text)
        T = self.s.transaction(words)
        V, F = self._vectors(T)
        Z = {k: (v if v is not None else np.zeros(self.s.model.vector_size, dtype=np.float32)) for k, v in V.items()}
        if "trans-it" in Z and "trans-fi" in Z:
            Z["trans2vec-ind"] = l2((Z["trans-it"] + Z["trans-fi"]) / 2)
        out = []
        for m in self.models:
            k = m["kind"]
            if k == "trans2vec-orig":
                toks = [t for t in orig_tokens(T, F) if t in m["rep"].wv.key_to_index]
                if not toks:
                    out.append({**self._meta(m), "proba": None})
                    continue
                S = m["clf"].decision_function(m["rep"].infer_vector(toks).reshape(1, -1))[0]
                p = np.exp(S - S.max())
                p /= p.sum()
            else:
                if k in V and V[k] is None or k == "trans2vec-ind" and V.get("trans-it") is None:
                    out.append({**self._meta(m), "proba": None})
                    continue
                if k == "trans2vec-cat":
                    X = np.hstack([Z["trans-it"], Z["trans-fi"], Z["trans2vec-joi"]])
                elif k == "trans2vec-stack":
                    X = np.hstack([self.by_kind[b]["clf"].predict_proba(Z[b].reshape(1, -1))[0] for b in self.VARIANTS])
                else:
                    X = Z[k]
                p = m["clf"].predict_proba(X.reshape(1, -1))[0]
            proba = sorted(zip(m["clf"].classes_, p), key=lambda x: -x[1])
            out.append({**self._meta(m), "proba": [(c, self.cat_name[c], float(x)) for c, x in proba]})
        ms = (time.perf_counter() - t0) * 1000
        joi = next((o for o in out if o["kind"] == "trans2vec-joi"), None)
        if log and joi and joi["proba"]:
            with self.s.lock, self.s.db.cursor() as c:
                c.execute("INSERT INTO classify_log (text_hash, run_id, pred_category_id, latency_ms) VALUES (%s,%s,%s,%s)",
                          (hashlib.sha256(text.encode()).digest(), joi["run"], self.cat_id[joi["proba"][0][0]], ms))
        tf = Counter(t for t in words if t in self.s.idf)
        items = sorted(T, key=lambda t: (-tf[t] * self.s.idf[t], t))
        return {"models": out, "words": words, "items": items, "fi": [f for f in F if len(f) > 1], "ms": ms}

    @staticmethod
    def _meta(m):
        return {k: m[k] for k in ("kind", "name", "note", "run", "f1", "improved")}
