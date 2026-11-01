"""Giao diện Trans2Vec News (GĐ-H5) — 4 mục: Phân loại · Tìm kiếm · Dữ liệu và đánh giá · Tin mới nhất.

Chạy:  scripts/run-app.sh  (hoặc .venv-exp/bin/streamlit run src/system/app/streamlit_app.py từ thư mục gốc)
Mọi số liệu đọc từ MariaDB (model_run, eval_result, view); tìm kiếm qua Manticore; mô hình ở system/models/.
Kiểu dáng theo template tham khảo sources/template_demo/ (nền tối, cyan/indigo); chỉ lấy bố cục, không lấy số liệu mẫu.
"""
import html
import json
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

APP = Path(__file__).resolve().parent
sys.path.insert(0, str(APP))
sys.path.insert(0, str(APP.parent / "pipeline"))
import theme  # noqa: E402
from classify import Classifier  # noqa: E402
from config import connect_mariadb  # noqa: E402
from search import Searcher  # noqa: E402
from vi_text import fold  # noqa: E402

MODES = {"BM25": "bm25", "Vector (Trans2Vec-JOI)": "knn", "Hybrid (RRF)": "hybrid"}
MODE_LABEL = {v: k for k, v in MODES.items()}
MODE_DESC = {
    "hybrid": "Hybrid: hợp nhất hạng BM25 và hạng vector bằng Reciprocal Rank Fusion (k = 60), mỗi bên lấy 100 ứng viên.",
    "knn": "Vector: truy vấn → pyvi → item và FI → infer_vector → KNN HNSW cosine trên Manticore.",
    "bm25": "BM25: toàn văn đã tách từ (title_seg, body_seg), k1 = 1,2, b = 0,75; giữ dấu tiếng Việt.",
}
SAMPLE_QUERIES = ["giá vàng tăng mạnh", "đội tuyển Việt Nam thắng trận", "dịch cúm gia cầm",
                  "máy tính xách tay giá rẻ", "xét xử vụ án tham nhũng"]
# biểu tượng và tông màu chỉ để trang trí nhãn chuyên mục (theo mã VNTC)
CAT_STYLE = {"XH": ("🏛️", "cyan"), "DS": ("🏠", "sky"), "KH": ("🔬", "violet"), "KD": ("💼", "amber"),
             "PL": ("⚖️", "rose"), "SK": ("🏥", "emerald"), "TG": ("🌏", "indigo"), "TT": ("⚽", "lime"),
             "VH": ("🎭", "pink"), "VT": ("💻", "blue")}
# icon dùng trong thẻ HTML: tên ligature của font Material Symbols mà Streamlit đã nạp sẵn
# (st.html lọc bỏ thẻ <svg> nên không dùng được Heroicons như template)
ICONS = {"db": "database", "cog": "settings", "info": "info", "list": "checklist", "trend": "trending_up",
         "tag": "sell", "chart": "bar_chart"}

st.set_page_config(page_title="Trans2Vec News", layout="wide")

# Khung CSS và token màu được quản lý tập trung trong theme.py.
name = st.session_state.get("t2v_palette", theme.DEFAULT)
st.html(theme.css(name))


# ===================================================================== tiện ích HTML
e = lambda x: html.escape(str(x))
txt = lambda x: x if isinstance(x, str) else ""  # summary NULL ra None/NaN/pd.NA; NaN truthy nên "or" không chặn được và str(NaN) thành "nan"
vn = lambda x, d=3: f"{x:.{d}f}".replace(".", ",")  # số thập phân dấu phẩy như trong báo cáo
pct = lambda x: f"{x * 100:.1f}%".replace(".", ",")
num = lambda n: "—" if pd.isna(n) else f"{int(n):,}".replace(",", ".")  # NaN: ô trống của pivot


def icon(name):
    return f'<span class="t2v-ic">{ICONS[name]}</span>'


def cat_chip(code, name=None, emoji=False):
    em, tone = CAT_STYLE.get(code, ("", "gray"))
    return f'<span class="t2v-cat {tone}">{em + " " if emoji else ""}{e(name or code)}</span>'


def bar(x, cls="", kind=""):
    """Thanh ngang; x trong [0, 1]."""
    return f'<div class="t2v-bar {kind}"><i class="{cls}" style="width:{max(0.0, min(x, 1.0)) * 100:.1f}%"></i></div>'


def chips(xs, hi=0, cls=""):
    return '<div class="t2v-chips">' + "".join(
        f'<span class="t2v-chip {cls}{" hi" if i < hi else ""}">{e(x)}</span>' for i, x in enumerate(xs)) + "</div>"


def card_head(title, sub="", tag="", right="", h="h3", dot=""):
    side = right or (f'<span class="t2v-tag">{e(tag)}</span>' if tag else "")
    return (f'<div class="t2v-ch"><div><{h}><span class="dot {dot}"></span>{e(title)}</{h}>'
            f'{f"<p>{sub}</p>" if sub else ""}</div>{side}</div>')


def topbar(title, sub):
    """Thanh trên như template: đường dẫn trang, nhãn tập dữ liệu và mô hình cải tiến; sau đó là tiêu đề trang."""
    _, clf = load()
    total, _, _ = corpus()
    best = next((m["name"] for m in clf.models if m["improved"]), "Trans2Vec-JOI")
    st.html(f'<div class="t2v-top"><div class="t2v-crumb"><span>Bảng điều khiển</span><span class="sep">/</span>'
            f'<b><span class="dot sm"></span>{e(title)}</b></div><div class="t2v-badges">'
            f'<span class="t2v-badge">{icon("db")}<span>Tập mẫu: <strong>VNTC-10</strong></span><span class="bar">|</span>'
            f'<em>{num(total)} bài</em></span>'
            f'<span class="t2v-badge model">{icon("cog")}<span>Mô hình: <strong>{e(best)}</strong></span>'
            f'<span class="dot g"></span></span></div></div>'
            f'<div class="t2v-head"><div class="t2v-h1"><span class="dot"></span>{e(title)}</div>'
            f'<div class="t2v-sub">{sub}</div></div>')


def banner(label, text):
    st.html(f'<div class="t2v-banner"><div class="ib">{icon("info")}</div>'
            f'<div><strong>[{e(label)}]</strong>{text}</div></div>')


@st.cache_resource(show_spinner="Đang nạp mô hình và kết nối CSDL…")
def load():
    s = Searcher()
    return s, Classifier(s)


def q(sql, args=None):
    s, _ = load()
    with s.cursor() as c:  # tự kết nối lại nếu MariaDB đã đóng kết nối rỗi
        c.execute(sql, args)
        cols = [d[0] for d in c.description]
        return pd.DataFrame(c.fetchall(), columns=cols)


@st.cache_data(ttl=3600)
def corpus():
    sp = q("SELECT split, COUNT(*) n FROM article GROUP BY split").set_index("split")["n"]
    return int(sp.sum()), int(sp["train"]), int(sp["test"])


# Bộ phân loại mà app thực sự dùng, chọn đúng như Classifier.__init__: embedding mới nhất của mỗi loại
# (MAX(id) theo kind), rồi lần chạy LR/SVM mới nhất có macro_f1 thuộc đúng embedding đó.
# Bảng tổng hợp và ma trận nhầm lẫn dùng chung định nghĩa này để cùng một lần chạy.
LATEST_CLF = """SELECT MAX(l2.id) FROM model_run l2
                JOIN eval_result v2 ON v2.run_id = l2.id AND v2.metric = 'macro_f1'
                WHERE l2.kind IN ('lr','svm') AND l2.parent_id IN (SELECT MAX(id) FROM model_run GROUP BY kind)
                GROUP BY l2.parent_id"""
# Lần chạy embedding mới nhất CÓ kết quả tìm kiếm của mỗi biểu diễn
LATEST_SEARCH = """SELECT MAX(e3.id) FROM model_run e3 JOIN eval_result v3 ON v3.run_id = e3.id AND v3.task = 'search'
                   GROUP BY e3.kind"""


