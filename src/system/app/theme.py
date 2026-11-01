import re

# Bảng màu được tách khỏi khung CSS để một nguồn duy nhất quyết định màu giao diện.
DARK_CYAN = {
        'light': False,
        'bg': '#07090E',
        'surface-rgb': '12 15 23',
        'surface-2': '#111622',
        'track-rgb': '15 23 42',
        'ink-rgb': '255 255 255',
        'grid': '#1E293B',
        'text-strong': '#FFFFFF',
        'text-input': '#F1F5F9',
        'text-em': '#E2E8F0',
        'text': '#CBD5E1',
        'text-2': '#94A3B8',
        'faint': '#64748B',
        'sep': '#475569',
        'selection-fg': '#000000',
        'logo-fg': '#FFFFFF',
        'a1': '#22D3EE',
        'a1-text': '#67E8F9',
        'a1-500': '#06B6D4',
        'a1-deep-rgb': '8 51 68',
        'neon': '#00F2FE',
        'a2': '#6366F1',
        'a2-600': '#4F46E5',
        'a2-700': '#4338CA',
        'a2-text': '#A5B4FC',
        'a2-deep-rgb': '30 27 75',
        'ok': '#34D399',
        'ok-text': '#6EE7B7',
        'ok-500-rgb': '16 185 129',
        'ok-deep-rgb': '2 44 34',
        'warn': '#FBBF24',
        'warn-text': '#FCD34D',
        'warn-500-rgb': '245 158 11',
        'warn-deep-rgb': '69 26 3',
        'bad': '#FB7185',
        'bad-text': '#FDA4AF',
        'bad-500-rgb': '244 63 94',
        'note-fg': '#FBBF24',
        'note-text': '#FCD34D',
        'note-soft-rgb': '253 230 138',
        'note-500-rgb': '245 158 11',
        'mark-fg': '#FCD34D',
        'mark-rgb': '251 191 36',
        'score-fg': '#FBBF24',
        'score-text': '#FCD34D',
        'score-500-rgb': '245 158 11',
        'score-deep-rgb': '69 26 3',
        'cat-cyan-fg': '#67E8F9',
        'cat-cyan-bg': 'rgba(8,51,68,.5)',
        'cat-cyan-bd': 'rgba(6,182,212,.3)',
        'cat-sky-fg': '#7DD3FC',
        'cat-sky-bg': 'rgba(12,74,110,.4)',
        'cat-sky-bd': 'rgba(14,165,233,.3)',
        'cat-violet-fg': '#C4B5FD',
        'cat-violet-bg': 'rgba(46,16,101,.45)',
        'cat-violet-bd': 'rgba(139,92,246,.3)',
        'cat-amber-fg': '#FCD34D',
        'cat-amber-bg': 'rgba(69,26,3,.5)',
        'cat-amber-bd': 'rgba(245,158,11,.3)',
        'cat-rose-fg': '#FDA4AF',
        'cat-rose-bg': 'rgba(76,5,25,.5)',
        'cat-rose-bd': 'rgba(244,63,94,.3)',
        'cat-emerald-fg': '#6EE7B7',
        'cat-emerald-bg': 'rgba(2,44,34,.5)',
        'cat-emerald-bd': 'rgba(16,185,129,.3)',
        'cat-indigo-fg': '#A5B4FC',
        'cat-indigo-bg': 'rgba(30,27,75,.5)',
        'cat-indigo-bd': 'rgba(99,102,241,.3)',
        'cat-lime-fg': '#BEF264',
        'cat-lime-bg': 'rgba(26,46,5,.5)',
        'cat-lime-bd': 'rgba(132,204,22,.3)',
        'cat-pink-fg': '#F9A8D4',
        'cat-pink-bg': 'rgba(80,7,36,.5)',
        'cat-pink-bd': 'rgba(236,72,153,.3)',
        'cat-blue-fg': '#93C5FD',
        'cat-blue-bg': 'rgba(23,37,84,.5)',
        'cat-blue-bd': 'rgba(59,130,246,.3)',
        'cat-gray-fg': '#94A3B8',
        'cat-gray-bg': 'rgba(255,255,255,.04)',
        'cat-gray-bd': 'rgba(255,255,255,.1)',
        'heat': ['#111622', '#4F46E5', '#22D3EE'],
        'heat-stroke': '#07090E',
        'heat-text-hi': '#07090E',
        'heat-text-lo': '#CBD5E1',
        'bg-glow': 'radial-gradient(at 0% 0%, rgba(99,102,241,.12) 0, transparent 50%), radial-gradient(at 100% 0%, rgba(0,242,254,.08) 0, transparent 40%), radial-gradient(at 50% 100%, rgba(139,92,246,.06) 0, transparent 60%)',
        'nav-active-bg': 'linear-gradient(90deg, rgb(var(--t2v-a2-600-rgb) / .30), rgb(var(--t2v-a2-rgb) / .20) 55%, transparent)',
        'logo-bg': 'linear-gradient(45deg, var(--t2v-a2-600), var(--t2v-a2), var(--t2v-a1))',
        'emo-bg': 'linear-gradient(45deg, var(--t2v-a2-600), var(--t2v-a2), var(--t2v-a1-500))',
        'bar-fill': 'linear-gradient(90deg, var(--t2v-a2), var(--t2v-a1))',
        'btn-primary-bg': 'linear-gradient(90deg, #0E7490, #4F46E5 60%, #4338CA)',
        'btn-primary-fg': '#FFFFFF',
        'btn-primary-bd': 'rgba(255,255,255,.2)',
        'btn-primary-bd-hover': 'rgba(255,255,255,.35)',
        'btn-primary-shadow': '0 10px 15px -3px rgb(var(--t2v-a1-500-rgb) / .2)',
        'btn-primary-shadow-hover': '0 10px 20px -3px rgb(var(--t2v-a1-500-rgb) / .4)',
        'seg-active-bg': 'linear-gradient(90deg, rgb(var(--t2v-a2-600-rgb) / .4), rgb(var(--t2v-a1-500-rgb) / .3))',
        'shadow-lg': '0 25px 50px -12px rgba(0,0,0,.8)',
        'shadow-md': '0 20px 25px -5px rgba(0,0,0,.5)',
        'shadow-sm': '0 10px 15px -3px rgba(0,0,0,.4)',
        'shadow-inset': 'inset 0 2px 4px rgba(0,0,0,.3)',
}
# Các bảng tối chỉ thay token khác để Tối cyan tiếp tục giữ nguyên giao diện B1.
DARK_GREEN = {**DARK_CYAN,
    'bg': '#060D0B', 'surface-rgb': '12 24 20', 'surface-2': '#151D1B', 'track-rgb': '21 29 27', 'grid': '#242C29',
    'faint': '#94A3B8', 'a1': '#34D399', 'a1-text': '#6EE7B7', 'a1-500': '#10B981', 'a1-deep-rgb': '2 44 34',
    'neon': '#5AF0B3', 'a2': '#2DD4BF', 'a2-600': '#0D9488', 'a2-700': '#0F766E', 'a2-text': '#5EEAD4', 'a2-deep-rgb': '4 47 46',
    'bg-glow': 'radial-gradient(at 0% 0%, rgb(var(--t2v-ok-500-rgb) / .12) 0, transparent 50%), radial-gradient(at 100% 0%, rgb(20 184 166 / .09) 0, transparent 40%), radial-gradient(at 50% 100%, rgb(5 150 105 / .08) 0, transparent 60%)',
    'btn-primary-bg': 'linear-gradient(90deg, #34D399, #2DD4BF)', 'btn-primary-fg': '#060D0B',
    'heat': ['#151D1B', '#0F766E', '#34D399'], 'heat-stroke': '#060D0B', 'heat-text-hi': '#060D0B',
}
DARK_ORANGE = {**DARK_CYAN,
    'bg': '#0B090E', 'surface-rgb': '24 18 32', 'surface-2': '#151219', 'track-rgb': '34 30 38', 'grid': '#2C2830',
    'a1': '#FB923C', 'a1-text': '#FDBA74', 'a1-500': '#F97316', 'a1-deep-rgb': '67 20 7', 'neon': '#FFB690',
    'a2': '#FFB783', 'a2-600': '#EA580C', 'a2-700': '#C2410C', 'a2-text': '#FED7AA', 'a2-deep-rgb': '67 20 7',
    'note-fg': '#38BDF8', 'note-text': '#7DD3FC', 'note-soft-rgb': '186 230 253', 'note-500-rgb': '14 165 233',
    'mark-fg': '#FDBA74', 'mark-rgb': '249 115 22', 'score-fg': '#FDBA74', 'score-text': '#FED7AA',
    'score-500-rgb': '251 146 60', 'score-deep-rgb': '67 20 7',
    'bg-glow': 'radial-gradient(at 0% 0%, rgba(249,115,22,.12) 0, transparent 50%), radial-gradient(at 100% 0%, rgba(225,29,72,.09) 0, transparent 40%), radial-gradient(at 50% 100%, rgba(194,65,12,.08) 0, transparent 60%)',
    'logo-bg': 'linear-gradient(45deg, #C2410C, #EA580C, #FB923C)',
    'btn-primary-bg': 'linear-gradient(90deg, #FB923C, #FFB783)', 'btn-primary-fg': '#0B090E',
    'heat': ['#151219', '#C2410C', '#FB923C'], 'heat-stroke': '#0B090E', 'heat-text-hi': '#0B090E',
}
LIGHT = {
    'light': True, 'bg': '#F8FAFC', 'surface-rgb': '255 255 255', 'surface-2': '#F1F5F9', 'track-rgb': '226 232 240', 'ink-rgb': '15 23 42',
    'grid': '#E2E8F0', 'text-strong': '#0F172A', 'text-input': '#0F172A', 'text-em': '#1E293B', 'text': '#334155', 'text-2': '#475569',
    'faint': '#64748B', 'sep': '#64748B', 'selection-fg': '#FFFFFF', 'logo-fg': '#FFFFFF',
    'a1': '#0E7490', 'a1-text': '#0E7490', 'a1-500': '#06B6D4', 'a1-deep-rgb': '207 250 254', 'neon': '#0891B2',
    'a2': '#6366F1', 'a2-600': '#4F46E5', 'a2-700': '#4338CA', 'a2-text': '#4338CA', 'a2-deep-rgb': '224 231 255',
    'ok': '#047857', 'ok-text': '#047857', 'ok-500-rgb': '16 185 129', 'ok-deep-rgb': '209 250 229',
    'warn': '#B45309', 'warn-text': '#92400E', 'warn-500-rgb': '245 158 11', 'warn-deep-rgb': '254 243 199',
    'bad': '#BE123C', 'bad-text': '#9F1239', 'bad-500-rgb': '244 63 94',
    'note-fg': '#0369A1', 'note-text': '#075985', 'note-soft-rgb': '12 74 110', 'note-500-rgb': '14 165 233',
    'mark-fg': '#92400E', 'mark-rgb': '251 191 36', 'score-fg': '#B45309', 'score-text': '#B45309', 'score-500-rgb': '245 158 11', 'score-deep-rgb': '254 243 199',
    'bg-glow': 'radial-gradient(at 0% 0%, rgb(99 102 241 / .06) 0, transparent 50%), radial-gradient(at 100% 0%, rgb(var(--t2v-a1-500-rgb) / .05) 0, transparent 40%), radial-gradient(at 50% 100%, rgb(139 92 246 / .04) 0, transparent 60%)',
    'nav-active-bg': 'linear-gradient(90deg, rgb(var(--t2v-a2-600-rgb) / .12), rgb(var(--t2v-a2-rgb) / .06) 55%, transparent)',
    'logo-bg': 'linear-gradient(45deg, #4F46E5, #6366F1, #22D3EE)', 'emo-bg': 'linear-gradient(45deg, var(--t2v-a2-600), var(--t2v-a2), var(--t2v-a1-500))',
    'bar-fill': 'linear-gradient(90deg, var(--t2v-a2), var(--t2v-a1))',
    'btn-primary-bg': 'linear-gradient(90deg, #0E7490, #4F46E5 60%, #4338CA)', 'btn-primary-fg': '#FFFFFF',
    'btn-primary-bd': 'rgba(255,255,255,.2)', 'btn-primary-bd-hover': 'rgba(255,255,255,.35)',
    'btn-primary-shadow': '0 10px 15px -3px rgba(6,182,212,.10)', 'btn-primary-shadow-hover': '0 10px 20px -3px rgba(6,182,212,.12)',
    'seg-active-bg': 'linear-gradient(90deg, rgba(79,70,229,.10), rgba(6,182,212,.10))',
    'shadow-lg': '0 25px 50px -12px rgba(15,23,42,.12)', 'shadow-md': '0 20px 25px -5px rgba(15,23,42,.08)',
    'shadow-sm': '0 10px 15px -3px rgba(15,23,42,.06)', 'shadow-inset': 'inset 0 2px 4px rgba(15,23,42,.06)',
    'heat': ['#F1F5F9', '#6366F1', '#0E7490'], 'heat-stroke': '#F8FAFC', 'heat-text-hi': '#FFFFFF', 'heat-text-lo': '#0F172A',
}
# Nhãn chuyên mục sáng dùng nền nhạt và chữ bậc 800 để tách được từng loại trên thẻ trắng.
_LIGHT_CATS = {
    'cyan': ('#155E75', '#ECFEFF', '#A5F3FC'), 'sky': ('#075985', '#F0F9FF', '#BAE6FD'), 'violet': ('#5B21B6', '#F5F3FF', '#DDD6FE'),
    'amber': ('#92400E', '#FFFBEB', '#FDE68A'), 'rose': ('#9F1239', '#FFF1F2', '#FECDD3'), 'emerald': ('#065F46', '#ECFDF5', '#A7F3D0'),
    'indigo': ('#3730A3', '#EEF2FF', '#C7D2FE'), 'lime': ('#3F6212', '#F7FEE7', '#D9F99D'), 'pink': ('#9D174D', '#FDF2F8', '#FBCFE8'),
    'blue': ('#1E40AF', '#EFF6FF', '#BFDBFE'), 'gray': ('#334155', '#F8FAFC', '#E2E8F0'),
}
for _tone, (_fg, _bg, _bd) in _LIGHT_CATS.items():
    LIGHT.update({'cat-' + _tone + '-fg': _fg, 'cat-' + _tone + '-bg': _bg, 'cat-' + _tone + '-bd': _bd})

