"""GĐ-H3: đối chiếu kết quả lưu trong MariaDB với E6/E5 (experiments/RESULTS.md) và kiểm tra các view.

Chạy: .venv-exp/bin/python src/system/bench/check_models.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import connect_mariadb  # noqa: E402

# Số liệu tham chiếu (experiments/results/*.jsonl): E6 LR C=1 và E5 TF-IDF LR C=10, view word k=50
REF = {
    "trans-it": {"macro_f1": 0.8473, "acc": 0.8740, "ndcg@10": 0.8029},
    "trans2vec-joi": {"macro_f1": 0.8487, "acc": 0.8749, "ndcg@10": 0.8117},
    "tfidf": {"macro_f1": 0.9065, "acc": 0.9246},
}

SQL = """
SELECT e.kind, ev.task, ev.metric, ev.value
FROM model_run e JOIN eval_result ev ON ev.run_id = e.id
WHERE e.kind IN ('trans-it','trans2vec-joi','tfidf') AND ev.task = 'search' AND ev.metric = 'ndcg@10'
UNION ALL
SELECT p.kind, ev.task, ev.metric, ev.value
FROM model_run l JOIN model_run p ON p.id = l.parent_id JOIN eval_result ev ON ev.run_id = l.id
WHERE l.kind = 'lr' AND ev.metric IN ('acc','macro_f1')"""


def main():
    con = connect_mariadb()
    with con.cursor() as c:
        c.execute("SELECT id, kind, parent_id, JSON_COMPACT(params) FROM model_run ORDER BY id")
        for r in c.fetchall():
            print("run", r)
        c.execute(SQL)
        print(f"\n{'mô hình':<15}{'độ đo':<10}{'MariaDB':>9}{'E5/E6':>9}{'chênh':>8}")
        for kind, _, metric, v in c.fetchall():
            ref = REF[kind].get(metric)
            diff = f"{v - ref:+.4f}" if ref else ""
            print(f"{kind:<15}{metric:<10}{v:>9.4f}{ref or float('nan'):>9.4f}{diff:>8}")
        c.execute("SELECT size, COUNT(*), SUM(is_closed), ROUND(MIN(support)), MAX(support) FROM itemset GROUP BY size")
        print("\nitemset theo độ dài (size, số, đóng, min sup, max sup):", c.fetchall())
        for name, sql in [
            ("v_category_fi (TT, top 5)", "SELECT code, label, n_article FROM v_category_fi WHERE code='TT' AND rk<=5"),
            ("v_category_fi (KD, top 5)", "SELECT code, label, n_article FROM v_category_fi WHERE code='KD' AND rk<=5"),
            ("v_confusion: cặp nhầm nhiều nhất (JOI)",
             "SELECT v.true_code, v.pred_code, v.n FROM v_confusion v JOIN model_run l ON l.id = v.run_id"
             " JOIN model_run p ON p.id = l.parent_id WHERE p.kind = 'trans2vec-joi'"
             " AND v.true_code <> v.pred_code ORDER BY v.n DESC LIMIT 5"),
            ("dung lượng (bảng, dòng ước lượng, data MB, index MB)",
             "SELECT table_name, table_rows, ROUND(data_length/1048576), ROUND(index_length/1048576)"
             " FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name IN"
             " ('itemset','itemset_item','article_itemset','article_vector','prediction') ORDER BY table_name"),
        ]:
            c.execute(sql)
            print(f"{name}: {c.fetchall()}")
    con.close()


if __name__ == "__main__":
    main()
