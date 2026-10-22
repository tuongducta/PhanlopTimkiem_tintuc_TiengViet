"""E9 (bản sửa 22/10) — Nên đưa loại FI nào vào Trans2Vec-JOI: all, closed hay "ổn định" (CICFI, K25)?

Ở cấu hình chính (δ = 0,535%) mọi FI đều đóng, nên ablation A3 cũ không kiểm chứng được gì. E9 hạ δ để có
FI không đóng và FI sát ngưỡng, rồi so các cách lọc. Thiết kế: KE_HOACH_SURVEY_v3.md Mục 10.3.

Giao thức như E6: vector train và test đều sinh bằng infer_vector, LR C = 1, 3 seed; thêm nDCG@10.
Chỉ lọc FI dài ≥ 2: JOI chỉ thêm FI dài ≥ 2 vào item, còn FI đơn cần giữ để match_fi dò được cặp.

Chạy:  .venv-exp/bin/python src/experiments/run_e9_fi_types.py --delta 0.002
"""
import argparse
import json
import math
import time
from collections import Counter
from pathlib import Path

import numpy as np

import t2v

ROOT = Path(__file__).resolve().parents[2]  # gốc dự án (mã ở src/experiments/)
CORPUS = ROOT / "sources/data/vntc/processed/corpus.tsv.gz"
OUT = ROOT / "src/experiments/results/e9_fi_types.json"
MAIN_DELTA, K, D, EPOCHS, SEEDS, Z = 0.00535, 50, 128, 20, [1, 2, 3], 1.96

ap = argparse.ArgumentParser()
ap.add_argument("--delta", type=float, default=0.002, help="δ thấp dùng cho các biến thể lọc FI")
ap.add_argument("--skip-closed", action="store_true", help="bỏ biến thể closed khi gần như mọi FI đã đóng")
args = ap.parse_args()


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def wilson_lower(c, n):
    """Cận dưới khoảng Wilson 95% của tỉ lệ c/n — tiêu chí 'phổ biến và ổn định' của K25 (Def. 8)."""
    p = c / n
    centre = p + Z * Z / (2 * n)
    margin = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (centre - margin) / (1 + Z * Z / n)


def keep_long(fis, predicate):
    """Giữ mọi FI đơn, chỉ lọc FI dài ≥ 2."""
    return {f: c for f, c in fis.items() if len(f) == 1 or predicate(f, c)}


def n_long(fis):
    return sum(len(f) > 1 for f in fis)


# ---------------------------------------------------------------- dữ liệu (giống E1–E6)
log("Tải corpus")
train_rows, test_rows = t2v.load_corpus(CORPUS)
ytr = np.array([r["label"] for r in train_rows])
yte = np.array([r["label"] for r in test_rows])
docs_tr = [r["word"].split() for r in train_rows]
vocab = t2v.Vocab(docs_tr)
T_tr = t2v.transactions(docs_tr, vocab, K)
T_te = t2v.transactions([r["word"].split() for r in test_rows], vocab, K)
rng = np.random.default_rng(0)  # cùng 1.000 truy vấn như E1–E6 và E-DB*
q_idx = np.concatenate([rng.choice(np.where(yte == c)[0], min(100, (yte == c).sum()), replace=False)
                        for c in sorted(set(yte))])

# ---------------------------------------------------------------- các tập FI
log(f"Khai phá FI ở δ = {MAIN_DELTA} và δ = {args.delta}")
fis_main = t2v.mine_fi(T_tr, MAIN_DELTA)
fis_low = t2v.mine_fi(T_tr, args.delta)
n_tr = len(T_tr)
variants = {"IT": None, f"all δ={MAIN_DELTA}": fis_main, f"all δ={args.delta}": fis_low}
if not args.skip_closed:
    variants["closed"] = t2v.closed_only(fis_low)

# CICFI toàn cục: N chung nên cận dưới Wilson tăng đơn điệu theo support → tương đương nâng δ.
# Kiểm tra điều đó bằng mã thay vì huấn luyện thêm một biến thể trùng.
cic_global = keep_long(fis_low, lambda f, c: wilson_lower(c, n_tr) >= args.delta)
min_kept = min(c for f, c in cic_global.items() if len(f) > 1)
raised = keep_long(fis_low, lambda f, c: c >= min_kept)
assert set(cic_global) == set(raised), "CICFI toàn cục khác với nâng δ"
variants["CICFI toàn cục"] = cic_global

