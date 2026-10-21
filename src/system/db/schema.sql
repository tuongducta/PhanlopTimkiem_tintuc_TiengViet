-- Lược đồ MariaDB 11.8 cho hệ thống Trans2Vec (GĐ-H2). Nguồn dữ liệu gốc; Manticore dựng lại từ đây.
-- Áp dụng:  docker exec -i t2v-mariadb mariadb -ut2v -pt2v_pass trans2vec < src/system/db/schema.sql
--
-- Quy ước collation (đã kiểm tra trên 11.8.9):
--   * Văn bản tiếng Việt: utf8mb4_uca1400_vietnamese_as_ci — GIỮ DẤU (bàn ≠ bán, đ ≠ d), không phân biệt hoa/thường,
--     sắp xếp theo bảng chữ cái tiếng Việt. Mặc định của server (uca1400_ai_ci) gộp dấu nên không dùng.
--   * Token (item.token): utf8mb4_bin — so khớp tuyệt đối, đúng như từ vựng của gensim/pyvi.
-- Ghi chú: InnoDB không cho khóa ngoại trên bảng phân vùng, nên chỉ hai bảng nhật ký (không có FK) được phân vùng.

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS classify_log, search_log, eval_result, prediction, article_vector,
    article_itemset, itemset_item, itemset, model_run, article_item, item, article, category;
SET FOREIGN_KEY_CHECKS = 1;

ALTER DATABASE trans2vec CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_vietnamese_as_ci;

