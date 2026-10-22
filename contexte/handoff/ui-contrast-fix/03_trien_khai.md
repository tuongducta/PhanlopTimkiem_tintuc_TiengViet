# 03_trien_khai · ui-contrast-fix

**Agent:** developer (điều khiển Codex CLI) · **Ngày:** 22/10/2026 · **Vòng:** 1

## Đầu vào
- File đã đọc: `02_dac_ta.md` (13 AC), `00_dau_vao.md`. Không có `01_kien_truc.md`.
- Phạm vi được duyệt: chỉ sửa `src/system/app/streamlit_app.py`, đúng 3 lỗi trong đặc tả.
- Do file đã có thay đổi chưa commit từ trước, phần Codex sửa được tách bằng `diff -u logs/streamlit_app.before.py src/system/app/streamlit_app.py`.

## Quyết định / Nội dung chính
- Lỗi 1: điểm đầu gradient nút chính `#06B6D4` -> `#0E7490`. Hover giữ `brightness(1.1)` vì Codex đo trắng/`#0F809E` = 4,56:1 (số Codex tự báo, tester cần đo lại).
- Lỗi 2: 4 selector `.t2v-sec`, `.t2v-cfoot`, `.t2v-table .fl`, `.t2v-sc3 small` đổi sang `#94A3B8`, cỡ 11px. Còn `#64748B` ở dòng 75 (icon) và 148 (`.dot.off`), đúng theo đặc tả.
- Lỗi 3: thêm `txt = lambda x: x if isinstance(x, str) else ""`, dùng ở hiển thị `.t2v-nsum` và `clf.predict`. Grep `summary or` = 0.

## Diff (chỉ phần Codex sửa)
```diff
--- contexte/handoff/ui-contrast-fix/logs/streamlit_app.before.py	2026-10-22 16:42:38
+++ src/system/app/streamlit_app.py	2026-10-22 16:43:48
@@ -90,7 +90,7 @@
   background: #00F2FE; box-shadow: 0 0 8px #00F2FE; }
 .t2v-brand b { display: block; font-size: 15px; color: #fff; letter-spacing: -.01em; }
 .t2v-brand span { font-size: 12px; color: #94A3B8; font-weight: 500; }
-.t2v-sec { font: 600 10px 'JetBrains Mono', monospace; color: #64748B; letter-spacing: .08em; text-transform: uppercase;
+.t2v-sec { font: 600 11px 'JetBrains Mono', monospace; color: #94A3B8; letter-spacing: .08em; text-transform: uppercase;
   margin: 4px 0 10px 4px; }
 .t2v-arch { margin-top: 22px; padding: 14px; border-radius: 16px; background: rgba(17,22,34,.8);
   border: 1px solid rgba(255,255,255,.1); box-shadow: 0 10px 15px -3px rgba(0,0,0,.4); }
@@ -111,7 +111,7 @@
   box-shadow: 0 0 0 4px rgba(6,182,212,.15); }
 [data-testid="stTextArea"] textarea { background: transparent; color: #F1F5F9; font-size: 14px; line-height: 1.7; }
 [data-testid="stTextInput"] input { background: transparent; color: #F1F5F9; font-size: 14px; font-weight: 500; }
-[data-testid="stBaseButton-primary"] { background: linear-gradient(90deg, #06B6D4, #4F46E5 60%, #4338CA); color: #fff;
+[data-testid="stBaseButton-primary"] { background: linear-gradient(90deg, #0E7490, #4F46E5 60%, #4338CA); color: #fff;
   border: 1px solid rgba(255,255,255,.2); border-radius: 12px; font-weight: 700; box-shadow: 0 10px 15px -3px rgba(6,182,212,.2); }
 [data-testid="stBaseButton-primary"]:hover { color: #fff; border-color: rgba(255,255,255,.35); filter: brightness(1.1);
   box-shadow: 0 10px 20px -3px rgba(6,182,212,.4); }
@@ -246,7 +246,7 @@
 .t2v-dist .hd b { font-family: 'JetBrains Mono', monospace; color: #94A3B8; font-weight: 500; }
 .t2v-dist.top .hd span { color: #fff; font-weight: 600; } .t2v-dist.top .hd b { color: #67E8F9; font-weight: 700; }
 .t2v-cfoot { display: flex; justify-content: space-between; align-items: center; gap: 8px; padding-top: 12px; margin-top: 16px;
-  border-top: 1px solid rgba(255,255,255,.05); font: 11px 'JetBrains Mono', monospace; color: #64748B; }
+  border-top: 1px solid rgba(255,255,255,.05); font: 11px 'JetBrains Mono', monospace; color: #94A3B8; }
 .t2v-cfoot b { color: #fff; }
 .t2v-text { max-height: 280px; overflow: auto; line-height: 1.75; font-size: 13px; color: #CBD5E1; padding: 14px;
   border-radius: 12px; background: rgba(7,9,14,.8); border: 1px solid rgba(255,255,255,.1); box-shadow: inset 0 2px 4px rgba(0,0,0,.3); }
@@ -301,7 +301,7 @@
 .t2v-table tr.sel .tt { color: #67E8F9; font-weight: 700; }
 .t2v-table .tt { color: #E2E8F0; font-weight: 600; line-height: 1.4; }
 .t2v-table .sn { font-size: 11px; color: #94A3B8; margin-top: 2px; }
-.t2v-table .fl { font: 10px 'JetBrains Mono', monospace; color: #64748B; margin-top: 2px; }
+.t2v-table .fl { font: 11px 'JetBrains Mono', monospace; color: #94A3B8; margin-top: 2px; }
 .t2v-table .sc { font: 700 12px 'JetBrains Mono', monospace; color: #E2E8F0; }
 .t2v-table tr.sel .sc { color: #67E8F9; }
 .t2v-tfoot { display: flex; justify-content: space-between; padding: 11px 18px; font: 500 11px 'JetBrains Mono', monospace;
@@ -312,7 +312,7 @@
 .t2v-sc3 div.on { background: rgba(30,27,75,.4); border-color: rgba(34,211,238,.4); box-shadow: 0 0 12px rgba(0,242,254,.1); }
 .t2v-sc3 span { display: block; font: 500 10px 'JetBrains Mono', monospace; color: #94A3B8; text-transform: uppercase; letter-spacing: .05em; }
 .t2v-sc3 b { display: block; font: 700 14px 'JetBrains Mono', monospace; color: #E2E8F0; margin: 2px 0; }
-.t2v-sc3 small { font: 10px 'JetBrains Mono', monospace; color: #64748B; }
+.t2v-sc3 small { font: 11px 'JetBrains Mono', monospace; color: #94A3B8; }
 .t2v-sc3 .on span, .t2v-sc3 .on b, .t2v-sc3 .on small { color: #67E8F9; }
 .t2v-meta { border-top: 1px solid rgba(255,255,255,.05); padding-top: 12px; font: 12px 'JetBrains Mono', monospace; color: #94A3B8; }
 .t2v-meta div { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 7px; }
@@ -347,6 +347,7 @@
 
 # ===================================================================== tiện ích HTML
 e = lambda x: html.escape(str(x))
+txt = lambda x: x if isinstance(x, str) else ""  # Bỏ NaN vì NaN truthy nhưng không phải mô tả.
 vn = lambda x, d=3: f"{x:.{d}f}".replace(".", ",")  # số thập phân dấu phẩy như trong báo cáo
 pct = lambda x: f"{x * 100:.1f}%".replace(".", ",")
 num = lambda n: f"{int(n):,}".replace(",", ".")
@@ -818,7 +819,7 @@
                 when = f'<span class="sep">·</span><span>{t:%H:%M · %d/%m/%Y}</span>' if t is not None else ""
                 a.html(f'<div class="t2v-nmeta"><b>{e(r.source_name)}</b>{when}{chip}</div>'
                        f'<div class="t2v-ntitle"><a href="{e(r.url)}" target="_blank">{e(r.title)}</a></div>'
-                       f'<div class="t2v-nsum">{e(r.summary or "")}</div>')
+                       f'<div class="t2v-nsum">{e(txt(r.summary))}</div>')
                 if b.button("Phân loại lại" if cat else "Phân loại bài này", key=f"n{r.id}", width="stretch"):
                     classify_news(s, clf, r)
                     st.rerun()
@@ -826,7 +827,7 @@
 
 def classify_news(s, clf, r):
     """Phân loại một tin RSS bằng mô hình cải tiến, ghi feed_item.pred_category."""
-    ms = clf.predict(f"{r.title}\n{r.summary or ''}", log=True)["models"]
+    ms = clf.predict(f"{r.title}\n{txt(r.summary)}", log=True)["models"]
     p = next((m for m in ms if m["improved"]), ms[-1])["proba"]
     if p:
         with s.lock, s.db.cursor() as c:
```

