"""Giao diện Trans2Vec News (GĐ-H5) — 4 mục theo bản phác: Phân loại · Tìm kiếm · Dữ liệu và đánh giá · Tin mới nhất.

Chạy:  .venv-exp/bin/streamlit run src/system/app/streamlit_app.py
Mọi số liệu đọc từ MariaDB (model_run, eval_result, view); tìm kiếm qua Manticore; mô hình ở system/models/.
"""
import html
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

APP = Path(__file__).resolve().parent
sys.path.insert(0, str(APP))
sys.path.insert(0, str(APP.parent / "pipeline"))
from classify import Classifier  # noqa: E402
from config import connect_mariadb  # noqa: E402
from search import Searcher  # noqa: E402
from vi_text import fold  # noqa: E402

ACCENT = "#1F4E99"  # màu chủ đạo của bản phác; mỗi biểu đồ chỉ một chuỗi dữ liệu
MODES = {"Hybrid (RRF)": "hybrid", "Vector (Trans2Vec-JOI)": "knn", "BM25": "bm25"}
MODE_LABEL = {v: k for k, v in MODES.items()}
MODE_DESC = {
    "hybrid": "Hợp nhất hạng BM25 và hạng vector bằng Reciprocal Rank Fusion (k = 60), mỗi bên lấy 100 ứng viên.",
    "knn": "Truy vấn → pyvi → item và FI → infer_vector → KNN HNSW cosine trên Manticore.",
    "bm25": "Toàn văn đã tách từ (title_seg, body_seg), BM25 k1 = 1,2, b = 0,75; giữ dấu tiếng Việt.",
}
SAMPLE_QUERIES = ["giá vàng tăng mạnh", "đội tuyển Việt Nam thắng trận", "dịch cúm gia cầm",
                  "máy tính xách tay giá rẻ", "xét xử vụ án tham nhũng"]

st.set_page_config(page_title="Trans2Vec News", layout="wide")

