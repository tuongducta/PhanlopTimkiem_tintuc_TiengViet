"""Giao diện Trans2Vec News (GĐ-H5) — 4 mục: Phân loại · Tìm kiếm · Dữ liệu và đánh giá · Tin mới nhất.

Chạy:  scripts/run-app.sh  (hoặc .venv-exp/bin/streamlit run src/system/app/streamlit_app.py từ thư mục gốc)
Mọi số liệu đọc từ MariaDB (model_run, eval_result, view); tìm kiếm qua Manticore; mô hình ở system/models/.
Kiểu dáng theo template tham khảo sources/template_demo/ (nền tối, cyan/indigo); chỉ lấy bố cục, không lấy số liệu mẫu.
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

# Kiểu dáng theo template: nền obsidian #07090E, thẻ kính mờ viền trắng 10%, cyan #22D3EE / indigo #6366F1,
# font Plus Jakarta Sans + JetBrains Mono. st.html không chạy script nên lớp Tailwind được dịch sang CSS thuần.
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');
html, body, [class*="st-"], .stMarkdown, button, input, textarea, select { font-family: 'Plus Jakarta Sans', sans-serif; }
[data-testid="stIconMaterial"], .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; }
code, .t2v-mono, .t2v-k, .t2v-tag, .t2v-cnt { font-family: 'JetBrains Mono', monospace; }
::selection { background: #00F2FE; color: #000; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgba(15,23,42,.4); }
::-webkit-scrollbar-thumb { background: rgba(99,102,241,.25); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,242,254,.4); }
.stApp { background-color: #07090E; background-attachment: fixed;
  background-image: radial-gradient(at 0% 0%, rgba(99,102,241,.12) 0, transparent 50%),
                    radial-gradient(at 100% 0%, rgba(0,242,254,.08) 0, transparent 40%),
                    radial-gradient(at 50% 100%, rgba(139,92,246,.06) 0, transparent 60%); }
header[data-testid="stHeader"] { background: transparent; height: 0; }
.block-container { padding-top: 1.1rem; padding-bottom: 3rem; max-width: 1400px; }
code { color: #67E8F9; background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.1); border-radius: 4px;
       padding: 1px 5px; font-size: .92em; }

/* ---------- thanh bên */
[data-testid="stSidebar"] { background: rgba(12,15,23,.92); border-right: 1px solid rgba(255,255,255,.05); }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding-top: .2rem; }
[data-testid="stSidebarHeader"] { height: 1rem; min-height: 1rem; padding: 0; }
[data-testid="stSidebar"] [role="radiogroup"] { gap: 6px; }
[data-testid="stSidebar"] [role="radiogroup"] label { width: 100%; padding: 10px 14px 10px 20px; border-radius: 12px; margin: 0;
  border: 1px solid transparent; position: relative; transition: background .15s, border-color .15s; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) { display: none; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover { background: rgba(255,255,255,.04); border-color: rgba(255,255,255,.05); }
[data-testid="stSidebar"] label[data-testid="stRadioOption"] p { font-size: 14px; font-weight: 500; color: #94A3B8; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"] [data-testid="stIconMaterial"] { color: #64748B; font-size: 19px; margin-right: 6px; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] {
  background: linear-gradient(90deg, rgba(79,70,229,.30), rgba(99,102,241,.20) 55%, transparent);
  border-color: rgba(99,102,241,.4); box-shadow: 0 10px 15px -3px rgba(79,70,229,.10); }
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"]::before { content: ''; position: absolute;
  left: 7px; top: 50%; transform: translateY(-50%); width: 5px; height: 16px; border-radius: 9px; background: #00F2FE;
  box-shadow: 0 0 8px #00F2FE; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] p { color: #fff; font-weight: 600; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] [data-testid="stIconMaterial"] { color: #22D3EE; }
.t2v-brand { display: flex; gap: 14px; align-items: center; padding: 6px 0 18px; margin-bottom: 14px;
  border-bottom: 1px solid rgba(255,255,255,.05); }
.t2v-logo { position: relative; width: 40px; height: 40px; border-radius: 12px; flex-shrink: 0; color: #fff;
  background: linear-gradient(45deg, #4F46E5, #6366F1, #22D3EE); display: flex; align-items: center; justify-content: center;
  font: 800 13px 'JetBrains Mono', monospace; box-shadow: 0 10px 15px -3px rgba(99,102,241,.2); outline: 1px solid rgba(255,255,255,.2); }
.t2v-logo::after { content: ''; position: absolute; top: -4px; right: -4px; width: 10px; height: 10px; border-radius: 50%;
  background: #00F2FE; box-shadow: 0 0 8px #00F2FE; }
.t2v-brand b { display: block; font-size: 15px; color: #fff; letter-spacing: -.01em; }
.t2v-brand span { font-size: 12px; color: #94A3B8; font-weight: 500; }
.t2v-sec { font: 600 10px 'JetBrains Mono', monospace; color: #64748B; letter-spacing: .08em; text-transform: uppercase;
  margin: 4px 0 10px 4px; }
.t2v-arch { margin-top: 22px; padding: 14px; border-radius: 16px; background: rgba(17,22,34,.8);
  border: 1px solid rgba(255,255,255,.1); box-shadow: 0 10px 15px -3px rgba(0,0,0,.4); }
.t2v-arch .hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.t2v-arch .hd span:first-child { font: 700 10px 'JetBrains Mono', monospace; letter-spacing: .08em; text-transform: uppercase; color: #22D3EE; }
.t2v-arch .on { display: flex; gap: 6px; align-items: center; font-size: 10px; font-weight: 600; color: #34D399; }
.t2v-arch .off { color: #FB7185; }
.t2v-arch .it { padding: 9px 10px; border-radius: 12px; background: rgba(7,9,14,.7); border: 1px solid rgba(255,255,255,.05); margin-top: 8px; }
.t2v-arch .it div { display: flex; justify-content: space-between; align-items: center; }
.t2v-arch .it b { font: 500 11px 'JetBrains Mono', monospace; color: #E2E8F0; }
.t2v-arch .it p { font-size: 11px; color: #94A3B8; margin: 3px 0 0; }

/* ---------- widget */
[data-testid="stWidgetLabel"] p { font: 600 12px 'JetBrains Mono', monospace; color: #CBD5E1; }
[data-baseweb="textarea"], [data-baseweb="input"], [data-baseweb="select"] > div {
  background: rgba(7,9,14,.8) !important; border-color: rgba(255,255,255,.12) !important; border-radius: 12px !important; }
[data-baseweb="textarea"]:focus-within, [data-baseweb="input"]:focus-within { border-color: rgba(34,211,238,.8) !important;
  box-shadow: 0 0 0 4px rgba(6,182,212,.15); }
[data-testid="stTextArea"] textarea { background: transparent; color: #F1F5F9; font-size: 14px; line-height: 1.7; }
[data-testid="stTextInput"] input { background: transparent; color: #F1F5F9; font-size: 14px; font-weight: 500; }
[data-testid="stBaseButton-primary"] { background: linear-gradient(90deg, #06B6D4, #4F46E5 60%, #4338CA); color: #fff;
  border: 1px solid rgba(255,255,255,.2); border-radius: 12px; font-weight: 700; box-shadow: 0 10px 15px -3px rgba(6,182,212,.2); }
[data-testid="stBaseButton-primary"]:hover { color: #fff; border-color: rgba(255,255,255,.35); filter: brightness(1.1);
  box-shadow: 0 10px 20px -3px rgba(6,182,212,.4); }
[data-testid="stBaseButton-primary"]:disabled { opacity: .45; filter: none; box-shadow: none; }
[data-testid="stBaseButton-secondary"] { background: rgba(255,255,255,.03); color: #94A3B8; border: 1px solid rgba(255,255,255,.1);
  border-radius: 12px; }
[data-testid="stBaseButton-secondary"]:hover { background: rgba(6,182,212,.08); color: #67E8F9; border-color: rgba(34,211,238,.5);
  box-shadow: 0 0 12px rgba(0,242,254,.2); }
[data-testid="stBaseButton-pills"], [data-testid="stBaseButton-segmented_control"] { background: rgba(255,255,255,.03);
  color: #CBD5E1; border: 1px solid rgba(255,255,255,.1); border-radius: 12px; font-size: 12px; }
[data-testid="stBaseButton-pills"]:hover, [data-testid="stBaseButton-segmented_control"]:hover { background: rgba(255,255,255,.08);
  color: #fff; border-color: rgba(255,255,255,.2); }
[data-testid="stBaseButton-pillsActive"], [data-testid="stBaseButton-segmented_controlActive"] {
  background: linear-gradient(90deg, rgba(79,70,229,.4), rgba(6,182,212,.3)); color: #67E8F9; font-weight: 600;
  border: 1px solid rgba(34,211,238,.4); border-radius: 12px; font-size: 12px; box-shadow: 0 0 12px rgba(0,242,254,.15); }
[data-testid="stExpander"] details { background: rgba(12,15,23,.72); border: 1px solid rgba(255,255,255,.1); border-radius: 16px; }
[data-testid="stExpander"] summary p { font-weight: 600; color: #E2E8F0; }
[data-testid="stCaptionContainer"] { color: #94A3B8; }

/* ---------- thẻ: container có key bắt đầu bằng card_ hoặc news_ */
.stVerticalBlock[class*="st-key-card"] { background-color: rgba(12,15,23,.72) !important; border: 1px solid rgba(255,255,255,.1) !important;
  border-radius: 16px !important; padding: 22px 24px !important; box-shadow: 0 25px 50px -12px rgba(0,0,0,.8) !important;
  background-image: radial-gradient(circle at 100% 0%, rgba(99,102,241,.10), transparent 40%) !important; }
.stVerticalBlock[class*="st-key-news_"] { background-color: rgba(7,9,14,.6) !important; border: 1px solid rgba(255,255,255,.05) !important;
  border-radius: 12px !important; padding: 14px 16px !important; transition: border-color .15s, background-color .15s; }
.stVerticalBlock[class*="st-key-news_"]:hover { border-color: rgba(6,182,212,.3) !important; background-color: rgba(7,9,14,.9) !important; }

/* ---------- khối HTML dùng chung */
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #22D3EE; box-shadow: 0 0 8px #00F2FE; flex-shrink: 0; }
.dot.sm { width: 6px; height: 6px; }
.dot.i { background: #6366F1; box-shadow: 0 0 8px #6366F1; }
.dot.g { background: #34D399; box-shadow: 0 0 6px #34D399; }
.dot.r { background: #FB7185; box-shadow: 0 0 6px #FB7185; }
.dot.off { background: #64748B; box-shadow: none; }
.t2v-ic { font-family: 'Material Symbols Rounded'; font-size: 18px; line-height: 1; font-weight: 400; flex-shrink: 0;
  font-style: normal; letter-spacing: normal; text-transform: none; white-space: nowrap; -webkit-font-feature-settings: 'liga'; }
.t2v-top { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;
  padding: 4px 0 14px; margin-bottom: 4px; border-bottom: 1px solid rgba(255,255,255,.05); }
.t2v-crumb { display: flex; gap: 8px; align-items: center; font: 12px 'JetBrains Mono', monospace; color: #94A3B8; }
.t2v-crumb .sep { color: #475569; }
.t2v-crumb b { display: flex; gap: 6px; align-items: center; color: #fff; font-weight: 600; }
.t2v-badges { display: flex; gap: 10px; flex-wrap: wrap; }
.t2v-badge { display: inline-flex; gap: 8px; align-items: center; padding: 6px 12px; border-radius: 12px; font-size: 12px;
  color: #CBD5E1; background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.1); }
.t2v-badge .t2v-ic { font-size: 16px; color: #22D3EE; }
.t2v-badge strong { color: #fff; font-family: 'JetBrains Mono', monospace; }
.t2v-badge em { font-style: normal; color: #22D3EE; font: 600 12px 'JetBrains Mono', monospace; }
.t2v-badge .bar { color: rgba(255,255,255,.2); }
.t2v-badge.model { color: #A5B4FC; background: rgba(99,102,241,.1); border-color: rgba(99,102,241,.3);
  box-shadow: 0 0 25px -4px rgba(99,102,241,.35); font-family: 'JetBrains Mono', monospace; }
.t2v-head { margin: 16px 0 14px; }
.t2v-h1 { display: flex; gap: 10px; align-items: center; font-size: 24px; font-weight: 800; color: #fff; letter-spacing: -.02em; margin: 0; }
.t2v-h1 .dot { width: 10px; height: 10px; }
.t2v-sub { font: 12px 'JetBrains Mono', monospace; color: #94A3B8; margin-top: 4px; }
.t2v-banner { display: flex; gap: 14px; align-items: flex-start; padding: 14px 18px; margin-bottom: 18px; border-radius: 16px;
  background: rgba(245,158,11,.04); border: 1px solid rgba(245,158,11,.22);
  background-image: radial-gradient(circle at 0% 0%, rgba(245,158,11,.10), transparent 30%); }
.t2v-banner .ib { padding: 7px; border-radius: 12px; color: #FBBF24; background: rgba(245,158,11,.1); border: 1px solid rgba(245,158,11,.2); display: flex; }
.t2v-banner .ib .t2v-ic { font-size: 20px; }
.t2v-banner div:last-child { font-size: 13px; line-height: 1.65; color: rgba(253,230,138,.9); font-weight: 300; }
.t2v-banner strong { font-weight: 600; color: #FCD34D; font-family: 'JetBrains Mono', monospace; margin-right: 6px; }
.t2v-banner b { color: #fff; font-weight: 600; }
.t2v-card { position: relative; overflow: hidden; background: rgba(12,15,23,.72); border: 1px solid rgba(255,255,255,.1);
  border-radius: 16px; padding: 22px 24px; box-shadow: 0 25px 50px -12px rgba(0,0,0,.8);
  background-image: radial-gradient(circle at 100% 0%, rgba(6,182,212,.08), transparent 35%); }
.t2v-card.flat { padding: 0; }
.t2v-ch { display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap;
  padding-bottom: 14px; margin-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,.05); }
.t2v-ch.nb { border-bottom: 0; padding-bottom: 0; }
.t2v-ch h2, .t2v-ch h3 { display: flex; gap: 10px; align-items: center; margin: 0; padding: 0; color: #fff; font-weight: 700; letter-spacing: -.01em; }
.t2v-ch h2 { font-size: 17px; } .t2v-ch h3 { font-size: 14px; }
.t2v-ch p { font-size: 12px; color: #94A3B8; margin: 4px 0 0; }
.t2v-ch p b { color: #67E8F9; }
.t2v-k { display: flex; gap: 6px; align-items: center; font-size: 10px; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase; color: #94A3B8; }
.t2v-k.cy { color: #22D3EE; text-transform: none; letter-spacing: 0; }
.t2v-tag { font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 6px; color: #67E8F9;
  background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.1); white-space: nowrap; }
.t2v-tag.i { color: #A5B4FC; background: rgba(30,27,75,.4); border-color: rgba(99,102,241,.2); }
.t2v-tag.g { color: #6EE7B7; background: rgba(16,185,129,.15); border-color: rgba(16,185,129,.3); }
.t2v-cnts { display: flex; gap: 8px; }
.t2v-cnt { font-size: 12px; color: #94A3B8; padding: 4px 10px; border-radius: 8px; background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.1); }
.t2v-foot { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; font-size: 12px; color: #94A3B8; min-height: 40px; }
.t2v-foot b { color: #E2E8F0; }
.t2v-grid3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.t2v-grid4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 18px; }
.t2v-grid5 { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; }
.t2v-split { display: grid; grid-template-columns: 3fr 2fr; gap: 20px; }
@media (max-width: 1150px) { .t2v-grid3, .t2v-grid4, .t2v-grid5, .t2v-split { grid-template-columns: 1fr 1fr; } }
@media (max-width: 760px) { .t2v-grid3, .t2v-grid4, .t2v-grid5, .t2v-split { grid-template-columns: 1fr; } }
.t2v-res { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin: 22px 0 14px; }
.t2v-res h3 { display: flex; gap: 8px; align-items: center; font-size: 16px; font-weight: 700; color: #fff; margin: 0; padding: 0; }
.t2v-res .t2v-mono { font-size: 12px; color: #94A3B8; }
.t2v-res .t2v-mono b { color: #67E8F9; }
.t2v-done { display: inline-flex; gap: 6px; align-items: center; padding: 2px 10px; border-radius: 999px; font: 700 10px 'JetBrains Mono', monospace;
  color: #6EE7B7; background: rgba(16,185,129,.15); border: 1px solid rgba(16,185,129,.3); }
.t2v-bar { height: 8px; border-radius: 999px; background: #07090E; border: 1px solid rgba(255,255,255,.05); overflow: hidden; }
.t2v-bar.big { height: 12px; padding: 2px; border-color: rgba(255,255,255,.1); }
.t2v-bar.thin { height: 6px; }
.t2v-bar i { display: block; height: 100%; border-radius: 999px; background: linear-gradient(90deg, #6366F1, #22D3EE);
  box-shadow: 0 0 8px #00F2FE; }
.t2v-bar i.lo { background: #475569; box-shadow: none; }
.t2v-bar i.mid { background: rgba(6,182,212,.8); box-shadow: none; }
.t2v-main { display: flex; gap: 16px; align-items: flex-start; }
.t2v-emo { width: 56px; height: 56px; border-radius: 16px; flex-shrink: 0; display: flex; align-items: center; justify-content: center;
  font-size: 26px; background: linear-gradient(45deg, #4F46E5, #6366F1, #06B6D4); border: 1px solid rgba(255,255,255,.2);
  box-shadow: 0 10px 15px -3px rgba(79,70,229,.3); }
.t2v-big { font-size: 24px; font-weight: 800; color: #fff; letter-spacing: -.02em; line-height: 1.2; }
.t2v-mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #94A3B8; }
.t2v-mono b { color: #67E8F9; }
.t2v-lbl { display: flex; justify-content: space-between; align-items: baseline; font: 12px 'JetBrains Mono', monospace;
  color: #94A3B8; margin: 22px 0 8px; }
.t2v-lbl b { color: #67E8F9; font-size: 14px; }
.t2v-sep { border-top: 1px solid rgba(255,255,255,.05); margin: 20px 0 12px; }
.t2v-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.t2v-chip { font: 500 12px 'JetBrains Mono', monospace; padding: 4px 10px; border-radius: 8px; color: #CBD5E1;
  background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.1); }
.t2v-chip.hi { color: #67E8F9; background: rgba(8,51,68,.4); border-color: rgba(6,182,212,.3); box-shadow: 0 0 8px rgba(0,242,254,.1); }
.t2v-chip.fi { font-size: 11px; color: #67E8F9; background: rgba(17,22,34,.9); border-color: rgba(6,182,212,.3); }
.t2v-mrow { padding: 11px 12px; border-radius: 12px; background: rgba(7,9,14,.6); border: 1px solid rgba(255,255,255,.05); margin-bottom: 10px; }
.t2v-mrow.hl { background: rgba(30,27,75,.3); border-color: rgba(99,102,241,.3); }
.t2v-mrow .hd { display: flex; justify-content: space-between; align-items: center; gap: 8px; font-size: 12px; margin-bottom: 7px; }
.t2v-mrow .nm { display: flex; gap: 7px; align-items: center; color: #CBD5E1; font-weight: 500; }
.t2v-mrow.hl .nm { color: #fff; font-weight: 700; }
.t2v-mrow .pv { font-family: 'JetBrains Mono', monospace; color: #CBD5E1; white-space: nowrap; }
.t2v-mrow .pv b { color: #fff; }
.t2v-mrow.hl .pv b { color: #67E8F9; }
.t2v-mrow .ds { font-size: 11px; color: #94A3B8; margin-top: 6px; }
.t2v-mrow.hl .ds { color: rgba(165,180,252,.85); }
.t2v-dist { margin-bottom: 13px; }
.t2v-dist .hd { display: flex; justify-content: space-between; font-size: 12px; font-weight: 500; color: #CBD5E1; margin-bottom: 5px; }
.t2v-dist .hd b { font-family: 'JetBrains Mono', monospace; color: #94A3B8; font-weight: 500; }
.t2v-dist.top .hd span { color: #fff; font-weight: 600; } .t2v-dist.top .hd b { color: #67E8F9; font-weight: 700; }
.t2v-cfoot { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding-top: 12px; margin-top: 16px;
  border-top: 1px solid rgba(255,255,255,.05); font: 11px 'JetBrains Mono', monospace; color: #64748B; }
.t2v-cfoot b { color: #fff; }
.t2v-text { max-height: 280px; overflow: auto; line-height: 1.75; font-size: 13px; color: #CBD5E1; padding: 14px;
  border-radius: 12px; background: rgba(7,9,14,.8); border: 1px solid rgba(255,255,255,.1); box-shadow: inset 0 2px 4px rgba(0,0,0,.3); }
mark { background: rgba(251,191,36,.25); color: #FCD34D; padding: 0 3px; border-radius: 4px; font-weight: 600; border: 1px solid rgba(251,191,36,.4); }
.t2v-cap { font: 600 11px 'JetBrains Mono', monospace; color: #94A3B8; margin: 0 0 8px; }
.t2v-cat { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 8px; font-size: 11px; font-weight: 500;
  white-space: nowrap; border: 1px solid; }
.t2v-cat.cyan { color: #67E8F9; background: rgba(8,51,68,.5); border-color: rgba(6,182,212,.3); }
.t2v-cat.sky { color: #7DD3FC; background: rgba(12,74,110,.4); border-color: rgba(14,165,233,.3); }
.t2v-cat.violet { color: #C4B5FD; background: rgba(46,16,101,.45); border-color: rgba(139,92,246,.3); }
.t2v-cat.amber { color: #FCD34D; background: rgba(69,26,3,.5); border-color: rgba(245,158,11,.3); }
.t2v-cat.rose { color: #FDA4AF; background: rgba(76,5,25,.5); border-color: rgba(244,63,94,.3); }
.t2v-cat.emerald { color: #6EE7B7; background: rgba(2,44,34,.5); border-color: rgba(16,185,129,.3); }
.t2v-cat.indigo { color: #A5B4FC; background: rgba(30,27,75,.5); border-color: rgba(99,102,241,.3); }
.t2v-cat.lime { color: #BEF264; background: rgba(26,46,5,.5); border-color: rgba(132,204,22,.3); }
.t2v-cat.pink { color: #F9A8D4; background: rgba(80,7,36,.5); border-color: rgba(236,72,153,.3); }
.t2v-cat.blue { color: #93C5FD; background: rgba(23,37,84,.5); border-color: rgba(59,130,246,.3); }
.t2v-cat.gray { color: #94A3B8; background: rgba(255,255,255,.04); border-color: rgba(255,255,255,.1); }
.t2v-stat { display: flex; gap: 16px; align-items: center; padding: 18px 20px; border-radius: 16px; background: rgba(12,15,23,.72);
  border: 1px solid rgba(255,255,255,.1); box-shadow: 0 20px 25px -5px rgba(0,0,0,.5); }
.t2v-stat .ib { width: 46px; height: 46px; border-radius: 12px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border: 1px solid; }
.t2v-stat .ib .t2v-ic { font-size: 22px; }
.t2v-stat .ib.cyan { color: #22D3EE; background: rgba(8,51,68,.4); border-color: rgba(6,182,212,.3); box-shadow: 0 0 12px rgba(0,242,254,.15); }
.t2v-stat .ib.amber { color: #FBBF24; background: rgba(69,26,3,.4); border-color: rgba(245,158,11,.3); box-shadow: 0 0 12px rgba(245,158,11,.15); }
.t2v-stat .ib.emerald { color: #34D399; background: rgba(2,44,34,.4); border-color: rgba(16,185,129,.3); box-shadow: 0 0 12px rgba(52,211,153,.15); }
.t2v-stat .ib.indigo { color: #A5B4FC; background: rgba(30,27,75,.4); border-color: rgba(99,102,241,.3); box-shadow: 0 0 12px rgba(99,102,241,.2); }
.t2v-stat .lb { font-size: 12px; color: #94A3B8; font-weight: 500; }
.t2v-stat .vl { font: 800 22px 'JetBrains Mono', monospace; color: #fff; letter-spacing: -.02em; margin-top: 2px; white-space: nowrap; }
.t2v-stat .vl.amber { color: #FCD34D; } .t2v-stat .vl.cyan { color: #67E8F9; }
.t2v-stat .sb { font-size: 11px; color: #94A3B8; margin-top: 2px; }
.t2v-kpi { padding: 16px; border-radius: 12px; background: rgba(7,9,14,.7); border: 1px solid rgba(255,255,255,.05); }
.t2v-kpi .lb { font: 12px 'JetBrains Mono', monospace; color: #94A3B8; }
.t2v-kpi .vl { font: 800 24px 'JetBrains Mono', monospace; color: #fff; letter-spacing: -.02em; margin-top: 8px; white-space: nowrap; }
.t2v-kpi .vl.cyan { color: #22D3EE; } .t2v-kpi .vl.sm { font-size: 19px; } .t2v-kpi .vl small { color: #475569; font-weight: 300; }
.t2v-kpi .sb { font-size: 11px; color: #94A3B8; margin-top: 4px; }
.t2v-tw { overflow-x: auto; border-radius: 12px; border: 1px solid rgba(255,255,255,.05); background: rgba(7,9,14,.6); }
.t2v-table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; }
.t2v-table th { padding: 11px 14px; font: 600 10px 'JetBrains Mono', monospace; letter-spacing: .08em; text-transform: uppercase;
  color: #94A3B8; background: rgba(255,255,255,.02); border-bottom: 1px solid rgba(255,255,255,.1); }
.t2v-table td { padding: 11px 14px; color: #CBD5E1; border-bottom: 1px solid rgba(255,255,255,.05); vertical-align: top; }
.t2v-table tr:last-child td { border-bottom: 0; }
.t2v-table tbody tr:hover { background: rgba(255,255,255,.03); }
.t2v-table .c { text-align: center; } .t2v-table .r { text-align: right; }
.t2v-table .n { font-family: 'JetBrains Mono', monospace; }
.t2v-table .best { color: #fff; font-weight: 700; }
.t2v-table tr.hl { background: rgba(30,27,75,.4); box-shadow: inset 0 0 15px rgba(0,242,254,.08); }
.t2v-table tr.hl td { color: #67E8F9; font-weight: 600; border-top: 2px solid rgba(6,182,212,.4); }
.t2v-table tr.hl td:first-child { color: #fff; }
.t2v-table tr td:first-child { border-left: 4px solid transparent; }
.t2v-table tr.sel { background: rgba(30,27,75,.3); }
.t2v-table tr.sel td:first-child { border-left-color: #22D3EE; color: #67E8F9; font-weight: 700; }
.t2v-table tr.sel .tt { color: #67E8F9; font-weight: 700; }
.t2v-table .tt { color: #E2E8F0; font-weight: 600; line-height: 1.4; }
.t2v-table .sn { font-size: 11px; color: #94A3B8; margin-top: 2px; }
.t2v-table .fl { font: 10px 'JetBrains Mono', monospace; color: #64748B; margin-top: 2px; }
.t2v-table .sc { font: 700 12px 'JetBrains Mono', monospace; color: #E2E8F0; }
.t2v-table tr.sel .sc { color: #67E8F9; }
.t2v-tfoot { display: flex; justify-content: space-between; padding: 11px 18px; font: 500 11px 'JetBrains Mono', monospace;
  color: #94A3B8; background: rgba(7,9,14,.8); border-top: 1px solid rgba(255,255,255,.1); }
.t2v-tfoot span:last-child { color: #22D3EE; }
.t2v-sc3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 14px 0; }
.t2v-sc3 div { padding: 10px; border-radius: 12px; text-align: center; background: rgba(7,9,14,.7); border: 1px solid rgba(255,255,255,.1); }
.t2v-sc3 div.on { background: rgba(30,27,75,.4); border-color: rgba(34,211,238,.4); box-shadow: 0 0 12px rgba(0,242,254,.1); }
.t2v-sc3 span { display: block; font: 500 10px 'JetBrains Mono', monospace; color: #94A3B8; text-transform: uppercase; letter-spacing: .05em; }
.t2v-sc3 b { display: block; font: 700 14px 'JetBrains Mono', monospace; color: #E2E8F0; margin: 2px 0; }
.t2v-sc3 small { font: 10px 'JetBrains Mono', monospace; color: #64748B; }
.t2v-sc3 .on span, .t2v-sc3 .on b, .t2v-sc3 .on small { color: #67E8F9; }
.t2v-meta { border-top: 1px solid rgba(255,255,255,.05); padding-top: 12px; font: 12px 'JetBrains Mono', monospace; color: #94A3B8; }
.t2v-meta div { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 7px; }
.t2v-meta span:first-child { white-space: nowrap; }
.t2v-meta span:last-child { color: #CBD5E1; text-align: right; }
.t2v-meta .file { color: #67E8F9; font-size: 11px; padding: 1px 8px; border-radius: 8px; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.1); }
.t2v-art { font-size: 16px; font-weight: 700; color: #fff; line-height: 1.4; margin: 12px 0; }
.t2v-note { font: italic 12px 'JetBrains Mono', monospace; color: #94A3B8; }
.t2v-src { padding: 18px 20px; border-radius: 16px; background: rgba(12,15,23,.8); border: 1px solid rgba(255,255,255,.1);
  box-shadow: 0 25px 50px -12px rgba(0,0,0,.8); background-image: radial-gradient(circle at 100% 0%, rgba(6,182,212,.10), transparent 35%); }
.t2v-src .hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.t2v-src h3 { font-size: 16px; font-weight: 700; color: #fff; margin: 0; padding: 0; }
.t2v-src .url { font: 12px 'JetBrains Mono', monospace; color: #94A3B8; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 14px; }
.t2v-st { display: inline-flex; gap: 6px; align-items: center; padding: 2px 10px; border-radius: 999px; font: 600 11px 'JetBrains Mono', monospace; border: 1px solid; }
.t2v-st.ok { color: #6EE7B7; background: rgba(16,185,129,.15); border-color: rgba(16,185,129,.3); }
.t2v-st.bad { color: #FDA4AF; background: rgba(244,63,94,.15); border-color: rgba(244,63,94,.3); max-width: 60%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.t2v-mini { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,.05); text-align: center; }
.t2v-mini div { padding: 9px; border-radius: 12px; background: rgba(7,9,14,.7); border: 1px solid rgba(255,255,255,.05); }
.t2v-mini span { display: block; font: 11px 'JetBrains Mono', monospace; color: #94A3B8; }
.t2v-mini b { display: block; font: 700 17px 'JetBrains Mono', monospace; color: #fff; margin-top: 2px; }
.t2v-mini b.cy { color: #67E8F9; } .t2v-mini b.gr { color: #34D399; } .t2v-mini small { font-size: 11px; font-weight: 400; color: #94A3B8; }
.t2v-nmeta { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; font: 12px 'JetBrains Mono', monospace; color: #94A3B8; margin-bottom: 5px; }
.t2v-nmeta b { color: #67E8F9; font-weight: 600; } .t2v-nmeta .sep { color: #475569; }
.t2v-ntitle a { font-size: 14px; font-weight: 600; color: #fff; text-decoration: none; line-height: 1.4; }
.t2v-ntitle a:hover { color: #67E8F9; }
.t2v-nsum { font-size: 12px; color: #94A3B8; font-weight: 300; margin-top: 4px; line-height: 1.55;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
</style>
"""
st.html(CSS)


