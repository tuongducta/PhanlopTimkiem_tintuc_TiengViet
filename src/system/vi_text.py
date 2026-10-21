"""Gộp dấu tiếng Việt cho nhánh truy vấn không dấu (đề xuất P1 của E-DB5, duyệt 21/10/2026).

Bảng Manticore `news` giữ dấu; trường `title_fold`, `body_fold` chứa cùng văn bản đã gộp dấu bằng hàm fold()
dưới đây (Manticore chỉ cho một charset_table mỗi bảng, nên gộp dấu làm ở Python trước khi đánh chỉ mục).
Gộp đều mọi nguyên âm, kể cả 'ạ' mà charset non_cjk bỏ sót (xem E-DB5).
"""
import re
import unicodedata

LETTER = re.compile(r"[^\W\d_]")


def fold(text):
    """Bỏ dấu thanh và dấu phụ (NFD bỏ dấu kết hợp), đ → d, chữ thường."""
    s = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    return unicodedata.normalize("NFC", "".join(ch for ch in s if unicodedata.category(ch) != "Mn")).lower()


def is_unaccented(text):
    """Truy vấn có chữ nhưng không có dấu nào: người dùng gõ không dấu."""
    return bool(LETTER.search(text)) and fold(text) == text.lower()