# Kiểu dáng theo bản phác giao diện: nền #F4F5F7, thẻ trắng viền mảnh, xanh #1F4E99, font Be Vietnam Pro
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap');
html, body, [class*="st-"], .stMarkdown, button, input, textarea, select { font-family: 'Be Vietnam Pro', sans-serif; }
[data-testid="stIconMaterial"], .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; }
[data-testid="stExpander"] details { background: #FFFFFF; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1320px; }
header[data-testid="stHeader"] { background: transparent; height: 0; }
[data-testid="stSidebar"] { border-right: 1px solid #E1E5EA; }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding-top: .4rem; }
/* menu chức năng: ẩn nút tròn, mỗi mục là một dòng bấm được */
[data-testid="stSidebar"] [role="radiogroup"] { gap: 2px; }
[data-testid="stSidebar"] [role="radiogroup"] label { width: 100%; padding: 9px 12px; border-radius: 8px; margin: 0; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) { display: none; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover { background: #F4F5F7; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] { background: #E8EEF8; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] p { color: #1F4E99; font-weight: 600; }
[data-testid="stSidebarHeader"] { height: 1rem; min-height: 1rem; padding: 0; }
[data-testid="stTextArea"] textarea { background: #FFFFFF; border: 1px solid #D5DCE6; }
[data-testid="stSidebar"] [role="radiogroup"] p { font-size: 14px; }
/* thẻ (container border=True) nền trắng */
[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stVerticalBlock"]:has(> div > [data-testid="stVerticalBlockBorderWrapper"]) {}
.stVerticalBlock[class*="st-key-card"], [data-testid="stVerticalBlockBorderWrapper"] { background: #FFFFFF; }
[data-testid="stMetricValue"] { font-size: 22px; font-weight: 600; }
[data-testid="stMetricLabel"] p { font-size: 12px; color: #4A5563; text-transform: uppercase; letter-spacing: .04em; }
mark { background: #DCE7F7; color: inherit; padding: 0 2px; border-radius: 3px; }
.t2v-crumb { font-size: 13px; color: #6B7480; margin-bottom: 2px; }
.t2v-title { font-size: 26px; font-weight: 700; color: #1A2230; margin: 0 0 6px 0; }
.t2v-chips { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 14px; }
.t2v-chip { font-size: 12px; color: #1F4E99; background: #E8EEF8; border-radius: 999px; padding: 3px 10px; font-weight: 500; }
.t2v-chip.gray { color: #4A5563; background: #E9ECF0; }
.t2v-brand { display: flex; gap: 10px; align-items: center; margin: 4px 0 18px; }
.t2v-logo { width: 36px; height: 36px; border-radius: 9px; background: #1F4E99; color: #fff; font-weight: 700;
            display: flex; align-items: center; justify-content: center; font-size: 13px; }
.t2v-brand b { display: block; font-size: 15px; color: #1A2230; }
.t2v-brand span { font-size: 12px; color: #6B7480; }
.t2v-sec { font-size: 11px; font-weight: 600; color: #6B7480; letter-spacing: .06em; text-transform: uppercase; margin: 14px 0 6px; }
.t2v-arch { border: 1px solid #E1E5EA; border-radius: 8px; padding: 8px 10px; margin-bottom: 6px; background: #FAFBFC; }
.t2v-arch b { font-size: 13px; color: #1A2230; display: block; }
.t2v-arch span { font-size: 12px; color: #6B7480; }
.t2v-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 6px 0 14px; }
@media (max-width: 900px) { .t2v-grid { grid-template-columns: 1fr; } }
.t2v-card { background: #fff; border: 1px solid #E1E5EA; border-radius: 10px; padding: 14px 16px; }
.t2v-card.best { border-color: #1F4E99; box-shadow: 0 0 0 1px #1F4E99 inset; }
.t2v-card .hd { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
.t2v-card .nm { font-weight: 600; font-size: 14px; color: #1A2230; }
.t2v-card .f1 { font-size: 12px; color: #4A5563; white-space: nowrap; }
.t2v-card .ds { font-size: 12px; color: #6B7480; margin: 2px 0 10px; min-height: 18px; }
.t2v-card .pr { font-size: 17px; font-weight: 600; color: #1A2230; }
.t2v-card .pc { font-size: 13px; color: #1F4E99; font-weight: 600; margin-left: 6px; }
.t2v-row { display: grid; grid-template-columns: 112px 1fr 40px; gap: 8px; align-items: center; font-size: 12px;
           color: #4A5563; margin-top: 7px; }
.t2v-row .tr { height: 6px; background: #EEF1F5; border-radius: 3px; overflow: hidden; }
.t2v-row .br { height: 6px; background: #1F4E99; border-radius: 3px; }
.t2v-row .br.lo { background: #9DB4DA; }
.t2v-row .v { text-align: right; font-variant-numeric: tabular-nums; }
.t2v-sum { background: #fff; border: 1px solid #E1E5EA; border-radius: 10px; padding: 10px 16px; margin: 8px 0 4px;
           display: flex; gap: 22px; flex-wrap: wrap; font-size: 14px; }
.t2v-sum b { color: #1F4E99; }
.t2v-text { max-height: 260px; overflow: auto; line-height: 1.75; background: #fff; border: 1px solid #E1E5EA;
            border-radius: 10px; padding: 12px 14px; font-size: 14px; }
.t2v-tags { display: flex; flex-wrap: wrap; gap: 6px; margin: 4px 0 12px; }
.t2v-tag { font-size: 12px; background: #fff; border: 1px solid #D5DCE6; border-radius: 6px; padding: 2px 8px; color: #1A2230; }
.t2v-tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 12px; margin: 4px 0 14px; }
.t2v-tile { background: #fff; border: 1px solid #E1E5EA; border-radius: 10px; padding: 12px 14px; }
.t2v-tile .lb { font-size: 11px; font-weight: 600; color: #6B7480; letter-spacing: .05em; text-transform: uppercase; }
.t2v-tile .vl { font-size: clamp(17px, 1.5vw, 22px); white-space: nowrap; font-weight: 600; color: #1A2230; margin-top: 2px; font-variant-numeric: tabular-nums; }
.t2v-tile .sb { font-size: 12px; color: #6B7480; }
.t2v-news-meta { display: flex; gap: 8px; align-items: center; font-size: 12px; color: #6B7480; margin-bottom: 4px; }
.t2v-news-title a { font-size: 16px; font-weight: 600; color: #1A2230; text-decoration: none; }
.t2v-news-title a:hover { color: #1F4E99; text-decoration: underline; }
.t2v-news-sum { font-size: 14px; color: #4A5563; margin-top: 4px; line-height: 1.55; }
.t2v-src b { font-size: 14px; color: #1A2230; } .t2v-src .ok { color: #1E7A46; font-size: 12px; font-weight: 600; }
.t2v-src .bad { color: #B42318; font-size: 12px; font-weight: 600; }
.t2v-src div { font-size: 12px; color: #6B7480; margin-top: 3px; word-break: break-all; }
</style>
"""
st.html(CSS)


def header(title, chips=()):
    """Tiêu đề trang như bản phác: đường dẫn, tên trang, các nhãn ngữ cảnh."""
    chip_html = "".join(f'<span class="t2v-chip{" gray" if g else ""}">{html.escape(c)}</span>' for c, g in chips)
    st.html(f'<div class="t2v-crumb">Bảng điều khiển › {html.escape(title)}</div>'
            f'<div class="t2v-title">{html.escape(title)}</div><div class="t2v-chips">{chip_html}</div>')


def tiles(items):
    """Ô chỉ số dạng thẻ: [(nhãn, giá trị, dòng phụ)] (thay st.metric để không có mũi tên delta)."""
    st.html('<div class="t2v-tiles">' + "".join(
        f'<div class="t2v-tile"><div class="lb">{html.escape(str(a))}</div><div class="vl">{html.escape(str(b))}</div>'
        f'<div class="sb">{html.escape(str(c or ""))}</div></div>' for a, b, c in items) + "</div>")


def hbars(rows, fmt="{:.0f}"):
    """Thanh ngang mảnh cho [(nhãn, giá trị)], giá trị lớn nhất = 100%."""
    mx = max((v for _, v in rows), default=1) or 1
    st.html("".join(f'<div class="t2v-row"><span>{html.escape(str(n))}</span><div class="tr"><div class="br" '
                    f'style="width:{v / mx * 100:.1f}%"></div></div><span class="v">{fmt.format(v)}</span></div>'
                    for n, v in rows))


def model_cards(models, best_f1):
    """Lưới thẻ mô hình: tên, Macro-F1, dự đoán và top-3 xác suất bằng thanh mảnh (HTML, không cần biểu đồ)."""
    cards = []
    for m in models:
        cls = "t2v-card best" if m["f1"] == best_f1 else "t2v-card"
        head = (f'<div class="hd"><span class="nm">{html.escape(m["name"])}</span>'
                f'<span class="f1">Macro-F1 {m["f1"]:.3f}</span></div><div class="ds">{html.escape(m["note"])}</div>')
        if not m["proba"]:
            body = '<div class="ds">Không có item nào trong từ vựng của mô hình.</div>'
        else:
            _, name, p = m["proba"][0]
            body = f'<div><span class="pr">{html.escape(name)}</span><span class="pc">{p:.0%}</span></div>'
            for i, (_, n, x) in enumerate(m["proba"][:3]):
                body += (f'<div class="t2v-row"><span>{html.escape(n)}</span><div class="tr">'
                         f'<div class="br{" lo" if i else ""}" style="width:{x * 100:.1f}%"></div></div>'
                         f'<span class="v">{x:.0%}</span></div>')
        cards.append(f'<div class="{cls}">{head}{body}</div>')
    st.html(f'<div class="t2v-grid">{"".join(cards)}</div>')


@st.cache_resource(show_spinner="Đang nạp mô hình và kết nối CSDL…")
def load():
    s = Searcher()
    return s, Classifier(s)


def q(sql, args=None):
    s, _ = load()
    with s.lock, s.db.cursor() as c:
        c.execute(sql, args)
        cols = [d[0] for d in c.description]
        return pd.DataFrame(c.fetchall(), columns=cols)


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
    return q("""SELECT a.id, cat.name, a.title, a.body FROM article a JOIN category cat ON cat.id = a.category_id
                WHERE a.id IN (SELECT MIN(a2.id) FROM article a2 JOIN prediction p ON p.article_id = a2.id
                               AND p.run_id = (SELECT MAX(id) FROM model_run WHERE kind = 'lr')
                               WHERE a2.split = 'test' AND a2.n_word BETWEEN 150 AND 250
                                 AND p.pred_category_id = a2.category_id
                               GROUP BY a2.category_id) ORDER BY cat.id""")


# ===================================================================== Phân loại
def page_classify():
    _, clf = load()
    n = len(clf.models)
    header("Phân loại bài báo", [("VNTC-10 · 84.132 bài", True), (f"{n} mô hình · mốc: Trans2Vec gốc", False)])
    ex = samples()
    with st.container(border=True):
        st.markdown("**Nội dung bài báo**")
        pick = st.pills("Đoạn ví dụ", ex["name"].tolist(), key="ex_pick", label_visibility="collapsed")
        if pick and st.session_state.get("ex_last") != pick:
            r = ex.set_index("name").loc[pick]
            st.session_state.text = f"{r['title']}\n{r['body']}"
            st.session_state.ex_last = pick
        text = st.text_area("Nội dung bài báo", key="text", height=170, label_visibility="collapsed",
                            placeholder="Dán nội dung (tiêu đề + thân bài) hoặc chọn một đoạn ví dụ ở trên")
        c1, c2, c3 = st.columns([1, 1, 6], vertical_alignment="center")
        go = c1.button("Phân loại", type="primary", disabled=not text.strip(), width="stretch")
        c2.button("Xóa", on_click=lambda: st.session_state.update(text="", ex_pick=None, ex_last=None), width="stretch")
        c3.caption("Tách từ pyvi · mốc Trans2Vec gốc (mã tác giả, LinearSVC), 4 biến thể và mô hình cải tiến (LR) · "
                   "Macro-F1 đo trên 50.373 bài test")
    if not go:
        return
    r = clf.predict(text, log=True)
    ok = [m for m in r["models"] if m["proba"]]
    top = pd.Series([m["proba"][0][1] for m in ok]).value_counts()
    best = max(m["f1"] for m in r["models"])
    base = next((m["f1"] for m in r["models"] if m["kind"] == "trans2vec-orig"), None)
    imp = next((m for m in r["models"] if m["improved"] and m["proba"]), None)
    parts = [f"So sánh <b>{n}</b> mô hình"]
    if len(top):
        parts.append(f"<b>{top.iloc[0]}/{n}</b> mô hình chọn “{html.escape(top.index[0])}”")
    if imp:
        parts.append(f"Mô hình cải tiến: <b>{html.escape(imp['proba'][0][1])}</b> ({imp['proba'][0][2]:.0%})")
    parts.append(f"{r['ms']:.0f} ms")
    st.html('<div class="t2v-sum">' + "".join(f"<span>{x}</span>" for x in parts) + "</div>")
    model_cards(r["models"], best)

    rows = [{"Mô hình": m["name"], "Dự đoán": m["proba"][0][1] if m["proba"] else "—",
             "Xác suất": m["proba"][0][2] if m["proba"] else 0.0, "Macro-F1": f"{m['f1']:.3f}",
             "So với mốc": "mốc" if m["kind"] == "trans2vec-orig" or base is None else f"{m['f1'] - base:+.3f}",
             "Cách tạo": m["note"]} for m in r["models"]]
    with st.expander("Bảng so sánh chi tiết"):
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch", column_config={
            "Xác suất": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1),
            "Cách tạo": st.column_config.TextColumn(width="large")})
        st.caption("Viền xanh: Macro-F1 cao nhất. Điểm của mốc là softmax điểm quyết định SVM, không phải xác suất. "
                   "Mốc học transductive trên cả văn bản test như mã gốc, nên Macro-F1 của mốc là con số có lợi cho mốc.")

    joi = next((m for m in r["models"] if m["kind"] == "trans2vec-joi"), None)
    if joi and joi["proba"]:
        st.markdown(f"**Vì sao Trans2Vec-JOI chọn “{joi['proba'][0][1]}”?**")
        a, b = st.columns([3, 2])
        fi_words = {w for f in r["fi"] for w in f}
        a.caption("Từ thuộc FI khớp được tô sáng")
        a.html(f"<div class='t2v-text'>{highlight(text, fi_words)}</div>")
        tag = lambda xs: '<div class="t2v-tags">' + "".join(f'<span class="t2v-tag">{html.escape(x)}</span>' for x in xs) + "</div>"
        b.caption("FI khớp (độ dài ≥ 2)")
        b.html(tag([" + ".join(f) for f in r["fi"][:16]]) if r["fi"] else
               "<div class='t2v-tags'>Không có FI nào đủ các từ; dự đoán dựa trên item đơn.</div>")
        b.caption("Item của bài (top tf·idf)")
        b.html(tag(r["items"][:20]))


# ===================================================================== Tìm kiếm
def page_search():
    s, _ = load()
    header("Tìm kiếm", [("VNTC-10 · kho 33.759 bài train", True), ("Manticore: BM25 + HNSW", False)])
    cats = q("SELECT id, name FROM category ORDER BY id")
    ndcg = q("""SELECT e.kind, ev.value FROM eval_result ev JOIN model_run e ON e.id = ev.run_id
                WHERE ev.task='search' AND ev.metric='ndcg@10'""").set_index("kind")["value"]
    with st.container(border=True):
        st.markdown("**Truy vấn và bộ lọc**")
        sq = st.pills("Truy vấn mẫu", SAMPLE_QUERIES, key="sq_pick")
        if sq and st.session_state.get("sq_last") != sq:
            st.session_state.query = sq
            st.session_state.sq_last = sq
        c1, c2, c3, c4 = st.columns([4, 2, 2, 1.4])
        query = c1.text_input("Từ khóa", key="query")
        mode = MODES[c2.selectbox("Chế độ tìm kiếm", list(MODES))]
        cat = c3.selectbox("Chuyên mục", [None] + cats["id"].tolist(),
                           format_func=lambda i: "Tất cả" if i is None else cats.set_index("id").loc[i, "name"])
        k = c4.radio("Số kết quả", [5, 10], index=1, horizontal=True)
        st.caption(MODE_DESC[mode])
    if not query.strip():
        st.info("Nhập từ khóa hoặc chọn một truy vấn mẫu.")
        return
    res = s.search(query, mode=mode, k=k, category_id=cat, log=True)
    hits = res["hits"]
    det = s.details([h["id"] for h in hits])
    tiles([("Kết quả", len(hits), f"{res['ms']:.0f} ms"),
           ("Điểm cao nhất", f"{hits[0]['score']:.4f}" if hits else "—", MODE_LABEL[mode]),
           ("Chuyên mục xuất hiện", len({det[h['id']]['code'] for h in hits}), "trong kết quả hiển thị"),
           ("nDCG@10 Trans2Vec-JOI", f"{ndcg.get('trans2vec-joi', float('nan')):.3f}", "1.000 truy vấn là bài báo")])
    if not hits:
        st.warning("Không có kết quả. Thử truy vấn khác, đổi chế độ hoặc bỏ lọc chuyên mục.")
        return
    if res["folded"]:
        st.caption("Truy vấn không dấu: BM25 tìm trên trường đã gộp dấu (title_fold, body_fold)."
                   + {"hybrid": " Chế độ hybrid chỉ dùng BM25, vì vector suy luận từ chữ không dấu kém tin cậy.",
                      "knn": " Vector suy luận từ chữ không dấu nên kém tin cậy; nên dùng BM25 hoặc hybrid."}.get(mode, ""))
    if res["query_fi"]:
        st.caption("FI của truy vấn: " + ", ".join(" + ".join(f) for f in res["query_fi"]))
    rows = [{"#": h["rank"], "Bài viết": det[h["id"]]["title"], "Chuyên mục": det[h["id"]]["category"],
             "FI khớp": ", ".join(det[h["id"]]["fi"][:3]) or "—", "Điểm": round(h["score"], 4),
             "Hạng BM25": h["bm25_rank"], "Hạng vector": h["knn_rank"]} for h in hits]
    left, right = st.columns([3, 2])
    with left:
        st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch",
                     column_config={"#": st.column_config.NumberColumn(width=40),
                                    "Bài viết": st.column_config.TextColumn(width="large")})
        st.markdown("**Phân bố theo chuyên mục**")
        hbars(list(pd.DataFrame(rows)["Chuyên mục"].value_counts().items()))
    with right:
        pick = st.selectbox("Chi tiết bài viết", [h["id"] for h in hits],
                            format_func=lambda i: f"#{next(h['rank'] for h in hits if h['id'] == i)} {det[i]['title'][:60]}")
        h, d = next(h for h in hits if h["id"] == pick), det[pick]
        with st.container(border=True):
            st.caption(f"{d['category']} · hạng #{h['rank']} · {d['split']}")
            st.markdown(f"**{d['title']}**")
            st.markdown(highlight(d["snippet"] + "…", res["words"], res["folded"]), unsafe_allow_html=True)
            tiles([("BM25", f"{h['bm25']:.0f}" if h["bm25"] else "—", f"hạng {h['bm25_rank'] or '—'}"),
                   ("Vector", f"{h['knn']:.3f}" if h["knn"] else "—", f"hạng {h['knn_rank'] or '—'}"),
                   ("RRF" if mode == "hybrid" else "Điểm", f"{h['score']:.4f}", "k = 60" if mode == "hybrid" else "")])
            st.caption("FI trong bài: " + (", ".join(d["fi"][:10]) or "không có"))
            st.caption(f"Tệp nguồn: {d['file']}")


# ===================================================================== Dữ liệu và đánh giá
def page_data():
    header("Dữ liệu và đánh giá", [("VNTC-10 · 84.132 bài", True), ("Số liệu đọc từ MariaDB", False)])
    fim = q("SELECT JSON_VALUE(params,'$.delta') delta, JSON_VALUE(metrics,'$.n_fi') n_fi FROM model_run WHERE kind='fim' ORDER BY id DESC LIMIT 1")
    split = q("SELECT split, COUNT(*) n FROM article GROUP BY split").set_index("split")["n"]
    dup = q("SELECT COUNT(*) - COUNT(DISTINCT body_md5) n FROM article")["n"][0]
    tiles([("Chuyên mục", 10, "VNTC-10"),
           ("Bài train / test", f"{split['train']:,} / {split['test']:,}".replace(",", "."), "cách chia gốc"),
           ("Ngưỡng δ (elbow)", f"{float(fim['delta'][0]) * 100:.3f}%".replace(".", ","), "khai phá FI trên train"),
           ("Số FI (độ dài ≤ 3)", f"{int(fim['n_fi'][0]):,}".replace(",", "."), "tất cả đều là FI đóng"),
           ("Bài trùng nội dung", f"{dup:,}".replace(",", "."), "3.056 bài test có bản sao trong train")])

    names = {"tfidf": "TF-IDF toàn văn", **{k: n for k, n, _ in Classifier.KINDS}}
    ev = q("""SELECT e.kind, ev.metric, ev.value FROM eval_result ev JOIN model_run l ON l.id = ev.run_id
              JOIN model_run e ON e.id = l.parent_id WHERE l.kind IN ('lr','svm') AND ev.metric IN ('acc','macro_f1')
              UNION ALL
              SELECT e.kind, ev.metric, ev.value FROM eval_result ev JOIN model_run e ON e.id = ev.run_id
              WHERE ev.task='search'""")
    ev["Biểu diễn"] = ev["kind"].map(names)
    t = ev.pivot_table(index="Biểu diễn", columns="metric", values="value")
    t = t.reindex([n for n in names.values() if n in t.index])
    a, b = st.columns(2)
    a.markdown("**Phân loại** · LR (mốc: LinearSVC) trên 50.373 bài test")
    a.dataframe(t[["acc", "macro_f1"]].rename(columns={"acc": "Accuracy", "macro_f1": "Macro-F1"}).style.format("{:.3f}"),
                width="stretch")
    b.markdown("**Tìm kiếm** · 1.000 truy vấn là bài báo, cosine vét cạn")
    b.dataframe(t[["p@10", "map@100", "ndcg@10"]].rename(columns={"p@10": "P@10", "map@100": "MAP@100", "ndcg@10": "nDCG@10"})
                .style.format("{:.3f}"), width="stretch")
    st.caption("“Liên quan” = cùng chuyên mục (proxy), chưa phải nhãn liên quan do người đánh giá. Số liệu đọc từ bảng eval_result.")

    a, b = st.columns(2)
    with a:
        kinds = [k for k in names if names[k] in t.index]
        kind = st.selectbox("Ma trận nhầm lẫn", kinds, format_func=names.get, index=kinds.index("trans2vec-joi"))
        cm = q("""SELECT v.true_code, v.pred_code, v.n FROM v_confusion v JOIN model_run l ON l.id = v.run_id
                  JOIN model_run e ON e.id = l.parent_id WHERE e.kind = %s""", (kind,))
        cm["tỉ lệ"] = cm["n"] / cm.groupby("true_code")["n"].transform("sum")
        heat = alt.Chart(cm).mark_rect(stroke="white", strokeWidth=2).encode(
            x=alt.X("pred_code:N", title="Dự đoán"), y=alt.Y("true_code:N", title="Thực tế"),
            color=alt.Color("tỉ lệ:Q", scale=alt.Scale(scheme="blues"), legend=alt.Legend(format=".0%")),
            tooltip=["true_code", "pred_code", "n", alt.Tooltip("tỉ lệ:Q", format=".1%")])
        st.altair_chart(heat.properties(height=340), width="stretch")
    with b:
        st.markdown("**Thống kê corpus** (view `v_corpus_stats`)")
        st.dataframe(q("SELECT name AS `Chuyên mục`, split AS `Tập`, n_article AS `Số bài`, avg_words AS `TB từ` "
                       "FROM v_corpus_stats ORDER BY code, split"), hide_index=True, width="stretch", height=340)

    st.markdown("**FI đặc trưng của từng chuyên mục** (view `v_category_fi`: FI độ dài ≥ 2 xuất hiện ở nhiều bài train nhất)")
    fi = q("""SELECT c.name, GROUP_CONCAT(REPLACE(v.label, '|', ' + ') ORDER BY v.rk SEPARATOR ' · ') AS fi
              FROM v_category_fi v JOIN category c ON c.code = v.code WHERE v.rk <= 10 GROUP BY c.id ORDER BY c.id""")
    st.dataframe(fi.rename(columns={"name": "Chuyên mục", "fi": "10 FI phổ biến nhất"}), hide_index=True,
                 width="stretch")
    logs = q("""SELECT 'tìm kiếm' AS loai, COUNT(*) n, ROUND(AVG(latency_ms)) tb_ms FROM search_log
                UNION ALL SELECT 'phân loại', COUNT(*), ROUND(AVG(latency_ms)) FROM classify_log""")
    st.caption("Nhật ký: " + " · ".join(f"{r.loai} {r.n} lượt" + (f", TB {r.tb_ms:.0f} ms" if r.n else "")
                                        for r in logs.itertuples()))


# ===================================================================== Tin mới nhất
def page_news():
    import fetch_news

    s, clf = load()
    header("Tin mới nhất", [("RSS: VnExpress · Tuổi Trẻ · Thanh Niên", True), ("Phân loại bằng Trans2Vec-CAT", False)])
    src = q("""SELECT s.id, s.code, s.name, s.rss_url, s.last_fetch_at,
                      l.http_status, l.n_items, l.n_new, l.latency_ms, l.error
               FROM news_source s LEFT JOIN fetch_log l ON l.id = (SELECT MAX(id) FROM fetch_log WHERE source_id = s.id)
               WHERE s.active ORDER BY s.id""")
    recent = q("SELECT TIMESTAMPDIFF(MINUTE, MAX(last_fetch_at), UTC_TIMESTAMP()) m FROM news_source")["m"][0]
    wait = recent is not None and recent < fetch_news.MIN_LOOP_MIN
    for col, r in zip(st.columns(len(src)), src.itertuples()):
        nz = lambda v: int(v) if pd.notna(v) else 0  # cột số từ LEFT JOIN có thể là NaN
        err = r.error if isinstance(r.error, str) and r.error else None
        status = (f'<span class="ok">HTTP {nz(r.http_status)}</span>' if nz(r.http_status) == 200 and not err else
                  f'<span class="bad">{html.escape(err or (f"HTTP {nz(r.http_status)}" if nz(r.http_status) else "chưa lấy"))}</span>')
        with col.container(border=True):
            st.html(f'<div class="t2v-src"><b>{html.escape(r.name)}</b> · {status}<div>{html.escape(r.rss_url)}</div>'
                    f'<div>Tin trong feed {nz(r.n_items)} · tin mới {nz(r.n_new)} · {nz(r.latency_ms)} ms</div></div>')
    news = q("SELECT id, source_name, published_at, title, summary, url, pred_category FROM v_latest_news "
             "ORDER BY published_at DESC LIMIT 30")
    todo = news[news["pred_category"].isna()]
    c1, c2, c3 = st.columns([1.2, 1.8, 4], vertical_alignment="center")
    if c1.button("Lấy tin ngay", type="primary", disabled=wait, width="stretch",
                 help=f"Tối đa một lần mỗi {fetch_news.MIN_LOOP_MIN} phút"):
        con = connect_mariadb()  # fetch_all commit/rollback theo từng báo nên cần kết nối không autocommit
        with st.spinner("Đang đọc RSS…"):
            fetch_news.fetch_all(con)
        con.close()
        st.rerun()
    if c2.button(f"Phân loại {len(todo)} tin mới", disabled=todo.empty, width="stretch"):
        with st.spinner("Đang phân loại bằng mô hình cải tiến…"):
            for r in todo.itertuples():
                classify_news(s, clf, r)
        st.rerun()
    c3.caption("Chỉ đọc RSS công khai: tiêu đề, mô tả ngắn, link, ảnh. Không tải trang bài viết. Trùng lặp chặn bằng SHA-1 "
               "của URL." + (f" Lần lấy gần nhất cách đây {recent} phút." if recent is not None else ""))
    for r in news.itertuples():
        with st.container(border=True):
            a, b = st.columns([6, 1.3], vertical_alignment="center")
            t = pd.Timestamp(r.published_at).tz_localize("UTC").tz_convert("Asia/Ho_Chi_Minh") if r.published_at else None
            cat = clf.cat_name.get(r.pred_category) if isinstance(r.pred_category, str) else None
            chip = (f'<span class="t2v-chip">{html.escape(cat)}</span>' if cat
                    else '<span class="t2v-chip gray">Chưa phân loại</span>')
            a.html(f'<div class="t2v-news-meta"><b>{html.escape(r.source_name)}</b><span>{t:%H:%M · %d/%m/%Y}</span>{chip}</div>'
                   if t is not None else f'<div class="t2v-news-meta"><b>{html.escape(r.source_name)}</b>{chip}</div>')
            a.html(f'<div class="t2v-news-title"><a href="{html.escape(r.url)}" target="_blank">{html.escape(r.title)}</a></div>'
                   f'<div class="t2v-news-sum">{html.escape(r.summary or "")}</div>')
            if b.button("Phân loại lại" if cat else "Phân loại", key=f"n{r.id}", width="stretch"):
                classify_news(s, clf, r)
                st.rerun()


def classify_news(s, clf, r):
    """Phân loại một tin RSS bằng mô hình cải tiến, ghi feed_item.pred_category."""
    ms = clf.predict(f"{r.title}\n{r.summary or ''}", log=True)["models"]
    p = next((m for m in ms if m["improved"]), ms[-1])["proba"]
    if p:
        with s.lock, s.db.cursor() as c:
            c.execute("UPDATE feed_item SET pred_category = %s WHERE id = %s", (p[0][0], r.id))


# ===================================================================== khung
PAGES = {"Phân loại bài báo": page_classify, "Tìm kiếm": page_search,
         "Dữ liệu và đánh giá": page_data, "Tin mới nhất": page_news}
with st.sidebar:
    st.html('<div class="t2v-brand"><div class="t2v-logo">T2V</div><div><b>Trans2Vec News</b>'
            '<span>Phân loại và tìm kiếm tin tức</span></div></div><div class="t2v-sec">Chức năng</div>')
    page = st.radio("Chức năng", list(PAGES), label_visibility="collapsed")
    st.html('<div class="t2v-sec">Kiến trúc</div>' + "".join(
        f'<div class="t2v-arch"><b>{a}</b><span>{b}</span></div>' for a, b in
        [("MariaDB 11.8", "Nguồn dữ liệu gốc, vector"), ("Manticore Search", "Chỉ mục BM25 và HNSW"),
         ("Python", "pyvi · gensim · LR · Streamlit")]))
PAGES[page]()