# ===================================================================== tiện ích HTML
e = lambda x: html.escape(str(x))
vn = lambda x, d=3: f"{x:.{d}f}".replace(".", ",")  # số thập phân dấu phẩy như trong báo cáo
pct = lambda x: f"{x * 100:.1f}%".replace(".", ",")
num = lambda n: f"{int(n):,}".replace(",", ".")


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


def dark(chart):
    """Biểu đồ Altair trên nền tối của app."""
    return (chart.configure(background="transparent", font="Plus Jakarta Sans")
            .configure_axis(labelColor="#94A3B8", titleColor="#94A3B8", domainColor="#1E293B", tickColor="#1E293B",
                            gridColor="#1E293B", labelFont="JetBrains Mono", titleFont="JetBrains Mono")
            .configure_legend(labelColor="#94A3B8", titleColor="#94A3B8", labelFont="JetBrains Mono")
            .configure_view(stroke=None))


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


@st.cache_data(ttl=3600)
def corpus():
    sp = q("SELECT split, COUNT(*) n FROM article GROUP BY split").set_index("split")["n"]
    return int(sp.sum()), int(sp["train"]), int(sp["test"])


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
                  on_click=lambda: st.session_state.update(text="", ex_pick=None))
        c3.html('<div class="t2v-foot"><span class="dot sm"></span><span class="t2v-mono">Tách từ: <code>pyvi</code></span>'
                f'<span>·</span><span>{n} mô hình chạy song song, Macro-F1 đo trên <b>{num(n_test)}</b> bài test</span></div>')
    if not go:
        return

    r = clf.predict(text, log=True)
    models = r["models"]
    ok = [m for m in models if m["proba"]]
    if not ok:
        st.warning("Không có item nào của bài nằm trong từ vựng của các mô hình. Thử một đoạn dài hơn.")
        return
    best = max(m["f1"] for m in models)
    base = next((m["f1"] for m in models if m["kind"] == "trans2vec-orig"), None)
    main = next((m for m in ok if m["improved"]), None) or max(ok, key=lambda m: m["f1"])
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
    rows = ""
    for m in models:
        hl = m is main
        if m["proba"]:
            _, nm, x = m["proba"][0]
            right = f'{e(nm)} · <b>{pct(x)}</b>'
        else:
            x, right = 0.0, "—"
        delta = "mốc" if base is None or m["kind"] == "trans2vec-orig" else vn(m["f1"] - base).replace("-", "−")
        delta = delta if delta == "mốc" or delta.startswith("−") else "+" + delta
        star = ' <span class="t2v-tag g">F1 cao nhất</span>' if m["f1"] == best else ""
        rows += (f'<div class="t2v-mrow{" hl" if hl else ""}"><div class="hd"><span class="nm"><span class="dot sm'
                 f'{"" if hl else " off"}"></span>{e(m["name"])}</span><span class="pv">{right}</span></div>'
                 f'{bar(x, "" if hl else "lo", "thin")}<div class="ds">{e(m["note"])} · Macro-F1 {vn(m["f1"])} '
                 f'({delta}){star}</div></div>')
    card2 = (f'<div class="t2v-card"><div class="t2v-ch nb"><span class="t2v-k"><span class="dot sm i"></span>'
             f'So sánh {n} mô hình</span><span class="t2v-tag i">top-1 · xác suất</span></div>{rows}'
             '<div class="t2v-cfoot"><span>* Điểm của mốc là softmax điểm quyết định SVM, không phải xác suất.</span></div></div>')
    dist = "".join(f'<div class="t2v-dist{" top" if i == 0 else ""}"><div class="hd"><span>{i + 1}. {e(nm)}</span>'
                   f'<b>{pct(x)}</b></div>{bar(x, "" if i == 0 else "lo")}</div>'
                   for i, (_, nm, x) in enumerate(main["proba"][:5]))
    top5 = sum(x for _, _, x in main["proba"][:5])
    card3 = (f'<div class="t2v-card"><div class="t2v-ch nb"><span class="t2v-k"><span class="dot sm"></span>'
             f'Phân bố xác suất đa chuyên mục</span><span class="t2v-k cy">Top 5</span></div>{dist}'
             f'<div class="t2v-cfoot"><span>Mô hình: <b>{e(main["name"])}</b></span><span>Top 5 = {pct(top5)}</span></div></div>')
    st.html(f'<div class="t2v-grid3">{card1}{card2}{card3}</div>')

    joi = next((m for m in models if m["kind"] == "trans2vec-joi"), None)
    if joi and joi["proba"]:
        fi_words = {w for f in r["fi"] for w in f}
        fi = (chips([" + ".join(f) for f in r["fi"][:16]], cls="fi") if r["fi"] else
              '<div class="t2v-mono">Không có FI nào đủ các từ; dự đoán dựa trên item đơn.</div>')
        why = f"Vì sao Trans2Vec-JOI chọn “{joi['proba'][0][1]}”?"
        st.html(f'<div class="t2v-card" style="margin-top:20px">'
                f'{card_head(why, "Từ thuộc FI khớp được tô sáng trong bài.")}'
                f'<div class="t2v-split"><div><div class="t2v-text">{highlight(text, fi_words)}</div></div>'
                f'<div><div class="t2v-cap">FI khớp (độ dài ≥ 2)</div>{fi}<div class="t2v-sep"></div>'
                f'<div class="t2v-cap">Item của bài (top tf·idf)</div>{chips(r["items"][:20])}</div></div></div>')

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
                f'<div class="fl">{e(d["file"])}</div></td><td>{cat_chip(d["code"], d["category"])}</td>'
                f'<td class="n" style="font-size:10px;color:#94A3B8">{e(", ".join(d["fi"][:2])) or "—"}</td>'
                f'<td class="r"><span class="sc">{vn(h["score"], 4)}</span>'
                f'{bar(h["score"] / top, "" if sel else "mid", "thin")}'
                f'<div class="fl">BM25 #{h["bm25_rank"] or "—"} · vec #{h["knn_rank"] or "—"}</div></td></tr>')
    left.html(f'<div class="t2v-card flat"><div class="t2v-ch" style="padding:16px 20px;margin:0;border-color:rgba(255,255,255,.1)">'
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
def eval_table(t, cols, hl_row):
    """Bảng HTML: hàng của Trans2Vec-JOI được tô như template, giá trị lớn nhất mỗi cột in đậm."""
    best = {c: t[c].max() for c, _ in cols}
    head = "<th>Biểu diễn</th>" + "".join(f'<th class="c">{e(lb)}</th>' for _, lb in cols)
    body = ""
    for name, r in t.iterrows():
        tds = "".join(f'<td class="c n{" best" if r[c] == best[c] else ""}">{vn(r[c]) if pd.notna(r[c]) else "—"}</td>'
                      for c, _ in cols)
        first = f'<span class="dot sm"></span> {e(name)}' if name == hl_row else e(name)
        body += f'<tr class="{"hl" if name == hl_row else ""}"><td>{first}</td>{tds}</tr>'
    return f'<div class="t2v-tw"><table class="t2v-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def page_data():
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
              JOIN model_run e ON e.id = l.parent_id WHERE l.kind IN ('lr','svm') AND ev.metric IN ('acc','macro_f1')
              UNION ALL
              SELECT e.kind, ev.metric, ev.value FROM eval_result ev JOIN model_run e ON e.id = ev.run_id
              WHERE ev.task='search'""")
    ev["Biểu diễn"] = ev["kind"].map(names)
    t = ev.pivot_table(index="Biểu diễn", columns="metric", values="value")
    t = t.reindex([n for n in names.values() if n in t.index])
    joi = names["trans2vec-joi"]
    st.html(f'<div class="t2v-split" style="grid-template-columns:1fr 1fr;margin-bottom:20px">'
            f'<div class="t2v-card">{card_head(f"Phân loại · {num(n_test)} bài test", "LR (mốc: LinearSVC) trên tập test gốc của VNTC-10.", tag="Macro-F1")}'
            f'{eval_table(t[["acc", "macro_f1"]].dropna(how="all"), [("acc", "Accuracy"), ("macro_f1", "Macro-F1")], joi)}</div>'
            f'<div class="t2v-card">{card_head("Tìm kiếm · 1.000 truy vấn là bài báo", "Cosine vét cạn trên vector của từng biểu diễn.", tag="Ranking", dot="i")}'
            f'{eval_table(t[["p@10", "map@100", "ndcg@10"]].dropna(how="all"), [("p@10", "P@10"), ("map@100", "MAP@100"), ("ndcg@10", "nDCG@10")], joi)}'
            f'<div class="t2v-cfoot"><span>“Liên quan” = cùng chuyên mục (proxy).</span></div></div></div>')

    a, b = st.columns(2, gap="medium")
    with a.container(key="card_cm"):
        st.html(card_head("Ma trận nhầm lẫn", "Tỉ lệ theo hàng (chuyên mục thực tế), view <b>v_confusion</b>."))
        kinds = [k for k in names if names[k] in t.index]
        kind = st.selectbox("Biểu diễn", kinds, format_func=names.get, index=kinds.index("trans2vec-joi"))
        cm = q("""SELECT v.true_code, v.pred_code, v.n FROM v_confusion v JOIN model_run l ON l.id = v.run_id
                  JOIN model_run e ON e.id = l.parent_id WHERE e.kind = %s""", (kind,))
        cm["tỉ lệ"] = cm["n"] / cm.groupby("true_code")["n"].transform("sum")
        heat = alt.Chart(cm).mark_rect(stroke="#07090E", strokeWidth=2, cornerRadius=3).encode(
            x=alt.X("pred_code:N", title="Dự đoán"), y=alt.Y("true_code:N", title="Thực tế"),
            color=alt.Color("tỉ lệ:Q", scale=alt.Scale(range=["#111622", "#4F46E5", "#22D3EE"]),
                            legend=alt.Legend(format=".0%")),
            tooltip=["true_code", "pred_code", "n", alt.Tooltip("tỉ lệ:Q", format=".1%")])
        st.altair_chart(dark(heat.properties(height=330)), width="stretch", theme=None)
    with b.container(key="card_corpus"):
        st.html(card_head("Thống kê corpus", "Số bài và số từ trung bình theo chuyên mục, view <b>v_corpus_stats</b>."))
        st.dataframe(q("SELECT name AS `Chuyên mục`, split AS `Tập`, n_article AS `Số bài`, avg_words AS `TB từ` "
                       "FROM v_corpus_stats ORDER BY code, split"), hide_index=True, width="stretch", height=410)

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
    n_all = q("SELECT COUNT(*) n FROM feed_item")["n"][0]
    with st.container(key="card_feed"):
        st.html(card_head("Tin mới nhất từ RSS", f"Lần lấy gần nhất <b>{last}</b> · đang có {num(n_all)} tin trong CSDL "
                          "· hiển thị 30 tin mới nhất", h="h2"))
        c1, c2, c3 = st.columns([4, 1.3, 1.6], vertical_alignment="center")
        pick = c1.segmented_control("Nguồn", ["Tất cả"] + src["name"].tolist(), default="Tất cả", key="news_src",
                                    label_visibility="collapsed") or "Tất cả"
        news = q("SELECT id, source_name, published_at, title, summary, url, pred_category FROM v_latest_news "
                 + ("" if pick == "Tất cả" else "WHERE source_name = %s ") + "ORDER BY published_at DESC LIMIT 30",
                 None if pick == "Tất cả" else (pick,))
        todo = news[news["pred_category"].isna()]
        if c3.button("Lấy tin ngay", type="primary", icon=":material/sync:", disabled=wait, width="stretch",
                     help=f"Tối đa một lần mỗi {fetch_news.MIN_LOOP_MIN} phút"
                          + (f"; lần gần nhất cách đây {recent} phút" if recent is not None else "")):
            con = connect_mariadb()  # fetch_all commit/rollback theo từng báo nên cần kết nối không autocommit
            with st.spinner("Đang đọc RSS…"):
                fetch_news.fetch_all(con)
            con.close()
            st.rerun()
        if c2.button(f"Phân loại {len(todo)} tin", disabled=todo.empty, width="stretch",
                     help="Phân loại các tin chưa có nhãn bằng mô hình cải tiến"):
            with st.spinner("Đang phân loại bằng mô hình cải tiến…"):
                for r in todo.itertuples():
                    classify_news(s, clf, r)
            st.rerun()
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
                       f'<div class="t2v-nsum">{e(r.summary or "")}</div>')
                if b.button("Phân loại lại" if cat else "Phân loại bài này", key=f"n{r.id}", width="stretch"):
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
PAGES[page][0]()
