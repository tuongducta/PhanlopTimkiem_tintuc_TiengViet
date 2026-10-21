"""Cấu hình kết nối dùng chung cho pipeline, app và bench.

Giá trị mặc định khớp với docker-compose.yml; ghi đè bằng biến môi trường cùng tên.
"""
import os

import pymysql

MARIADB = dict(
    host=os.getenv("MARIADB_HOST", "127.0.0.1"),
    port=int(os.getenv("MARIADB_PORT", "3307")),
    user=os.getenv("MARIADB_USER", "t2v"),
    password=os.getenv("MARIADB_PASSWORD", "t2v_pass"),
    database=os.getenv("MARIADB_DATABASE", "trans2vec"),
    charset="utf8mb4",
    # Collation của kết nối quyết định phép so sánh chuỗi hằng; mặc định server (uca1400_ai_ci) gộp dấu.
    collation="utf8mb4_uca1400_vietnamese_as_ci",
)

MANTICORE = dict(
    host=os.getenv("MANTICORE_HOST", "127.0.0.1"),
    port=int(os.getenv("MANTICORE_SQL_PORT", "9306")),
    user="",
    password="",
    charset="utf8mb4",
)


def connect_mariadb(**kw):
    return pymysql.connect(**{**MARIADB, **kw})


def connect_manticore(**kw):
    # Manticore không có transaction kiểu InnoDB; autocommit để mỗi lệnh có hiệu lực ngay.
    return pymysql.connect(**{**MANTICORE, "autocommit": True, **kw})
