"""Bước 3 — Tổng hợp kết quả: bảng Markdown + biểu đồ PNG trong experiments/results/.

Chạy:  .venv-exp/bin/python src/experiments/make_report.py
"""
import json
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RES = Path(__file__).resolve().parent / "results"
# Bảng màu tham chiếu (dataviz): slot 1–4 + mực chữ, nền trắng cho bản in
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, GRID, MUTED = "#0b0b0b", "#52514e", "#e6e5e0", "#b8b6ad"
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 10, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2})

T2V = {"TRANS-IT", "TRANS-FI", "Trans2Vec-IND", "Trans2Vec-JOI"}


BASE = ["exp", "method", "view", "k", "d", "seed", "clf", "acc", "macro_f1", "fit_s", "predict_s"]
EXTRA_BY_LEN = {  # trường bổ sung theo số cột (xem các lời gọi record() trong run_experiments.py / run_tuned.py)
    11: [], 13: ["train_s", "infer_s"], 14: ["n_fi", "train_s", "infer_s"],
    15: ["n_fi", "mine_s", "train_s", "infer_s"],
}


def load_classification():
    """classification.csv có số cột thay đổi theo loại dòng (tiêu đề chỉ ghi một lần)."""
    import csv
    rows = []
    with open(RES / "classification.csv", encoding="utf-8") as f:
        r = csv.reader(f)
        next(r)
        for vals in r:
            if len(vals) == 12:  # best_C (C tinh chỉnh), infer_s (E6) hoặc repr_s (MLP, LDA)
                extra = "best_C" if "tuned" in vals[6] else ("infer_s" if vals[0] == "E6" else "repr_s")
                names = BASE + [extra]
            else:
                names = BASE + EXTRA_BY_LEN[len(vals)]
            rows.append(dict(zip(names, vals)))
    df = pd.DataFrame(rows)
    for c in df.columns:
        if c not in {"exp", "method", "view", "clf", "k"}:
            df[c] = pd.to_numeric(df[c])
    return df


def load_retrieval():
    import csv
    with open(RES / "retrieval.csv", encoding="utf-8") as f:
        r = csv.reader(f)
        head = next(r)
        rows = [dict(zip(head + ["n_q"], v)) for v in r]
    df = pd.DataFrame(rows)
    for c in ["p@10", "map@100", "ndcg@10"]:
        df[c] = pd.to_numeric(df[c])
    df["n_q"] = df.get("n_q", pd.Series(dtype=str)).fillna("")
    return df


def fmt(m, s, n):
    return f"{m:.4f}" if n == 1 or pd.isna(s) else f"{m:.4f} ± {s:.4f}"


def agg(df, keys):
    g = df.groupby(keys, sort=False)
    out = g.agg(acc=("acc", "mean"), acc_sd=("acc", "std"), f1=("macro_f1", "mean"),
                f1_sd=("macro_f1", "std"), n=("seed", "count")).reset_index()
    out["Accuracy"] = [fmt(a, s, n) for a, s, n in zip(out.acc, out.acc_sd, out.n)]
    out["Macro-F1"] = [fmt(a, s, n) for a, s, n in zip(out.f1, out.f1_sd, out.n)]
    return out


def md(df, cols):
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join("---" for _ in cols) + "|"]
    lines += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for _, r in df.iterrows()]
    return "\n".join(lines)


