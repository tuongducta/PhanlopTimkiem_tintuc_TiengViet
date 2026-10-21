"""A3–A5 (GĐ-H3): khai phá FI, huấn luyện Trans2Vec, LR — đọc transaction TỪ MariaDB và ghi kết quả về MariaDB.

Tái hiện cấu hình E6 (view word, k=50, d=128, seed 1, 20 epoch, vector train suy luận lại như test):
  run 'fim'            δ theo elbow, FI độ dài ≤ 3     → itemset, itemset_item, article_itemset
  run 'trans-it'       PV-DBOW trên item               → article_vector, eval_result (search)
  run 'trans2vec-joi'  PV-DBOW trên item ∪ FI(≥2)      → article_vector, eval_result (search)
  run 'lr'             LR (C=1) trên từng embedding     → prediction (test), eval_result (classify)
  run 'tfidf-lr'       TF-IDF toàn văn + LR (C=10, như E5) → prediction, eval_result
Mô hình lưu ở system/models/ để giao diện suy luận trực tuyến.

Chạy (sau load_articles.py):  .venv-exp/bin/python src/system/pipeline/train_models.py
Chạy lại: xóa các run cũ trước (DELETE FROM model_run; các bảng con xóa theo ON DELETE CASCADE).
"""
import json
import math
import pickle
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]  # gốc dự án (mã ở src/system/<gói>/)
sys.path.insert(0, str(ROOT / "src/system"))
sys.path.insert(0, str(ROOT / "src/experiments"))
import t2v  # noqa: E402
from config import connect_mariadb  # noqa: E402

MODELS = ROOT / "src/system/models"
DELTA_GRID = list(np.round(np.geomspace(0.001, 0.05, 15), 5))  # như run_experiments.py
K, D, SEED, EPOCHS = 50, 128, 1, 20
BATCH = 20000
T0 = time.time()


def log(*a):
    print(f"[{time.time() - T0:6.0f}s]", *a, flush=True)


def new_run(c, kind, params, parent=None):
    c.execute("INSERT INTO model_run (kind, parent_id, params) VALUES (%s,%s,%s)",
              (kind, parent, json.dumps(params, ensure_ascii=False)))
    return c.lastrowid


def insert_many(con, c, sql, rows):
    for i in range(0, len(rows), BATCH):
        c.executemany(sql, rows[i:i + BATCH])
    con.commit()


