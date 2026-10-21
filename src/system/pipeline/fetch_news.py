"""Lấy tin mới nhất từ RSS của VnExpress, Tuổi Trẻ, Thanh Niên và lưu vào MariaDB (bảng feed_item).

Chỉ đọc RSS (kênh các báo công bố để phân phối tin), không tải trang bài viết.
Mỗi tin lưu tiêu đề, mô tả ngắn, link, ảnh, thời điểm đăng. Trùng lặp chặn bằng SHA-1 của url.

Chạy:
  .venv-exp/bin/python src/system/pipeline/fetch_news.py               # lấy một lần, cả 3 báo
  .venv-exp/bin/python src/system/pipeline/fetch_news.py --only vne    # một báo
  .venv-exp/bin/python src/system/pipeline/fetch_news.py --loop 15     # lặp mỗi 15 phút (Ctrl+C để dừng)
  .venv-exp/bin/python src/system/pipeline/fetch_news.py --latest 10   # in 10 tin mới nhất trong CSDL
"""
import argparse
import hashlib
import html
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import connect_mariadb  # noqa: E402

SOURCES = [
    # code, tên, RSS "tin mới nhất". Cả ba đều là nguồn của bộ VNTC nên cùng miền dữ liệu với mô hình.
    ("vne", "VnExpress", "https://vnexpress.net/rss/tin-moi-nhat.rss"),
    ("tto", "Tuổi Trẻ", "https://tuoitre.vn/rss/tin-moi-nhat.rss"),
    ("tn", "Thanh Niên", "https://thanhnien.vn/rss/home.rss"),
]

USER_AGENT = "Trans2Vec-research/0.1 (HUTECH coursework; RSS reader)"
TIMEOUT_S = 15
MAX_BYTES = 5 * 1024 * 1024
MIN_LOOP_MIN = 5  # không lấy dày hơn 5 phút một lần
VN_TZ = timezone(timedelta(hours=7))
SCHEMA = Path(__file__).resolve().parents[1] / "db" / "feed.sql"


def apply_schema(con):
    sql = "\n".join(l for l in SCHEMA.read_text(encoding="utf-8").splitlines() if not l.lstrip().startswith("--"))
    with con.cursor() as c:
        for stmt in filter(None, (s.strip() for s in sql.split(";"))):
            c.execute(stmt)
        c.executemany(
            "INSERT INTO news_source (code, name, rss_url) VALUES (%s, %s, %s)"
            " ON DUPLICATE KEY UPDATE name = VALUES(name), rss_url = VALUES(rss_url)",
            SOURCES,
        )
    con.commit()


def parse_date(s):
    """RFC 822 (VnExpress, Thanh Niên, kể cả năm 2 chữ số) hoặc 'MM/DD/YYYY h:mm:ss AM' giờ VN (Tuổi Trẻ). Trả về UTC naive."""
    s = (s or "").strip()
    if not s:
        return None
    try:
        dt = parsedate_to_datetime(s)
    except (TypeError, ValueError):
        try:
            dt = datetime.strptime(s, "%m/%d/%Y %I:%M:%S %p")
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=VN_TZ)
    return dt.astimezone(timezone.utc).replace(tzinfo=None)