def main():
    cls = load_classification()
    cls["method"] = cls.method.str.replace("⊕", "+")
    parts = []

    # ---- E1 phân loại
    e1 = cls[(cls.exp == "E1") & (cls.clf == "svm")]
    a = agg(e1, ["method", "k", "d"]).sort_values("f1", ascending=False)
    a["Số seed"] = a.n
    parts.append("## E1 — Phân loại (word, SVM tuyến tính C=1, test 50.373 bài)\n\n" +
                 md(a.rename(columns={"method": "Phương pháp"}), ["Phương pháp", "k", "d", "Accuracy", "Macro-F1", "Số seed"]))
    lr = cls[(cls.exp == "E1") & (cls.clf == "lr")]
    if len(lr):
        parts.append("**Hồi quy logistic (bộ phân loại triển khai):**\n\n" +
                     md(agg(lr, ["method"]).rename(columns={"method": "Phương pháp"}), ["Phương pháp", "Accuracy", "Macro-F1"]))
    tm = e1[e1.method.isin(T2V | {"JOI – FI đóng (A3)"}) & e1.train_s.notna()] if "train_s" in e1 else pd.DataFrame()
    if len(tm):
        t = tm.groupby("method").agg(train=("train_s", "mean"), infer=("infer_s", "mean")).reset_index()
        t["Huấn luyện (s)"] = t.train.round(1)
        t["Suy luận 50.373 bài (s)"] = t.infer.round(1)
        parts.append("**Thời gian (trung bình qua seed):**\n\n" + md(t.rename(columns={"method": "Phương pháp"}),
                                                                    ["Phương pháp", "Huấn luyện (s)", "Suy luận 50.373 bài (s)"]))

    # ---- Ablation
    # ---- E5 / E5z / E6: bộ phân loại và tính nhất quán train–test
    for exp, title in [("E5z", "E5z — C tinh chỉnh + chuẩn hóa z-score (lẫn hai yếu tố, chỉ tham khảo)"),
                       ("E5", "E5 — C tinh chỉnh bằng 3-fold CV trên train (vector train = model.dv)"),
                       ("E6", "E6 — Vector train suy luận lại bằng infer_vector (nhất quán với test)")]:
        e = cls[cls.exp == exp].copy()
        if len(e):
            e["Macro-F1"] = e.macro_f1.map(lambda v: f"{v:.4f}")
            e["Accuracy"] = e.acc.map(lambda v: f"{v:.4f}")
            e["C"] = e.get("best_C", pd.Series(index=e.index, dtype=float)).map(
                lambda v: "" if pd.isna(v) else f"{v:g}")
            e.loc[~e.clf.str.contains("tuned"), "C"] = "1"
            parts.append(f"## {title}\n\n" + md(e.rename(columns={"method": "Phương pháp", "clf": "Bộ phân loại"}),
                                                ["Phương pháp", "view", "k", "Bộ phân loại", "C", "Accuracy", "Macro-F1"]))

    for exp, title in [("E2", "E2 (A1) — Âm tiết, không tách từ"), ("E3", "E3 (A2) — Số item k mỗi bài"),
                       ("E4", "E4 (A4) — Số chiều d")]:
        e = cls[cls.exp == exp]
        if len(e):
            cols = ["Phương pháp", "view", "k", "d", "Accuracy", "Macro-F1"]
            extra = []
            if exp == "E3":
                e = e.copy()
                extra = ["n_fi", "mine_s", "train_s"]
                b = agg(e, ["method", "view", "k", "d"]).merge(
                    e.groupby(["method", "k"])[extra].mean().reset_index(), on=["method", "k"])
                b["mine_s"] = b.mine_s.round(1)
                b["train_s"] = b.train_s.round(1)
                cols += ["n_fi", "mine_s", "train_s"]
            else:
                b = agg(e, ["method", "view", "k", "d"])
            parts.append(f"## {title}\n\n" + md(b.rename(columns={"method": "Phương pháp"}), cols))

    # ---- Tìm kiếm
    ret = load_retrieval()
    for c in ["p@10", "map@100", "ndcg@10"]:
        ret[c] = ret[c].map(lambda v: f"{v:.4f}")
    parts.append("## Tìm kiếm (1.000 truy vấn phân tầng, kho = 33.759 bài train, liên quan = cùng chủ đề)\n\n" +
                 md(ret.rename(columns={"method": "Phương pháp", "query": "Truy vấn"}),
                    ["exp", "Phương pháp", "view", "Truy vấn", "p@10", "map@100", "ndcg@10"] +
                    (["n_q"] if "n_q" in ret else [])))

    # ---- Thống kê FI
    stats = {p.stem: json.load(open(p)) for p in sorted(RES.glob("stats_*.json"))}
    rows = [{"cấu hình": k.replace("stats_", ""), **{kk: v[kk] for kk in
             ["vocab", "stopwords", "delta", "n_fi", "n_fi_len", "mine_s", "fi_per_doc_train", "docs_without_fi2_test"]}}
            for k, v in stats.items()]
    if rows:
        df = pd.DataFrame(rows)
        df["fi_per_doc_train"] = df.fi_per_doc_train.round(1)
        df["docs_without_fi2_test"] = (100 * df.docs_without_fi2_test).round(1).astype(str) + "%"
        parts.append("## Thống kê khai phá tập phổ biến\n\n" + md(df, list(df.columns)))
    sw = RES / "syllable_fi_words.csv"
    if sw.exists():
        s = pd.read_csv(sw).iloc[0]
        parts.append(f"**FI 2 âm tiết trùng một từ ghép của pyvi:** {int(s.is_pyvi_word)}/{int(s.n_pair_fi)} "
                     f"({100 * s.ratio:.1f}%).")
    (RES / "tables.md").write_text("# Bảng kết quả (sinh tự động)\n\n" + "\n\n".join(parts) + "\n", encoding="utf-8")

    # ---- Hình 1: đường cong elbow
    curve = pd.read_csv(RES / "fi_curve.csv").drop_duplicates(["view", "k", "delta"])  # E5 dựng lại View → ghi trùng
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    colors = [BLUE, ORANGE, AQUA, YELLOW]
    for (key, g), col in zip(curve.groupby(["view", "k"], sort=False), colors):
        lab = f"{'từ' if key[0] == 'word' else 'âm tiết'}, k={key[1]}"
        ax.plot(g.delta * 100, g.n_fi_le2, color=col, lw=2, label=lab)
        ch = g[g.chosen]
        ax.plot(ch.delta * 100, ch.n_fi_le2, "o", ms=8, color=col, mec="white", mew=2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Ngưỡng hỗ trợ tối thiểu δ (%)")
    ax.set_ylabel("Số tập phổ biến (độ dài ≤ 2)")
    ax.grid(True, color=GRID, lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9)
    ax.set_title("Đường cong elbow chọn δ (chấm tròn = δ được chọn)", color=INK, fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(RES / "fig_fi_curve.png", dpi=200)

    # ---- Hình 2: Macro-F1 (SVM C=1). Baseline: E1. Trans2Vec: E6 (vector train suy luận lại, nhất quán với
    # test) + một thanh JOI bản model.dv (E1, 3 seed) để thấy hiệu ứng lệch phân phối train/test.
    base = a[~a.method.isin(T2V) & ~a.method.str.contains("JOI")][["method", "f1", "f1_sd"]]
    e6 = cls[(cls.exp == "E6") & (cls.clf == "svm") & (cls.view == "word") & (cls.k == "50")]
    e6 = pd.DataFrame({"method": e6.method.str.replace(" (train suy luận lại)", "", regex=False),
                       "f1": e6.macro_f1, "f1_sd": float("nan")})
    dv = a[a.method == "Trans2Vec-JOI"][["f1", "f1_sd"]].assign(method="Trans2Vec-JOI (model.dv, E1)")
    a = pd.concat([base, e6, dv]).sort_values("f1")
    fig, ax = plt.subplots(figsize=(6.2, 0.32 * len(a) + 0.9))
    cols = [BLUE if (m in T2V or "JOI" in m) else MUTED for m in a.method]
    ax.barh(a.method, a.f1, color=cols, height=0.62, xerr=a.f1_sd.fillna(0), ecolor=INK2, capsize=2)
    for y, (v, sd) in enumerate(zip(a.f1, a.f1_sd.fillna(0))):
        ax.text(v + sd + 0.004, y, f"{v:.3f}", va="center", fontsize=8.5, color=INK)
    lo = max(0, a.f1.min() - 0.08)
    ax.set_xlim(lo, min(1, a.f1.max() + 0.06))
    ax.set_xlabel("Macro-F1 trên tập test VNTC-10")
    ax.grid(True, axis="x", color=GRID, lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title("Macro-F1, SVM C=1 (xanh: Trans2Vec, xám: baseline)", color=INK, fontsize=11, loc="left")
    fig.tight_layout()
    fig.savefig(RES / "fig_macro_f1.png", dpi=200)
    print("Đã ghi tables.md, fig_fi_curve.png, fig_macro_f1.png")


if __name__ == "__main__":
    main()