## Tiêu chí nghiệm thu (AC)
| AC | Mô tả | Cách kiểm | Trạng thái |
|---|---|---|---|
| AC-1 | Gradient `#0E7490` | thấy trong diff | đã làm |
| AC-2, AC-3 | Tương phản nút default/hover | Codex đo hover 4,56:1; chưa đo 3 điểm default | chưa kiểm (tester) |
| AC-4 | Ảnh chụp nút | cần chạy app | chưa làm (tester) |
| AC-5 | `#64748B` còn 2 chỗ đồ họa | grep: dòng 75, 148 | đã làm |
| AC-6 | 4 selector 11px + `#94A3B8` | thấy trong diff | đã làm |
| AC-7 | Tương phản `#94A3B8` | contrast.py | chưa kiểm (tester) |
| AC-8 | Ảnh chụp, không xuống dòng | cần chạy app | chưa làm (tester) |
| AC-9 | Không còn `summary or` | grep = 0; 2 chỗ dùng `txt(r.summary)` | đã làm |
| AC-10 | `txt` trả "" cho None/NaN/pd.NA | chưa chạy | chưa kiểm (tester) |
| AC-11, AC-13 | Trang RSS, dọn log | cần chạy app/CSDL | chưa làm (tester) |
| AC-12 | py_compile | `PYC_OK` (xem dưới) | đã làm một phần |

## Đầu ra
- File Codex đã sửa: `src/system/app/streamlit_app.py` (7 vùng: dòng 93, 114, 249, 304, 315, +1 dòng `txt` ở 350, 822, 830).
- py_compile: `.venv-exp/bin/python -m py_compile src/system/app/streamlit_app.py` thành công (PYC_OK).
- `git status --porcelain` không đổi so với trước khi chạy Codex: không có file ngoài phạm vi.
- Log: `logs/03_codex_events.jsonl`, `logs/03_codex_stderr.log`, `codex_last.md`.

## Việc mở cho bước sau
- Cần khởi động lại Streamlit (đổi `streamlit_app.py`, `st.cache_resource`).
- Lưu ý: `pd.NA` không phải `str` nên `txt` trả ""; đúng AC-10.
- Dòng 815 (`NaT`) ngoài phạm vi, giữ nguyên.
- Tester dọn `classify_log`, `search_log` nếu sinh dữ liệu.

## Cách kiểm tra
- `diff -u contexte/handoff/ui-contrast-fix/logs/streamlit_app.before.py src/system/app/streamlit_app.py`
- `.venv-exp/bin/python -m py_compile src/system/app/streamlit_app.py`
- `grep -n "64748B\|summary or" src/system/app/streamlit_app.py`