PALETTES = {"Tối cyan": DARK_CYAN, "Tối xanh lục": DARK_GREEN, "Tối cam": DARK_ORANGE, "Sáng": LIGHT}
DEFAULT = "Tối cyan"
FONTS_IMPORT = (
    "\n@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');\n"
)

RGB_KEYS = {"bg", "surface-2", "a1", "a1-500", "neon", "a2", "a2-600", "a2-text", "ok"}

# Khung giữ nguyên cấu trúc bộ chọn; dùng token để đổi bảng màu mà không sửa từng quy tắc.
SKELETON = """


html, body, [class*="st-"], .stMarkdown, button, input, textarea, select { font-family: 'Plus Jakarta Sans', sans-serif; }
[data-testid="stIconMaterial"], .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; }
code, .t2v-mono, .t2v-k, .t2v-tag, .t2v-cnt { font-family: 'JetBrains Mono', monospace; }
::selection { background: var(--t2v-neon); color: var(--t2v-selection-fg); }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: rgb(var(--t2v-track-rgb) / .4); }
::-webkit-scrollbar-thumb { background: rgb(var(--t2v-a2-rgb) / .25); border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: rgb(var(--t2v-neon-rgb) / .4); }
.stApp { background-color: var(--t2v-bg); background-attachment: fixed;
  background-image: var(--t2v-bg-glow); }
header[data-testid="stHeader"] { background: transparent; height: 0; }
.block-container { padding-top: 1.1rem; padding-bottom: 3rem; max-width: 1400px; }
code { color: var(--t2v-a1-text); background: rgb(var(--t2v-ink-rgb) / .05); border: 1px solid rgb(var(--t2v-ink-rgb) / .1); border-radius: 4px;
       padding: 1px 5px; font-size: .92em; }

/* ---------- thanh bên */
[data-testid="stSidebar"] { background: rgb(var(--t2v-surface-rgb) / .92); border-right: 1px solid rgb(var(--t2v-ink-rgb) / .05); }
[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding-top: .2rem; }
[data-testid="stSidebarHeader"] { height: 1rem; min-height: 1rem; padding: 0; }
[data-testid="stSidebar"] [role="radiogroup"] { gap: 6px; }
[data-testid="stSidebar"] [role="radiogroup"] label { width: 100%; padding: 10px 14px 10px 20px; border-radius: 12px; margin: 0;
  border: 1px solid transparent; position: relative; transition: background .15s, border-color .15s; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) { display: none; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:hover { background: rgb(var(--t2v-ink-rgb) / .04); border-color: rgb(var(--t2v-ink-rgb) / .05); }
[data-testid="stSidebar"] label[data-testid="stRadioOption"] p { font-size: 14px; font-weight: 500; color: var(--t2v-text-2); }
[data-testid="stSidebar"] label[data-testid="stRadioOption"] [data-testid="stIconMaterial"] { color: var(--t2v-faint); font-size: 19px; margin-right: 6px; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] {
  background: var(--t2v-nav-active-bg);
  border-color: rgb(var(--t2v-a2-rgb) / .4); box-shadow: 0 10px 15px -3px rgb(var(--t2v-a2-600-rgb) / .10); }
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"]::before { content: ''; position: absolute;
  left: 7px; top: 50%; transform: translateY(-50%); width: 5px; height: 16px; border-radius: 9px; background: var(--t2v-neon);
  box-shadow: 0 0 8px var(--t2v-neon); }
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] p { color: var(--t2v-text-strong); font-weight: 600; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"][data-selected="true"] [data-testid="stIconMaterial"] { color: var(--t2v-a1); }
.t2v-brand { display: flex; gap: 14px; align-items: center; padding: 6px 0 18px; margin-bottom: 14px;
  border-bottom: 1px solid rgb(var(--t2v-ink-rgb) / .05); }
.t2v-logo { position: relative; width: 40px; height: 40px; border-radius: 12px; flex-shrink: 0; color: var(--t2v-logo-fg);
  background: var(--t2v-logo-bg); display: flex; align-items: center; justify-content: center;
  font: 800 13px 'JetBrains Mono', monospace; box-shadow: 0 10px 15px -3px rgb(var(--t2v-a2-rgb) / .2); outline: 1px solid rgb(var(--t2v-ink-rgb) / .2); }
.t2v-logo::after { content: ''; position: absolute; top: -4px; right: -4px; width: 10px; height: 10px; border-radius: 50%;
  background: var(--t2v-neon); box-shadow: 0 0 8px var(--t2v-neon); }
.t2v-brand b { display: block; font-size: 15px; color: var(--t2v-text-strong); letter-spacing: -.01em; }
.t2v-brand span { font-size: 12px; color: var(--t2v-text-2); font-weight: 500; }
.t2v-sec { font: 600 11px 'JetBrains Mono', monospace; color: var(--t2v-text-2); letter-spacing: .08em; text-transform: uppercase;
  margin: 4px 0 10px 4px; }
.t2v-arch { margin-top: 22px; padding: 14px; border-radius: 16px; background: rgb(var(--t2v-surface-2-rgb) / .8);
  border: 1px solid rgb(var(--t2v-ink-rgb) / .1); box-shadow: var(--t2v-shadow-sm); }
.t2v-arch .hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.t2v-arch .hd span:first-child { font: 700 10px 'JetBrains Mono', monospace; letter-spacing: .08em; text-transform: uppercase; color: var(--t2v-a1); }
.t2v-arch .on { display: flex; gap: 6px; align-items: center; font-size: 10px; font-weight: 600; color: var(--t2v-ok); }
.t2v-arch .off { color: var(--t2v-bad); }
.t2v-arch .it { padding: 9px 10px; border-radius: 12px; background: rgb(var(--t2v-bg-rgb) / .7); border: 1px solid rgb(var(--t2v-ink-rgb) / .05); margin-top: 8px; }
.t2v-arch .it div { display: flex; justify-content: space-between; align-items: center; }
.t2v-arch .it b { font: 500 11px 'JetBrains Mono', monospace; color: var(--t2v-text-em); }
.t2v-arch .it p { font-size: 11px; color: var(--t2v-text-2); margin: 3px 0 0; }

/* ---------- widget */
[data-testid="stWidgetLabel"] p { font: 600 12px 'JetBrains Mono', monospace; color: var(--t2v-text); }
[data-baseweb="textarea"], [data-baseweb="input"], [data-baseweb="select"] > div {
  background: rgb(var(--t2v-bg-rgb) / .8) !important; border-color: rgb(var(--t2v-ink-rgb) / .12) !important; border-radius: 12px !important; }
[data-baseweb="textarea"]:focus-within, [data-baseweb="input"]:focus-within { border-color: rgb(var(--t2v-a1-rgb) / .8) !important;
  box-shadow: 0 0 0 4px rgb(var(--t2v-a1-500-rgb) / .15); }
[data-testid="stTextArea"] textarea { background: transparent; color: var(--t2v-text-input); font-size: 14px; line-height: 1.7; }
[data-testid="stTextInput"] input { background: transparent; color: var(--t2v-text-input); font-size: 14px; font-weight: 500; }
[data-testid="stBaseButton-primary"] { background: var(--t2v-btn-primary-bg); color: var(--t2v-btn-primary-fg);
  border: 1px solid var(--t2v-btn-primary-bd); border-radius: 12px; font-weight: 700; box-shadow: var(--t2v-btn-primary-shadow); }
[data-testid="stBaseButton-primary"]:hover { color: var(--t2v-btn-primary-fg); border-color: var(--t2v-btn-primary-bd-hover); filter: brightness(1.1);
  box-shadow: var(--t2v-btn-primary-shadow-hover); }
[data-testid="stBaseButton-primary"]:disabled { opacity: .45; filter: none; box-shadow: none; }
[data-testid="stBaseButton-secondary"] { background: rgb(var(--t2v-ink-rgb) / .03); color: var(--t2v-text-2); border: 1px solid rgb(var(--t2v-ink-rgb) / .1);
  border-radius: 12px; }
[data-testid="stBaseButton-secondary"]:hover { background: rgb(var(--t2v-a1-500-rgb) / .08); color: var(--t2v-a1-text); border-color: rgb(var(--t2v-a1-rgb) / .5);
  box-shadow: 0 0 12px rgb(var(--t2v-neon-rgb) / .2); }
[data-testid="stBaseButton-pills"], [data-testid="stBaseButton-segmented_control"] { background: rgb(var(--t2v-ink-rgb) / .03);
  color: var(--t2v-text); border: 1px solid rgb(var(--t2v-ink-rgb) / .1); border-radius: 12px; font-size: 12px; }
[data-testid="stBaseButton-pills"]:hover, [data-testid="stBaseButton-segmented_control"]:hover { background: rgb(var(--t2v-ink-rgb) / .08);
  color: var(--t2v-text-strong); border-color: rgb(var(--t2v-ink-rgb) / .2); }
[data-testid="stBaseButton-pillsActive"], [data-testid="stBaseButton-segmented_controlActive"] {
  background: var(--t2v-seg-active-bg); color: var(--t2v-a1-text); font-weight: 600;
  border: 1px solid rgb(var(--t2v-a1-rgb) / .4); border-radius: 12px; font-size: 12px; box-shadow: 0 0 12px rgb(var(--t2v-neon-rgb) / .15); }
[data-testid="stExpander"] details { background: rgb(var(--t2v-surface-rgb) / .72); border: 1px solid rgb(var(--t2v-ink-rgb) / .1); border-radius: 16px; }
[data-testid="stExpander"] summary p { font-weight: 600; color: var(--t2v-text-em); }
[data-testid="stCaptionContainer"] { color: var(--t2v-text-2); }

/* ---------- thẻ: container có key bắt đầu bằng card_ hoặc news_ */
.stVerticalBlock[class*="st-key-card"] { background-color: rgb(var(--t2v-surface-rgb) / .72) !important; border: 1px solid rgb(var(--t2v-ink-rgb) / .1) !important;
  border-radius: 16px !important; padding: 22px 24px !important; box-shadow: var(--t2v-shadow-lg) !important;
  background-image: radial-gradient(circle at 100% 0%, rgb(var(--t2v-a2-rgb) / .10), transparent 40%) !important; }
.stVerticalBlock[class*="st-key-news_"] { background-color: rgb(var(--t2v-bg-rgb) / .6) !important; border: 1px solid rgb(var(--t2v-ink-rgb) / .05) !important;
  border-radius: 12px !important; padding: 14px 16px !important; transition: border-color .15s, background-color .15s; }
.stVerticalBlock[class*="st-key-news_"]:hover { border-color: rgb(var(--t2v-a1-500-rgb) / .3) !important; background-color: rgb(var(--t2v-bg-rgb) / .9) !important; }
.st-key-clf_grid [data-testid="stColumn"] > div, .st-key-clf_grid [data-testid="stColumn"] .stVerticalBlock:not([class*="st-key-mrow_"]) { height: 100%; }
.st-key-clf_grid [data-testid="stElementContainer"]:has(> [data-testid="stHtml"] > .t2v-card),
.st-key-clf_grid [data-testid="stHtml"]:has(> .t2v-card), .st-key-clf_grid .t2v-card { height: 100%; }
/* st.columns chỉ xếp chồng theo cửa sổ, không tính sidebar; cho thẻ tự xuống hàng khi vùng nội dung hẹp */
.st-key-clf_grid [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
.st-key-clf_grid [data-testid="stColumn"] { flex: 1 1 300px !important; min-width: min(100%, 300px) !important; }
.stVerticalBlock.st-key-card_models { gap: 0 !important; }
/* Nút trong suốt phủ cả dòng mô hình: giữ được bàn phím và trình đọc màn hình của nút thật, còn nhìn như một dòng */
.stVerticalBlock[class*="st-key-mrow_"] { position: relative; gap: 0 !important; }
.stVerticalBlock[class*="st-key-mrow_"] [data-testid="stElementContainer"]:has(.stButton) { position: absolute; inset: 0 0 10px 0; width: auto !important; height: auto; z-index: 2; }
.stVerticalBlock[class*="st-key-mrow_"] .stButton, .stVerticalBlock[class*="st-key-mrow_"] .stButton button { width: 100%; height: 100%; }
.stVerticalBlock[class*="st-key-mrow_"] .stButton button { background: transparent !important; border: 0 !important; box-shadow: none !important; border-radius: 12px; }
.stVerticalBlock[class*="st-key-mrow_"] .stButton button p { position: absolute; width: 1px; height: 1px; overflow: hidden; clip-path: inset(50%); white-space: nowrap; }
.stVerticalBlock[class*="st-key-mrow_"] .stButton button:focus-visible { outline: 2px solid var(--t2v-a1); outline-offset: 1px; }
.stVerticalBlock[class*="st-key-mrow_"] .stButton button:disabled { cursor: not-allowed; }
.stVerticalBlock[class*="st-key-mrow_"]:has(button:hover:not(:disabled)) .t2v-mrow:not(.hl) { background: rgb(var(--t2v-a1-500-rgb) / .08); border-color: rgb(var(--t2v-a1-rgb) / .5); }

/* ---------- khối HTML dùng chung */
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--t2v-a1); box-shadow: 0 0 8px var(--t2v-neon); flex-shrink: 0; }
.dot.sm { width: 6px; height: 6px; }
.dot.i { background: var(--t2v-a2); box-shadow: 0 0 8px var(--t2v-a2); }
.dot.g { background: var(--t2v-ok); box-shadow: 0 0 6px var(--t2v-ok); }
.dot.r { background: var(--t2v-bad); box-shadow: 0 0 6px var(--t2v-bad); }
.dot.off { background: var(--t2v-faint); box-shadow: none; }
.t2v-ic { font-family: 'Material Symbols Rounded'; font-size: 18px; line-height: 1; font-weight: 400; flex-shrink: 0;
  font-style: normal; letter-spacing: normal; text-transform: none; white-space: nowrap; -webkit-font-feature-settings: 'liga'; }
.t2v-top { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;
  padding: 4px 0 14px; margin-bottom: 4px; border-bottom: 1px solid rgb(var(--t2v-ink-rgb) / .05); }
.t2v-crumb { display: flex; gap: 8px; align-items: center; font: 12px 'JetBrains Mono', monospace; color: var(--t2v-text-2); }
.t2v-crumb .sep { color: var(--t2v-sep); }
.t2v-crumb b { display: flex; gap: 6px; align-items: center; color: var(--t2v-text-strong); font-weight: 600; }
.t2v-badges { display: flex; gap: 10px; flex-wrap: wrap; }
.t2v-badge { display: inline-flex; gap: 8px; align-items: center; padding: 6px 12px; border-radius: 12px; font-size: 12px;
  color: var(--t2v-text); background: rgb(var(--t2v-ink-rgb) / .03); border: 1px solid rgb(var(--t2v-ink-rgb) / .1); }
.t2v-badge .t2v-ic { font-size: 16px; color: var(--t2v-a1); }
.t2v-badge strong { color: var(--t2v-text-strong); font-family: 'JetBrains Mono', monospace; }
.t2v-badge em { font-style: normal; color: var(--t2v-a1); font: 600 12px 'JetBrains Mono', monospace; }
.t2v-badge .bar { color: rgb(var(--t2v-ink-rgb) / .2); }
.t2v-badge.model { color: var(--t2v-a2-text); background: rgb(var(--t2v-a2-rgb) / .1); border-color: rgb(var(--t2v-a2-rgb) / .3);
  box-shadow: 0 0 25px -4px rgb(var(--t2v-a2-rgb) / .35); font-family: 'JetBrains Mono', monospace; }
.t2v-head { margin: 16px 0 14px; }
.t2v-h1 { display: flex; gap: 10px; align-items: center; font-size: 24px; font-weight: 800; color: var(--t2v-text-strong); letter-spacing: -.02em; margin: 0; }
.t2v-h1 .dot { width: 10px; height: 10px; }
.t2v-sub { font: 12px 'JetBrains Mono', monospace; color: var(--t2v-text-2); margin-top: 4px; }
.t2v-banner { display: flex; gap: 14px; align-items: flex-start; padding: 14px 18px; margin-bottom: 18px; border-radius: 16px;
  background: rgb(var(--t2v-note-500-rgb) / .04); border: 1px solid rgb(var(--t2v-note-500-rgb) / .22);
  background-image: radial-gradient(circle at 0% 0%, rgb(var(--t2v-note-500-rgb) / .10), transparent 30%); }
.t2v-banner .ib { padding: 7px; border-radius: 12px; color: var(--t2v-note-fg); background: rgb(var(--t2v-note-500-rgb) / .1); border: 1px solid rgb(var(--t2v-note-500-rgb) / .2); display: flex; }
.t2v-banner .ib .t2v-ic { font-size: 20px; }
.t2v-banner div:last-child { font-size: 13px; line-height: 1.65; color: rgb(var(--t2v-note-soft-rgb) / .9); font-weight: 300; }
.t2v-banner strong { font-weight: 600; color: var(--t2v-note-text); font-family: 'JetBrains Mono', monospace; margin-right: 6px; }
.t2v-banner b { color: var(--t2v-text-strong); font-weight: 600; }
.t2v-card { position: relative; overflow: hidden; background: rgb(var(--t2v-surface-rgb) / .72); border: 1px solid rgb(var(--t2v-ink-rgb) / .1);
  border-radius: 16px; padding: 22px 24px; box-shadow: var(--t2v-shadow-lg);
  background-image: radial-gradient(circle at 100% 0%, rgb(var(--t2v-a1-500-rgb) / .08), transparent 35%); }
.t2v-card.flat { padding: 0; }
.t2v-ch { display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap;
  padding-bottom: 14px; margin-bottom: 14px; border-bottom: 1px solid rgb(var(--t2v-ink-rgb) / .05); }
.t2v-ch.nb { border-bottom: 0; padding-bottom: 0; }
.t2v-ch h2, .t2v-ch h3 { display: flex; gap: 10px; align-items: center; margin: 0; padding: 0; color: var(--t2v-text-strong); font-weight: 700; letter-spacing: -.01em; }
.t2v-ch h2 { font-size: 17px; } .t2v-ch h3 { font-size: 14px; }
.t2v-ch p { font-size: 12px; color: var(--t2v-text-2); margin: 4px 0 0; }
.t2v-ch p b { color: var(--t2v-a1-text); }
.t2v-k { display: flex; gap: 6px; align-items: center; font-size: 10px; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase; color: var(--t2v-text-2); }
.t2v-k.cy { color: var(--t2v-a1); text-transform: none; letter-spacing: 0; }
.t2v-tag { font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 6px; color: var(--t2v-a1-text);
  background: rgb(var(--t2v-ink-rgb) / .04); border: 1px solid rgb(var(--t2v-ink-rgb) / .1); white-space: nowrap; }
.t2v-tag.i { color: var(--t2v-a2-text); background: rgb(var(--t2v-a2-deep-rgb) / .4); border-color: rgb(var(--t2v-a2-rgb) / .2); }
.t2v-tag.g { color: var(--t2v-ok-text); background: rgb(var(--t2v-ok-500-rgb) / .15); border-color: rgb(var(--t2v-ok-500-rgb) / .3); }
.t2v-cnts { display: flex; gap: 8px; }
.t2v-cnt { font-size: 12px; color: var(--t2v-text-2); padding: 4px 10px; border-radius: 8px; background: rgb(var(--t2v-ink-rgb) / .03); border: 1px solid rgb(var(--t2v-ink-rgb) / .1); }
.t2v-foot { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; font-size: 12px; color: var(--t2v-text-2); min-height: 40px; }
.t2v-foot b { color: var(--t2v-text-em); }
.t2v-grid3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.t2v-grid4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; margin-bottom: 18px; }
.t2v-grid5 { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 14px; }
.t2v-split { display: grid; grid-template-columns: 3fr 2fr; gap: 20px; }
@media (max-width: 1150px) { .t2v-grid3, .t2v-grid4, .t2v-grid5, .t2v-split { grid-template-columns: 1fr 1fr; } }
@media (max-width: 760px) { .t2v-grid3, .t2v-grid4, .t2v-grid5, .t2v-split { grid-template-columns: 1fr; } }
.t2v-res { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; margin: 22px 0 14px; }
.t2v-res h3 { display: flex; gap: 8px; align-items: center; font-size: 16px; font-weight: 700; color: var(--t2v-text-strong); margin: 0; padding: 0; }
.t2v-res .t2v-mono { font-size: 12px; color: var(--t2v-text-2); }
.t2v-res .t2v-mono b { color: var(--t2v-a1-text); }
.t2v-done { display: inline-flex; gap: 6px; align-items: center; padding: 2px 10px; border-radius: 999px; font: 700 10px 'JetBrains Mono', monospace;
  color: var(--t2v-ok-text); background: rgb(var(--t2v-ok-500-rgb) / .15); border: 1px solid rgb(var(--t2v-ok-500-rgb) / .3); }
.t2v-bar { height: 8px; border-radius: 999px; background: var(--t2v-bg); border: 1px solid rgb(var(--t2v-ink-rgb) / .05); overflow: hidden; }
.t2v-bar.big { height: 12px; padding: 2px; border-color: rgb(var(--t2v-ink-rgb) / .1); }
.t2v-bar.thin { height: 6px; }
.t2v-bar i { display: block; height: 100%; border-radius: 999px; background: var(--t2v-bar-fill);
  box-shadow: 0 0 8px var(--t2v-neon); }
.t2v-bar i.lo { background: var(--t2v-sep); box-shadow: none; }
.t2v-bar i.mid { background: rgb(var(--t2v-a1-500-rgb) / .8); box-shadow: none; }
.t2v-main { display: flex; gap: 16px; align-items: flex-start; }
.t2v-emo { width: 56px; height: 56px; border-radius: 16px; flex-shrink: 0; display: flex; align-items: center; justify-content: center;
  font-size: 26px; background: var(--t2v-emo-bg); border: 1px solid rgb(var(--t2v-ink-rgb) / .2);
  box-shadow: 0 10px 15px -3px rgb(var(--t2v-a2-600-rgb) / .3); }
.t2v-big { font-size: 24px; font-weight: 800; color: var(--t2v-text-strong); letter-spacing: -.02em; line-height: 1.2; }
.t2v-mono { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: var(--t2v-text-2); }
.t2v-mono b { color: var(--t2v-a1-text); }
.t2v-lbl { display: flex; justify-content: space-between; align-items: baseline; font: 12px 'JetBrains Mono', monospace;
  color: var(--t2v-text-2); margin: 22px 0 8px; }
.t2v-lbl b { color: var(--t2v-a1-text); font-size: 14px; }
.t2v-sep { border-top: 1px solid rgb(var(--t2v-ink-rgb) / .05); margin: 20px 0 12px; }
.t2v-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.t2v-chip { font: 500 12px 'JetBrains Mono', monospace; padding: 4px 10px; border-radius: 8px; color: var(--t2v-text);
  background: rgb(var(--t2v-ink-rgb) / .04); border: 1px solid rgb(var(--t2v-ink-rgb) / .1); }
.t2v-chip.hi { color: var(--t2v-a1-text); background: rgb(var(--t2v-a1-deep-rgb) / .4); border-color: rgb(var(--t2v-a1-500-rgb) / .3); box-shadow: 0 0 8px rgb(var(--t2v-neon-rgb) / .1); }
.t2v-chip.fi { font-size: 11px; color: var(--t2v-a1-text); background: rgb(var(--t2v-surface-2-rgb) / .9); border-color: rgb(var(--t2v-a1-500-rgb) / .3); }
.t2v-mrow { padding: 11px 12px; border-radius: 12px; background: rgb(var(--t2v-bg-rgb) / .6); border: 1px solid rgb(var(--t2v-ink-rgb) / .05); margin-bottom: 10px; }
.t2v-mrow.hl { background: rgb(var(--t2v-a2-deep-rgb) / .3); border-color: rgb(var(--t2v-a2-rgb) / .3); }
.t2v-mrow .hd { display: flex; justify-content: space-between; align-items: center; gap: 8px; font-size: 12px; margin-bottom: 7px; }
.t2v-mrow .nm { display: flex; gap: 7px; align-items: center; color: var(--t2v-text); font-weight: 500; }
.t2v-mrow.hl .nm { color: var(--t2v-text-strong); font-weight: 700; }
.t2v-mrow .pv { font-family: 'JetBrains Mono', monospace; color: var(--t2v-text); white-space: nowrap; }
.t2v-mrow .pv b { color: var(--t2v-text-strong); }
.t2v-mrow.hl .pv b { color: var(--t2v-a1-text); }
.t2v-mrow .ds { font-size: 11px; color: var(--t2v-text-2); margin-top: 6px; }
.t2v-mrow.hl .ds { color: rgb(var(--t2v-a2-text-rgb) / .85); }
.t2v-dist { margin-bottom: 13px; }
.t2v-dist .hd { display: flex; justify-content: space-between; font-size: 12px; font-weight: 500; color: var(--t2v-text); margin-bottom: 5px; }
.t2v-dist .hd b { font-family: 'JetBrains Mono', monospace; color: var(--t2v-text-2); font-weight: 500; }
.t2v-dist.top .hd span { color: var(--t2v-text-strong); font-weight: 600; } .t2v-dist.top .hd b { color: var(--t2v-a1-text); font-weight: 700; }
.t2v-cfoot { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding-top: 12px; margin-top: 16px;
  border-top: 1px solid rgb(var(--t2v-ink-rgb) / .05); font: 11px 'JetBrains Mono', monospace; color: var(--t2v-text-2); }
.t2v-cfoot b { color: var(--t2v-text-strong); }
.t2v-text { max-height: 280px; overflow: auto; line-height: 1.75; font-size: 13px; color: var(--t2v-text); padding: 14px;
  border-radius: 12px; background: rgb(var(--t2v-bg-rgb) / .8); border: 1px solid rgb(var(--t2v-ink-rgb) / .1); box-shadow: var(--t2v-shadow-inset); }
mark { background: rgb(var(--t2v-mark-rgb) / .25); color: var(--t2v-mark-fg); padding: 0 3px; border-radius: 4px; font-weight: 600; border: 1px solid rgb(var(--t2v-mark-rgb) / .4); }
.t2v-cap { font: 600 11px 'JetBrains Mono', monospace; color: var(--t2v-text-2); margin: 0 0 8px; }
.t2v-cat { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 8px; font-size: 11px; font-weight: 500;
  white-space: nowrap; border: 1px solid; }
.t2v-cat.cyan { color: var(--t2v-cat-cyan-fg); background: var(--t2v-cat-cyan-bg); border-color: var(--t2v-cat-cyan-bd); }
.t2v-cat.sky { color: var(--t2v-cat-sky-fg); background: var(--t2v-cat-sky-bg); border-color: var(--t2v-cat-sky-bd); }
.t2v-cat.violet { color: var(--t2v-cat-violet-fg); background: var(--t2v-cat-violet-bg); border-color: var(--t2v-cat-violet-bd); }
.t2v-cat.amber { color: var(--t2v-cat-amber-fg); background: var(--t2v-cat-amber-bg); border-color: var(--t2v-cat-amber-bd); }
.t2v-cat.rose { color: var(--t2v-cat-rose-fg); background: var(--t2v-cat-rose-bg); border-color: var(--t2v-cat-rose-bd); }
.t2v-cat.emerald { color: var(--t2v-cat-emerald-fg); background: var(--t2v-cat-emerald-bg); border-color: var(--t2v-cat-emerald-bd); }
.t2v-cat.indigo { color: var(--t2v-cat-indigo-fg); background: var(--t2v-cat-indigo-bg); border-color: var(--t2v-cat-indigo-bd); }
.t2v-cat.lime { color: var(--t2v-cat-lime-fg); background: var(--t2v-cat-lime-bg); border-color: var(--t2v-cat-lime-bd); }
.t2v-cat.pink { color: var(--t2v-cat-pink-fg); background: var(--t2v-cat-pink-bg); border-color: var(--t2v-cat-pink-bd); }
.t2v-cat.blue { color: var(--t2v-cat-blue-fg); background: var(--t2v-cat-blue-bg); border-color: var(--t2v-cat-blue-bd); }
.t2v-cat.gray { color: var(--t2v-cat-gray-fg); background: var(--t2v-cat-gray-bg); border-color: var(--t2v-cat-gray-bd); }
.t2v-stat { display: flex; gap: 16px; align-items: center; padding: 18px 20px; border-radius: 16px; background: rgb(var(--t2v-surface-rgb) / .72);
  border: 1px solid rgb(var(--t2v-ink-rgb) / .1); box-shadow: var(--t2v-shadow-md); }
.t2v-stat .ib { width: 46px; height: 46px; border-radius: 12px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; border: 1px solid; }
.t2v-stat .ib .t2v-ic { font-size: 22px; }
.t2v-stat .ib.cyan { color: var(--t2v-a1); background: rgb(var(--t2v-a1-deep-rgb) / .4); border-color: rgb(var(--t2v-a1-500-rgb) / .3); box-shadow: 0 0 12px rgb(var(--t2v-neon-rgb) / .15); }
.t2v-stat .ib.amber { color: var(--t2v-score-fg); background: rgb(var(--t2v-score-deep-rgb) / .4); border-color: rgb(var(--t2v-score-500-rgb) / .3); box-shadow: 0 0 12px rgb(var(--t2v-score-500-rgb) / .15); }
.t2v-stat .ib.emerald { color: var(--t2v-ok); background: rgb(var(--t2v-ok-deep-rgb) / .4); border-color: rgb(var(--t2v-ok-500-rgb) / .3); box-shadow: 0 0 12px rgb(var(--t2v-ok-rgb) / .15); }
.t2v-stat .ib.indigo { color: var(--t2v-a2-text); background: rgb(var(--t2v-a2-deep-rgb) / .4); border-color: rgb(var(--t2v-a2-rgb) / .3); box-shadow: 0 0 12px rgb(var(--t2v-a2-rgb) / .2); }
.t2v-stat .lb { font-size: 12px; color: var(--t2v-text-2); font-weight: 500; }
.t2v-stat .vl { font: 800 22px 'JetBrains Mono', monospace; color: var(--t2v-text-strong); letter-spacing: -.02em; margin-top: 2px; white-space: nowrap; }
.t2v-stat .vl.amber { color: var(--t2v-score-text); } .t2v-stat .vl.cyan { color: var(--t2v-a1-text); }
.t2v-stat .sb { font-size: 11px; color: var(--t2v-text-2); margin-top: 2px; }
.t2v-kpi { padding: 16px; border-radius: 12px; background: rgb(var(--t2v-bg-rgb) / .7); border: 1px solid rgb(var(--t2v-ink-rgb) / .05); }
.t2v-kpi .lb { font: 12px 'JetBrains Mono', monospace; color: var(--t2v-text-2); }
.t2v-kpi .vl { font: 800 24px 'JetBrains Mono', monospace; color: var(--t2v-text-strong); letter-spacing: -.02em; margin-top: 8px; white-space: nowrap; }
.t2v-kpi .vl.cyan { color: var(--t2v-a1); } .t2v-kpi .vl.sm { font-size: 19px; } .t2v-kpi .vl small { color: var(--t2v-sep); font-weight: 300; }
.t2v-kpi .sb { font-size: 11px; color: var(--t2v-text-2); margin-top: 4px; }
.t2v-err { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.t2v-err > div { padding: 16px 18px; border-radius: 12px; background: rgb(var(--t2v-bg-rgb) / .7); border: 1px solid rgb(var(--t2v-ink-rgb) / .05); }
.t2v-err h4 { margin: 0 0 4px; font-size: 14px; font-weight: 600; color: var(--t2v-text-strong); }
.t2v-err h4 span { font: 600 11px 'JetBrains Mono', monospace; color: var(--t2v-a1-text); margin-right: 6px; }
.t2v-err .big { font: 800 26px 'JetBrains Mono', monospace; color: var(--t2v-a1); margin: 6px 0 2px; letter-spacing: -.02em; }
.t2v-err p { font-size: 12px; color: var(--t2v-text-2); margin: 0 0 12px; line-height: 1.55; }
.t2v-err p b { color: var(--t2v-text-em); }
.t2v-concl { margin-top: 16px; padding: 14px 18px; border-radius: 12px; border: 1px solid rgb(var(--t2v-a1-500-rgb) / .25);
  background: rgb(var(--t2v-a1-500-rgb) / .06); font-size: 13px; line-height: 1.6; color: var(--t2v-text); }
@media (max-width: 900px) { .t2v-err { grid-template-columns: 1fr; } }
.t2v-tw { overflow-x: auto; border-radius: 12px; border: 1px solid rgb(var(--t2v-ink-rgb) / .05); background: rgb(var(--t2v-bg-rgb) / .6); }
.t2v-table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: left; }
.t2v-table th { padding: 11px 14px; font: 600 10px 'JetBrains Mono', monospace; letter-spacing: .08em; text-transform: uppercase;
  color: var(--t2v-text-2); background: rgb(var(--t2v-ink-rgb) / .02); border-bottom: 1px solid rgb(var(--t2v-ink-rgb) / .1); }
.t2v-table td { padding: 11px 14px; color: var(--t2v-text); border-bottom: 1px solid rgb(var(--t2v-ink-rgb) / .05); vertical-align: top; }
.t2v-table tr:last-child td { border-bottom: 0; }
.t2v-table tbody tr:hover { background: rgb(var(--t2v-ink-rgb) / .03); }
.t2v-table .c { text-align: center; } .t2v-table .r { text-align: right; }
.t2v-table .n { font-family: 'JetBrains Mono', monospace; }
.t2v-table .best { color: var(--t2v-text-strong); font-weight: 700; }
.t2v-table tr.hl { background: rgb(var(--t2v-a2-deep-rgb) / .4); box-shadow: inset 0 0 15px rgb(var(--t2v-neon-rgb) / .08); }
.t2v-table tr.hl td { color: var(--t2v-a1-text); font-weight: 600; border-top: 2px solid rgb(var(--t2v-a1-500-rgb) / .4); }
.t2v-table tr.hl td:first-child { color: var(--t2v-text-strong); }
.t2v-table tr td:first-child { border-left: 4px solid transparent; }
.t2v-table tr.sel { background: rgb(var(--t2v-a2-deep-rgb) / .3); }
.t2v-table tr.sel td:first-child { border-left-color: var(--t2v-a1); color: var(--t2v-a1-text); font-weight: 700; }
.t2v-table tr.sel .tt { color: var(--t2v-a1-text); font-weight: 700; }
.t2v-table .tt { color: var(--t2v-text-em); font-weight: 600; line-height: 1.4; }
.t2v-table .sn { font-size: 11px; color: var(--t2v-text-2); margin-top: 2px; }
.t2v-table .fl { font: 11px 'JetBrains Mono', monospace; color: var(--t2v-text-2); margin-top: 2px; }
.t2v-table .fl.path { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 0; min-width: 100%; } /* width: 0 tránh làm tăng min-content của cột */
.t2v-table .sc { font: 700 12px 'JetBrains Mono', monospace; color: var(--t2v-text-em); }
.t2v-table tr.sel .sc { color: var(--t2v-a1-text); }
.t2v-tfoot { display: flex; justify-content: space-between; padding: 11px 18px; font: 500 11px 'JetBrains Mono', monospace;
  color: var(--t2v-text-2); background: rgb(var(--t2v-bg-rgb) / .8); border-top: 1px solid rgb(var(--t2v-ink-rgb) / .1); }
.t2v-tfoot span:last-child { color: var(--t2v-a1); }
.t2v-sc3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 14px 0; }
.t2v-sc3 div { padding: 10px; border-radius: 12px; text-align: center; background: rgb(var(--t2v-bg-rgb) / .7); border: 1px solid rgb(var(--t2v-ink-rgb) / .1); }
.t2v-sc3 div.on { background: rgb(var(--t2v-a2-deep-rgb) / .4); border-color: rgb(var(--t2v-a1-rgb) / .4); box-shadow: 0 0 12px rgb(var(--t2v-neon-rgb) / .1); }
.t2v-sc3 span { display: block; font: 500 10px 'JetBrains Mono', monospace; color: var(--t2v-text-2); text-transform: uppercase; letter-spacing: .05em; }
.t2v-sc3 b { display: block; font: 700 14px 'JetBrains Mono', monospace; color: var(--t2v-text-em); margin: 2px 0; }
.t2v-sc3 small { font: 11px 'JetBrains Mono', monospace; color: var(--t2v-text-2); }
.t2v-sc3 .on span, .t2v-sc3 .on b, .t2v-sc3 .on small { color: var(--t2v-a1-text); }
.t2v-meta { border-top: 1px solid rgb(var(--t2v-ink-rgb) / .05); padding-top: 12px; font: 12px 'JetBrains Mono', monospace; color: var(--t2v-text-2); }
.t2v-meta div { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 7px; }
.t2v-meta span:first-child { white-space: nowrap; }
.t2v-meta span:last-child { color: var(--t2v-text); text-align: right; }
.t2v-meta .file { color: var(--t2v-a1-text); font-size: 11px; padding: 1px 8px; border-radius: 8px; background: rgb(var(--t2v-ink-rgb) / .04); border: 1px solid rgb(var(--t2v-ink-rgb) / .1); }
.t2v-art { font-size: 16px; font-weight: 700; color: var(--t2v-text-strong); line-height: 1.4; margin: 12px 0; }
.t2v-note { font: italic 12px 'JetBrains Mono', monospace; color: var(--t2v-text-2); }
.t2v-src { padding: 18px 20px; border-radius: 16px; background: rgb(var(--t2v-surface-rgb) / .8); border: 1px solid rgb(var(--t2v-ink-rgb) / .1);
  box-shadow: var(--t2v-shadow-lg); background-image: radial-gradient(circle at 100% 0%, rgb(var(--t2v-a1-500-rgb) / .10), transparent 35%); }
.t2v-src .hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.t2v-src h3 { font-size: 16px; font-weight: 700; color: var(--t2v-text-strong); margin: 0; padding: 0; }
.t2v-src .url { font: 12px 'JetBrains Mono', monospace; color: var(--t2v-text-2); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 14px; }
.t2v-st { display: inline-flex; gap: 6px; align-items: center; padding: 2px 10px; border-radius: 999px; font: 600 11px 'JetBrains Mono', monospace; border: 1px solid; }
.t2v-st.ok { color: var(--t2v-ok-text); background: rgb(var(--t2v-ok-500-rgb) / .15); border-color: rgb(var(--t2v-ok-500-rgb) / .3); }
.t2v-st.bad { color: var(--t2v-bad-text); background: rgb(var(--t2v-bad-500-rgb) / .15); border-color: rgb(var(--t2v-bad-500-rgb) / .3); max-width: 60%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.t2v-mini { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; padding-top: 12px; border-top: 1px solid rgb(var(--t2v-ink-rgb) / .05); text-align: center; }
.t2v-mini div { padding: 9px; border-radius: 12px; background: rgb(var(--t2v-bg-rgb) / .7); border: 1px solid rgb(var(--t2v-ink-rgb) / .05); }
.t2v-mini span { display: block; font: 11px 'JetBrains Mono', monospace; color: var(--t2v-text-2); }
.t2v-mini b { display: block; font: 700 17px 'JetBrains Mono', monospace; color: var(--t2v-text-strong); margin-top: 2px; }
.t2v-mini b.cy { color: var(--t2v-a1-text); } .t2v-mini b.gr { color: var(--t2v-ok); } .t2v-mini small { font-size: 11px; font-weight: 400; color: var(--t2v-text-2); }
.t2v-nmeta { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; font: 12px 'JetBrains Mono', monospace; color: var(--t2v-text-2); margin-bottom: 5px; }
.t2v-nmeta b { color: var(--t2v-a1-text); font-weight: 600; } .t2v-nmeta .sep { color: var(--t2v-sep); }
.t2v-ntitle a { font-size: 14px; font-weight: 600; color: var(--t2v-text-strong); text-decoration: none; line-height: 1.4; }
.t2v-ntitle a:hover { color: var(--t2v-a1-text); }
.t2v-nsum { font-size: 12px; color: var(--t2v-text-2); font-weight: 300; margin-top: 4px; line-height: 1.55;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

"""