def confusion():  # không cache: phải cùng thời điểm với bảng tổng hợp (huấn luyện lại khi app đang chạy)
    """Ma trận nhầm lẫn (view v_confusion) của lần chạy bộ phân loại mới nhất cho mỗi biểu diễn."""
    return q("""SELECT e.kind, l.id AS run_id, v.true_code, v.pred_code, v.n FROM v_confusion v
                JOIN model_run l ON l.id = v.run_id JOIN model_run e ON e.id = l.parent_id
                WHERE l.id IN (""" + LATEST_CLF + ")")


@st.cache_data(ttl=3600)
def dup_conflicts():
    """Bài test trùng nội dung (body_md5) với một bài mang nhãn khác: {article_id: (nhãn, {mọi nhãn của nhóm})}.

    Lấy nhóm md5 lặp bằng chỉ mục ix_body_md5 trước (vài ms) rồi mới đọc nhãn, thay vì EXISTS tương quan (~4 s).
    Bỏ md5 của chuỗi rỗng: 1.550 file VNTC chỉ có một dòng nên body rỗng, không phải bài trùng."""
    rows = q("""SELECT a.id, a.split, c.code, a.body_md5 FROM article a JOIN category c ON c.id = a.category_id
                JOIN (SELECT body_md5 FROM article GROUP BY body_md5 HAVING COUNT(*) > 1) d ON d.body_md5 = a.body_md5
                WHERE a.body_md5 <> UNHEX(MD5(''))""")
    groups = rows.groupby("body_md5")["code"].agg(set)
    return {r.id: (r.code, groups[r.body_md5]) for r in rows.itertuples()
            if r.split == "test" and len(groups[r.body_md5]) > 1}


@st.cache_data(ttl=3600)
def error_stats(run_id):
    """Số liệu phân tích lỗi của một lần chạy: hạng của nhãn đúng, ngưỡng tin cậy, nhiễu nhãn.
    Cache theo run_id nên luôn khớp với ma trận nhầm lẫn của cùng lần chạy."""
    p = q("""SELECT p.article_id, ct.code AS true_code, cp.code AS pred_code, p.proba FROM prediction p
             JOIN article a ON a.id = p.article_id AND a.split = 'test'
             JOIN category ct ON ct.id = a.category_id JOIN category cp ON cp.id = p.pred_category_id
             WHERE p.run_id = %s""", (run_id,))
    proba = p.proba.map(json.loads)
    err = p.true_code != p.pred_code
    rank = pd.Series([sorted(d, key=d.get, reverse=True).index(t) + 1 for d, t in zip(proba[err], p.true_code[err])])
    hi = proba.map(lambda d: max(d.values())) >= 0.9
    conf = dup_conflicts()
    dup = [(t != pc, pc in conf[a][1]) for a, t, pc in zip(p.article_id, p.true_code, p.pred_code) if a in conf]
    return {"n": len(p), "n_err": int(err.sum()), "rank2": float((rank == 2).mean()), "rank3": float((rank == 3).mean()),
            "cover": float(hi.mean()), "acc_hi": float((~err[hi]).mean()),
            "n_conf": len(dup), "dup_err": sum(w for w, _ in dup), "dup_lbl": sum(w and lbl for w, lbl in dup)}


def error_card(name, kind, cm, pc, tf):
    """Thẻ "Phân tích lỗi" bốn ô theo ảnh mẫu; mọi con số tính từ lần chạy đang chọn, không viết cứng."""
    _, clf = load()
    clf_name = lambda c: clf.cat_name.get(c, c)
    es = error_stats(int(cm.run_id.iloc[0]))
    off = cm[cm.true_code != cm.pred_code]
    pairs = (off.assign(pair=[" ↔ ".join(sorted(x)) for x in zip(off.true_code, off.pred_code)])
             .groupby("pair")["n"].sum().nlargest(5))
    share = pairs.sum() / max(off.n.sum(), 1)
    cell1 = (f'<div><h4><span>1</span>Ranh giới mờ giữa chuyên mục</h4><div class="big">{pct(share)}</div>'
             f'<p>số lỗi rơi vào <b>5 cặp</b> chuyên mục giao thoa (tính cả hai chiều).</p>'
             + "".join(f'<div class="t2v-dist{" top" if i == 0 else ""}"><div class="hd"><span>{e(k)}</span>'
                       f'<b>{num(v)} bài</b></div>{bar(v / pairs.iloc[0], "" if i == 0 else "mid")}</div>'
                       for i, (k, v) in enumerate(pairs.items())) + "</div>")
    f1 = pc.f1.sort_values()
    weak = list(f1.index[:2])
    smallest = set(pc.n.nsmallest(2).index) == set(weak)
    cell2 = (f'<div><h4><span>2</span>Chuyên mục yếu nhất</h4><div class="big">{vn(f1.iloc[0])}</div>'
             f'<p>F1 của <b>{e(clf_name(weak[0]))}</b>; tiếp theo là <b>{e(clf_name(weak[1]))}</b> ({vn(f1.iloc[1])}).'
             + (" Đây cũng là hai chuyên mục ít bài test nhất." if smallest else "") + "</p>"
             + "".join(f'<div class="t2v-dist{" top" if c in weak else ""}"><div class="hd"><span>{e(clf_name(c))}</span>'
                       f'<b>{vn(v)}</b></div>{bar((v - 0.5) / 0.5, "" if c in weak else "lo", "thin")}</div>'
                       for c, v in f1.iloc[:5].items())
             + f'<p style="margin-top:12px">5 chuyên mục F1 thấp nhất; cao nhất là {e(clf_name(f1.index[-1]))} '
               f'({vn(f1.iloc[-1])}).</p></div>')
    cell3 = (f'<div><h4><span>3</span>Nhiễu nhãn trong dữ liệu</h4>'
             f'<div class="big">≥ {pct(es["dup_lbl"] / max(es["n_err"], 1))}</div>'
             f'<p>số lỗi không thể tránh. <b>{num(es["n_conf"])}</b> bài test trùng nội dung với một bài mang nhãn khác; '
             f'mô hình sai <b>{num(es["dup_err"])}</b> bài trong số đó, và ở <b>{num(es["dup_lbl"])}</b> bài nhãn đoán '
             f'chính là nhãn của bản sao.</p>'
             + "".join(f'<div class="t2v-dist{" top" if i == 2 else ""}"><div class="hd"><span>{k}</span>'
                       f'<b>{num(v)} bài</b></div>{bar(v / max(es["n_conf"], 1), "" if i == 2 else "lo", "thin")}</div>'
                       for i, (k, v) in enumerate([("Trùng nội dung, khác nhãn", es["n_conf"]),
                                                   ("Mô hình đoán sai", es["dup_err"]),
                                                   ("Đoán đúng nhãn của bản sao", es["dup_lbl"])]))
             + "</div>")
    rest = max(1 - es["rank2"] - es["rank3"], 0.0)
    cell4 = (f'<div><h4><span>4</span>Lỗi sát nút</h4><div class="big">{pct(es["rank2"])}</div>'
             f'<p>số bài sai có nhãn đúng đứng <b>hạng 2</b>.</p>'
             + "".join(f'<div class="t2v-dist{" top" if i == 0 else ""}"><div class="hd"><span>{k}</span><b>{pct(v)}</b></div>'
                       f'{bar(v, "" if i == 0 else "lo", "thin")}</div>'
                       for i, (k, v) in enumerate([("Nhãn đúng ở hạng 2", es["rank2"]), ("Hạng 3", es["rank3"]),
                                                   ("Hạng 4 trở xuống", rest)]))
             + f'<p style="margin-top:12px">Chỉ tự gán khi xác suất ≥ 0,9: phủ <b>{pct(es["cover"])}</b> số bài với '
               f'accuracy <b>{vn(es["acc_hi"])}</b>; phần còn lại chuyển người duyệt.'
             + (" Với mốc gốc, “xác suất” là softmax điểm SVM." if kind == "trans2vec-orig" else "") + "</p></div>")
    if tf is not None and kind != "tfidf":
        worse = int((pc.f1 < tf.f1.reindex(pc.index)).sum())
        tail = (f" Tuy vậy {e(name)} vẫn kém TF-IDF ở <b>{worse}/{len(pc)}</b> chuyên mục, "
                "nên giới hạn của biểu diễn cũng góp phần, không chỉ dữ liệu.") if worse else ""
    else:
        tail = ""
    concl = (f'<div class="t2v-concl">Phần lớn lỗi gắn với đặc điểm dữ liệu: <b>{pct(share)}</b> nằm ở 5 cặp chuyên mục '
             f'giao thoa và ít nhất <b>{pct(es["dup_lbl"] / max(es["n_err"], 1))}</b> do nhiễu nhãn.{tail}</div>')
    st.html(f'<div class="t2v-card" style="margin-bottom:20px">'
            + card_head("Phân tích lỗi: giới hạn của mô hình nằm ở đâu?",
                        f"{e(name)} · {num(es['n_err'])} lỗi trên {num(es['n'])} bài test; tính từ <b>prediction</b>, "
                        "<b>v_confusion</b> và <b>body_md5</b>.", tag="Bước 09")
            + f'<div class="t2v-err">{cell1}{cell2}{cell3}{cell4}</div>{concl}</div>')


