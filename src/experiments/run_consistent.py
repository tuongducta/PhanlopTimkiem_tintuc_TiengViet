"""Bước 2c — E6: vector train và test sinh bằng CÙNG một quy trình.

Phát hiện ở E5: với vector train lấy từ model.dv (học cùng mô hình) còn vector test sinh bằng
infer_vector, CV trên train chọn C rất lớn (10–100) nhưng điểm test lại giảm → hai tập vector có
phân phối khác nhau. E6 suy luận lại vector train bằng infer_vector (như test), rồi đánh giá
phân loại (SVM C=1 như [13], LR C=1, và C chọn bằng CV) và tìm kiếm.

Chạy:  .venv-exp/bin/python src/experiments/run_consistent.py
"""
import sys
import time

sys.argv = [sys.argv[0], "--only", "NONE"]  # chỉ nạp dữ liệu + hàm của run_experiments
import run_experiments as R  # noqa: E402
import t2v  # noqa: E402
from run_tuned import tuned_rows  # noqa: E402


def run(V, mode, name, k):
    T_tr = t2v.pattern_tokens(V.T_tr, V.F_tr, mode)
    T_te = t2v.pattern_tokens(V.T_te, V.F_te, mode)
    model, _ = t2v.train_pvdbow(T_tr, 128, 1, epochs=R.EPOCHS)
    t0 = time.time()
    Ztr = t2v.l2(t2v.infer(model, T_tr, epochs=R.EPOCHS))  # suy luận lại train, giống hệt test
    Zte = t2v.l2(t2v.infer(model, T_te, epochs=R.EPOCHS))
    tm = {"infer_s": time.time() - t0}
    label = f"{name} (train suy luận lại)"
    for clf in ["svm", "lr"]:
        R.record("E6", label, V.view, k, 128, 1, t2v.classify(Ztr, R.ytr, Zte, R.yte, clf), clf, **tm)
    for row in tuned_rows(Ztr, Zte):
        R.record("E6", label, V.view, k, 128, 1, row[1], row[0], best_C=row[2])
    R.record_ret("E6", label, V.view, "doc", t2v.retrieval(Ztr, R.ytr, Zte[R.q_idx], R.yte[R.q_idx]))


if __name__ == "__main__":
    R.log("=== E6: vector train suy luận lại (nhất quán với test)")
    for view, k in [("word", 50), ("word", 100), ("syl", 50)]:
        V = R.View(view, k)
        for mode, name in [("it", "TRANS-IT"), ("fi", "TRANS-FI"), ("joi", "Trans2Vec-JOI")]:
            if (view, k) == ("word", 100) and mode == "fi":
                continue
            run(V, mode, name, k)
    R.log("=== E6 XONG")