# Ghi đè riêng cho giao diện sáng. Bộ chọn L1–L15, S1, S2 chưa xác minh trên DOM thật vì frontend đóng gói minified; tester cần kiểm tra, nhất là DOM progress/alert/listbox.
LIGHT_CSS = """
.stApp, [data-testid="stMarkdownContainer"], [data-testid="stSidebar"] { color: var(--t2v-text); }
[data-testid="stTextArea"] textarea::placeholder, [data-testid="stTextInput"] input::placeholder { color: var(--t2v-text-2); opacity: 1; }
[data-baseweb="select"] > div, [data-baseweb="select"] input { color: var(--t2v-text-input); }
[data-baseweb="select"] svg { color: var(--t2v-text-2); fill: currentColor; }
/* :has() giới hạn khung listbox để tooltip help không bị sáng. */
[data-baseweb="popover"]:has(ul[role="listbox"]) > div, ul[role="listbox"] { background: rgb(var(--t2v-surface-rgb) / 1); border: 1px solid rgb(var(--t2v-ink-rgb) / .1); box-shadow: var(--t2v-shadow-sm); }
ul[role="listbox"] li[role="option"] { color: var(--t2v-text); }
ul[role="listbox"] li[role="option"]:hover, ul[role="listbox"] li[role="option"][aria-selected="true"]:not([data-selected="true"]) { background: rgb(var(--t2v-ink-rgb) / .05); }
ul[role="listbox"] li[role="option"][aria-selected="true"] { background: rgb(var(--t2v-a1-deep-rgb) / .6); color: var(--t2v-a1-text); }
[data-testid="stExpander"] summary svg, [data-testid="stExpander"] summary [data-testid="stIconMaterial"] { color: var(--t2v-text-2); }
[data-testid="stSpinner"], [data-testid="stSpinner"] p { color: var(--t2v-text); }
[data-testid="stProgress"] p { color: var(--t2v-text); }
/* Chưa xác minh DOM của thanh rãnh progress trên Streamlit hiện hành. */
[data-testid="stProgress"] > div > div { background: rgb(var(--t2v-ink-rgb) / .08); }
[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) { background: rgb(var(--t2v-note-500-rgb) / .08); border-color: rgb(var(--t2v-note-500-rgb) / .3); color: var(--t2v-note-text); }
[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) [data-testid="stAlertContentInfo"], [data-testid="stAlert"]:has([data-testid="stAlertContentInfo"]) svg { color: var(--t2v-note-fg); }
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) { background: rgb(var(--t2v-warn-500-rgb) / .10); border-color: rgb(var(--t2v-warn-500-rgb) / .3); color: var(--t2v-warn-text); }
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) svg { color: var(--t2v-warn); }
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"], [data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] { color: var(--t2v-text-2); }
"""

