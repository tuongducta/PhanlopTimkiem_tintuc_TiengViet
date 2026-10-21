"""Thư viện lõi cho thực nghiệm Trans2Vec trên VNTC (Chương 9 của survey).

Mô-đun tương ứng kiến trúc Hình 9.1:
  M2  build_vocab / transactions   — từ dừng theo dữ liệu + giữ top-k item mỗi bài theo TF-IDF
  M3  pair_counts / choose_delta / mine_fi / match_fi / closed_only — khai phá tập phổ biến
  M4  train_pvdbow / infer         — PV-DBOW (gensim Doc2Vec dm=0) trên item / FI / item ∪ FI
  M6  classify                     — SVM tuyến tính (C=1, như [13]) và hồi quy logistic
  M7  retrieval                    — tìm kiếm cosine top-k, P@10 / MAP@100 / nDCG@10

Nguyên tắc chống rò rỉ (Mục 7.3): từ vựng, IDF, tập phổ biến, δ và embedding chỉ học trên train.
"""
import csv
import gzip
import itertools
import math
import time
from collections import Counter

import numpy as np
from scipy import sparse

FI_SEP = "|"


# ---------------------------------------------------------------- dữ liệu
def load_corpus(path):
    csv.field_size_limit(10**9)
    with gzip.open(path, "rt", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    split = lambda s: [r for r in rows if r["split"] == s]
    return split("train"), split("test")


# ---------------------------------------------------------------- M2: từ vựng và transaction
class Vocab:
    """Từ dừng = token xuất hiện trong > max_df văn bản train; bỏ token hiếm (< min_df)."""

    def __init__(self, train_docs, min_df=3, max_df=0.3):
        df = Counter()
        for d in train_docs:
            df.update(set(d))
        n = len(train_docs)
        self.stopwords = {t for t, c in df.items() if c / n > max_df}
        self.idf = {t: math.log(n / c) for t, c in df.items() if c >= min_df and t not in self.stopwords}
        self.index = {t: i for i, t in enumerate(sorted(self.idf))}


def transactions(docs, vocab, k):
    """Mỗi bài → tập (frozenset) k item có điểm tf·idf cao nhất trong bài (k=None: giữ hết)."""
    out = []
    for d in docs:
        tf = Counter(t for t in d if t in vocab.idf)
        ranked = sorted(tf, key=lambda t: (-tf[t] * vocab.idf[t], t))
        out.append(frozenset(ranked[:k] if k else ranked))
    return out


def top_items(docs, vocab, n):
    """n item tf·idf cao nhất của mỗi bài, có thứ tự (dùng làm truy vấn từ khóa ngắn)."""
    res = []
    for d in docs:
        tf = Counter(t for t in d if t in vocab.idf)
        res.append(sorted(tf, key=lambda t: (-tf[t] * vocab.idf[t], t))[:n])
    return res


# ---------------------------------------------------------------- M3: tập phổ biến
def binary_matrix(trans, items):
    idx = {t: i for i, t in enumerate(items)}
    rows, cols = [], []
    for r, T in enumerate(trans):
        for t in T:
            j = idx.get(t)
            if j is not None:
                rows.append(r)
                cols.append(j)
    return sparse.csr_matrix((np.ones(len(rows), dtype=np.int32), (rows, cols)), shape=(len(trans), len(items)))


def pair_counts(trans, min_count):
    """Đếm support của item đơn và cặp item (chỉ trên item có support ≥ min_count) bằng XᵀX thưa."""
    c1 = Counter()
    for T in trans:
        c1.update(T)
    items = sorted(t for t, c in c1.items() if c >= min_count)
    X = binary_matrix(trans, items)
    C = sparse.triu(X.T @ X, k=1).tocoo()
    keep = C.data >= min_count
    pairs = {(items[i], items[j]): int(c) for i, j, c in zip(C.row[keep], C.col[keep], C.data[keep])}
    return {t: c1[t] for t in items}, pairs


def choose_delta(trans, grid):
    """Phương pháp elbow (như [13]): đường cong số FI (độ dài ≤ 2) theo δ; chọn điểm xa dây cung nhất
    sau khi chuẩn hóa hai trục về [0, 1] trên thang TUYẾN TÍNH (kiểu Kneedle) — điểm mà giảm δ thêm
    thì số FI bắt đầu tăng vọt, đúng như cách đọc Fig. 4 của [13].

    Ghi chú: phiên bản đầu dùng thang log-log và chọn δ = 2,16% trên VNTC (chỉ 20 cặp FI, 82% bài
    test không chứa FI độ dài ≥ 2) — lệch hẳn khoảng 0,2–0,7% của [13]. Xem RESULTS.md."""
    n = len(trans)
    singles, pairs = pair_counts(trans, max(2, math.floor(min(grid) * n)))
    s_vals = np.array(list(singles.values()))
    p_vals = np.array(list(pairs.values()))
    curve = [(d, int((s_vals >= d * n).sum() + (p_vals >= d * n).sum())) for d in grid]
    x = np.array([d for d, _ in curve], dtype=float)
    y = np.array([c for _, c in curve], dtype=float)
    x = (x - x.min()) / (x.max() - x.min())
    y = (y - y.min()) / max(y.max() - y.min(), 1)
    p0, p1 = np.array([x[0], y[0]]), np.array([x[-1], y[-1]])
    u = (p1 - p0) / np.linalg.norm(p1 - p0)
    dist = [abs(u[0] * (yi - p0[1]) - u[1] * (xi - p0[0])) for xi, yi in zip(x, y)]
    return grid[int(np.argmax(dist))], curve


def mine_fi(trans, delta, max_len=3):
    """Tập phổ biến độ dài 1..max_len với support ≥ δ (đếm trực tiếp, cắt tỉa kiểu Apriori)."""
    n = len(trans)
    min_count = max(2, math.ceil(delta * n))
    singles, pairs = pair_counts(trans, min_count)
    fis = {(t,): c for t, c in singles.items()}
    fis.update(pairs)
    if max_len >= 3:
        pair_set = set(pairs)
        c3 = Counter()
        for T in trans:
            for tri in _triples_in(T, singles, pair_set):
                c3[tri] += 1
        fis.update({t: c for t, c in c3.items() if c >= min_count})
    return fis


def _pairs_in(T, singles, pair_set):
    items = sorted(t for t in T if t in singles)
    return [p for p in itertools.combinations(items, 2) if p in pair_set]


def _triples_in(T, singles, pair_set):
    hits = _pairs_in(T, singles, pair_set)
    nbr = {}
    for a, b in hits:
        nbr.setdefault(a, set()).add(b)
    for a, b in hits:
        for c in nbr.get(b, ()):
            if c in nbr.get(a, ()):
                yield (a, b, c)


def match_fi(trans, fis):
    """Danh sách FI (độ dài ≥ 1) chứa trong mỗi transaction."""
    singles = {t[0] for t in fis if len(t) == 1}
    pair_set = {t for t in fis if len(t) == 2}
    tri_set = {t for t in fis if len(t) == 3}
    out = []
    for T in trans:
        found = [(t,) for t in sorted(T) if t in singles]
        found += _pairs_in(T, singles, pair_set)
        if tri_set:
            found += [t for t in _triples_in(T, singles, pair_set) if t in tri_set]
        out.append(found)
    return out


def closed_only(fis):
    """Giữ tập phổ biến đóng: không có tập cha (trong tập đã khai phá) cùng support."""
    not_closed = set()
    for s, sc in fis.items():  # với mỗi tập cha s, đánh dấu các tập con trực tiếp cùng support
        if len(s) > 1:
            for t in itertools.combinations(s, len(s) - 1):
                if fis.get(t) == sc:
                    not_closed.add(t)
    return {t: c for t, c in fis.items() if t not in not_closed}


def fi_token(t):
    return FI_SEP.join(t)


def pattern_tokens(trans, matched, mode):
    """Chuỗi "từ" đưa vào PV-DBOW:  it = item;  fi = FI (gồm cả FI 1 phần tử);  joi = item ∪ FI(≥2)."""
    out = []
    for T, F in zip(trans, matched):
        if mode == "it":
            out.append(sorted(T))
        elif mode == "fi":
            out.append([fi_token(f) for f in F])
        else:
            out.append(sorted(T) + [fi_token(f) for f in F if len(f) > 1])
    return out


# ---------------------------------------------------------------- M4: PV-DBOW
def train_pvdbow(token_lists, d, seed, epochs=20, workers=8):
    from gensim.models.doc2vec import Doc2Vec, TaggedDocument

    docs = [TaggedDocument(t, [i]) for i, t in enumerate(token_lists)]
    model = Doc2Vec(dm=0, dbow_words=0, vector_size=d, negative=5, hs=0, min_count=1, sample=0,
                    epochs=epochs, workers=workers, seed=seed)
    model.build_vocab(docs)
    model.train(docs, total_examples=len(docs), epochs=model.epochs)
    X = np.vstack([model.dv[i] for i in range(len(docs))])
    X[[len(t) == 0 for t in token_lists]] = 0.0  # transaction rỗng → vector 0 (như [13])
    return model, X


def infer(model, token_lists, epochs=20):
    X = np.zeros((len(token_lists), model.vector_size), dtype=np.float32)
    for i, toks in enumerate(token_lists):
        toks = [t for t in toks if t in model.wv.key_to_index]
        if toks:
            X[i] = model.infer_vector(toks, epochs=epochs)
    return X


def l2(X):
    if sparse.issparse(X):
        from sklearn.preprocessing import normalize
        return normalize(X)
    n = np.linalg.norm(X, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return X / n


# ---------------------------------------------------------------- M6: phân loại
def classify(Xtr, ytr, Xte, yte, kind="svm"):
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, f1_score
    from sklearn.svm import LinearSVC

    clf = LinearSVC(C=1.0, max_iter=5000) if kind == "svm" else LogisticRegression(max_iter=3000)
    t0 = time.time()
    clf.fit(Xtr, ytr)
    t1 = time.time()
    pred = clf.predict(Xte)
    t2 = time.time()
    return {"acc": accuracy_score(yte, pred), "macro_f1": f1_score(yte, pred, average="macro"),
            "fit_s": t1 - t0, "predict_s": t2 - t1}


# ---------------------------------------------------------------- M7: tìm kiếm
def retrieval(Zc, yc, Zq, yq, k=10, map_k=100):
    """Truy vấn Zq trên kho Zc theo cosine; liên quan = cùng chủ đề (nhãn thay thế, Mục 7.3)."""
    Zc, Zq = l2(Zc), l2(Zq)
    S = Zq @ Zc.T
    S = S.toarray() if sparse.issparse(S) else np.asarray(S)
    top = np.argpartition(-S, map_k, axis=1)[:, :map_k]
    order = np.take_along_axis(S, top, axis=1).argsort(axis=1)[:, ::-1]
    top = np.take_along_axis(top, order, axis=1)
    rel = (np.asarray(yc)[top] == np.asarray(yq)[:, None]).astype(float)
    n_rel = np.array([min(map_k, (np.asarray(yc) == y).sum()) for y in yq])
    prec = np.cumsum(rel, axis=1) / np.arange(1, map_k + 1)
    ap = (prec * rel).sum(axis=1) / n_rel
    disc = 1 / np.log2(np.arange(2, k + 2))
    idcg = np.array([disc[: min(k, r)].sum() for r in n_rel])
    ndcg = (rel[:, :k] * disc).sum(axis=1) / idcg
    return {"p@10": rel[:, :k].mean(), "map@100": ap.mean(), "ndcg@10": ndcg.mean()}
