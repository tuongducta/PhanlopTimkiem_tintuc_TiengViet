"""Mục 17 (21/10): bổ sung mốc Trans2Vec gốc, TRANS-FI, Trans2Vec-IND và một mô hình cải tiến — chạy THÊM trên CSDL
đã có (sau train_models.py), không đụng các run cũ.

  run 'trans2vec-orig'   mã tác giả sources/repos/Trans2Vec/codes/trans2vec_joi_classify.py:
                         đầu vào Items-FIs (item + MỌI FI, kể cả FI 1 phần tử, FI là token riêng), PV-DBOW d=128,
                         50 epoch, min_count=0, tham số còn lại mặc định; học transductive trên toàn bộ bài (không nhãn),
                         vector = model.dv; LinearSVC() C=1, không chuẩn hóa                → con 'svm'
  run 'trans-fi'         PV-DBOW trên token FI (E6: 20 epoch, train suy luận lại)          → con 'lr'
  run 'trans2vec-ind'    l2((IT + FI) / 2), IT và FI đã chuẩn hóa (survey 05_trans2vec.md)  → con 'lr'
  run 'trans2vec-cat' hoặc 'trans2vec-stack' — mô hình cải tiến, chọn bằng 3-fold CV trên train (không nhìn test):
      C1 cat    [IT ‖ FI ‖ JOI] (384 chiều) → LR C=1
      C2 stack  xác suất out-of-fold của LR trên IT, FI, IND, JOI (40 cột) → LR meta
Khác mã gốc ở chỗ bắt buộc: FI lấy từ run fim của hệ thống (FIM_Trans.exe chỉ chạy trên Windows), gensim 4.4,
chia train/test gốc của VNTC, LinearSVC max_iter=10000 (mặc định 1000 không hội tụ, như E7).

Chạy (sau train_models.py):  .venv-exp/bin/python src/system/pipeline/train_variants.py
"""
import json
import pickle
import time

import numpy as np

from train_models import (EPOCHS, MODELS, SEED, D, K, classify_and_store, connect_mariadb, evaluate_search,
                          insert_many, load, log, new_run, save_eval, t2v)

ORIG_EPOCHS = 50
FI_PREFIX = "fi:"  # mã gốc ghi FI thành mã số riêng, không trùng item; FI 1 phần tử cũng là token riêng


def orig_tokens(T, F):
    return sorted(T) + [FI_PREFIX + t2v.fi_token(f) for f in sorted(F, key=lambda f: (len(f), f))]


def softmax(S):
    E = np.exp(S - S.max(1, keepdims=True))
    return E / E.sum(1, keepdims=True)


def load_vectors(c, run, ids):
    c.execute("SELECT article_id, vec FROM article_vector WHERE run_id = %s", (run,))
    d = {a: np.frombuffer(b, dtype="<f4") for a, b in c.fetchall()}
    return np.vstack([d[i] for i in ids])


def store_vectors(con, c, run, ids, Z):
    insert_many(con, c, "INSERT INTO article_vector (article_id, run_id, vec) VALUES (%s,%s,%s)",
                [(a, run, z.astype("<f4").tobytes()) for a, z in zip(ids, Z)])


def latest(c, kind):
    c.execute("SELECT MAX(id) FROM model_run WHERE kind = %s", (kind,))
    return c.fetchone()[0]


def lr_of(c, emb):
    c.execute("SELECT MAX(id) FROM model_run WHERE kind = 'lr' AND parent_id = %s", (emb,))
    return c.fetchone()[0]