# Hai điểm Streamlit/BaseWeb vẫn lấy màu cyan từ config nếu không được đồng bộ với bảng.
SHARED_B2 = """
[data-testid="stProgress"] [role="progressbar"] > div { background: var(--t2v-a1); }
[data-baseweb="select"] > div:focus-within { border-color: var(--t2v-a1) !important; }
"""

def _root(palette):
    """Sinh biến CSS; giữ alpha qua kênh RGB riêng và bỏ heat/light chỉ dùng ở Python."""
    entries = []
    for key, value in palette.items():
        if key.startswith("heat") or key == "light":
            continue
        entries.append("--t2v-" + key + ":" + str(value) + ";")
        if key in RGB_KEYS:
            if not isinstance(value, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
                raise ValueError("RGB token '%s' phải có giá trị hex 6 ký tự" % key)
            rgb = " ".join(str(int(value[i:i+2], 16)) for i in (1, 3, 5))
            entries.append("--t2v-" + key + "-rgb:" + rgb + ";")
    return ":root{" + "".join(entries) + "}"

def css(name):
    """Ghép CSS bằng nối chuỗi để dấu ngoặc CSS được giữ nguyên và font nạp trước quy tắc."""
    palette = _palette(name)
    light_css = LIGHT_CSS if palette.get("light") is True else ""
    return "<style>" + FONTS_IMPORT + _root(palette) + SKELETON + SHARED_B2 + light_css + "</style>"


def _palette(name):
    return PALETTES.get(name, PALETTES[DEFAULT])

def chart(c, name):
    """Áp cấu hình Altair đồng bộ với chữ và lưới của bảng màu."""
    palette = _palette(name)
    return (c.configure(background="transparent", font="Plus Jakarta Sans")
            .configure_axis(
                labelColor=palette["text-2"], titleColor=palette["text-2"],
                domainColor=palette["grid"], tickColor=palette["grid"],
                gridColor=palette["grid"], labelFont="JetBrains Mono",
                titleFont="JetBrains Mono",
            )
            .configure_legend(labelColor=palette["text-2"], titleColor=palette["text-2"], labelFont="JetBrains Mono")
            .configure_view(stroke=None))


def heat(name):
    """Trả màu heatmap từ palette để dải và chữ theo bảng màu; các giá trị chỉ dùng trong Python."""
    palette = _palette(name)
    return {"range": palette["heat"], "stroke": palette["heat-stroke"], "text_hi": palette["heat-text-hi"], "text_lo": palette["heat-text-lo"]}

# Bảo vệ thứ tự menu và tính tương thích của token giữa các bảng.
assert list(PALETTES) == ["Tối cyan", "Tối xanh lục", "Tối cam", "Sáng"]
assert all(set(palette) == set(DARK_CYAN) for palette in PALETTES.values())