def clean_text(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def first_img(desc):
    m = re.search(r'<img[^>]+src="([^"]+)"', desc or "")
    return html.unescape(m.group(1)) if m else None


def parse_feed(raw):
    items = []
    for it in ET.fromstring(raw).iter("item"):
        url = (it.findtext("link") or it.findtext("guid") or "").strip()
        title = clean_text(it.findtext("title"))
        if not url.startswith("http") or not title:
            continue
        desc = it.findtext("description") or ""
        enc = it.find("enclosure")
        items.append(dict(
            url=url[:512],
            title=title[:512],
            summary=clean_text(desc) or None,
            image_url=((enc.get("url") if enc is not None else None) or first_img(desc) or "")[:512] or None,
            published_at=parse_date(it.findtext("pubDate")),
        ))
    return items


def http_get(url, etag, last_modified):
    headers = {"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/xml, text/xml"}
    if etag:
        headers["If-None-Match"] = etag
    if last_modified:
        headers["If-Modified-Since"] = last_modified
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
            body = r.read(MAX_BYTES + 1)
            if len(body) > MAX_BYTES:
                raise ValueError("feed vượt quá 5 MB")
            return r.status, body, r.headers.get("ETag"), r.headers.get("Last-Modified")
    except urllib.error.HTTPError as e:
        if e.code == 304:
            return 304, b"", etag, last_modified
        raise


def fetch_source(con, src_id, code, rss_url, etag, last_modified):
    started = datetime.now(timezone.utc).replace(tzinfo=None)
    t0 = time.perf_counter()
    status, n_items, n_new, err = None, 0, 0, None
    try:
        status, body, new_etag, new_lm = http_get(rss_url, etag, last_modified)
        with con.cursor() as c:
            if status == 200:
                items = parse_feed(body)
                n_items = len(items)
                for it in items:
                    n_new += c.execute(
                        "INSERT IGNORE INTO feed_item (source_id, url, url_hash, title, summary, image_url, published_at)"
                        " VALUES (%s, %s, UNHEX(SHA1(%s)), %s, %s, %s, %s)",
                        (src_id, it["url"], it["url"], it["title"], it["summary"], it["image_url"], it["published_at"]),
                    )
            c.execute(
                "UPDATE news_source SET etag = %s, last_modified = %s, last_fetch_at = %s WHERE id = %s",
                (new_etag, new_lm, started, src_id),
            )
    except Exception as e:  # một báo lỗi không làm dừng các báo khác
        con.rollback()
        n_new = 0
        err = f"{type(e).__name__}: {e}"[:512]
    latency = int((time.perf_counter() - t0) * 1000)
    with con.cursor() as c:
        c.execute(
            "INSERT INTO fetch_log (source_id, started_at, http_status, n_items, n_new, latency_ms, error)"
            " VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (src_id, started, status, n_items, n_new, latency, err),
        )
    con.commit()  # tin mới, ETag và nhật ký của một báo ghi cùng một transaction
    print(f"[{code}] HTTP {status or '-'} · {n_items} tin trong feed · {n_new} tin mới · {latency} ms"
          + (f" · LỖI {err}" if err else ""))
    return n_new


def fetch_all(con, only=None):
    with con.cursor() as c:
        c.execute("SELECT id, code, rss_url, etag, last_modified FROM news_source WHERE active")
        rows = [r for r in c.fetchall() if not only or r[1] in only]
    return sum(fetch_source(con, *r) for r in rows)


def print_latest(con, n):
    with con.cursor() as c:
        c.execute(
            "SELECT source_name, published_at, title FROM v_latest_news ORDER BY published_at DESC LIMIT %s", (n,)
        )
        for name, pub, title in c.fetchall():
            local = pub.replace(tzinfo=timezone.utc).astimezone(VN_TZ).strftime("%d/%m %H:%M") if pub else "--"
            print(f"{local}  {name:<10}  {title}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", nargs="+", choices=[s[0] for s in SOURCES], help="chỉ lấy các báo này")
    ap.add_argument("--loop", type=int, metavar="PHÚT", help=f"lặp lại sau mỗi PHÚT (tối thiểu {MIN_LOOP_MIN})")
    ap.add_argument("--latest", type=int, metavar="N", help="chỉ in N tin mới nhất trong CSDL, không lấy tin")
    args = ap.parse_args()

    con = connect_mariadb()
    apply_schema(con)
    if args.latest:
        print_latest(con, args.latest)
        return
    if not args.loop:
        print(f"Tổng: {fetch_all(con, args.only)} tin mới")
        return
    every = max(args.loop, MIN_LOOP_MIN) * 60
    try:
        while True:
            print(f"--- {datetime.now(VN_TZ):%d/%m/%Y %H:%M:%S}")
            print(f"Tổng: {fetch_all(con, args.only)} tin mới")
            time.sleep(every)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