def wilson_lo(k, n, z=1.96):
    p = k / n
    return (p + z * z / (2 * n) - z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / (1 + z * z / n)


def load(c):
    c.execute("SELECT a.id, a.split, cat.code FROM article a JOIN category cat ON cat.id = a.category_id ORDER BY a.id")
    arts = c.fetchall()
    c.execute("SELECT ai.article_id, i.token FROM article_item ai JOIN item i ON i.id = ai.item_id")
    trans = defaultdict(set)
    for aid, tok in c.fetchall():
        trans[aid].add(tok)
    c.execute("SELECT id, token FROM item")
    item_id = {t: i for i, t in c.fetchall()}
    return arts, {a: frozenset(s) for a, s in trans.items()}, item_id


def evaluate_search(Ztr, ytr, Zte, yte, q_idx):
    return t2v.retrieval(Ztr, ytr, Zte[q_idx], yte[q_idx])


def save_eval(con, c, run_id, task, res, config=""):
    rows = [(run_id, task, m, config, float(v)) for m, v in res.items()]
    c.executemany("INSERT INTO eval_result (run_id, task, metric, config, value) VALUES (%s,%s,%s,%s,%s)", rows)
    con.commit()


def classify_and_store(con, c, parent, kind, params, clf, Xtr, ytr, Xte, yte, te_ids, cat_id):
    from sklearn.metrics import accuracy_score, f1_score

    run = new_run(c, kind, params, parent)
    t0 = time.time()
    clf.fit(Xtr, ytr)
    fit_s = time.time() - t0
    P = clf.predict_proba(Xte)
    pred = clf.classes_[P.argmax(1)]
    res = {"acc": accuracy_score(yte, pred), "macro_f1": f1_score(yte, pred, average="macro"), "fit_s": fit_s}
    save_eval(con, c, run, "classify", res)
    rows = [(aid, run, cat_id[p], json.dumps({l: round(float(x), 4) for l, x in zip(clf.classes_, pr)}))
            for aid, p, pr in zip(te_ids, pred, P)]
    insert_many(con, c, "INSERT INTO prediction (article_id, run_id, pred_category_id, proba) VALUES (%s,%s,%s,%s)", rows)
    c.execute("UPDATE model_run SET metrics = %s WHERE id = %s", (json.dumps(res), run))
    con.commit()
    return run, res


def main():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression

    MODELS.mkdir(exist_ok=True)
    con = connect_mariadb()
    c = con.cursor()
    c.execute("SELECT COUNT(*) FROM model_run")
    if c.fetchone()[0]:
        sys.exit("model_run không rỗng: DELETE FROM model_run trước khi chạy lại.")
    arts, trans, item_id = load(c)
    c.execute("SELECT code, id FROM category")
    cat_id = dict(c.fetchall())
    tr = [a for a in arts if a[1] == "train"]
    te = [a for a in arts if a[1] == "test"]
    T_tr = [trans.get(a[0], frozenset()) for a in tr]
    T_te = [trans.get(a[0], frozenset()) for a in te]
    ytr = np.array([a[2] for a in tr])
    yte = np.array([a[2] for a in te])
    te_ids = [a[0] for a in te]
    # Truy vấn tìm kiếm như run_experiments.py: 100 bài test mỗi chủ đề, kho = train
    rng = np.random.default_rng(0)
    q_idx = np.concatenate([rng.choice(np.where(yte == l)[0], min(100, (yte == l).sum()), replace=False)
                            for l in sorted(set(yte))])
    log(f"đọc từ MariaDB: train={len(tr)} test={len(te)}, {sum(map(len, T_tr)) + sum(map(len, T_te))} item")

    # ---------------- A3: khai phá FI
    t0 = time.time()
    delta, curve = t2v.choose_delta(T_tr, DELTA_GRID)
    fis = t2v.mine_fi(T_tr, delta)
    mine_s = time.time() - t0
    closed = set(t2v.closed_only(fis))
    n = len(T_tr)
    by_len = Counter(len(f) for f in fis)
    fim = new_run(c, "fim", {"view": "word", "k": K, "delta_grid": [float(x) for x in DELTA_GRID],
                             "delta": float(delta), "max_len": 3, "n_train": n})
    c.execute("UPDATE model_run SET metrics = %s WHERE id = %s",
              (json.dumps({"n_fi": len(fis), "n_fi_len": dict(sorted(by_len.items())), "n_closed": len(closed),
                           "mine_s": round(mine_s, 2), "curve": [[float(d), k] for d, k in curve]}), fim))
    fi_list = sorted(fis, key=lambda f: (len(f), f))
    c.executemany("INSERT INTO itemset (run_id, size, support, is_closed, wilson_lo, label) VALUES (%s,%s,%s,%s,%s,%s)",
                  [(fim, len(f), fis[f], f in closed, wilson_lo(fis[f], n), t2v.fi_token(f)) for f in fi_list])
    c.execute("SELECT label, id FROM itemset WHERE run_id = %s", (fim,))
    fi_id = dict(c.fetchall())
    insert_many(con, c, "INSERT INTO itemset_item (itemset_id, item_id) VALUES (%s,%s)",
                [(fi_id[t2v.fi_token(f)], item_id[t]) for f in fi_list for t in f])
    F_tr, F_te = t2v.match_fi(T_tr, fis), t2v.match_fi(T_te, fis)
    rows = [(a[0], fi_id[t2v.fi_token(f)]) for a, F in zip(tr + te, F_tr + F_te) for f in F]
    insert_many(con, c, "INSERT INTO article_itemset (article_id, itemset_id) VALUES (%s,%s)", rows)
    with open(MODELS / f"run{fim}_fim.pkl", "wb") as f:
        pickle.dump({"fis": fis, "delta": delta}, f)
    log(f"FIM run {fim}: δ={delta}, {len(fis)} FI {dict(by_len)}, {len(closed)} đóng, {mine_s:.1f}s; "
        f"{len(rows)} dòng article_itemset")

    # ---------------- A4–A5: Trans2Vec + LR
    results = {}
    for mode, kind in [("it", "trans-it"), ("joi", "trans2vec-joi")]:
        t0 = time.time()
        P_tr, P_te = t2v.pattern_tokens(T_tr, F_tr, mode), t2v.pattern_tokens(T_te, F_te, mode)
        model, _ = t2v.train_pvdbow(P_tr, D, SEED, epochs=EPOCHS)
        train_s = time.time() - t0
        Ztr = t2v.l2(t2v.infer(model, P_tr, epochs=EPOCHS))  # train suy luận lại như test (E6)
        Zte = t2v.l2(t2v.infer(model, P_te, epochs=EPOCHS))
        infer_s = time.time() - t0 - train_s
        emb = new_run(c, kind, {"mode": mode, "d": D, "seed": SEED, "epochs": EPOCHS, "k": K,
                                "train_vectors": "infer_vector", "model_file": f"run{{id}}_{mode}.model"}, fim)
        model.save(str(MODELS / f"run{emb}_{mode}.model"))
        c.execute("UPDATE model_run SET params = JSON_SET(params, '$.model_file', %s),"
                  " metrics = %s WHERE id = %s",
                  (f"run{emb}_{mode}.model", json.dumps({"train_s": train_s, "infer_s": infer_s}), emb))
        ids = [a[0] for a in tr] + te_ids
        Z = np.vstack([Ztr, Zte]).astype("<f4")
        insert_many(con, c, "INSERT INTO article_vector (article_id, run_id, vec) VALUES (%s,%s,%s)",
                    [(aid, emb, z.tobytes()) for aid, z in zip(ids, Z)])
        ret = evaluate_search(Ztr, ytr, Zte, yte, q_idx)
        save_eval(con, c, emb, "search", ret, "cosine-exact")
        lr = LogisticRegression(max_iter=3000)
        run, res = classify_and_store(con, c, emb, "lr", {"C": 1.0, "input_run": emb}, lr,
                                      Ztr, ytr, Zte, yte, te_ids, cat_id)
        with open(MODELS / f"run{run}_lr.pkl", "wb") as f:
            pickle.dump(lr, f)
        results[kind] = {**res, **ret}
        log(f"{kind}: emb run {emb}, lr run {run}: acc={res['acc']:.4f} macroF1={res['macro_f1']:.4f} "
            f"nDCG@10={ret['ndcg@10']:.4f} (train {train_s:.0f}s, infer {infer_s:.0f}s)")

    # ---------------- baseline TF-IDF toàn văn
    c.execute("SELECT token FROM item WHERE idf IS NOT NULL ORDER BY token")
    vocab = [r[0] for r in c.fetchall()]
    c.execute("SELECT body_seg FROM article ORDER BY id")
    seg = [r[0] for r in c.fetchall()]
    split = [a[1] for a in arts]
    vec = TfidfVectorizer(analyzer=str.split, vocabulary=vocab)
    Xtr = vec.fit_transform([s for s, sp in zip(seg, split) if sp == "train"])
    Xte = vec.transform([s for s, sp in zip(seg, split) if sp == "test"])
    tf_run = new_run(c, "tfidf", {"vocab": len(vocab), "source": "body_seg, từ vựng item.idf"}, None)
    ret = evaluate_search(Xtr, ytr, Xte, yte, q_idx)
    save_eval(con, c, tf_run, "search", ret, "cosine-exact")
    lr = LogisticRegression(C=10.0, max_iter=3000)
    run, res = classify_and_store(con, c, tf_run, "lr", {"C": 10.0, "input_run": tf_run}, lr,
                                  Xtr, ytr, Xte, yte, te_ids, cat_id)
    with open(MODELS / f"run{tf_run}_tfidf.pkl", "wb") as f:
        pickle.dump(vec, f)
    with open(MODELS / f"run{run}_lr.pkl", "wb") as f:
        pickle.dump(lr, f)
    results["tfidf"] = {**res, **ret}
    log(f"tfidf: run {tf_run}, lr run {run}: acc={res['acc']:.4f} macroF1={res['macro_f1']:.4f} "
        f"nDCG@10={ret['ndcg@10']:.4f}")
    c.execute("ANALYZE TABLE itemset, itemset_item, article_itemset, article_vector, prediction")
    c.fetchall()
    con.close()
    log("XONG", json.dumps(results, default=float))


if __name__ == "__main__":
    main()