def per_class(cm):
    """P/R/F1 từng chuyên mục suy từ ma trận nhầm lẫn: eval_result chỉ lưu accuracy và Macro-F1."""
    hit = cm[cm.true_code == cm.pred_code].set_index("true_code")["n"]
    t = pd.DataFrame({"n": cm.groupby("true_code")["n"].sum(), "pred": cm.groupby("pred_code")["n"].sum(), "tp": hit}).fillna(0)
    t["p"], t["r"] = t.tp / t.pred, t.tp / t.n  # 0/0 → NaN (chuyên mục không được đoán / không có bài)
    t["f1"] = 2 * t.p * t.r / (t.p + t.r)
    return t.fillna(0)


def highlight(text, words, folded=False):
    """Tô các âm tiết thuộc từ trong `words` (token pyvi dạng a_b); folded: so khớp sau khi gộp dấu."""
    norm = fold if folded else str.lower
    syl = {norm(p) for w in words for p in w.split("_")}
    out = []
    for tok in html.escape(text).split(" "):
        core = norm(tok.strip(".,;:!?\"'()"))
        out.append(f"<mark>{tok}</mark>" if core in syl else tok)
    return " ".join(out)


@st.cache_data(ttl=3600)
def samples():
    # mỗi chuyên mục một bài test 150–250 từ mà mô hình mới nhất (LR) phân loại đúng: ví dụ minh họa không gây hiểu nhầm
    return q("""SELECT a.id, cat.code, cat.name, a.title, a.body FROM article a JOIN category cat ON cat.id = a.category_id
                WHERE a.id IN (SELECT MIN(a2.id) FROM article a2 JOIN prediction p ON p.article_id = a2.id
                               AND p.run_id = (SELECT MAX(id) FROM model_run WHERE kind = 'lr')
                               WHERE a2.split = 'test' AND a2.n_word BETWEEN 150 AND 250
                                 AND p.pred_category_id = a2.category_id
                               GROUP BY a2.category_id) ORDER BY cat.id""")


# ===================================================================== Phân loại
def _load_example():
    pick = st.session_state.ex_pick
    if pick:
        r = samples().set_index("name").loc[pick]
        st.session_state.text = f"{r['title']}\n{r['body']}"