-- ------------------------------------------------------------------ dữ liệu gốc
CREATE TABLE category (
  id   TINYINT UNSIGNED PRIMARY KEY,
  code CHAR(2)     NOT NULL UNIQUE,          -- XH, DS, KH, KD, PL, SK, TG, TT, VH, VT
  name VARCHAR(64) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE article (
  id          INT UNSIGNED PRIMARY KEY,      -- = vị trí dòng trong corpus.tsv.gz + 1 (Manticore cấm id 0)
  category_id TINYINT UNSIGNED NOT NULL,
  split       ENUM('train','test') NOT NULL,
  source_file VARCHAR(128) NOT NULL,         -- "<Train_Full|Test_Full>/<thư mục>/<tệp>.txt"
  title       VARCHAR(512) NOT NULL,         -- dòng đầu của tệp gốc
  body        MEDIUMTEXT   NOT NULL,         -- toàn văn gốc (NFC), không gồm tiêu đề
  body_md5    BINARY(16) AS (UNHEX(MD5(body))) STORED,  -- phát hiện bài trùng nội dung (VNTC có 4.984 bản thừa)
  body_syl    MEDIUMTEXT   NOT NULL,         -- âm tiết, chữ thường  (cột `syl` của corpus.tsv)
  body_seg    MEDIUMTEXT   NOT NULL,         -- từ pyvi nối '_'     (cột `word` của corpus.tsv)
  n_syl       INT UNSIGNED NOT NULL,
  n_word      INT UNSIGNED NOT NULL,
  UNIQUE KEY uq_source (source_file),
  KEY ix_split_cat (split, category_id),
  KEY ix_body_md5 (body_md5),
  CONSTRAINT fk_article_cat FOREIGN KEY (category_id) REFERENCES category (id)
) ENGINE=InnoDB;

-- Từ vựng view "word" (min_df=3, max_df=0.3 trên train, như t2v.Vocab). Từ dừng vẫn lưu để giải thích.
CREATE TABLE item (
  id       MEDIUMINT UNSIGNED PRIMARY KEY,
  token    VARCHAR(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  df_train MEDIUMINT UNSIGNED NOT NULL,
  idf      FLOAT NULL,                       -- NULL nếu là từ dừng hoặc quá hiếm (không vào transaction)
  is_stop  BOOLEAN NOT NULL DEFAULT FALSE,
  UNIQUE KEY uq_token (token)
) ENGINE=InnoDB;

-- Bảng transaction: top-k (k=50) item theo tf·idf của mỗi bài. PK (article_id, item_id) phục vụ
-- "lấy transaction của một bài"; chỉ mục ngược (item_id, article_id) là chỉ mục phủ cho đếm support.
CREATE TABLE article_item (
  article_id INT UNSIGNED NOT NULL,
  item_id    MEDIUMINT UNSIGNED NOT NULL,
  tf         SMALLINT UNSIGNED NOT NULL,
  tfidf      FLOAT NOT NULL,
  rnk        TINYINT UNSIGNED NOT NULL,      -- 1 = tf·idf cao nhất
  PRIMARY KEY (article_id, item_id),
  KEY ix_item_article (item_id, article_id),
  CONSTRAINT fk_ai_article FOREIGN KEY (article_id) REFERENCES article (id) ON DELETE CASCADE,
  CONSTRAINT fk_ai_item    FOREIGN KEY (item_id)    REFERENCES item (id)
) ENGINE=InnoDB;

-- ------------------------------------------------------------------ mô hình và kết quả (nạp ở GĐ-H3)
CREATE TABLE model_run (
  id         SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  kind       VARCHAR(32) NOT NULL,           -- 'fim', 'trans2vec-joi', 'trans-it', 'lr', ...
  parent_id  SMALLINT UNSIGNED NULL,         -- vd. mô hình LR dựng trên vector của lần chạy Trans2Vec nào
  params     JSON NOT NULL CHECK (JSON_VALID(params)),
  metrics    JSON NULL CHECK (metrics IS NULL OR JSON_VALID(metrics)),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_run_parent FOREIGN KEY (parent_id) REFERENCES model_run (id)
) ENGINE=InnoDB;

CREATE TABLE itemset (
  id        INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  run_id    SMALLINT UNSIGNED NOT NULL,
  size      TINYINT UNSIGNED NOT NULL,
  support   INT UNSIGNED NOT NULL,           -- số giao dịch train chứa itemset
  is_closed BOOLEAN NOT NULL,
  wilson_lo FLOAT NULL,                      -- cận dưới CI Wilson của relative support (K25)
  label     VARCHAR(400) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,  -- token FI kiểu t2v.fi_token
  UNIQUE KEY uq_run_label (run_id, label),
  CONSTRAINT fk_is_run FOREIGN KEY (run_id) REFERENCES model_run (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE itemset_item (
  itemset_id INT UNSIGNED NOT NULL,
  item_id    MEDIUMINT UNSIGNED NOT NULL,
  PRIMARY KEY (itemset_id, item_id),
  KEY ix_item (item_id),
  CONSTRAINT fk_isi_set  FOREIGN KEY (itemset_id) REFERENCES itemset (id) ON DELETE CASCADE,
  CONSTRAINT fk_isi_item FOREIGN KEY (item_id)    REFERENCES item (id)
) ENGINE=InnoDB;

CREATE TABLE article_itemset (
  article_id INT UNSIGNED NOT NULL,
  itemset_id INT UNSIGNED NOT NULL,
  PRIMARY KEY (article_id, itemset_id),
  KEY ix_itemset (itemset_id),
  CONSTRAINT fk_ais_article FOREIGN KEY (article_id) REFERENCES article (id) ON DELETE CASCADE,
  CONSTRAINT fk_ais_set     FOREIGN KEY (itemset_id) REFERENCES itemset (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Vector 128 chiều (L2-chuẩn hóa) của mỗi bài theo từng lần chạy. VECTOR INDEX chỉ cho một cột/bảng
-- và không lọc theo run_id, nên benchmark E-DB2 chép vector của một run sang bảng riêng (xem bench/).
CREATE TABLE article_vector (
  article_id INT UNSIGNED NOT NULL,
  run_id     SMALLINT UNSIGNED NOT NULL,
  vec        VECTOR(128) NOT NULL,
  PRIMARY KEY (article_id, run_id),
  KEY ix_run (run_id),
  CONSTRAINT fk_av_article FOREIGN KEY (article_id) REFERENCES article (id) ON DELETE CASCADE,
  CONSTRAINT fk_av_run     FOREIGN KEY (run_id)     REFERENCES model_run (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE prediction (
  article_id       INT UNSIGNED NOT NULL,
  run_id           SMALLINT UNSIGNED NOT NULL,
  pred_category_id TINYINT UNSIGNED NOT NULL,
  proba            JSON NOT NULL CHECK (JSON_VALID(proba)),   -- {"XH":0.01, ...}
  PRIMARY KEY (article_id, run_id),
  KEY ix_run_pred (run_id, pred_category_id),
  CONSTRAINT fk_pred_article FOREIGN KEY (article_id)       REFERENCES article (id) ON DELETE CASCADE,
  CONSTRAINT fk_pred_run     FOREIGN KEY (run_id)           REFERENCES model_run (id) ON DELETE CASCADE,
  CONSTRAINT fk_pred_cat     FOREIGN KEY (pred_category_id) REFERENCES category (id)
) ENGINE=InnoDB;

CREATE TABLE eval_result (
  run_id SMALLINT UNSIGNED NOT NULL,
  task   ENUM('classify','search') NOT NULL,
  metric VARCHAR(32) NOT NULL,               -- acc, macro_f1, ndcg@10, p50_ms, ...
  config VARCHAR(64) NOT NULL DEFAULT '',    -- vd. 'bm25', 'knn', 'hybrid', 'manticore-vi'
  value  DOUBLE NOT NULL,
  PRIMARY KEY (run_id, task, metric, config),
  CONSTRAINT fk_eval_run FOREIGN KEY (run_id) REFERENCES model_run (id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------------ nhật ký (phân vùng theo tháng, không FK)
CREATE TABLE search_log (
  id         BIGINT UNSIGNED AUTO_INCREMENT,
  ts         DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  query      VARCHAR(1024) NOT NULL,
  mode       ENUM('bm25','knn','hybrid') NOT NULL,
  category_id TINYINT UNSIGNED NULL,
  latency_ms FLOAT NOT NULL,
  result_ids JSON NOT NULL CHECK (JSON_VALID(result_ids)),
  PRIMARY KEY (id, ts)
) ENGINE=InnoDB
PARTITION BY RANGE COLUMNS (ts) (
  PARTITION p2026_10 VALUES LESS THAN ('2026-11-01'),
  PARTITION p2026_11 VALUES LESS THAN ('2026-12-01'),
  PARTITION p2026_12 VALUES LESS THAN ('2027-01-01'),
  PARTITION pmax     VALUES LESS THAN (MAXVALUE)
);

CREATE TABLE classify_log (
  id          BIGINT UNSIGNED AUTO_INCREMENT,
  ts          DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  text_hash   BINARY(32) NOT NULL,           -- SHA-256 của văn bản đầu vào
  run_id      SMALLINT UNSIGNED NOT NULL,
  pred_category_id TINYINT UNSIGNED NOT NULL,
  latency_ms  FLOAT NOT NULL,
  PRIMARY KEY (id, ts)
) ENGINE=InnoDB
PARTITION BY RANGE COLUMNS (ts) (
  PARTITION p2026_10 VALUES LESS THAN ('2026-11-01'),
  PARTITION p2026_11 VALUES LESS THAN ('2026-12-01'),
  PARTITION p2026_12 VALUES LESS THAN ('2027-01-01'),
  PARTITION pmax     VALUES LESS THAN (MAXVALUE)
);

-- Danh mục chuyên mục (theo Stats.txt của VNTC; mã khớp experiments/prepare.py).
INSERT INTO category (id, code, name) VALUES
  (1,'XH','Chính trị Xã hội'), (2,'DS','Đời sống'), (3,'KH','Khoa học'), (4,'KD','Kinh doanh'),
  (5,'PL','Pháp luật'), (6,'SK','Sức khỏe'), (7,'TG','Thế giới'), (8,'TT','Thể thao'),
  (9,'VH','Văn hóa'), (10,'VT','Vi tính');
