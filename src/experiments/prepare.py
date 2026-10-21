"""Bước 1 — Tiền xử lý VNTC-10 (mô-đun M1, Chương 9).

Đọc 84.132 bài (UTF-16) trong data/vntc/raw/{Train_Full,Test_Full}/<chủ đề>/*.txt và sinh hai
"góc nhìn" item cho mỗi bài:
  - syl : âm tiết (không tách từ), chữ thường
  - word: từ do pyvi tách (ghép âm tiết bằng '_'), chữ thường
Chuẩn hóa Unicode NFC; bỏ số, dấu câu và token không phải chữ. Từ dừng KHÔNG bỏ ở đây mà
được xác định theo dữ liệu (tần suất văn bản trên tập train) ở bước dựng đặc trưng.

Kết quả: data/vntc/processed/corpus.tsv.gz với các cột split, label, file, syl, word.
Chạy:  .venv-exp/bin/python src/experiments/prepare.py
"""
import gzip
import re
import time
import unicodedata
from multiprocessing import Pool
from pathlib import Path

from pyvi import ViTokenizer

ROOT = Path(__file__).resolve().parents[2]  # gốc dự án (mã ở src/experiments/)
RAW = ROOT / "sources/data/vntc/raw"
OUT = ROOT / "sources/data/vntc/processed/corpus.tsv.gz"

LABELS = {  # tên thư mục → mã chủ đề (theo Stats.txt của VNTC)
    "Chinh tri Xa hoi": "XH", "Doi song": "DS", "Khoa hoc": "KH", "Kinh doanh": "KD",
    "Phap luat": "PL", "Suc khoe": "SK", "The gioi": "TG", "The thao": "TT",
    "Van hoa": "VH", "Vi tinh": "VT",
}
SYL = re.compile(r"[^\W\d_]+")
WORD = re.compile(r"[^\W\d_]+(?:_[^\W\d_]+)*")


def process(path):
    split = "train" if path.parts[-3] == "Train_Full" else "test"
    label = LABELS[path.parts[-2].strip()]
    text = unicodedata.normalize("NFC", path.read_bytes().decode("utf-16"))
    syl = SYL.findall(text.lower())
    words = [w for w in (t.lower() for t in ViTokenizer.tokenize(text).split()) if WORD.fullmatch(w)]
    return split, label, path.name, " ".join(syl), " ".join(words)


def main():
    files = sorted(RAW.glob("*_Full/*/*.txt"))
    print(f"{len(files)} tệp")
    t0 = time.time()
    with Pool(10) as pool:
        rows = pool.map(process, files, chunksize=200)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT, "wt", encoding="utf-8") as f:
        f.write("split\tlabel\tfile\tsyl\tword\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    n_train = sum(r[0] == "train" for r in rows)
    print(f"Đã ghi {OUT.relative_to(ROOT)}: train={n_train}, test={len(rows) - n_train}, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