def page_classify():
    _, clf = load()
    n = len(clf.models)
    _, _, n_test = corpus()
    topbar("Phân loại bài báo", f"So sánh {n} mô hình trên cùng một bài: mốc Trans2Vec gốc, 4 biến thể và mô hình cải tiến.")
    banner("Ghi chú", f"Dự đoán chạy bằng các mô hình thật nạp từ <b>src/system/models/</b>; Macro-F1 đo trên "
                      f"<b>{num(n_test)}</b> bài test VNTC-10 (bảng <b>eval_result</b>). Mốc học transductive trên cả "
                      "văn bản test như mã tác giả, nên Macro-F1 của mốc là con số có lợi cho mốc.")
    ex = samples()
    emoji = dict(zip(ex["name"], (CAT_STYLE.get(c, ("",))[0] for c in ex["code"])))
    cur = st.session_state.get("text", "")
    with st.container(key="card_input"):
        st.html(card_head("Nội dung bài báo cần phân tích", "Dán nội dung (tiêu đề + thân bài) hoặc chọn một đoạn ví dụ, "
                          "rồi bấm <b>Phân loại ngay</b>.", h="h2",
                          right=f'<div class="t2v-cnts"><span class="t2v-cnt">{num(len(cur))} ký tự</span>'
                                f'<span class="t2v-cnt">{num(len(cur.split()))} từ</span></div>'))
        text = st.text_area("Nội dung bài báo", key="text", height=170, label_visibility="collapsed",
                            placeholder="Ví dụ: Công an tỉnh vừa bắt giữ đối tượng có hành vi lừa đảo chiếm đoạt tài sản…")
        st.pills("⚡ Đoạn ví dụ nhanh (bài test được mô hình phân loại đúng)", ex["name"].tolist(), key="ex_pick",
                 format_func=lambda c: f"{emoji.get(c, '')} {c}", on_change=_load_example)
        c1, c2, c3 = st.columns([1.3, 0.8, 5], vertical_alignment="center")
        go = c1.button("Phân loại ngay", type="primary", icon=":material/science:", disabled=not text.strip(),
                       width="stretch")
        c2.button("Xóa", icon=":material/delete:", width="stretch",
                  on_click=lambda: st.session_state.update(text="", ex_pick=None, clf_result=None))
        c3.html('<div class="t2v-foot"><span class="dot sm"></span><span class="t2v-mono">Tách từ: <code>pyvi</code></span>'
                f'<span>·</span><span>{n} mô hình chạy song song, Macro-F1 đo trên <b>{num(n_test)}</b> bài test</span></div>')
    # Bấm chọn mô hình làm Streamlit chạy lại script và nút "Phân loại ngay" trở về False, nên phải giữ kết quả
    # trong session; nhờ vậy đổi mô hình không dự đoán lại và không ghi thêm dòng classify_log.
    if go:
        st.session_state.clf_result = {"text": text, "r": clf.predict(text, log=True)}
        st.session_state.clf_sel = None
    res = st.session_state.get("clf_result")
    if not res or res["text"] != text:  # đã sửa nội dung: kết quả cũ không còn ứng với bài đang nhập
        return

    r = res["r"]
    models = r["models"]
    ok = [m for m in models if m["proba"]]
    if not ok:
        st.warning("Không có item nào của bài nằm trong từ vựng của các mô hình. Thử một đoạn dài hơn.")
        return
    best = max(m["f1"] for m in models)
    base = next((m["f1"] for m in models if m["kind"] == "trans2vec-orig"), None)
    main = next((m for m in ok if m["improved"]), None) or max(ok, key=lambda m: m["f1"])
    sel = next((m for m in ok if m["kind"] == st.session_state.get("clf_sel")), main)
    votes = pd.Series([m["proba"][0][1] for m in ok]).value_counts()
    st.html(f'<div class="t2v-res"><div style="display:flex;gap:10px;align-items:center"><h3><span class="dot i"></span>'
            f'Kết quả phân loại và dự đoán chủ đề</h3><span class="t2v-done"><span class="dot sm g"></span>'
            f'Hoàn tất ({r["ms"]:.0f} ms)</span></div><span class="t2v-mono"><b>{votes.iloc[0]}/{n}</b> mô hình chọn '
            f'“{e(votes.index[0])}”</span></div>')

    code, name, p = main["proba"][0]
    em = CAT_STYLE.get(code, ("📰",))[0]
    card1 = (f'<div class="t2v-card"><div class="t2v-ch nb"><span class="t2v-k"><span class="dot sm"></span>Chuyên mục chính'
             f'</span><span class="t2v-k cy">{e(main["name"])}</span></div>'
             f'<div class="t2v-main"><div class="t2v-emo">{em}</div><div><div class="t2v-big">{e(name)}</div>'
             f'<div class="t2v-mono" style="margin-top:4px">Mã nhãn VNTC: <b>{e(code)}</b></div></div></div>'
             f'<div class="t2v-lbl"><span>Xác suất của mô hình cải tiến</span><b>{pct(p)}</b></div>{bar(p, kind="big")}'
             f'<div class="t2v-sep"></div><div class="t2v-cap">Item của bài (top tf·idf)</div>{chips(r["items"][:8], hi=3)}</div>')
    dist = "".join(f'<div class="t2v-dist{" top" if i == 0 else ""}"><div class="hd"><span>{i + 1}. {e(nm)}</span>'
                   f'<b>{pct(x)}</b></div>{bar(x, "" if i == 0 else "lo")}</div>'
                   for i, (_, nm, x) in enumerate(main["proba"][:5]))
    top5 = sum(x for _, _, x in main["proba"][:5])
    card3 = (f'<div class="t2v-card"><div class="t2v-ch nb"><span class="t2v-k"><span class="dot sm"></span>'
             f'Phân bố xác suất đa chuyên mục</span><span class="t2v-k cy">Top 5</span></div>{dist}'
             f'<div class="t2v-cfoot"><span>Mô hình: <b>{e(main["name"])}</b></span><span>Top 5 = {pct(top5)}</span></div></div>')

    def model_row(m):
        hl = m is sel
        if m["proba"]:
            _, nm, x = m["proba"][0]
            right = f'{e(nm)} · <b>{pct(x)}</b>'
        else:
            x, right = 0.0, "—"
        delta = "mốc" if base is None or m["kind"] == "trans2vec-orig" else vn(m["f1"] - base).replace("-", "−")
        delta = delta if delta == "mốc" or delta.startswith("−") else "+" + delta
        star = ' <span class="t2v-tag g">F1 cao nhất</span>' if m["f1"] == best else ""
        # chữ "Đang xem": trạng thái chọn không chỉ dựa vào màu nền
        seen = ' <span class="t2v-tag i">Đang xem</span>' if hl else ""
        return (f'<div class="t2v-mrow{" hl" if hl else ""}"><div class="hd"><span class="nm"><span class="dot sm'
                f'{"" if hl else " off"}"></span>{e(m["name"])}</span><span class="pv">{right}</span></div>'
                f'{bar(x, "" if hl else "lo", "thin")}<div class="ds">{e(m["note"])} · Macro-F1 {vn(m["f1"])} '
                f'({delta}){star}{seen}</div></div>')

    # Thẻ giữa phải dùng widget thật để bấm được; st.html không gửi được sự kiện về Python.
    with st.container(key="clf_grid"):
        col1, col2, col3 = st.columns(3, gap="medium")
        col1.html(card1)
        with col2.container(key="card_models"):
            st.html(f'<div class="t2v-ch nb"><span class="t2v-k"><span class="dot sm i"></span>So sánh {n} mô hình</span>'
                    '<span class="t2v-tag i">Bấm để xem chi tiết</span></div>')
            for m in models:
                with st.container(key=f"mrow_{m['kind']}"):
                    st.html(model_row(m))
                    st.button(f"{'Đang xem' if m is sel else 'Xem'} {m['name']}", key=f"pick_{m['kind']}",
                              disabled=not m["proba"], on_click=st.session_state.update, kwargs={"clf_sel": m["kind"]})
            st.html('<div class="t2v-cfoot"><span>* Điểm của mốc là softmax điểm quyết định SVM, không phải xác suất.</span></div>')
        col3.html(card3)

    # TRANS-IT chỉ dùng item, TRANS-FI chỉ dùng FI; các mô hình còn lại dùng cả hai.
    uses_fi, uses_items = sel["kind"] != "trans-it", sel["kind"] != "trans-fi"
    marked = {w for f in r["fi"] for w in f} if uses_fi else set(r["items"][:20])
    what = "Từ thuộc FI khớp" if uses_fi else "Item top tf·idf"
    fi = (chips([" + ".join(f) for f in r["fi"][:16]], cls="fi") if r["fi"] else
          '<div class="t2v-mono">Không có FI nào đủ các từ; dự đoán dựa trên item đơn.</div>')
    side = (f'<div class="t2v-cap">Top 3 dự đoán ({"softmax điểm SVM" if sel["kind"] == "trans2vec-orig" else "xác suất"})</div>'
            + "".join(f'<div class="t2v-dist{" top" if i == 0 else ""}"><div class="hd"><span>{i + 1}. {e(nm)}</span>'
                      f'<b>{pct(x)}</b></div>{bar(x, "" if i == 0 else "lo")}</div>'
                      for i, (_, nm, x) in enumerate(sel["proba"][:3])))
    if uses_fi:
        side += f'<div class="t2v-sep"></div><div class="t2v-cap">FI khớp (độ dài ≥ 2)</div>{fi}'
    if uses_items:
        side += f'<div class="t2v-sep"></div><div class="t2v-cap">Item của bài (top tf·idf)</div>{chips(r["items"][:20])}'
    why = f"Vì sao {sel['name']} chọn “{sel['proba'][0][1]}”?"
    st.html(f'<div class="t2v-card" style="margin-top:20px">'
            + card_head(why, f"{e(sel['note'])}. {what} được tô sáng trong bài. Đây là đầu vào của mô hình; "
                             "ứng dụng chưa đo mức đóng góp của từng từ.")
            + f'<div class="t2v-split"><div><div class="t2v-text">{highlight(text, marked)}</div></div>'
              f'<div>{side}</div></div></div>')

    rows = [{"Mô hình": m["name"], "Dự đoán": m["proba"][0][1] if m["proba"] else "—",
             "Xác suất": m["proba"][0][2] if m["proba"] else 0.0, "Macro-F1": f"{m['f1']:.3f}",
             "So với mốc": "mốc" if m["kind"] == "trans2vec-orig" or base is None else f"{m['f1'] - base:+.3f}",
             "Cách tạo": m["note"]} for m in models]
    st.write("")
    with st.expander("Bảng so sánh chi tiết"):
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", column_config={
            "Xác suất": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1),
            "Cách tạo": st.column_config.TextColumn(width="large")})


# ===================================================================== Tìm kiếm
def _load_query():
    if st.session_state.sq_pick:
        st.session_state.query = st.session_state.sq_pick


def stat_cards(items):
    """4 ô chỉ số có icon: [(icon, tông, nhãn, giá trị, dòng phụ, tô màu giá trị)]."""
    st.html('<div class="t2v-grid4">' + "".join(
        f'<div class="t2v-stat"><div class="ib {tone}">{icon(ic)}</div><div><div class="lb">{e(lb)}</div>'
        f'<div class="vl {vc}">{e(vl)}</div><div class="sb">{e(sb)}</div></div></div>'
        for ic, tone, lb, vl, sb, vc in items) + "</div>")


