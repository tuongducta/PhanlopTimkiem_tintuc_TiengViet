"""E-DB5: giữ dấu hay gộp dấu trong Manticore? (BM25, cùng dữ liệu, cùng ranker)

Cấu hình:
  (a) fold     bảng `news_fold`, charset_table='non_cjk' mặc định: gộp dấu, '_' là dấu tách → từ ghép pyvi
               "giá_vàng" thành hai âm tiết; truy vấn gửi dạng cụm "gia vang" để giữ thứ tự
  (b) vi       bảng `news`, charset giữ dấu + '_' → khớp đúng token pyvi
  (c) vi+syl   như (b) và khớp thêm âm tiết trên body_syl
  (d) vi-fold  bảng `news`, trường title_fold/body_fold (gộp dấu bằng system/vi_text.fold, P1): nhánh mà hệ thống
               dùng khi truy vấn không dấu (Searcher.bm25_fold); từ ghép khớp dạng cụm như (a)
Truy vấn: kw (3 từ khóa), kw không dấu (người dùng gõ "gia vang"), doc (50 từ). Kho = train.
Đầu-cuối: kw không dấu gõ như người dùng (âm tiết cách nhau bằng dấu cách, không biết từ ghép) qua Searcher.search():
  đường cũ (pyvi → BM25 trường giữ dấu) so với hệ thống hiện tại ở chế độ bm25 / knn / hybrid.
Bảng news_fold được dựng bằng sync_manticore.py nếu chưa có.

Chạy: .venv-exp/bin/python src/system/bench/edb5_diacritics.py
"""
import subprocess
import sys

from common import BENCH, Protocol, lat_stats, save, strip_accents, table, timed
from search import BM25, Searcher

ROOT = BENCH.parents[1]


def fold_bm25(s, terms):
    phrases = [f'"{t.replace("_", " ")}"' if "_" in t else t for t in terms]
    expr = "@(title_seg,body_seg) (" + " | ".join(phrases) + ")"
    with s.mc.cursor() as m:
        m.execute(f"SELECT id FROM news_fold WHERE MATCH(%s) AND split='train' LIMIT 100 " + BM25.format(n=1000), (expr,))
        return [r[0] for r in m.fetchall()]


def main():
    s = Searcher()
    with s.mc.cursor() as m:
        m.execute("SHOW TABLES")
        tables = {r[0] for r in m.fetchall()}
    if "news_fold" not in tables:
        subprocess.run([sys.executable, str(ROOT / "system/pipeline/sync_manticore.py"),
                        "--table", "news_fold", "--charset", "non_cjk"], check=True)
    sizes = {}
    with s.mc.cursor() as m:
        for t in ["news", "news_fold"]:
            m.execute(f"SHOW TABLE {t} STATUS")
            sizes[t] = int(dict(m.fetchall())["disk_bytes"])
    P = Protocol(s.db)
    qsets = {"kw": P.queries("kw"), "kw không dấu": [[strip_accents(t) for t in q] for q in P.queries("kw")],
             "doc": P.queries("doc")}
    configs = {
        "(a) fold": lambda q: fold_bm25(s, q),
        "(b) vi": lambda q: [i for i, _ in s.bm25(q, 100, split="train")],
        "(c) vi+syl": lambda q: [i for i, _ in s.bm25(q, 100, split="train", syllables=True)],
        "(d) vi-fold": lambda q: [i for i, _ in s.bm25_fold(q, 100, split="train")],
    }
    rows = []
    for qname, Q in qsets.items():
        for cname, fn in configs.items():
            fn(Q[0])
            ranked, lat = timed(fn, Q)
            r = {"query": qname, "config": cname, **P.metrics(ranked), **lat_stats(lat),
                 "table_bytes": sizes["news_fold" if cname.startswith("(a)") else "news"]}
            rows.append(r)
            print(f"{qname:<13} {cname:<11} nDCG@10={r['ndcg@10']:.4f} rỗng={r['empty']:.3f} p50={r['p50_ms']:.1f}ms",
                  flush=True)
    # Ví dụ nhập nhằng do gộp dấu: số bài train khớp từng token khi có dấu / gộp dấu
    examples = {}
    with s.mc.cursor() as m:
        for w in ["bàn", "bán", "bạn", "bản", "ban"]:
            m.execute("SELECT COUNT(*) FROM news WHERE MATCH(%s) AND split='train'", (f"@body_seg {w}",))
            vi = m.fetchone()[0]
            m.execute("SELECT COUNT(*) FROM news_fold WHERE MATCH(%s) AND split='train'", (f"@body_seg {w}",))
            nf = m.fetchone()[0]
            m.execute("SELECT COUNT(*) FROM news WHERE MATCH(%s) AND split='train'", (f"@body_fold {strip_accents(w)}",))
            examples[w] = {"vi": vi, "fold": nf, "vi_fold_field": m.fetchone()[0]}
    print("số bài train khớp:", examples)
    typed = [" ".join(strip_accents(t).replace("_", " ") for t in q) for q in P.queries("kw")]
    e2e = {"old: bm25 giữ dấu": P.metrics([[i for i, _ in s.bm25(s.query_terms(s.segment(q)), 100, split="train")]
                                           for q in typed])}
    for mode in ["bm25", "knn", "hybrid"]:
        e2e[f"search() {mode}"] = P.metrics([[h["id"] for h in s.search(q, mode=mode, k=100, split="train",
                                                                        dedupe=False)["hits"]] for q in typed])
    print("đầu-cuối, kw không dấu gõ tự do:", {k: round(v["ndcg@10"], 3) for k, v in e2e.items()})
    save("edb5_diacritics", {"rows": rows, "table_bytes": sizes, "examples": examples, "end_to_end": e2e})
    table(rows, ["query", "config", "p@10", "map@100", "ndcg@10", "empty", "p50_ms", "p95_ms"])


if __name__ == "__main__":
    main()
