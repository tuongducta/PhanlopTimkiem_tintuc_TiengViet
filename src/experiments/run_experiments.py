"""Bước 2 — Chạy toàn bộ thực nghiệm theo thiết kế Bảng 9.1 / 9.2 của survey.

  E1  Chính (từ pyvi, k=50, d=128): baseline + TRANS-IT/FI/IND/JOI × 3 seed; tìm kiếm; A3, A5, A6;
      FI đặc trưng cho từng chuyên mục (diễn giải, mô-đun M6)
  E2  A1: âm tiết (không tách từ)
  E3  A2: k ∈ {20, 100}
  E4  A4: d ∈ {64, 256}

Kết quả ghi vào experiments/results/*.csv (+ log). Chạy:
  .venv-exp/bin/python src/experiments/run_experiments.py            # toàn bộ VNTC-10
  .venv-exp/bin/python src/experiments/run_experiments.py --quick    # thử nhanh trên mẫu nhỏ
"""
import argparse
import csv
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import sparse

import t2v

ROOT = Path(__file__).resolve().parents[2]  # gốc dự án (mã ở src/experiments/)
CORPUS = ROOT / "sources/data/vntc/processed/corpus.tsv.gz"
DELTA_GRID = list(np.round(np.geomspace(0.001, 0.05, 15), 5))

ap = argparse.ArgumentParser()
ap.add_argument("--quick", action="store_true")
ap.add_argument("--only", default="E1,E2,E3,E4")
args = ap.parse_args()
OUT = ROOT / ("src/experiments/results_quick" if args.quick else "src/experiments/results")
OUT.mkdir(parents=True, exist_ok=True)
SEEDS = [1] if args.quick else [1, 2, 3]
EPOCHS = 20  # 5 epoch là quá ít: vector gần như không rời giá trị khởi tạo (đã kiểm chứng, xem RESULTS.md)
LOG = open(OUT / "log.txt", "a", encoding="utf-8")


def log(*a):
    msg = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(msg, flush=True)
    LOG.write(msg + "\n")
    LOG.flush()