def page_search():
    s, _ = load()
    _, n_train, _ = corpus()
    topbar("Tìm kiếm nâng cao", f"Manticore Search trên kho {num(n_train)} bài train: BM25, vector HNSW và hybrid RRF.")
    cats = q("SELECT id, code, name FROM category ORDER BY id")
    ndcg = q("""SELECT e.kind, ev.value FROM eval_result ev JOIN model_run e ON e.id = ev.run_id
                WHERE ev.task='search' AND ev.metric='ndcg@10'""").set_index("kind")["value"]
    ndcg_joi = ("chart", "indigo", "nDCG@10 Trans2Vec-JOI",
                vn(ndcg["trans2vec-joi"]) if "trans2vec-joi" in ndcg else "—", "1.000 truy vấn là bài báo", "cyan")
    stats = st.empty()  # ô chỉ số đứng trên thẻ truy vấn như template, điền sau khi có kết quả
    with st.container(key="card_query"):
        st.html(card_head("Truy vấn và bộ lọc", "Gõ có dấu hoặc không dấu; truy vấn không dấu dùng trường đã gộp dấu."))
        query = st.text_input("Từ khóa", key="query", placeholder="Nhập cụm từ tìm kiếm, ví dụ: giá vàng tăng mạnh")
        c1, c2, c3 = st.columns([6, 3, 3])
        mode = MODES[c1.segmented_control("Chế độ tìm kiếm", list(MODES), default="Hybrid (RRF)", key="mode")
                     or "Hybrid (RRF)"]
        cat = c2.selectbox("Chuyên mục", [None] + cats["id"].tolist(),
                           format_func=lambda i: "Tất cả chuyên mục" if i is None else cats.set_index("id").loc[i, "name"])
        k = c3.selectbox("Số kết quả", [5, 10, 20], index=1, format_func=lambda x: f"Top {x}")
        st.html(f'<div class="t2v-note">{e(MODE_DESC[mode])}</div>')
        st.pills("⚡ Truy vấn mẫu", SAMPLE_QUERIES, key="sq_pick", on_change=_load_query)
    if not query.strip():
        with stats.container():
            stat_cards([("list", "cyan", "Kết quả", "—", "chưa có truy vấn", ""),
                        ("trend", "amber", "Điểm cao nhất", "—", MODE_LABEL[mode], "amber"),
                        ("tag", "emerald", "Chuyên mục xuất hiện", "—", "trong kết quả hiển thị", ""), ndcg_joi])
        st.info("Nhập từ khóa hoặc chọn một truy vấn mẫu.")
        return
    res = s.search(query, mode=mode, k=k, category_id=cat, log=True)
    hits = res["hits"]
    det = s.details([h["id"] for h in hits])
    with stats.container():
        stat_cards([("list", "cyan", "Kết quả", len(hits), f"{res['ms']:.0f} ms", ""),
                    ("trend", "amber", "Điểm cao nhất", vn(hits[0]["score"], 4) if hits else "—", MODE_LABEL[mode], "amber"),
                    ("tag", "emerald", "Chuyên mục xuất hiện", len({det[h["id"]]["code"] for h in hits}),
                     "trong kết quả hiển thị", ""), ndcg_joi])
    if not hits:
        st.warning("Không có kết quả. Thử truy vấn khác, đổi chế độ hoặc bỏ lọc chuyên mục.")
        return
    notes = []
    if res["folded"]:
        notes.append("Truy vấn không dấu: BM25 tìm trên trường đã gộp dấu (title_fold, body_fold)."
                     + {"hybrid": " Chế độ hybrid chỉ dùng BM25, vì vector suy luận từ chữ không dấu kém tin cậy.",
                        "knn": " Vector suy luận từ chữ không dấu nên kém tin cậy; nên dùng BM25 hoặc hybrid."}.get(mode, ""))
    if res["query_fi"]:
        notes.append("FI của truy vấn: " + ", ".join(" + ".join(f) for f in res["query_fi"]))
    if notes:
        st.html("".join(f'<div class="t2v-note" style="margin:16px 0 0">{e(x)}</div>' for x in notes))
    st.write("")

    left, right = st.columns([7, 5], gap="medium")
    with right:
        pick = st.selectbox("Chi tiết bài viết", [h["id"] for h in hits],
                            format_func=lambda i: f"#{next(h['rank'] for h in hits if h['id'] == i)} {det[i]['title'][:60]}")
    top = hits[0]["score"] or 1.0
    trs = ""
    for h in hits:
        d = det[h["id"]]
        sel = h["id"] == pick
        snip = d["snippet"].replace("\n", " ")
        trs += (f'<tr class="{"sel" if sel else ""}"><td class="c n">{h["rank"]}</td>'
                f'<td><div class="tt">{e(d["title"])}</div><div class="sn">{e(snip[:90])}…</div>'
                f'<div class="fl path" title="{e(d["file"])}">{e(d["file"])}</div></td><td>{cat_chip(d["code"], d["category"])}</td>'
                f'<td class="n" style="font-size:10px;color:var(--t2v-text-2)">{e(", ".join(d["fi"][:2])) or "—"}</td>'
                f'<td class="r"><span class="sc">{vn(h["score"], 4)}</span>'
                f'{bar(h["score"] / top, "" if sel else "mid", "thin")}'
                f'<div class="fl">BM25 #{h["bm25_rank"] or "—"} · vec #{h["knn_rank"] or "—"}</div></td></tr>')
    left.html(f'<div class="t2v-card flat"><div class="t2v-ch" style="padding:16px 20px;margin:0;border-color:rgb(var(--t2v-ink-rgb) / .1)">'
              f'<div><h3><span class="dot sm"></span>Kết quả tìm kiếm</h3><p>Manticore · kho {num(n_train)} bài train · '
              f'đã khử bài trùng nội dung</p></div><span class="t2v-tag">BM25 + HNSW</span></div>'
              f'<div style="overflow-x:auto"><table class="t2v-table"><thead><tr><th class="c">#</th><th>Bài viết</th>'
              f'<th>Chuyên mục</th><th style="width:120px">FI trong bài</th><th class="r">Điểm</th></tr></thead><tbody>{trs}</tbody></table></div>'
              f'<div class="t2v-tfoot"><span>Hiển thị {len(hits)} kết quả · sắp theo điểm giảm dần</span>'
              f'<span>{e(MODE_LABEL[mode])}</span></div></div>')

    h, d = next(h for h in hits if h["id"] == pick), det[pick]
    hyb = mode == "hybrid"
    boxes = (f'<div><span>BM25</span><b>{vn(h["bm25"], 0) if h["bm25"] else "—"}</b><small>hạng {h["bm25_rank"] or "—"}</small></div>'
             f'<div><span>Vector</span><b>{vn(h["knn"]) if h["knn"] else "—"}</b><small>hạng {h["knn_rank"] or "—"}</small></div>'
             f'<div class="on"><span>{"RRF" if hyb else "Điểm"}</span><b>{vn(h["score"], 4)}</b>'
             f'<small>{"k = 60" if hyb else MODE_LABEL[mode]}</small></div>')
    counts = pd.Series([det[x["id"]]["code"] for x in hits]).value_counts()
    names = cats.set_index("code")["name"]
    dist = "".join(f'<div class="t2v-dist{" top" if i == 0 else ""}"><div class="hd"><span>{cat_chip(c, names[c], True)}</span>'
                   f'<b>{v} bài</b></div>{bar(v / len(hits), "" if i == 0 else "lo")}</div>'
                   for i, (c, v) in enumerate(counts.items()))
    right.html(f'<div class="t2v-card">{card_head("Chi tiết bài viết", tag=d["split"])}'
               f'<div style="display:flex;gap:8px">{cat_chip(d["code"], d["category"], True)}'
               f'<span class="t2v-cat gray">Hạng #{h["rank"]}</span></div><div class="t2v-art">{e(d["title"])}</div>'
               f'<div class="t2v-text">{highlight(d["snippet"] + "…", res["words"], res["folded"])}</div>'
               f'<div class="t2v-sc3">{boxes}</div><div class="t2v-meta">'
               f'<div><span>FI trong bài:</span><span>{e(", ".join(d["fi"][:10])) or "không có"}</span></div>'
               f'<div><span>Tệp nguồn:</span><span class="file">{e(d["file"])}</span></div></div></div>'
               f'<div class="t2v-card" style="margin-top:20px">{card_head("Phân bố theo chuyên mục", tag=f"{len(hits)} bài")}{dist}</div>')


# ===================================================================== Dữ liệu và đánh giá
def simple_table(head, rows, row_cls=None):
    """Bảng HTML t2v-table: cột đầu căn trái, các cột số căn giữa. Ô là HTML, hoặc (HTML, class thêm) như
    (“0,907”, "best"); row_cls(i) trả class cho hàng (ví dụ "hl")."""
    cell = lambda v: v if isinstance(v, tuple) else (v, "")
    th = "".join(f"<th>{e(h)}</th>" if j == 0 else f'<th class="c">{e(h)}</th>' for j, h in enumerate(head))
    tr = "".join(f'<tr class="{row_cls(i) if row_cls else ""}">' + "".join(
        f"<td>{cell(v)[0]}</td>" if j == 0 else f'<td class="c n {cell(v)[1]}">{cell(v)[0]}</td>'
        for j, v in enumerate(r)) + "</tr>" for i, r in enumerate(rows))
    return f'<div class="t2v-tw"><table class="t2v-table"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


