"""Hình cho báo cáo môn Hệ CSDL nâng cao: sơ đồ kiến trúc, sơ đồ ER, biểu đồ E-DB1/2/4/5.

Số liệu benchmark đọc từ system/bench/results/*.json; ảnh giao diện chụp sẵn đặt trong report_db/figures/.
Chạy:  .venv-exp/bin/python livrables/report_db/make_figures.py
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[2]  # gốc dự án (file ở livrables/report_db/)
RES = ROOT / "src/system/bench/results"
FIG = Path(__file__).resolve().parent / "figures"
# Cùng bảng màu với experiments/make_report.py (đã kiểm tra bằng validate_palette của dataviz)
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, MUTED = "#0b0b0b", "#52514e", "#e6e5e0", "#b8b6ad"
NAVY, PALE = "#1F3864", "#EEF3FB"
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 10, "axes.edgecolor": INK2,
                     "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2})


def load(name):
    return json.loads((RES / f"{name}.json").read_text(encoding="utf-8"))


def style(ax, title, axis="y"):
    ax.set_title(title, color=INK, fontsize=11, loc="left")
    ax.grid(True, axis=axis, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def bars(ax, groups, series, values, colors, fmt="{:.3f}", log=False):
    """Cột nhóm, có nhãn số trên mỗi cột (nhãn trực tiếp thay cho việc dựa vào màu)."""
    n = len(series)
    w = 0.8 / n
    for j, (s, col) in enumerate(zip(series, colors)):
        xs = [i + (j - (n - 1) / 2) * w for i in range(len(groups))]
        vs = [values[g][s] for g in groups]
        ax.bar(xs, vs, w * 0.92, color=col, label=s)
        for x, v in zip(xs, vs):
            ax.text(x, v * (1.08 if log else 1) + (0 if log else 0.006), fmt.format(v), ha="center", va="bottom",
                    fontsize=8, color=INK)
    ax.set_xticks(range(len(groups)), groups)
    if log:
        ax.set_yscale("log")


# ----------------------------------------------------------------------------- sơ đồ khối
def box(ax, x, y, w, h, title, lines=(), fill=PALE, edge=NAVY, title_size=10.5, line_size=8.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc=fill, ec=edge, lw=1.1))
    ax.text(x + 0.15, y + h - 0.22, title, fontsize=title_size, weight="bold", color=NAVY, va="top")
    for i, t in enumerate(lines):
        ax.text(x + 0.15, y + h - 0.62 - i * 0.33, t, fontsize=line_size, color=INK, va="top")


def arrow(ax, a, b, label=None, color=INK2, rad=0.0, both=False, lpos=0.5, dy=0.12):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="<|-|>" if both else "-|>", mutation_scale=11, color=color,
                                 lw=1.1, connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))
    if label:
        x, y = a[0] + (b[0] - a[0]) * lpos, a[1] + (b[1] - a[1]) * lpos
        ax.text(x, y + dy, label, fontsize=8, color=INK2, ha="center", va="bottom",
                bbox=dict(fc="white", ec="none", pad=0.5))


def fig_arch():
    fig, ax = plt.subplots(figsize=(11, 6.2))
    ax.set_xlim(0, 15.4)
    ax.set_ylim(0, 8.6)
    ax.axis("off")
    # nguồn dữ liệu
    box(ax, 0.1, 5.5, 2.6, 1.7, "VNTC-10", ["84.132 bài (UTF-16)", "train 33.759 / test 50.373"],
        fill="#F5F5F3", edge=INK2)
    box(ax, 0.1, 2.85, 2.6, 1.7, "RSS 3 báo", ["VnExpress, Tuổi Trẻ,", "Thanh Niên"], fill="#F5F5F3", edge=INK2)
    # tầng xử lý lô (Python)
    box(ax, 3.5, 6.35, 3.4, 1.1, "load_articles.py", ["A1–A2: NFC, pyvi, top-50 item"])
    box(ax, 3.5, 4.75, 3.4, 1.25, "train_models.py", ["train_variants.py", "A3–A5: FI, Trans2Vec, LR"])
    box(ax, 3.5, 3.15, 3.4, 1.1, "fetch_news.py", ["GET có điều kiện, chống trùng"])
    box(ax, 3.5, 1.3, 3.4, 1.1, "sync_manticore.py", ["A6: dựng lại bảng news"])
    ax.text(5.2, 7.85, "Python (.venv-exp): xử lý lô", ha="center", fontsize=10, color=INK2, style="italic")
    # hai hệ lưu trữ
    box(ax, 7.8, 3.6, 3.5, 4.3, "MariaDB 11.8 (nguồn gốc)",
        ["category, article", "item, article_item (4,15 tr dòng)", "itemset, itemset_item,", "   article_itemset (3,1 tr)",
         "model_run (JSON), eval_result", "article_vector  VECTOR(128)", "prediction (JSON proba)",
         "search_log, classify_log", "   (phân vùng theo tháng)", "news_source, feed_item, fetch_log"],
        fill="#E3ECF9")
    box(ax, 7.8, 0.4, 3.5, 2.4, "Manticore 29.9 (phái sinh)",
        ["bảng RT news, 84.132 tài liệu", "BM25: title_seg, body_seg", "HNSW cosine: vec (JOI, 128)",
         "lọc: category_id, split", "charset giữ dấu tiếng Việt"], fill="#FBEDE6", edge=ORANGE)
    # ứng dụng
    box(ax, 12.2, 2.3, 3.1, 4.6, "Streamlit (4 trang)",
        ["Phân loại bài báo", "Tìm kiếm", "Dữ liệu và đánh giá", "Tin mới nhất", "",
         "Trong bộ nhớ:", "pyvi, Doc2Vec ×5,", "LR/SVM ×7, bảng FI"], fill="#E8F6F0", edge=AQUA)
    # luồng
    arrow(ax, (2.7, 6.6), (3.5, 6.85))
    arrow(ax, (2.7, 3.7), (3.5, 3.7))
    arrow(ax, (6.9, 6.9), (7.8, 6.9), "INSERT lô")
    arrow(ax, (6.9, 5.35), (7.8, 5.35), "đọc / ghi", both=True)
    arrow(ax, (6.9, 3.95), (7.8, 3.95), "INSERT", dy=0.08)
    arrow(ax, (7.8, 3.65), (6.6, 2.4), "SELECT", lpos=0.4, dy=-0.05)
    arrow(ax, (6.9, 1.6), (7.8, 1.6), "REPLACE lô", dy=0.08)
    arrow(ax, (12.2, 5.6), (11.3, 5.6), "chi tiết, FI, eval,\nghi log", lpos=0.5, dy=0.1, both=True)
    arrow(ax, (12.2, 2.8), (11.3, 1.9), "MATCH / knn()", lpos=0.5, dy=0.1)
    ax.text(9.55, 3.08, "dựng lại được hoàn toàn từ MariaDB", fontsize=8, color=ORANGE, ha="center", style="italic")
    fig.tight_layout()
    fig.savefig(FIG / "fig_arch.png", dpi=200)
    plt.close(fig)


# ----------------------------------------------------------------------------- sơ đồ ER
TABLES = {  # tên: (x, y_top, [cột], nhóm)
    "category": (0.0, 10.4, ["PK id", "code UNIQUE", "name"], "goc"),
    "article": (3.4, 10.4, ["PK id", "FK category_id", "split ENUM", "source_file UNIQUE", "title, body",
                            "body_md5 (cột sinh)", "body_syl, body_seg"], "goc"),
    "article_item": (6.8, 10.4, ["PK,FK article_id", "PK,FK item_id", "tf, tfidf, rnk", "KEY (item_id, article_id)"],
                     "goc"),
    "item": (10.2, 10.4, ["PK id", "token UNIQUE (bin)", "df_train, idf", "is_stop"], "goc"),
    "prediction": (0.0, 6.4, ["PK,FK article_id", "PK,FK run_id", "FK pred_category_id", "proba JSON"], "mh"),
    "article_vector": (3.4, 6.4, ["PK,FK article_id", "PK,FK run_id", "vec VECTOR(128)"], "mh"),
    "article_itemset": (6.8, 6.4, ["PK,FK article_id", "PK,FK itemset_id"], "fi"),
    "itemset_item": (10.2, 6.4, ["PK,FK itemset_id", "PK,FK item_id"], "fi"),
    "eval_result": (0.0, 2.9, ["PK,FK run_id", "PK task, metric, config", "value"], "mh"),
    "model_run": (3.4, 2.9, ["PK id", "kind", "FK parent_id", "params, metrics JSON"], "mh"),
    "itemset": (6.8, 2.9, ["PK id", "FK run_id", "size, support", "is_closed, wilson_lo", "label"], "fi"),
    "news_source": (14.0, 7.9, ["PK id", "code UNIQUE", "rss_url", "etag, last_modified"], "rss"),
    "feed_item": (14.0, 5.3, ["PK id", "FK source_id", "url_hash UNIQUE", "title, summary", "pred_category"], "rss"),
    "fetch_log": (14.0, 10.4, ["PK id", "FK source_id", "http_status, n_new"], "rss"),
    "search_log": (10.2, 2.9, ["PK (id, ts)", "query, mode", "result_ids JSON", "PARTITION theo tháng"], "log"),
    "classify_log": (14.0, 2.3, ["PK (id, ts)", "text_hash, run_id", "PARTITION theo tháng"], "log"),
}
ROWS = {"category": "10", "article": "84.132", "article_item": "4,15 tr", "item": "135.546",
        "prediction": "352.611", "article_vector": "420.660", "article_itemset": "3,11 tr", "itemset_item": "5.485",
        "eval_result": "42", "model_run": "15", "itemset": "3.586", "news_source": "3", "feed_item": "325",
        "fetch_log": "9", "search_log": "", "classify_log": ""}
COLORS = {"goc": ("#E3ECF9", NAVY), "fi": ("#E8F6F0", "#127a55"), "mh": ("#F3EEFA", "#5b3d8f"),
          "rss": ("#F5F5F3", INK2), "log": ("#FBEDE6", "#a8441d")}
W, LH = 3.0, 0.36


def tbox(name):
    x, y, cols, _ = TABLES[name]
    return x, y - 0.5 - LH * len(cols) - 0.1, W, 0.5 + LH * len(cols) + 0.1


def edge_point(name, side, f=0.5):
    """Điểm trên cạnh trái/phải/trên/dưới; f là vị trí dọc cạnh (0 = trái/dưới, 1 = phải/trên)."""
    x, y, w, h = tbox(name)
    return {"l": (x, y + h * f), "r": (x + w, y + h * f), "t": (x + w * f, y + h), "b": (x + w * f, y)}[side]


def fig_er():
    fig, ax = plt.subplots(figsize=(12, 8.4))
    ax.set_xlim(-0.2, 17.2)
    ax.set_ylim(-0.2, 10.6)
    ax.axis("off")
    for name, (x, y, cols, g) in TABLES.items():
        fill, edge = COLORS[g]
        bx, by, bw, bh = tbox(name)
        ax.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0,rounding_size=0.08", fc="white",
                                    ec=edge, lw=1.1))
        ax.add_patch(FancyBboxPatch((bx, y - 0.5), bw, 0.5, boxstyle="round,pad=0,rounding_size=0.08", fc=fill,
                                    ec=edge, lw=1.1))
        ax.text(bx + 0.12, y - 0.25, name, weight="bold", fontsize=10, color=edge, va="center")
        if ROWS[name]:
            ax.text(bx + bw - 0.1, y - 0.25, ROWS[name], fontsize=8, color=INK2, va="center", ha="right")
        for i, c in enumerate(cols):
            key = c.split(" ")[0] if c.split(" ")[0] in ("PK", "FK", "PK,FK") else ""
            ax.text(bx + 0.12, y - 0.5 - 0.05 - LH * (i + 0.5), c, fontsize=8.6, va="center",
                    color=NAVY if key else INK, weight="bold" if key.startswith("PK") else "normal")
    fks = [("article", "l", "category", "r"), ("article_item", "l", "article", "r"), ("article_item", "r", "item", "l"),
           ("prediction", "t", "category", "b"), (("prediction", "t", 0.9), ("article", "l", 0.12)),
           (("prediction", "b", 0.8), ("model_run", "t", 0.3)),
           ("article_vector", "t", "article", "b"), (("article_vector", "b"), ("model_run", "t", 0.6)),
           ("article_itemset", "t", "article", "r"), ("article_itemset", "b", "itemset", "t"),
           ("itemset_item", "t", "item", "b"), (("itemset_item", "b", 0.1), ("itemset", "t", 0.8)),
           ("itemset", "l", "model_run", "r"), ("eval_result", "r", "model_run", "l"),
           ("feed_item", "t", "news_source", "b"), ("fetch_log", "b", "news_source", "t")]
    for fk in fks:
        if len(fk) == 4:
            pa, pb = edge_point(fk[0], fk[1]), edge_point(fk[2], fk[3])
        else:
            pa, pb = edge_point(*fk[0]), edge_point(*fk[1])
        ax.add_patch(FancyArrowPatch(pa, pb, arrowstyle="-|>", mutation_scale=10, color=INK2, lw=1, shrinkA=0,
                                     shrinkB=0))
    # model_run.parent_id tự tham chiếu
    x, y, w, h = tbox("model_run")
    ax.add_patch(FancyArrowPatch((x + 0.7, y), (x + 2.1, y), arrowstyle="-|>", mutation_scale=10,
                                 color=INK2, lw=1, connectionstyle="arc3,rad=0.5"))
    ax.text(x + 1.4, y - 0.42, "parent_id", fontsize=8, color=INK2, ha="center")
    legend = [("goc", "Dữ liệu gốc"), ("fi", "Tập phổ biến"), ("mh", "Mô hình, kết quả"), ("rss", "Thu thập RSS"),
              ("log", "Nhật ký (không FK)")]
    for i, (g, t) in enumerate(legend):
        fill, edge = COLORS[g]
        ax.add_patch(FancyBboxPatch((i * 2.9, -0.15), 0.35, 0.3, boxstyle="round,pad=0,rounding_size=0.05",
                                    fc=fill, ec=edge))
        ax.text(i * 2.9 + 0.5, 0.0, t, fontsize=9, va="center", color=INK)
    ax.text(14.6, 0.0, "→ khóa ngoại (con → cha)", fontsize=9, va="center", color=INK2)
    fig.tight_layout()
    fig.savefig(FIG / "fig_er.png", dpi=200)
    plt.close(fig)


# ----------------------------------------------------------------------------- benchmark
def fig_edb1():
    rows = load("edb1_fulltext")["rows"]
    name = {"innodb": "InnoDB FULLTEXT", "manticore": "Manticore BM25"}
    q = {"kw": "kw (3 từ)", "doc": "doc (50 từ)"}
    nd = {q[r["query"]]: {} for r in rows}
    lat = {q[r["query"]]: {} for r in rows}
    for r in rows:
        nd[q[r["query"]]][name[r["engine"]]] = r["ndcg@10"]
        lat[q[r["query"]]][name[r["engine"]]] = r["p50_ms"]
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
    series, cols = list(name.values()), [MUTED, ORANGE]
    bars(axs[0], list(nd), series, nd, cols)
    axs[0].set_ylim(0.5, 0.78)
    style(axs[0], "nDCG@10 (cao hơn là tốt)")
    bars(axs[1], list(lat), series, lat, cols, fmt="{:.1f}", log=True)
    axs[1].set_ylim(0.5, 600)
    axs[1].set_ylabel("ms (thang log)")
    style(axs[1], "Độ trễ p50, ms (thấp hơn là tốt)")
    axs[0].legend(frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "fig_edb1.png", dpi=200)
    plt.close(fig)


def fig_edb2():
    rows = [r for r in load("edb2_vector")["rows"] if r["engine"] in ("mariadb", "manticore")]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    spec = [("mariadb", 16, BLUE, "-", "MariaDB M=16"), ("mariadb", 6, BLUE, "--", "MariaDB M=6"),
            ("manticore", 16, ORANGE, "-", "Manticore M=16"), ("manticore", 6, ORANGE, "--", "Manticore M=6")]
    for eng, m, col, ls, lab in spec:
        g = sorted((r for r in rows if r["engine"] == eng and r["M"] == m), key=lambda r: r["ef"])
        ax.plot([r["ef"] for r in g], [r["recall@10"] for r in g], linestyle=ls, color=col, lw=2, marker="o", ms=5,
                mec="white", mew=1, label=lab)
    ax.set_xscale("log")
    ax.set_xticks([10, 20, 40, 100, 200], ["10", "20", "40", "100", "200"])
    ax.minorticks_off()
    ax.set_xlabel("ef (thang log)")
    ax.set_ylabel("recall@10 so với vét cạn")
    ax.set_ylim(0.84, 1.005)
    style(ax, "Recall@10 của chỉ mục HNSW theo ef (33.759 vector, 1.000 truy vấn)", axis="both")
    ax.legend(frameon=False, fontsize=9, loc="lower right", handlelength=3.5)
    fig.tight_layout()
    fig.savefig(FIG / "fig_edb2.png", dpi=200)
    plt.close(fig)


def fig_edb4():
    rows = load("edb4_hybrid")["rows"]
    method = {"bm25": "BM25", "knn": "Vector (JOI)", "hybrid k=60 d=100": "Hybrid RRF"}
    groups = {("kw", "tất cả"): "kw, tất cả", ("kw", "có FI"): "kw có FI (n=56)",
              ("kw", "không FI"): "kw không FI", ("doc", "tất cả"): "doc"}
    vals = {g: {} for g in groups.values()}
    for r in rows:
        g = groups.get((r["query"], r["subset"]))
        if g and r["method"] in method:
            vals[g][method[r["method"]]] = r["ndcg@10"]
    fig, ax = plt.subplots(figsize=(9, 3.5))
    bars(ax, list(vals), list(method.values()), vals, [ORANGE, BLUE, AQUA])
    ax.set_ylim(0.55, 0.92)
    style(ax, "nDCG@10 của BM25, vector và hybrid trên Manticore")
    ax.legend(frameon=False, fontsize=9, ncol=3, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "fig_edb4.png", dpi=200)
    plt.close(fig)


def fig_edb5():
    rows = load("edb5_diacritics")["rows"]
    cfg = {"(a) fold": "(a) bảng gộp dấu", "(b) vi": "(b) giữ dấu", "(c) vi+syl": "(c) giữ dấu + âm tiết",
           "(d) vi-fold": "(d) trường gộp dấu (P1)"}
    qn = {"kw": "kw có dấu", "kw_nodiac": "kw không dấu", "doc": "doc"}
    vals = {}
    for r in rows:
        vals.setdefault(qn.get(r["query"], r["query"]), {})[cfg[r["config"]]] = r["ndcg@10"]
    fig, ax = plt.subplots(figsize=(9, 3.5))
    bars(ax, list(vals), list(cfg.values()), vals, [MUTED, BLUE, AQUA, ORANGE])
    ax.set_ylim(0.25, 0.82)
    style(ax, "nDCG@10 theo cách xử lý dấu (BM25, Manticore)")
    ax.legend(frameon=False, fontsize=9, ncol=4, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "fig_edb5.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(exist_ok=True)
    for f in (fig_arch, fig_er, fig_edb1, fig_edb2, fig_edb4, fig_edb5):
        f()
        print("ok", f.__name__)