def main():
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, f1_score
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.svm import LinearSVC

    con = connect_mariadb()
    c = con.cursor()
    # Chạy tiếp được: bước nào đã có run thì dùng lại; riêng mô hình cải tiến phải xóa trước khi chạy lại
    for kind in ["trans2vec-cat", "trans2vec-stack"]:
        if latest(c, kind):
            raise SystemExit(f"đã có run '{kind}': DELETE FROM model_run WHERE kind IN (…) trước khi chạy lại.")
    arts, trans, _ = load(c)
    c.execute("SELECT code, id FROM category")
    cat_id = dict(c.fetchall())
    tr = [a for a in arts if a[1] == "train"]
    te = [a for a in arts if a[1] == "test"]
    tr_ids, te_ids = [a[0] for a in tr], [a[0] for a in te]
    T_tr = [trans.get(i, frozenset()) for i in tr_ids]
    T_te = [trans.get(i, frozenset()) for i in te_ids]
    ytr, yte = np.array([a[2] for a in tr]), np.array([a[2] for a in te])
    rng = np.random.default_rng(0)
    q_idx = np.concatenate([rng.choice(np.where(yte == l)[0], min(100, (yte == l).sum()), replace=False)
                            for l in sorted(set(yte))])
    fim, it_run, joi_run = latest(c, "fim"), latest(c, "trans-it"), latest(c, "trans2vec-joi")
    with open(MODELS / f"run{fim}_fim.pkl", "rb") as f:
        fis = pickle.load(f)["fis"]
    F_tr, F_te = t2v.match_fi(T_tr, fis), t2v.match_fi(T_te, fis)
    log(f"fim run {fim} ({len(fis)} FI), trans-it run {it_run}, joi run {joi_run}")
    results = {}

    # ---------------- mốc: Trans2Vec gốc (mã tác giả)
    if latest(c, "trans2vec-orig"):
        log(f"trans2vec-orig: dùng lại run {latest(c, 'trans2vec-orig')}")
    else:
        from gensim.models.doc2vec import Doc2Vec, TaggedDocument

        t0 = time.time()
        docs = [TaggedDocument(orig_tokens(T, F), [i]) for i, (T, F) in enumerate(zip(T_tr + T_te, F_tr + F_te))]
        model = Doc2Vec(dm=0, vector_size=D, min_count=0, epochs=ORIG_EPOCHS, workers=8, seed=SEED)
        model.build_vocab(docs)
        model.train(docs, total_examples=model.corpus_count, epochs=model.epochs)
        V = np.vstack([model.dv[i] for i in range(len(docs))])
        train_s = time.time() - t0
        orig = new_run(c, "trans2vec-orig", {
            "source": "sources/repos/Trans2Vec/codes/trans2vec_joi_classify.py", "input": "items + all FI (Items-FIs)",
            "d": D, "epochs": ORIG_EPOCHS, "min_count": 0, "seed": SEED, "protocol": "transductive (train+test, không nhãn)",
            "train_vectors": "model.dv", "normalize": False, "model_file": "", "fim_run": fim}, fim)
        model.save(str(MODELS / f"run{orig}_orig.model"))
        c.execute("UPDATE model_run SET params = JSON_SET(params, '$.model_file', %s), metrics = %s WHERE id = %s",
                  (f"run{orig}_orig.model", json.dumps({"train_s": train_s}), orig))
        Vtr, Vte = V[:len(tr)], V[len(tr):]
        store_vectors(con, c, orig, tr_ids + te_ids, V)
        save_eval(con, c, orig, "search", evaluate_search(t2v.l2(Vtr), ytr, t2v.l2(Vte), yte, q_idx), "cosine-exact")
        svm = LinearSVC(max_iter=10000)
        run = new_run(c, "svm", {"C": 1.0, "input_run": orig, "proba": "softmax(decision_function)"}, orig)
        t0 = time.time()
        svm.fit(Vtr, ytr)
        fit_s = time.time() - t0
        P = softmax(svm.decision_function(Vte))
        pred = svm.classes_[P.argmax(1)]
        res = {"acc": accuracy_score(yte, pred), "macro_f1": f1_score(yte, pred, average="macro"), "fit_s": fit_s}
        save_eval(con, c, run, "classify", res)
        insert_many(con, c, "INSERT INTO prediction (article_id, run_id, pred_category_id, proba) VALUES (%s,%s,%s,%s)",
                    [(a, run, cat_id[p], json.dumps({l: round(float(x), 4) for l, x in zip(svm.classes_, pr)}))
                     for a, p, pr in zip(te_ids, pred, P)])
        c.execute("UPDATE model_run SET metrics = %s WHERE id = %s", (json.dumps(res), run))
        con.commit()
        with open(MODELS / f"run{run}_svm.pkl", "wb") as f:
            pickle.dump(svm, f)
        results["trans2vec-orig"] = res
        log(f"trans2vec-orig: emb {orig}, svm {run}: macroF1={res['macro_f1']:.4f} (train {train_s:.0f}s)")

    # ---------------- TRANS-FI (cấu hình E6)
    fi_run = latest(c, "trans-fi")
    if fi_run:
        FItr, FIte = load_vectors(c, fi_run, tr_ids), load_vectors(c, fi_run, te_ids)
        log(f"trans-fi: dùng lại run {fi_run}")
    else:
        t0 = time.time()
        P_tr, P_te = t2v.pattern_tokens(T_tr, F_tr, "fi"), t2v.pattern_tokens(T_te, F_te, "fi")
        model, _ = t2v.train_pvdbow(P_tr, D, SEED, epochs=EPOCHS)
        train_s = time.time() - t0
        FItr, FIte = t2v.l2(t2v.infer(model, P_tr, epochs=EPOCHS)), t2v.l2(t2v.infer(model, P_te, epochs=EPOCHS))
        fi_run = new_run(c, "trans-fi", {"mode": "fi", "d": D, "seed": SEED, "epochs": EPOCHS, "k": K,
                                         "train_vectors": "infer_vector", "model_file": ""}, fim)
        model.save(str(MODELS / f"run{fi_run}_fi.model"))
        c.execute("UPDATE model_run SET params = JSON_SET(params, '$.model_file', %s), metrics = %s WHERE id = %s",
                  (f"run{fi_run}_fi.model", json.dumps({"train_s": train_s, "infer_s": time.time() - t0 - train_s}), fi_run))
        log(f"trans-fi: emb {fi_run} ({time.time() - t0:.0f}s)")

    ITtr, ITte = load_vectors(c, it_run, tr_ids), load_vectors(c, it_run, te_ids)
    JOtr, JOte = load_vectors(c, joi_run, tr_ids), load_vectors(c, joi_run, te_ids)
    INtr, INte = t2v.l2((ITtr + FItr) / 2), t2v.l2((ITte + FIte) / 2)
    ind_run = latest(c, "trans2vec-ind")
    lrs = {"trans-fi": lr_of(c, fi_run)} if lr_of(c, fi_run) else {}
    todo = [] if lrs else [(fi_run, "trans-fi", FItr, FIte)]
    if ind_run:
        lrs["trans2vec-ind"] = lr_of(c, ind_run)
    else:
        ind_run = new_run(c, "trans2vec-ind", {"formula": "l2((IT + FI) / 2)", "inputs": [it_run, fi_run]}, fim)
        todo.append((ind_run, "trans2vec-ind", INtr, INte))
    for emb, name, Ztr, Zte in todo:
        store_vectors(con, c, emb, tr_ids + te_ids, np.vstack([Ztr, Zte]))
        ret = evaluate_search(Ztr, ytr, Zte, yte, q_idx)
        save_eval(con, c, emb, "search", ret, "cosine-exact")
        lr = LogisticRegression(max_iter=3000)
        run, res = classify_and_store(con, c, emb, "lr", {"C": 1.0, "input_run": emb}, lr, Ztr, ytr, Zte, yte,
                                      te_ids, cat_id)
        with open(MODELS / f"run{run}_lr.pkl", "wb") as f:
            pickle.dump(lr, f)
        lrs[name] = run
        results[name] = {**res, **ret}
        log(f"{name}: emb {emb}, lr {run}: macroF1={res['macro_f1']:.4f} nDCG@10={ret['ndcg@10']:.4f}")

    # ---------------- mô hình cải tiến: chọn giữa C1 (cat) và C2 (stack) bằng 3-fold CV trên train
    cv = StratifiedKFold(3, shuffle=True, random_state=0)
    blocks = {"trans-it": (ITtr, ITte), "trans-fi": (FItr, FIte), "trans2vec-ind": (INtr, INte),
              "trans2vec-joi": (JOtr, JOte)}
    t0 = time.time()
    CATtr, CATte = np.hstack([ITtr, FItr, JOtr]), np.hstack([ITte, FIte, JOte])
    cv_cat = f1_score(ytr, cross_val_predict(LogisticRegression(max_iter=3000), CATtr, ytr, cv=cv, n_jobs=3),
                      average="macro")
    OOF = np.hstack([cross_val_predict(LogisticRegression(max_iter=3000), Ztr, ytr, cv=cv, n_jobs=3,
                                       method="predict_proba") for Ztr, _ in blocks.values()])
    # Macro-F1 CV của stack: LR meta đánh giá chéo trên chính xác suất OOF (cùng các fold)
    cv_stack = f1_score(ytr, cross_val_predict(LogisticRegression(max_iter=3000), OOF, ytr, cv=cv), average="macro")
    cv_single = {n: f1_score(ytr, cross_val_predict(LogisticRegression(max_iter=3000), Ztr, ytr, cv=cv, n_jobs=3),
                             average="macro") for n, (Ztr, _) in blocks.items()}
    log(f"CV train macro-F1: cat={cv_cat:.4f} stack={cv_stack:.4f} đơn={ {k: round(v, 4) for k, v in cv_single.items()} } "
        f"({time.time() - t0:.0f}s)")
    choice = "cat" if cv_cat >= cv_stack else "stack"
    cv_info = {"cv_macro_f1": {"cat": cv_cat, "stack": cv_stack, **cv_single}, "chosen": choice, "folds": 3}
    base_lr = {"trans-it": lr_of(c, it_run), "trans-fi": lrs["trans-fi"], "trans2vec-ind": lrs["trans2vec-ind"],
               "trans2vec-joi": lr_of(c, joi_run)}
    if choice == "cat":
        emb = new_run(c, "trans2vec-cat", {"inputs": {"trans-it": it_run, "trans-fi": fi_run, "trans2vec-joi": joi_run},
                                           "formula": "[IT ‖ FI ‖ JOI] → LR", **cv_info}, fim)
        # 384 chiều không vừa cột VECTOR(128) → không lưu article_vector; đánh giá tìm kiếm trong bộ nhớ
        Z = np.vstack([CATtr, CATte]) / np.sqrt(3)  # chuẩn L2 = 1 cho tìm kiếm cosine
        save_eval(con, c, emb, "search", evaluate_search(Z[:len(tr)], ytr, Z[len(tr):], yte, q_idx), "cosine-exact")
        lr = LogisticRegression(max_iter=3000)
        run, res = classify_and_store(con, c, emb, "lr", {"C": 1.0, "input_run": emb}, lr, CATtr, ytr, CATte, yte,
                                      te_ids, cat_id)
    else:
        emb = new_run(c, "trans2vec-stack", {"inputs": base_lr, "formula": "proba(IT, FI, IND, JOI) → LR meta",
                                             **cv_info}, fim)
        TEST = np.hstack([pickle.load(open(MODELS / f"run{base_lr[n]}_lr.pkl", "rb")).predict_proba(Zte)
                          for n, (_, Zte) in blocks.items()])
        lr = LogisticRegression(max_iter=3000)
        run, res = classify_and_store(con, c, emb, "lr", {"C": 1.0, "input_run": emb, "meta": True}, lr,
                                      OOF, ytr, TEST, yte, te_ids, cat_id)
    with open(MODELS / f"run{run}_lr.pkl", "wb") as f:
        pickle.dump(lr, f)
    results[f"trans2vec-{choice}"] = res
    log(f"cải tiến = {choice}: emb {emb}, lr {run}: macroF1={res['macro_f1']:.4f}")
    c.execute("ANALYZE TABLE article_vector, prediction")
    c.fetchall()
    con.close()
    log("XONG", json.dumps(results, default=float))


if __name__ == "__main__":
    main()
