"""E7 — Tái hiện Trans2Vec trên Snippets bằng dữ liệu của mã nguồn chính thức (github.com/nphdang/Trans2Vec).

Mục đích:
  (1) kiểm chứng cách cài đặt trong experiments/ có tái hiện được kết quả bài [13]
      (Table 2: TRANS-IT 75,23 / TRANS-FI 77,88 / JOI 79,05 accuracy) không;
  (2) đo riêng ảnh hưởng của GIAO THỨC đánh giá:
      - transductive: như mã gốc, PV-DBOW học trên TOÀN BỘ tài liệu (cả test), vector lấy từ model.dv;
      - inductive:    như E6 của đề tài, học trên train, vector test (và train) sinh bằng infer_vector.

Theo mã gốc (trans2vec_joi_classify.py): PV-DBOW d=128, 50 epoch, min_count=0, LinearSVC() mặc định (C=1),
không chuẩn hóa vector. Chia cố định: 10.060 dòng đầu = train, 2.280 dòng sau = test (Bảng 1 của [13];
lưu ý mã gốc có lỗi if/else khiến Snippets thực tế dùng 80% = 9.872 dòng).

Chạy:  .venv-exp/bin/python src/experiments/replicate_snippets.py
"""
import json
import time
from pathlib import Path

import numpy as np
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.metrics import accuracy_score, f1_score
from sklearn.svm import LinearSVC

ROOT = Path(__file__).resolve().parents[2]  # gốc dự án (mã ở src/experiments/)
DATA = ROOT / "sources/repos/Trans2Vec/datasets/snippets"
OUT = ROOT / "src/experiments/results/replicate_snippets.json"
N_TRAIN, DIM, EPOCHS, SEEDS = 10060, 128, 50, [0, 1, 2]
FILES = {"TRANS-IT": "snippets.txt", "TRANS-FI": "snippets_trans_fis_0.002.txt",
         "Trans2Vec-JOI": "snippets_items_fis_0.002.txt"}
PAPER = {"TRANS-IT": (75.23, 74.79), "TRANS-FI": (77.88, 77.41), "Trans2Vec-JOI": (79.05, 78.31)}


def load(name):
    y, X = [], []
    for line in open(DATA / name, encoding="utf-8"):
        label, content = line.rstrip("\n").split("\t")
        y.append(label)
        X.append(content.split())
    return X, np.array(y)


def train(docs, seed):
    tagged = [TaggedDocument(d, [i]) for i, d in enumerate(docs)]
    m = Doc2Vec(dm=0, vector_size=DIM, min_count=0, epochs=EPOCHS, workers=8, seed=seed)
    m.build_vocab(tagged)
    m.train(tagged, total_examples=len(tagged), epochs=m.epochs)
    return m


def evaluate(Xtr, ytr, Xte, yte):
    pred = LinearSVC(max_iter=10000).fit(Xtr, ytr).predict(Xte)
    return 100 * accuracy_score(yte, pred), 100 * f1_score(yte, pred, average="macro")


def main():
    rows = []
    for method, fname in FILES.items():
        X, y = load(fname)
        for protocol in ["transductive", "inductive"]:
            accs, f1s = [], []
            t0 = time.time()
            for seed in SEEDS:
                if protocol == "transductive":
                    m = train(X, seed)  # học trên toàn bộ 12.340 tài liệu như mã gốc
                    V = np.vstack([m.dv[i] for i in range(len(X))])
                    Vtr, Vte = V[:N_TRAIN], V[N_TRAIN:]
                else:
                    m = train(X[:N_TRAIN], seed)  # chỉ học trên train, suy luận cho cả hai tập
                    inf = lambda docs: np.vstack([m.infer_vector(d, epochs=EPOCHS) for d in docs])
                    Vtr, Vte = inf(X[:N_TRAIN]), inf(X[N_TRAIN:])
                a, f = evaluate(Vtr, y[:N_TRAIN], Vte, y[N_TRAIN:])
                accs.append(a)
                f1s.append(f)
            row = {"method": method, "protocol": protocol, "acc": float(np.mean(accs)), "acc_sd": float(np.std(accs)),
                   "macro_f1": float(np.mean(f1s)), "f1_sd": float(np.std(f1s)),
                   "paper_acc": PAPER[method][0], "paper_f1": PAPER[method][1], "seconds": round(time.time() - t0, 1)}
            rows.append(row)
            print(f"{method:<14} {protocol:<12} acc={row['acc']:.2f}±{row['acc_sd']:.2f}  "
                  f"F1={row['macro_f1']:.2f}±{row['f1_sd']:.2f}  (bài báo: {PAPER[method][0]} / {PAPER[method][1]})", flush=True)
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Đã ghi", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