def eval_table(t, cols, hl_row):
    """Bảng đánh giá: hàng hl_row được tô như template, giá trị lớn nhất mỗi cột in đậm."""
    best = {c: t[c].max() for c, _ in cols}
    names = list(t.index)
    rows = [[f'<span class="dot sm"></span> {e(n)}' if n == hl_row else e(n)]
            + [(vn(r[c]), "best" if r[c] == best[c] else "") if pd.notna(r[c]) else "—" for c, _ in cols]
            for n, r in t.iterrows()]
    return simple_table(["Biểu diễn"] + [lb for _, lb in cols], rows, row_cls=lambda i: "hl" if names[i] == hl_row else "")


def page_data():
    _, clf = load()
    total, n_train, n_test = corpus()
    topbar("Dữ liệu và đánh giá", "Số liệu thực nghiệm đọc trực tiếp từ MariaDB: model_run, eval_result và các view.")
    banner("Ghi chú", "Mọi số trên trang này lấy từ bảng <b>eval_result</b> và các view của MariaDB. Với tìm kiếm, "
                      "“liên quan” = cùng chuyên mục (proxy), chưa phải nhãn liên quan do người đánh giá.")
    fim = q("SELECT JSON_VALUE(params,'$.delta') delta, JSON_VALUE(metrics,'$.n_fi') n_fi FROM model_run WHERE kind='fim' ORDER BY id DESC LIMIT 1")
    dup = q("SELECT COUNT(*) - COUNT(DISTINCT body_md5) n FROM article")["n"][0]
    kpis = [("Chuyên mục", "10", "VNTC-10", ""),
            ("Bài train / test", f'{num(n_train)} <small>/</small> {num(n_test)}', "cách chia gốc", "sm"),
            ("Ngưỡng δ (elbow)", f"{float(fim['delta'][0]) * 100:.3f}%".replace(".", ","), "khai phá FI trên train", "cyan"),
            ("Số FI (độ dài ≤ 3)", num(fim["n_fi"][0]), "tất cả đều là FI đóng", ""),
            ("Bài trùng nội dung", num(dup), "3.056 bài test có bản sao trong train", "")]
    st.html(f'<div class="t2v-card" style="margin-bottom:20px">'
            f'{card_head("Dữ liệu VNTC-10", tag="Metadata", right="")}<div class="t2v-grid5">' + "".join(
                f'<div class="t2v-kpi"><div class="lb">{e(a)}</div><div class="vl {vc}">{b}</div>'
                f'<div class="sb">{e(c)}</div></div>'
                for a, b, c, vc in kpis) + "</div></div>")

    names = {"tfidf": "TF-IDF toàn văn", **{k: n for k, n, _ in Classifier.KINDS}}
    ev = q("""SELECT e.kind, ev.metric, ev.value FROM eval_result ev JOIN model_run l ON l.id = ev.run_id
              JOIN model_run e ON e.id = l.parent_id WHERE l.id IN (""" + LATEST_CLF + """) AND ev.metric IN ('acc','macro_f1')
              UNION ALL
              SELECT e.kind, ev.metric, ev.value FROM eval_result ev JOIN model_run e ON e.id = ev.run_id
              WHERE ev.task='search' AND e.id IN (""" + LATEST_SEARCH + ")")
    ev["Biểu diễn"] = ev["kind"].map(names)
    t = ev.pivot_table(index="Biểu diễn", columns="metric", values="value")
    # đủ cột kể cả khi chưa có dự đoán / kết quả tìm kiếm, để bảng hiện "—" thay vì KeyError
    t = t.reindex(index=[n for n in names.values() if n in t.index],
                  columns=["acc", "p_macro", "r_macro", "macro_f1", "p@10", "map@100", "ndcg@10"])
    cms = confusion()
    pcs = {kind: per_class(g) for kind, g in cms.groupby("kind")}  # tính một lần, thẻ bên dưới dùng lại
    for kind, pc in pcs.items():  # precision / recall macro: trung bình đều 10 chuyên mục
        if kind in names and names[kind] in t.index:
            t.loc[names[kind], ["p_macro", "r_macro"]] = round(pc.p.mean(), 4), round(pc.r.mean(), 4)
    joi = names["trans2vec-joi"]  # tìm kiếm dùng JOI; phân loại dùng mô hình cải tiến như thanh trên
    best = names.get(next((m["kind"] for m in clf.models if m["improved"]), "trans2vec-joi"), joi)
    st.html(f'<div class="t2v-split" style="grid-template-columns:1fr 1fr;margin-bottom:20px">'
            f'<div class="t2v-card">{card_head(f"Phân loại · {num(n_test)} bài test", "LR (mốc: LinearSVC). Precision, Recall, F1: macro.", tag="Macro")}'
            f'{eval_table(t[["acc", "p_macro", "r_macro", "macro_f1"]].dropna(how="all"), [("acc", "Accuracy"), ("p_macro", "Precision"), ("r_macro", "Recall"), ("macro_f1", "F1")], best)}</div>'
            f'<div class="t2v-card">{card_head("Tìm kiếm · 1.000 truy vấn là bài báo", "Cosine vét cạn trên vector của từng biểu diễn.", tag="Ranking", dot="i")}'
            f'{eval_table(t[["p@10", "map@100", "ndcg@10"]].dropna(how="all"), [("p@10", "P@10"), ("map@100", "MAP@100"), ("ndcg@10", "nDCG@10")], joi)}'
            f'<div class="t2v-cfoot"><span>“Liên quan” = cùng chuyên mục (proxy).</span></div></div></div>')

    a, b = st.columns(2, gap="medium")
    with a.container(key="card_cm"):
        st.html(card_head("Ma trận nhầm lẫn", "Số bài trong ô; màu = tỉ lệ theo hàng (chuyên mục thực tế), view <b>v_confusion</b>."))
        kinds = [k for k in names if names[k] in t.index and k in set(cms.kind)]
        default = next((k for k in ("trans2vec-cat", "trans2vec-joi") if k in kinds), None)
        kind = st.selectbox("Biểu diễn", kinds, format_func=names.get, index=kinds.index(default) if default else 0)
        cm = cms[cms.kind == kind].copy()
        cm["tỉ lệ"] = cm["n"] / cm.groupby("true_code")["n"].transform("sum")
        base = alt.Chart(cm).encode(x=alt.X("pred_code:N", title="Dự đoán"), y=alt.Y("true_code:N", title="Thực tế"))
        heat_colors = theme.heat(name)
        heat = base.mark_rect(stroke=heat_colors["stroke"], strokeWidth=2, cornerRadius=3).encode(
            color=alt.Color("tỉ lệ:Q", scale=alt.Scale(range=heat_colors["range"]),
                            legend=alt.Legend(format=".0%")),
            tooltip=["true_code", "pred_code", "n", alt.Tooltip("tỉ lệ:Q", format=".1%")])
        # ô đường chéo nền sáng → chữ tối; ô lỗi nền tối → chữ sáng, ẩn ô < 20 bài cho đỡ rối
        text = base.transform_filter("datum.n >= 20").mark_text(font="JetBrains Mono", fontSize=10).encode(
            text="n:Q", color=alt.condition("datum['tỉ lệ'] > 0.5", alt.value(heat_colors["text_hi"]), alt.value(heat_colors["text_lo"])))
        st.altair_chart(theme.chart((heat + text).properties(height=380), name), width="stretch", theme=None)
    with b.container(key="card_perclass"):
        cat = clf.cat_name
        if kind not in pcs:  # lần chạy chưa có dòng prediction
            st.html(card_head("Precision · Recall · F1 theo chuyên mục", f"{e(names.get(kind, '—'))}: chưa có dự đoán trên tập test."))
        else:
            pc = pcs[kind]
            worst = pc.f1.idxmin()
            errs = cm[cm.true_code != cm.pred_code]
            off = errs.nlargest(1, "n").iloc[0] if not errs.empty else None
            st.html(card_head("Precision · Recall · F1 theo chuyên mục", f"{e(names[kind])}; suy từ ma trận nhầm lẫn bên trái.",
                              tag=f"Acc {vn(pc.tp.sum() / pc.n.sum())}"))
            st.html(simple_table(["Chuyên mục", "Số bài", "Precision", "Recall", "F1"],
                                 [[cat_chip(c, cat.get(c, c)), num(r.n), vn(r.p), vn(r.r),
                                   f"<b>{vn(r.f1)}</b>" if c == worst else vn(r.f1)] for c, r in pc.iterrows()])
                    + f'<div class="t2v-cfoot"><span>Yếu nhất: <b>{e(cat.get(worst, worst))}</b> (F1 {vn(pc.f1[worst])})</span>'
                    + (f'<span>Nhầm nhiều nhất: {e(off.true_code)} → {e(off.pred_code)} ({num(off.n)} bài)</span>'
                       if off is not None else "<span>Không có lỗi</span>") + "</div>")

    if kind in pcs:
        error_card(names[kind], kind, cm, pcs[kind], pcs.get("tfidf"))

    cs = q("SELECT code, name, split, n_article, avg_words FROM v_corpus_stats ORDER BY code")
    cs = cs.pivot_table(index=["code", "name"], columns="split", values=["n_article", "avg_words"], sort=False)
    st.html(f'<div class="t2v-card">{card_head("Thống kê corpus", "Số bài và số từ trung bình theo chuyên mục, view <b>v_corpus_stats</b>.")}'
            + simple_table(["Chuyên mục", "Bài train", "Bài test", "TB từ (train)", "TB từ (test)"],
                           [[cat_chip(c, n), num(r[("n_article", "train")]), num(r[("n_article", "test")]),
                             num(r[("avg_words", "train")]), num(r[("avg_words", "test")])]
                            for (c, n), r in cs.iterrows()]) + "</div>")

    fi = q("""SELECT c.code, c.name, GROUP_CONCAT(v.label ORDER BY v.rk SEPARATOR '§') AS fi
              FROM v_category_fi v JOIN category c ON c.code = v.code WHERE v.rk <= 10 GROUP BY c.id ORDER BY c.id""")
    trs = "".join(f'<tr><td style="width:190px">{cat_chip(r.code, r.name, True)}</td><td>'
                  + chips(["{" + l.replace("|", ", ") + "}" for l in r.fi.split("§")], cls="fi") + "</td></tr>"
                  for r in fi.itertuples())
    logs = q("""SELECT 'tìm kiếm' AS loai, COUNT(*) n, ROUND(AVG(latency_ms)) tb_ms FROM search_log
                UNION ALL SELECT 'phân loại', COUNT(*), ROUND(AVG(latency_ms)) FROM classify_log""")
    log = " · ".join(f"{r.loai} {r.n} lượt" + (f", TB {r.tb_ms:.0f} ms" if r.n else "") for r in logs.itertuples())
    st.html(f'<div class="t2v-card" style="margin-top:20px">'
            f'{card_head("FI đặc trưng của từng chuyên mục", "View <b>v_category_fi</b>: FI độ dài ≥ 2 xuất hiện ở nhiều bài train nhất.", tag=f"{len(fi)}/10 chuyên mục")}'
            f'<div class="t2v-tw"><table class="t2v-table"><thead><tr><th>Chuyên mục</th><th>10 FI phổ biến nhất</th></tr></thead>'
            f'<tbody>{trs}</tbody></table></div><div class="t2v-cfoot"><span>Nhật ký: {e(log)}</span>'
            f'<span>VNTC-10 · {num(total)} bài</span></div></div>')


