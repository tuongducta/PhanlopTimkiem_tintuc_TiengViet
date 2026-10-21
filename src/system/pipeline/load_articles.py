"""A1–A2 (GĐ-H2): nạp VNTC-10 vào MariaDB — category, article, item, article_item.

Nguồn:
  - data/vntc/processed/corpus.tsv.gz  (kết quả experiments/prepare.py: âm tiết + từ pyvi, NFC)
  - data/vntc/raw/*_Full/<chủ đề>/*.txt (UTF-16) để lấy tiêu đề và toàn văn gốc
Từ vựng và transaction dùng đúng t2v.Vocab (min_df=3, max_df=0.3, học trên train) và top-k=50 theo
tf·idf như t2v.transactions, nên khớp view ("word", 50) của E6.

Chạy (sau khi áp schema.sql lên CSDL rỗng):
  .venv-exp/bin/python src/system/pipeline/load_articles.py
"""
import csv
import gzip
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # gốc dự án (mã ở src/system/<gói>/)
sys.path.insert(0, str(ROOT / "src/system"))
sys.path.insert(0, str(ROOT / "src/experiments"))
import t2v  # noqa: E402
from config import connect_mariadb  # noqa: E402
from prepare import LABELS  # noqa: E402

CORPUS = ROOT / "sources/data/vntc/processed/corpus.tsv.gz"
RAW = ROOT / "sources/data/vntc/raw"
K = 50
BATCH = 1000


def read_raw(path):
    lines = unicodedata.normalize("NFC", path.read_bytes().decode("utf-16")).strip().splitlines()
    return lines[0].strip()[:512], "\n".join(l.strip() for l in lines[1:] if l.strip())


def raw_index():
    """(split, nhãn, tên tệp) → đường dẫn tệp gốc. Tên thư mục có thể có khoảng trắng thừa."""
    idx = {}
    for p in RAW.glob("*_Full/*/*.txt"):
        split = "train" if p.parts[-3] == "Train_Full" else "test"
        idx[(split, LABELS[p.parts[-2].strip()], p.name)] = p
    return idx


def ranked_items(doc, vocab):
    """Như t2v.transactions nhưng giữ cả tf, tf·idf và thứ hạng."""
    tf = Counter(t for t in doc if t in vocab.idf)
    ranked = sorted(tf, key=lambda t: (-tf[t] * vocab.idf[t], t))[:K]
    return [(t, tf[t], tf[t] * vocab.idf[t], r) for r, t in enumerate(ranked, 1)]


def main():
    t0 = time.time()
    csv.field_size_limit(10**9)
    with gzip.open(CORPUS, "rt", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    train_docs = [r["word"].split() for r in rows if r["split"] == "train"]
    vocab = t2v.Vocab(train_docs)
    df = Counter()
    for d in train_docs:
        df.update(set(d))
    print(f"{len(rows)} bài; từ vựng train {len(df)} token, {len(vocab.idf)} item, "
          f"{len(vocab.stopwords)} từ dừng ({time.time() - t0:.0f}s)")

    # Kiểm tra khớp với thư viện thực nghiệm trên 500 bài đầu
    sample = train_docs[:500]
    assert [frozenset(t for t, *_ in ranked_items(d, vocab)) for d in sample] == t2v.transactions(sample, vocab, K)

    items = sorted(df)
    item_id = {t: i for i, t in enumerate(items, 1)}
    idx = raw_index()
    con = connect_mariadb()
    with con.cursor() as c:
        c.execute("SELECT COUNT(*) FROM article")
        if c.fetchone()[0]:
            sys.exit("Bảng article không rỗng: áp lại system/db/schema.sql trước khi nạp.")
        c.executemany(
            "INSERT INTO item (id, token, df_train, idf, is_stop) VALUES (%s,%s,%s,%s,%s)",
            [(item_id[t], t, df[t], vocab.idf.get(t), t in vocab.stopwords) for t in items],
        )
        con.commit()
        print(f"item: {len(items)} dòng ({time.time() - t0:.0f}s)")

        cat = {code: i for i, code in enumerate(LABELS.values(), 1)}
        folder = {v: k for k, v in LABELS.items()}
        n_ai = 0
        for start in range(0, len(rows), BATCH):
            arts, ais = [], []
            for i, r in enumerate(rows[start:start + BATCH], start + 1):
                p = idx[(r["split"], r["label"], r["file"])]
                title, body = read_raw(p)
                src = f"{p.parts[-3]}/{folder[r['label']]}/{p.name}"
                syl, seg = r["syl"], r["word"]
                arts.append((i, cat[r["label"]], r["split"], src, title, body, syl, seg,
                             syl.count(" ") + 1 if syl else 0, seg.count(" ") + 1 if seg else 0))
                ais += [(i, item_id[t], tf, w, rk) for t, tf, w, rk in ranked_items(seg.split(), vocab)]
            c.executemany(
                "INSERT INTO article (id, category_id, split, source_file, title, body, body_syl, body_seg,"
                " n_syl, n_word) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", arts)
            c.executemany("INSERT INTO article_item (article_id, item_id, tf, tfidf, rnk) VALUES (%s,%s,%s,%s,%s)", ais)
            con.commit()
            n_ai += len(ais)
            if (start // BATCH) % 10 == 0:
                print(f"  {start + len(arts)}/{len(rows)} bài, {n_ai} dòng transaction ({time.time() - t0:.0f}s)",
                      flush=True)
        c.execute("ANALYZE TABLE article, item, article_item")
        c.fetchall()
    con.close()
    print(f"XONG: {len(rows)} bài, {n_ai} dòng article_item, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