def append(name, row):
    # Ghi thêm bản JSON Lines (mỗi dòng đủ tên trường); CSV giữ để tương thích make_report.py
    with open(OUT / name.replace(".csv", ".jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False, default=float) + "\n")
    path = OUT / name
    new = not path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow({k: (round(v, 5) if isinstance(v, float) else v) for k, v in row.items()})


def record(exp, method, view, k, d, seed, res, clf="svm", **extra):
    row = {"exp": exp, "method": method, "view": view, "k": k, "d": d, "seed": seed, "clf": clf, **res, **extra}
    append("classification.csv", row)
    log(f"[{exp}] {method:<22} {view} k={k} d={d} seed={seed} {clf}: acc={res['acc']:.4f} macroF1={res['macro_f1']:.4f}")


def record_ret(exp, method, view, query, res, **extra):
    append("retrieval.csv", {"exp": exp, "method": method, "view": view, "query": query, **res, **extra})
    log(f"[{exp}] RET {method:<18} {view} {query}: P@10={res['p@10']:.4f} MAP@100={res['map@100']:.4f} nDCG@10={res['ndcg@10']:.4f}")


# ---------------------------------------------------------------- dữ liệu
log("=== Tải corpus", "(quick)" if args.quick else "")
train_rows, test_rows = t2v.load_corpus(CORPUS)
if args.quick:
    rng = np.random.default_rng(0)
    train_rows = [train_rows[i] for i in rng.choice(len(train_rows), 3000, replace=False)]
    test_rows = [test_rows[i] for i in rng.choice(len(test_rows), 3000, replace=False)]
ytr = np.array([r["label"] for r in train_rows])
yte = np.array([r["label"] for r in test_rows])
log(f"train={len(ytr)} test={len(yte)}")

# Truy vấn tìm kiếm: 100 bài test mỗi chủ đề (phân tầng), kho = toàn bộ train
rng = np.random.default_rng(0)
q_idx = np.concatenate([rng.choice(np.where(yte == c)[0], min(100, (yte == c).sum()), replace=False)
                        for c in sorted(set(yte))])


class View:
    """Dữ liệu dẫn xuất cho một góc nhìn (word/syl) và một k."""

    def __init__(self, view, k):
        self.view, self.k = view, k
        self.tr_docs = [r[view].split() for r in train_rows]
        self.te_docs = [r[view].split() for r in test_rows]
        self.vocab = t2v.Vocab(self.tr_docs)
        self.T_tr = t2v.transactions(self.tr_docs, self.vocab, k)
        self.T_te = t2v.transactions(self.te_docs, self.vocab, k)
        t0 = time.time()
        self.delta, self.curve = t2v.choose_delta(self.T_tr, DELTA_GRID)
        self.fis = t2v.mine_fi(self.T_tr, self.delta)
        self.mine_s = time.time() - t0
        self.F_tr = t2v.match_fi(self.T_tr, self.fis)
        self.F_te = t2v.match_fi(self.T_te, self.fis)
        n_by_len = Counter(len(t) for t in self.fis)
        self.stats = {"vocab": len(self.vocab.idf), "stopwords": len(self.vocab.stopwords),
                      "delta": self.delta, "n_fi": len(self.fis), "n_fi_len": dict(sorted(n_by_len.items())),
                      "mine_s": round(self.mine_s, 1),
                      "fi_per_doc_train": float(np.mean([len(f) for f in self.F_tr])),
                      "docs_without_fi2_test": float(np.mean([not any(len(x) > 1 for x in f) for f in self.F_te]))}
        for dlt, n in self.curve:
            append("fi_curve.csv", {"view": view, "k": k, "delta": dlt, "n_fi_le2": n, "chosen": dlt == self.delta})
        log(f"View {view} k={k}: {json.dumps(self.stats, ensure_ascii=False)}")

    def trans2vec(self, mode, d, seed, fis_override=None):
        F_tr, F_te = self.F_tr, self.F_te
        if fis_override is not None:
            F_tr, F_te = t2v.match_fi(self.T_tr, fis_override), t2v.match_fi(self.T_te, fis_override)
        t0 = time.time()
        model, Xtr = t2v.train_pvdbow(t2v.pattern_tokens(self.T_tr, F_tr, mode), d, seed, epochs=EPOCHS)
        t1 = time.time()
        Xte = t2v.infer(model, t2v.pattern_tokens(self.T_te, F_te, mode), epochs=EPOCHS)
        t2 = time.time()
        return model, t2v.l2(Xtr), t2v.l2(Xte), {"train_s": t1 - t0, "infer_s": t2 - t1}


def tfidf(view, full=True):
    from sklearn.feature_extraction.text import TfidfVectorizer
    vocab = sorted(view.vocab.idf)
    vec = TfidfVectorizer(analyzer=lambda x: x, vocabulary=vocab)
    if full:
        f = lambda docs: [[t for t in d if t in view.vocab.idf] for d in docs]
        return vec.fit_transform(f(view.tr_docs)), vec.transform(f(view.te_docs))
    return vec.fit_transform([list(T) for T in view.T_tr]), vec.transform([list(T) for T in view.T_te])


def fi_matrix(view, kind):
    fis = sorted(view.fis)
    idx = {t: i for i, t in enumerate(fis)}
    n = len(view.T_tr)

    def build(F):
        rows, cols, vals = [], [], []
        for r, found in enumerate(F):
            for t in found:
                rows.append(r)
                cols.append(idx[t])
                vals.append(1.0 if kind == "bin" else view.fis[t] / n)
        return sparse.csr_matrix((vals, (rows, cols)), shape=(len(F), len(fis)))

    return build(view.F_tr), build(view.F_te)


def short_queries(view, n_items=3):
    """A6: truy vấn từ khóa ngắn = 3 item tf·idf cao nhất của bài truy vấn."""
    q_docs = [view.te_docs[i] for i in q_idx]
    items = t2v.top_items(q_docs, view.vocab, n_items)
    T = [frozenset(x) for x in items]
    return T, t2v.match_fi(T, view.fis)


# ================================================================= E1: thực nghiệm chính
if "E1" in args.only:
    log("=== E1: thực nghiệm chính (word, k=50, d=128)")
    V = View("word", 50)
    json.dump(V.stats, open(OUT / "stats_word_k50.json", "w"), ensure_ascii=False, indent=1)

    # --- Baseline thưa
    Xtr, Xte = tfidf(V, full=True)
    tfidf_tr, tfidf_te = Xtr, Xte
    for clf in ["svm", "lr"]:
        record("E1", "TF-IDF (toàn văn)", "word", "full", Xtr.shape[1], 0, t2v.classify(Xtr, ytr, Xte, yte, clf), clf)
    record_ret("E1", "TF-IDF (toàn văn)", "word", "doc", t2v.retrieval(Xtr, ytr, Xte[q_idx], yte[q_idx]))
    from sklearn.feature_extraction.text import CountVectorizer
    cv = CountVectorizer(analyzer=lambda x: x, vocabulary=sorted(V.vocab.idf))
    f = lambda docs: [[t for t in d if t in V.vocab.idf] for d in docs]
    B_tr, B_te = cv.fit_transform(f(V.tr_docs)), cv.transform(f(V.te_docs))
    record("E1", "BOW (toàn văn)", "word", "full", B_tr.shape[1], 0, t2v.classify(B_tr, ytr, B_te, yte))
    Xtr, Xte = tfidf(V, full=False)
    record("E1", "TF-IDF (top-k item)", "word", 50, Xtr.shape[1], 0, t2v.classify(Xtr, ytr, Xte, yte))
    for kind in ["bin", "sup"]:
        Xtr, Xte = fi_matrix(V, kind)
        record("E1", f"FI-{kind.upper()}", "word", 50, Xtr.shape[1], 0, t2v.classify(Xtr, ytr, Xte, yte))
    from sklearn.feature_selection import SelectKBest, chi2
    sel = SelectKBest(chi2, k=128).fit(tfidf_tr, ytr)
    record("E1", "TF-IDF + χ² (128)", "word", "full", 128, 0,
           t2v.classify(t2v.l2(sel.transform(tfidf_tr)), ytr, t2v.l2(sel.transform(tfidf_te)), yte))

    # --- MLP-128 có giám sát (theo [7]: TF-IDF 10k → 2 lớp ẩn → lấy lớp ẩn cuối làm đặc trưng → SVM)
    from sklearn.neural_network import MLPClassifier
    df_rank = np.asarray((tfidf_tr > 0).sum(axis=0)).ravel().argsort()[::-1][:10000]
    M_tr, M_te = t2v.l2(tfidf_tr[:, df_rank]), t2v.l2(tfidf_te[:, df_rank])
    t0 = time.time()
    mlp = MLPClassifier(hidden_layer_sizes=(128, 128), batch_size=128, max_iter=30, early_stopping=True,
                        random_state=1).fit(M_tr, ytr)
    hid = lambda X: np.maximum(0, np.maximum(0, X @ mlp.coefs_[0] + mlp.intercepts_[0]) @ mlp.coefs_[1] + mlp.intercepts_[1])
    H_tr, H_te = t2v.l2(np.asarray(hid(M_tr))), t2v.l2(np.asarray(hid(M_te)))
    record("E1", "MLP-128 có giám sát [7]", "word", "full", 128, 1, t2v.classify(H_tr, ytr, H_te, yte),
           repr_s=time.time() - t0)
    record_ret("E1", "MLP-128 có giám sát [7]", "word", "doc", t2v.retrieval(H_tr, ytr, H_te[q_idx], yte[q_idx]))

    # --- LDA-100 (mô hình chủ đề, nhánh D3)
    from gensim.corpora import Dictionary
    from gensim.models import LdaModel  # LdaMulticore tạo tiến trình con, nạp lại script trên macOS
    t0 = time.time()
    dct = Dictionary([list(V.vocab.idf)])
    bow = lambda docs: [dct.doc2bow([t for t in d if t in V.vocab.idf]) for d in docs]
    btr, bte = bow(V.tr_docs), bow(V.te_docs)
    lda = LdaModel(btr, id2word=dct, num_topics=100, passes=3 if not args.quick else 1, random_state=1)
    topics = lambda bb: np.array([[p for _, p in lda.get_document_topics(b, minimum_probability=0)] for b in bb])
    L_tr, L_te = t2v.l2(topics(btr)), t2v.l2(topics(bte))
    record("E1", "LDA-100", "word", "full", 100, 1, t2v.classify(L_tr, ytr, L_te, yte), repr_s=time.time() - t0)
    record_ret("E1", "LDA-100", "word", "doc", t2v.retrieval(L_tr, ytr, L_te[q_idx], yte[q_idx]))

    # --- Trans2Vec: 4 biến thể × seed
    joi_model = None
    for seed in SEEDS:
        vecs = {}
        for mode in ["it", "fi", "joi"]:
            model, Ztr, Zte, tm = V.trans2vec(mode, 128, seed)
            vecs[mode] = (Ztr, Zte)
            name = {"it": "TRANS-IT", "fi": "TRANS-FI", "joi": "Trans2Vec-JOI"}[mode]
            record("E1", name, "word", 50, 128, seed, t2v.classify(Ztr, ytr, Zte, yte), **tm)
            if mode == "joi" and seed == SEEDS[0]:
                joi_model = model
                record("E1", name, "word", 50, 128, seed, t2v.classify(Ztr, ytr, Zte, yte, "lr"), "lr")
            if seed == SEEDS[0]:
                record_ret("E1", name, "word", "doc", t2v.retrieval(Ztr, ytr, Zte[q_idx], yte[q_idx]))
        Ztr = t2v.l2(vecs["it"][0] + vecs["fi"][0])
        Zte = t2v.l2(vecs["it"][1] + vecs["fi"][1])
        record("E1", "Trans2Vec-IND", "word", 50, 128, seed, t2v.classify(Ztr, ytr, Zte, yte))
        if seed == SEEDS[0]:
            record_ret("E1", "Trans2Vec-IND", "word", "doc", t2v.retrieval(Ztr, ytr, Zte[q_idx], yte[q_idx]))
            joi_tr, joi_te = vecs["joi"]
            it_model_vecs = vecs["it"]

    # --- A5: JOI ⊕ TF-IDF (bổ sung tần suất, giải H1)
    Xtr = sparse.hstack([tfidf_tr, sparse.csr_matrix(joi_tr)]).tocsr()
    Xte = sparse.hstack([tfidf_te, sparse.csr_matrix(joi_te)]).tocsr()
    record("E1", "JOI ⊕ TF-IDF (A5)", "word", 50, 128, 1, t2v.classify(Xtr, ytr, Xte, yte))

    # --- A3: chỉ tập phổ biến đóng
    closed = t2v.closed_only(V.fis)
    _, Ztr, Zte, tm = V.trans2vec("joi", 128, 1, fis_override=closed)
    record("E1", "JOI – FI đóng (A3)", "word", 50, 128, 1, t2v.classify(Ztr, ytr, Zte, yte), n_fi=len(closed), **tm)

    # --- A6: truy vấn từ khóa ngắn (3 item)
    T_q, F_q = short_queries(V)
    has_fi = np.array([any(len(x) > 1 for x in f) for f in F_q])
    yq = yte[q_idx]
    from sklearn.feature_extraction.text import TfidfVectorizer
    vec = TfidfVectorizer(analyzer=lambda x: x, vocabulary=sorted(V.vocab.idf)).fit([[t for t in d if t in V.vocab.idf] for d in V.tr_docs])
    Q = vec.transform([list(T) for T in T_q])
    for subset, mask in [("tất cả", np.ones(len(yq), bool)), ("có FI", has_fi), ("không FI", ~has_fi)]:
        if mask.sum() == 0:
            continue
        record_ret("E1", "TF-IDF (toàn văn)", "word", f"3 từ khóa – {subset}", t2v.retrieval(tfidf_tr, ytr, Q[mask], yq[mask]), n_q=int(mask.sum()))
        Zq = t2v.infer(joi_model, t2v.pattern_tokens(T_q, F_q, "joi"), epochs=EPOCHS)
        record_ret("E1", "Trans2Vec-JOI", "word", f"3 từ khóa – {subset}", t2v.retrieval(joi_tr, ytr, Zq[mask], yq[mask]), n_q=int(mask.sum()))

    # --- Diễn giải (M6): FI có tích vô hướng lớn nhất với tâm chuyên mục trong mô hình JOI
    out = ["# FI đặc trưng cho từng chuyên mục (mô hình Trans2Vec-JOI, word, k=50)\n"]
    kv = joi_model.syn1neg
    fi_keys = [w for w in joi_model.wv.index_to_key if t2v.FI_SEP in w]
    fi_vecs = np.vstack([kv[joi_model.wv.key_to_index[w]] for w in fi_keys])
    for c in sorted(set(ytr)):
        centroid = joi_tr[ytr == c].mean(axis=0)
        top = np.argsort(-(fi_vecs @ centroid))[:10]
        out.append(f"- **{c}**: " + ", ".join("{" + fi_keys[i].replace(t2v.FI_SEP, ", ") + "}" for i in top))
    (OUT / "category_fis.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    log("Đã ghi category_fis.md")

# ================================================================= E2: A1 âm tiết
if "E2" in args.only:
    log("=== E2 (A1): âm tiết, k=50, d=128")
    S = View("syl", 50)
    json.dump(S.stats, open(OUT / "stats_syl_k50.json", "w"), ensure_ascii=False, indent=1)
    Xtr, Xte = tfidf(S, full=True)
    record("E2", "TF-IDF (toàn văn)", "syl", "full", Xtr.shape[1], 0, t2v.classify(Xtr, ytr, Xte, yte))
    record_ret("E2", "TF-IDF (toàn văn)", "syl", "doc", t2v.retrieval(Xtr, ytr, Xte[q_idx], yte[q_idx]))
    for mode, name in [("it", "TRANS-IT"), ("fi", "TRANS-FI"), ("joi", "Trans2Vec-JOI")]:
        _, Ztr, Zte, tm = S.trans2vec(mode, 128, 1)
        record("E2", name, "syl", 50, 128, 1, t2v.classify(Ztr, ytr, Zte, yte), **tm)
        record_ret("E2", name, "syl", "doc", t2v.retrieval(Ztr, ytr, Zte[q_idx], yte[q_idx]))
    # FI 2 âm tiết là từ ghép có trong tập từ của pyvi?
    word_vocab = set(t2v.Vocab([r["word"].split() for r in train_rows]).idf)
    pairs = [t for t in S.fis if len(t) == 2]
    as_word = sum(("_".join(p) in word_vocab or "_".join(p[::-1]) in word_vocab) for p in pairs)
    append("syllable_fi_words.csv", {"n_pair_fi": len(pairs), "is_pyvi_word": as_word,
                                     "ratio": as_word / max(len(pairs), 1)})
    log(f"FI 2 âm tiết trùng một từ của pyvi: {as_word}/{len(pairs)}")

# ================================================================= E3: A2 k
if "E3" in args.only:
    for k in ([20] if args.quick else [20, 100]):
        log(f"=== E3 (A2): word, k={k}")
        Vk = View("word", k)
        json.dump(Vk.stats, open(OUT / f"stats_word_k{k}.json", "w"), ensure_ascii=False, indent=1)
        for mode, name in [("it", "TRANS-IT"), ("joi", "Trans2Vec-JOI")]:
            _, Ztr, Zte, tm = Vk.trans2vec(mode, 128, 1)
            record("E3", name, "word", k, 128, 1, t2v.classify(Ztr, ytr, Zte, yte),
                   n_fi=Vk.stats["n_fi"], mine_s=Vk.mine_s, **tm)

# ================================================================= E4: A4 d
if "E4" in args.only:
    V4 = V if "E1" in args.only else View("word", 50)
    for d in ([64] if args.quick else [64, 256]):
        log(f"=== E4 (A4): word, k=50, d={d}")
        _, Ztr, Zte, tm = V4.trans2vec("joi", d, 1)
        record("E4", "Trans2Vec-JOI", "word", 50, d, 1, t2v.classify(Ztr, ytr, Zte, yte), **tm)

log("=== XONG")