# ===================================================================== Tin mới nhất
def page_news():
    import fetch_news

    s, clf = load()
    topbar("Tin mới nhất", "Đọc RSS VnExpress · Tuổi Trẻ · Thanh Niên, phân loại bằng mô hình cải tiến.")
    banner("Ghi chú", "Chỉ đọc RSS công khai: tiêu đề, mô tả ngắn, link, ảnh; không tải trang bài viết. Trùng lặp chặn "
                      f"bằng SHA-1 của URL. Nút <b>Lấy tin ngay</b> chạy tối đa một lần mỗi {fetch_news.MIN_LOOP_MIN} phút.")
    src = q("""SELECT s.id, s.code, s.name, s.rss_url, s.last_fetch_at,
                      l.http_status, l.n_items, l.n_new, l.latency_ms, l.error
               FROM news_source s LEFT JOIN fetch_log l ON l.id = (SELECT MAX(id) FROM fetch_log WHERE source_id = s.id)
               WHERE s.active ORDER BY s.id""")
    recent = q("SELECT TIMESTAMPDIFF(MINUTE, MAX(last_fetch_at), UTC_TIMESTAMP()) m FROM news_source")["m"][0]
    wait = recent is not None and recent < fetch_news.MIN_LOOP_MIN
    nz = lambda v: int(v) if pd.notna(v) else 0  # cột số từ LEFT JOIN có thể là NaN
    cards = ""
    for r in src.itertuples():
        err = r.error if isinstance(r.error, str) and r.error else None
        code = nz(r.http_status)
        status = (f'<span class="t2v-st ok"><span class="dot sm g"></span>HTTP {code}</span>' if code == 200 and not err else
                  f'<span class="t2v-st bad" title="{e(err or "")}"><span class="dot sm r"></span>'
                  f'{e(err or (f"HTTP {code}" if code else "chưa lấy"))}</span>')
        url = r.rss_url.split("://", 1)[-1]
        cards += (f'<div class="t2v-src"><div class="hd"><h3>{e(r.name)}</h3>{status}</div><div class="url">{e(url)}</div>'
                  f'<div class="t2v-mini"><div><span>Tin trong feed</span><b>{nz(r.n_items)}</b></div>'
                  f'<div><span>Tin mới</span><b class="cy">{nz(r.n_new)}</b></div>'
                  f'<div><span>Độ trễ</span><b class="gr">{nz(r.latency_ms)} <small>ms</small></b></div></div></div>')
    st.html(f'<div class="t2v-grid3" style="margin-bottom:20px">{cards}</div>')

    last = pd.to_datetime(src["last_fetch_at"]).max()
    last = (f"{last.tz_localize('UTC').tz_convert('Asia/Ho_Chi_Minh'):%H:%M · %d/%m/%Y}" if pd.notna(last) else "chưa lấy")
    reset = lambda: st.session_state.update(nf_page=1)  # đổi bộ lọc thì quay về trang 1
    with st.container(key="card_feed"):
        head = st.empty()
        c1, c2, c4, c3 = st.columns([3.2, 1.35, 1.45, 1.5], vertical_alignment="center")
        pick = c1.segmented_control("Nguồn", ["Tất cả"] + src["name"].tolist(), default="Tất cả", key="news_src",
                                    label_visibility="collapsed", on_change=reset) or "Tất cả"
        f1, f2, f3, f4 = st.columns([2.5, 1.5, 2.2, 0.9], vertical_alignment="bottom")
        status = f1.segmented_control("Trạng thái", ["Tất cả", "Chưa phân loại", "Đã phân loại"], default="Tất cả",
                                      key="nf_status", on_change=reset) or "Tất cả"
        fcat = f2.selectbox("Chuyên mục", [None] + sorted(clf.cat_name), key="nf_cat", on_change=reset,
                           format_func=lambda c: "Tất cả chuyên mục" if c is None else clf.cat_name[c],
                           disabled=status == "Chưa phân loại", placeholder="Tất cả chuyên mục")
        kw = f3.text_input("Từ khóa (tiêu đề, mô tả)", key="nf_kw", on_change=reset, placeholder="Có dấu hoặc không dấu")
        size = f4.selectbox("Số tin / trang", [10, 20, 50], index=1, key="nf_size", on_change=reset)

        # điều kiện lọc ghép thành SQL có tham số (không nối chuỗi giá trị người dùng nhập)
        cond, args = [], []
        if pick != "Tất cả":
            cond.append("source_name = %s"); args.append(pick)
        if status == "Chưa phân loại":
            cond.append("pred_category IS NULL")
        elif status == "Đã phân loại":
            cond.append("pred_category IS NOT NULL")
        if fcat and status != "Chưa phân loại":
            cond.append("pred_category = %s"); args.append(fcat)
        if kw.strip():
            # %, _ và \ trong từ khóa là ký tự thường, không phải ký tự đại diện của LIKE
            like = "%" + kw.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
            cond.append("(title LIKE %s ESCAPE '\\\\' OR summary LIKE %s ESCAPE '\\\\')"); args += [like] * 2
        where = (" WHERE " + " AND ".join(cond)) if cond else ""
        cnt = q("SELECT COUNT(*) n, COALESCE(SUM(pred_category IS NULL), 0) todo FROM v_latest_news" + where, tuple(args))
        n_match, n_todo = int(cnt["n"][0]), int(cnt["todo"][0])
        n_all = n_match if not cond else int(q("SELECT COUNT(*) n FROM feed_item")["n"][0])
        pages = max(1, -(-n_match // size))
        page = min(max(1, st.session_state.get("nf_page", 1)), pages)
        news = q("SELECT id, source_name, published_at, title, summary, url, pred_category FROM v_latest_news" + where
                 + " ORDER BY published_at DESC, id DESC LIMIT %s OFFSET %s", tuple(args) + (size, (page - 1) * size))
        head.html(card_head("Tin mới nhất từ RSS", f"Lần lấy gần nhất <b>{last}</b> · đang có {num(n_all)} tin trong CSDL "
                            f"· khớp bộ lọc <b>{num(n_match)}</b> tin", h="h2"))
        todo = news[news["pred_category"].isna()]
        if c3.button("Lấy tin ngay", type="primary", icon=":material/sync:", disabled=wait, width="stretch",
                     help=f"Tối đa một lần mỗi {fetch_news.MIN_LOOP_MIN} phút"
                          + (f"; lần gần nhất cách đây {recent} phút" if recent is not None else "")):
            con = connect_mariadb()  # fetch_all commit/rollback theo từng báo nên cần kết nối không autocommit
            with st.spinner("Đang đọc RSS…"):
                fetch_news.fetch_all(con)
            con.close()
            st.rerun()
        if c2.button(f"Trang này ({len(todo)})", disabled=todo.empty, width="stretch",
                     help="Phân loại các tin chưa có nhãn trên trang này bằng mô hình cải tiến"):
            with st.spinner("Đang phân loại bằng mô hình cải tiến…"):
                for r in todo.itertuples():
                    classify_news(s, clf, r)
            st.rerun()
        # mỗi lần bấm tối đa BATCH tin: chạy đồng bộ trong một lượt Streamlit, rời trang là dừng giữa chừng
        BATCH = 200
        label = f"Phân loại hết ({num(n_todo)})" if n_todo <= BATCH else f"Phân loại {BATCH} / {num(n_todo)}"
        if c4.button(label, disabled=n_todo == 0, width="stretch",
                     help=f"Phân loại các tin chưa có nhãn khớp bộ lọc hiện tại (mọi trang), mới nhất trước, "
                          f"tối đa {BATCH} tin mỗi lần bấm"):
            rest = q("SELECT id, title, summary FROM v_latest_news" + where
                     + (" AND " if cond else " WHERE ") + "pred_category IS NULL ORDER BY published_at DESC, id DESC"
                     + " LIMIT %s", tuple(args) + (BATCH,))
            bar_ = st.progress(0.0, text=f"Đang phân loại 0 / {num(len(rest))} tin…")
            for i, r in enumerate(rest.itertuples(), 1):
                classify_news(s, clf, r)
                bar_.progress(i / len(rest), text=f"Đang phân loại {num(i)} / {num(len(rest))} tin…")
            st.session_state.nf_page = 1  # tin đã có nhãn rời bộ lọc "Chưa phân loại": quay về trang đầu
            st.rerun()
        if news.empty:
            st.html('<div class="t2v-nsum" style="padding:24px 0;text-align:center">Không có tin nào khớp bộ lọc.</div>')
        code_of = {v: k for k, v in clf.cat_name.items()}
        for r in news.itertuples():
            with st.container(key=f"news_{r.id}"):
                a, b = st.columns([6, 1.3], vertical_alignment="center")
                t = pd.Timestamp(r.published_at).tz_localize("UTC").tz_convert("Asia/Ho_Chi_Minh") if r.published_at else None
                cat = clf.cat_name.get(r.pred_category) if isinstance(r.pred_category, str) else None
                chip = cat_chip(code_of[cat], cat, True) if cat else '<span class="t2v-cat gray">Chưa phân loại</span>'
                when = f'<span class="sep">·</span><span>{t:%H:%M · %d/%m/%Y}</span>' if t is not None else ""
                a.html(f'<div class="t2v-nmeta"><b>{e(r.source_name)}</b>{when}{chip}</div>'
                       f'<div class="t2v-ntitle"><a href="{e(r.url)}" target="_blank">{e(r.title)}</a></div>'
                       f'<div class="t2v-nsum">{e(txt(r.summary))}</div>')
                if b.button("Phân loại lại" if cat else "Phân loại bài này", key=f"n{r.id}", width="stretch"):
                    classify_news(s, clf, r)
                    st.rerun()
        if pages > 1:
            p1, p2, p3 = st.columns([1, 2, 1], vertical_alignment="center")
            if p1.button("← Trang trước", key="nf_prev", disabled=page <= 1, width="stretch"):
                st.session_state.nf_page = page - 1
                st.rerun()
            p2.html(f'<div class="t2v-nmeta" style="justify-content:center">Trang <b>{page}</b> / {pages} · '
                    f'tin {num((page - 1) * size + 1)}–{num(min(page * size, n_match))} trong {num(n_match)}</div>')
            if p3.button("Trang sau →", key="nf_next", disabled=page >= pages, width="stretch"):
                st.session_state.nf_page = page + 1
                st.rerun()


def classify_news(s, clf, r):
    """Phân loại một tin RSS bằng mô hình cải tiến, ghi feed_item.pred_category."""
    ms = clf.predict(f"{r.title}\n{txt(r.summary)}", log=True)["models"]
    p = next((m for m in ms if m["improved"]), ms[-1])["proba"]
    if p:
        with s.cursor() as c:
            c.execute("UPDATE feed_item SET pred_category = %s WHERE id = %s", (p[0][0], r.id))


# ===================================================================== khung
PAGES = {"Phân loại bài báo": (page_classify, ":material/description:"),
         "Tìm kiếm nâng cao": (page_search, ":material/search:"),
         "Dữ liệu và đánh giá": (page_data, ":material/bar_chart:"),
         "Tin mới nhất": (page_news, ":material/rss_feed:")}
with st.sidebar:
    st.html('<div class="t2v-brand"><div class="t2v-logo">T2V</div><div><b>Trans2Vec News</b>'
            '<span>Phân loại và tìm kiếm tin tức</span></div></div><div class="t2v-sec">Chức năng chính</div>')
    page = st.radio("Chức năng", list(PAGES), label_visibility="collapsed", format_func=lambda p: f"{PAGES[p][1]} {p}")
    try:
        load()
        status = '<span class="on"><span class="dot sm g"></span>Trực tuyến</span>'
    except Exception:  # CSDL chưa bật: vẫn hiện khung, trang sẽ báo lỗi chi tiết
        status = '<span class="on off"><span class="dot sm r"></span>Mất kết nối</span>'
    st.html(f'<div class="t2v-arch"><div class="hd"><span>Kiến trúc hệ thống</span>{status}</div>' + "".join(
        f'<div class="it"><div><b>{a}</b><span class="t2v-tag {c}">{t}</span></div><p>{d}</p></div>' for a, t, c, d in
        [("MariaDB 11.8", "SQL", "", "Nguồn dữ liệu gốc, vector"), ("Manticore Search", "Search", "",
         "Chỉ mục BM25 và HNSW"), ("Python", "NLP", "i", "pyvi · gensim · LR · Streamlit")]) + "</div>")
    st.selectbox("Bảng màu", list(theme.PALETTES), key="t2v_palette")
PAGES[page][0]()
