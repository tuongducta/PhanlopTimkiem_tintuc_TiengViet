"""E8 — Hồ sơ dữ liệu giao dịch theo K26 (Trasierras et al., Inf. Sci. 2024) cho Snippets và VNTC-10.

Câu hỏi: vì sao FI giúp Trans2Vec trên Snippets (JOI − IT = +3,07 khi đánh giá inductive, E7) mà gần như
không giúp trên VNTC (+0,1, E6)? Giả thuyết của K26: hiệu ứng phụ thuộc hồ sơ dữ liệu (độ dày, độ giống
nhau, độ dài giao dịch), và hồ sơ đó lại đổi theo ngưỡng δ. Thiết kế: KE_HOACH_SURVEY_v3.md Mục 10.2.

Chỉ dùng tập train. Ở mỗi δ, bỏ item có support < δ rồi mới tính độ đo (cách làm của K26 Mục 4).
Density, IT, |T|, |B|, ||T|| khớp Bảng 3 của K26; Similarity, ID, IS cài theo công thức in trong bài
(Eq. 3, 5, 9) — các công thức này không tái tạo được số trong Bảng 3, nên chỉ so giữa các corpus ở đây.

Chạy:  .venv-exp/bin/python src/experiments/run_e8_profile.py
"""
import json
import math
import time
from collections import Counter
from pathlib import Path

import numpy as np

import t2v

ROOT = Path(__file__).resolve().parents[2]  # gốc dự án (mã ở src/experiments/)
CORPUS = ROOT / "sources/data/vntc/processed/corpus.tsv.gz"
SNIPPETS = ROOT / "sources/repos/Trans2Vec/datasets/snippets/snippets.txt"
OUT = ROOT / "src/experiments/results/e8_profile.json"
N_TRAIN_SNIPPETS = 10060  # chia cố định như Bảng 1 của [13]
DELTAS = [0.0, 0.002, 0.00535, 0.01, 0.02]
PAIR_LIMIT = 1_000_000  # quá ngưỡng này thì bỏ khai phá bộ ba: bùng nổ FI (H2) làm bước đếm hết bộ nhớ
JOI_MINUS_IT = {  # đóng góp của FI khi đánh giá nhất quán (Macro-F1 với VNTC, accuracy với Snippets)
    "snippets": ("+3,07", "E7 inductive"), "vntc_word_k50": ("+0,1", "E6"),
    "vntc_word_k100": ("-0,3", "E6"), "vntc_syl_k50": ("+0,9", "E6"),
}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def profile(trans):
    """8 độ đo của K26. Tính qua support của item để khỏi so từng cặp giao dịch (O(|T|²))."""
    trans = [t for t in trans if t]
    n_t = len(trans)
    sup = Counter()
    for t in trans:
        sup.update(t)
    n_b = len(sup)
    lens = np.array([len(t) for t in trans], dtype=float)
    # Σ_{k≠j} |t_j ∩ t_k| = Σ_{i∈t_j} (sup(i) − 1): số item chung của t_j với mọi giao dịch khác
    shared = np.array([sum(sup[i] - 1 for i in t) for t in trans], dtype=float) / (n_t - 1)
    # Eq. 9: kích thước kỳ vọng của một tập con khác rỗng = n·2^(n−1) / (2^n − 1)
    is_ = np.array([n / 2 / (1 - 2.0 ** -n) for n in lens])
    return {
        "n_trans": n_t, "n_items": n_b, "size": int(lens.sum()),
        "density": float(lens.sum() / (n_b * n_t)),
        "it_mean": float(lens.mean()), "it_std": float(lens.std(ddof=1)),
        "sim_shared_items": float(shared.mean()),          # Eq. 3 đúng như in
        "sim_pct": float((100 * shared / lens).mean()),    # cùng đại lượng, tính theo % độ dài giao dịch
        "id": float((lens * (lens - 1)).sum() / (n_b * n_t)),  # Eq. 5: Σ_t |t|(|t|−1) / (|B|·|T|)
        "is": float(is_.mean()),
    }


def fi_stats(trans, delta):
    """Thống kê FI (độ dài ≤ 3) ở δ — cùng hàm khai phá với E1–E6 để số liệu so được."""
    min_count = max(2, math.ceil(delta * len(trans)))
    _, pairs = t2v.pair_counts(trans, min_count)
    if len(pairs) > PAIR_LIMIT:
        return {"skipped": f"{len(pairs)} cặp phổ biến > {PAIR_LIMIT}"}
    t0 = time.time()
    fis = t2v.mine_fi(trans, delta)
    mine_s = time.time() - t0
    closed = t2v.closed_only(fis)
    matched = t2v.match_fi(trans, fis)
    long_per_doc = np.array([sum(len(f) > 1 for f in F) for F in matched])
    by_len = Counter(len(f) for f in fis)
    return {
        "min_count": min_count, "n_fi": len(fis), "n_fi_len": {str(k): by_len[k] for k in sorted(by_len)},
        "mine_s": round(mine_s, 1),
        # "đóng" xét trong tập đã khai phá (độ dài ≤ 3): FI dài 3 có thể có tập cha dài 4 cùng support
        "share_not_closed": 1 - len(closed) / len(fis),
        "fi2_per_doc": float(long_per_doc.mean()),
        "share_docs_without_fi2": float((long_per_doc == 0).mean()),
    }


def snippets_trans():
    trans = []
    with open(SNIPPETS, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= N_TRAIN_SNIPPETS:
                break
            trans.append(frozenset(line.rstrip("\n").split("\t")[1].split()))
    return trans


def vntc_configs():
    train_rows, _ = t2v.load_corpus(CORPUS)
    for view in ["word", "syl"]:
        docs = [r[view].split() for r in train_rows]
        vocab = t2v.Vocab(docs)  # cùng từ dừng và min_df như E1–E6
        ks = [20, 50, 100, None] if view == "word" else [50]
        for k in ks:
            yield f"vntc_{view}_k{k or 'all'}", t2v.transactions(docs, vocab, k), k is not None


def main():
    rows = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
    done = {(r["config"], r["delta"]) for r in rows}

    def configs():
        yield "snippets", snippets_trans(), True
        yield from vntc_configs()

    for name, trans, with_fi in configs():
        sup = Counter()
        for t in trans:
            sup.update(t)
        for delta in DELTAS:
            if (name, delta) in done:
                continue
            t0 = time.time()
            try:
                min_count = max(1, math.ceil(delta * len(trans)))
                kept = [frozenset(i for i in t if sup[i] >= min_count) for t in trans]
                row = {"config": name, "delta": delta, **profile(kept),
                       "share_empty": float(np.mean([not t for t in kept]))}
                if with_fi and delta > 0:
                    row["fi"] = fi_stats(trans, delta)
                if name in JOI_MINUS_IT:
                    row["joi_minus_it"], row["joi_minus_it_src"] = JOI_MINUS_IT[name]
            except MemoryError as e:  # chạy tiếp các cấu hình khác thay vì dừng cả script
                row = {"config": name, "delta": delta, "error": repr(e)}
            row["seconds"] = round(time.time() - t0, 1)
            rows.append(row)
            OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
            fi = row.get("fi", {})
            log(f"{name:<16} δ={delta:<8} |T|={row.get('n_trans')} |B|={row.get('n_items')} "
                f"IT={row.get('it_mean', 0):.1f} dens={row.get('density', 0):.2e} sim%={row.get('sim_pct', 0):.2f} "
                f"FI={fi.get('n_fi', fi.get('skipped', '-'))} notclosed={fi.get('share_not_closed', '-')} "
                f"({row['seconds']}s)")
    log("Đã ghi", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
