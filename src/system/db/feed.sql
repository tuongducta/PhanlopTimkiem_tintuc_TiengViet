-- Thu thập tin mới nhất từ RSS của các báo (VnExpress, Tuổi Trẻ, Thanh Niên).
-- Tách khỏi bảng `article` (VNTC) để không trộn dữ liệu huấn luyện với dữ liệu thu thập trực tuyến.
-- Chạy lặp lại được: mọi lệnh đều IF NOT EXISTS.

CREATE TABLE IF NOT EXISTS news_source (
  id            TINYINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  code          VARCHAR(16)  NOT NULL UNIQUE,
  name          VARCHAR(64)  NOT NULL,
  rss_url       VARCHAR(255) NOT NULL,
  active        BOOLEAN      NOT NULL DEFAULT TRUE,
  -- GET có điều kiện: gửi lại ETag / Last-Modified để máy chủ trả 304 khi feed chưa đổi
  etag          VARCHAR(255) NULL,
  last_modified VARCHAR(64)  NULL,
  last_fetch_at DATETIME     NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS feed_item (
  id             BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  source_id      TINYINT UNSIGNED NOT NULL,
  url            VARCHAR(512) NOT NULL,
  url_hash       BINARY(20)   NOT NULL,              -- SHA-1 của url, khóa chống trùng
  title          VARCHAR(512) NOT NULL,
  summary        TEXT         NULL,                   -- mô tả trong RSS, đã bỏ thẻ HTML
  image_url      VARCHAR(512) NULL,
  published_at   DATETIME     NULL,                   -- UTC
  fetched_at     DATETIME     NOT NULL DEFAULT UTC_TIMESTAMP(),
  pred_category  CHAR(2)      NULL,                   -- điền ở GĐ-H3 khi có mô hình
  indexed_at     DATETIME     NULL,                   -- thời điểm đã đồng bộ sang Manticore (A6)
  UNIQUE KEY uq_url_hash (url_hash),
  KEY ix_published (published_at),
  KEY ix_source_published (source_id, published_at),
  CONSTRAINT fk_feed_source FOREIGN KEY (source_id) REFERENCES news_source (id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS fetch_log (
  id          BIGINT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
  source_id   TINYINT UNSIGNED NOT NULL,
  started_at  DATETIME     NOT NULL,
  http_status SMALLINT     NULL,
  n_items     SMALLINT     NOT NULL DEFAULT 0,
  n_new       SMALLINT     NOT NULL DEFAULT 0,
  latency_ms  INT          NULL,
  error       VARCHAR(512) NULL,
  KEY ix_source_started (source_id, started_at),
  CONSTRAINT fk_log_source FOREIGN KEY (source_id) REFERENCES news_source (id)
) ENGINE=InnoDB;

-- Tin kèm tên báo, dùng cho tab "Tin mới nhất" của giao diện.
-- Không đặt ORDER BY trong view; truy vấn ngoài tự sắp: ... ORDER BY published_at DESC LIMIT n
CREATE OR REPLACE VIEW v_latest_news AS
SELECT f.id, s.code AS source_code, s.name AS source_name, f.title, f.summary, f.url,
       f.image_url, f.published_at, f.fetched_at, f.pred_category
FROM feed_item f JOIN news_source s ON s.id = f.source_id;
