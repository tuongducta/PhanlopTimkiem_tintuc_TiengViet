"""Bước 2b — E5: tinh chỉnh bộ phân loại (giải hạn chế H3 của [13]: SVM cố định C = 1).

Với từng biểu diễn chính (word, k = 50, d = 128, seed = 1), chọn C của SVM tuyến tính và của hồi quy
logistic bằng 3-fold cross-validation CHỈ trên tập train, rồi đánh giá một lần trên test.
Vector giữ chuẩn hóa L2 như E1, để chỉ C thay đổi. (Bản đầu dùng z-score — làm kết quả giảm, lẫn với
hiệu ứng của C — được giữ trong classification.csv với nhãn E5z.)

Chạy (sau run_experiments.py):  .venv-exp/bin/python src/experiments/run_tuned.py
"""
import time

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

import sys

sys.argv = [sys.argv[0], "--only", "NONE"]  # chỉ nạp dữ liệu + hàm của run_experiments, không chạy E1–E4
import run_experiments as R  # noqa: E402

GRID = [0.01, 0.1, 1, 10, 100]
CV = StratifiedKFold(3, shuffle=True, random_state=0)


def tuned_rows(Xtr, Xte):
    """[(kind, kết quả, C tốt nhất)] cho SVM và LR với C chọn bằng 3-fold CV trên train."""
    out = []
    for kind, est in [("svm-tuned", LinearSVC(max_iter=10000)), ("lr-tuned", LogisticRegression(max_iter=5000))]:
        t0 = time.time()
        gs = GridSearchCV(est, {"C": GRID}, scoring="f1_macro", cv=CV, n_jobs=6).fit(Xtr, R.ytr)
        pred = gs.predict(Xte)
        out.append((kind, {"acc": accuracy_score(R.yte, pred), "macro_f1": f1_score(R.yte, pred, average="macro"),
                           "fit_s": time.time() - t0, "predict_s": 0.0}, gs.best_params_["C"]))
    return out


def tuned(name, Xtr, Xte, dense, k=50):
    for kind, est in [("svm", LinearSVC(max_iter=10000)), ("lr", LogisticRegression(max_iter=5000))]:
        model, key = est, "C"  # giữ chuẩn hóa L2 như E1 (bản z-score đầu tiên lẫn hai yếu tố, lưu là E5z)
        t0 = time.time()
        gs = GridSearchCV(model, {key: GRID}, scoring="f1_macro", cv=CV, n_jobs=6).fit(Xtr, R.ytr)
        pred = gs.predict(Xte)
        res = {"acc": accuracy_score(R.yte, pred), "macro_f1": f1_score(R.yte, pred, average="macro"),
               "fit_s": time.time() - t0, "predict_s": 0.0}
        R.record("E5", name, "word", k, Xtr.shape[1], 1, res, f"{kind}-tuned", best_C=gs.best_params_[key])


if __name__ == "__main__":
    R.log("=== E5: bộ phân loại tinh chỉnh C bằng CV trên train")
    V = R.View("word", 50)
    Xtr, Xte = R.tfidf(V, full=True)
    tuned("TF-IDF (toàn văn)", Xtr, Xte, dense=False)
    for mode, name in [("it", "TRANS-IT"), ("fi", "TRANS-FI"), ("joi", "Trans2Vec-JOI")]:
        _, Ztr, Zte, _ = V.trans2vec(mode, 128, 1)
        tuned(name, Ztr, Zte, dense=True)
    # k = 100: cấu hình duy nhất mà FI giúp rõ với SVM C=1 — kiểm tra lại khi bộ phân loại đã tinh chỉnh
    V100 = R.View("word", 100)
    for mode, name in [("it", "TRANS-IT"), ("joi", "Trans2Vec-JOI")]:
        _, Ztr, Zte, _ = V100.trans2vec(mode, 128, 1)
        tuned(name, Ztr, Zte, dense=True, k=100)
    R.log("=== E5 XONG")
