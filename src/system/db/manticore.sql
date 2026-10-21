-- Bảng tìm kiếm Manticore 29.9 (GĐ-H4): chỉ mục PHÁI SINH, dựng lại toàn bộ từ MariaDB bằng
-- system/pipeline/sync_manticore.py (script đọc file này, thay {table} và {charset_table}).
--
-- Trường (đã kiểm tra trên bản cài thật):
--   title      text           lưu + đánh chỉ mục (âm tiết, vì tiêu đề gốc chưa tách từ) → HIGHLIGHT() được
--   title_seg  text indexed   tiêu đề tách từ pyvi
--   body_seg   text indexed   toàn văn tách từ pyvi ('giá_vàng' là một token nhờ '_' trong charset_table)
--   body_syl   text indexed   toàn văn theo âm tiết — cấu hình (c) của E-DB5: truy vấn "vàng" vẫn khớp
--   title_fold, body_fold  text indexed  tiêu đề / âm tiết đã gộp dấu bằng system/vi_text.fold() — nhánh cho
--              truy vấn gõ không dấu (P1); gộp ở Python vì charset_table áp cho cả bảng
--   (`text indexed` = không lưu nội dung; toàn văn lấy từ MariaDB, giữ bảng nhỏ)
-- Thuộc tính lọc: category_id, split. Vector: Trans2Vec-JOI 128 chiều (đã L2-chuẩn hóa), HNSW cosine.
-- charset_table mặc định của dịch vụ là 'non_cjk' (gộp dấu, tách '_'); hệ thống dùng bảng giữ dấu VI.

CREATE TABLE {table} (
  title       text,
  title_seg   text indexed,
  body_seg    text indexed,
  body_syl    text indexed,
  title_fold  text indexed,
  body_fold   text indexed,
  category_id uint,
  split       string attribute,
  vec         float_vector knn_type='hnsw' knn_dims='128' hnsw_similarity='COSINE'
              hnsw_m='16' hnsw_ef_construction='200'
) charset_table='{charset_table}' min_word_len='1';