# Ổn định theo chuyên mục (dùng nhãn train → có giám sát). Ngưỡng "cận dưới ≥ δ" trong từng chuyên mục
# giữ gần như mọi FI (rsup trong chuyên mục cao gấp ~10 lần toàn cục; lần chạy đầu 22/10 giữ 17.349/17.349),
# nên thay bằng xếp hạng: lấy đúng bằng số FI của CICFI toàn cục, theo cận dưới Wilson lớn nhất qua các
# chuyên mục. Ba biến thể cùng cỡ chỉ khác tiêu chí chọn: support toàn cục / ổn định chuyên mục / ngẫu nhiên.
matched_tr = t2v.match_fi(T_tr, fis_low)
per_cat = {c: Counter() for c in set(ytr)}
for F, y in zip(matched_tr, ytr):
    per_cat[y].update(f for f in F if len(f) > 1)
n_cat = Counter(ytr)
long_low = sorted(f for f in fis_low if len(f) > 1)
score = {f: max(wilson_lower(per_cat[c][f], n_cat[c]) for c in per_cat) for f in long_low}
size = n_long(cic_global)
stable = set(sorted(long_low, key=lambda f: (-score[f], f))[:size])
variants["ổn định theo chuyên mục"] = keep_long(fis_low, lambda f, c: f in stable)

pick = {long_low[i] for i in np.random.default_rng(0).permutation(len(long_low))[:size]}
variants["ngẫu nhiên (cùng cỡ)"] = keep_long(fis_low, lambda f, c: f in pick)
log(f"Trùng với CICFI toàn cục: ổn định chuyên mục {len(stable & set(cic_global))}/{size}, "
    f"ngẫu nhiên {len(pick & set(cic_global))}/{size}")

summary = {name: (n_long(f) if f is not None else 0) for name, f in variants.items()}
log("Số FI dài ≥ 2:", json.dumps(summary, ensure_ascii=False))
log(f"CICFI toàn cục ≡ support ≥ {min_kept} bài (δ' = {min_kept / n_tr:.4%})")


# ---------------------------------------------------------------- huấn luyện và đánh giá
def run(name, fis, seed):
    if fis is None:
        F_tr, F_te, mode = [[]] * len(T_tr), [[]] * len(T_te), "it"
    else:
        F_tr, F_te, mode = t2v.match_fi(T_tr, fis), t2v.match_fi(T_te, fis), "joi"
    tok_tr, tok_te = t2v.pattern_tokens(T_tr, F_tr, mode), t2v.pattern_tokens(T_te, F_te, mode)
    t0 = time.time()
    model, _ = t2v.train_pvdbow(tok_tr, D, seed, epochs=EPOCHS)
    t1 = time.time()
    Ztr = t2v.l2(t2v.infer(model, tok_tr, epochs=EPOCHS))  # suy luận lại train, giống hệt test (E6)
    Zte = t2v.l2(t2v.infer(model, tok_te, epochs=EPOCHS))
    t2 = time.time()
    cls = t2v.classify(Ztr, ytr, Zte, yte, "lr")
    ret = t2v.retrieval(Ztr, ytr, Zte[q_idx], yte[q_idx])
    return {"variant": name, "seed": seed, "n_fi2": summary[name],
            "fi2_per_doc_train": float(np.mean([sum(len(f) > 1 for f in F) for F in F_tr])),
            "acc": cls["acc"], "macro_f1": cls["macro_f1"], **ret,
            "train_s": round(t1 - t0, 1), "infer_s": round(t2 - t1, 1)}


rows = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
done = {(r["variant"], r["seed"]) for r in rows if r.get("delta_low") == args.delta}
for seed in SEEDS:  # vòng ngoài là seed để có sớm một lượt đủ mọi biến thể
    for name, fis in variants.items():
        if (name, seed) in done:
            continue
        try:
            row = {"delta_low": args.delta, "cicfi_global_min_support": min_kept, **run(name, fis, seed)}
        except Exception as e:  # ghi lỗi rồi chạy tiếp biến thể khác
            row = {"delta_low": args.delta, "variant": name, "seed": seed, "error": repr(e)}
        rows.append(row)
        OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        log(f"{name:<32} seed={seed} MF1={row.get('macro_f1', float('nan')):.4f} "
            f"nDCG={row.get('ndcg@10', float('nan')):.4f} ({row.get('train_s')}+{row.get('infer_s')} s)")
log("Đã ghi", OUT.relative_to(ROOT))
